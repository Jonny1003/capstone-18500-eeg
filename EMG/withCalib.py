import pyfirmata 
from pyfirmata import Arduino
import time
import numpy as np

board = pyfirmata.Arduino('/dev/cu.usbmodem143401')

it = pyfirmata.util.Iterator(board)
it.start()

A0_analog = board.get_pin('a:0:i')   #input pin A0

################ calibration ##############

bufSize = 5000
calibBuf = [1] * bufSize  # 5000 ints
stdCalib = 100            #dummyValue
while (stdCalib > 0.5):
    i = 0
    while i < bufSize:
        EMG_value = A0_analog.read()
        if (EMG_value != None):
            value = EMG_value * 1024
            print(EMG_value, value)
            calibBuf[i] = value
            i += 1
        #print(type(calibBuf[0]))
        #print("Calibrating value", calibBuf[i])

    print(calibBuf)
    # print(type(calibBuf[0]))
    stdCalib = np.std(calibBuf)
    aveCalib = np.average(calibBuf)
    print("std is", stdCalib)

############ reading normal data ############
dataBufSize = 500
dataBuf = [1] * dataBufSize
i = 0
while True:
    while i < dataBufSize:
        EMG_value = A0_analog.read()
        if (EMG_value != None):
            value = EMG_value * 1024    #rescaling
            #print(EMG_value, value)
            dataBuf[i] = value
            i += 1
    stdData = np.std(dataBuf)
    aveData = np.std(dataBuf)
    ratio = aveData / aveCalib
    if (stdData > 2 and ratio > 2.5):  #the other way is to not use 
       #event movement

