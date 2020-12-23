import argparse

from flask import Flask, request, jsonify, json
import os

import serial
import time
import struct

parser = argparse.ArgumentParser(description='sunbird control gateway server')
parser.add_argument('--port', help='linux serial device, e.g. /dev/ttyACM0, /dev/ttyUSB1')
parser.add_argument('--baud', help='baud rate in bits per second, e.g 9600')
args = parser.parse_args()

serialInterface = args.port
baudRate = args.baud 

def command(power, leftRight, fwdRev):
    # power       [0, 255]
    # leftRight   [-64, 63]
    # fwdRev      [-128, 127]

    p = struct.pack('>B', power)[0]
    lr = struct.pack('>b', leftRight)[0]
    fr = struct.pack('>b', fwdRev)[0]

    return [p, lr, fr]

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def get():
    return 'sunbird'

@app.route('/', methods = ['POST'])
def post():

    content = request.json
    print(f'command received: {content}')
    cmd = command(content['hover'], content['rotate'], content['thrust'])
    print('sending over serial...', cmd)
    ser.write(cmd)
    print('sent.')
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 


print(f'initializing serial connection on {serialInterface} @ {baudRate} baud rate...')
ser = serial.Serial(serialInterface, baudRate)
ser.baudrate = baudRate
print('initialized.')

app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'sunbird.sqlite'),
    )
app.run()