import importlib.util
import pathlib

import pytest

spec = importlib.util.spec_from_file_location(
    'throttle_steps', pathlib.Path(__file__).resolve().parent.parent / 'tools' / 'throttle_steps.py')
throttle_steps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(throttle_steps)


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += s


def test_steps_through_levels_then_zero():
    clock, sent = FakeClock(), []
    throttle_steps.run([10, 20], sent.append, 1.0, lambda: False,
                       log=lambda m: None, clock=clock, sleep=clock.sleep)
    assert sent == [10] * 4 + [20] * 4 + [0] * 12


def test_stop_drops_to_zero():
    clock, sent = FakeClock(), []
    throttle_steps.run([10, 20, 30], sent.append, 1.0, lambda: clock.t >= 1.5,
                       log=lambda m: None, clock=clock, sleep=clock.sleep)
    assert sent == [10] * 4 + [20] * 2 + [0] * 12


def test_failure_still_sends_zero():
    clock, sent = FakeClock(), []

    def send(throttle):
        sent.append(throttle)
        if throttle == 20:
            raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        throttle_steps.run([10, 20], send, 1.0, lambda: False,
                           log=lambda m: None, clock=clock, sleep=clock.sleep)
    assert sent[-12:] == [0] * 12


def test_resend_within_gateway_timeout():
    assert throttle_steps.RESEND_S < 1.0
