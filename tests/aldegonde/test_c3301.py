import random
from collections import Counter

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
    data = [i % 7 for i in range(200)]
    out = c3301.low_doublet_null()(data, random.Random(0))
    assert len(out) == len(data)
    assert all(0 <= r < len(c3301.CICADA_ALPHABET) for r in out)


def test_low_doublet_null_preserves_frequencies_exactly() -> None:
    data = [i % 7 for i in range(200)]
    out = c3301.low_doublet_null()(data, random.Random(0))
    assert Counter(out) == Counter(data)


def test_low_doublet_null_matches_observed_doublet_rate() -> None:
    # Data with a low but nonzero doublet rate, like the Liber Primus.
    rng = random.Random(0)
    data: list[int] = []
    while len(data) < 3000:
        r = rng.randrange(12)
        if data and r == data[-1] and rng.random() < 0.85:
            continue  # suppress most doublets
        data.append(r)
    observed = c3301._observed_doublet_rate(data)
    out = c3301.low_doublet_null()(data, random.Random(1))
    rate = sum(1 for a, b in zip(out, out[1:]) if a == b) / (len(out) - 1)
    assert 0.0 < observed < 0.03  # genuinely low but nonzero
    assert abs(rate - observed) < 0.01


def test_low_doublet_null_is_reproducible() -> None:
    data = [i % 5 for i in range(100)]
    model = c3301.low_doublet_null()
    assert model(data, random.Random(4)) == model(data, random.Random(4))


def test_randomrunes_with_low_doublets_removed() -> None:
    assert not hasattr(c3301, "randomrunes_with_low_doublets")
