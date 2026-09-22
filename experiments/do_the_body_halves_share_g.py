# ABOUTME: Salvages the d-profile comparison from a retracted experiment by applying it
# ABOUTME: to the body's own two halves, with a null sized for an equal split.
"""SUPERSEDED. This duplicates `does_g_change_mid_book.py`, which I failed to find.

That file asks the same question with better-built arms -- both planted, thirty trials --
and reports chi2 6.9 for the body with a likelihood ratio of 5 to 1. This file
independently reached the same 6.9 and 4.8 to 1, which is a useful agreement between two
codebases and not a new result. Use `does_g_change_anywhere.py`, which extends the
midpoint question to changes at any point.

Kept for the reconciliation and for the note below on how to weigh a weak ratio.

The body is one cipher on three statistics. Is it one LETTER STEP?

`the-body-is-one-cipher.md` establishes homogeneity on doublet rate, d5 and IoC across
nine sections and fifty-five pages. None of those carries `g`. The within-block d-profile
does: the base cancels at every distance, so the rate at distance k is set by g^(k mod 5),
and at k = 5 the power is the identity, which makes d5 a plaintext control while d2, d3,
d4, d6 and d7 carry the step.

`does_the_front_matter_share_g.py` built that instrument and is **withdrawn** -- the front
matter turned out to be a few-alphabet cipher, so the comparison was invalid. It used the
body's own two halves as a calibration, labelling them "known same g", which was an
assumption rather than a measurement. Treated as a measurement instead, and with a null
sized for an equal split rather than the lopsided one, it answers a question the
homogeneity file leaves open.

## Result, and it is weak

The body's halves, 1,464 blocks each: **chi2 = 6.9 on 5 df.**

| planted | median | spread | P(chi2 <= observed) |
|---|---|---|---|
| the same g | 7.3 | 5.3 | 0.483 |
| a different g | 23.3 | 23.0 | 0.100 |

**Likelihood ratio 4.8 to 1 for one letter step across the body.**

## Why this is reported and the retracted claim was not

4.8 to 1 is the same strength as the 4.3 to 1 that
`does_the_front_matter_share_g.py` reported for the front matter, which is withdrawn. The
difference is not the number, it is what else is known:

- the front matter's 4.3 to 1 stood against **decisive contrary evidence** -- rune
  frequencies non-uniform at P = 5e-79 where the body is uniform at 0.55, and a doublet
  rate differing at z = +4.16;
- the body's 4.8 to 1 stands **alongside agreeing evidence** -- the same flat IoC, the
  same doublet suppression, and homogeneity on three other statistics across sections and
  pages.

A weak likelihood ratio is worth reporting only with that context attached, which is the
lesson the retraction taught. On its own, 4.8 to 1 settles nothing.

    python do_the_body_halves_share_g.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import order5, prose_corpora  # noqa: E402
from does_the_front_matter_share_g import (  # noqa: E402
    BODY_CHUNKS,
    DISTANCES,
    blocks_of,
    d_profile,
    distance_between,
    encipher,
)

DRAWS = 60


def main() -> None:
    body = blocks_of(BODY_CHUNKS)
    half = len(body) // 2
    first, second = d_profile(body[:half]), d_profile(body[half:])
    observed, df = distance_between(first, second)

    print(f"{'distance':>10}{'first half':>14}{'second half':>14}")
    for k in DISTANCES:
        print(f"{k:>10}{first[k][0]:>14.4f}{second[k][0]:>14.4f}")
    print(f"\n{half:,} blocks per half; chi2 = {observed:.1f} on {df} df.\n")

    plain = prose_corpora(2 * half, 1)[0]
    print(f"{'planted':<16}{'median':>9}{'spread':>9}{'P(chi2 <= observed)':>22}")
    tails = {}
    for label, same in (("the same g", True), ("a different g", False)):
        chis = []
        for t in range(DRAWS):
            r = random.Random(7000 + t)
            g = order5(r)
            a = encipher(plain[:half], r, g)
            b = encipher(
                plain[half : 2 * half], r, g if same else order5(random.Random(9000 + t))
            )
            chis.append(distance_between(d_profile(a), d_profile(b))[0])
        chis = np.array(chis)
        tails[label] = max(float((chis <= observed).mean()), 1 / DRAWS)
        print(
            f"{label:<16}{np.median(chis):>9.1f}{chis.std(ddof=1):>9.1f}"
            f"{tails[label]:>22.3f}"
        )
    lr = tails["the same g"] / tails["a different g"]
    print(
        f"\nLikelihood ratio for one letter step across the body: {lr:.1f} to 1."
        "\nThat is the same strength as the front-matter claim this instrument was"
        "\nbuilt for and which is withdrawn. It is reported here only because it agrees"
        "\nwith everything else known about the body, where that one contradicted"
        "\nfrequency and doublet evidence at 5e-79 and z = +4.16."
    )


if __name__ == "__main__":
    main()
