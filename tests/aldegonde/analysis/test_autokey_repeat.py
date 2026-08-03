import random

import pytest

from aldegonde.analysis.autokey_repeat import (
    count_violations,
    forced_equal_positions,
)
from aldegonde.exceptions import InvalidInputError


def test_forced_positions_from_a_repeat() -> None:
    # window 4, depth 1 over a stream with the repeat ABCXY
    classes = forced_equal_positions(list("ABCXYABCXY"), depth=1, window=4)
    assert classes == [[1, 6], [2, 7], [3, 8], [4, 9]]


def test_depth_zero_links_whole_repeat() -> None:
    classes = forced_equal_positions(list("ABAB"), depth=0, window=2)
    # AB occurs at 0 and 2: offsets 0..1 link (0,2) and (1,3)
    assert classes == [[0, 2], [1, 3]]


def test_no_repeats_no_classes() -> None:
    assert forced_equal_positions(list("ABCDEFGH"), depth=1, window=3) == []


def test_validation() -> None:
    with pytest.raises(InvalidInputError):
        forced_equal_positions("ABC", depth=-1, window=2)
    with pytest.raises(InvalidInputError):
        forced_equal_positions("ABC", depth=1, window=0)
    with pytest.raises(InvalidInputError):
        forced_equal_positions("ABC", depth=2, window=2)


def test_true_plaintext_has_no_violations() -> None:
    # build a genuine depth-d ciphertext autokey, decrypt with the true
    # tableau, and confirm the forced classes are all constant
    modulus = 5
    depth = 2
    rng = random.Random(3)
    plain = [rng.randrange(modulus) for _ in range(300)]
    # seed the first `depth` key symbols, then key on prior ciphertext
    cipher: list[int] = []
    seed = [rng.randrange(modulus) for _ in range(depth)]
    for i, p in enumerate(plain):
        key = seed[i] if i < depth else cipher[i - depth]
        cipher.append((p + key) % modulus)
    # decrypt back to the true plaintext
    recovered: list[int] = []
    for i, c in enumerate(cipher):
        key = seed[i] if i < depth else cipher[i - depth]
        recovered.append((c - key) % modulus)
    assert recovered == plain
    classes = forced_equal_positions(cipher, depth=depth, window=depth + 3)
    assert count_violations(recovered, classes) == 0


def test_wrong_plaintext_violates_constraints() -> None:
    classes = forced_equal_positions(list("ABCXYABCXY"), depth=1, window=4)
    # a plaintext that is constant satisfies everything
    assert count_violations(["Q"] * 10, classes) == 0
    # an all-distinct plaintext violates every class
    assert count_violations(list("ABCDEFGHIJ"), classes) == len(classes)


def test_count_violations_out_of_range_raises() -> None:
    classes = forced_equal_positions(list("ABCXYABCXY"), depth=1, window=4)
    with pytest.raises(InvalidInputError):
        count_violations(["A"] * 3, classes)
