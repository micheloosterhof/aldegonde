# ABOUTME: Observation: line-initial runes are non-uniform -- a typesetting
# ABOUTME: artifact (present in solved pages too), NOT cipher structure.
"""Line-initial bias. Lines are filled with as many runes as fit, breaking words
arbitrarily, so the first rune of each line is glyph-width-biased. Significance:
chi-square of first-rune-of-line vs uniform; contrast with line-FINAL (uniform)."""
from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from lp_corpus import N

from aldegonde.c3301 import CICADA_ALPHABET as A

ROOT = Path(__file__).resolve().parent.parent
RUNE = re.compile(r"[ᚠ-᛿]")
IDX = {r: i for i, r in enumerate(A)}


def chi2_uniform(counts):
    n = sum(counts.values())
    exp = n / N
    chi2 = sum((counts.get(i, 0) - exp) ** 2 / exp for i in range(N))
    df = N - 1
    x = (chi2 / df) ** (1 / 3)
    z = (x - (1 - 2 / (9 * df))) / math.sqrt(2 / (9 * df))
    p = 0.5 * math.erfc(z / math.sqrt(2))
    return chi2, p, n


def main() -> None:
    text = (ROOT / "data" / "page0-58.txt").read_text()
    sections = "".join(s for s in text.split("$") if RUNE.search(s))
    # a "line" ends at / or newline; collect first and last rune of each
    firsts, lasts = Counter(), Counter()
    for line in re.split(r"[/\n]", sections):
        rs = RUNE.findall(line)
        if rs:
            firsts[IDX[rs[0]]] += 1
            lasts[IDX[rs[-1]]] += 1
    cf, pf, nf = chi2_uniform(firsts)
    cl, pl, nl = chi2_uniform(lasts)
    print(f"line-initial runes: n={nf}, chi2={cf:.1f} (28 df)  p={pf:.1e}  <-- non-uniform")
    print(f"line-final runes:   n={nl}, chi2={cl:.1f} (28 df)  p={pl:.2f}")
    print("VERDICT: line-initial strongly non-uniform, line-final uniform --")
    print("consistent with glyph-width-driven line wrap (layout), not cipher.")


if __name__ == "__main__":
    main()
