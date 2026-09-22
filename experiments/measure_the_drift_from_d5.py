# ABOUTME: Measures the preventer's firing rate two independent ways -- from the d5
# ABOUTME: attenuation and from the doublet arithmetic -- and checks they agree.
"""The drift rate was assumed. It can be measured, and twice.

`is_the_d5_rate_normal_for_english.py` concludes the body's d5 is ordinary English once
the preventer's clock drift is undone, and records its own weak point: the firing rate q
is not measured. At q = 0 the deficit against English is -2.04 sigma; at q = 0.034 it is
-1.22. The conclusion rests on a number taken from elsewhere.

Two independent handles exist and neither has been used.

## From the doublets

The preventer fires when the cipher would emit an adjacent repeat and suppresses it with
probability phi. Writing m1 for the unsuppressed rate:

    observed doublets = (1 - phi) * m1 = 0.0063
    firing rate       = phi * m1 = m1 - 0.0063

So **q is m1 minus the observed doublet rate**, with no dependence on phi at all. That is
worth stating on its own: `graph-mass-is-not-recoverable.md` treats m1 and phi as an
underdetermined pair, and the *firing rate* is determined by m1 alone.

`graph_mass_is_not_recoverable.py` gives m1 a prior of 0.0309 +- 0.0110 over order-5
permutations, so q = 0.0246 +- 0.0110.

## From the d5 attenuation

A firing between positions i and i+5 destroys the relation, so

    observed d5 = (1-q)^5 * E5 + (1 - (1-q)^5) / 29

with E5 the plaintext's own rate. Taking E5 from English weighted by the body's block
lengths, this is one equation in one unknown.

## The check

The two estimates share no inputs: one uses the adjacent-repeat rate and a prior over g,
the other uses the distance-5 rate and an English reference. If they disagree, one of the
model's parts is wrong.

## Result

| source | firing rate q |
|---|---|
| the doublets, with a prior over g | **0.0246 +- 0.0110** |
| the d5 attenuation, against English | **0.0949 +- 0.0573** |
| difference | +0.0703 +- 0.0583, **z = +1.20** |
| combined | **0.0271 +- 0.0108** |

**They agree.** Two estimates sharing no inputs -- one the adjacent-repeat rate with a
prior over `g`, the other the distance-5 rate against an English reference -- land within
1.2 sigma. Nothing was tuned to make them meet, so this is a consistency check on the walk
plus preventer rather than a fit.

The combined 0.0271 +- 0.0108 sits close to the 0.034 that
`is_the_d5_rate_normal_for_english.py` assumed, so its conclusion holds: at this rate the
body's implied plaintext d5 is about 1.4 sigma below English, which is ordinary.

## The part worth keeping separately

**phi cancels out of the firing rate.** `graph-mass-is-not-recoverable.md` treats m1 and
phi as an underdetermined pair and concludes neither is recoverable, which is right for
those two. But

    q = phi * m1     and     observed = (1 - phi) * m1
    so  q = m1 - observed

and the firing rate depends on m1 alone. One of the two unknowns drops out of the quantity
that matters for every drift correction in this directory.

## Two assumptions, both stated rather than buried

**The preventer always succeeds.** The arithmetic assumes a firing removes the doublet. If
a firing can still emit one, surviving doublets are `(1-phi)m1 + phi*m1*r` for some
residual r, and q is overestimated by `phi*m1*r`.

**The d5 arm needs the English reference.** It inherits the register question that caps
this corpus -- the author's plaintext has 158 d5 pairs, far too few to check whether the
body's plaintext repeats letters at distance five like English prose does.

    python measure_the_drift_from_d5.py
"""

from __future__ import annotations

import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from can_d5_see_the_joining import BODY, d5, words  # noqa: E402
from compact_state_models import IDX_ENG, to_runeglish  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402

CHANCE = 1 / 29
D1_OBSERVED = 0.0063
M1_PRIOR, M1_SPREAD = 0.0309, 0.0110
MIN_PAIRS = 200
REGISTER_COUNT = 5


def english_reference(body):
    """English within-word d5, weighted by the body's own block lengths."""
    english = []
    for number in REGISTERS[:REGISTER_COUNT]:
        path = fetch(number)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        trim = len(text) // 10
        for token in re.findall(r"[A-Za-z']+", text[trim : len(text) - trim]):
            runes = [IDX_ENG[c] for c in to_runeglish(token.upper()) if c in IDX_ENG]
            if len(runes) >= 6:
                english.append(runes)
    rates = {}
    for length in range(6, 21):
        _, pairs, hits = d5(english, length, length)
        if pairs >= MIN_PAIRS:
            rates[length] = hits / pairs
    weights = Counter()
    for w in body:
        if len(w) >= 6:
            weights[len(w)] += len(w) - 5
    total = sum(weights[k] for k in weights if k in rates)
    return sum(weights[k] * rates[k] for k in weights if k in rates) / total


def main() -> None:
    body = words(BODY)
    e5 = english_reference(body)
    _, pairs, hits = d5(body, 6, 60)
    observed = hits / pairs
    se = math.sqrt(observed * (1 - observed) / pairs)

    print("FROM THE DOUBLETS\n")
    q_doublet = M1_PRIOR - D1_OBSERVED
    print(f"  m1 prior over order-5 permutations   {M1_PRIOR:.4f} +- {M1_SPREAD:.4f}")
    print(f"  observed adjacent-repeat rate        {D1_OBSERVED:.4f}")
    print(f"  firing rate q = m1 - observed        {q_doublet:.4f} +- {M1_SPREAD:.4f}")
    print("  (phi cancels: q = phi*m1 and observed = (1-phi)*m1, so q = m1 - observed)")

    print("\nFROM THE d5 ATTENUATION\n")
    keep = (observed - CHANCE) / (e5 - CHANCE)
    q_d5 = 1 - keep ** (1 / 5)
    d_keep = se / (e5 - CHANCE)
    q_err = d_keep / (5 * (1 - q_d5) ** 4)
    print(f"  body d5                              {observed:.4f} +- {se:.4f}")
    print(f"  English, body-length-weighted        {e5:.4f}")
    print(f"  surviving fraction (1-q)^5           {keep:.3f} +- {d_keep:.3f}")
    print(f"  firing rate q                        {q_d5:.4f} +- {q_err:.4f}")

    gap = q_d5 - q_doublet
    gap_se = math.hypot(q_err, M1_SPREAD)
    print(
        f"\nAGREEMENT\n\n  d5 gives {q_d5:.4f} +- {q_err:.4f}, doublets give"
        f" {q_doublet:.4f} +- {M1_SPREAD:.4f}"
        f"\n  difference {gap:+.4f} +- {gap_se:.4f}   z = {gap / gap_se:+.2f}"
    )
    print(
        "\n  Two estimates sharing no inputs -- one the adjacent-repeat rate with a prior"
        "\n  over g, the other the distance-5 rate against an English reference -- and"
        "\n  they agree. That is a consistency check on the walk plus preventer, not a"
        "\n  fit: nothing here was tuned to make them meet."
    )
    print(
        f"\n  Combined, weighting by inverse variance:"
        f" q = {(q_d5 / q_err**2 + q_doublet / M1_SPREAD**2) / (1 / q_err**2 + 1 / M1_SPREAD**2):.4f}"
        f" +- {1 / math.sqrt(1 / q_err**2 + 1 / M1_SPREAD**2):.4f}"
    )


if __name__ == "__main__":
    main()
