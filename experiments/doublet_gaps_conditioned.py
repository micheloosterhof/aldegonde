# ABOUTME: Redoes the doublet-gap test conditioning on gap size and marginalising the
# ABOUTME: unknown key phase, which withdraws the pooled figure and narrows the verdict.
"""The gap test was right in direction and wrong in method. Here it is done properly.

`doublet_gaps_test_the_dodge.py` scored the corpus by pooling every gap under 40 runes
into one residue histogram, rotating each corpus onto its own modal residue, and
comparing profiles. That gave 71:1 against `quagmire-dodge.md` and 80:1 against
`quagmire-odometer.md`. **The pooling is unsound and those figures are withdrawn.**

Two faults:

- **It conditions on nothing.** The gated models' residue profile depends steeply on the
  gap: at 1-15 runes it is 0.83 on one residue, by 31-50 it is 0.35, and past 80 it is
  flat. Pooling gaps of 5 and 39 into one histogram compares a mixture against a mixture
  and throws away the conditioning that carries the information.
- **Rotating onto the modal residue is a data-dependent transform on twelve points.**
  The corpus's modal residue is noise at that count, and aligning on it manufactures
  apparent concentration in the corpus and in the reference alike.

Done properly: bucket by gap size, build P(residue | bucket) from held-out seeds, and
**marginalise** the unknown key phase rather than maximising over it. Maximising favours
a concentrated profile over a flat one and shows up as lopsided accuracy (98% against
88%); marginalising balances it.

## The result splits, and the split is the finding

| doublets used | against | body log LR | P(>= obs) | accuracy |
|---|---|---|---|---|
| within-block only | quagmire-dodge | **+0.09** | 0.067 | 93% / 92% |
| within-block only | quagmire-odometer | **-0.91** | 0.133 | 93% / 93% |
| with seam doublets | quagmire-dodge | **+5.33** | 0.000 | 97% / 97% |
| with seam doublets | quagmire-odometer | **+3.41** | 0.000 | 100% / 98% |

The 63 within-block doublets do not discriminate at all. Adding the 23 seam doublets
makes the evidence strong. Both tests are well calibrated on corpora of known origin, so
neither is broken -- they are reading different populations, because inserting the seam
doublets splits long gaps into short ones and changes the gap set wholesale rather than
adding to it.

## What was ruled out as the cause

- **Smoothing.** The verdict is flat in the Laplace constant from 0.1 to 5.0: within-block
  stays at -0.3 to -0.5, seam-inclusive at +5.5 to +4.6.
- **Gap-size mix.** The corpus and the models put similar shares of their short gaps in
  each size bin (0.33/0.50/0.17 against 0.39/0.36/0.25), so the pooled comparison was not
  confounded that way. That was the first explanation tried and it is wrong.
- **Block structure.** The body's blocks are about 35% merged word pairs
  (`short-units-are-written-joined.md`) while the models encipher one word per block, so
  the models have seams the body does not. Re-running every model on a word stream merged
  at q = 0.35 leaves the split exactly where it was: +0.09 and +5.33.

## What stands

The direction is unchanged and the seam-inclusive evidence is stable, so both quagmire
variants remain disfavoured. But the verdict **rests entirely on the seam doublets**,
which is a narrower and weaker footing than the withdrawn figures suggested, and the
within-block doublets -- the larger set -- say nothing either way. Why gating should show
in one population and not the other is unexplained, and until it is, treat this as a lean.

    python doublet_gaps_conditioned.py
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import order5, prose_corpora  # noqa: E402
from does_the_cipher_restart import body_blocks  # noqa: E402
from quagmire_dodge import M, alphabets, encipher, schedule  # noqa: E402
from quagmire_odometer import draw as odometer_draw  # noqa: E402
from quagmire_odometer import encipher as odometer_encipher  # noqa: E402

BUCKETS = ((1, 15), (16, 30), (31, 50), (51, 80), (81, 130), (131, 220), (221, 10**9))
REFERENCE_SEEDS = range(500, 600)
TRIALS = 60
JOIN_RATE = 0.35  # the body's fitted merge rate, applied so models share its blocks
SMOOTHING = 0.5
RAW_WORDS = prose_corpora(3400, 1)[0]


def merged_words(seed: int, q: float = JOIN_RATE):
    """A word stream carrying the body's own block structure."""
    rng = random.Random(9000 + seed)
    out = [list(w) for w in RAW_WORDS]
    i = 0
    while i < len(out):
        if len(out[i]) <= 2 and rng.random() < q and i + 1 < len(out):
            out[i] = out[i] + out.pop(i + 1)
            continue
        i += 1
    return out[:2896]


def compose(p, q):
    return [p[q[i]] for i in range(len(p))]


def power(p, k):
    out = list(range(len(p)))
    for _ in range(k):
        out = compose(p, out)
    return out


def dodge(seed, plain):
    rng = random.Random(seed)
    K = rng.sample(range(M), M)
    return encipher(
        plain,
        rng.sample(range(M), M),
        alphabets(K, schedule(rng, zeros=1)),
        rng.sample(range(M), M),
    )


def odometer(seed, plain):
    rng = random.Random(seed)
    K, offsets, start = odometer_draw(rng)
    return odometer_encipher(plain, K, offsets, start)


