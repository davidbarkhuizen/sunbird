
# header

# 11111111111111111111111111111111111111111
# 0000000000000000000000000000000000000000

# 4 bytes

# 11111 0000 000					1
# 11111 0000 000 00000000			0
# 11111 1000000					    1
# 11111 10000000					1
# 11111 0000000					    1
# 11111 100000					    1
# 11111 10000000 000000000		    0
# 11111 10000						1

"""Decode captured S107G IR commands into bytes.

Input: a text file, one capture per line, each a string of '0' and '1'
samples. The bit threshold below (12 samples) depends on the capture's
sample rate; check it against a known command before trusting the output.

usage: python3 tools/decode_capture.py [path] [--step]
"""

import argparse

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

parser = argparse.ArgumentParser(description='decode captured S107G IR commands')
parser.add_argument('path', nargs='?', default='input/in.raw', help='capture file (default input/in.raw)')
parser.add_argument('--step', action='store_true', help='pause after each capture')
args = parser.parse_args()
fileName = args.path

lines = []
with open(fileName, 'r') as inFile:
    lines = inFile.readlines()

print(f'{len(lines)} lines')

def cut_next_bit(stream):
    h1 = stream.find('0')
    h2 = stream.find('1', h1)
 
    if h1 == -1 or h2 == -1:
        return stream, ''

    return stream[:h2], stream[h2:]

def parse_bit(raw):
    z = raw.find('0')
    ones = raw[:z]
    zeros = raw[z:]
    return not (len(zeros) > 12)

for line in lines:

    splut = []

    sections = line.split('01')
    count = len(sections)
    for i in range(count):
        
        if i == 0:
            splut.append(sections[i] + '0')
        elif i == count - 1:
            splut.append('1' + sections[i])
        else:
            splut.append('1' + sections[i] + '0')

        print(splut[-1:][0].count('1'), splut[-1:][0].count('0'), splut[-1:][0])



    stream = line
    header, body = cut_next_bit(stream)

    raw_bit_stream = []

    remainder = body
    while (remainder != ''):
        bit, remainder = cut_next_bit(remainder)
        raw_bit_stream.append(bit)

    bit_stream = [parse_bit(bit) for bit in raw_bit_stream]

    print(len(bit_stream))

    parsed = [
        int(''.join(['1' if bit else '0' for bit in byte]), 2) 
        for byte 
        in chunks(bit_stream[:-1], 8)
    ]

    print(parsed)

    if args.step:
        input()
