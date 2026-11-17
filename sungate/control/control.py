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

ZERO_THROTTLE = 0
ZERO_LEFT_RIGHT = 63 - 3
ZERO_FWD_BACK = 63
ZERO_CALIB = 52

MIN_THROTTLE = 20

# T-ASCEND
#
T_ASCEND_LOW_BATTERY = 120 # empty battery
T_ASCEND_MED_BATTERY = 100 # med battery
T_ASCEND_HIGH_BATTERY = 80 # full battery
#
T_ASCEND = 100

# T-HOVER
#
T_HOVER = T_ASCEND - 5

# T-DESCEND
#
T_DESCEND = T_HOVER - 5

LR_OFFSET = 10

CMD = {
    'ZERO': { 'throttle': ZERO_THROTTLE, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT, 'calib': ZERO_CALIB },
    'WARMUP': { 'throttle': MIN_THROTTLE, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT, 'calib': ZERO_CALIB },
    'ASCEND': { 'throttle': T_ASCEND, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT, 'calib': ZERO_CALIB },
    'HOVER': { 'throttle': T_HOVER, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT, 'calib': ZERO_CALIB },
    'HOVER_LEFT': { 'throttle': T_HOVER, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT - LR_OFFSET, 'calib': ZERO_CALIB },
    'HOVER_RIGHT': { 'throttle': T_HOVER, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT + LR_OFFSET, 'calib': ZERO_CALIB },
    'DESCEND': { 'throttle': T_DESCEND, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT, 'calib': ZERO_CALIB },

}

def shutdown(url):
    sendCommand(url, CMD["ZERO"])

def warmup(url):
    sendCommand(url, CMD["ZERO"])
    time.sleep(2)
    sendCommand(url, CMD["WARMUP"])
    time.sleep(2)

def takeoff(url):
    sendCommand(url, CMD["ASCEND"])
    time.sleep(4)
    sendCommand(url, CMD["HOVER"])
    time.sleep(2)

def hover(url):
    sendCommand(url, CMD["HOVER"])
    time.sleep(2)
    # sendCommand(url, CMD["HOVER_LEFT"])
    # time.sleep(2)
    # sendCommand(url, CMD["HOVER_RIGHT"])
    time.sleep(2)

def descend(url):
    sendCommand(url, { 'throttle': T_DESCEND, 'fwdback': ZERO_FWD_BACK, 'leftright': ZERO_LEFT_RIGHT, 'calib': ZERO_CALIB })
    time.sleep(4)
    sendCommand(url, CMD['ZERO'])

url = f'http://{host}:{port}'

warmup(url)
takeoff(url)
hover(url)

descend(url)