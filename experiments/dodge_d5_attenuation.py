# ABOUTME: Tests whether the doublet dodge accounts for the LP's PARTIAL distance-5 leak,
# ABOUTME: predicting the attenuation from the doublet rate with no free parameter.
"""Does the dodge explain why d5 leaks only partly?

Michel's original question (September 2026): "what could break the d5 repeat is the
reduced doublet rule". This tests it quantitatively.

Under the length-clocked walk `g^5 = id`, so two positions five apart inside a word
share both the alphabet and the base, and coincide exactly when the plaintext does. That
makes d5 the one key-free channel, and it predicts the plaintext's own lag-5 rate with
nothing fitted. `period5-is-confirmed.md` records the observed leak as PARTIAL and the
full-versus-partial question as undecided.

The dodge supplies an attenuation, and its size is forced. The skip fires whenever the
emission would repeat, at some rate q; it fails, leaving a visible doublet, only when
the next schedule offset is zero, which is one phase in five. So

    q = 5 x d1                                     (from the observed doublet rate)
    d5 = (1-q)^5 x plaintext_d5 + (1-(1-q)^5)/29   (a skip in between kills the echo)

Both lines use the corpus's own doublet rate and nothing else. The walk is the q = 0
case of the same formula.

The register matters here: d5 pairs come only from words of six runes or more, so a
prose sample has to carry the LP's word-length distribution or the plaintext rate is
measured on the wrong words. The register is resampled to put an error bar on it.

**Result (2026-09-20): the dodge's prediction is near exact, and d5 still does not
decide.** The attenuation moves the residual from -0.41 SE to -0.04 SE, but the two
predictions sit 0.37 SE apart, so the corpus cannot separate them. A lean, not a finding.

The register is what makes this measurable at all. On raw prose, ignoring the LP's word
lengths, the plaintext lag-5 rate reads 0.0596 and both models look badly off (-2.2 and
-1.4 SE). Length-matched it reads 0.0521 and both are fine. d5 pairs come only from
words of six runes or more, and prose has more of those than the LP does, so the
unmatched figure is measuring the wrong words.

Run with no arguments.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ea_direction_test import PROSE_CACHE  # noqa: E402
from fingerprint_battery import lp_words  # noqa: E402
from quagmire_runner import load_clean, load_register  # noqa: E402

M = 29
DRAWS = 40


def lag_rate(words, distance: int) -> tuple[int, int]:
    """(coincidences, pairs) at `distance` inside words."""
    hits = pairs = 0
    for w in words:
        for j in range(len(w) - distance):
            pairs += 1
            hits += w[j] == w[j + distance]
    return hits, pairs


def main() -> None:
    rng = random.Random(3301)
    lp = lp_words()
    d1_hits, d1_pairs = lag_rate(lp, 1)
    d5_hits, d5_pairs = lag_rate(lp, 5)
    d1 = d1_hits / d1_pairs
    d5 = d5_hits / d5_pairs
    se5 = math.sqrt(d5 * (1 - d5) / d5_pairs)

    # the register must carry the LP's word lengths: d5 pairs come only from long words
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    pools, _table, _floor = load_register(PROSE_CACHE)
    plain5 = np.array(
        [
            lag_rate([rng.choice(pools[L])[:L] for L in lens], 5)[0] / d5_pairs
            for _ in range(DRAWS)
        ]
    )

    q = 5 * d1
    keep = (1 - q) ** 5
    print(f"LP: d1 {d1:.5f} ({d1_hits}/{d1_pairs}), d5 {d5:.5f} ({d5_hits}/{d5_pairs})")
    print(f"skip rate q = 5 x d1 = {q:.4f}; surviving echo (1-q)^5 = {keep:.4f}")
    print(
        f"length-matched plaintext d5 over {DRAWS} registers: "
        f"{plain5.mean():.5f} +- {plain5.std():.5f}\n"
    )

    walk = plain5.mean()
    dodge = keep * walk + (1 - keep) / M
    spread = math.hypot(se5, plain5.std())
    print(f"{'model':<34}{'predicted d5':>13}{'observed - predicted':>23}")
    for label, value in (
        ("length-clocked walk (g^5 = id)", walk),
        ("the same with the dodge", dodge),
    ):
        print(f"{label:<34}{value:>13.5f}{(d5 - value) / spread:>20.2f} SE")
    print(f"\nthe two predictions differ by {abs(walk - dodge) / spread:.2f} SE")

    assert plain5.mean() > 1 / M, "the plaintext must have a lag-5 excess to attenuate"
    assert 0 < keep < 1, "the attenuation must be a proper fraction"
    assert abs(d5 - dodge) < abs(d5 - walk), (
        "the attenuation should move the prediction toward the observation, or the "
        "mechanism does not help at all"
    )
    if abs(walk - dodge) / spread < 2:
        print(
            "under 2 SE apart: d5 does not decide between them, as recorded elsewhere"
        )


if __name__ == "__main__":
    main()
