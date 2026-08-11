"""Functions to deal with Cicada 3301."""

import random
from collections import defaultdict
from collections.abc import Iterator, Sequence

from aldegonde import pasc
from aldegonde.exceptions import AldegondeKeyError, AlphabetError
from aldegonde.maths.prime_numbers import primes
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


# --- Transcription punctuation -------------------------------------------
#
# The page marks words and larger units with clusters of dots. The
# transcription encodes each cluster as a circled numeral carrying its dot
# count, so the count is the identity rather than an interpretation:
#
#     ①  1 dot   word separator
#     ③  3 dots
#     ④  4 dots  sentence mark
#     ⑩ ⑬ ㉓     larger glyphs, see data/SYMBOLS.md
#
# `-` and `.` are the legacy encoding, which collapsed every cluster onto two
# characters. They are still accepted so older files and the solved-page
# numeric blocks keep parsing.

CIRCLED_ONE_TO_TWENTY = frozenset(chr(0x2460 + n) for n in range(20))
CIRCLED_TWENTY_ONE_UP = frozenset(chr(0x3251 + n) for n in range(15))
DOT_MARKS = CIRCLED_ONE_TO_TWENTY | CIRCLED_TWENTY_ONE_UP
LEGACY_MARKS = frozenset("-.")
MARKS = DOT_MARKS | LEGACY_MARKS


def dot_count(mark: str) -> int:
    """How many dots the mark draws on the page.

    Args:
        mark: A single mark character from `DOT_MARKS`.

    Returns:
        The number of dots, 1 to 35.

    Raises:
        AldegondeKeyError: If the mark is not a circled numeral. The legacy `-`
            and `.` never recorded a count -- collapsing the counts is exactly
            what they did wrong -- so no number can be returned for them.
    """
    if mark in CIRCLED_ONE_TO_TWENTY:
        return ord(mark) - 0x2460 + 1
    if mark in CIRCLED_TWENTY_ONE_UP:
        return ord(mark) - 0x3251 + 21
    msg = f"{mark!r} records no dot count"
    raise AldegondeKeyError(msg)


#: Every mark character as a string, for code that composes a boundary set by
#: concatenation (`MARK_CHARS + "%&$"`) rather than by set union.
MARK_CHARS = "".join(sorted(MARKS))

#: Marks of four dots or more, which the transcription collapsed onto `.`.
#: Membership is by dot count, an observed property; what the clusters MEAN is
#: still open, so the grouping deliberately claims nothing beyond size.
CLUSTER_MARKS = frozenset([m for m in DOT_MARKS if dot_count(m) >= 4] + ["."])

#: Marks of fewer than four dots, which the transcription collapsed onto `-`.
#: `①` is the word separator; `③` is the triple-dot mark.
WORD_MARKS = MARKS - CLUSTER_MARKS

#: Division the project added, not glyphs on the page: page, paragraph, section.
STRUCTURE = frozenset("%&$")

#: Verse numbers. Pages 36-38 open each block with a large red Arabic numeral,
#: set against whitespace and abutting the runes with no separator dot. They are
#: on the page but they are not runes, and a word cannot run through one: the
#: numeral starts a new verse. Without this, a line ending mid-word joins the
#: text after the next numeral, which is how the clean corpus briefly read 2,927
#: words instead of 2,928.
NUMERALS = frozenset("0123456789")

#: The numerals as a string, to compose a boundary set alongside `MARK_CHARS`.
NUMERAL_CHARS = "".join(sorted(NUMERALS))

#: Quotation marks, recovered from the page scans. Speech opens or closes at
#: one, so it ends the word beside it. The apostrophe is deliberately NOT here:
#: it sits INSIDE a word, and a contraction is one word, not two.
QUOTES = frozenset('"')

#: The quotation marks as a string, to compose a boundary set alongside
#: `MARK_CHARS` and `NUMERAL_CHARS`.
QUOTE_CHARS = "".join(sorted(QUOTES))

#: Everything that ends a word.
WORD_BOUNDARY = MARKS | STRUCTURE | NUMERALS | QUOTES

#: Line wraps. A word runs THROUGH these -- they are not word boundaries.
LINE_WRAP = frozenset("/\n")


def is_rune(char: str) -> bool:
    """Is this one of the 29 runes?"""
    return char in RUNE_SET


RUNE_SET = frozenset(CICADA_ALPHABET)


def r2i(rune: str) -> int:
    """Rune to index"""
    for i, e in enumerate(CICADA_ALPHABET):
        if rune == e:
            return i
    msg = f"{rune!r} is not one of the 29 runes"
    raise AldegondeKeyError(msg)


def i2r(rune: int) -> str:
    """Index to rune"""
    return CICADA_ALPHABET[rune]


def r2v(rune: str) -> int:
    """Rune to (prime) value"""
    primelist = primes(110)
    for i, e in enumerate(CICADA_ALPHABET):
        if rune == e:
            return primelist[i]
    msg = f"{rune!r} is not one of the 29 runes"
    raise AldegondeKeyError(msg)


def v2r(value: int) -> str:
    """(prime) value to rune"""
    primelist = primes(110)
    for i, e in enumerate(primelist):
        if value == e:
            return CICADA_ALPHABET[i]
    msg = f"{value} is not a Gematria Primus prime value"
    raise AldegondeKeyError(msg)


def v2i(value: int) -> int:
    """(prime) value to index"""
    primelist = primes(110)
    for i, e in enumerate(primelist):
        if value == e:
            return i
    msg = f"{value} is not a Gematria Primus prime value"
    raise AldegondeKeyError(msg)


def randomrunes(
    length: int, maximum: int = 29, rng: random.Random | None = None
) -> list[int]:
    """Random list of rune indices.

    Args:
        length: How many runes to draw
        maximum: Exclusive upper bound on the index drawn
        rng: Injected random source. Defaults to the system source; pass a
            seeded `Random` to reproduce a draw.

    Returns:
        A list of `length` rune indices
    """
    source = random.Random() if rng is None else rng
    return [source.randrange(0, maximum) for _ in range(length)]


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
                msg = f"{t!r} is not a known tabula recta type"
                raise AlphabetError(msg)
    return TR


unigrams = compare.loadgrams("aldegonde.data.ngrams.runeglish", "unigrams.txt")
bigrams = compare.loadgrams("aldegonde.data.ngrams.runeglish", "bigrams.txt")
trigrams = compare.loadgrams("aldegonde.data.ngrams.runeglish", "trigrams.txt")
quadgrams = compare.loadgrams("aldegonde.data.ngrams.runeglish", "quadgrams.txt")

quadgramscore = compare.make_ngram_scorer(quadgrams)
trigramscore = compare.make_ngram_scorer(trigrams)
bigramscore = compare.make_ngram_scorer(bigrams)
