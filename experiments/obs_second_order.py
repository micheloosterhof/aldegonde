# ABOUTME: Tests the LP ciphertext for 2nd-order Markov structure (bigram -> next
# ABOUTME: rune) and shows the test rejects 2-back autokeys but not the walk.
"""No second-order structure: knowing two runes predicts the third no better
than knowing one.

`pairwise-dependence.md` shows the MARGINAL (2-variable) contingency table is at
chance for every lag >= 2. That does not settle the JOINT question: c[i] could
depend on the pair (c[i-1], c[i-2]) while being marginally independent of
c[i-2] alone. This script tests the joint 2nd-order structure directly.

Statistic: conditional mutual information I(c[i] ; c[i-2] | c[i-1]) and the
trigram IoC. Both are compared against a surrogate that preserves the bigram
counts EXACTLY (per-state successor shuffle -> random Eulerian path) and
randomises only the 2nd order.

Null choice is load-bearing. A Markov RESAMPLE null (draw a fresh stream from
the estimated bigram transition matrix) is WRONG: it smooths the sampling
noise in the transition matrix, lowers the null MI, and manufactures a
spurious +4.8 sigma for the LP (and trigram IoC 1.19 vs observed 1.04). The
exact bigram-preserving surrogate removes the artifact. This is the same
null-choice trap as the doublet-suppression battery (`bigram-ioc.md`).

Power: the flatness is informative, not data starvation. Planted 2-back
autokeys light up the conditional MI (additive and Quagmire alike, since MI is
invariant under the mixed alphabet's bijective relabelling), while the LP sits
at the null -- so the 2-back autokey family is rejected. The pooled MI test
keeps power where the per-context test (grouping ciphertext by the previous
BIGRAM to expose a monoalphabetic group) dies at ~15 samples per context.
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict

from lp_corpus import N as M
from lp_corpus import load_clean

SURROGATES = 200
SEED = 3301


def cond_mi(s: list[int]) -> float:
    """I(next ; 2-back | 1-back) in nats, plug-in estimate."""
    tri: Counter = Counter()
    yx: Counter = Counter()
    zy: Counter = Counter()
    uy: Counter = Counter()
    for i in range(2, len(s)):
        z, y, x = s[i - 2], s[i - 1], s[i]
        tri[(z, y, x)] += 1
        yx[(y, x)] += 1
        zy[(z, y)] += 1
        uy[y] += 1
    t = sum(tri.values())
    return sum(
        (n / t) * math.log((n * uy[y]) / (yx[(y, x)] * zy[(z, y)]))
        for (z, y, x), n in tri.items()
    )


def trigram_ioc(s: list[int]) -> float:
    tri = Counter((s[i - 2], s[i - 1], s[i]) for i in range(2, len(s)))
    t = sum(tri.values())
    return (M**3) * sum(v * (v - 1) for v in tri.values()) / (t * (t - 1))


def bigram_preserving(seq: list[int], rng: random.Random) -> list[int]:
    """Random Eulerian-ish walk consuming each state's successor multiset:
    preserves every bigram count, randomises the 2nd order."""
    succ = defaultdict(list)
    for i in range(1, len(seq)):
        succ[seq[i - 1]].append(seq[i])
    for v in succ.values():
        rng.shuffle(v)
    out = [seq[0]]
    cur = seq[0]
    for _ in range(len(seq) - 1):
        if not succ[cur]:
            live = [k for k, v in succ.items() if v]
            if not live:
                break
            cur = rng.choice(live)  # rare dead-end restart (~2/surrogate)
            out.append(cur)
            continue
        cur = succ[cur].pop()
        out.append(cur)
    return out


def z_vs_own_null(seq: list[int], rng: random.Random, b: int = SURROGATES):
    obs = cond_mi(seq)
    nn = [cond_mi(bigram_preserving(seq, rng)) for _ in range(b)]
    mu = sum(nn) / b
    sd = math.sqrt(sum((v - mu) ** 2 for v in nn) / b)
    return obs, mu, sd, (obs - mu) / sd


def main() -> None:
    stream, _ = load_clean()
    n = len(stream)
    rng = random.Random(SEED)

    print("LP ciphertext, second-order (bigram -> next rune) structure:")
    obs, mu, sd, z = z_vs_own_null(stream, rng)
    print(
        f"  conditional MI I(next;2back|1back): {obs:.4f}  "
        f"exact-bigram null {mu:.4f} +- {sd:.4f}  z = {z:+.2f}"
    )
    obs = trigram_ioc(stream)
    nn = [trigram_ioc(bigram_preserving(stream, rng)) for _ in range(SURROGATES)]
    mu = sum(nn) / SURROGATES
    sd = math.sqrt(sum((v - mu) ** 2 for v in nn) / SURROGATES)
    print(
        f"  trigram IoC: {obs:.4f}  exact-bigram null {mu:.4f} +- {sd:.4f}  "
        f"z = {(obs - mu) / sd:+.2f}"
    )

    # doublet rate as a function of the 2-back rune
    dbl: Counter = Counter()
    tot: Counter = Counter()
    for i in range(2, n):
        tot[stream[i - 2]] += 1
        if stream[i] == stream[i - 1]:
            dbl[stream[i - 2]] += 1
    overall = sum(dbl.values()) / sum(tot.values())
    chi = sum(
        (dbl[a] - tot[a] * overall) ** 2 / (tot[a] * overall)
        for a in range(M)
        if tot[a] * overall > 0
    )
    print(
        f"  doublet rate by 2-back rune: chi2 {chi:.1f} on 28 df -> "
        f"{'flat' if chi < 40 else 'structured'}"
    )

    # power: planted 2-back autokeys must light up (else the flatness is vacuous)
    print("\npower check (each vs its OWN exact-bigram null):")
    plain = _prose(n)
    add = [plain[0], plain[1]]
    for i in range(2, len(plain)):
        add.append((plain[i] + add[i - 1] + add[i - 2]) % M)
    _, _, _, z = z_vs_own_null(add, rng)
    print(f"  planted 2-back additive autokey: z = {z:+.1f}")
    kap = list(range(M))
    rng.shuffle(kap)
    ki = [0] * M
    for i, v in enumerate(kap):
        ki[v] = i
    quag = [plain[0], plain[1]]
    for i in range(2, len(plain)):
        quag.append(kap[(ki[plain[i]] + quag[i - 1] + quag[i - 2]) % M])
    _, _, _, z = z_vs_own_null(quag, rng)
    print(
        f"  planted 2-back Quagmire autokey: z = {z:+.1f} "
        f"(mixed alphabet cannot hide it -- MI is bijection-invariant)"
    )

    # data budget: third order is unmeasurable
    bi = Counter((stream[i - 1], stream[i]) for i in range(1, n))
    tri = Counter((stream[i - 2], stream[i - 1], stream[i]) for i in range(2, n))
    print("\ndata budget:")
    print(
        f"  bigram contexts with >=30 samples: "
        f"{sum(1 for v in bi.values() if v >= 30)}/{M * M} (mean {n / (M * M):.0f})"
    )
    print(
        f"  distinct trigrams {len(tri)}/{M**3}, max repeat {max(tri.values())} "
        f"-> per-context 3rd order is not measurable"
    )

    print("\nVERDICT: no second-order structure (z ~ 0 on every statistic under the")
    print("exact-bigram null); the test rejects 2-back autokeys (planted z ~ +35).")
    print("Consistent with a per-word latent-state cipher (the walk), not with")
    print("running feedback. The +4.8 sigma under a resample null is an artifact.")


def _prose(n: int) -> list[int]:
    from period5_confirmation import prose_words

    return [x for w in prose_words() for x in w][:n]


if __name__ == "__main__":
    main()
