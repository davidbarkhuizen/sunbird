import argparse

from flask import Flask, request, jsonify, json
import os

import serial
import time
import struct

parser = argparse.ArgumentParser(description='sunbird control gateway server')
parser.add_argument('--host', help='host to server as, e.g. 0.0.0.0 or 127.0.0.1')
parser.add_argument('--port', help='TCIP/IP port to listen on')
parser.add_argument('--serial', help='linux serial device, e.g. /dev/ttyACM0, /dev/ttyUSB1')
parser.add_argument('--baud', help='baud rate in bits per second, e.g 9600')
args = parser.parse_args()

host = args.host 
port = args.port

serialInterface = args.serial
baudRate = args.baud 

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def get():
    return 'sunbird-server'

@app.route('/', methods = ['POST'])
def post():

    content = request.json
    print(f'command received via HTTP POST: {content}')

    # power       [0, 255]
    # leftRight   [-64, 63]
    # fwdRev      [-128, 127]

    cmd = [
        struct.pack('>B', content['thrust'])[0],
        struct.pack('>b', content['leftright'])[0],
        struct.pack('>b', content['fwdrev'])[0]
    ]

    print(f'transmitting command to ground station over serial interface: {cmd}',)
    ser.write(cmd)
    print('sent.')
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

# -----------------------------------

print('-' * 80)
print('sunbird-server [{serialInterface} @ {baudRate} kb/s]')
print('-' * 80)

print(f'initializing serial connection...')
ser = serial.Serial(serialInterface, baudRate)
ser.baudrate = baudRate
print('initialized.')

app.run(host, port)