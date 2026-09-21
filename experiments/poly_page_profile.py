# ABOUTME: Characterises the four polyalphabetic LP transcription pages: IoC against a flat
# ABOUTME: null, Friedman alphabet count, period scans, and a windowed test for local plaintext.
"""What kind of cipher is on the four pages that are neither monoalphabetic nor flat?

`solved-page-testbed.md` leaves pages 1, 2, 12 and 13 enciphered. Their normalised
index of coincidence sits at 1.07-1.28: below the 1.52-2.06 of plaintext and
monoalphabetic ciphertext, and above the unsolved corpus's 1.000. They are the only
material in the book at that intermediate level, which makes them the closest thing
to a bridge between the solved front matter and the unsolved body.

Four measurements, in the order they should be trusted:

  elevation    is the IoC really above flat at these page lengths, or is 1.07-1.28
               what 93-264 runes of random text looks like? Simulated null.
  diversity    the Friedman estimate of how many alphabets the elevation implies,
               k ~ (I_plain - 1) / (I_obs - 1) with I_plain from the LP's own
               plaintext pages rather than from English prose
  period       coset IoC for every period to 12, and kappa autocorrelation to shift
               25. If the alphabets cycle, one of these should find it.
  locality     windowed IoC, to rule out a plaintext region raising the whole-page
               figure while the rest is flat

    python poly_page_profile.py [--draws 4000]
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

from aldegonde import c3301
from aldegonde.stats import ioc

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
POLY = (1, 2, 12, 13)
MONO = (0, 4, 5, 6, 7)
PLAIN = (3, 8, 9, 10, 11, 14)
WINDOW = 60


def page_runes(n: int) -> list[int]:
    pages = MASTER.read_text().split("%")
    return [IDX[c] for c in pages[n] if RUNE.match(c)]


def nioc(r: list[int]) -> float:
    return ioc(r) * M


def main() -> None:
    draws = 4000
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])
    rng = random.Random(3301)

    plain_level = sum(nioc(page_runes(n)) for n in PLAIN) / len(PLAIN)
    print(
        f"plaintext IoC level, from the LP's own plaintext pages: {plain_level:.3f}\n"
    )

    print("elevation and diversity")
    print(
        f"{'page':>5}{'runes':>7}{'IoC':>8}{'z vs flat':>11}{'p':>9}{'k (Friedman)':>14}"
    )
    data = {}
    for n in POLY:
        r = page_runes(n)
        data[n] = r
        obs = nioc(r)
        nulls = [nioc([rng.randrange(M) for _ in range(len(r))]) for _ in range(draws)]
        mu = sum(nulls) / len(nulls)
        sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5
        p = (sum(1 for x in nulls if x >= obs) + 1) / (len(nulls) + 1)
        k = (plain_level - 1) / (obs - 1) if obs > 1 else float("inf")
        print(
            f"{n:>5}{len(r):>7}{obs:>8.3f}{(obs - mu) / sd:>11.2f}{p:>9.4f}{k:>14.1f}"
        )

    print("\nperiod scan: coset IoC (a real period should reach the plaintext level)")
    print(f"{'period':>7}" + "".join(f"{f'p{n}':>8}" for n in POLY))
    for p in range(1, 13):
        row = f"{p:>7}"
        for n in POLY:
            vals = [nioc(data[n][i::p]) for i in range(p) if len(data[n][i::p]) >= 12]
            row += f"{sum(vals) / len(vals):>8.2f}" if vals else f"{'-':>8}"
        print(row)

    print("\nkappa autocorrelation, best shift per page (25 shifts tried each)")
    for n in POLY:
        r = data[n]
        best = []
        for d in range(1, 26):
            m = len(r) - d
            if m < 25:
                continue
            hits = sum(1 for i in range(m) if r[i] == r[i + d])
            sd = (m * (1 / M) * (1 - 1 / M)) ** 0.5
            best.append(((hits - m / M) / sd, d))
        best.sort(reverse=True)
        top = "  ".join(f"d={d} z={z:+.1f}" for z, d in best[:3])
        print(f"  page {n:>2}: {top}")

    print(
        f"\nwindowed IoC (window {WINDOW}, step 20): a plaintext region would show 1.5+"
    )
    for group, label in ((POLY, "poly"), (MONO[:1], "mono"), (PLAIN[1:2], "PLAIN")):
        for n in group:
            r = page_runes(n)
            vals = [
                nioc(r[a : a + WINDOW])
                for a in range(0, max(1, len(r) - WINDOW), 20)
                if len(r[a : a + WINDOW]) == WINDOW
            ]
            print(f"  page {n:>2} [{label}]: " + " ".join(f"{v:.2f}" for v in vals))


if __name__ == "__main__":
    main()
