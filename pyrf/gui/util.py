import os
import  control_util 
import numpy as np
import constants
from PySide import QtGui, QtCore
def frequency_text(hz):
    """
    return hz as readable text in Hz, kHz, MHz or GHz
    """
    if hz < 1e3:
        return "%.3f Hz" % hz
    elif hz < 1e6:
        return "%.3f kHz" % (hz / 1e3)
    elif hz < 1e9:
        return "%.3f MHz" % (hz / 1e6)
    return "%.3f GHz" % (hz / 1e9)
    
def hotkey_util(layout,event):
    """
    modify elements in the gui layout based on which key was pressed
    """
    if control_util.arrow_dict.has_key(str(event.key())):
        hotkey =  control_util.arrow_dict[str(event.key())]
    else:
        hotkey = str(event.text()).upper()
    if control_util.hotkey_dict.has_key(hotkey):
        control_util.hotkey_dict[hotkey](layout)
        
def find_max_index(array):
    """
    returns the maximum index of an array         
    """
    # keep track of max index
    index = 0
    
    array_size = len(array)
    
    max_value = 0
    for i in range(array_size):
        
        if i == 0:
            max_value = array[i]
            index = i
        elif array[i] > max_value:
            max_value = array[i]
            index = i
    return index

def find_nearest_index(value, array):
    """
    returns the index in the array of the nearest value      
    """
    idx = (np.abs(array-value)).argmin()
    return idx
def update_playback_list(layout):

    data_files = [(x[0], x[2]) for x in os.walk(layout.plot_state.playback_dir)]

    if (data_files):
        layout.plot_state.playback_file_list = data_files[0][1]

        layout._playback_list.clear()
        for name in layout.plot_state.playback_file_list:
            if 'csv' in name and (name not in layout.plot_state.playback_ignore_list):
                file = open(os.path.join(layout.plot_state.playback_dir, name), 'r')
                header = file.readline()
                if 'Pyrf' in header: 
                    layout._playback_list.addItem(name)
            layout._playback_list.setCurrentRow(0)
            
def select_fstart(layout):
    layout._fstart.setStyleSheet('background-color: %s; color: white;' % constants.ORANGE)
    layout._cfreq.setStyleSheet("")
    layout._fstop.setStyleSheet("")
    layout._bw.setStyleSheet("")
    
def select_center(layout):
    layout._cfreq.setStyleSheet('background-color: %s; color: white;' % constants.ORANGE)
    layout._fstart.setStyleSheet("")
    layout._fstop.setStyleSheet("")
    layout._bw.setStyleSheet("")
    
def select_bw(layout):
    layout._bw.setStyleSheet('background-color: %s; color: white;' % constants.ORANGE)
    layout._fstart.setStyleSheet("")
    layout._cfreq.setStyleSheet("")
    layout._fstop.setStyleSheet("")

def select_fstop(layout):
    layout._fstop.setStyleSheet('background-color: %s; color: white;' % constants.ORANGE)
    layout._fstart.setStyleSheet("")
    layout._cfreq.setStyleSheet("")
    layout._bw.setStyleSheet("")
    
def change_item_color(item, textColor, backgroundColor):
    item.setStyleSheet("QPushButton{Background-color: %s; color: %s; } QToolButton{color: Black}" % (textColor, backgroundColor)) 

def enable_freq_cont(layout):
    layout._bw.setEnabled(True)
    layout._bw_edit.setEnabled(True)
    layout._fstart.setEnabled(True)
    layout._fstart_edit.setEnabled(True)
    layout._fstop.setEnabled(True)
    layout._fstop_edit.setEnabled(True)
    
def disable_freq_cont(layout):
    layout._bw.setEnabled(False)
    layout._bw_edit.setEnabled(False)
    layout._fstart.setEnabled(False)
    layout._fstart_edit.setEnabled(False)
    layout._fstop.setEnabled(False)
    layout._fstop_edit.setEnabled(False)

def change_icon(bt,im):
    # change the specified button's icon
    im_path = os.path.join("Icons", im) 
    icon = QtGui.QIcon(im_path);
    bt.setIcon(icon)
    bt.setIconSize(QtCore.QSize(constants.ICON_SIZE,constants.ICON_SIZE)); 


