# ABOUTME: Asks whether the space's clock skip leaves any trace in the ciphertext
# ABOUTME: statistics at all, by enciphering one plaintext with one key at every skip.
"""Can the space's clock skip be recovered from the ciphertext at all?

`space-eats-clock-steps.md` closes with a plan: `k` shows up only through which clock
phase each word starts on, so it needs a likelihood comparison inside a fitted model
rather than a coincidence count. That plan assumes `k` is identifiable. This checks the
assumption first, because if it is not, no amount of fitting will recover it.

The check is a paired one. Take a key, take a plaintext, and encipher it five times with
`k = 0, 1, 2, 3, 4`. Everything else is held fixed, so any difference in the fingerprint
is caused by `k` alone. Repeat over many keys and ask, cell by cell, whether the value
at `k` differs from the value at `k = 0` by more than the paired noise.

Only `k mod 5` can matter under a period-5 schedule, so these five cover every skip in
both directions -- `k = 4` is `k = -1`, the backward space that repeats the previous
word's last alphabet.

**What each outcome means.** If some cell separates the five, `k` is identifiable and a
fit can go looking for it in the corpus. If none does, `k` is invisible to every
statistic in the battery, the corpus cannot distinguish a space that eats steps from one
that does not, and the question is closed by unknowability rather than by an answer.

Run with no arguments; `--drift-free` to use the preventer that does not move the clock.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_phase_test import encipher  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from fingerprint_battery import M, fingerprint, lp_words  # noqa: E402
from pure_quagmire_restart import matched_register, schedule  # noqa: E402
from quagmire_runner import load_clean, load_register  # noqa: E402

KEYS = 30
SKIPS = (0, 1, 2, 3, 4)


def main() -> None:
    variant = "re-emit" if "--drift-free" in sys.argv else "advance"
    rng = random.Random(3301)
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    pools, _t, _f = load_register(PROSE_CACHE)
    cells = list(fingerprint(lp_words()))

    print(f"preventer: {variant}; {KEYS} keys, each enciphered at every skip")
    print("the plaintext and the key are held fixed across the five, so any")
    print("difference in a cell is caused by the space skip alone\n")

    # rows[key][skip][cell]
    rows = np.zeros((KEYS, len(SKIPS), len(cells)))
    for i in range(KEYS):
        K = rng.sample(range(M), M)
        offsets = schedule(rng)
        start = (rng.randrange(M), rng.randrange(M))
        plain = matched_register(rng, lens, pools)
        for s, k in enumerate(SKIPS):
            got = fingerprint(encipher(plain, K, offsets, start, k, variant))
            rows[i, s] = [got[c] for c in cells]

    print(
        f"{'cell':<16}{'mean at k=0':>13}{'largest shift':>15}{'paired z':>10}   verdict"
    )
    separates = []
    for c, name in enumerate(cells):
        base = rows[:, 0, c]
        worst_z, worst_shift = 0.0, 0.0
        for s in range(1, len(SKIPS)):
            diff = rows[:, s, c] - base
            sd = diff.std(ddof=1)
            z = diff.mean() / (sd / np.sqrt(KEYS)) if sd > 1e-12 else 0.0
            if abs(z) > abs(worst_z):
                worst_z, worst_shift = z, diff.mean()
        flag = abs(worst_z) > 3  # Bonferroni-ish over 19 cells x 4 comparisons
        if flag:
            separates.append(name)
        print(
            f"{name:<16}{base.mean():>13.4f}{worst_shift:>15.4f}{worst_z:>10.2f}"
            f"   {'SEPARATES' if flag else 'blind to k'}"
        )
    print(
        f"\ncells that can see the skip: {', '.join(separates) if separates else 'none'}"
    )
    if not separates:
        print(
            "no statistic in the battery distinguishes the five skips, so the corpus"
            "\ncannot either, and fitting k would be fitting noise."
        )
        return
    against_corpus(rows, cells, separates)


def against_corpus(rows, cells, separates) -> None:
    """What the corpus says about each skip, using only the cells that can see it.

    Separating the skips in a PAIRED test over many keys is a weaker claim than
    separating them on one corpus. The paired test cancels the key-to-key noise; the LP
    is a single sample and carries its own.
    """
    lp = fingerprint(lp_words())
    print("\nwhat the corpus says, cell by cell and skip by skip:")
    for name in separates:
        c = cells.index(name)
        print(f"\n   {name}: the LP reads {lp[name]:.4f}")
        for s, k in enumerate(SKIPS):
            values = rows[:, s, c]
            mean, sd = values.mean(), values.std(ddof=1)
            if name == "triplets":
                # a count with no spread across keys is Poisson, not Gaussian
                note = (
                    f"P(see {lp[name]:.0f} | mean {mean:.2f}) = "
                    f"{np.exp(-mean) if lp[name] == 0 else float('nan'):.3f}"
                )
            else:
                note = f"z {(lp[name] - mean) / sd:+.2f} on the key spread"
            label = " <- the backward space" if k == 4 else ""
            print(
                f"      k = {k}{'  (= -1)' if k == 4 else '       '} "
                f"model {mean:>8.4f} +- {sd:<8.4f} {note}{label}"
            )
    print(
        "\nthe separation is real but small against one corpus: the shifts between"
        "\nadjacent skips are about the size of the LP's own error on these cells."
    )


if __name__ == "__main__":
    main()
