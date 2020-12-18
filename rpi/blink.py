

import serial
import time
import struct

print('initializing serial connection...')
ser = serial.Serial("/dev/ttyACM0", 9600)  # ls /dev/tty/ACM*
ser.baudrate=9600
time.sleep(2)
print('serial connection initialized.')

def command(power, leftRight, fwdRev):
	# power       [0, 255]
	# leftRight   [-64, 63]
    # fwdRev      [-128, 127]
	
	p = struct.pack('>B', power)[0]
	lr = struct.pack('>b', leftRight)[0]
	fr = struct.pack('>b', fwdRev)[0]
	
	return [p, lr, fr]

cmd = command(20, 0, 0)
print(cmd)
ser.write(cmd)

while True:
	availableCount = ser.in_waiting
	
	if (availableCount > 0):
		received = ser.read(availableCount)
		print(received)
