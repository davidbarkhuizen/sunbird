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
    print(f'HTTP POST: {command}')
    try:
        r = requests.post(url, json=command)
    except requests.exceptions.ConnectionError as e:
        print(e)
        return False
        pass
    print(f'HTTP status code: {r.status_code}')
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
thover = 90 # med battery

tdescend = 50

ZERO_THROTTLE = 0
ZERO_LEFT_RIGHT = 63
ZERO_FWD_BACK = 63
ZERO_CALIB = 52

MIN_THROTTLE = 30

calib = 52

CMD = {
    'ZERO': { 'throttle': ZERO_THROTTLE, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT, 'calib': ZERO_CALIB },
    'WARMUP': { 'throttle': MIN_THROTTLE, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT, 'calib': ZERO_CALIB }
}


def warmup(url):
    sendCommand(url, CMD["ZERO"])
    time.sleep(2)
    sendCommand(url, CMD["WARMUP"])
    time.sleep(4)
    sendCommand(url, CMD["ZERO"])

warmup(f'http://{host}:{port}')