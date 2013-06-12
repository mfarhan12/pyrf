import constants
import numpy as np
from pyrf.config import TriggerSettings
class plot_state(object):
    """
    Class to hold all the GUI's plot states
    """

    def __init__(self):
        
        self.grid = False
        
        self.mhold = False
        self.mhold_fft = None
        self.trig = False
        
        self.marker = False
        self.marker_sel = False
        self.marker_ind = None
        
        self.delta = False
        self.delta_sel = False
        self.delta_ind = None
        self.peak = False
        
        self.freq_range = None
        self.points = constants.STARTUP_POINTS
        
        self.center_freq = None
        self.bandwidth = None
        self.decimation_factor = None
        self.decimation_points = None
        self.start_freq = None
        self.stop_freq = None
        
        self.enable_plot = True
        
        self.freq_sel = 'CENT'
    
    def enable_marker(self, layout):
        self.marker = True
        self.marker_sel = True
        change_item_color(layout._marker,  constants.ORANGE, constants.WHITE)
        layout._plot.add_marker()
        layout._marker.setDown(True)
        layout.update_marker()
        if layout.plot_state.delta_sel:
            self.delta_sel = False
            change_item_color(layout._delta,  constants.ORANGE, constants.WHITE)
            layout._delta.setDown(False)
            

    def disable_marker(self, layout):
        
        self.marker = False
        self.marker_sel = False
        change_item_color(layout._marker, constants.NORMAL_COLOR, constants.BLACK)
        layout._marker.setDown(False)
        layout._plot.remove_marker()
        layout._marker_lab.setText('')
        layout._plot.center_view(layout.plot_state.center_freq, layout.plot_state.bandwidth)
        if self.delta:
            self.enable_delta(layout)

    def enable_delta(self, layout):
        self.delta = True
        self.delta_sel = True
        change_item_color(layout._delta, constants.ORANGE, constants.WHITE)
        layout._plot.add_delta()
        layout._delta.setDown(True)
        
        if self.marker:
            self.marker_sel = False             
            change_item_color(layout._marker, constants.ORANGE, constants.WHITE)
            layout._marker.setDown(False)
            
    def disable_delta(self, layout):
        self.delta = False
        self.delta_sel = False
        change_item_color(layout._delta, constants.NORMAL_COLOR ,constants.BLACK)
        layout._delta.setDown(False)
        layout._plot.remove_delta()
        layout._delta_lab.setText('')
        layout._diff_lab.setText('')
        layout._plot.center_view(layout.plot_state.center_freq, layout.plot_state.bandwidth)
        if self.marker:
            self.enable_marker(layout)
    
    def enable_trig(self, layout):
        self.trig = True
        change_item_color(layout._trigger, constants.NORMAL_COLOR, constants.BLACK)
        layout._plot.remove_trigger()
        layout.plot_state.trig_set = TriggerSettings(constants.NONE_TRIGGER_TYPE,
                                                layout.plot_state.center_freq - 10e6, 
                                                layout.plot_state.center_freq + 10e6,-100) 
        layout.dut.trigger(layout.plot_state.trig_set)
        
    def disable_trig(self, layout):
        self.trig = False
        change_item_color(layout._trigger, constants.ORANGE,constants.WHITE)
        layout.plot_state.trig_set = TriggerSettings(constants.LEVELED_TRIGGER_TYPE,
                                                layout.plot_state.center_freq - 10e6, 
                                                layout.plot_state.center_freq + 10e6,-100) 
        layout.dut.trigger(layout.plot_state.trig_set)
        layout._plot.add_trigger(layout.plot_state.center_freq)
        
    def update_freq_range(self, start, stop, size):
        self.freq_range = np.linspace(start, stop, size)
        
    def update_freq(self,state):
        if state == 'CENT':
            self.start_freq = (self.center_freq) - (self.bandwidth / 2)
            self.stop_freq = (self.center_freq) + (self.bandwidth / 2)
        # TODO: UPDATE TO CHANGE FOR FSTART/FSTOP
    
    def reset_freq_bounds(self):
            self.start_freq = None
            self.stop_freq = None
            

def select_fstart(layout):
    layout._fstart.setStyleSheet('background-color: %s; color: white;' % constants.ORANGE)
    layout._cfreq.setStyleSheet("")
    layout._fstop.setStyleSheet("")

def select_center(layout):
    layout._cfreq.setStyleSheet('background-color: %s; color: white;' % constants.ORANGE)
    layout._fstart.setStyleSheet("")
    layout._fstop.setStyleSheet("")

def select_fstop(layout):
    layout._fstop.setStyleSheet('background-color: %s; color: white;' % constants.ORANGE)
    layout._fstart.setStyleSheet("")
    layout._cfreq.setStyleSheet("")

def change_item_color(item, textColor, backgroundColor):
        item.setStyleSheet("QPushButton{Background-color: %s; color: %s; } QToolButton{color: Black}" % (textColor, backgroundColor)) 

    