echo usage: deploy-sungate.sh <serial device> e.g. deploy-sungate.sh /dev/ttyACM0

arduino --upload arduino/sungate/sungate.ino --port "$1"
python3 sungate.py --host 0.0.0.0 --port 8888 --baud 9600 --serial "$1"