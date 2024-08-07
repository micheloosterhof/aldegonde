from aldegonde.stats.hamming import hamming_distance

karolin = "karolin"
kathrin = "kathrin"
kerstin = "kerstin"


def test_hamming() -> None:
    assert hamming_distance(karolin, kathrin) == 3
    assert hamming_distance(karolin, kerstin) == 3
    assert hamming_distance(kathrin, kerstin) == 4
