import argparse

from flask import Flask, request, jsonify, json
import os

import serial
import time
import struct

import multiprocessing

parser = argparse.ArgumentParser(description='sunbird control gateway server')
parser.add_argument('--host', help='host to server as, e.g. 0.0.0.0 or 127.0.0.1')
parser.add_argument('--port', help='TCIP/IP port to listen on')
parser.add_argument('--serial', help='linux serial device, e.g. /dev/ttyACM0, /dev/ttyUSB1')
parser.add_argument('--baud', help='baud rate in bits per second, e.g 9600')
args = parser.parse_args()

host = args.host 
port = args.port

# ------------------------------------------

serialInterface = args.serial
baudRate = args.baud 

print(f'initializing serial connection...')
ser = serial.Serial(serialInterface, baudRate)
ser.baudrate = baudRate
print('initialized.')

def encode(data):

    header = [17, 171]
    length = 4

    trailer = sum(data) % 256

    return [struct.pack('>B', x)[0] for x in [header[0], header[1], length, *data, trailer]]

# ------------------------------------------

def renderCommandByteArray(leftright, fwdback, throttle, calib):
    '''
    leftright       byte    0..255
    fwdback         byte    0..255
    throttle        byte    0..255
    calib           byte    0..255
    '''
    ords = [leftright, fwdback, throttle, calib]
    packed = [struct.pack('>B', o)[0] for o in ords]
    return bytearray(packed)

# ------------------------------------------

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def get():
    return 'sungate ground transmission station'

@app.route('/', methods = ['POST'])
def post():

    j = request.json
    print(f'HTTP-POST from {request.remote_addr}: {j}')

    throttle=j['throttle']
    leftright=j['leftright']
    fwdback=j['fwdback']
    calib=j['calib']

    cmd = renderCommandByteArray(leftright, fwdback, throttle, calib)
    print('raw command:', [b for b in cmd])
    encoded = encode(cmd)
    print('encoded', [b for b in encoded])
    ser.write(encoded)
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

# -----------------------------------

print('-' * 80)
print(f'sungate relay station http://sungate:{port} -> {serialInterface} @ {baudRate} kb/s)')
print('-' * 80)

def startServer():
    app.run(host, port)

p = multiprocessing.Process(target=startServer)
p.start()

try:
    while True:
        time.sleep(0.1)

        charCount = ser.inWaiting()
        if charCount >= 4:
            cmd = ser.read(4)        
           
            print([str(x) for x in cmd])

finally:
    ser.close()