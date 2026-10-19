# ABOUTME: Four autokey variants that combine lag-1 feedback with period-5 structure,
# ABOUTME: scored on the within-word distance profile against the LP and the walk.
"""Can lag-1 feedback live anywhere in a period-5 cipher without erasing d4-d6?

`dual-autokey-lag1-lag5.md` closes ADDITIVE lag-1 feedback: c_j - c_{j-d} is a sum of
d plaintext terms, so every distance past 1 sits at chance. That proof uses addition.
This script tries the places it does not reach:

  A  general lag-1 ciphertext feedback, c_j = h_{c_{j-1}}( a(p_j) + b(tap) ), with an
     independent random permutation h_c for every previous rune -- no group law. The
     lag-5 tap restarts in every word and reads either plaintext or ciphertext.
  B  the walk, c_j = base_w( g^(k_j)(p_j) ), whose clock is a plaintext autokey:
     k_(j+1) = k_j + 2 after a rune in a skip set S, else k_j + 1.
  C  the same, with the clock driven by the ciphertext rune instead.
  D  the walk enciphering a(p_j) + b(p_(j-1)): a lag-1 plaintext autokey inside the
     period-5 alphabet (the first rune of a word has no tap).

B with S empty is the walk itself, and is the control: it must land on the fitted
profile, or the harness is broken.

**Result (2026-10-19).** Feedback that enters the rune VALUE erases d5 in both forms
tried. Feedback that only moves the CLOCK keeps it, and is then the walk with a
perturbed clock. 20 prose corpora, mean (sd):

    model                     skip q   d1w     d4w     d5w     d6w
    LP                                 0.0063  0.0410  0.0492  0.0245
    A lag-1 h_c, plain tap             0.0352  0.0343  0.0325  0.0348
    A lag-1 h_c, cipher tap            0.0347  0.0348  0.0342  0.0336
    B walk control, S empty   0.000    0.0070  0.0381  0.0609  0.0241
    B plain-clocked           0.118    0.0079  0.0424  0.0483  0.0285
    C cipher-clocked          0.104    0.0098  0.0418  0.0503  0.0258
    C cipher-clocked          0.206    0.0122  0.0435  0.0432  0.0309
    D walk of a(p)+b(p_-1)             0.0687  0.0370  0.0309  0.0353

A: every distance 1-6 sits at chance (0.033-0.036) with random rows h_c. The lag
theorem's conclusion holds without a group law: c_j depends on the whole prefix of the
word. The h_c were not tuned, so A's d1 is not a test of the doublet rate.

D: d5 at chance (0.0309), and d1 rises to 0.0687, double chance. A plaintext tap
inside the alphabet makes each cipher rune a function of two plaintext runes, and the
lag-5 equality then needs a two-rune match.

B and C: d5 falls as the skip rate q rises, and the period-5 cells survive. At q near
0.1 no cell departs from the control by more than about 1.5 sd. These are the walk's
clock perturbation, already bounded at q 95% [0.003, 0.262] by
`hypotheses/d5-bounds-the-clock-perturbation.md`. A ciphertext-driven clock at
q = 0.206 lifts d1 to 0.0122, 4 sd above the LP, because a skip puts g^2 between
adjacent runes and g was fitted without skips. A g refitted with skips might recover
it; that was not tried.

Run with no arguments for the self-test (round-trip decryption of every variant and
the control), `--run` for the profile table.
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
    distance_tables,
    fingerprint,
    fit_walk_key,
    lp_words,
    prose_corpora,
)

from aldegonde.maths import permutation  # noqa: E402

CELLS = ("d1w", "d2w", "d3w", "d4w", "d5w", "d6w", "seam", "d5x")


def powers(g):
    return [permutation.power(g, k) for k in range(5)]


# --- A: general lag-1 ciphertext feedback ------------------------------------------


def encipher_a(plain, h, a, b, *, tap_cipher: bool):
    """c_j = h[c_(j-1)][ a(p_j) + b(tap) ]; the tap is position j-5 of the same word."""
    out, previous = [], 0
    for word in plain:
        cw = []
        for j, p in enumerate(word):
            tap = 0
            if j >= 5:
                tap = cw[j - 5] if tap_cipher else word[j - 5]
            previous = h[previous][(a[p] + b[tap]) % M]
            cw.append(previous)
        out.append(cw)
    return out


def decipher_a(cipher, h, a, b, *, tap_cipher: bool):
    h_inv = [permutation.inverse(row) for row in h]
    a_inv = permutation.inverse(a)
    out, previous = [], 0
    for cw in cipher:
        pw = []
        for j, c in enumerate(cw):
            tap = 0
            if j >= 5:
                tap = cw[j - 5] if tap_cipher else pw[j - 5]
            pw.append(a_inv[(h_inv[previous][c] - b[tap]) % M])
            previous = c
        out.append(pw)
    return out


# --- B, C: the walk with an autokeyed clock ----------------------------------------


def encipher_clocked(plain, base0, g, sigma, skip, *, by_cipher: bool):
    """c_j = base_w(g^(k_j)(p_j)); the clock steps 2 after a rune in `skip`, else 1.

    The clock restarts at each word, as in the walk, and the base steps by
    g^(k_last) o sigma, k_last being the clock at the word's last rune.
    """
    gp = powers(g)
    base, out = list(base0), []
    for word in plain:
        cw, k = [], 0
        for j, p in enumerate(word):
            if j:
                driver = cw[-1] if by_cipher else word[j - 1]
                k += 2 if driver in skip else 1
            cw.append(base[gp[k % 5][p]])
        out.append(cw)
        base = permutation.compose(base, permutation.compose(gp[k % 5], sigma))
    return out


def decipher_clocked(cipher, base0, g, sigma, skip, *, by_cipher: bool):
    gp = powers(g)
    gi = [permutation.inverse(x) for x in gp]
    base, out = list(base0), []
    for cw in cipher:
        b_inv = permutation.inverse(base)
        pw, k = [], 0
        for j, c in enumerate(cw):
            if j:
                driver = cw[j - 1] if by_cipher else pw[-1]
                k += 2 if driver in skip else 1
            pw.append(gi[k % 5][b_inv[c]])
        out.append(pw)
        base = permutation.compose(base, permutation.compose(gp[k % 5], sigma))
    return out


# --- D: lag-1 plaintext autokey inside the walk ------------------------------------


def encipher_d(plain, base0, g, sigma, a, b):
    gp = powers(g)
    base, out = list(base0), []
    for word in plain:
        cw = []
        for j, p in enumerate(word):
            x = (a[p] + (b[word[j - 1]] if j else 0)) % M
            cw.append(base[gp[j % 5][x]])
        out.append(cw)
        base = permutation.compose(
            base, permutation.compose(gp[(len(word) - 1) % 5], sigma)
        )
    return out


def decipher_d(cipher, base0, g, sigma, a, b):
    gp = powers(g)
    gi = [permutation.inverse(x) for x in gp]
    a_inv = permutation.inverse(a)
    base, out = list(base0), []
    for cw in cipher:
        b_inv = permutation.inverse(base)
        pw = []
        for j, c in enumerate(cw):
            x = gi[j % 5][b_inv[c]]
            pw.append(a_inv[(x - (b[pw[-1]] if j else 0)) % M])
        out.append(pw)
        base = permutation.compose(
            base, permutation.compose(gp[(len(cw) - 1) % 5], sigma)
        )
    return out


# --- harness -----------------------------------------------------------------------


def walk_key(seed: int = 3301):
    """g and sigma fitted to the LP's d1-d4, d6 and seam, as the walk is."""
    rng = random.Random(seed)
    lp = fingerprint(lp_words())
    g, sigma, _, _ = fit_walk_key(distance_tables(), lp, rng)
    return g, sigma


