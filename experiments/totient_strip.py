#!/usr/bin/env python3
"""Totient / math-sequence keystream stripping on the J stream.

Motivation: 3301 used phi(prime_n) as a literal keystream in a solved LP
page, and the unsolved cipher's inner step stream J lives in exactly
28 = phi(29) symbols. Prior math-keystream disproofs tested mod-29
sequences against the RAW ciphertext only. Here we test, for the first
time:

  - keystreams reduced mod 28 against the J stream (the inner cipher),
  - in BOTH interrupter alignments (doublets deleted = EA consumes no
    key; doublets as gaps = EA consumes key),
  - and mod-29 keystreams against the doublet-COMPRESSED ciphertext,
  - at every sequence start offset 0..OFFMAX, both signs.

If J = img(P) + K mod 28 for a monoalphabetic img and any candidate K,
then (J - K) has runeglish-level IoC (~1.7 normalized) — unmissable.
"""

import math

import numpy as np

from anomaly_scan import parse

N = 29
M = 28
OFFMAX = 1500


def sieve_primes(count):
    # enough primes for count + OFFMAX terms
    limit = 300000
    sieve = np.ones(limit, dtype=bool)
    sieve[:2] = False
    for i in range(2, int(limit**0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = False
    primes = np.nonzero(sieve)[0]
    return primes[:count]


def totients(limit):
    phi = np.arange(limit)
    for i in range(2, limit):
        if phi[i] == i:  # prime
            phi[i::i] = phi[i::i] - phi[i::i] // i
    return phi


def ioc_counts(x, mod):
    c = np.bincount(x, minlength=mod)
    n = len(x)
    return float((c * (c - 1)).sum()) / (n * (n - 1)) * mod


def scan(stream, K, mod, label, results):
    """IoC of (stream - K[off:off+n]) and (stream + K[off:off+n]) for all
    offsets."""
    n = len(stream)
    for sign, sname in ((1, "-K"), (-1, "+K")):
        for off in range(OFFMAX):
            seg = K[off : off + n]
            x = (stream - sign * seg) % mod
            v = ioc_counts(x, mod)
            results.append((v, label + sname, off))


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = np.array(stream[:-nplain], dtype=np.int64)
    n = len(cipher)

    delta = (cipher[1:] - cipher[:-1]) % N
    nz = delta != 0
    Jc = ((delta[nz] - 1) % M).astype(np.int64)          # compressed
    raw_idx = np.where(nz)[0]                             # gapped key index
    # compressed C: drop the second rune of each doublet
    keep = np.ones(n, dtype=bool)
    keep[1:][delta == 0] = False
    Ccomp = cipher[keep]

    total_terms = max(len(Jc), n) + OFFMAX + 10
    primes = sieve_primes(total_terms).astype(np.int64)
    phi = totients(total_terms + 2).astype(np.int64)
    idx = np.arange(total_terms, dtype=np.int64)
    fib = np.zeros(total_terms, dtype=np.int64)
    a, b = 1, 1
    for i in range(total_terms):
        fib[i] = a
        a, b = b, (a + b) % (M * N)  # keep small; residues mod 28/29 cycle

    sequences = {
        "prime": primes,
        "phi(prime)": primes - 1,
        "phi(n)": phi[1 : total_terms + 1],
        "fib": fib,
        "square": (idx + 1) ** 2,
        "triangular": (idx + 1) * (idx + 2) // 2,
    }

    results = []
    for name, seq in sequences.items():
        # mod 28 vs compressed J (EA consumes no key)
        scan(Jc, seq % M, M, f"Jcomp {name} mod28 ", results)
        # mod 28 vs gapped alignment (EA consumes key): key index = raw step
        Kfull = seq % M
        scan_gapped = (Jc - 0)  # values same; key indexed by raw position
        for sign, sname in ((1, "-K"), (-1, "+K")):
            for off in range(OFFMAX):
                seg = Kfull[off + raw_idx]
                x = (Jc - sign * seg) % M
                v = ioc_counts(x, M)
                results.append((v, f"Jgap {name} mod28 {sname}", off))
        # mod 29 vs compressed ciphertext
        scan(Ccomp, seq % N, N, f"Ccomp {name} mod29 ", results)

    results.sort(reverse=True)
    ntests = len(results)
    # null sd of nIoC for these lengths
    for stream_, mod in ((Jc, M), (Ccomp, N)):
        n_ = len(stream_)
        pairs = n_ * (n_ - 1)
        sd = mod * math.sqrt((1 / mod) * (1 - 1 / mod) * 2 / pairs) * math.sqrt(n_)
        # empirical instead:
    rng = np.random.default_rng(1)
    null = [ioc_counts(rng.integers(0, M, len(Jc)), M) for _ in range(60)]
    print(f"null nIoC for len {len(Jc)} mod {M}: mean={np.mean(null):.4f} "
          f"sd={np.std(null):.4f}")
    thresh = 1.0 + 6 * np.std(null)
    print(f"{ntests} tests; flag threshold nIoC > {thresh:.4f} "
          f"(6 sigma; english signal would be ~1.5+)")
    print("top 12 results:")
    for v, label, off in results[:12]:
        print(f"  nIoC={v:.4f} {label} offset={off}")
    nflag = sum(1 for v, _, _ in results if v > thresh)
    print(f"flagged above threshold: {nflag}")


if __name__ == "__main__":
    main()
