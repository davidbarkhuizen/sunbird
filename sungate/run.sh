#!/bin/bash
# Start the gateway. Uses the repo's .venv if there is one.

if [[ $# -eq 0 ]] ; then
    echo 'usage: ./run.sh <serial device> e.g. run.sh /dev/ttyUSB0'
    exit 0
fi

cd "$(dirname "$0")" || exit 1
PYTHON=python3
[[ -x ../.venv/bin/python ]] && PYTHON=../.venv/bin/python

set -x # echo on

"$PYTHON" rpi/sungate.py --host 0.0.0.0 --port 8888 --baud 9600 --serial "$1"