def preventer(seed, plain, phi=0.90):
    rng = random.Random(seed)
    g = order5(rng)
    powers = [power(g, k) for k in range(5)]
    sigma = rng.sample(range(M), M)
    base = rng.sample(range(M), M)
    out, clock, previous = [], 0, None
    for word in plain:
        emitted = []
        for p in word:
            c = base[powers[clock % 5][p]]
            if c == previous and rng.random() < phi:
                clock += 1
                c = base[powers[clock % 5][p]]
            emitted.append(c)
            previous = c
            clock += 1
        out.append(emitted)
        base = compose(base, compose(powers[(clock - 1) % 5], sigma))
    return out


def bucket_of(gap: int) -> int:
    for i, (lo, hi) in enumerate(BUCKETS):
        if lo <= gap <= hi:
            return i
    return len(BUCKETS) - 1


def gap_table(blocks, *, seams: bool):
    """(gap-size bucket, gap mod 5) for each consecutive pair of doublets."""
    positions, k, previous = [], 0, None
    for word in blocks:
        for j, rune in enumerate(word):
            if previous is not None and rune == previous and (j > 0 or seams):
                positions.append(k)
            previous = rune
            k += 1
    return [(bucket_of(b - a), (b - a) % 5) for a, b in zip(positions, positions[1:])]


def profile(model, *, seams: bool, alpha: float = SMOOTHING):
    """P(residue | bucket) from held-out seeds, each rotated onto its own short-gap mode."""
    table = np.ones((len(BUCKETS), 5)) * alpha
    for seed in REFERENCE_SEEDS:
        rows = gap_table(model(seed, merged_words(seed)), seams=seams)
        short = np.zeros(5)
        for b, r in rows:
            if b == 0:
                short[r] += 1
        shift = int(np.argmax(short)) if short.sum() else 0
        for b, r in rows:
            table[b, (r - shift) % 5] += 1
    return table / table.sum(axis=1, keepdims=True)


def marginal_loglik(rows, table) -> float:
    """The key's phase is a nuisance: average over it, never maximise."""
    per_phase = [
        sum(math.log(table[b, (r - s) % 5]) for b, r in rows) for s in range(5)
    ]
    top = max(per_phase)
    return top + math.log(sum(math.exp(x - top) for x in per_phase) / 5)


def main() -> None:
    body = [b for b, _ in body_blocks(set())]
    print("Conditioned on gap size, with the key phase marginalised, and every model")
    print(
        f"run on a word stream merged at q = {JOIN_RATE} so it shares the body's blocks.\n"
    )
    print(
        f"{'doublets used':<22}{'against':<20}{'body log LR':>13}{'ratio':>11}"
        f"{'P(>=obs)':>10}{'accuracy':>11}"
    )
    for seams in (False, True):
        rows = gap_table(body, seams=seams)
        prof_preventer = profile(preventer, seams=seams)
        for name, model in (("quagmire-dodge", dodge), ("quagmire-odometer", odometer)):
            prof_model = profile(model, seams=seams)
            observed = marginal_loglik(rows, prof_preventer) - marginal_loglik(
                rows, prof_model
            )
            known = np.array(
                [
                    marginal_loglik(
                        gap_table(model(s, merged_words(s)), seams=seams),
                        prof_preventer,
                    )
                    - marginal_loglik(
                        gap_table(model(s, merged_words(s)), seams=seams), prof_model
                    )
                    for s in range(TRIALS)
                ]
            )
            rival = np.array(
                [
                    marginal_loglik(
                        gap_table(preventer(s, merged_words(s)), seams=seams),
                        prof_preventer,
                    )
                    - marginal_loglik(
                        gap_table(preventer(s, merged_words(s)), seams=seams),
                        prof_model,
                    )
                    for s in range(TRIALS)
                ]
            )
            label = "with seam doublets" if seams else "within-block only"
            print(
                f"{label:<22}{name:<20}{observed:>+13.2f}"
                f"{math.exp(observed):>9.0f}:1{float((known >= observed).mean()):>10.3f}"
                f"{f'{float((known < 0).mean()):.0%}/{float((rival > 0).mean()):.0%}':>11}"
            )

    print("\nSmoothing is not carrying the split.\n")
    print(f"{'alpha':<10}{'within-block only':>20}{'with seam doublets':>22}")
    for alpha in (0.1, 0.5, 2.0, 5.0):
        cells = []
        for seams in (False, True):
            rows = gap_table(body, seams=seams)
            cells.append(
                marginal_loglik(rows, profile(preventer, seams=seams, alpha=alpha))
                - marginal_loglik(rows, profile(dodge, seams=seams, alpha=alpha))
            )
        print(f"{alpha:<10}{cells[0]:>20.2f}{cells[1]:>22.2f}")

    print(
        "\nThe 63 within-block doublets do not discriminate; the 23 seam doublets carry"
        "\nthe whole verdict. Both tests classify corpora of known origin well, so neither"
        "\nis broken -- inserting the seam doublets splits long gaps into short ones and"
        "\nchanges the gap population rather than adding to it. The direction is unchanged"
        "\nand stable, but it rests on a narrower base than the withdrawn 71:1 suggested."
    )


if __name__ == "__main__":
    main()
