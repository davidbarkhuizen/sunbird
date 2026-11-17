"""Super simple serial protocol (SSSP), host side.

Mirrors sungate/arduino/sungate/sssp.h: a packet is H1, H2, DATA_LENGTH,
4 data bytes, then the sum of the data bytes mod 256. The data bytes are
the IR command in wire order: leftright (yaw), fwdback (pitch), throttle,
calib (trim).
"""

H1 = 17
H2 = 171
DATA_LENGTH = 4
PACKET_LENGTH = 3 + DATA_LENGTH + 1


def checksum(data):
    return sum(data) % 256


def encode(data):
    """Returns the packet for 4 data bytes (ints 0..255) as bytes."""
    data = list(data)
    if len(data) != DATA_LENGTH:
        raise ValueError(f'expected {DATA_LENGTH} data bytes, got {len(data)}')
    for value in data:
        if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 255:
            raise ValueError(f'data bytes must be ints in 0..255, got {value!r}')
    return bytes([H1, H2, DATA_LENGTH, *data, checksum(data)])


class Decoder:
    """Streaming decoder with the firmware's state machine."""

    _WAIT_H1, _WAIT_H2, _WAIT_LENGTH, _WAIT_DATA, _WAIT_CHECKSUM = range(5)

    def __init__(self):
        self._state = self._WAIT_H1
        self._buffer = []
        self.accepted = 0
        self.rejected = 0

    def feed(self, b):
        """Feeds one byte; returns the data tuple when it completes a valid packet."""
        state = self._state
        if state == self._WAIT_H1:
            if b == H1:
                self._state = self._WAIT_H2
        elif state == self._WAIT_H2:
            if b == H2:
                self._state = self._WAIT_LENGTH
            elif b != H1:
                self._state = self._WAIT_H1
        elif state == self._WAIT_LENGTH:
            if b == DATA_LENGTH:
                self._state = self._WAIT_DATA
                self._buffer = []
            else:
                self.rejected += 1
                self._state = self._WAIT_H2 if b == H1 else self._WAIT_H1
        elif state == self._WAIT_DATA:
            self._buffer.append(b)
            if len(self._buffer) == DATA_LENGTH:
                self._state = self._WAIT_CHECKSUM
        else:
            if b == checksum(self._buffer):
                self.accepted += 1
                self._state = self._WAIT_H1
                return tuple(self._buffer)
            self.rejected += 1
            self._state = self._WAIT_H2 if b == H1 else self._WAIT_H1
        return None

    def feed_bytes(self, data):
        """Feeds bytes; returns the list of decoded data tuples."""
        out = []
        for b in data:
            packet = self.feed(b)
            if packet is not None:
                out.append(packet)
        return out
