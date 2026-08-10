#!/usr/bin/env python3
# ABOUTME: Tests aperiodic number-theoretic running keys (primes, totient,
# ABOUTME: Fibonacci...) as Vigenere/Beaufort shifts on the LP ciphertext.
"""The algebra battery killed fixed-period and fixed-shift arithmetic, but not an
APERIODIC number-sequence running key -- a very Cicada-idiomatic construction
(the runes ARE the first 29 primes, and solved LP pages used totient/prime
shifts). A pure-shift number-Vigenere would flatten IoC to ~1.0 (which LP shows)
yet be undone by subtracting the same sequence, jumping IoC back to plaintext
(~1.7). We try each sequence under add / Vigenere / Beaufort, indexed over the
whole text, reset per word, and reset per section, and report any IoC jump.

Caveat: this only catches PURE-shift keys; a mixed permutation in the loop would
not linearize under subtraction. Negative here excludes number-key Vigenere, not
number structure inside a mixed cipher.
"""

from __future__ import annotations

from collections import Counter

from aldegonde import c3301
from experiments.within_word_phase_profile import load_sections

M = 29
ALPH = c3301.CICADA_ALPHABET
R2I = {r: i for i, r in enumerate(ALPH)}
PLAINTEXT_IOC = 1.7  # runeglish reference


def ioc(seq: list[int]) -> float:
    n = len(seq)
    if n < 2:
        return 0.0
    c = Counter(seq)
    return M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def _spf(nmax: int) -> list[int]:
    """Smallest prime factor sieve up to nmax."""
    spf = list(range(nmax + 1))
    i = 2
    while i * i <= nmax:
        if spf[i] == i:
            for j in range(i * i, nmax + 1, i):
                if spf[j] == j:
                    spf[j] = i
        i += 1
    return spf


def _factorize(k: int, spf: list[int]) -> dict[int, int]:
    f: dict[int, int] = {}
    while k > 1:
        p = spf[k]
        while k % p == 0:
            f[p] = f.get(p, 0) + 1
            k //= p
    return f


def sequences(nmax: int) -> dict[str, list[int]]:
    """Candidate integer sequences (pre-mod), 1-indexed at element k=1..nmax."""
    import math

    # bound large enough to contain the first nmax primes (nth prime ~ n ln n)
    bound = max(30, int(nmax * (math.log(nmax) + math.log(math.log(nmax))) + 10))
    spf = _spf(bound)
    primes = [k for k in range(2, bound + 1) if spf[k] == k][:nmax]

    def totient(k: int) -> int:
        r = k
        for p in _factorize(k, spf):
            r -= r // p
        return r

    def mobius(k: int) -> int:
        f = _factorize(k, spf)
        if any(e > 1 for e in f.values()):
            return 0
        return -1 if len(f) % 2 else 1

    def divisor_sum(k: int) -> int:
        s = 1
        for p, e in _factorize(k, spf).items():
            s *= (p ** (e + 1) - 1) // (p - 1)
        return s

    def omega(k: int) -> int:
        return len(_factorize(k, spf)) if k > 1 else 0

    fib = [0, 1]
    while len(fib) < nmax + 2:
        fib.append(fib[-1] + fib[-2])
    lucas = [2, 1]
    while len(lucas) < nmax + 2:
        lucas.append(lucas[-1] + lucas[-2])
    trib = [0, 0, 1]
    while len(trib) < nmax + 3:
        trib.append(trib[-1] + trib[-2] + trib[-3])
    prime_sum, s = [], 0
    for p in primes:
        s += p
        prime_sum.append(s)
    tot = [totient(k) for k in range(1, nmax + 1)]
    tot_sum, acc = [], 0
    for t in tot:
        acc += t
        tot_sum.append(acc)
    primepi, cnt = [], 0
    for k in range(1, nmax + 1):
        if spf[k] == k and k > 1:
            cnt += 1
        primepi.append(cnt)
    seqs = {
        "index":        list(range(1, nmax + 1)),                   # Trithemius
        "prime":        primes,
        "prime_gap":    [primes[k] - primes[k - 1] for k in range(1, nmax)] + [0],
        "prime_sum":    prime_sum,
        "totient":      tot,
        "totient_sum":  tot_sum,
        "fibonacci":    fib[1:nmax + 1],
        "lucas":        lucas[:nmax],
        "tribonacci":   trib[2:nmax + 2],
        "triangular":   [k * (k + 1) // 2 for k in range(1, nmax + 1)],
        "square":       [k * k for k in range(1, nmax + 1)],
        "cube":         [k ** 3 for k in range(1, nmax + 1)],
        "mobius":       [mobius(k) for k in range(1, nmax + 1)],
        "divisor_sum":  [divisor_sum(k) for k in range(1, nmax + 1)],
        "omega":        [omega(k) for k in range(1, nmax + 1)],
        "primecount":   primepi,
    }
    return {k: [int(x) % M for x in v] for k, v in seqs.items()}


def apply_key(ct: list[int], key: list[int], op: str) -> list[int]:
    if op == "vig":       # c - k
        return [(ct[i] - key[i]) % M for i in range(len(ct))]
    if op == "beaufort":  # k - c
        return [(key[i] - ct[i]) % M for i in range(len(ct))]
    return [(ct[i] + key[i]) % M for i in range(len(ct))]  # add


def framings(sections: list[tuple[list[int], list[int]]], seqs: dict[str, list[int]]):
    """Yield (label, ciphertext, key) for whole-text / per-word / per-section
    index resets. Ciphertext is the full concatenated stream in each case."""
    stream = [r for runes, _ in sections for r in runes]
    n = len(stream)

    # whole-text index
    for name, seq in seqs.items():
        yield f"{name}/whole", stream, seq[:n]

    # reset per word (index restarts at 1 each word)
    word_idx: list[int] = []
    for _runes, lengths in sections:
        for length in lengths:
            word_idx += list(range(length))
    word_idx = word_idx[:n] + [0] * (n - len(word_idx))
    for name, seq in seqs.items():
        key = [seq[word_idx[i]] for i in range(n)]
        yield f"{name}/perword", stream, key

    # reset per section
    for name, seq in seqs.items():
        key = []
        for runes, _ in sections:
            key += seq[:len(runes)]
        yield f"{name}/persection", stream, key[:n]


def main() -> None:
    sections = load_sections()
    stream = [r for runes, _ in sections for r in runes]
    n = len(stream)
    print(f"LP ciphertext: {n} runes, IoC {ioc(stream):.3f} (flat)")
    print(f"target: a key+op that jumps IoC toward plaintext ~{PLAINTEXT_IOC}\n")

    seqs = sequences(max(200, n + 5))
    results = []
    for label, ct, key in framings(sections, seqs):
        for op in ("vig", "beaufort", "add"):
            out = apply_key(ct, key, op)
            results.append((ioc(out), label, op))
    results.sort(reverse=True)

    print("top 12 IoC results (1.00 = no structure found):")
    for v, label, op in results[:12]:
        flag = "  <== HIT" if v > 1.15 else ""
        print(f"  {v:.3f}  {label:<22} {op}{flag}")
    print(f"\nbest deviation from 1.00: {max(abs(r[0]-1) for r in results):.3f}")
    if all(r[0] < 1.15 for r in results):
        print("=> no pure-shift number-sequence key linearizes the ciphertext.")


if __name__ == "__main__":
    main()
