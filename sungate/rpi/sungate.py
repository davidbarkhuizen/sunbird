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

# ------------------------------------------

def command(throttle, leftright, fwdback):
    # throttle      [0, 255]
    # leftright     [-64, 63]
    # fwdback       [-128, 127]

    t = struct.pack('>B', throttle)[0]
    lr = struct.pack('>b', leftright)[0]
    fb = struct.pack('>b', fwdback)[0]

    return [t, lr, fb]

app = Flask(__name__)

@app.route('/', methods = ['GET'])
def get():
    return 'sunbird-server'

@app.route('/', methods = ['POST'])
def post():

    j = request.json
    print(f'command received via HTTP POST: {j}')

    # throttle      [0, 255]
    # leftright     [-64, 63]
    # fwdback       [-128, 127]

    throttle=j['throttle']
    leftright=j['leftright']
    fwdback=j['fwdback']
    calib=j['calib']

    ords = [leftright, fwdback, throttle, calib]
    packed = [struct.pack('>B', o)[0] for o in ords]
    ba = bytearray(packed)
    ser.write(ba)
    print('sent:', [b for b in ba])
    
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 

# -----------------------------------

print('-' * 80)
print(f'sunbird-server :{port} -> {serialInterface} ({baudRate} kb/s)')
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