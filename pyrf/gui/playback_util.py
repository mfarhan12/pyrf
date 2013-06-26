
from pyrf.devices.thinkrf import WSA4000
from pyrf.sweep_device import SweepDevice
import base64
import csv
import sys
import time
import datetime
import math
import numpy as np

LINES_PER_PACKET = 3
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
        
        
    def make_header (self,start,stop,size):
        return [['start_freq', 'stop_freq', 'size'], [str(start), str(stop), len(bins)]]
    
    def create_file(self, fileName = None):
        if fileName == None:
            fileName = str(datetime.datetime.now()) + '.csv'
            fileName = fileName.replace(':', '-')
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
        self.csv_reader = []
        self.curr_index = 0
        
    def open_file(self, fileName):
        self.file = open(fileName, 'rb')
        reader = csv.reader(self.file)
        for row in reader:
            self.csv_reader.append(row)
        # every packet has 3 lines (2 header, 1 for data)
        self.num_packets = len(self.csv_reader) / LINES_PER_PACKET
        self.curr_index = 0
        
    def read_data(self):
        # print self.csv_reader

        header = self.csv_reader[self.curr_index + 1] 
        start = header[0]
        stop = header[1]
        data = []
        raw_data = self.csv_reader[self.curr_index + 2] 

        decoded_data = base64.b64decode(raw_data[0])
        split_data  = decoded_data.split(', ')
        for x in split_data:
            if "[" in x:
                x = x.replace("[","")
            if "]" in x:
                x = x.replace("]","")
            data.append(float(x))
                
        self.curr_index += 3
        if self.curr_index >= (self.num_packets * LINES_PER_PACKET):
            self.curr_index = 0
        
        if self.callback == None:
            return start,stop,data
        else:
            time.sleep(0.1)
            self.callback(start,stop,data)
            return


