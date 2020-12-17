import serial
import time

print('initializing')
ser = serial.Serial("/dev/ttyACM0", 9600)  # ls /dev/tty/ACM*
ser.baudrate=9600
time.sleep(2)
print('initialized')

cmd = bytes([200,3,5])
ser.write(cmd)

while True:
	availableCount = ser.in_waiting
	
	if (availableCount > 0):
		received = ser.read(availableCount)
		print(received)
