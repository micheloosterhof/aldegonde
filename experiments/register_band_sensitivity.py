# ABOUTME: Measures how often a letter-step relation that sits in the observed doublet
# ABOUTME: band under one prose register stays in the band under another register.
"""How much does the d1 band filter depend on the stand-in register?

The keyword sweeps keep a letter-wheel candidate only if its predicted within-word
doublet rate -- the diagonal sum_x P(R(x), x) of its step relation R on the
plaintext's within-word adjacent-pair table P -- falls inside the Wilson band of
the observed rate (63 of 10,028). P is taken from stand-in prose (Pride and
Prejudice). The unsolved plaintext has its own P. If the same R lands in the band
under one book and outside it under another, the filter drops a true key whenever
the stand-in register is off, and the band must be widened by the measured spread.

Method: draw random permutations R, keep those inside the band under the reference
book, and report the share still inside the band under each other book, with the
spread of the ratio diag_other / diag_reference.

**Result (2026-09-19).** Of 4,838 random relations inside the band under Pride and
Prejudice, only 24-60% (typically ~45%) are still inside it under another book:
Emerson 46-52%, King James Bible 49%, Nietzsche 45-48%, Walden 54%, Blake 31-35%,
Beowulf 24%. The diagonal of one relation moves by a factor of 0.8 to 1.9 between
registers (10th-90th percentile), because it is a sum of 29 RARE pair frequencies,
and rare pairs are what differs between books. So a band built on one stand-in
register keeps a true letter wheel about half the time, before the same loss on the
sigma side. A sweep meant to exclude a family has to widen both bands by that
factor (about [0.004, 0.014] for d1), at roughly ten times the candidates per side.

Needs the books cached by `external_text_length_match.py --run`.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from external_text_length_match import BOOKS, CACHE  # noqa: E402
from runeglish_frequency import english_to_runeglish  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
BAND = (0.0049, 0.0080)  # Wilson 95% interval of 63 / 10,028
REFERENCE = 1342  # Pride and Prejudice, the sweeps' stand-in register
DRAWS = 3_000_000


def adjacent_table(text: str) -> np.ndarray:
    """P[a][b]: share of within-word adjacent pairs (a then b)."""
    table = np.zeros((M, M))
    for word in re.findall(r"[A-Za-z]+", text):
        runes = [IDX[c] for c in english_to_runeglish(word) if c in IDX]
        for a, b in zip(runes, runes[1:]):
            table[a, b] += 1
    return table / table.sum()


def book_text(number: int) -> str | None:
    path = (
        CACHE / f"pg{number}.txt"
        if number != REFERENCE
        else CACHE.parent / "pg1342.txt"
    )
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else None


def main() -> None:
    rng = np.random.default_rng(3301)
    reference = adjacent_table(book_text(REFERENCE))
    cols = np.arange(M)
    kept = []
    for _ in range(DRAWS // 100_000):
        perms = rng.random((100_000, M)).argsort(axis=1)
        diag = reference[perms, cols].sum(axis=1)  # sum_x P(R(x), x)
        kept.append(perms[(diag >= BAND[0]) & (diag <= BAND[1])])
    perms = np.concatenate(kept)
    ref_diag = reference[perms, cols].sum(axis=1)
    print(
        f"{len(perms):,} of {DRAWS:,} random relations sit in the band under the reference\n"
    )
    print(f"{'register':<52}{'still in band':>14}{'ratio p10':>11}{'p50':>7}{'p90':>7}")
    for number, title in BOOKS.items():
        text = book_text(number)
        if text is None:
            continue
        ratio = adjacent_table(text)[perms, cols].sum(axis=1) / ref_diag
        other = ratio * ref_diag
        inside = ((other >= BAND[0]) & (other <= BAND[1])).mean()
        p10, p50, p90 = np.percentile(ratio, [10, 50, 90])
        print(f"{title[:50]:<52}{inside:>13.0%}{p10:>11.2f}{p50:>7.2f}{p90:>7.2f}")


if __name__ == "__main__":
    main()
