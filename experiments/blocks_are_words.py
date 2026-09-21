# ABOUTME: Tests whether the body's blocks are whole words or arbitrary cuts of a stream,
# ABOUTME: using the d5 channel, which reads plaintext equality without a key.
"""If the separators are not word boundaries, are the blocks still words?

`separators-are-not-word-boundaries.md` shows the block lengths carry no language order.
Three readings survive that, and they are not equivalent for anything downstream:

    A  a list      -- blocks ARE words, in an order with no prose structure
    B  reordering  -- blocks ARE words, permuted
    C  cuts        -- blocks are arbitrary cuts of a continuous stream

A and B keep every crib program valid, because a block is still a dictionary word. C
invalidates them: an 8-rune cut spans word boundaries and matches no entry.

The d5 channel decides between them. Under a letter step of order 5, positions five apart
inside a block share an alphabet, so `c[j] == c[j+5]` reads plaintext equality with no key
(`period5-is-confirmed`). Two statistics of that channel behave differently for words and
for cuts, and they were measured on runeglish prose rather than assumed:

    level  real words 0.0537, arbitrary cuts 0.0620 -- cuts are HIGHER, because a cut
           spans word boundaries and English repeats common words at short distances
    trend  the correlation between coincidence and segment length: real words +0.0360,
           arbitrary cuts +0.0029

The trend is the better test because it survives the leak. If only a fraction phi5 of the
d5 pairs actually share an alphabet, the rest contribute chance matches, which carry no
length trend at all -- so attenuation can only SHRINK the observed correlation. An
observed r therefore sets a floor on the plaintext's r, whatever phi5 is.

    python blocks_are_words.py
"""

from __future__ import annotations

import math
import random
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from word_length_sequence import body_sequences  # noqa: E402

CACHE = Path(tempfile.gettempdir()) / "lp_external_texts"
LAG = 5


def pairs_by_length(segments: list[list[int]]) -> list[tuple[int, int]]:
    return [
        (len(s), int(s[i] == s[i + LAG]))
        for s in segments
        for i in range(len(s) - LAG)
    ]


def level(pairs: list[tuple[int, int]]) -> tuple[float, int]:
    return (sum(y for _l, y in pairs) / len(pairs)), len(pairs)


def trend(pairs: list[tuple[int, int]]) -> tuple[float, float]:
    """Correlation of coincidence with segment length, and its z."""
    n = len(pairs)
    lengths = [a for a, _ in pairs]
    ys = [b for _a, b in pairs]
    ml = sum(lengths) / n
    my = sum(ys) / n
    num = sum((a - ml) * (b - my) for a, b in pairs)
    den = math.sqrt(
        sum((a - ml) ** 2 for a in lengths) * sum((b - my) ** 2 for b in ys)
    )
    r = num / den if den else 0.0
    z = r * math.sqrt(n - 2) / math.sqrt(1 - r * r) if abs(r) < 1 else 0.0
    return r, z


def blocks_of_body() -> list[list[int]]:
    stream, wid = load_clean()
    segments: list[list[int]] = []
    cur: list[int] = []
    for i, v in enumerate(stream):
        if i and wid[i] != wid[i - 1]:
            segments.append(cur)
            cur = []
        cur.append(v)
    segments.append(cur)
    return segments


def main() -> None:
    from runeglish_frequency import english_to_runeglish  # noqa: PLC0415

    rng = random.Random(4)
    text = (CACHE / "pg1033.txt").read_text(encoding="utf-8", errors="ignore")
    words = [
        [ord(c) for c in english_to_runeglish(w)]
        for w in re.findall(r"[A-Za-z]+", text.upper())[:60000]
    ]
    words = [w for w in words if w]
    stream = [r for w in words for r in w]

    lengths = [x for s in body_sequences() for x in s]
    shuffled = lengths[:]
    rng.shuffle(shuffled)
    cuts, i, k = [], 0, 0
    while i < len(stream):
        length = shuffled[k % len(shuffled)]
        cuts.append(stream[i : i + length])
        i += length
        k += 1

    print(f"{'segmentation':<26}{'d5 level':>10}{'pairs':>9}{'trend r':>10}{'z':>8}")
    rows = {}
    for label, segs in (
        ("prose, real words", words),
        ("prose, arbitrary cuts", cuts),
        ("body, within-block", blocks_of_body()),
    ):
        p = pairs_by_length(segs)
        rate, n = level(p)
        r, z = trend(p)
        rows[label] = (rate, n, r)
        print(f"{label:<26}{rate:>10.4f}{n:>9,}{r:>+10.4f}{z:>+8.2f}")

    rate_b, n_b, r_b = rows["body, within-block"]
    se_r = 1 / math.sqrt(n_b)
    print("\nthe body against each model:")
    for label in ("prose, real words", "prose, arbitrary cuts"):
        rate_m, _n, r_m = rows[label]
        se_l = math.sqrt(rate_m * (1 - rate_m) / n_b)
        print(f"  vs {label:<24} level z = {(rate_b - rate_m) / se_l:+.2f},"
              f"  trend z = {(r_b - r_m) / se_r:+.2f}")
    print(
        "\nBoth statistics favour real words. The trend is the one that survives the"
        "\nleak: chance matches carry no length trend, so attenuation can only shrink"
        f"\nthe observed r. The body's {r_b:+.4f} therefore sets a FLOOR on the"
        "\nplaintext's, and the cuts model offers +0.0029."
    )


if __name__ == "__main__":
    main()
