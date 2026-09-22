# ABOUTME: Asks whether the enciphered front matter and the body use the same letter step g,
# ABOUTME: using the within-block d-profile, with d5 as a built-in plaintext-register control.
"""Does the book use one letter step throughout, or did it change at page fifteen?

`the-body-is-one-cipher.md` shows the body is homogeneous across its own sections and
pages. It does not compare the body with the **enciphered front matter** -- the nine
ASCII-convention chunks (0, 1, 2, 4, 5, 6, 7, 12, 13) that are still unsolved, as
`marks-are-not-clause-punctuation.md` establishes by scoring each chunk as runeglish.

That comparison matters twice over. The front matter is the control in
`encipherment_does_not_break_the_link.py`, which shows enciphered LP text keeps the
sentence-final lengthening at +1.21 +- 0.33 where the body reads -0.17 +- 0.21. A control
from a different cipher is a weaker control. And if the two sections share `g`, every
constraint on it can be measured on 14,600 runes instead of 12,956.

## The instrument, and why d5 is the control

Within a block the base cancels at every distance:

    c_i = c_(i+k)   iff   p_i = g^(k mod 5)(p_(i+k))

So the coincidence rate at distance k is set by `g` raised to k mod 5, together with the
plaintext's own repeat structure at that distance. **At k = 5 the power is the identity**,
so every `g` predicts the same thing and the rate measures the plaintext alone.

That splits the profile cleanly:

- **d5 is a register control.** If the two sections disagree there, they differ in
  plaintext and nothing about `g` can be read from the rest.
- **d2, d3, d4, d6, d7 carry `g`.** Agreement is evidence of a shared step.
- **d1 is unusable.** The body's adjacent rate is pushed down by the doublet preventer
  (0.0063 against an unsuppressed ~0.031) and `nothing-else-in-the-book-suppresses-repeats.md`
  records that no other part of the book does this, so the two sections are not comparable
  at distance 1. `the-preventer-is-strictly-adjacent.md` confirms the other distances are
  untouched.

## The power check comes first

The front matter is small. Before any cross-section claim, the same instrument is run on
the body's own two halves, where the answer is known to be "same `g`", and on simulated
pairs enciphered with the same and with different `g`. If it cannot separate those, it
cannot answer the real question and the result is a bound rather than a verdict.

## Result: weak support for one letter step through the whole book

| corpus | pairs | d2 | d3 | d4 | d5 | d6 | d7 |
|---|---|---|---|---|---|---|---|
| the body | 19,284 | 0.0347 | 0.0370 | 0.0410 | 0.0492 | 0.0245 | 0.0421 |
| the body, first half | 9,735 | 0.0370 | 0.0348 | 0.0364 | 0.0512 | 0.0172 | 0.0476 |
| the body, second half | 9,549 | 0.0324 | 0.0393 | 0.0457 | 0.0472 | 0.0318 | 0.0365 |
| the enciphered front matter | 2,218 | 0.0326 | 0.0430 | 0.0401 | 0.0586 | 0.0625 | 0.0986 |

Chance is 0.0345.

**The register control passes.** d5, which every `g` predicts alike, reads 0.0492 +- 0.0048
in the body against 0.0586 +- 0.0158 in the front matter, z = -0.57. The two sections do
not differ in plaintext, so the rest of the profile can be read.

**The instrument works, checked twice.** On simulated pairs at these exact sizes it gives
a median chi2 of 5.1 for a shared `g` and 15.6 for different ones, on 5 degrees of
freedom. On real data the body's own two halves -- known to share `g` -- give 6.9.

**The body against the front matter gives 6.0**, which is 60.5% of the shared-`g` arm and
14.0% of the different-`g` arm: a likelihood ratio of **4.3 to 1 for a shared letter
step.**

That is weak evidence and is reported as such. The arms overlap heavily because the front
matter supplies only 467 blocks and 2,218 within-block pairs against the body's 19,284,
and most of the observed chi2 comes from d6 and d7, where the front matter's 0.0625 and
0.0986 sit on the fewest pairs in the table.

## What it is worth

Two things, both modest.

`encipherment_does_not_break_the_link.py` uses the enciphered front matter as the control
that shows a length-preserving cipher keeps the sentence-final lengthening (+1.21 +- 0.33
against the body's -0.17 +- 0.21). A control drawn from a different cipher would be
weaker. At 4.3 to 1 the control is somewhat better founded than before and not
established.

If the step really is shared, `g` can be constrained on 14,752 runes rather than 12,956 --
an 11% gain in pairs, which does not change any search cost materially.

**What would settle it:** more enciphered same-cipher text, which the book does not have,
or a constraint on `g` strong enough that the two sections can be tested for agreeing on
the same candidate rather than on a summary statistic.

    python does_the_front_matter_share_g.py
"""

from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import N_RUNES, order5, prose_corpora  # noqa: E402
from does_the_cipher_restart import compose, power  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
INDEX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
ENCIPHERED_FRONT = (0, 1, 2, 4, 5, 6, 7, 12, 13)
BODY_CHUNKS = range(15, 71)
DISTANCES = (2, 3, 4, 5, 6, 7)
CARRY_G = (2, 3, 4, 6, 7)
DRAWS = 200


