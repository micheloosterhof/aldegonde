# ABOUTME: Running-key attacks: offset scan with a self-calibrating empirical
# ABOUTME: null, and the autokey depth-split detector.
"""Running-key and autokey detection.

Two attacks that recur whenever a keystream is suspected:

`offset_scan` subtracts a candidate keystream from the ciphertext at every
starting offset and scores each derived plaintext, then standardizes the
scores against the scan's own distribution — a self-calibrating empirical
null, so no analytic model of the score is needed. The right offset stands
out as an outlier in the scan's own spread.

`autokey_split` detects ciphertext autokey without recovering the key: it
partitions positions by the ciphertext symbol a fixed depth back and pools
the index of coincidence within groups. If each group is a monoalphabetic
image of natural language — which ciphertext autokey makes it — the pooled
IOC rises to the plaintext level, well above the flat-text value.

Both are alphabet-generic; correct any offset scan for the offsets tried.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from statistics import fmean, pstdev
from typing import NamedTuple, TypeVar

from aldegonde.exceptions import InvalidInputError

T = TypeVar("T")

Score = Callable[[Sequence[int]], float]
"""A plaintext score to maximize over offsets, e.g. n-gram fitness."""


class OffsetHit(NamedTuple):
    """One offset in a keystream scan, standardized against the scan itself.

    Attributes:
        offset: Keystream starting offset
        score: The plaintext score at this offset
        z: Standard score against the mean and spread of all offsets tried
    """

    offset: int
    score: float
    z: float


def offset_scan(
    cipher: Sequence[int],
    keystream: Sequence[int],
    modulus: int,
    score: Score,
    *,
    max_offset: int | None = None,
    subtract: bool = True,
) -> list[OffsetHit]:
    """Score the ciphertext against every window of a long keystream.

    The keystream is at least as long as the ciphertext; at each starting
    offset the aligned window is combined with the whole ciphertext
    (subtracted for an additive cipher, added for Beaufort-like ones) modulo
    the alphabet size, and the resulting plaintext is scored. Every offset's
    score is then standardized against the mean and spread of all offsets in
    the scan — the self-calibrating empirical null — so a genuine hit shows
    as a large z without any analytic model of the score distribution.

    Args:
        cipher: Ciphertext as alphabet indices
        keystream: Candidate keystream as integers (reduced modulo modulus),
            at least as long as the ciphertext
        modulus: Alphabet size
        score: Plaintext scorer to maximize
        max_offset: Largest starting offset to try; as many as fit when
            omitted
        subtract: Subtract the keystream (additive cipher); add it otherwise

    Returns:
        One OffsetHit per offset, in offset order

    Raises:
        InvalidInputError: If modulus is not positive, the keystream is
            shorter than the ciphertext, or no offset fits
    """
    if modulus < 1:
        msg = f"modulus must be positive, got {modulus}"
        raise InvalidInputError(msg)
    span = len(keystream) - len(cipher)
    if span < 0:
        msg = "keystream is shorter than the ciphertext"
        raise InvalidInputError(msg)
    last = span if max_offset is None else min(span, max_offset)
    offsets = range(last + 1)
    reduced = [k % modulus for k in keystream]
    raw: list[tuple[int, float]] = []
    for offset in offsets:
        window = reduced[offset : offset + len(cipher)]
        if subtract:
            plain = [(c - k) % modulus for c, k in zip(cipher, window)]
        else:
            plain = [(k - c) % modulus for c, k in zip(cipher, window)]
        raw.append((offset, score(plain)))
    if not raw:
        msg = "no offset fits the given max_offset"
        raise InvalidInputError(msg)
    scores = [value for _, value in raw]
    mean = fmean(scores)
    sd = pstdev(scores) if len(scores) > 1 else 0.0
    return [
        OffsetHit(offset=offset, score=value, z=(value - mean) / sd if sd else 0.0)
        for offset, value in raw
    ]


class AutokeySplit(NamedTuple):
    """Pooled within-group coincidence of an autokey depth split.

    Attributes:
        depth: The feedback depth tested
        pooled_ioc: Normalized IOC pooled across groups keyed on the symbol
            `depth` positions back
        groups: Number of non-empty groups
    """

    depth: int
    pooled_ioc: float
    groups: int


def autokey_split(
    cipher: Sequence[T],
    depth: int,
    alphabetsize: int | None = None,
) -> AutokeySplit:
    """Pool the coincidence within groups keyed on an earlier symbol.

    Partitions the positions from index `depth` on by the ciphertext symbol
    `depth` positions back, then pools the index of coincidence across those
    groups (summing matching-pair and total-pair counts, not averaging
    per-group rates, so unequal groups combine correctly). Under a
    ciphertext autokey of that depth each group is a monoalphabetic image of
    the plaintext, so the pooled normalized IOC climbs toward the plaintext
    value (well above 1.0); flat text leaves it near 1.0.

    Args:
        cipher: Ciphertext stream
        depth: Feedback depth to test
        alphabetsize: Alphabet size for normalization; the count of distinct
            symbols when omitted

    Returns:
        The pooled normalized IOC and the group count for this depth

    Raises:
        InvalidInputError: If depth is not positive
    """
    if depth < 1:
        msg = f"depth must be positive, got {depth}"
        raise InvalidInputError(msg)
    if alphabetsize is None:
        alphabetsize = len(set(cipher))
    groups: dict[T, dict[T, int]] = {}
    sizes: dict[T, int] = {}
    for i in range(depth, len(cipher)):
        key = cipher[i - depth]
        bucket = groups.setdefault(key, {})
        symbol = cipher[i]
        bucket[symbol] = bucket.get(symbol, 0) + 1
        sizes[key] = sizes.get(key, 0) + 1
    matches = 0
    pairs = 0
    for key, bucket in groups.items():
        size = sizes[key]
        pairs += size * (size - 1)
        matches += sum(count * (count - 1) for count in bucket.values())
    pooled = (alphabetsize * matches / pairs) if pairs else 0.0
    return AutokeySplit(depth=depth, pooled_ioc=pooled, groups=len(groups))
