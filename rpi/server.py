from flask import Flask, request, jsonify, json
import os

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

app = Flask(__name__)
app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'sunbird.sqlite'),
    )

@app.route('/', methods = ['GET'])
def get():
    return 'sunbird'

@app.route('/', methods = ['POST'])
def post():

    content = request.json
    print(content)
   
    cmd = command(content['hover'], content['rotate'], content['thrust'])
    print('sending', cmd)
    ser.write(cmd)
    print('sent')
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
