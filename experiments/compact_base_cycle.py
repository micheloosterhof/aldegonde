# ABOUTME: A compact-state cipher whose per-word base cycles through powers of one
# ABOUTME: permutation while the order-5 letter step stays outside that cycle.
"""Can a few thousand bases carry the LP's profile, DJU-BEI's return included?

`dju-bei-gate-validity.md` leaves this open after a retraction. The seam forces
consecutive bases to differ by a rare-diagonal permutation, and a counting argument
allows about ten such tuned edges per state -- but nothing forces the bases to be a
group, so Burnside does not bound them.

The construction here is the cheapest one that satisfies every edge at once. Let the
base advance by powers of a single permutation `pi`,

    base_w = base_0 . pi^h(w),     h(w+1) = h(w) + e[feature(w)]  (mod N)

with N = ord(pi) and `feature` a low-entropy plaintext feature. The bases then take N
values and every transition difference is some `pi^e`, so tuning the handful of
exponents in use tunes every edge.

The point that was got wrong before: `g` need NOT lie in <pi>. Folding
`g^(word length - 1 mod 5)` into the base step is the WALK's device for keeping the
letter clock continuous across a space, and `length-clocked-walk.md` records that the
reset-versus-continuous choice is a reparametrisation and not observable. Dropping it
lets the letter phase reset per word and leaves `g` free, so `g` can be rich (cycle
type 5^5 1^4, which the doublet rate needs) while `pi` carries a large order. Requiring
`g` in <pi> is what capped the state count at 100.

The seam relation is then `p_last = g^-a . pi^e (p_first)` with a the word's last
phase, so the constraint is that `g^-a pi^e` be rare-diagonal over the (a, e) pairs
that occur: 5 x d relations, against the 205 bits in the pair (g, pi).

**Result (2026-09-20): the cyclic construction is refuted, and it corrects the bound.**
A tuned key reproduces the doublet rate and the distance-5 echo, but powers of one
permutation are far too correlated to pass as a set of bases:

              d1     seam       d2       d4       d5       d6      IoC    clock
    LP    0.0063   0.0079   0.0347   0.0410   0.0492   0.0245   0.9999   1.0071
    model 0.0063   0.0113   0.0339   0.0299   0.0585   0.0282   1.0332   1.2145

    returns 3.5 against 1, identical words 144 against 17, long repeats 34 against 0

The cause is structural. `pi^h` and `pi^h'` agree on every cycle whose length divides
h - h', so two states share about 4 of 29 images where two independent permutations
would share 1. That inflates the identical-word count eightfold, lifts the unigram IoC
off 1.000 and shows up in any bucketing of the corpus. Shortening the cycles makes it
worse: a first attempt used cycle type (2,3,5,7,11,1), whose fixed point pins one
ciphertext rune for every state (IoC 1.056).

**And the seam never reached its target**, stopping at 0.0146 against 0.0079, which is
the real lesson. The seam relation is `g^-a . D` with a the word's last phase, so one
transition edge carries FIVE constraints, not one. Redoing the count in
`dju-bei-gate-validity.md` with that correction:

    branching d   constraints   bits needed   against 102.8 available
    1             4.5           44            yes
    2             9.0           88            yes, marginally
    3             13.5          132           no

So the branching factor is bounded near **2**, not the 10 recorded before: the
plaintext feature driving the state carries about one bit per word, and even then the
design spends 88 of its 103 bits. A compact-state cipher of this shape is at the edge
of what 29 symbols allow.

Run with no arguments for the self-test, `--fit` to tune a key and measure it.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import (  # noqa: E402
    GP_VALUE,
    clock_reading,
    lp_words,
    prose_corpora,
    recurrence_counts,
)

M = 29
# cycle type (9,8,7,5): order 2520, the largest on 29 points with no cycle under 5, and
# inside the 2,000-4,205 the word repeats allow. Short cycles are what a first attempt
# got wrong: pi^h and pi^h' agree wherever h == h' modulo a cycle length, so a fixed
# point pins one ciphertext rune for every state (unigram IoC 1.056 against the LP's
# 1.000) and a 2- or 3-cycle makes different states produce identical cipher words.
PI_CYCLES = (9, 8, 7, 5)
N_STATES = 2520
TARGET_D1 = 0.0063
TARGET_SEAM = 0.0079


def compose(a, b):
    return [a[b[x]] for x in range(M)]


def inverse(p):
    q = [0] * M
    for i, v in enumerate(p):
        q[v] = i
    return q


def powers(p, k):
    out = [list(range(M))]
    for _ in range(k - 1):
        out.append(compose(p, out[-1]))
    return out


def rich_order5(rng):
    """Cycle type 5^5 1^4: 25 runes moving, which the doublet rate needs."""
    pts = rng.sample(range(M), 25)
    g = list(range(M))
    for c in range(5):
        cycle = pts[5 * c : 5 * c + 5]
        for t in range(5):
            g[cycle[t]] = cycle[(t + 1) % 5]
    return g


def pi_of_order(rng):
    """A permutation of order N_STATES with no cycle shorter than 5."""
    pts = rng.sample(range(M), M)
    p = list(range(M))
    at = 0
    for length in PI_CYCLES:
        cycle = pts[at : at + length]
        at += length
        for t in range(length):
            p[cycle[t]] = cycle[(t + 1) % length]
    return p


def diagonal(table, perm):
    return float(sum(table[perm[y], y] for y in range(M)))


def tables(draws=40):
    """Within-word adjacent and cross-word (final x initial) plaintext tables."""
    adjacent = np.zeros((M, M))
    cross = np.zeros((M, M))
    for plain in prose_corpora(2928, draws):
        for word in plain:
            for x, y in zip(word, word[1:]):
                adjacent[x, y] += 1
        for before, after in zip(plain, plain[1:]):
            if before and after:
                cross[before[-1], after[0]] += 1
    return adjacent / adjacent.sum(), cross / cross.sum()


def feature(word):
    """One bit of the plaintext word: the parity of its gematria sum.

    The counting bound allows a branching factor near ten; two is well inside it, and
    a solver cannot compute it without the plaintext.
    """
    return sum(GP_VALUE[r] for r in word) % 2


def pi_power(pi, k, cache):
    """pi^k by binary powering, memoised across a run."""
    if k not in cache:
        result, base, e = list(range(M)), pi, k
        while e:
            if e & 1:
                result = compose(base, result)
            base = compose(base, base)
            e >>= 1
        cache[k] = result
    return cache[k]


def states(plain, exponents):
    """The state h before each word, and the step exponent taken after it."""
    out, h = [], 0
    for word in plain:
        out.append(h)
        h = (h + exponents[feature(word)]) % N_STATES
    return out


def encipher(plain, base0, g, pi, exponents, cache=None):
    """c_j = base_{h(w)}( g^(j mod 5)( p_j ) ), base_h = base_0 . pi^h."""
    cache = {} if cache is None else cache
    gp = powers(g, 5)
    out = []
    for word, h in zip(plain, states(plain, exponents)):
        base = compose(base0, pi_power(pi, h, cache))
        out.append([base[gp[j % 5][p]] for j, p in enumerate(word)])
    return out


def decipher(cipher, base0, g, pi, exponents, plain_hint):
    """Inverse of `encipher`. The state needs the plaintext, so the feature is
    recovered word by word as decryption proceeds; `plain_hint` supplies the word
    lengths, which are public."""
    cache = {}
    gp = [inverse(q) for q in powers(g, 5)]
    out, h = [], 0
    for word in cipher:
        base = inverse(compose(base0, pi_power(pi, h, cache)))
        plain_word = [gp[j % 5][base[c]] for j, c in enumerate(word)]
        out.append(plain_word)
        h = (h + exponents[feature(plain_word)]) % N_STATES
    assert len(out) == len(plain_hint)
    return out


def seam_diagonal(g, pi, exponents, cross, weights):
    """Average rate of `p_last = g^-a pi^e (p_first)` over the (a, e) pairs in use."""
    gp = powers(g, 5)
    cache = {}
    total = 0.0
    for (a, e), w in weights.items():
        relation = compose(inverse(gp[a]), pi_power(pi, exponents[e], cache))
        total += w * diagonal(cross, relation)
    return total


def seam_weights(plain, exponents):
    """How often each (last-phase, exponent choice) pair occurs at a boundary."""
    counts: dict[tuple[int, int], float] = {}
    for word in plain[:-1]:
        key = ((len(word) - 1) % 5, feature(word))
        counts[key] = counts.get(key, 0) + 1
    total = sum(counts.values())
    return {k: v / total for k, v in counts.items()}


def tune_g(adjacent, rng, rounds=6000):
    """A rich order-5 g whose diagonal on the adjacent table sits at TARGET_D1."""
    best = rich_order5(rng)
    score = abs(diagonal(adjacent, best) - TARGET_D1)
    for _ in range(rounds):
        cand = list(best)
        a, b = rng.sample(range(M), 2)
        t = list(range(M))
        t[a], t[b] = b, a
        cand = [t[best[t[x]]] for x in range(M)]  # conjugation keeps the cycle type
        s = abs(diagonal(adjacent, cand) - TARGET_D1)
        if s < score:
            best, score = cand, s
    return best, score


def tune_pi(g, cross, weights, rng, rounds=30000):
    """A pi and two exponents whose seam relations average TARGET_SEAM."""
    pi = pi_of_order(rng)
    exponents = [rng.randrange(1, N_STATES), rng.randrange(1, N_STATES)]
    score = abs(seam_diagonal(g, pi, exponents, cross, weights) - TARGET_SEAM)
    for step in range(rounds):
        cand_pi, cand_e = pi, list(exponents)
        if step % 3:
            a, b = rng.sample(range(M), 2)
            t = list(range(M))
            t[a], t[b] = b, a
            cand_pi = [t[pi[t[x]]] for x in range(M)]
        else:
            cand_e[rng.randrange(2)] = rng.randrange(1, N_STATES)
        s = abs(seam_diagonal(g, cand_pi, cand_e, cross, weights) - TARGET_SEAM)
        if s < score:
            pi, exponents, score = cand_pi, cand_e, s
    return pi, exponents, score


def profile(cipher):
    out = {}
    for d in (1, 2, 4, 5, 6):
        hits = total = 0
        for word in cipher:
            for j in range(len(word) - d):
                total += 1
                hits += word[j] == word[j + d]
        out[f"d{d}"] = hits / total if total else float("nan")
    seam = sum(1 for a, b in zip(cipher, cipher[1:]) if a and b and a[-1] == b[0])
    out["seam"] = seam / (len(cipher) - 1)
    runes = [r for w in cipher for r in w]
    counts = np.bincount(runes, minlength=M)
    n = len(runes)
    out["IoC"] = float((counts * (counts - 1)).sum() / (n * (n - 1)) * M)
    return out


def self_test() -> None:
    rng = random.Random(3301)
    plain = prose_corpora(2928, 1)[0]
    g, pi = rich_order5(rng), pi_of_order(rng)
    exponents = [7, 13]
    base0 = rng.sample(range(M), M)
    cipher = encipher(plain, base0, g, pi, exponents)
    assert decipher(cipher, base0, g, pi, exponents, plain) == plain, (
        "round trip failed"
    )
    print("round-trip decryption holds")

    visited = len(set(states(plain, exponents)))
    print(f"distinct bases visited over 2,928 words: {visited}")
    assert visited > 1500, "the state should not collapse"

    # the seam prediction must match what the cipher actually does
    _adjacent, cross = tables(draws=4)
    weights = seam_weights(plain, exponents)
    predicted = seam_diagonal(g, pi, exponents, cross, weights)
    measured = profile(cipher)["seam"]
    print(f"seam: predicted {predicted:.4f} from the tables, measured {measured:.4f}")
    assert abs(predicted - measured) < 0.012, (
        "the seam algebra does not match the cipher"
    )
    print("self-test passed")


def fit(draws: int = 12) -> None:
    """Tune a key, then measure everything the LP fixes."""
    rng = random.Random(3301)
    adjacent, cross = tables()
    corpora = prose_corpora(2928, draws)
    weights = seam_weights(corpora[0], [1, 1])
    g, g_err = tune_g(adjacent, rng)
    pi, exponents, seam_err = tune_pi(g, cross, weights, rng)
    print(f"tuned g:  diagonal {diagonal(adjacent, g):.4f}  (target {TARGET_D1})")
    print(
        f"tuned pi: seam relations average "
        f"{seam_diagonal(g, pi, exponents, cross, weights):.4f}  (target {TARGET_SEAM})"
    )
    print(f"exponents {exponents}, state space {N_STATES}\n")

    lp = lp_words()
    lp_profile = profile(lp)
    lp_counts = recurrence_counts(lp)
    rows, counts = [], []
    for plain in corpora:
        base0 = rng.sample(range(M), M)
        cipher = encipher(plain, base0, g, pi, exponents)
        rows.append(profile(cipher))
        rows[-1]["clock"] = clock_reading(cipher)
        counts.append(recurrence_counts(cipher))
    keys = ("d1", "seam", "d2", "d4", "d5", "d6", "IoC", "clock")
    print(f"{'':<12}" + "".join(f"{k:>9}" for k in keys))
    print(
        f"{'LP':<12}"
        + "".join(f"{lp_profile.get(k, clock_reading(lp)):>9.4f}" for k in keys)
    )
    print(
        f"{'model':<12}"
        + "".join(f"{np.mean([r[k] for r in rows]):>9.4f}" for k in keys)
    )
    print(
        f"{'spread':<12}"
        + "".join(f"{np.std([r[k] for r in rows]):>9.4f}" for k in keys)
    )
    print()
    print(f"{'':<12}{'returns':>10}{'identical':>12}{'long':>8}")
    print(
        f"{'LP':<12}{lp_counts['returns']:>10}{lp_counts['identical']:>12}{lp_counts['long']:>8}"
    )
    for label, fn in (("model mean", np.mean), ("spread", np.std)):
        print(
            f"{label:<12}"
            + "".join(
                f"{fn([c[k] for c in counts]):>10.1f}"
                if k == "returns"
                else f"{fn([c[k] for c in counts]):>12.1f}"
                if k == "identical"
                else f"{fn([c[k] for c in counts]):>8.1f}"
                for k in ("returns", "identical", "long")
            )
        )
    share = np.mean([c["returns"] >= 1 for c in counts])
    print(f"\ncorpora producing a DJU-BEI-style return: {share:.0%}")


if __name__ == "__main__":
    if "--fit" in sys.argv:
        fit()
    else:
        self_test()
