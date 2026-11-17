import pytest

import sungate


class RecordingLink:
    def __init__(self):
        self.commands = []

    def set_command(self, command):
        self.commands.append(command)

    def status(self):
        return {'sent': len(self.commands)}


@pytest.fixture
def client_and_link():
    l = RecordingLink()
    return sungate.create_app(l).test_client(), l


def test_post_forwards_wire_order(client_and_link):
    client, l = client_and_link
    r = client.post('/', json={'throttle': 95, 'fwdback': 63, 'leftright': 60, 'calib': 52})
    assert r.status_code == 200
    assert l.commands == [[60, 63, 95, 52]]


@pytest.mark.parametrize('body', [
    {'throttle': 95, 'fwdback': 63, 'leftright': 60},                 # missing calib
    {'throttle': 95, 'fwdback': -20, 'leftright': 60, 'calib': 52},   # out of range
    {'throttle': 256, 'fwdback': 63, 'leftright': 60, 'calib': 52},
    {'throttle': '95', 'fwdback': 63, 'leftright': 60, 'calib': 52},  # not an int
    [1, 2, 3, 4],
])
def test_bad_commands_get_400(client_and_link, body):
    client, l = client_and_link
    r = client.post('/', json=body)
    assert r.status_code == 400
    assert r.get_json()['success'] is False
    assert l.commands == []


def test_non_json_gets_400(client_and_link):
    client, _ = client_and_link
    assert client.post('/', data='nope').status_code == 400


def test_status(client_and_link):
    client, _ = client_and_link
    assert client.get('/status').get_json() == {'sent': 0}
