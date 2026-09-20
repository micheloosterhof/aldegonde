# ABOUTME: Michel's stripped model -- a plain Quagmire restarting at a fixed key offset
# ABOUTME: each word, with a doublet preventer and no general permutation anywhere.
"""Can the cipher be a plain Quagmire with a per-word restart?

Michel's proposal (September 2026): drop `g` and σ. No general permutation. One keyed
alphabet, a five-step shift schedule, the key restarting at a fixed offset in every
word, and the doublet preventer on top. In K coordinates everything is then a shift:

    c_j = K[ (pos_K(p_j) + u_w + S[(r + j) mod 5]) mod 29 ]

with `r` the restart offset and the doublet rule advancing the phase on a repeat.

**Result (2026-09-21): the restart is ruled out; the rest of the proposal is not.**

The doublet preventer works in every version -- d1w lands whatever else is changed. The
restart is what fails, and it fails structurally.

Inside a word the preventer fails at one phase in five, which is where the corpus's
doublets come from, so the within-word rate is (1/5) x a diagonal. A word boundary is
the same event at whatever phase the clock is on. With a FIXED restart every boundary
sits at the same phase `r`, so the preventer there fails either at every boundary or at
none, according to whether offsets[(r+1) % 5] is the zero one. Measured over 16 draws
the seam-to-doublet ratio is 0.0 ten times and 3.4 to 25.5 six times. The corpus reads
1.25, which is in neither branch.

The escape would be a preventer that stops at the word break, leaving the seam
unsuppressed. That gives a seam of 0.0355 against chance 0.0345 and the corpus's
0.0079, so the corpus's boundary IS suppressed and the preventer does run across it.

A ratio near 1 needs the boundaries spread over all five phases, which is a clock that
runs on through the word break -- the opposite of a restart.

Two further measurements, on the parts of the proposal that survive.

**The IoC does not object to dropping the general permutation.** With nothing changing
between words the text uses five alphabets and reads nIoC 1.28 against the corpus's
0.9999. One per-word shift covers all 29 residues in K coordinates and washes it out
completely, 0.9999. So the per-word step is not optional, but it need not be a general
permutation.

**Identical ciphertext words set the size of that step.** The corpus holds 17 pairs of
equal words. A per-word shift offers 29 states and gives about 490; the budget measured
against a pool of N states lands 17 between N = 4,000 and N = 20,000.

A caution about reaching that budget with shifts: a per-word state that is a LINEAR
function of the word index has 29 values however many dials it has, since two dials
advancing at fixed rates stay on a line. Two dials stepping by 1 each give the same 480
as one dial. Drawn independently they give 30, close to the corpus's 17, so two
decorrelated dials -- an odometer with a carry, or an advance that depends on the word
-- would meet the budget without any general permutation.

The register is matched to the LP's word lengths throughout. Word length drives both
cells directly -- `identical` only counts words of MIN_WORD runes or more, and prose has
longer words than the LP -- so an unmatched corpus understates the collisions.

Run with no arguments.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ea_direction_test import PROSE_CACHE  # noqa: E402
from fingerprint_battery import M, fingerprint, lp_words  # noqa: E402
from quagmire_runner import load_clean, load_register  # noqa: E402

DRAWS = 8
POOLS = (1, 5, 29, 145, 841, 4_000, 20_000)


def schedule(rng, *, zeros: int = 1) -> list[int]:
    """Five offsets summing to 0 mod 29 with exactly `zeros` of them zero.

    A zero offset makes two adjacent phases share an alphabet, which is the only way
    the doublet preventer can fail and so the only way the corpus's doublets arise.
    """
    while True:
        free = [rng.randrange(1, M) for _ in range(4 - zeros)]
        last = (-sum(free)) % M
        if last == 0:
            continue
        offsets = [*free, last, *([0] * zeros)]
        rng.shuffle(offsets)
        if sum(offsets) % M == 0 and offsets.count(0) == zeros:
            return offsets


def running(offsets: list[int]) -> list[int]:
    out, total = [], 0
    for step in offsets:
        total = (total + step) % M
        out.append(total)
    return out


def encipher(
    plain,
    K,
    offsets,
    restart,
    word_step,
    rng=None,
    pool=None,
    outer=None,
    *,
    within_word_only=False,
):
    """Quagmire with a per-word key restart and a doublet preventer.

    `word_step` is the shift added inside K at each word: 0 leaves five alphabets for
    the entire text, a non-zero constant cycles through all 29, and `None` redraws it
    at random per word. `outer` adds a second shift OUTSIDE K, stepping by that amount
    per word; the two do not commute, so together they offer 29 x 29 states and the
    restart makes it 4,205 -- all shifts, no general permutation. `pool` replaces the
    whole per-word step with a permutation drawn from that list, which is how the state
    budget is measured. `within_word_only` stops the preventer at the word break, to
    show what the seam looks like when the boundary is left unsuppressed.
    """
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    out = []
    previous = None
    u = v = 0
    base = None
    for word in plain:
        if pool is not None:
            base = pool[rng.randrange(len(pool))]
        phase = restart
        if within_word_only:
            previous = None
        cipher_word = []
        for p in word:
            c = (K[(pos[p] + u + S[phase % 5]) % M] + v) % M
            if base is not None:
                c = base[c]
            if c == previous:
                phase += 1
                c = (K[(pos[p] + u + S[phase % 5]) % M] + v) % M
                if base is not None:
                    c = base[c]
            cipher_word.append(c)
            previous = c
            phase += 1
        out.append(cipher_word)
        if pool is None:
            u = rng.randrange(M) if word_step is None else (u + word_step) % M
            if outer == "random":
                v = rng.randrange(M)
            elif outer is not None:
                v = (v + outer) % M
    return out


def matched_register(rng, lens, pools):
    """Prose carrying the LP's exact word-length sequence."""
    return [rng.choice(pools[L])[:L] for L in lens]


