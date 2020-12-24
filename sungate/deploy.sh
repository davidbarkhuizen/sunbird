# usage: deploy-sungate.sh <serial device> e.g. deploy-sungate.sh /dev/ttyACM0

arduino --upload arduino/sungate/sungate.ino --port "$1"