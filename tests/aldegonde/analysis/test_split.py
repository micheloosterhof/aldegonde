"""
"""

from aldegonde.analysis.split import split_by_slice_interrupted, trim

TXT2 = """CVJAFENMHGSO"""
#         012012340123


def test_split_by_slice_interrupted() -> None:
    slices = {
        0: ["C", "A", "H"],
        1: ["V", "F", "G"],
        2: ["J", "E", "S"],
        3: ["N", "O"],
        4: ["M"],
    }
    assert split_by_slice_interrupted(TXT2, 5, interrupter="A") == slices


def test_trim() -> None:
    assert list(trim("ABC")) == list("ABC")
    assert list(trim("ABC ")) == list("ABC")
    assert list(trim(" ABC")) == list("ABC")
    assert list(trim(" ABC ")) == list("ABC")
    assert list(trim("ABC DEF")) == list("ABC DEF")
    assert list(trim("ABC DEF ")) == list("ABC DEF")
    assert list(trim(" ABC DEF")) == list("ABC DEF")
    assert list(trim(" ABC DEF ")) == list("ABC DEF")
    assert list(trim("ABC  DEF")) == list("ABC  DEF")
    assert list(trim("ABC  DEF ")) == list("ABC  DEF")
    assert list(trim(" ABC  DEF")) == list("ABC  DEF")
    assert list(trim(" ABC  DEF ")) == list("ABC  DEF")
