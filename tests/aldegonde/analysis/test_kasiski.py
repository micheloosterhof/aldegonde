"""Tests for the Kasiski examination (repeated n-grams at a distance)."""

import random

import pytest

from aldegonde import c3301, pasc
from aldegonde.analysis.kasiski import (
    distance_spectrum,
    kasiski_examination,
    print_kasiski_statistics,
    repeat_distances,
)
from aldegonde.exceptions import InsufficientDataError, InvalidInputError
from aldegonde.stats.kappa import doublets

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# Repetitive English-like plaintext so repeated fragments occur at
# distances that are multiples of the key period after encryption.
PLAINTEXT = (
    "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDTHENTHEQUICKBROWNFOX"
    "JUMPSOVERTHELAZYDOGAGAINANDAGAINTHEREISNOTHINGNEWUNDERTHESUN"
    "ATTACKATDAWNATTACKATDUSKATTACKATNOONTHEENEMYWILLNOTEXPECTTHE"
    "ATTACKATDAWNORTHEATTACKATDUSKORTHEATTACKATNOONSAIDTHEGENERAL"
) * 3


def test_repeat_distances_simple() -> None:
    """ABCXYZABC: the trigram ABC repeats at distance 6."""
    dist = repeat_distances("ABCXYZABC", length=3)
    assert dist == {("A", "B", "C"): [6]}


def test_repeat_distances_all_pairs() -> None:
    """Three occurrences yield all three pairwise distances."""
    dist = repeat_distances("ABXABXXAB", length=2)
    assert dist[("A", "B")] == [3, 7, 4]


def test_repeat_distances_no_repeats() -> None:
    """Text without repeated ngrams yields an empty dictionary."""
    assert repeat_distances("ABCDEFG", length=2) == {}


def test_repeat_distances_cut_uses_text_positions() -> None:
    """With cut=1, distances are text offsets, not block indices."""
    dist = repeat_distances("ABCABC", length=3, cut=1)
    assert dist == {("A", "B", "C"): [3]}


def test_repeat_distances_max_distance() -> None:
    """Occurrence pairs beyond max_distance are dropped."""
    dist = repeat_distances("ABXABXXAB", length=2, max_distance=4)
    assert dist[("A", "B")] == [3, 4]
    full = repeat_distances("ABXABXXAB", length=2)
    capped = repeat_distances("ABXABXXAB", length=2, max_distance=100)
    assert full == capped


def test_distance_spectrum_matches_kappa_doublets() -> None:
    """Pairs at distance d in the spectrum equal kappa doublets at skip d."""
    rng = random.Random(42)
    text = [rng.choice(ABC) for _ in range(300)]
    for length in (1, 2):
        spectrum = distance_spectrum(text, length=length)
        for skip in range(1, 30):
            positions, _ = doublets(text, skip=skip, length=length)
            assert spectrum.get(skip, 0) == len(positions)


def test_kasiski_finds_vigenere_period() -> None:
    """Kasiski examination recovers the period of a Vigenere cipher."""
    period = 7
    key = "MUSKETS"
    assert len(key) == period
    tr = pasc.vigenere_tr(ABC)
    ciphertext = list(pasc.pasc_encrypt(PLAINTEXT, keyword=key, tr=tr))
    scores = kasiski_examination(
        ciphertext,
        min_length=3,
        max_length=5,
        max_period=15,
    )
    assert scores[period] > 1.5
    # the true period beats every candidate that is not a multiple of it
    for candidate, score in scores.items():
        if candidate % period != 0:
            assert scores[period] >= score


def test_kasiski_with_runes() -> None:
    """The examination works on the 29-rune Cicada alphabet."""
    period = 5
    rng = random.Random(1337)
    runes = c3301.CICADA_ALPHABET
    # plaintext with a recurring rune phrase to create repeats
    phrase = list("ᚦᛖᚹᛁᛋᛞᛟᛗ")
    plaintext: list[str] = []
    while len(plaintext) < 600:
        plaintext += phrase + [rng.choice(runes) for _ in range(2 * period)]
    key = runes[:period]
    tr = pasc.vigenere_tr(runes)
    ciphertext = list(pasc.pasc_encrypt(plaintext, keyword=key, tr=tr))
    scores = kasiski_examination(
        ciphertext,
        min_length=3,
        max_length=5,
        max_period=12,
    )
    best = next(iter(scores))
    assert best % period == 0
    assert scores[period] > 1.5


def test_kasiski_flat_on_random_text() -> None:
    """Random text shows no strong period: all scores stay near 1.0."""
    rng = random.Random(99)
    text = [rng.choice(ABC) for _ in range(2000)]
    scores = kasiski_examination(text, min_length=1, max_length=3, max_period=10)
    for score in scores.values():
        assert score < 1.5


def test_invalid_length_raises() -> None:
    """A non-positive ngram length is rejected."""
    with pytest.raises(InvalidInputError):
        repeat_distances("ABCABC", length=0)


def test_insufficient_data_raises() -> None:
    """Text shorter than length + 1 is rejected."""
    with pytest.raises(InsufficientDataError):
        repeat_distances("AB", length=3)


def test_inverted_bounds_raise() -> None:
    """min > max bounds are rejected instead of silently accepted."""
    with pytest.raises(InvalidInputError):
        kasiski_examination(PLAINTEXT, min_length=5, max_length=3)
    with pytest.raises(InvalidInputError):
        kasiski_examination(PLAINTEXT, min_period=10, max_period=5)


def test_print_kasiski_validates_input() -> None:
    """The print helper validates parameters like kasiski_examination."""
    with pytest.raises(InvalidInputError):
        print_kasiski_statistics(PLAINTEXT, min_period=0)
    with pytest.raises(InvalidInputError):
        print_kasiski_statistics(PLAINTEXT, min_length=0)


def test_kasiski_max_distance_keeps_signal() -> None:
    """Capping the distance still recovers the Vigenere period."""
    period = 7
    tr = pasc.vigenere_tr(ABC)
    ciphertext = list(pasc.pasc_encrypt(PLAINTEXT, keyword="MUSKETS", tr=tr))
    scores = kasiski_examination(
        ciphertext,
        min_length=3,
        max_length=5,
        max_period=15,
        max_distance=100,
    )
    assert scores[period] > 1.5
    for candidate, score in scores.items():
        if candidate % period != 0:
            assert scores[period] >= score


def test_print_kasiski_statistics(capsys: pytest.CaptureFixture[str]) -> None:
    """The print helper emits one line per candidate period."""
    print_kasiski_statistics(PLAINTEXT, min_length=3, max_length=4, max_period=10)
    out = capsys.readouterr().out
    assert "period=2" in out
    assert "period=10" in out


def test_print_kasiski_no_repeats(capsys: pytest.CaptureFixture[str]) -> None:
    """Text without repeats prints a notice instead of statistics."""
    print_kasiski_statistics("ABCDEFGHIJ", min_length=3, max_length=4)
    out = capsys.readouterr().out
    assert "no repeated ngrams" in out
