"""Check the serial link to the Arduino, without the gateway or helicopter.

Opens the port, waits for the board to boot (opening resets most
Arduinos), then sends zero-throttle commands at --rate Hz for --seconds and
counts the firmware's echoes. Every command keeps throttle 0, so the IR
LEDs only ever tell a helicopter to stay down.

usage: python3 tools/link_check.py /dev/ttyUSB0 [--seconds 10] [--rate 10]
exit status: 0 if every packet was echoed back unchanged, 1 otherwise.
"""

import argparse
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / 'sungate' / 'rpi'))
import sssp  # noqa: E402

import serial  # noqa: E402

# yaw, pitch, throttle, trim: the flown neutrals with throttle 0
ZERO = (60, 63, 0, 52)


def main(argv=None):
    parser = argparse.ArgumentParser(description='check the serial link to the sungate Arduino')
    parser.add_argument('port', help='serial device, e.g. /dev/ttyUSB0')
    parser.add_argument('--baud', type=int, default=9600)
    parser.add_argument('--seconds', type=float, default=10.0)
    parser.add_argument('--rate', type=float, default=10.0, help='packets per second')
    parser.add_argument('--boot-wait', type=float, default=2.5, help='seconds to wait after opening')
    args = parser.parse_args(argv)

    port = serial.Serial(args.port, args.baud, timeout=0)
    print(f'opened {args.port} @ {args.baud}; waiting {args.boot_wait} s for the board to boot')
    time.sleep(args.boot_wait)
    port.reset_input_buffer()

    decoder = sssp.Decoder()
    # Vary trim so each packet is distinguishable in the echo (52..55).
    sent, echoes = [], []
    period = 1.0 / args.rate
    end = time.monotonic() + args.seconds
    next_send = time.monotonic()
    while time.monotonic() < end:
        now = time.monotonic()
        if now >= next_send:
            command = ZERO[:3] + (ZERO[3] + len(sent) % 4,)
            port.write(sssp.encode(command))
            sent.append(command)
            next_send += period
        waiting = port.in_waiting
        if waiting:
            echoes += decoder.feed_bytes(port.read(waiting))
        time.sleep(0.005)
    drain_end = time.monotonic() + 0.5
    while time.monotonic() < drain_end:
        waiting = port.in_waiting
        if waiting:
            echoes += decoder.feed_bytes(port.read(waiting))
        time.sleep(0.01)
    port.close()

    matched = sum(1 for a, b in zip(sent, echoes) if a == b)
    print(f'sent {len(sent)}, echoed {len(echoes)}, matching in order {matched}, '
          f'rejected echo bytes {decoder.rejected}')
    ok = len(sent) > 0 and len(echoes) == len(sent) and matched == len(sent)
    print('link OK' if ok else 'link NOT OK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
