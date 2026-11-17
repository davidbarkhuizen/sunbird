import control


def test_hold_resends_until_time_is_up(monkeypatch):
    sent = []
    monkeypatch.setattr(control, 'sendCommand', lambda url, cmd: sent.append(cmd))
    t = [0.0]
    control.hold('u', control.CMD['HOVER'], 1.0, interval=0.25,
                 clock=lambda: t[0], sleep=lambda s: t.__setitem__(0, t[0] + s))
    assert len(sent) == 5  # at 0, 0.25, 0.5, 0.75, 1.0
    assert t[0] == 1.0


def test_hold_interval_within_gateway_timeout():
    assert control.KEEPALIVE_S < 1.0


def test_commands_are_valid_wire_values():
    import sungate
    for name, cmd in control.CMD.items():
        sungate.parse_command(cmd)  # raises on a bad command
