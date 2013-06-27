import constants
import util
import numpy as np
from pyrf.config import TriggerSettings
from playback_util import playBack
class plot_state(object):
    """
    Class to hold all the GUI's plot states
    """

    def __init__(self, layout):
        
        self.grid = False
        
        self.ant = 1
        self.gain = 'vlow'
        self.if_gain = 0 
        self.mhold = False
        self.mhold_fft = None
        
        
        
        self.trig = False
        self.trig_set = None
        self.marker = False
        self.marker_sel = False
        self.marker_ind = None
        
        self.delta = False
        self.delta_sel = False
        self.delta_ind = None
        self.peak = False
        
        self.freq_range = None        
        self.center_freq = constants.INIT_CENTER_FREQ
        self.bandwidth = constants.INIT_BANDWIDTH
        self.fstart = self.center_freq - self.bandwidth / 2
        self.fstop = self.center_freq + self.bandwidth / 2
        self.bin_size = constants.INIT_BIN_SIZE
        self.rbw = self.bandwidth / self.bin_size
        
        self.enable_plot = True
        self.freq_sel = 'CENT'
        
        self.playback = playBack()
        self.playback_enable = False
        self.playback_file_list = None
        self.playback_dir = '/Playback Capture'
        self.selected_playback = None
        self.playback_record = False
        
    def enable_marker(self, layout):
        self.marker = True
        self.marker_sel = True
        util.change_item_color(layout._marker,  constants.ORANGE, constants.WHITE)
        layout._plot.add_marker()
        layout._marker.setDown(True)
        layout.update_marker()
        if layout.plot_state.delta_sel:
            self.delta_sel = False
            util.change_item_color(layout._delta,  constants.ORANGE, constants.WHITE)
            layout._delta.setDown(False)
            

    def disable_marker(self, layout):
        
        self.marker = False
        self.marker_sel = False
        util.change_item_color(layout._marker, constants.NORMAL_COLOR, constants.BLACK)
        layout._marker.setDown(False)
        layout._plot.remove_marker()
        layout._marker_lab.setText('')
        layout._plot.center_view(layout.plot_state.center_freq, layout.plot_state.bandwidth)
        if self.delta:
            self.enable_delta(layout)

    def enable_delta(self, layout):
        self.delta = True
        self.delta_sel = True
        util.change_item_color(layout._delta, constants.ORANGE, constants.WHITE)
        layout._plot.add_delta()
        layout._delta.setDown(True)
        layout.update_delta()
        if self.marker:
            self.marker_sel = False             
            util.change_item_color(layout._marker, constants.ORANGE, constants.WHITE)
            layout._marker.setDown(False)
            
    def disable_delta(self, layout):
        self.delta = False
        self.delta_sel = False
        util.change_item_color(layout._delta, constants.NORMAL_COLOR ,constants.BLACK)
        layout._delta.setDown(False)
        layout._plot.remove_delta()
        layout._delta_lab.setText('')
        layout._diff_lab.setText('')
        layout._plot.center_view(layout.plot_state.center_freq, layout.plot_state.bandwidth)
        if self.marker:
            self.enable_marker(layout)
    
    def disable_trig(self, layout):
        self.trig = False
        util.change_item_color(layout._trigger, constants.NORMAL_COLOR, constants.BLACK)
        layout._plot.remove_trigger()
        self.trig_set.trigtype = constants.NONE_TRIGGER_TYPE
        layout.dut.trigger(self.trig_set)
        
    def enable_trig(self, layout):
        self.trig = True
        util.change_item_color(layout._trigger, constants.ORANGE,constants.WHITE)
        if self.trig_set == None:
            self.trig_set = TriggerSettings(constants.LEVELED_TRIGGER_TYPE,
                                                    self.center_freq + 10e6, 
                                                    self.center_freq - 10e6,-100) 
        self.trig_set.trigtype = constants.LEVELED_TRIGGER_TYPE
        layout.dut.trigger(self.trig_set)
        layout._plot.add_trigger(self.trig_set.fstart, self.trig_set.fstop)
        
    def update_freq_range(self, start, stop, size):
        self.freq_range = np.linspace(start, stop, size)
        


    def update_freq_set(self,
                          fstart = None, 
                          fstop = None, 
                          fcenter = None, 
                          rbw = None, 
                          bw = None):
        
        if fcenter != None:
            self.fstart = fcenter - (self.bandwidth / 2)
            if self.fstart < constants.MIN_FREQ:
                self.fstart = constants.MIN_FREQ
            self.fstop = fcenter + (self.bandwidth / 2)
            if self.fstop > constants.MAX_FREQ:    
                self.fstop = constants.MAX_FREQ
            self.bandwidth = self.fstop - self.fstart
            self.center_freq = self.fstart + (self.bandwidth / 2)
            self.bin_size = int((self.bandwidth) / self.rbw)
            if self.bin_size < 1:
                self.bin_size = 1
        
        elif fstart != None:
            if fstart >= self.fstop:
                fstart = self.fstop - constants.MIN_BW
            self.fstart = fstart
            self.bandwidth = self.fstop - fstart
            self.center_freq = fstart + (self.bandwidth / 2)
            self.bin_size = int((self.bandwidth) / self.rbw)
            if self.bin_size < 1:
                self.bin_size = 1
                
        elif fstop != None:
            if fstop <= self.fstart:
                fstop = self.fstart + constants.MIN_BW
            self.fstop = fstop
            self.bandwidth = fstop - self.fstart
            self.center_freq = fstop - (self.bandwidth / 2)
            self.bin_size = int((self.bandwidth) / self.rbw)
            if self.bin_size < 1:
                self.bin_size = 1
                
        elif rbw != None:
            self.rbw = rbw * 1e3
            self.bin_size = int((self.bandwidth) / self.rbw)
            if self.bin_size < 1:
                self.bin_size = 1
        
        elif bw != None:
            if bw < constants.MIN_BW:
                bw = constants.MIN_BW
            self.fstart = (self.center_freq - (bw / 2))
            self.fstop = (self.center_freq + (bw / 2))
            if self.fstart < constants.MIN_FREQ:
                self.fstart = constants.MIN_FREQ
            if self.fstop > constants.MAX_FREQ:    
                self.fstop = constants.MAX_FREQ
            self.bandwidth = self.fstop - self.fstart
            self.center_freq = self.fstart + (self.bandwidth / 2)
            self.bin_size = int((self.bandwidth) / self.rbw)
            if self.bin_size < 1:
                self.bin_size = 1
                
    def reset_freq_bounds(self):
            self.start_freq = None
            self.stop_freq = None

class debug(object):
    """
    Class to hold all the GUI's debug stats
    """

    def __init__(self,mode):
        self.enable = mode
        self.fps = 0
        self.fps_timer = 0
        
        self.data_bytes = 0
        self.data_captured = 0
        
        self.sweep_dev_acq_time = 0
        
        self.plot_runtime = 0 
        
        self.fft_time = 0
        self.fft_time_total = 0
        
        self.bin_calc_time = 0
        self.bin_calc_total = 0
        
        self.sweep_dev_min_points = constants.SWEEP_DEV_MIN_POINTS
        self.sweep_dev_max_points = constants.SWEEP_DEV_MAX_POINTS
        self.cap_speed = 0
        self.cap_speed_timer = 0
        
    def print_stats(self):
        x = 1
        # print 'fps: ', self.fps, 'plot time: ', self.plot_time
        # print 'fft time', self.fft_time, 'data acq  time', self.sweep_dev_acq_time
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
