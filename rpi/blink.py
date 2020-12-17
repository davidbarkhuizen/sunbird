import serial
import time

ser=serial.Serial("/dev/ttyACM0",9600)  # ls /dev/tty/ACM*
ser.baudrate=9600

ser.write(100)
read_ser = ser.readline()
print(read_ser)