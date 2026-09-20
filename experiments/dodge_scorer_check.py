# ABOUTME: Checks whether the sweep's kernel can score a doublet-dodge key at all, by
# ABOUTME: planting one and seeing whether it separates from two thousand wrong sigmas.
"""Can the existing sweep find a dodge key if one is there?

`quagmire-dodge.md` step 1 says to sweep the zero-offset schedules with
`quagmire_ungated_sweep.py`, and `zero_offset_census.py` prices that at 30 core-hours
over 3301's own vocabulary. Both assume the sweep's scorer would recognise the key.

It would not. `walk_score_kernel.score_sigmas` undoes the letter step at position j with
the alphabet for clock `j`, because in every model it was written for the clock IS the
position. The dodge breaks that: a skip inserts a step, so from the first skip onward
the kernel applies the wrong alphabet to every remaining rune, and the base step
compounds it at the next word boundary. The skips land on 4-6% of positions, so a
200-word window holds about forty of them and the clock is wrong for essentially all of
it.

This is the sweep's own positive control run against dodge ciphertext. The same planted
key is scored twice:

  * enciphered WITHOUT the dodge, where it must separate -- the control the ungated
    sweep already passes, included so a failure here cannot be blamed on the harness;
  * enciphered WITH the dodge, where the question is whether anything survives.

A sweep whose scorer cannot see its own planted key returns negative whether or not the
key is in the space, so this decides whether step 1 is worth its 30 core-hours.

Run with no arguments.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies  # noqa: E402
from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from quagmire_dodge import alphabets, encipher  # noqa: E402
from quagmire_runner import (  # noqa: E402
    conj_shift,
    encrypt_walk,
    letter_steps,
    load_clean,
    load_register,
)
from quagmire_ungated_sweep import windows_of  # noqa: E402
from walk_score_kernel import score_sigmas  # noqa: E402

M = 29
WRONG_SIGMAS = 2000


def keyed(word: str) -> list[int]:
    """A keyword-mixed alphabet, as the sweep's own positive control builds one."""
    seen: list[int] = []
    for r in [IDX_ENG[t] for t in to_runeglish(word)] + list(range(M)):
        if r not in seen:
            seen.append(r)
    return seen


def separation(letter_perms, cipher, sigma, rng) -> tuple[float, float]:
    """(true sigma's score, best of `WRONG_SIGMAS` wrong ones) under the sweep's kernel."""
    sigmas = np.array(
        [sigma] + [rng.sample(range(M), M) for _ in range(WRONG_SIGMAS)], dtype=np.int8
    )
    scores = score_sigmas(letter_perms, sigmas, windows_of(cipher), log_frequencies())
    return float(scores[0]), float(scores[1:].max())


def main() -> None:
    rng = random.Random(3301)
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    pools, _table, _floor = load_register(PROSE_CACHE)
    plain = [rng.choice(pools[L])[:L] for L in lens]

    # one zero offset, which is what the dodge model needs and every sweep excluded
    K, sched = keyed("DIUINITY"), [3, 7, 0, 11, (0 - 3 - 7 - 11) % M]
    sigma = conj_shift(keyed("PILGRIM"), 8)
    base0 = rng.sample(range(M), M)
    perms = letter_steps(K, sched)

    plainly = encrypt_walk(plain, base0, perms, sigma)
    dodged = encipher(plain, base0, alphabets(K, sched), sigma)
    doublets = sum(
        w[j] == w[j - 1] for w in dodged for j in range(1, len(w))
    ) / sum(max(0, len(w) - 1) for w in dodged)
    print(f"schedule {sched}, one zero offset; dodge doublet rate {doublets:.5f}")
    assert len({tuple(w) for w in dodged}) > 2000, "planted key is degenerate"

    print(f"\n{'ciphertext':<28}{'planted key':>13}{'best of 2000 wrong':>21}{'gap':>9}")
    verdicts = []
    for label, cipher in (
        ("no dodge (the sweep's own)", plainly),
        ("with the dodge", dodged),
    ):
        good, bad = separation(perms, cipher, sigma, random.Random(4242))
        print(f"{label:<28}{good:>13.3f}{bad:>21.3f}{good - bad:>9.3f}")
        verdicts.append(good - bad)

    assert verdicts[0] > 0.2, (
        "the harness is broken: the planted key must separate without the dodge"
    )
    print(
        "\nthe kernel undoes the letter step with the alphabet for clock = position, so"
        "\nevery rune after the first skip is decoded through the wrong alphabet."
    )
    if verdicts[1] > 0.2:
        print("the dodge key separates anyway: the sweep could be run as planned")
    else:
        print(
            "the dodge key does NOT separate, so a zero-offset sweep with this scorer"
            "\nwould return negative whether or not the key is in the space."
        )
    assert verdicts[1] < verdicts[0], (
        "the dodge cannot make the key EASIER to find than the model it perturbs"
    )


if __name__ == "__main__":
    main()
