# ABOUTME: A length-clocked walk whose letter clock skips a step at a marked plaintext
# ABOUTME: rune, in the style of 3301's own solved interrupter pages.
"""The walk, with 3301's own interrupter.

Two facts point the same way. The walk's only falsifiable cell over-predicts: it puts
the within-word distance-5 rate at 0.056-0.059 against the corpus's 0.0492
(`length-clocked-walk.md`). And phi5, the fraction of the distance-5 echo that leaks,
has sat at 0.64-0.85 for a year -- "consistent with full leak but below it"
(`d5-partial-alphabet-leak.md`). Both say something occasionally breaks the period-5
alignment.

3301 already does exactly that. The solved AN END page is `P = C - (p_n - 1) mod 29`
with keystream interrupts at a marked rune: the key skips a step whenever the plaintext
letter is F. `missed_tests.py` closed the loophole of a PERIODIC key hidden by such
interrupts, but the walk has never been given one.

    c_j = base_w( g^(k_j) (p_j) ),   k_(j+1) = k_j + 1 + [p_j in S]

with S a small set of plaintext runes. The letter clock still advances once per rune
and the alphabet still has period 5, but an interrupt costs an extra step, so two
positions five apart share an alphabet only when no interrupt falls between them:

and it is decodable the way 3301's own page is: the decoder recovers p_j and only then
knows whether to skip, so no ambiguity arises.

**Result (2026-09-20): the idea is sound and the effect is far too small.** The first
version of this file predicted phi5 = (1-s)^5, reasoning that an interrupt breaks the
alignment. That is wrong. With n interrupts between a pair the relation is g^n, and
g^5 = id, so the rate CYCLES rather than decaying -- n = 5 returns to the identity and
the full plaintext rate. Measured, d5 falls only about 5% at an interrupt rate of 0.17,
where the corpus needs roughly 30%. The mechanism cannot deliver it.

Run with no arguments for the self-test (round-trip decryption, and phi5 matching
(1-s)^5), `--fit` to tune a key and score it against the corpus.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies  # noqa: E402
from fingerprint_battery import (  # noqa: E402
    M,
    compare,
    compose,
    distance_tables,
    fingerprint,
    fit_walk_key,
    lp_words,
    ppow,
    prose_corpora,
)

# g is fitted to the within-word distances and sigma to the seam, as for the walk; the
# interrupter set is fitted to the distance-5 rate, which the plain walk overshoots
FITTED = {"d1w", "d2w", "d3w", "d4w", "d6w", "seam", "d5w"}


def interrupt_rate(plain, marked: frozenset[int]) -> float:
    total = sum(len(w) for w in plain)
    return sum(1 for w in plain for p in w if p in marked) / total


def encipher(plain, base0, g, sigma, marked: frozenset[int]):
    """The walk with an extra clock step after every marked plaintext rune."""
    gp = [ppow(g, k) for k in range(5)]
    base = list(base0)
    out = []
    for word in plain:
        k = 0
        cipher_word = []
        for p in word:
            cipher_word.append(base[gp[k % 5][p]])
            k += 2 if p in marked else 1
        out.append(cipher_word)
        base = compose(base, compose(gp[(k - 1) % 5], sigma))
    return out


def decipher(cipher, base0, g, sigma, marked: frozenset[int]):
    """Inverse. The decoder recovers p before deciding whether to skip, as 3301's does."""
    gp = [ppow(g, k) for k in range(5)]
    inv_g = [[q.index(x) for x in range(M)] for q in gp]
    base = list(base0)
    out = []
    for word in cipher:
        binv = [base.index(x) for x in range(M)]
        k = 0
        plain_word = []
        for c in word:
            p = inv_g[k % 5][binv[c]]
            plain_word.append(p)
            k += 2 if p in marked else 1
        out.append(plain_word)
        base = compose(base, compose(gp[(k - 1) % 5], sigma))
    return out


def generator(g, sigma, marked):
    def generate(plain, rng):
        base0 = rng.sample(range(M), M)
        return encipher(plain, base0, g, sigma, marked)

    return generate


