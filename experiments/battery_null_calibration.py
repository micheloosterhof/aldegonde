# ABOUTME: Scores deliberately wrong ciphers on the fingerprint battery, to find how many
# ABOUTME: of its cells any polyalphabetic cipher passes without trying.
"""A count of battery cells landed is quoted as evidence. It had never been calibrated.

`length-clocked-walk.md`, `quagmire-odometer.md` and `doublet-dodge-walk.md` all report
their standing as "twelve free cells land, three do not", and that count is read as
support. `dodge_three_cells.py` showed the five-cell joint rate matches independence,
which raises the obvious question: what does a cipher with no relationship to the corpus
score?

Three deliberately wrong models answer it. None has a letter step, an order-5 structure, a
per-word step or a doublet rule -- none of the machinery the project models:

    independent alphabet per rune   a fresh random permutation at every position
    one random alphabet per word    per-word monoalphabetic, nothing else
    plain Vigenere, key length 11   a repeating shift

**Sixty draws are required, and the reason is a one-sided resolution limit.** The
battery's tail is `2 * min(below, 1 - below + 1/n)`, so a corpus value sitting ABOVE every
model draw yields `2/n` at best. At 25 draws that is 0.08, above the 0.05 threshold, and
such a cell can never register as a miss however wrong the model is. Forty draws is the
minimum; the battery's own `compare` uses sixty and so does this.

    python battery_null_calibration.py [--draws 60]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import M, fingerprint, lp_words, prose_corpora  # noqa: E402


def per_rune(plain, rng):
    out = []
    for w in plain:
        cw = []
        for p in w:
            a = list(range(M))
            rng.shuffle(a)
            cw.append(a[p])
        out.append(cw)
    return out


def per_word(plain, rng):
    out = []
    for w in plain:
        a = list(range(M))
        rng.shuffle(a)
        out.append([a[p] for p in w])
    return out


def vigenere(plain, rng):
    key = [rng.randrange(M) for _ in range(11)]
    i, out = 0, []
    for w in plain:
        cw = []
        for p in w:
            cw.append((p + key[i % len(key)]) % M)
            i += 1
        out.append(cw)
    return out


def score(gen, lp, cells, draws: int):
    rng = random.Random(3301)
    sims = [fingerprint(gen(plain, rng)) for plain in prose_corpora(2928, draws)]
    landed, missed = [], []
    for k in cells:
        v = np.array([s[k] for s in sims])
        sd = float(v.std())
        below = float((v <= lp[k]).mean())
        tail = 2 * min(below, 1 - below + 1 / len(v))
        if sd < 1e-12 and abs(float(v.mean()) - lp[k]) < 1e-9:
            tail = 1.0
        (landed if tail > 0.05 else missed).append(k)
    return landed, missed


def main() -> None:
    draws = 60
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lp = fingerprint(lp_words())
    cells = list(lp)
    print(f"battery: {len(cells)} cells; a cell lands when its empirical tail > 0.05\n")
    all_missed = []
    for name, gen in (
        ("independent alphabet per rune", per_rune),
        ("one random alphabet per word", per_word),
        ("plain Vigenere, key length 11", vigenere),
    ):
        landed, missed = score(gen, lp, cells, draws)
        all_missed.append(set(missed))
        print(f"{name:<32} lands {len(landed):>2}/{len(cells)}")
        print(f"{'':<32} misses {', '.join(missed)}")
    common = set.intersection(*all_missed)
    print(f"\nmissed by ALL THREE wrong models: {', '.join(sorted(common))}")
    print(
        f"\nA cipher with a fresh random alphabet at every position -- no letter step, no"
        f"\norder-5 structure, no per-word step, no doublet rule -- lands"
        f" {len(cells) - len(all_missed[0])} of {len(cells)}."
        "\nSo a cell count is not evidence: the baseline is high and the discriminating"
        "\npower sits in the few cells even a wrong cipher fails. Model comparisons"
        "\nbelong on those cells, not on the tally."
    )


if __name__ == "__main__":
    main()
