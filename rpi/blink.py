import serial
import time

ser=serial.Serial("/dev/ttyACM0",9600)  # ls /dev/tty/ACM*
ser.baudrate=9600

b = 0x32

ser.write(b)
print(b)
read_ser = ser.readline()
print(read_ser)