def choose_marked(target_phi5: float, rng) -> frozenset[int]:
    """A rune set whose plaintext share s gives (1 - s)^5 = target_phi5."""
    want = 1.0 - target_phi5**0.2
    freq = np.exp(log_frequencies())
    order = sorted(range(M), key=lambda r: -freq[r])
    marked: list[int] = []
    total = 0.0
    for r in reversed(
        order
    ):  # add rare runes first, so the set stays small and plausible
        if total + freq[r] > want * 1.15:
            continue
        marked.append(r)
        total += freq[r]
        if total >= want * 0.85:
            break
    return frozenset(marked)


def within_rate(words, d: int) -> float:
    hits = total = 0
    for w in words:
        for j in range(len(w) - d):
            total += 1
            hits += w[j] == w[j + d]
    return hits / total if total else float("nan")


def self_test() -> None:
    rng = random.Random(3301)
    plain = prose_corpora(2928, 1)[0]
    lp = fingerprint(lp_words())
    tabs = distance_tables(draws=12)
    g, sigma, _, _ = fit_walk_key(tabs, lp, rng)

    marked = choose_marked(0.70, rng)
    base0 = rng.sample(range(M), M)
    cipher = encipher(plain, base0, g, sigma, marked)
    assert decipher(cipher, base0, g, sigma, marked) == plain, "round trip failed"
    print(f"round-trip decryption holds ({len(marked)} marked runes)")

    # what the interrupter actually does to d5. With n interrupts between a pair the
    # relation is g^n, and g^5 = id, so the rate CYCLES rather than decaying: it cannot
    # be driven to chance. The first version of this file predicted phi5 = (1-s)^5,
    # which is wrong for exactly that reason.
    print(f"\n{'marked':>7}{'rate s':>9}{'d5':>9}{'drop':>8}")
    chance = 1.0 / M
    base_d5 = within_rate(encipher(plain, base0, g, sigma, frozenset()), 5)
    rates = []
    for target in (1.0, 0.85, 0.70, 0.55, 0.35):
        marked = choose_marked(target, rng) if target < 1.0 else frozenset()
        s_rate = interrupt_rate(plain, marked)
        got = within_rate(encipher(plain, base0, g, sigma, marked), 5)
        rates.append(got)
        print(
            f"{len(marked):>7}{s_rate:>9.4f}{got:>9.4f}{(base_d5 - got) / base_d5:>8.1%}"
        )
    assert rates[0] == base_d5, "no interrupts must reproduce the plain walk"
    assert min(rates) < base_d5, "interrupts should lower d5"
    assert min(rates) > chance + 0.02, (
        "d5 cannot be driven near chance: g^5 = id makes the relation cycle"
    )
    print(f"\nthe corpus reads {lp['d5w']:.4f}, chance {chance:.4f}")
    print("so the interrupter moves d5 the right way but only a few percent")
    print("self-test passed")


def fit() -> None:
    rng = random.Random(3301)
    lp = fingerprint(lp_words())
    tabs = distance_tables(draws=20)
    g, sigma, _, _ = fit_walk_key(tabs, lp, rng)
    plain = prose_corpora(2928, 1)[0]
    chance, plain_d5 = 1.0 / M, within_rate(plain, 5)
    # the interrupt rate the corpus's own d5 implies
    phi = (lp["d5w"] - chance) / (plain_d5 - chance)
    s = 1 - phi**0.2
    marked = choose_marked(phi, rng)
    print(
        f"corpus d5 {lp['d5w']:.4f}, plaintext {plain_d5:.4f} -> phi5 {phi:.3f}, "
        f"interrupt rate {s:.4f}"
    )
    print(
        f"marked set: {len(marked)} runes, plaintext share "
        f"{interrupt_rate(plain, marked):.4f}\n"
    )
    compare(generator(g, sigma, marked), 60, FITTED, "interrupted walk")


if __name__ == "__main__":
    if "--fit" in sys.argv:
        fit()
    else:
        self_test()
