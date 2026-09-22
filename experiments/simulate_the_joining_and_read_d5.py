# ABOUTME: Runs the joining model forward on real English runes and reads the d5-by-length
# ABOUTME: curve off the result, replacing the crossing-fraction arithmetic with simulation.
"""Stop approximating the dilution. Produce it.

`fit_the_merge_rate_from_d5.py` infers a merged fraction of 0.78 +- 0.28 against the
model's predicted 0.25, a 1.9-sigma tension, using an analytic crossing fraction of
`2/(L-5)`. That arithmetic makes three approximations at once:

- **one boundary per block.** At q = 0.40 a merged block can absorb a second short unit,
  and chains put two boundaries inside one block;
- **crossing pairs are independent.** With two boundaries a single d5 pair may straddle
  both, so crossings do not add;
- **the cross-boundary rate is chance.** It is close to chance but not exactly, since
  English constrains which letters end and begin adjacent words.

A forward simulation makes all three exact. Take real English words as rune sequences,
apply the joining rule to them, and measure the d5 rate on the merged sequences. Nothing
is assumed: the within-word rate, the cross-boundary rate, chained merges and overlapping
crossings all come out of the same run.

## What it tests

The body's d5-by-length curve against the curve the fitted model produces. If they agree,
the model's rate is right and the earlier tension was the arithmetic. If the simulated
curve is too shallow, the body really does show more merging than q = 0.40 gives.

## The comparison is honest only with the register caveat attached

The simulation supplies English's own within-word d5, which is the reference the body's
register may not match. That limit is not removed by simulating -- it is the same ceiling
`fit_the_merge_rate_from_d5.py` reaches, and the author's plaintext has 158 d5 pairs, far
too few to check.

## Result: merging does not dilute d5 at all, and the premise was false

| joining rate | 6 | 7 | 8-9 | 10-30 | chi2 vs the body |
|---|---|---|---|---|---|
| **the body** | 0.0352 | 0.0440 | 0.0474 | 0.0612 | |
| q = 0.00 | 0.0372 | 0.0520 | 0.0684 | 0.0623 | 8.3 |
| q = 0.40 | 0.0338 | 0.0565 | 0.0687 | 0.0634 | 9.5 |
| q = 0.70 | 0.0319 | 0.0585 | 0.0689 | 0.0632 | 10.3 |

**The curve barely moves.** At q = 0.70 the 8-9 cell reads 0.0689 against 0.0684 with no
joining at all. Merging does not dilute d5.

The analytic version assumed the **cross-boundary d5 rate is chance**. Measured directly,
concatenating every adjacent English word pair:

    d5 pairs not crossing the join   503,922   rate 0.0597
    d5 pairs crossing the join       813,861   rate 0.0620
    chance                                     0.0345

**The cross-boundary rate is 103 sigma above chance and level with the within-word rate.**
English constrains which letters end and begin adjacent words no less than it constrains
letters inside one, so a merge moves a d5 pair from one structured distribution to another
almost identical one. There is nothing to dilute.

## What this retracts

`fit_the_merge_rate_from_d5.py` reports merging detected at 2.8 sigma with the predicted
shape, and `can_d5_see_the_joining.py` at 2.0 sigma before it. **Both are void.** Their
entire signal is the gap between the body and English, converted into a merge rate by
dividing by `(within - chance)` -- a denominator that should have been `(within - cross)`,
which is 0.0597 - 0.0620, near zero and of the wrong sign.

The error came from reading "cross-word d5 count at chance" in the README as a fact about
plaintext. It is a fact about the body's **ciphertext** across a block boundary, where the
base changes and destroys the relation. Inside a merged block the base does not change, so
the plaintext's own cross-word structure shows through undiminished.

## What survives, and it is unexplained

The body's d5 curve sits **below** English at every length, most at 8-9: 0.0474 +- 0.0076
against 0.0687, **-2.8 sigma**. Pooled over the four cells that is chi2 8.3, P ~ 0.08.

Merging does not explain it, since merging changes nothing. Either the body's plaintext has
less distance-5 letter repetition than English prose -- a register difference -- or
something else is suppressing it. Unresolved, and the register question is the one the
author's 158 d5 pairs cannot answer.

    python simulate_the_joining_and_read_d5.py
"""

from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from can_d5_see_the_joining import BODY, d5, words  # noqa: E402
from compact_state_models import IDX_ENG, to_runeglish  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402

BANDS = ((6, 6), (7, 7), (8, 9), (10, 30))
RATES = (0.0, 0.25, 0.40, 0.55, 0.70)
THRESHOLD = 2
REGISTER_COUNT = 5


def english_stream():
    """English words as rune-index sequences, in running order."""
    out = []
    for number in REGISTERS[:REGISTER_COUNT]:
        path = fetch(number)
        if path is None:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        trim = len(text) // 10
        for token in re.findall(r"[A-Za-z']+", text[trim : len(text) - trim]):
            runes = [IDX_ENG[c] for c in to_runeglish(token.upper()) if c in IDX_ENG]
            if runes:
                out.append(runes)
    return out


def apply_joining(stream, q, rng, threshold=THRESHOLD):
    """Merge a short unit into the next, keeping the runes -- chains included."""
    out = list(stream)
    i = 0
    while i < len(out) - 1:
        if len(out[i]) <= threshold and rng.random() < q:
            out[i + 1] = out[i] + out[i + 1]
            out.pop(i)
            continue
        i += 1
    return out


def curve(rows):
    out = {}
    for lo, hi in BANDS:
        _, pairs, hits = d5(rows, lo, hi)
        out[(lo, hi)] = (hits / pairs if pairs else float("nan"), pairs)
    return out


def main() -> None:
    rng = random.Random(3301)
    stream = english_stream()
    body = curve(words(BODY))
    print(f"{len(stream):,} English words; {sum(len(w) for w in stream):,} runes.\n")

    header = "".join(f"{f'{lo}-{hi}':>13}" for lo, hi in BANDS)
    print(f"{'joining rate':<16}{header}")
    print(
        f"{'THE BODY':<16}"
        + "".join(
            f"{f'{body[b][0]:.4f}+-{math.sqrt(body[b][0] * (1 - body[b][0]) / body[b][1]):.3f}':>13}"
            for b in BANDS
        )
    )
    scores = {}
    for q in RATES:
        merged = apply_joining(stream, q, rng)
        sim = curve(merged)
        chi = 0.0
        for b in BANDS:
            se = math.sqrt(body[b][0] * (1 - body[b][0]) / body[b][1])
            chi += ((body[b][0] - sim[b][0]) / se) ** 2
        scores[q] = chi
        print(f"{f'q = {q:.2f}':<16}" + "".join(f"{sim[b][0]:>13.4f}" for b in BANDS))

    print(f"\n{'joining rate':<16}{'chi2 against the body, 4 cells':>34}")
    for q, chi in scores.items():
        print(f"{f'q = {q:.2f}':<16}{chi:>34.1f}")
    best = min(scores, key=scores.get)
    print(
        f"\n  best fit at q = {best:.2f}; the histogram fit gives 0.40."
        "\n  Every approximation in the analytic version -- one boundary per block,"
        "\n  independent crossings, a chance cross-boundary rate -- is exact here."
    )


if __name__ == "__main__":
    main()
