 #*- coding: UTF-8 -*-
 #encoding:utf-8
import numpy as np

def load_raw12(file):
    fp = open(file, 'rb')
    data = fp.read()
    fp.close()
    raw12_data = np.frombuffer(data, dtype=np.uint8)
    raw12_np_array1 = raw12_data[::2].reshape((2181,
                                               3840))
    raw12_np_array2 = raw12_data[1::2].reshape((2181,
                                                3840))
    return raw12_np_array1, raw12_np_array2

def load_raw8(file):
    fp = open(file, 'rb')
    data = fp.read()
    fp.close()
    raw24_data = np.frombuffer(data[:3840*2160], dtype=np.uint8)
    raw24_np_array = raw24_data.reshape((2160,
                                        3840))
        
    return self._raw24_np_array

def load_rgb888(file):
    fp = open(file, 'rb')
    data = fp.read()
    fp.close()
    raw24_data = np.frombuffer(data, dtype=np.uint8)
    raw24_data = raw24_data.reshape((2160, 3840 , 3))
    return raw24_data

def load_raw24(file):
    fp = open(file, 'rb')
    data = fp.read()
    fp.close()
    raw24_data = np.frombuffer(data, dtype=np.uint8)
    raw24_np_array = raw24_data.reshape((2160,
                                        3840*3))
    return raw24_np_array