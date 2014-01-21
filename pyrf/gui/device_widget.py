from PySide import QtGui

WSA5000_RFE_MODES = ['ZIF', 'SH', 'HDR']

class DeviceControlsWidget(QtGui.QGroupBox):

    """
    A widget based from the Qt QGroupBox widget with a layout containing widgets that
    can be used to control the WSA4000/WSA5000
    :param name: The name of the groupBox
    
    Note: All the widgets inside this groupBox are not connected to any controls, and must be
    connected within the parent layout.

"""
    def __init__(self, name = "Device Control"):
        super(DeviceControlsWidget, self).__init__()       
        
        self.setTitle(name)
        
        dev_layout = QtGui.QVBoxLayout(self)
        
        first_row = QtGui.QHBoxLayout()
        first_row.addWidget(self._attenuator_control())
        first_row.addWidget(self._rfe_mode_control())
        first_row.addWidget(self._antenna_control())
        first_row.addWidget(self._trigger_control())
        
        second_row = QtGui.QHBoxLayout()
        second_row.addWidget(self._decimation_control())
        
        fshift_lable, fshift_edit, fshift_unit = self._freq_shift_control()
        second_row.addWidget(fshift_lable)
        second_row.addWidget(fshift_edit)
        second_row.addWidget(fshift_unit)
        
        second_row.addWidget(self._gain_control())
        second_row.addWidget(self._ifgain_control())
        
        dev_layout.addLayout(first_row)
        dev_layout.addLayout(second_row)

        self.setLayout(dev_layout)         
        self.layout = dev_layout
    
    def _antenna_control(self):
        antenna = QtGui.QComboBox(self)
        antenna.setToolTip("Choose Antenna") 
        antenna.addItem("Antenna 1")
        antenna.addItem("Antenna 2")
        self._antenna_box = antenna
        return antenna
    
    def _decimation_control(self):
        dec = QtGui.QComboBox(self)
        dec.setToolTip("Choose Decimation Rate") 
        dec_values = ['1', '4', '8', '16', '32', '64', '128', '256', '512', '1024']
        for d in dec_values:
            dec.addItem("Decimation Rate: %s" % d)
        self._dec_values = dec_values
        self._dec_box = dec
        return dec
        
    def _freq_shift_control(self):
        fshift_label = QtGui.QLabel("Frequency Shift")
        self._fshift_label = fshift_label
        
        fshift_unit = QtGui.QLabel("MHz")
        self._fshift_unit = fshift_unit
        
        fshift = QtGui.QLineEdit("0")
        fshift.setToolTip("Frequency Shift") 
        self._freq_shift_edit = fshift
        
        return fshift_label, fshift, fshift_unit
        
    def _gain_control(self):
        gain = QtGui.QComboBox(self)
        gain.setToolTip("Choose RF Gain setting") 
        gain_values = ['VLow', 'Low', 'Med', 'High']
        for g in gain_values:
            gain.addItem("RF Gain: %s" % g)
        self._gain_values = [g.lower() for g in gain_values]
        self._gain_box = gain
        return gain

    def _ifgain_control(self):
        ifgain = QtGui.QSpinBox(self)
        ifgain.setToolTip("Choose IF Gain setting")
        ifgain.setRange(-10, 25)
        ifgain.setSuffix(" dB")
        self._ifgain_box = ifgain
        return ifgain
    
    def _trigger_control(self):
        trigger = QtGui.QCheckBox("Trigger")
        trigger.setToolTip("[T]\nTurn the Triggers on/off") 
        self._trigger = trigger
        return trigger

    def _attenuator_control(self):
        attenuator = QtGui.QCheckBox("Attenuator")
        attenuator.setChecked(True)
        self._attenuator_box = attenuator
        return attenuator
        
    def _rfe_mode_control(self):
        rfe_mode = QtGui.QComboBox()
        rfe_mode.setToolTip("Change the Input mode of the WSA")
        self._rfe_mode = rfe_mode
        for mode in WSA5000_RFE_MODES:
            
            rfe_mode.addItem(mode)
        return rfe_mode
        
