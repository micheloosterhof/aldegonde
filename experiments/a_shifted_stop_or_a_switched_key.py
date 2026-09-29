# ABOUTME: Tests two proposals for the four-dot: a full stop displaced by a variable number
# ABOUTME: of words, and a key that switches cyclically at each mark rather than resetting.
"""Two readings of the four-dot that the existing tests do not cover.

**A displaced full stop.** `the_long_block_is_nowhere.py` scores a *fixed* displacement:
mean block length at each offset from a mark, with the body's largest value anywhere in
+-4 being +0.44 at offset +3 against English's +1.19 at -1. Every fixed shift is excluded
at 2.6 sigma or more, and `which_permutation_survives.py` extends that to -12.

A **variable** shift is not covered. If the mark sits one word past the stop sometimes
and two or none at other times, the long sentence-final block is smeared across offsets
and every per-offset mean is diluted.

The instrument for that is a forward model, not a window statistic. A symmetric window
mean or maximum has no power here, for a reason worth recording: English puts +1.19 at
offset -1 and -0.71 at offset +1, so any symmetric window averages the two away. Planting
a +-1 to +-3 shift in English moves the +-2 window mean from +0.05 to at most +0.08.
Instead, English's whole offset profile is smeared by each candidate shift distribution
and the body scored against the result.

**A switched key.** `does_the_cipher_restart.py` excludes a base *reset* at a mark: blocks
following one would share a base and coincide at the plaintext rate, and they do not
(z = -0.96 against +53 for a planted reset). That test assumes the mark returns the base
to one common value. A key that **cycles** through N keys, advancing at each mark, is
invisible to it: with N = 3 only every third span shares a base, and pooling all spans
dilutes the signal by the number of keys. Grouping the spans by mark index mod N recovers
it; N = 1 is the existing test.

## Result 1: a displaced stop is NOT excluded, and a fixed one still is

| the mark is | chi2, 8 offsets | P |
|---|---|---|
| exactly at the stop | 28.3 | **0.0004** |
| displaced by up to +-1 block | 13.0 | 0.11 |
| displaced by up to +-2 | 12.3 | 0.14 |
| displaced by up to +-3 | 8.1 | 0.43 |
| displaced by up to +-4 | 5.0 | 0.75 |
| unrelated to any stop | 5.6 | 0.69 |

A stop exactly at the mark is excluded, which is the anomaly restated. **A stop displaced
by a variable block or two is not excluded at all.** This is new: the fixed-displacement
test ruled out every constant shift, and a variable one survives because it flattens the
profile instead of moving the peak.

The fit improves monotonically with the size of the smear, and at +-3 or more it is
indistinguishable from "unrelated to any stop" (8.1 and 5.0 against 5.6). So the test
cannot separate a heavily smeared stop from no stop. What it establishes is narrower and
still useful: **the profile is flat, and a variable displacement is one of the things that
would flatten it.**

## Result 2: the key does not cycle at the mark, for any period to eight

Aligned coincidence among span-initial blocks, grouped by mark index mod N. Chance is
1/29 = 0.0345.

| keys in the cycle | observed | z |
|---|---|---|
| 1 | 0.0337 | -0.87 |
| 2 | 0.0341 | -0.49 |
| 3 | 0.0300 | -2.09 |
| 4 | 0.0357 | +0.63 |
| 5 | 0.0309 | -1.38 |
| 6 | 0.0310 | -1.26 |
| 8 | 0.0320 | -0.83 |

The control enciphers English with a real 3-key cycle and reads it back at +34.19 for
N = 3 and +22.83 for N = 6, its multiple, against +9.8 to +19.5 at the wrong periods. The
test works and the body shows nothing at any period.

That closes key switching at the four-dot as a family, not just the single-key reset
already on record.

    python a_shifted_stop_or_a_switched_key.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import (  # noqa: E402
    N_RUNES,
    order5,
    prose_corpora,  # noqa: E402
)
from does_the_cipher_restart import (  # noqa: E402
    aligned_rate,
    body_blocks,
    compose,
    power,
)
from final_lengthening_across_registers import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

WINDOWS = (1, 2, 3)
CYCLES = (1, 2, 3, 4, 5, 6, 8)
MIN_SPAN = 6


def offset_profile(spans, offsets):
    """Mean block length at each offset from a mark, minus the span interior.

    Negative offsets count back from the block the mark closes; positive ones count
    forward into the next span.
    """
    interior = np.array([x for s in spans for x in s[1:-1]], float)
    out = {}
    for o in offsets:
        vals = []
        for i in range(len(spans) - 1):
            a, b = spans[i], spans[i + 1]
            if len(a) < MIN_SPAN or len(b) < MIN_SPAN:
                continue
            vals.append(a[o] if o < 0 else b[o - 1])
        v = np.array(vals, float)
        out[o] = (
            float(v.mean() - interior.mean()),
            math.hypot(
                v.std(ddof=1) / math.sqrt(len(v)),
                interior.std(ddof=1) / math.sqrt(len(interior)),
            ),
        )
    return out


def smear(profile, offsets, shift):
    """What the profile becomes if the mark is written a random number of blocks late.

    A shift of s puts the true sentence end s blocks away, so the value seen at offset o
    is the unshifted value at o + s. Averaging over s uniform on -shift..+shift gives the
    profile a variable displacement would produce. Offsets outside the measured range
    contribute zero, which the wings justify.
    """
    out = {}
    for o in offsets:
        vals = [profile.get(o + s, (0.0, 0.0))[0] for s in range(-shift, shift + 1)]
        out[o] = float(np.mean(vals))
    return out


def first_blocks(marks):
    """The first block of each span, in order, with the spans closed by these marks."""
    blocks = body_blocks(marks)
    out, started = [], True
    for block, flag in blocks:
        if started or flag:
            out.append(block)
        started = False
    return [b for b, f in blocks if f]


def cycle_score(blocks, pool, cycle, rng, draws=120):
    """Aligned coincidence within each residue class mod `cycle`, pooled."""
    hits = trials = 0
    for r in range(cycle):
        group = blocks[r::cycle]
        if len(group) < 4:
            continue
        h, t = aligned_rate(group)
        hits += h
        trials += t
    if not trials:
        return float("nan"), float("nan")
    observed = hits / trials
    null = []
    for _ in range(draws):
        shuffled = list(blocks)
        rng.shuffle(shuffled)
        sampled = [rng.choice(pool) for _ in blocks]
        by_len: dict[int, list] = {}
        for b in pool:
            by_len.setdefault(len(b), []).append(b)
        sampled = [rng.choice(by_len[len(b)]) for b in blocks]
        h = t = 0
        for r in range(cycle):
            group = sampled[r::cycle]
            if len(group) < 4:
                continue
            gh, gt = aligned_rate(group)
            h += gh
            t += gt
        null.append(h / t)
    null = np.array(null)
    return observed, (observed - null.mean()) / null.std(ddof=1)


def simulate_cycle(plain, mark_every, rng, cycle):
    """The walk, with the base switching to key[i mod cycle] at each mark."""
    g = order5(rng)
    powers = [power(g, k) for k in range(5)]
    sigma = rng.sample(range(N_RUNES), N_RUNES)
    keys = [rng.sample(range(N_RUNES), N_RUNES) for _ in range(cycle)]
    base, clock, following, seen = list(keys[0]), 0, False, 0
    cipher, flags = [], []
    for w, word in enumerate(plain):
        flags.append(following)
        cipher.append([base[powers[(clock + j) % 5][p]] for j, p in enumerate(word)])
        clock += len(word)
        base = compose(base, compose(powers[(clock - 1) % 5], sigma))
        following = w % mark_every == mark_every - 1
        if following:
            seen += 1
            base, clock = list(keys[seen % cycle]), 0
    return cipher, flags


def main() -> None:
    rng = random.Random(3301)
    registers = [
        register_spans(p, rng) for p in (fetch(n) for n in REGISTERS) if p is not None
    ]
    body, author = body_spans(), author_spans()

    print("PART 1. A full stop displaced by a VARIABLE number of blocks.")
    print("English's profile is smeared by the shift and compared with the body's.")
    print("A symmetric window MEAN or MAXIMUM cannot do this: English puts +1.19 at")
    print("offset -1 and -0.71 at +1, so any symmetric window averages them away.\n")
    offsets = [-4, -3, -2, -1, 1, 2, 3, 4]
    ref_runs = [offset_profile(s, offsets) for s in registers]
    ref = {
        o: (
            float(np.mean([r[o][0] for r in ref_runs])),
            float(np.std([r[o][0] for r in ref_runs], ddof=1)),
        )
        for o in offsets
    }
    obs = offset_profile(body, offsets)
    aut = offset_profile(author, offsets)
    print(f"{'offset':>8}{'ten registers':>20}{'the author':>14}{'the body':>18}")
    for o in offsets:
        print(
            f"{o:>8}{f'{ref[o][0]:+.2f} +- {ref[o][1]:.2f}':>20}"
            f"{f'{aut[o][0]:+.2f}':>14}"
            f"{f'{obs[o][0]:+.2f} +- {obs[o][1]:.2f}':>18}"
        )

    print("\nSmearing English by each shift, then scoring the body against it.\n")
    flat = {o: (0.0, ref[o][1]) for o in offsets}
    print(f"{'the mark is':<28}{'chi2 (8 cells)':>16}{'P':>10}")
    from scipy import stats

    rows = []
    for shift in (0, 1, 2, 3, 4):
        predicted = smear({o: ref[o] for o in offsets}, offsets, shift)
        chi = sum(
            ((obs[o][0] - predicted[o]) / math.hypot(obs[o][1], ref[o][1])) ** 2
            for o in offsets
        )
        label = "exactly at the stop" if not shift else f"displaced by up to +-{shift}"
        rows.append((chi, label))
    chi_flat = sum(
        ((obs[o][0] - 0.0) / math.hypot(obs[o][1], flat[o][1])) ** 2 for o in offsets
    )
    rows.append((chi_flat, "unrelated to any stop"))
    for chi, label in rows:
        print(f"{label:<28}{chi:>16.1f}{stats.chi2.sf(chi, len(offsets)):>10.4f}")

    print("\n\nPART 2. A key that CYCLES through N keys, advancing at each mark.")
    print("Aligned coincidence among span-initial blocks within each residue class.")
    print("Chance is 1/29 = 0.0345; a shared base reads the plaintext rate.\n")
    blocks = first_blocks({"④"})
    pool = [b for b, _ in body_blocks({"④"})]
    print(f"{'keys in the cycle':<22}{'span starts':>13}{'observed':>11}{'z':>8}")
    for cycle in CYCLES:
        observed, z = cycle_score(blocks, pool, cycle, rng)
        print(f"{cycle:<22}{len(blocks):>13}{observed:>11.4f}{z:>+8.2f}")

    print(
        "\nControl: encipher English with a real 3-key cycle, then read every N back."
    )
    print("The true N must stand out and the wrong ones must not.\n")
    plain = prose_corpora(2896, 1)[0]
    cipher, flags = simulate_cycle(plain, 17, random.Random(7), 3)
    planted = [c for c, f in zip(cipher, flags) if f]
    print(f"{'keys read back':<22}{'observed':>11}{'z':>8}")
    for cycle in (1, 2, 3, 4, 6):
        observed, z = cycle_score(planted, cipher, cycle, rng)
        flag = "   <- the planted cycle" if cycle == 3 else ""
        print(f"{cycle:<22}{observed:>11.4f}{z:>+8.2f}{flag}")


if __name__ == "__main__":
    main()