def variants(g, sigma, rng):
    """name -> (generator(plain, rng), clock skip set or None, skip driven by cipher).

    Keys are fixed per variant; only the base is drawn per corpus.
    """

    def perm():
        return permutation.random_permutation(M, rng)

    out = {}
    h = [perm() for _ in range(M)]
    a, b = perm(), perm()
    for tap_cipher in (False, True):
        name = f"A lag-1 h_c, lag-5 {'cipher' if tap_cipher else 'plain'} tap"
        out[name] = (
            lambda plain, r, t=tap_cipher: encipher_a(plain, h, a, b, tap_cipher=t),
            None,
            False,
        )
    for by_cipher, letter in ((False, "B"), (True, "C")):
        for size in (0, 1, 3, 6) if not by_cipher else (1, 3, 6):
            skip = frozenset(rng.sample(range(M), size))
            name = f"{letter} {'cipher' if by_cipher else 'plain'}-clocked, |S|={size}"
            out[name] = (
                lambda plain, r, s=skip, c=by_cipher: encipher_clocked(
                    plain,
                    permutation.random_permutation(M, r),
                    g,
                    sigma,
                    s,
                    by_cipher=c,
                ),
                skip,
                by_cipher,
            )
    out["D walk of a(p_j)+b(p_j-1)"] = (
        lambda plain, r: encipher_d(
            plain, permutation.random_permutation(M, r), g, sigma, a, b
        ),
        None,
        False,
    )
    return out


