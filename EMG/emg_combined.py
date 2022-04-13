import serial
# import pydispatch import Dispatcher

def start_bluetooth():
    bluetooth = serial.Serial(port='/dev/tty.DSDTECHHC-05', baudrate=9600)
    return bluetooth


def detectEMG(dispatch, bluetooth):
    while 1:
        foundEnd = 0
        while (not foundEnd): #also check that the data is available
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

            if (data[0] == 'l'):
                #event
                data = int(data[1:])
                dispatch.emit("left_emg", data)
                print("In left", data)
        
            elif (data[0] == 'r'):
                #event
                data = int(data[1:])
                dispatch.emit("right_emg", data)
                print("in right", data)


def emgCalib(bluetooth):
    ################ calibration ##############

    bufSize = 5000
    calibBuf = [1] * bufSize  # 5000 ints
    stdCalib = 100            #dummyValue
    while (stdCalib > 0.5 or stdCalib == 100):
        i = 0
        while i < bufSize:
            EMG_value = bluetooth.readline()
            data = EMG_value.decode()

            if (data[0] == 'l'):
                #event
                data = int(data[1:])
        
            elif (data[0] == 'r'):
                #event
                data = int(data[1:])

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
    
    return (stdCalib, aveCalib)




