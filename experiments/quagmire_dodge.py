# ABOUTME: A word-delimited Quagmire whose letter schedule holds one zero offset, with
# ABOUTME: a doublet-dodge rule on top; predicts the doublet rate with no free parameter.
"""Michel's proposal: a word-delimited Quagmire with a doublet suppression rule on top.

A Quagmire letter schedule uses alphabets `A_k = K . (add S_k)`, so the relation
between adjacent positions is a pure SHIFT, `add(s_(k+1))`, in K coordinates. Put the
dodge rule of `doublet-dodge-walk.md` on top: when the emission would repeat, advance
the clock one step and re-emit.

The dodge re-emits with `A_(k+1)` in place of `A_k`, so it FAILS precisely when

    A_(k+1)(p) = A_k(p)   <=>   s_(k+1) = 0

which does not depend on the plaintext at all. It is a property of the schedule. So a
schedule holding exactly one ZERO offset gives

    P(doublet) = P(the next step is zero) x P(would-be doublet)
               = 1/5  x  (a shift diagonal, untuned, about 1/29)
               = 0.0069

against the corpus's 0.0063 — and `README.md` already records that the observed rate
"fits (1/5)x(1/29) with NO free parameters (z = -0.36)", a coincidence nothing in this
directory has explained. Here it is forced.

Two further consequences:

  * the survivors are shift coincidences rather than plaintext doubles, so they carry
    none of the end-heavy positional signature that disproved `stay-slot-hold.md`;
  * every keyword sweep in this project excluded this key by construction.
    `quagmire_runner.g_candidates` masks its candidate schedules with `nz = r != 0`,
    requiring all five offsets non-zero, while this model requires one to be zero. The
    3.1e8-key enumeration, the ungated 7.0e8 re-run and the priority sweep all searched
    only the zero-free half of the schedule space.

Run with no arguments for the self-test, `--fit` to score it on the held-out battery.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import (  # noqa: E402
    M,
    compare,
    compose,
    fingerprint,
    lp_words,
    prose_corpora,
)
from quagmire_runner import conj_shift  # noqa: E402

# The schedule's one zero offset FORCES the doublet rate and the alphabets are drawn at
# random, so d1w is not fitted. The word step is chosen against the seam, so that one
# is. Everything else is a prediction.
FITTED = {"seam"}


def schedule(rng, *, zeros: int) -> list[int]:
    """Five offsets summing to 0 mod 29, with exactly `zeros` of them zero.

    A zero offset makes two adjacent alphabets coincide, which is the condition under
    which a dodge fails. `quagmire_runner.g_candidates` forbids zeros, so every sweep
    in this project searched only the `zeros = 0` half.
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


def alphabets(K: list[int], offsets: list[int]) -> list[list[int]]:
    """A_k = K . (add S_k) . K^-1 for the running sums of the schedule."""
    out, total = [], 0
    for step in offsets:
        total = (total + step) % M
        out.append(conj_shift(K, total))
    return out


def encipher(plain, base0, alpha, sigma):
    """Emit; on a would-be repeat advance the clock and re-emit."""
    base = list(base0)
    out = []
    clock = 0
    previous = None
    for word in plain:
        cipher_word = []
        for p in word:
            c = base[alpha[clock % 5][p]]
            if c == previous:
                clock += 1
                c = base[alpha[clock % 5][p]]
            cipher_word.append(c)
            previous = c
            clock += 1
        out.append(cipher_word)
        base = compose(base, compose(alpha[(clock - 1) % 5], sigma))
    return out


def generator(alpha, sigma):
    def generate(plain, rng):
        return encipher(plain, rng.sample(range(M), M), alpha, sigma)

    return generate


def dodge_failures(plain, alpha, base0, sigma) -> tuple[int, int]:
    """(would-be doublets, survivors) — survivors should occur only at the zero step."""
    base = list(base0)
    tried = survived = 0
    clock = 0
    previous = None
    for word in plain:
        for p in word:
            c = base[alpha[clock % 5][p]]
            if c == previous:
                tried += 1
                clock += 1
                c = base[alpha[clock % 5][p]]
                if c == previous:
                    survived += 1
            previous = c
            clock += 1
        base = compose(base, compose(alpha[(clock - 1) % 5], sigma))
    return tried, survived


def self_test() -> None:
    rng = random.Random(3301)
    plain = prose_corpora(2928, 1)[0]
    lp = fingerprint(lp_words())
    K = rng.sample(range(M), M)
    offsets = schedule(rng, zeros=1)
    alpha = alphabets(K, offsets)
    sigma = conj_shift(rng.sample(range(M), M), rng.randrange(1, M))
    base0 = rng.sample(range(M), M)

    print(f"schedule {offsets} (sum {sum(offsets) % M} mod 29, one zero)")
    zero_at = offsets.index(0)
    # the dodge fails exactly when the NEXT step is zero, whatever the plaintext
    for k in range(5):
        same = alpha[k] == alpha[(k + 1) % 5]
        assert same == (offsets[(k + 1) % 5] == 0), "dodge-failure condition is wrong"
    print(
        f"adjacent alphabets coincide only at phase {(zero_at - 1) % 5}, as predicted"
    )

    cipher = encipher(plain, base0, alpha, sigma)
    got = fingerprint(cipher)
    tried, survived = dodge_failures(plain, alpha, base0, sigma)
    print(
        f"\nwould-be doublets {tried}, survivors {survived} "
        f"({survived / max(1, tried):.3f}, predicted 1/5 = 0.200)"
    )
    print(
        f"doublet rate  model {got['d1w']:.5f}   predicted (1/5)(1/29) "
        f"{1 / 5 / M:.5f}   corpus {lp['d1w']:.5f}"
    )
    assert abs(got["d1w"] - 1 / 5 / M) < 0.004, "doublet rate off the prediction"
    assert 0.12 < survived / max(1, tried) < 0.30, "survivor share should be about 1/5"

    # control: with NO zero offset the dodge always succeeds and doublets vanish
    rates = []
    for _ in range(8):
        clean_offsets = schedule(rng, zeros=0)
        clean_alpha = alphabets(K, clean_offsets)
        assert all(clean_alpha[k] != clean_alpha[(k + 1) % 5] for k in range(5)), (
            "a zero-free schedule must have no two adjacent alphabets equal"
        )
        rates.append(fingerprint(encipher(plain, base0, clean_alpha, sigma))["d1w"])
    print(
        f"control, schedules with NO zero offset: doublet rate "
        f"{np.mean(rates):.5f} over 8 keys (the dodge then never fails)"
    )
    assert max(rates) < 1e-6, "a zero-free schedule should emit no doublets at all"
    print("self-test passed")


def fit() -> None:
    rng = random.Random(3301)
    lp = fingerprint(lp_words())
    plain = prose_corpora(2928, 1)[0]
    best = None
    for _ in range(60):
        K = rng.sample(range(M), M)
        offsets = schedule(rng, zeros=1)
        alpha = alphabets(K, offsets)
        sigma = conj_shift(rng.sample(range(M), M), rng.randrange(1, M))
        got = fingerprint(encipher(plain, rng.sample(range(M), M), alpha, sigma))
        score = abs(got["seam"] - lp["seam"]) / 0.002
        if best is None or score < best[0]:
            best = (score, alpha, sigma, offsets)
    _s, alpha, sigma, offsets = best
    print(f"schedule {offsets}; alphabets random, word step chosen on the seam only\n")
    compare(generator(alpha, sigma), 60, FITTED, "word-delimited Quagmire with dodge")


if __name__ == "__main__":
    if "--fit" in sys.argv:
        fit()
    else:
        self_test()
