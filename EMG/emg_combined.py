import serial
import numpy as np
import time
# import pydispatch import Dispatcher


def start_bluetooth():
    bluetooth = serial.Serial(port='/dev/tty.DSDTECHHC-05', baudrate=9600)
    print("bluetooth")
    EMG_value = bluetooth.readline()
    print(EMG_value)
    return bluetooth


def detectEMG(dispatch, bluetooth, stdR, stdL, aveR, aveL):

    bufSize = 10
    rightBuf = [0] * bufSize
    leftBuf = [0] * bufSize
    offsetR = 0
    offsetL = 0

    while 1:
        #also check that the data is available
        data_bytes = bluetooth.readline()
        data = data_bytes.decode()
        

        ####################### for reading per byte ###################
        #print(input_data.decode())
        #print(type(data))
        # if input_data == b'\n':
        #     foundEnd = 1
        # else:
        #     val_str = input_data.decode()
        #     val = val + val_str

        if (data[0] == 'r'):
            data = int(data[1:])
            # print('R', data)
            rightBuf[offsetR] = data
            offsetR += 1

            #check every time the buf is filled
            if (offsetR == bufSize-1):
                stdDataR = np.std(rightBuf)
                aveDataR = np.average(rightBuf)
                ratioR = aveDataR / aveR
                # print("Ratio R", ratioR)
                #event 
                if (stdDataR > 20 and ratioR > 1.3):
                    print('right_emg')
                    dispatch.emit("right_emg", data)
                offsetR = 0 #reset the offset

                #print("In left", data)
            
    
        elif (data[0] == 'l'):
            # print(data)
            data = int(data[1:])
            leftBuf[offsetL] = data
            offsetL += 1

            # print('L', data)

            
            #check every time the buf is filled
            if (offsetL == bufSize-1):
                stdDataL = np.std(leftBuf)
                aveDataL = np.average(leftBuf)
                ratioL = aveDataL / aveL
                # print("Ratio L", ratioL)
                #event 
                if (stdDataL > 20 and ratioL > 1.3):
                    print('left_emg')
                    dispatch.emit("left_emg", data)
                offsetL = 0 #reset the offset
            
        #     print("in right", data)


def emgCalib(bluetooth):
    ################ calibration ##############
    print("entered Calib")
    bufSize = 1000
    calibBufRight = [0] * bufSize  # 5000 ints
    calibBufLeft = [0] * bufSize  # 5000 ints
    #stdCalib = 100            #dummyValue
    stdR = 100
    stdL = 100
    print(time.time())
    while (stdR > 40 and stdL > 40):
        rightIdx = 0
        leftIdx = 0

        while rightIdx < bufSize or leftIdx < bufSize:
            EMG_value = bluetooth.readline()
            
            data = EMG_value.decode()

            # print(data)

            if (data[0] == 'r'):
                value = int(data[1:])
                calibBufRight[rightIdx] = value
                print("r:", value)
                rightIdx += 1
        
            elif (data[0] == 'l'):
                value = int(data[1:])
                calibBufLeft[leftIdx] = value
                leftIdx += 1
                print("l:", value)

            #print(type(calibBuf[0]))
            #print("Calibrating value", calibBuf[i])

        print(calibBufLeft)
        # print(type(calibBuf[0]))
        stdR = np.std(calibBufRight)
        aveR = np.average(calibBufRight)
        print("Right:", stdR, aveR)
        stdL = np.std(calibBufLeft)
        aveL = np.average(calibBufLeft)
        print("Left:", stdL, aveL)
    print(time.time())
    return [stdR, stdL, aveR, aveL]

