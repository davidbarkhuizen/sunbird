#!/bin/bash

if [[ $# -eq 0 ]] ; then
    echo 'usage: ./deploy.sh <serial device> e.g. ./deploy.sh /dev/ttyACM0'
    exit 0
fi

set -x # echo on

arduino --upload arduino/sungate/sungate.ino --port "$1"