def sample(rng, lens, pools, *, word_step=0, pool=None, outer=None):
    """Mean fingerprint cells over `DRAWS` keys, each on its own register draw."""
    rows = []
    for _ in range(DRAWS):
        K = rng.sample(range(M), M)
        plain = matched_register(rng, lens, pools)
        got = fingerprint(
            encipher(
                plain,
                K,
                schedule(rng),
                rng.randrange(5),
                word_step,
                rng=rng,
                pool=pool,
                outer=outer,
            )
        )
        rows.append((got["ioc"], got["identical"], got["d1w"], got["d5w"], got["seam"]))
    return np.array(rows).mean(axis=0)


def main() -> None:
    rng = random.Random(3301)
    lp = fingerprint(lp_words())
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    pools, _table, _floor = load_register(PROSE_CACHE)

    header = f"{'model':<36}{'nIoC':>9}{'identical':>11}{'d1w':>9}{'d5w':>9}{'seam':>9}"
    print("register matched to the LP's word lengths\n")
    print(header)
    print(
        f"{'the corpus':<36}{lp['ioc']:>9.4f}{lp['identical']:>11.0f}"
        f"{lp['d1w']:>9.4f}{lp['d5w']:>9.4f}{lp['seam']:>9.4f}"
    )
    for label, step, outer in (
        ("restart only, 5 alphabets", 0, None),
        ("+ shift inside K, 29 states", 1, None),
        ("+ shift inside K, random", None, None),
        ("+ a second shift outside K, 4,205", 1, 1),
        ("the same, both random", None, "random"),
    ):
        ioc, ident, d1, d5, seam = sample(rng, lens, pools, word_step=step, outer=outer)
        print(f"{label:<36}{ioc:>9.4f}{ident:>11.0f}{d1:>9.4f}{d5:>9.4f}{seam:>9.4f}")

    # How many per-word states does the corpus's identical-word count demand? Give the
    # step a pool of N permutations and read off where it lands 17.
    print(f"\n{'per-word states':<36}{'nIoC':>9}{'identical':>11}{'d1w':>9}{'d5w':>9}")
    for n in POOLS:
        pool = [rng.sample(range(M), M) for _ in range(n)]
        ioc, ident, d1, d5, _seam = sample(rng, lens, pools, pool=pool)
        print(f"{n:<36,}{ioc:>9.4f}{ident:>11.0f}{d1:>9.4f}{d5:>9.4f}")
    print(
        f"\nthe corpus reads {lp['identical']:.0f}. A per-word SHIFT offers 29 states, "
        "and a shift\nwith the restart moved as well offers 29 x 5 = 145."
    )
    seam_test(rng, lens, pools, lp)


