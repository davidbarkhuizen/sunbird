#!/bin/bash
# Compile and upload the sketch with arduino-cli.
# FQBN defaults to a Nano with the old bootloader (most clones); for a
# Nano with the new bootloader use FQBN=arduino:avr:nano, for an Uno
# FQBN=arduino:avr:uno.

if [[ $# -eq 0 ]] ; then
    echo 'usage: ./deploy.sh <serial device> e.g. ./deploy.sh /dev/ttyUSB0'
    exit 0
fi

FQBN="${FQBN:-arduino:avr:nano:cpu=atmega328old}"
cd "$(dirname "$0")" || exit 1

set -x # echo on

arduino-cli compile --upload --port "$1" --fqbn "$FQBN" arduino/sungate
