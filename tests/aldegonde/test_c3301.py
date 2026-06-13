from aldegonde import c3301


def test_welcome() -> None:
    data = [1, 28, 21, 15, 12, 0, 5, 4, 12, 1, 6, 13, 28, 28, 0, 7, 14, 16]
    seq = "".join([c3301.CICADA_ALPHABET[e] for e in data])
    assert seq == "ᚢᛠᛝᛋᛇᚠᚳᚱᛇᚢᚷᛈᛠᛠᚠᚹᛉᛏ"


def test_i2r() -> None:
    assert c3301.i2r(1) == "ᚢ"


def test_r2i() -> None:
    assert c3301.r2i("ᚢ") == 1


def test_r2v() -> None:
    assert c3301.r2v("ᚢ") == 3


def test_v2r() -> None:
    assert c3301.v2r(3) == "ᚢ"


def test_v2i() -> None:
    assert c3301.v2i(3) == 1


def test_low_doublet_null_preserves_length_and_alphabet() -> None:
    import random

    data = [i % 7 for i in range(200)]
    model = c3301.low_doublet_null()
    out = model(data, random.Random(0))
    assert len(out) == len(data)
    assert all(0 <= r < len(c3301.CICADA_ALPHABET) for r in out)


def test_low_doublet_null_zero_rate_has_no_doublets() -> None:
    import random

    data = [i % 7 for i in range(200)]
    model = c3301.low_doublet_null(doublet_rate=0.0)
    out = model(data, random.Random(1))
    assert all(a != b for a, b in zip(out, out[1:]))


def test_low_doublet_null_matches_observed_alphabet() -> None:
    import random

    data = [0, 1, 2, 0, 1, 2, 0, 1, 2, 1]
    model = c3301.low_doublet_null(doublet_rate=0.0)
    out = model(data, random.Random(2))
    assert set(out) <= {0, 1, 2}


def test_low_doublet_null_is_reproducible() -> None:
    import random

    data = [i % 5 for i in range(100)]
    model = c3301.low_doublet_null()
    assert model(data, random.Random(4)) == model(data, random.Random(4))


def test_randomrunes_with_low_doublets_removed() -> None:
    assert not hasattr(c3301, "randomrunes_with_low_doublets")
