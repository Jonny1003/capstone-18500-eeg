import serial

bluetooth = serial.Serial(port='/dev/tty.DSDTECHHC-05', baudrate=9600)
print("Connected!!!!!!!!!!")
#size = 1024

while 1:
    # data = bluetooth.readline(size)
    # if data:
    #     print(data)
    # bluetooth.write(b'HI')
    
    #bluetooth.write(1)     # write a string
    foundEnd = 0
    val = ''
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
            data = int(data[1:])
            print("In left", data)
    
        elif (data[0] == 'r'):
            data = int(data[1:])
            print("in right", data)


