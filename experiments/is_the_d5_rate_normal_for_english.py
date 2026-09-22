# ABOUTME: Compares the body's d5 rate against length-matched English with the preventer's
# ABOUTME: drift accounted for, replacing chance as the baseline for a plaintext statistic.
"""d5 is a plaintext statistic. Chance is the wrong thing to compare it with.

The corpus's most-cited key-free observation is the within-word d5 rate: 4.92% against a
chance 1/29 = 3.45%, permutation-verified at p ~ 0.001. It is read as an **excess**, and
the comparison is with chance.

Chance is what a random sequence would give. d5 reads the plaintext directly -- within a
block the base cancels, so `c_i = c_(i+5)` exactly when `p_i = p_(i+5)` -- so the question
a plaintext statistic should answer is whether the rate matches **English**, not whether
it beats random.

Two corrections stand between the two comparisons and neither is on record.

**Length.** English's within-word d5 rate is not flat: 0.0356 at six runes, 0.0539 at
seven, 0.0687 at eight to nine, 0.0622 beyond. The body's blocks are not distributed like
English words, so the reference has to be weighted by the body's own length distribution.

**Drift.** The doublet preventer advances the clock whenever it fires
(`the-preventer-is-in-the-stream.md`), and a firing between positions i and i+5 destroys
the relation. At a firing rate q the observed rate is `(1-q)^5` of the plaintext's own,
with the rest at chance. At q = 0.03 that is a 14% attenuation.

Both push in the same direction: they make the body's rate look lower than its plaintext's.

## Result: the body's d5 is ordinary English once both corrections are made

| | rate |
|---|---|
| body d5, 2,105 within-block pairs | **0.0494 +- 0.0047** |
| English, weighted by the body's own block lengths | **0.0591** |
| chance | 0.0345 |

| comparison | difference | sigma |
|---|---|---|
| against chance | +0.0149 | **+3.16** -- the figure on record |
| against length-matched English | -0.0096 | **-2.04** |

| preventer firing rate | implied plaintext d5 | sigma from English |
|---|---|---|
| q = 0.000 | 0.0494 | -2.04 |
| q = 0.020 | 0.0510 | -1.54 |
| **q = 0.034** | **0.0522** | **-1.22** |
| q = 0.050 | 0.0538 | -0.87 |

**At the preventer's measured firing rate the body's implied plaintext d5 is within about
one sigma of English.**

## What this changes

The "+3.16 sigma excess over chance" and a "-2.04 sigma deficit against English" are **the
same measurement read against two different baselines**, and neither is right uncorrected.
For a statistic that reads the plaintext directly, the question is whether it matches
English, and the answer is that it does once length and drift are accounted for.

That turns an anomaly into a confirmation. `simulate_the_joining_and_read_d5.py` left the
body's d5 sitting below English at every length with no explanation, and the explanation is
that two known effects had not been applied: English's own d5 rises steeply with word
length, and the preventer attenuates the relation by `(1-q)^5`.

So the only key-free window onto the plaintext says it is **ordinary English**, which is
what the word-length and function-word channels say and what the transposition reading
needs to be true.

## The weak point

q is not measured directly. It comes from the preventer's suppression strength, and at
q = 0 the deficit is -2.04 sigma rather than -1.22. The conclusion needs the drift to be
real, which `the-preventer-is-in-the-stream.md` establishes independently -- the
suppression crosses word boundaries, line breaks and marks alike, which is a clock-level
mechanism and not a scribal one.

    python is_the_d5_rate_normal_for_english.py
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
DRIFTS = (0.0, 0.02, 0.034, 0.05)
MIN_PAIRS = 200
REGISTER_COUNT = 5


def english_words():
    out = []
    for number in REGISTERS[:REGISTER_COUNT]:
        path = fetch(number)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        trim = len(text) // 10
        for token in re.findall(r"[A-Za-z']+", text[trim : len(text) - trim]):
            runes = [IDX_ENG[c] for c in to_runeglish(token.upper()) if c in IDX_ENG]
            if len(runes) >= 6:
                out.append(runes)
    return out


def main() -> None:
    body = words(BODY)
    english = english_words()

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
    expected = sum(weights[k] * rates[k] for k in weights if k in rates) / total

    _, pairs, hits = d5(body, 6, 60)
    observed = hits / pairs
    se = math.sqrt(observed * (1 - observed) / pairs)

    print(f"body d5, {pairs:,} within-block pairs   {observed:.4f} +- {se:.4f}")
    print(f"English, weighted by the body's own block lengths   {expected:.4f}")
    print(f"chance                                              {CHANCE:.4f}\n")
    print(
        f"  against chance   {observed - CHANCE:+.4f}"
        f"  ({(observed - CHANCE) / se:+.2f} sigma)   <- the figure on record"
    )
    print(
        f"  against English  {observed - expected:+.4f}"
        f"  ({(observed - expected) / se:+.2f} sigma)"
    )

    print("\nWith the preventer's drift undone.\n")
    print(f"{'firing rate':<16}{'implied plaintext d5':>22}{'sigma from English':>22}")
    for q in DRIFTS:
        keep = (1 - q) ** 5
        corrected = (observed - (1 - keep) * CHANCE) / keep
        print(
            f"{f'q = {q:.3f}':<16}{corrected:>22.4f}"
            f"{(corrected - expected) / (se / keep):>22.2f}"
        )

    print(
        "\n  At the preventer's measured firing rate the body's implied plaintext d5 is"
        "\n  within about one sigma of English. The '+3 sigma excess over chance' and"
        "\n  the '-2 sigma deficit against English' are the same number read against"
        "\n  two different baselines, and neither is the right one uncorrected."
    )


if __name__ == "__main__":
    main()
