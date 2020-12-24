#!/bin/bash

if [[ $# -eq 0 ]] ; then
    echo 'usage: ./deploy-and-run.sh <serial device> e.g. ./deploy-and-run.sh /dev/ttyACM0'
    exit 0
fi

set -x # echo on

bash deploy.sh "$1"
bash run.sh "$1"