import math
import random
from collections import namedtuple
import time
from pyrf.numpy_util import compute_fft
from pyrf.config import SweepEntry

SweepStep = namedtuple('SweepStep', '''
    fcenter
    fstep
    fshift
    decimation
    points
    bins_skip
    bins_run
    bins_keep
    ''')

class SweepDeviceError(Exception):
    pass

class SweepDevice(object):
    """
    Virtual device that generates power levels from a range of
    frequencies by sweeping the frequencies with a real device
    and piecing together FFT results.

    :param real_device: device that will will be used for capturing data,
                        typically a :class:`WSA4000` instance.
    :param callback: callback to use for async operation (not used if
                     real_device is using a :class:`PlainSocketConnector`)
    """
    def __init__(self, real_device, async_callback=None):
        self.real_device = real_device
        self._sweep_id = random.randrange(0, 2**32-1) # don't want 2**32-1
        if hasattr(self.connector, 'vrt_callback'):
            if not async_callback:
                raise SweepDeviceError(
                    "async_callback required for async operation")
            # disable receiving data until we are expecting it
            self.connector.vrt_callback = None
        else:
            if async_callback:
                raise SweepDeviceError(
                    "async_callback not applicable for sync operation")
        self._prev_sweep_id = None
        self.async_callback = async_callback
        self.context_bytes_received = 0
        self.data_bytes_received = 0
        self.data_bytes_processed = 0
        self.martian_bytes_discarded = 0
        self.past_end_bytes_discarded = 0
        self.fft_calculation_seconds = 1.0
        self.bin_collection_seconds = 1.0

    connector = property(lambda self: self.real_device.connector)

    def capture_power_spectrum(self,
            fstart, fstop, bins, antenna=1, rfgain='vlow', ifgain=0,
            min_points=128, max_points=8192):
        """
        Initiate a capture of power spectral density in the linear domain by
        setting up a sweep list and starting a single sweep.

        :param fstart: starting frequency in Hz
        :type fstart: float
        :param fstop: ending frequency in Hz
        :type fstop: float
        :param bins: FFT bins requested (number produced likely more)
        :type bins: int
        :param min_points: smallest number of points per capture from real_device
        :type min_points: int
        :param max_points: largest number of points per capture from real_device
                           (due to decimation limits points returned may be larger)
        :type max_points: int
        """
        self.real_device.abort()
        self.real_device.flush()
        self.real_device.request_read_perm()
        self.fstart, self.fstop, self.plan = plan_sweep(self.real_device,
            fstart, fstop, bins, min_points, max_points)

        self.real_device.sweep_clear()

        for ss in self.plan:
            steps = math.ceil(float(ss.bins_keep) / ss.bins_run)
            if ss.points > 32*1024:
                raise SweepDeviceError('large captures not yet supported')
            self.real_device.sweep_add(SweepEntry(
                fstart=ss.fcenter,
                fstop=min(ss.fcenter + (steps + 0.5) * ss.fstep,
                    self.real_device.MAX_TUNABLE),
                fstep=ss.fstep,
                fshift=ss.fshift,
                decimation=ss.decimation,
                antenna=antenna,
                gain=rfgain,
                ifgain=ifgain,
                spp=ss.points,
                ppb=1,
                ))

        if self.async_callback:
            if not self.plan:
                self.async_callback(self.fstart, self.fstop, [])
                return
            self.connector.vrt_callback = self._vrt_receive
            self._start_sweep()
            return

        if not self.plan:
            return (self.fstart, self.fstop, [])
        self._start_sweep()
        result = None
        while result is None:
            result = self._vrt_receive(self.real_device.read())
            print result
        return result

    def _start_sweep(self):
        self._prev_sweep_id = self._sweep_id
        self._sweep_id = (self._sweep_id + 1) & (2**32 - 1)
        self._vrt_context = {}
        self._ss_index = 0
        self._ss_received = 0
        self.bins = []
        self.real_device.sweep_iterations(1)
        self.real_device.sweep_start(self._sweep_id)

    def _vrt_receive(self, packet):
        packet_bytes = packet.size * 4

        if packet.is_context_packet():
            self._vrt_context.update(packet.fields)
            self.context_bytes_received += packet_bytes
            return

        self.data_bytes_received += packet_bytes
        sweep_id = self._vrt_context.get('sweepid')
        if sweep_id != self._sweep_id:
            if sweep_id == self._prev_sweep_id:
                self.past_end_bytes_discarded += packet_bytes
            else:
                self.martian_bytes_discarded += packet_bytes
            return # not our data
        assert 'reflevel' in self._vrt_context, (
            "missing required context, sweep failed")

        if self._ss_index is None:
            self.past_end_bytes_discarded += packet_bytes
            return # more data than we asked for

        fft_start_time = time.time()
        pow_data = compute_fft(self.real_device, packet, self._vrt_context)
        # collect and compute bins
        collect_start_time = time.time()
        ss = self.plan[self._ss_index]
        take = min(ss.bins_run, ss.bins_keep - self._ss_received)
        self.bins.extend(pow_data[ss.bins_skip:ss.bins_skip + take])
        self._ss_received += take
        collect_stop_time = time.time()

        self.fft_calculation_seconds += collect_start_time - fft_start_time
        self.bin_collection_seconds += collect_stop_time - collect_start_time
        self.data_bytes_processed += take * 4

        if self._ss_received < ss.bins_keep:
            return

        self._ss_received = 0
        self._ss_index += 1
        if self._ss_index < len(self.plan):
            return

        # done the complete sweep
        # XXX: in case sweep_iterations() does not work
        self._ss_index = None
        self.real_device.abort()
        self.real_device.flush()

        if self.async_callback:
            self.real_device.vrt_callback = None
            self.async_callback(self.fstart, self.fstop, self.bins)
            return
        return (self.fstart, self.fstop, self.bins)