def blocks_of(chunks) -> list[list[int]]:
    """Blocks as rune indices; line breaks do not cut a block, separators do."""
    text = MASTER.read_text().split("%")
    out, cur = [], []
    for n in chunks:
        if n >= len(text):
            continue
        for ch in text[n]:
            if RUNE.match(ch):
                cur.append(INDEX[ch])
            elif ch in "/\n":
                continue
            elif ch in c3301.WORD_BOUNDARY and cur:
                out.append(cur)
                cur = []
        if cur:
            out.append(cur)
            cur = []
    return out


def d_profile(blocks, distances=DISTANCES):
    """{distance: (rate, standard error, pairs)} from within-block pairs only."""
    out = {}
    for k in distances:
        hits = trials = 0
        for b in blocks:
            for i in range(len(b) - k):
                trials += 1
                hits += b[i] == b[i + k]
        p = hits / trials if trials else float("nan")
        out[k] = (p, math.sqrt(p * (1 - p) / trials) if trials else float("nan"), trials)
    return out


def distance_between(a, b, distances=CARRY_G) -> tuple[float, int]:
    """Chi-squared between two profiles over the distances that carry g."""
    chi = 0.0
    for k in distances:
        se = math.hypot(a[k][1], b[k][1])
        chi += ((a[k][0] - b[k][0]) / se) ** 2
    return chi, len(distances)


def encipher(plain, rng, g=None):
    """The length-clocked walk with no preventer, which the d-profile does not need."""
    g = g or order5(rng)
    powers = [power(g, k) for k in range(5)]
    sigma = rng.sample(range(N_RUNES), N_RUNES)
    base, clock = rng.sample(range(N_RUNES), N_RUNES), 0
    out = []
    for word in plain:
        out.append([base[powers[(clock + j) % 5][p]] for j, p in enumerate(word)])
        clock += len(word)
        base = compose(base, compose(powers[(clock - 1) % 5], sigma))
    return out


def show(label, profile):
    row = f"{label:<30}{sum(v[2] for v in profile.values()):>9,}"
    for k in DISTANCES:
        p, se, _ = profile[k]
        row += f"{f'{p:.4f}':>9}"
    print(row)


def main() -> None:
    body = blocks_of(BODY_CHUNKS)
    front = blocks_of(ENCIPHERED_FRONT)
    half = len(body) // 2
    print(
        f"body {sum(len(b) for b in body):,} runes in {len(body):,} blocks; "
        f"enciphered front matter {sum(len(b) for b in front):,} runes "
        f"in {len(front):,} blocks.\n"
    )
    print(f"{'corpus':<30}{'pairs':>9}" + "".join(f"{f'd{k}':>9}" for k in DISTANCES))
    profiles = {
        "the body": d_profile(body),
        "the body, first half": d_profile(body[:half]),
        "the body, second half": d_profile(body[half:]),
        "the enciphered front matter": d_profile(front),
    }
    for label, p in profiles.items():
        show(label, p)
    print("  chance is 1/29 = 0.0345")

    print("\nd5 first: if the two disagree here they differ in plaintext, not in g.\n")
    a, b = profiles["the body"][5], profiles["the enciphered front matter"][5]
    se = math.hypot(a[1], b[1])
    print(
        f"  body {a[0]:.4f} +- {a[1]:.4f}   front matter {b[0]:.4f} +- {b[1]:.4f}"
        f"   z = {(a[0] - b[0]) / se:+.2f}"
    )

    print("\nAgreement over the distances that carry g (2, 3, 4, 6, 7).\n")
    print(f"{'pair':<44}{'chi2':>9}{'df':>5}")
    for label, x, y in (
        (
            "the body's two halves (known same g)",
            profiles["the body, first half"],
            profiles["the body, second half"],
        ),
        (
            "the body against the enciphered front matter",
            profiles["the body"],
            profiles["the enciphered front matter"],
        ),
    ):
        chi, df = distance_between(x, y)
        print(f"{label:<44}{chi:>9.1f}{df:>5}")

    print("\nCan the instrument tell same g from different g at these sizes?\n")
    n_body, n_front = len(body), len(front)
    plain = prose_corpora(n_body + n_front, 1)[0]
    observed = distance_between(
        profiles["the body"], profiles["the enciphered front matter"]
    )[0]
    arms = {}
    for label, same in (("the same g", True), ("a different g", False)):
        chis = []
        for t in range(DRAWS):
            r = random.Random(1000 + t)
            g = order5(r)
            big = encipher(plain[:n_body], r, g)
            small = encipher(
                plain[n_body:], r, g if same else order5(random.Random(5000 + t))
            )
            chis.append(distance_between(d_profile(big), d_profile(small))[0])
        arms[label] = np.array(chis)
    print(f"{'planted':<30}{'median':>9}{'P(chi2 <= observed)':>22}")
    for label, chis in arms.items():
        share = float((chis <= observed).mean())
        print(f"{label:<30}{np.median(chis):>9.1f}{share:>22.3f}")
    a = max(float((arms["the same g"] <= observed).mean()), 1 / DRAWS)
    b = max(float((arms["a different g"] <= observed).mean()), 1 / DRAWS)
    print(
        f"\nObserved chi2 = {observed:.1f}. Likelihood ratio {a / b:.1f} to 1 for a"
        "\nSHARED letter step. That is weak evidence, not a finding: the two arms"
        "\noverlap heavily at 467 front-matter blocks, and the front matter contributes"
        "\nonly 2,218 within-block pairs against the body's 19,284."
    )


if __name__ == "__main__":
    main()
