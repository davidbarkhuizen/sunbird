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
import time

import requests


# Resend interval while holding a command. The gateway drops a command
# that isn't resent within its --client-timeout (default 1 s), after which
# the Arduino's failsafe brings the helicopter down.
KEEPALIVE_S = 0.25


def sendCommand(url, command):
    print(f'HTTP POST: {command}')
    try:
        r = requests.post(url, json=command, timeout=1)
    except requests.exceptions.RequestException as e:
        print(e)
        return False
    if r.status_code != 200:
        print(f'HTTP status code: {r.status_code} {r.text}')
    return r.status_code == 200


def hold(url, command, seconds, interval=KEEPALIVE_S, clock=time.monotonic, sleep=time.sleep):
    """Sends command and keeps resending it for seconds."""
    end = clock() + seconds
    while True:
        sendCommand(url, command)
        remaining = end - clock()
        if remaining <= 0:
            return
        sleep(min(interval, remaining))


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
    sendCommand(url, CMD['ZERO'])

def warmup(url):
    hold(url, CMD['ZERO'], 2)
    hold(url, CMD['WARMUP'], 2)

def takeoff(url):
    hold(url, CMD['ASCEND'], 4)
    hold(url, CMD['HOVER'], 2)

def hover(url):
    hold(url, CMD['HOVER'], 4)
    # hold(url, CMD['HOVER_LEFT'], 2)
    # hold(url, CMD['HOVER_RIGHT'], 2)

def descend(url):
    hold(url, CMD['DESCEND'], 4)
    sendCommand(url, CMD['ZERO'])


def main(argv=None):
    parser = argparse.ArgumentParser(description='sungate control client')
    parser.add_argument('--host', required=True, help='sungate host')
    parser.add_argument('--port', required=True, help='sungate port')
    args = parser.parse_args(argv)
    url = f'http://{args.host}:{args.port}'

    try:
        warmup(url)
        takeoff(url)
        hover(url)
        descend(url)
    except KeyboardInterrupt:
        # Ctrl-C is the operator's kill switch: cut throttle now. (A lost
        # client instead ramps down through the gateway and firmware.)
        print('interrupted: cutting throttle')
        shutdown(url)


if __name__ == '__main__':
    main()
