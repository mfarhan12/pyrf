
from pyrf.devices.thinkrf import WSA4000
from pyrf.sweep_device import SweepDevice
import base64
import csv
import sys
import time
import datetime
import math
import numpy as np

LINES_PER_PACKET = 2
class playBack(object):
    """
   Class that is used to store FFT in a CSV file, or open an existing file with
   IQ/FFT data.

    :param filename: name of file to open/create 
    """
    
    def __init__(self, callback = None):
        self.file_opened = False
        self.callback = callback
        self.file = None
        self.csv_writer = None
        self.csv_reader = []
        self.number_lines = 0
        self.file_name = None
    def make_header (self,start,stop):
        return [[str(start), str(stop)]]
    
    def create_file(self, fileName = None):
        if fileName == None:
            fileName = 'Playback Captures' + '//' + str(datetime.datetime.now()) + '.csv'
            fileName = fileName.replace(':', '-')
        self.file = open(fileName, 'wb')
        self.csv_writer = csv.writer(self.file)
        self.file_opened = True
        
    def save_data(self, start, stop, data):
        
        if self.file_opened:
            header = self.make_header(start,stop)
            
            b64 = base64.b64encode(str(data))

            for h in header:
                self.csv_writer.writerow(h)
            self.csv_writer.writerow([b64])
        
    def close_file(self):
        self.file_opened = False
        self.file.close()
        self.csv_writer = None
        self.csv_reader = []
        self.curr_index = 0
        
        
    def open_file(self, fileName):
        self.file_name = fileName
        self.curr_index = 0
        
    def read_data(self):
        file = open(self.file_name, 'rb')
        num_lines = 0
        # print self.csv_reader
        for i, line in enumerate(file):
            # print i, self.curr_index
            num_lines += 1
            if i == self.curr_index:
                start = line
                stop = line
            elif i == self.curr_index + 1:
                raw_data = line

        
        decoded_data = base64.b64decode(raw_data)
        
        split_data  = decoded_data.split(', ')
        data = []
        for x in split_data:
            if "[" in x:
                x = x.replace("[","")
            if "]" in x:
                x = x.replace("]","")
            data.append(float(x))
                
        self.curr_index += LINES_PER_PACKET
        if self.curr_index >= num_lines:
            self.curr_index = 0
        file.close()
        if self.callback == None:
            return start,stop, data
        else:
            self.callback(start,stop,data)
            return