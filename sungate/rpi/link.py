"""The serial link to the Arduino: one thread owns the port.

The gateway hands commands to set_command(); the link thread writes them,
resends the current one every keepalive_s so the firmware's failsafe
stays off, and reads the firmware's echoes.

Client deadman: once client_timeout_s passes with no new command, the
link stops sending. The firmware then sees silence and its failsafe ramps
throttle down. So a client that dies or loses the network brings the
helicopter down; a client that wants to hold a command must resend it
(control.py's hold() does).
"""

import threading
import time

import sssp


class Link:

    def __init__(self, port, keepalive_s=0.2, client_timeout_s=1.0, clock=time.monotonic):
        self._port = port
        self._keepalive_s = keepalive_s
        self._client_timeout_s = client_timeout_s
        self._clock = clock
        self._lock = threading.Lock()
        self._decoder = sssp.Decoder()

        self._command = None
        self._command_at = None
        self._send_now = False
        self._last_sent_at = None

        self.sent = 0
        self.echoed = 0
        self.last_echo = None
        self.last_echo_at = None

    def set_command(self, command):
        """Queues a command (4 ints, wire order) to send at the next step."""
        packet = sssp.encode(command)  # validates
        with self._lock:
            self._command = tuple(command)
            self._packet = packet
            self._command_at = self._clock()
            self._send_now = True

    def step(self):
        """Sends if due, then reads echoes. Called by run(); tests call it directly."""
        now = self._clock()
        packet = None
        with self._lock:
            client_active = (self._command_at is not None
                             and now - self._command_at <= self._client_timeout_s)
            due = (self._send_now or self._last_sent_at is None
                   or now - self._last_sent_at >= self._keepalive_s)
            if client_active and due:
                packet = self._packet
                self._send_now = False
                self._last_sent_at = now
        if packet is not None:
            self._port.write(packet)
            self.sent += 1

        waiting = self._port.in_waiting
        if waiting:
            for echo in self._decoder.feed_bytes(self._port.read(waiting)):
                self.echoed += 1
                self.last_echo = echo
                self.last_echo_at = now

    def status(self):
        now = self._clock()
        with self._lock:
            command = self._command
            command_age = None if self._command_at is None else now - self._command_at
        return {
            'command': command,
            'command_age_s': command_age,
            'client_active': command_age is not None and command_age <= self._client_timeout_s,
            'sent': self.sent,
            'echoed': self.echoed,
            'echo_rejected': self._decoder.rejected,
            'last_echo': self.last_echo,
            'last_echo_age_s': None if self.last_echo_at is None else now - self.last_echo_at,
        }

    def run(self, stop, period_s=0.02):
        """Steps until the stop event is set."""
        while not stop.is_set():
            self.step()
            stop.wait(period_s)
