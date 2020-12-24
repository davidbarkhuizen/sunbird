# Thrust
# spin but not take off 
# => T = 20
# 
# 
# take off and hover
# full battery => 80
# low battery => 100
# 
# T = 150 => nothing ?

import argparse

parser = argparse.ArgumentParser(description='sungate control client')
parser.add_argument('--host', help='sungate host')
parser.add_argument('--port', help='sungate port')
args = parser.parse_args()
host = args.host 
port = args.port

import requests
import time

def sendCommand(url, command):
    print(command)
    r = requests.post(url, json=command)
    return r.status_code == 200

def takeOffAndLandNoHover(url):
    sendCommand(url, { 'throttle': 0, 'fwdback': 0, 'leftright': 0 })
    time.sleep(1)
    sendCommand(url, { 'throttle': 80, 'fwdback': 0, 'leftright': 0 })
    time.sleep(1)
    sendCommand(url, { 'throttle': 0, 'fwdback': 0, 'leftright': 0 })

def fwd(url):
    sendCommand(url, { 'throttle': 0, 'fwdback': 0, 'leftright': 0 })
    time.sleep(2)
    sendCommand(url, { 'throttle': 20, 'fwdback': 0, 'leftright': 0 })
    time.sleep(4)
    sendCommand(url, { 'throttle': 100, 'fwdback': 0, 'leftright': 0 })
    time.sleep(4)
    sendCommand(url, { 'throttle': 100, 'fwdback': -20, 'leftright': 0 })
    time.sleep(2)
    sendCommand(url, { 'throttle': 100, 'fwdback': 0, 'leftright': 0 })
    time.sleep(4)
    sendCommand(url, { 'throttle': 0, 'fwdback': 0, 'leftright': 0 })

thover = 100 # full battery
thover = 80 # empty battery
tdescend = 50

def leftright(url):
    sendCommand(url, { 'throttle': 0, 'fwdback': 0, 'leftright': 0 })
    time.sleep(2)
    sendCommand(url, { 'throttle': 20, 'fwdback': 0, 'leftright': 0 })
    time.sleep(4)
    sendCommand(url, { 'throttle': thover, 'fwdback': 0, 'leftright': 0 })
    time.sleep(3)
    sendCommand(url, { 'throttle': thover, 'fwdback': 0, 'leftright': 20 })
    time.sleep(2)
    sendCommand(url, { 'throttle': thover, 'fwdback': 0, 'leftright': -20 })
    time.sleep(2)
    sendCommand(url, { 'throttle': tdescend, 'fwdback': 0, 'leftright': 0 })
    time.sleep(2)
    sendCommand(url, { 'throttle': 0, 'fwdback': 0, 'leftright': 0 })

def test(url):

    for i in 

    sendCommand(url, { 'throttle': 0, 'fwdback': 0, 'leftright': 0 })
    time.sleep(2)


test(f'http://{host}:{port}')