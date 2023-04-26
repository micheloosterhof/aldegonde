from aldegonde.stats.compare import quadgramscore

am = "ABCDEFGHIJKLM"
nz = "NOPQRSTUVWXYZ"
a = "A"


# def test_chisquare() -> None:
#    assert chisquarescipy(am, nz) == 0.0
#    assert chisquarescipy(a, a) == 1.0


# def test_gtest() -> None:
#    assert gtest(am, nz) == 1.0
#    assert gtest(a, a) == 1.0


def test_quadgramscore() -> None:
    # lowercase letters are not in the corpus. floor value
    assert quadgramscore("TEST") < -3.6
    assert quadgramscore("TEST") > -3.7
    assert quadgramscore("THISISATESTOFTHEEMERGENCYBROADCASTSYSTEM") > -153.0
    assert quadgramscore("THISISATESTOFTHEEMERGENCYBROADCASTSYSTEM") < -152.0
