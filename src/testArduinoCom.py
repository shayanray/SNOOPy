import serial
import time

ser = serial.Serial('COM4')
ser.write(7)

#res = ser.read()
#print(res)

'''
ser = serial.Serial('COM1', 9600, timeout=0)
var = raw_input("Enter something: ")
ser.write(var)

while 1:
    try:
        print ser.readline()
        time.sleep(1)
    except ser.SerialTimeoutException:
        print('Data could not be read')
'''