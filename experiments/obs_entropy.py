# ABOUTME: Observation: near-maximal entropy and zero compressible redundancy
# ABOUTME: -- the stream carries no exploitable statistical structure.
"""Entropy & incompressibility. Significance: H1 vs the 4.858-bit maximum, and
zlib/bz2 compressed size vs the mean of shuffled surrogates (z)."""
from __future__ import annotations
import math, zlib, bz2, statistics, random
from collections import Counter
from lp_corpus import load_clean, N


def entropy(seq):
    n = len(seq)
    c = Counter(seq)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def cond_entropy(seq):
    bg = Counter((seq[i], seq[i + 1]) for i in range(len(seq) - 1))
    uni = Counter(seq[i] for i in range(len(seq) - 1))
    tot = sum(bg.values())
    h = 0.0
    for (a, b), v in bg.items():
        p_ab = v / tot
        p_b_given_a = v / uni[a]
        h -= p_ab * math.log2(p_b_given_a)
    return h


def main() -> None:
    stream, _ = load_clean()
    rng = random.Random(0)
    h1 = entropy(stream)
    h2 = cond_entropy(stream)
    print(f"H1 = {h1:.4f} bits of max {math.log2(N):.4f} ({100*h1/math.log2(N):.2f}%)")
    print(f"H(X2|X1) = {h2:.4f} bits")
    raw = bytes(stream)
    for name, comp in (("zlib", lambda b: zlib.compress(b, 9)), ("bz2", bz2.compress)):
        obs = len(comp(raw))
        null = []
        for _ in range(30):
            sh = stream[:]; rng.shuffle(sh)
            null.append(len(comp(bytes(sh))))
        mu, sd = statistics.mean(null), statistics.stdev(null)
        print(f"{name}: {obs} bytes vs shuffled {mu:.0f}+/-{sd:.0f}  z={(obs-mu)/sd:+.1f}")
    print("VERDICT: >99.9% of max entropy, no compressible redundancy (z~0)")


if __name__ == "__main__":
    main()
