if [[ $# -eq 0 ]] ; then
    echo 'usage: ./run.sh <serial device> e.g. run.sh /dev/ttyACM0'
    exit 0
fi

python3 rpi/sungate.py --host 0.0.0.0 --port 8888 --baud 9600 --serial "$1"