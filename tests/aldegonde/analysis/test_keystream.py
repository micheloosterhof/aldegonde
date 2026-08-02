import random
from collections import Counter

import pytest

from aldegonde.analysis.keystream import autokey_split, offset_scan
from aldegonde.exceptions import InvalidInputError

MOD = 29


def _ioc(pt: list[int]) -> float:
    counts = Counter(pt)
    n = len(pt)
    return sum(v * (v - 1) for v in counts.values()) / (n * (n - 1))


def test_offset_scan_recovers_planted_offset() -> None:
    ks_rng = random.Random(99)
    keystream = [ks_rng.randrange(MOD) for _ in range(500)]
    rng = random.Random(4)
    true_offset = 37
    # peaked plaintext so the recovered stream scores high on IoC
    plain = [rng.choices(range(MOD), weights=[12] + [1] * 28)[0] for _ in range(200)]
    cipher = [(plain[i] + keystream[true_offset + i]) % MOD for i in range(200)]
    hits = offset_scan(cipher, keystream, MOD, _ioc, subtract=True)
    best = max(hits, key=lambda h: h.z)
    assert best.offset == true_offset
    assert best.z > 5.0


def test_offset_scan_reports_every_offset() -> None:
    hits = offset_scan([1, 2, 3], [0, 0, 0, 0, 0], MOD, _ioc)
    assert [h.offset for h in hits] == [0, 1, 2]


def test_offset_scan_respects_max_offset() -> None:
    hits = offset_scan([1, 2, 3], list(range(20)), MOD, _ioc, max_offset=5)
    assert [h.offset for h in hits] == list(range(6))


def test_offset_scan_beaufort_direction() -> None:
    # add direction: plain = key - cipher
    keystream = list(range(10))
    cipher = [3, 4, 5]
    hits = offset_scan(cipher, keystream, MOD, _ioc, subtract=False)
    assert hits  # runs without error over the add direction


def test_offset_scan_validation() -> None:
    with pytest.raises(InvalidInputError):
        offset_scan([1, 2, 3], [0], MOD, _ioc)  # keystream too short
    with pytest.raises(InvalidInputError):
        offset_scan([1, 2], [0, 0], 0, _ioc)  # bad modulus


def test_autokey_split_detects_ciphertext_autokey() -> None:
    rng = random.Random(7)
    plain = [
        rng.choices(range(MOD), weights=[10, 8, 6] + [1] * 26)[0] for _ in range(3000)
    ]
    cipher = [plain[0]]
    for i in range(1, len(plain)):
        cipher.append((plain[i] + cipher[i - 1]) % MOD)
    hit = autokey_split(cipher, 1, alphabetsize=MOD)
    assert hit.pooled_ioc > 1.3


def test_autokey_split_flat_on_random_text() -> None:
    rng = random.Random(11)
    stream = [rng.randrange(MOD) for _ in range(3000)]
    hit = autokey_split(stream, 1, alphabetsize=MOD)
    assert abs(hit.pooled_ioc - 1.0) < 0.2


def test_autokey_split_wrong_depth_stays_flat() -> None:
    rng = random.Random(7)
    plain = [
        rng.choices(range(MOD), weights=[10, 8, 6] + [1] * 26)[0] for _ in range(3000)
    ]
    cipher = [plain[0]]
    for i in range(1, len(plain)):
        cipher.append((plain[i] + cipher[i - 1]) % MOD)
    # true depth is 1; depth 7 should not show the lift
    right = autokey_split(cipher, 1, alphabetsize=MOD).pooled_ioc
    wrong = autokey_split(cipher, 7, alphabetsize=MOD).pooled_ioc
    assert right > wrong


def test_autokey_split_invalid_depth() -> None:
    with pytest.raises(InvalidInputError):
        autokey_split([1, 2, 3], 0)
