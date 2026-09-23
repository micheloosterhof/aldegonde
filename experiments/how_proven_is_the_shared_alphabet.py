# ABOUTME: Prices the shared-alphabet claim as a likelihood ratio rather than a sigma, and
# ABOUTME: says how much more long-word material proof would take.
"""How strongly is "positions i and i+5 inside a word share an alphabet" actually held?

It rests on one number: 104 within-word lag-5 coincidences against 72.5 expected. The
digraph and trigraph cells are not extra evidence -- their hits are a subset of those 104,
so they are the same observation looked at again.

A sigma is the wrong summary for a claim with two named alternatives. Both are specified:

- **H0, no shared alphabet.** Coincidence at the ciphertext's own chance rate, measured by
  permuting the body's runes and keeping word lengths: p0 = 0.0344.
- **H1, shared alphabet.** Coincidence equals the plaintext's own within-word repeat rate
  at distance five, taken from English at matched word lengths: p1 = 0.0574. The doublet
  preventer breaks a distance-five relation whenever it fires in between, attenuating the
  excess by (1 - q)^5 = 0.872 at the measured q = 0.0271, which puts H1 at 0.0545.

## Result

    H1 raw              0.0574   expects 120.9    LR vs H0 = 123 : 1   observed -1.59 sigma
    H1 drift-adjusted   0.0545   expects 114.7    LR vs H0 = 265 : 1   observed -1.03 sigma
    H0 no sharing       0.0346   expects  72.8                         observed +3.72 sigma
    observed            0.0494              104

**Between one and three hundred to one.** That is strong, and it is not proof. It is also the right way round:
the observed value sits one sigma below the shared-alphabet prediction and nearly four
above the no-sharing one.

## What the number is sensitive to

H1's rate comes from English at matched word lengths across three registers, and English
registers differ. The likelihood ratio moves with p1 and nothing pins p1 to better than
about ten percent. The 265 should be read as a couple of hundred, not as a precise figure.

## What proof would need

    1,000 : 1   about 1.2x these 2,105 pairs
   10,000 : 1   about 1.7x

The pairs come from words of six runes or more, of which the body has 815. **The book does
not contain another 1.7 times that**, so within this corpus the claim tops out in the low
thousands to one. Settling it further needs material outside the body, or a consequence of
the shared alphabet that is not the coincidence rate -- and the local-channel theorem says
equality is the only invariant visible at every order, which is why there is one number
and not a battery.

    python how_proven_is_the_shared_alphabet.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ngram_kappa_inside_a_word import body_words, english_words  # noqa: E402

LAG = 5
MIN_LENGTH = 6
DRIFT = 0.0271  # the preventer's measured firing rate
DRAWS = 400


def by_length(words):
    """{word length: (hits at distance 5, pairs)}."""
    out: dict[int, tuple[int, int]] = {}
    for w in words:
        n = len(w)
        if n < MIN_LENGTH:
            continue
        hits = sum(w[i] == w[i + LAG] for i in range(n - LAG))
        seen, pairs = out.get(n, (0, 0))
        out[n] = (seen + hits, pairs + n - LAG)
    return out


def chance_rate(words, rng):
    """The ciphertext's own coincidence rate: runes permuted, word lengths kept."""
    lengths = [len(w) for w in words]
    flat = list("".join(words))
    total = hits = 0
    for _ in range(DRAWS):
        pool = rng.sample(flat, len(flat))
        at = 0
        for n in lengths:
            w = pool[at : at + n]
            at += n
            for i in range(max(0, n - LAG)):
                total += 1
                hits += w[i] == w[i + LAG]
    return hits / total


def main() -> None:
    rng = random.Random(3301)
    body, english = body_words(), english_words(rng)
    cb, ce = by_length(body), by_length(english)

    print(
        f"{'length':>7}{'body hits':>11}{'body pairs':>12}{'body rate':>11}"
        f"{'English rate':>14}{'English pairs':>15}"
    )
    weighted = total_pairs = 0.0
    for n in sorted(cb):
        hb, pb = cb[n]
        he, pe = ce.get(n, (0, 0))
        if pe < 50:
            continue
        weighted += pb * he / pe
        total_pairs += pb
        print(f"{n:>7}{hb:>11}{pb:>12}{hb / pb:>11.4f}{he / pe:>14.4f}{pe:>15,}")

    seen = sum(h for h, _ in cb.values())
    pairs = sum(p for _, p in cb.values())
    p0 = chance_rate(body, rng)
    p1 = weighted / total_pairs
    attenuation = (1 - DRIFT) ** LAG
    p1a = p0 + (p1 - p0) * attenuation

    print(f"\nthe body: {seen} of {pairs} pairs, rate {seen / pairs:.4f}\n")
    print(
        f"{'model':<22}{'rate':>8}{'expects':>10}{'LR vs H0':>12}{'observed sits':>16}"
    )
    for label, p in (
        ("H1 raw", p1),
        ("H1 drift-adjusted", p1a),
        ("H0 no sharing", p0),
    ):
        ratio = np.exp(
            stats.binom.logpmf(seen, pairs, p) - stats.binom.logpmf(seen, pairs, p0)
        )
        z = (seen - pairs * p) / np.sqrt(pairs * p * (1 - p))
        shown = "--" if label.startswith("H0") else f"{ratio:9.1f} : 1"
        print(f"{label:<22}{p:>8.4f}{pairs * p:>10.1f}{shown:>12}{z:>+15.2f}σ")

    best = np.exp(
        stats.binom.logpmf(seen, pairs, p1a) - stats.binom.logpmf(seen, pairs, p0)
    )
    print(
        f"\npreventer attenuation (1 - {DRIFT})^{LAG} = {attenuation:.3f}"
        f"\n\nto reach  1,000 : 1 takes about {np.log(1e3) / np.log(best):.1f}x these pairs"
        f"\nto reach 10,000 : 1 takes about {np.log(1e4) / np.log(best):.1f}x"
        f"\n\nThe pairs come from the {sum(1 for w in body if len(w) >= MIN_LENGTH)} body"
        " words of six runes or more."
        "\nThe book has no more, so within this corpus the claim tops out here."
    )


if __name__ == "__main__":
    main()
