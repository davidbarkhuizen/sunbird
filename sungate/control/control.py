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
    time.sleep(1)
    # sendCommand(url, { 'throttle': 80, 'fwdback': 0, 'leftright': 0 })
    # time.sleep(1)
    sendCommand(url, { 'throttle': 80, 'fwdback': 10, 'leftright': 0 })
    time.sleep(3)
    sendCommand(url, { 'throttle': 0, 'fwdback': 0, 'leftright': 0 })


fwd(f'http://{host}:{port}')