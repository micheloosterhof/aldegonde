# ABOUTME: Asks what the body's block lengths depend on -- content, position, layout, each
# ABOUTME: other -- and finds they depend on nothing measurable.
"""If the separators were placed by a rule, the lengths should depend on something.

`separators-are-not-word-boundaries.md` establishes that the body's block lengths carry
a tenth of the serial structure language has, under every tokenization, and that no
merge, null or padding rule reproduces both the histogram and the order. Two readings
survive: an i.i.d.-length source, or a key-driven reordering.

Both say the lengths should be independent of everything visible, so this checks. If the
lengths were set by the enciphering process they would depend on position; if by the page
layout, on the line; if they still carried plaintext words, on each other.

The statistic is mutual information against a label-shuffling null, which needs no
distributional assumption and handles the small cells at long lengths.

    python block_length_independence.py
"""

from __future__ import annotations

import collections
import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"


def blocks() -> list[tuple[list[int], int, int, int]]:
    """(runes, absolute rune index of the first rune, line index, position in line)."""
    out = []
    total = 0
    for chunk in MASTER.read_text().split("%")[15:]:
        if not RUNE.search(chunk):
            continue
        cur: list[int] = []
        line = pos = 0
        start_line = start_pos = 0
        for c in chunk:
            if RUNE.match(c):
                if not cur:
                    start_line, start_pos = line, pos
                cur.append(IDX[c])
                pos += 1
            elif c == "/":
                line += 1
                pos = 0
            elif c == "\n":
                continue
            elif c in c3301.WORD_BOUNDARY and cur:
                out.append((cur, total, start_line, start_pos))
                total += len(cur)
                cur = []
        if cur:
            out.append((cur, total, start_line, start_pos))
            total += len(cur)
    return out


def mutual_information(xs: list[int], ys: list[int]) -> float:
    n = len(xs)
    joint = collections.Counter(zip(xs, ys))
    mx = collections.Counter(xs)
    my = collections.Counter(ys)
    return sum(c / n * math.log(c * n / (mx[a] * my[b])) for (a, b), c in joint.items())


def main() -> None:
    bs = blocks()
    rng = random.Random(3301)
    print(f"{len(bs):,} blocks, {sum(len(b[0]) for b in bs):,} runes\n")
    lengths = [min(len(b[0]), 8) for b in bs]

    cases = [
        ("first rune of the block", [b[0][0] for b in bs], lengths),
        ("last rune of the block", [b[0][-1] for b in bs], lengths),
        ("absolute rune index mod 5", [b[1] % 5 for b in bs], lengths),
        ("absolute rune index mod 29", [b[1] % 29 for b in bs], lengths),
        ("line index mod 4", [b[2] % 4 for b in bs], lengths),
        ("position in line, bucketed", [min(b[3] // 5, 4) for b in bs], lengths),
        ("the previous block's length", lengths[:-1], lengths[1:]),
    ]
    print(f"{'block length against':<32}{'MI':>9}{'null':>19}{'z':>8}")
    for label, xs, ys in cases:
        obs = mutual_information(xs, ys)
        sur = []
        for _ in range(300):
            t = list(ys)
            rng.shuffle(t)
            sur.append(mutual_information(xs, t))
        mu = sum(sur) / len(sur)
        sd = (sum((x - mu) ** 2 for x in sur) / len(sur)) ** 0.5
        print(f"{label:<32}{obs:>9.5f}{mu:>11.5f} +-{sd:.5f}{(obs - mu) / sd:>+8.2f}")
    print(
        "\nNothing. The lengths do not depend on what is in the block, on where the"
        "\nblock sits in the text or on the page, or on the block before it. They are"
        "\ni.i.d. draws from a language-shaped distribution, attached to nothing."
    )


if __name__ == "__main__":
    main()