def plan_sweep(device, fstart, fstop, bins, min_points=128, max_points=8192):
    """
    :param device: a device class or instance such as
                   :class:`pyrf.devices.thinkrf.WSA4000`
    :param fstart: starting frequency in Hz
    :type fstart: float
    :param fstop: ending frequency in Hz
    :type fstop: float
    :param bins: FFT bins requested (number produced likely more)
    :type bins: int
    :param min_points: smallest number of points per capture
    :type min_points: int
    :param max_points: largest number of points per capture (due to
                       decimation limits points returned may be larger)
    :type max_points: int

    The following device attributes are used in planning the sweep:

    device.FULL_BW
      full width of the filter in Hz
    device.USABLE_BW
      usable portion before filter drop-off at edges in Hz
    device.MIN_TUNABLE
      the lowest valid center frequency for arbitrary tuning in Hz,
      0(DC) is always assumed to be available for direct digitization
    device.MAX_TUNABLE
      the highest valid center frequency for arbitrart tuning in Hz
    device.MIN_DECIMATION
      the lowest valid decimation value above 1, 1(no decimation) is
      assumed to always be available
    device.MAX_DECIMATION
      the highest valid decimation value, only powers of 2 will be used
    device.DECIMATED_USABLE
      the fraction decimated output containing usable data, float < 1.0
    device.DC_OFFSET_BW
      the range of frequencies around center that may be affected by
      a DC offset and should not be used

    :returns: (actual fstart, actual fstop, list of SweepStep instances)

    The caller would then use each of these tuples to do the following:

    1. The first 5 values are used for a single capture or single sweep
    2. An FFT is run on the points returned to produce bins in the linear
       domain
    3. bins[bins_skip:bins_skip + bins_run] are selected
    4. take logarithm of output bins and appended to the result
    5. for sweeps repeat from 2 until the sweep is complete
    6. bins_keep is the total number of selected bins to keep; for
       single captures bins_run == bins_keep
    """
    out = []
    usable2 = device.USABLE_BW / 2.0
    dc_offset2 = device.DC_OFFSET_BW / 2.0

    # FIXME: truncate to left-hand sweep area for now
    fstart = max(device.MIN_TUNABLE - usable2, fstart)
    fstop = min(device.MAX_TUNABLE - dc_offset2, fstop)

    if fstop <= fstart:
        return (fstart, fstart, [])

    ideal_bin_size = (fstop - fstart) / float(bins)
    points = device.FULL_BW / ideal_bin_size
    points = max(min_points, 2 ** math.ceil(math.log(points, 2)))

    decimation = 1
    ideal_decimation = 2 ** math.ceil(math.log(float(points) / max_points, 2))
    min_decimation = max(2, device.MIN_DECIMATION)
    max_decimation = 2 ** math.floor(math.log(device.MAX_DECIMATION, 2))
    if max_points < points and min_decimation <= ideal_decimation:
        decimation = min(max_decimation, ideal_decimation)
        points /= decimation
        decimated_bw = device.FULL_BW / decimation
        decimation_edge_bins = math.ceil(points * device.DECIMATED_USABLE / 2.0)
        decimation_edge = decimation_edge_bins * decimated_bw / points

    bin_size = device.FULL_BW / decimation / float(points)

    # there are three regions that need to be handled differently
    # region 0: direct digitization / "VLOW band"
    if fstart < device.MIN_TUNABLE - usable2:
        raise NotImplemented # yet

    # region 1: left-hand sweep area
    if device.MIN_TUNABLE - usable2 <= fstart:
        if decimation == 1:
            left_edge = device.FULL_BW / 2.0 - usable2
            left_bin = math.ceil(left_edge / bin_size)
            fshift = left_bin * bin_size - left_edge
            usable_bins = (usable2 - dc_offset2 - fshift) // bin_size
        else:
            left_bin = decimation_edge_bins
            fshift = usable2 + decimation_edge - (decimated_bw / 2.0)
            usable_bins = min(points - (decimation_edge_bins * 2),
                (usable2 - dc_offset2) // bin_size)

        usable_bw = usable_bins * bin_size

        fcenter = fstart + usable2
        # FIXME: fstop not being updated here
        max_steps = math.floor((device.MAX_TUNABLE - fstart) / usable_bw)
        bins_keep = min(round((fstop - fstart) / bin_size),
            max_steps * usable_bins)
        sweep_steps = math.ceil(bins_keep / usable_bins)
        out.append(SweepStep(
            fcenter=fcenter,
            fstep=usable_bw,
            fshift=fshift,
            decimation=decimation,
            points=int(points),
            bins_skip=int(left_bin),
            bins_run=int(min(usable_bins, bins_keep)),
            bins_keep=int(bins_keep),
            ))

    # region 2: right-hand edge
    if device.MAX_TUNABLE - dc_offset2 < fstop:
        raise NotImplemented # yet

    return (fstart, fstop, out)
