import pyfirmata 
from pyfirmata import Arduino
import time

board = pyfirmata.Arduino('/dev/cu.usbmodem141301')

it = pyfirmata.util.Iterator(board)
it.start()

A0_analog = board.get_pin('a:0:i')   #input pin A0

while True:
    EMG_value = A0_analog.read()
    if EMG_value is not None:
        print(EMG_value)
        #time.sleep(1)
        
    

