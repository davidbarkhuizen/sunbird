import link
import sssp


class FakePort:
    """Stands in for the serial port; echoes every valid packet like the firmware."""

    def __init__(self):
        self.written = bytearray()
        self._incoming = bytearray()
        self._decoder = sssp.Decoder()

    def write(self, data):
        self.written += data
        for packet in self._decoder.feed_bytes(data):
            self._incoming += sssp.encode(packet)

    @property
    def in_waiting(self):
        return len(self._incoming)

    def read(self, n):
        out, self._incoming = bytes(self._incoming[:n]), self._incoming[n:]
        return out


class Clock:
    def __init__(self):
        self.t = 100.0

    def __call__(self):
        return self.t


def make():
    port, clock = FakePort(), Clock()
    return port, clock, link.Link(port, keepalive_s=0.2, client_timeout_s=1.0, clock=clock)


def packets(port):
    return sssp.Decoder().feed_bytes(port.written)


def test_sends_nothing_before_first_command():
    port, clock, l = make()
    l.step()
    assert port.written == b''


def test_sends_at_once_then_keepalive():
    port, clock, l = make()
    l.set_command([60, 63, 95, 52])
    l.step()
    assert packets(port) == [(60, 63, 95, 52)]
    clock.t += 0.1
    l.step()
    assert len(packets(port)) == 1
    clock.t += 0.15
    l.step()
    assert len(packets(port)) == 2
    assert l.echoed == 2
    assert l.status()['last_echo'] == (60, 63, 95, 52)


def test_new_command_sent_immediately():
    port, clock, l = make()
    l.set_command([60, 63, 95, 52])
    l.step()
    clock.t += 0.05
    l.set_command([60, 63, 0, 52])
    l.step()
    assert packets(port)[-1] == (60, 63, 0, 52)


def test_client_deadman_stops_sending():
    port, clock, l = make()
    l.set_command([60, 63, 95, 52])
    for _ in range(4):
        l.step()
        clock.t += 0.25
    assert l.status()['client_active'] is True  # 1.0 s: at the timeout, still held
    l.step()
    clock.t += 0.25
    sent = len(packets(port))
    assert l.status()['client_active'] is False
    for _ in range(10):
        clock.t += 0.2
        l.step()
    assert len(packets(port)) == sent
    l.set_command([60, 63, 95, 52])  # client back
    l.step()
    assert len(packets(port)) == sent + 1


def test_invalid_command_rejected_and_not_queued():
    port, clock, l = make()
    try:
        l.set_command([60, 63, 300, 52])
    except ValueError:
        pass
    else:
        raise AssertionError('expected ValueError')
    l.step()
    assert port.written == b''
