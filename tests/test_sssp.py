import random

import pytest

import sssp


def test_encode_format():
    assert sssp.encode([60, 63, 95, 52]) == bytes([17, 171, 4, 60, 63, 95, 52, (60 + 63 + 95 + 52) % 256])


@pytest.mark.parametrize('data', [[1, 2, 3], [1, 2, 3, 4, 5], [0, 0, 0, 256], [0, 0, 0, -1], [0, 0, 0, 1.0], [0, 0, 0, True]])
def test_encode_rejects_bad_data(data):
    with pytest.raises(ValueError):
        sssp.encode(data)


def test_round_trip_with_junk_and_damage():
    rng = random.Random(1)
    d = sssp.Decoder()
    stream = bytes(rng.randrange(256) for _ in range(5000))
    damaged = bytearray(sssp.encode([1, 2, 3, 4]))
    del damaged[4]
    stream += bytes(damaged) + sssp.encode([60, 63, 0, 52]) + sssp.encode([60, 63, 95, 52])
    got = d.feed_bytes(stream)
    assert got[-1] == (60, 63, 95, 52)
    assert (1, 2, 3, 4) not in got


def test_header_values_in_data():
    assert sssp.Decoder().feed_bytes(sssp.encode([17, 171, 17, 171])) == [(17, 171, 17, 171)]


def test_bad_checksum_rejected():
    p = bytearray(sssp.encode([60, 63, 95, 52]))
    p[-1] ^= 1
    d = sssp.Decoder()
    assert d.feed_bytes(p) == []
    assert d.rejected == 1