def self_test() -> None:
    rng = random.Random(1)
    plain = prose_corpora(400, 1)[0]
    g = permutation.random_with_cycle_type(M, [5] * 5 + [1] * 4, rng)
    sigma = permutation.random_permutation(M, rng)
    base0 = permutation.random_permutation(M, rng)
    h = [permutation.random_permutation(M, rng) for _ in range(M)]
    a = permutation.random_permutation(M, rng)
    b = permutation.random_permutation(M, rng)
    skip = frozenset(rng.sample(range(M), 5))
    for t in (False, True):
        assert (
            decipher_a(encipher_a(plain, h, a, b, tap_cipher=t), h, a, b, tap_cipher=t)
            == plain
        )
    for c in (False, True):
        cipher = encipher_clocked(plain, base0, g, sigma, skip, by_cipher=c)
        assert decipher_clocked(cipher, base0, g, sigma, skip, by_cipher=c) == plain
    assert (
        decipher_d(encipher_d(plain, base0, g, sigma, a, b), base0, g, sigma, a, b)
        == plain
    )
    print("round trip: all six encipherings decrypt to the plaintext")

    # the base cancels inside a word, so with S empty, c_i == c_(i+5) <=> p_i == p_(i+5)
    cipher = encipher_clocked(plain, base0, g, sigma, frozenset(), by_cipher=False)
    bad = sum(
        (cw[j] == cw[j + 5]) != (pw[j] == pw[j + 5])
        for pw, cw in zip(plain, cipher)
        for j in range(len(cw) - 5)
    )
    print(f"control: d5 equalities that disagree with the plaintext's: {bad}")
    assert bad == 0
    print("self-test passed")


def skip_rate(words, skip) -> float:
    """Fraction of clock steps inside words that take the extra step."""
    drivers = [x for w in words for x in w[:-1]]
    return sum(x in skip for x in drivers) / len(drivers)


def run(draws: int = 20) -> None:
    lp = fingerprint(lp_words())
    g, sigma = walk_key()
    corpora = prose_corpora(2928, draws)
    rng = random.Random(3301)
    print(f"{draws} prose corpora of 2,928 words; mean (sd) per cell\n")
    print(f"{'model':<34}{'skip q':>8}" + "".join(f"{c:>15}" for c in CELLS))
    print(f"{'LP':<42}" + "".join(f"{lp[c]:>15.4f}" for c in CELLS))
    print(f"{'chance':<42}" + "".join(f"{1 / M:>15.4f}" for c in CELLS))
    for name, (gen, skip, by_cipher) in variants(g, sigma, rng).items():
        ciphers = [gen(plain, rng) for plain in corpora]
        sims = [fingerprint(c) for c in ciphers]
        q = ""
        if skip is not None:
            rates = [
                skip_rate(c if by_cipher else p, skip) for p, c in zip(corpora, ciphers)
            ]
            q = f"{np.mean(rates):.3f}"
        row = f"{q:>8}"
        for c in CELLS:
            v = np.array([s[c] for s in sims])
            row += f"{v.mean():.4f}({v.std():.4f})".rjust(15)
        print(f"{name:<34}{row}")


if __name__ == "__main__":
    if "--run" in sys.argv:
        run()
    else:
        self_test()
