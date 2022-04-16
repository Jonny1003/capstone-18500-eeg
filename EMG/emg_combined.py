import serial
# import pydispatch import Dispatcher

def start_bluetooth():
    bluetooth = serial.Serial(port='/dev/tty.DSDTECHHC-05', baudrate=9600)
    return bluetooth


def detectEMG(dispatch, bluetooth, stdR, stdL, aveR, aveL):
    rightBuf = [0] * 200
    leftBuf = [0] * 200

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
            rightBuf[offsetR] = data
            offsetR += 1

            #check every time the buf is filled
            if (offsetR == bufSize-1):
                stdDataR = np.std(rightBuf)
                aveDataR = np.ave(rightBuf)
                ratioR = aveDataR / aveR
                #event 
                if (stdDataR > 2 and ratioR > 2.5):
                    dispatch.emit("right_emg", data)
                offsetR = 0 #reset the offset

                #print("In left", data)
            
    
        elif (data[0] == 'l'):
            data = int(data[1:])
            leftBuf[offsetL] = data
            offsetL += 1
            
            #check every time the buf is filled
            if (offsetL == bufSize-1):
                stdDataL = np.std(leftBuf)
                aveDataL = np.ave(leftBuf)
                ratioL = aveDataL / aveL
                #event 
                if (stdR > 2 and ratioR > 2.5):
                    dispatch.emit("right_emg", data)
                offsetL = 0 #reset the offset
            
            print("in right", data)


def emgCalib(bluetooth):
    ################ calibration ##############

    bufSize = 5000
    calibBufRight = [0] * bufSize  # 5000 ints
    calibBufLeft = [0] * bufSize  # 5000 ints
    stdCalib = 100            #dummyValue
    while (stdR > 0.5 or stdL > 0.5):
        rightIdx = 0
        leftIdx = 0
        while rightIdx < bufSize and leftIdx < bufSize:
            EMG_value = bluetooth.readline()
            data = EMG_value.decode()

            if (data[0] == 'r'):
                value = int(data[1:])
                calibBufRight[rightIdx] = value
                rightIdx += 1
        
            elif (data[0] == 'l'):
                value = int(data[1:])
                calibBufLeft[leftIdx] = value
                leftIdx += 1

            # if (EMG_value != None):
            #     # value = EMG_value * 1024
            #     print(EMG_value, value)
            #     calibBuf[i] = value
            #     i += 1
            #print(type(calibBuf[0]))
            #print("Calibrating value", calibBuf[i])

        # print(calibBuf)
        # print(type(calibBuf[0]))
        stdR = np.std(calibBufRight)
        aveR = np.average(calibBufRight)
        stdL = np.std(calibBufLeft)
        aveL = np.average(calibBufLeft)
    
    return [stdR, stdL, aveR, aveL]




