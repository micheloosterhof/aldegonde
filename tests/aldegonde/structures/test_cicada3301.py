from aldegonde.structures import cicada3301


def test_welcome() -> None:
    data = [1, 28, 21, 15, 12, 0, 5, 4, 12, 1, 6, 13, 28, 28, 0, 7, 14, 16]
    seq = "".join([cicada3301.CICADA_ALPHABET[e] for e in data])
    assert seq == "ᚢᛠᛝᛋᛇᚠᚳᚱᛇᚢᚷᛈᛠᛠᚠᚹᛉᛏ"


def test_i2r() -> None:
    assert cicada3301.i2r(1) == "ᚢ"


def test_r2i() -> None:
    assert cicada3301.r2i("ᚢ") == 1


def test_r2v() -> None:
    assert cicada3301.r2v("ᚢ") == 3


def test_v2r() -> None:
    assert cicada3301.v2r(3) == "ᚢ"


def test_v2i() -> None:
    assert cicada3301.v2i(3) == 1
