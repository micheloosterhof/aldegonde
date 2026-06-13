"""Functions to deal with Cicada 3301."""

import random
from collections import defaultdict
from collections.abc import Iterator, Sequence

from aldegonde import pasc
from aldegonde.maths.primes import primes
from aldegonde.stats import compare, nulls

CICADA_ALPHABET = [
    "ᚠ",
    "ᚢ",
    "ᚦ",
    "ᚩ",
    "ᚱ",
    "ᚳ",
    "ᚷ",
    "ᚹ",
    "ᚻ",
    "ᚾ",
    "ᛁ",
    "ᛄ",
    "ᛇ",
    "ᛈ",
    "ᛉ",
    "ᛋ",
    "ᛏ",
    "ᛒ",
    "ᛖ",
    "ᛗ",
    "ᛚ",
    "ᛝ",
    "ᛟ",
    "ᛞ",
    "ᚪ",
    "ᚫ",
    "ᚣ",
    "ᛡ",
    "ᛠ",
]

CICADA_ENGLISH_ALPHABET = [
    "F",
    "U",
    "TH",
    "O",
    "R",
    "C",
    "G",
    "W",
    "H",
    "N",
    "I",
    "J",
    "EO",
    "P",
    "X",
    "S",
    "T",
    "B",
    "E",
    "M",
    "L",
    "NG",
    "OE",
    "D",
    "A",
    "AE",
    "Y",
    "IA",
    "EA",
]


def r2i(rune: str) -> int:
    """Rune to index"""
    for i, e in enumerate(CICADA_ALPHABET):
        if rune == e:
            return i
    raise ValueError


def i2r(rune: int) -> str:
    """Index to rune"""
    return CICADA_ALPHABET[rune]


def r2v(rune: str) -> int:
    """Rune to (prime) value"""
    primelist = primes(110)
    for i, e in enumerate(CICADA_ALPHABET):
        if rune == e:
            return primelist[i]
    raise ValueError


def v2r(value: int) -> str:
    """(prime) value to rune"""
    primelist = primes(110)
    for i, e in enumerate(primelist):
        if value == e:
            return CICADA_ALPHABET[i]
    raise ValueError


def v2i(value: int) -> int:
    """(prime) value to index"""
    primelist = primes(110)
    for i, e in enumerate(primelist):
        if value == e:
            return i
    raise ValueError


def randomrunes(length: int, maximum: int = 29) -> list[int]:
    """Random list of runes of lenth len."""
    output: list[int] = []
    for _ in range(length):
        output.append(random.randrange(0, maximum))
    return output


def _observed_doublet_rate(data: Sequence[int]) -> float:
    """Fraction of adjacent positions holding equal runes."""
    pairs = len(data) - 1
    if pairs <= 0:
        return 0.0
    doublets = sum(1 for a, b in zip(data, data[1:]) if a == b)
    return doublets / pairs


def low_doublet_null() -> nulls.NullModel[int]:
    """Frequency-exact null matching the text's own doublet rate.

    The Liber Primus suppresses adjacent equal runes to about a fifth of the
    frequency-matched chance rate (roughly 0.7%), but not to zero. The
    appropriate null preserves the exact rune frequencies and reproduces that
    observed doublet rate, so the suppression is held fixed rather than mistaken
    for signal; only structure beyond frequencies and doublets survives. Each
    surrogate is drawn from the injected random source the harness supplies.

    Returns:
        A null model whose surrogates match the observed rune frequencies and
        adjacent-doublet rate
    """

    def model(data: Sequence[int], rng: random.Random) -> Sequence[int]:
        rate = _observed_doublet_rate(data)
        sampler: nulls.NullModel[int] = nulls.doublet_shuffle(rate)
        return sampler(data, rng)

    return model


def numberToBase(n: int, b: int) -> list[int]:
    """Convert from base10 to any other base. outputs as list of int."""
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]


def base29(value: int, padding: int = -1) -> list[int]:
    """Input `int` and output in Base29 as list of integers."""
    l = numberToBase(value, 29)
    if padding == -1:
        return l
    pad_value = 0
    pad_size = padding - len(l)
    return [*[pad_value] * pad_size, *l]


class RuneIterator:
    """iterates over runes length L, [0,0,0], [0,0,1], [0,0,2], ..., [0,0,28], [0,1,0], ..."""

    i: int
    maximum: int
    length: int

    def __init__(self, length: int) -> None:
        self.length = length
        self.maximum = int(29**length)

    def __iter__(self) -> Iterator[list[int]]:
        self.i = 0
        return self

    def __next__(self) -> list[int]:
        if self.i >= self.maximum:
            raise StopIteration
        x = self.i
        self.i += 1
        return base29(x, padding=self.length)


def print_all(runes: str, limit: int = 0) -> None:
    """Print runes, rune indexes and english output."""
    print_rune(runes, limit)
    print_rune_index(runes, limit)
    print_english(runes, limit)


def print_english(runes: str, limit: int = 0) -> None:
    """Print rune output translated back to english letters."""
    if limit == 0 or limit > len(runes):
        limit = len(runes)

    print("ENGLISH: ", end="")
    for i in range(limit):
        eng = CICADA_ENGLISH_ALPHABET[r2i(runes[i])]
        print(f"{eng:>2} ", end="")
    print()


def print_rune_index(runes: str, limit: int = 0) -> None:
    """Print rune output translated back to english letters."""
    if limit == 0 or limit > len(runes):
        limit = len(runes)

    print("RUNEIDX: ", end="")
    for i in range(limit):
        print(f"{r2i(runes[i]):02} ", end="")
    print()


def print_rune(runes: str, limit: int = 0) -> None:
    """Print rune output translated back to english letters."""
    if limit == 0 or limit > len(runes):
        limit = len(runes)

    print("RUNES  :  ", end="")
    for i in range(limit):
        print(f"{runes[i]:2} ", end="")
    print()


def valueTR(t: str = "vigenere") -> pasc.TR[str]:
    """Funny TR that works by prime values"""
    TR: pasc.TR[str] = defaultdict(dict)
    for key in CICADA_ALPHABET:
        for plaintext in CICADA_ALPHABET:
            if t == "vigenere":
                TR[key][plaintext] = i2r((r2i(plaintext) + r2v(key)) % 29)
            elif t == "beaufort":
                TR[key][plaintext] = i2r((r2v(key) - r2i(plaintext)) % 29)
            elif t == "variantbeaufort":
                TR[key][plaintext] = i2r((r2i(plaintext) - r2v(key)) % 29)
            else:
                raise ValueError
    return TR


unigrams = compare.loadgrams("aldegonde.data.ngrams.runeglish", "unigrams.txt")
bigrams = compare.loadgrams("aldegonde.data.ngrams.runeglish", "bigrams.txt")
trigrams = compare.loadgrams("aldegonde.data.ngrams.runeglish", "trigrams.txt")
quadgrams = compare.loadgrams("aldegonde.data.ngrams.runeglish", "quadgrams.txt")

quadgramscore = compare.NgramScorer(quadgrams)
trigramscore = compare.NgramScorer(trigrams)
bigramscore = compare.NgramScorer(bigrams)
