"""Step the throttle through a list of levels via a running gateway.

Holds each level for --hold seconds (resending every 0.25 s, inside the
gateway's client timeout), then sends throttle 0 for 3 s. Yaw, pitch and
trim stay at the flown neutrals. Prints a timestamp at each step, so an
observer's "it moved" can be matched to a level.

To stop early, create the stop file (default ~/sunbird-runs/STOP): the run
drops to throttle 0 at the next resend. Ctrl-C does the same. The stop file
is removed at start, so a stale one doesn't end the next run.

Used on 2026-11-18 to find where the rotor starts: twitching at about 16,
spinning steadily at about 20 (see README, Bench results).

usage: python3 tools/throttle_steps.py 0 10 20 30 [--hold 10] [--url http://127.0.0.1:8888]
"""

import argparse
import datetime
import pathlib
import sys
import time

NEUTRAL = {'leftright': 60, 'fwdback': 63, 'calib': 52}
RESEND_S = 0.25
FINAL_ZERO_S = 3.0


def hold(send, throttle, seconds, stop_requested, clock=time.monotonic, sleep=time.sleep):
    """Resends throttle for seconds; returns False if a stop was requested."""
    end = clock() + seconds
    while clock() < end:
        if stop_requested():
            return False
        send(throttle)
        sleep(RESEND_S)
    return True


def run(levels, send, hold_s, stop_requested, log=print, clock=time.monotonic, sleep=time.sleep):
    """Steps through levels, then always finishes with throttle 0."""
    try:
        for level in levels:
            log(f'throttle {level}')
            if not hold(send, level, hold_s, stop_requested, clock, sleep):
                log(f'stop requested during throttle {level}')
                break
    finally:
        log('throttle 0')
        hold(send, 0, FINAL_ZERO_S, lambda: False, clock, sleep)
        log('done')


def level(text):
    value = int(text)
    if not 0 <= value <= 255:
        raise argparse.ArgumentTypeError(f'throttle must be in 0..255, got {value}')
    return value


def main(argv=None):
    parser = argparse.ArgumentParser(description='step the sungate throttle through levels')
    parser.add_argument('levels', nargs='+', type=level, help='throttle levels, in order')
    parser.add_argument('--hold', type=float, default=10.0, help='seconds at each level')
    parser.add_argument('--url', default='http://127.0.0.1:8888', help='gateway URL')
    parser.add_argument('--stop-file', default='~/sunbird-runs/STOP',
                        help='create this file to stop early')
    args = parser.parse_args(argv)

    import requests  # here so tests import this module without it

    stop_file = pathlib.Path(args.stop_file).expanduser()
    stop_file.unlink(missing_ok=True)

    def send(throttle):
        requests.post(args.url, json={**NEUTRAL, 'throttle': throttle}, timeout=1).raise_for_status()

    def log(message):
        print(datetime.datetime.now().strftime('%H:%M:%S'), message, flush=True)

    try:
        run(args.levels, send, args.hold, stop_file.exists, log=log)
    except KeyboardInterrupt:
        pass  # run()'s finally has already sent throttle 0
    return 0


if __name__ == '__main__':
    sys.exit(main())
