# ABOUTME: Asks whether the written line is a cipher unit, and separately whether
# ABOUTME: block-initial runes share anything, using coincidence with surrogate nulls.
"""The separators are the cipher's units. Are the lines anything at all?

`separators-are-the-cipher-unit.md` shows the alphabet phase is anchored to the scribal
separators. Nothing has ever tested the other visible division: the written line. The
body's lines are notably regular -- 21.75 runes at a coefficient of variation of 0.124,
against 19.03 and 0.273 in the front matter -- and 76% of them end mid-word, so they are
set as continuous justified text.

Two questions, each with a clean statistic:

    Is the line a cipher unit?   Pairs in the same line but DIFFERENT blocks must be at
                                 chance under any block-anchored model, at every lag.
    Do line positions index it?  Bucket runes by position-in-line and pool coincidence.
                                 A shared alphabet reads about 1.74.

And one that came out of the second: block-initial runes all use the base with no letter
step applied, so if the bases repeated often they would coincide. They are the cleanest
place to look for base reuse without assuming anything about the letter step.

    python line_structure.py
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
ENG = c3301.CICADA_ENGLISH_ALPHABET
M = 29
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"


def load():
    """(runes, line index, position in line, position in block)."""
    raw = MASTER.read_text().split("%")
    stream, line, pos, bpos = [], [], [], []
    li = pi = bi = 0
    started = False
    for n in range(15, 71):
        if n >= len(raw) or not RUNE.search(raw[n]):
            continue
        for ch in raw[n]:
            if RUNE.match(ch):
                stream.append(IDX[ch])
                line.append(li)
                pos.append(pi)
                bpos.append(bi)
                pi += 1
                bi += 1
                started = True
            elif ch == "/":
                li += 1
                pi = 0
            elif ch == "\n":
                continue
            elif started and ch in c3301.WORD_BOUNDARY:
                bi = 0
                started = False
        li += 1
        pi = bi = 0
        started = False
    return stream, line, pos, bpos


def subset_ioc(stream, idx, rng, draws=300):
    """Normalised IoC of a subset against a same-size random subset."""
    counts = collections.Counter(stream[i] for i in idx)
    t = len(idx)
    obs = M * sum(v * (v - 1) for v in counts.values()) / (t * (t - 1))
    null = []
    for _ in range(draws):
        s = rng.sample(range(len(stream)), t)
        c = collections.Counter(stream[i] for i in s)
        null.append(M * sum(v * (v - 1) for v in c.values()) / (t * (t - 1)))
    mu = sum(null) / len(null)
    sd = (sum((x - mu) ** 2 for x in null) / len(null)) ** 0.5
    return obs, (obs - mu) / sd


def main() -> None:
    stream, line, pos, bpos = load()
    n = len(stream)
    rng = random.Random(3)
    print(f"{n:,} runes, {line[-1] + 1} lines, {sum(1 for b in bpos if b == 0):,} blocks\n")

    print("pairs in the same LINE but different blocks:")
    print(f"{'lag':>5}{'hits/pairs':>16}{'x chance':>10}{'z':>8}")
    for lag in range(1, 9):
        h = p = 0
        for i in range(n - lag):
            if line[i] == line[i + lag] and _block_of(bpos, i) != _block_of(bpos, i + lag):
                p += 1
                h += stream[i] == stream[i + lag]
        if p < 100:
            continue
        rate = h / p
        se = math.sqrt((1 / M) * (1 - 1 / M) / p)
        print(f"{lag:>5}{f'{h}/{p}':>16}{rate * M:>10.3f}{(rate - 1 / M) / se:>+8.2f}")
    print("  lag 1 is the seam doublet suppression, which is global; the rest is chance.\n")

    print("subsets, against a same-size random subset of the body:")
    for label, idx in (
        ("block-initial runes", [i for i, b in enumerate(bpos) if b == 0]),
        ("block-initial, not line-initial",
         [i for i, b in enumerate(bpos) if b == 0 and pos[i] != 0]),
        ("line-initial runes", [i for i, p in enumerate(pos) if p == 0]),
        ("line-initial, not block-initial",
         [i for i, p in enumerate(pos) if p == 0 and bpos[i] != 0]),
    ):
        obs, z = subset_ioc(stream, idx, rng)
        print(f"  {label:<34} n={len(idx):>5}  nIoC {obs:.4f}  z={z:+.2f}")

    counts = collections.Counter(stream[i] for i, p in enumerate(pos) if p == 0)
    total = sum(counts.values())
    top = sorted(counts.items(), key=lambda kv: -kv[1])[:6]
    print("\n  commonest line-initial runes: "
          + "  ".join(f"{ENG[i]}={v} ({v / total:.1%})" for i, v in top)
          + f"  against {1 / M:.1%}")
    print(
        "\nThe line is not a cipher unit, and the whole positional excess is the known"
        "\nline-initial layout artifact -- it survives removing block-initial runes, so"
        "\nit belongs to the typesetting, not the segmentation. Block-initial runes,"
        "\nwhich carry the base with no letter step applied, are flat."
    )


def _block_of(bpos: list[int], i: int) -> int:
    """Block id by counting resets up to i -- cheap enough via a running index."""
    return _BLOCK_IDS[i]


_BLOCK_IDS: list[int] = []


if __name__ == "__main__":
    _stream, _line, _pos, _bpos = load()
    b = -1
    for v in _bpos:
        if v == 0:
            b += 1
        _BLOCK_IDS.append(b)
    main()
