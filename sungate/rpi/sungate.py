"""sungate: HTTP -> serial gateway for the Syma S107G.

POST / with JSON {"leftright", "fwdback", "throttle", "calib"}, each an
int 0..255 (wire values; see README for neutrals). The command is held
for --client-timeout seconds; resend it to keep it, or the link stops
sending and the Arduino's failsafe brings the helicopter down.

GET /status reports the link: current command, packets sent, echoes.
"""

import argparse
import threading

from flask import Flask, jsonify, request

import link as link_module

FIELDS = ('leftright', 'fwdback', 'throttle', 'calib')  # wire order


def parse_command(j):
    """Returns the 4 wire bytes from a JSON command, or raises ValueError."""
    if not isinstance(j, dict):
        raise ValueError('expected a JSON object')
    missing = [f for f in FIELDS if f not in j]
    if missing:
        raise ValueError(f'missing fields: {", ".join(missing)}')
    command = []
    for f in FIELDS:
        value = j[f]
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 255:
            raise ValueError(f'{f} must be an int in 0..255, got {value!r}')
        command.append(value)
    return command


def create_app(link):
    app = Flask(__name__)

    @app.route('/', methods=['GET'])
    def get():
        return 'sungate ground transmission station'

    @app.route('/status', methods=['GET'])
    def status():
        return jsonify(link.status())

    @app.route('/', methods=['POST'])
    def post():
        j = request.get_json(silent=True)
        print(f'HTTP-POST from {request.remote_addr}: {j}')
        try:
            command = parse_command(j)
        except ValueError as e:
            return jsonify({'success': False, 'error': str(e)}), 400
        link.set_command(command)
        return jsonify({'success': True})

    return app


def main(argv=None):
    parser = argparse.ArgumentParser(description='sunbird control gateway server')
    parser.add_argument('--host', default='127.0.0.1', help='host to serve as, e.g. 0.0.0.0 or 127.0.0.1')
    parser.add_argument('--port', type=int, default=8888, help='TCP/IP port to listen on')
    parser.add_argument('--serial', required=True, help='linux serial device, e.g. /dev/ttyACM0, /dev/ttyUSB1')
    parser.add_argument('--baud', type=int, default=9600, help='baud rate in bits per second')
    parser.add_argument('--keepalive', type=float, default=0.2,
                        help='seconds between resends of the current command (firmware failsafe: 1 s)')
    parser.add_argument('--client-timeout', type=float, default=1.0,
                        help='seconds a command is held without a resend from the client')
    args = parser.parse_args(argv)

    import serial  # here so tests import this module without pyserial's port

    print('initializing serial connection...')
    # Opening the port resets most Arduinos; packets sent while the
    # bootloader runs (~2 s) are lost and replaced by the keepalive.
    port = serial.Serial(args.serial, args.baud, timeout=0)
    print('initialized.')

    link = link_module.Link(port, keepalive_s=args.keepalive, client_timeout_s=args.client_timeout)
    stop = threading.Event()
    thread = threading.Thread(target=link.run, args=(stop,), daemon=True)
    thread.start()

    print('-' * 80)
    print(f'sungate relay station sungate:{args.port} -> {args.serial} @ {args.baud} baud')
    print('-' * 80)

    try:
        create_app(link).run(args.host, args.port, threaded=True)
    finally:
        stop.set()
        thread.join(timeout=1)
        port.close()


if __name__ == '__main__':
    main()