def seam_test(rng, lens, pools, lp) -> None:
    """The restart's own signature: the seam is 0 or 5x the doublet rate, never 1x.

    Inside a word the doublet preventer fails at one phase in five, which is where the
    corpus's doublets come from. At a word boundary a FIXED restart puts every boundary
    at the same phase `r`, so the preventer there fails either always or never according
    to whether offsets[(r+1) % 5] is the zero one. The seam rate is therefore bimodal.

    A clock that runs on through the boundary instead spreads the boundaries over all
    five phases, so one in five can fail and the seam matches the within-word rate.
    """
    print("\nseam / d1w per draw, fixed restart (the corpus reads ", end="")
    print(f"{lp['seam'] / lp['d1w']:.2f})")
    ratios, zeroed = [], []
    for _ in range(16):
        K = rng.sample(range(M), M)
        offsets = schedule(rng)
        restart = rng.randrange(5)
        plain = matched_register(rng, lens, pools)
        got = fingerprint(
            encipher(plain, K, offsets, restart, None, rng=rng, outer="random")
        )
        ratios.append(got["seam"] / got["d1w"] if got["d1w"] else float("nan"))
        zeroed.append(offsets[(restart + 1) % 5] == 0)
    hot = [r for r, z in zip(ratios, zeroed) if z]
    cold = [r for r, z in zip(ratios, zeroed) if not z]
    print(f"  boundary phase sits on the zero offset ({len(hot)} draws): ", end="")
    print(" ".join(f"{r:.1f}" for r in hot) or "none")
    print(f"  it does not ({len(cold)} draws): ", end="")
    print(" ".join(f"{r:.1f}" for r in cold) or "none")
    assert all(r < 0.35 for r in cold), (
        "without the zero offset at the boundary the preventer must never fail there"
    )
    assert all(r > 2.0 for r in hot), (
        "with it, every boundary is exposed, so the seam must run about 5x the "
        "within-word rate"
    )
    # The escape would be a preventer that does not act across the boundary at all.
    # Then the seam is an unsuppressed shift diagonal, which the corpus is nowhere near.
    loose = []
    for _ in range(6):
        K = rng.sample(range(M), M)
        plain = matched_register(rng, lens, pools)
        loose.append(
            fingerprint(
                encipher(
                    plain,
                    K,
                    schedule(rng),
                    rng.randrange(5),
                    None,
                    rng=rng,
                    outer="random",
                    within_word_only=True,
                )
            )["seam"]
        )
    print(
        f"\npreventer acting inside words only: seam {np.mean(loose):.4f}, "
        f"against chance {1 / M:.4f} and the corpus's {lp['seam']:.4f}"
    )
    assert np.mean(loose) > 3 * lp["seam"], (
        "a preventer that skips the boundary leaves the seam unsuppressed, which the "
        "corpus is not"
    )
    print(
        "\nSo the boundary IS suppressed, the preventer does run across it, and with a"
        "\nFIXED restart every boundary sits at one phase -- exposed or safe together."
        "\nThe corpus's ratio of 1.25 needs the boundaries spread over all five phases,"
        "\nwhich is a clock that runs on through the word break rather than restarting."
    )


if __name__ == "__main__":
    main()
