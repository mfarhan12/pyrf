
from pyrf.devices.thinkrf import WSA4000
from pyrf.sweep_device import SweepDevice
import base64
import csv
import sys
import time
import math
import numpy as np

class playBack(object):
    """
   Class that is used to store FFT in a CSV file, or open an existing file with
   IQ/FFT data

    :param filename: name of file to open/create 
    """
    
    def __init__(self):
        self.csv_writer = None
        self.csv_reader = None
        self.file
    def make_header (self,start,stop,size):
        return [['start_freq', 'stop_freq', 'size'], [str(fstart), str(fstop), len(bins)]]
    
    def create_file(self, fileName = None):
        if fileName == None:
            fileName = 'derp.csv'
        self.file = open(fileName, 'wb')
        self.csv_writer = csv.writer(self.file)
        self.file_opened = True
        
    def save_data(self, start, stop, data):
        if self.file_opened:
            header = self.make_header(start,stop,len(data))
            b64 = base64.b64encode(str(data))

            for h in header:
                self.csv_writer.writerow(h)
            self.csv_writer.writerow([b64])
        
    def close_file(self):
        self.file_opened = False
        self.file.close()
        self.csv_writer = None
        self.csv_reader = None
        
    def open_file(self, fileName):
        self.file = open(fileName, 'rb')
        self.csv_reader = csv.reader(self.file)
        self.fi
        
# connect to wsa
dut = WSA4000()
dut.connect(sys.argv[1])
sd = SweepDevice(dut)
fstart, fstop, bins = sd.capture_power_spectrum(5300e6, 5500e6, 2000, rfgain ='high', antenna = 2)
pb = playBack()
pb.create_file()
pb.save_data(fstart,fstop,bins)
pb.close_file()