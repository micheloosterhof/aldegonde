# ABOUTME: Tests cipher models that operate on GP prime values instead of rune indices.
# ABOUTME: Tries additive and multiplicative autokey with various moduli.

"""Test cipher models using Gematria Primus prime values.

Each rune has a unique prime value (F=2, U=3, TH=5, ..., EA=109).
Instead of C[i] = C[i-1] - P[i] mod 29 on rune indices, what if:
  prime(C[i]) = prime(C[i-1]) - prime(P[i]) mod M

The result must be a valid GP prime for the model to be consistent.
Since there are only 29 valid primes out of M possible values, random
arithmetic almost never lands on valid primes — so consistency is a
very strong test.
"""

from __future__ import annotations

import sys
from collections import Counter

sys.path.insert(0, "src")

from aldegonde import c3301
from aldegonde.stats.ioc import ioc as compute_ioc

ALPHABET = c3301.CICADA_ALPHABET
ENG = c3301.CICADA_ENGLISH_ALPHABET
N = len(ALPHABET)

GP_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43,
             47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]

# Rune index -> GP prime
IDX_TO_PRIME = {i: p for i, p in enumerate(GP_PRIMES)}
# GP prime -> rune index
PRIME_TO_IDX = {p: i for i, p in enumerate(GP_PRIMES)}
PRIME_SET = set(GP_PRIMES)


def load() -> list[int]:
    with open("data/page0-58.txt") as f:
        text = f.read()
    return [c3301.r2i(c) for c in text if c in ALPHABET]


def ct_primes(ct_indices: list[int]) -> list[int]:
    """Convert rune indices to GP prime values."""
    return [IDX_TO_PRIME[i] for i in ct_indices]


def test_additive_autokey(ct: list[int], mod: int) -> None:
    """Test: prime(C[i]) = (prime(C[i-1]) - prime(P[i])) mod M

    Beaufort-style. For each primer, check if every decrypted value is
    a valid GP prime.
    """
    primes = ct_primes(ct)
    n = len(primes)

    consistent = 0
    best_ioc = 0.0
    best_primer = -1
    best_pt = None

    for primer_idx in range(N):
        primer_prime = GP_PRIMES[primer_idx]
        pt_indices = []
        valid = True

        prev_p = primer_prime
        for c_p in primes:
            diff = (prev_p - c_p) % mod
            if diff not in PRIME_TO_IDX:
                valid = False
                break
            pt_indices.append(PRIME_TO_IDX[diff])
            prev_p = c_p

        if valid:
            consistent += 1
            ioc_val = compute_ioc(pt_indices)
            if ioc_val > best_ioc:
                best_ioc = ioc_val
                best_primer = primer_idx
                best_pt = pt_indices

    if consistent > 0:
        eng = "".join(ENG[p] for p in best_pt[:50]) if best_pt else ""
        print(f"    {consistent:3d} consistent primers, "
              f"best IOC={best_ioc:.6f} (primer={ENG[best_primer]})")
        print(f"        Plaintext: {eng}")
    else:
        print(f"    No consistent primers")


def test_vigenere_autokey(ct: list[int], mod: int) -> None:
    """Test: prime(C[i]) = (prime(P[i]) + prime(C[i-1])) mod M"""
    primes = ct_primes(ct)

    consistent = 0
    best_ioc = 0.0
    best_primer = -1
    best_pt = None

    for primer_idx in range(N):
        primer_prime = GP_PRIMES[primer_idx]
        pt_indices = []
        valid = True

        prev_p = primer_prime
        for c_p in primes:
            diff = (c_p - prev_p) % mod
            if diff not in PRIME_TO_IDX:
                valid = False
                break
            pt_indices.append(PRIME_TO_IDX[diff])
            prev_p = c_p

        if valid:
            consistent += 1
            ioc_val = compute_ioc(pt_indices)
            if ioc_val > best_ioc:
                best_ioc = ioc_val
                best_primer = primer_idx
                best_pt = pt_indices

    if consistent > 0:
        eng = "".join(ENG[p] for p in best_pt[:50]) if best_pt else ""
        print(f"    {consistent:3d} consistent primers, "
              f"best IOC={best_ioc:.6f} (primer={ENG[best_primer]})")
        print(f"        Plaintext: {eng}")
    else:
        print(f"    No consistent primers")


def test_multiplicative_autokey(ct: list[int], mod: int) -> None:
    """Test: prime(C[i]) = (prime(C[i-1]) * prime(P[i])) mod M

    Multiplicative in prime space. Since all GP primes are non-zero
    and mod is prime, inverses exist.
    """
    primes = ct_primes(ct)

    consistent = 0
    best_ioc = 0.0
    best_primer = -1
    best_pt = None

    for primer_idx in range(N):
        primer_prime = GP_PRIMES[primer_idx]
        pt_indices = []
        valid = True

        prev_p = primer_prime
        for c_p in primes:
            # P_prime = C_prime * inverse(C_prev_prime) mod M
            inv_prev = pow(prev_p, mod - 2, mod) if mod > 2 else pow(prev_p, -1, mod)
            p_prime = (c_p * inv_prev) % mod
            if p_prime not in PRIME_TO_IDX:
                valid = False
                break
            pt_indices.append(PRIME_TO_IDX[p_prime])
            prev_p = c_p

        if valid:
            consistent += 1
            ioc_val = compute_ioc(pt_indices)
            if ioc_val > best_ioc:
                best_ioc = ioc_val
                best_primer = primer_idx
                best_pt = pt_indices

    if consistent > 0:
        eng = "".join(ENG[p] for p in best_pt[:50]) if best_pt else ""
        print(f"    {consistent:3d} consistent primers, "
              f"best IOC={best_ioc:.6f} (primer={ENG[best_primer]})")
        print(f"        Plaintext: {eng}")
    else:
        print(f"    No consistent primers")


def test_power_map_autokey(ct: list[int], mod: int, exp: int) -> None:
    """Test: prime(C[i]) = (prime(C[i-1]) + prime(P[i]))^exp mod M

    Power map. Decrypt: prime(P[i]) = prime(C[i])^(1/exp) - prime(C[i-1]) mod M
    """
    from math import gcd
    if gcd(exp, mod - 1) != 1:
        print(f"    Exponent {exp} not invertible mod {mod-1}")
        return

    primes = ct_primes(ct)
    exp_inv = pow(exp, -1, mod - 1)

    consistent = 0
    best_ioc = 0.0
    best_primer = -1
    best_pt = None

    for primer_idx in range(N):
        primer_prime = GP_PRIMES[primer_idx]
        pt_indices = []
        valid = True

        prev_p = primer_prime
        for c_p in primes:
            root = pow(c_p, exp_inv, mod) if c_p != 0 else 0
            p_prime = (root - prev_p) % mod
            if p_prime not in PRIME_TO_IDX:
                valid = False
                break
            pt_indices.append(PRIME_TO_IDX[p_prime])
            prev_p = c_p

        if valid:
            consistent += 1
            ioc_val = compute_ioc(pt_indices)
            if ioc_val > best_ioc:
                best_ioc = ioc_val
                best_primer = primer_idx
                best_pt = pt_indices

    if consistent > 0:
        eng = "".join(ENG[p] for p in best_pt[:50]) if best_pt else ""
        print(f"    {consistent:3d} consistent primers, "
              f"best IOC={best_ioc:.6f} (primer={ENG[best_primer]})")
        print(f"        Plaintext: {eng}")
    else:
        print(f"    No consistent primers")


def main() -> None:
    ct = load()
    print(f"Ciphertext: {len(ct)} runes")
    print(f"GP prime range: {min(GP_PRIMES)}-{max(GP_PRIMES)}")
    print(f"GP primes: {GP_PRIMES}")

    # Random hit probability: 29/M for each position
    # Over 13136 positions, need ALL to hit: (29/M)^13136
    # Even for M=113: (29/113)^13136 ≈ 0. Consistency is extremely selective.

    # Moduli to try: various primes near and above 109
    moduli = [29, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167,
              173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
              233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283]

    # Also try composite moduli with special properties
    moduli.extend([110, 116, 120, 210, 290, 29 * 4, 29 * 5])

    print(f"\n{'=' * 70}")
    print("ADDITIVE BEAUFORT: prime(C) = (prime(C_prev) - prime(P)) mod M")
    print(f"{'=' * 70}")
    for m in sorted(set(moduli)):
        hit_pct = 100 * len(PRIME_SET) / m
        print(f"\n  mod {m:4d} (hit rate {hit_pct:.1f}%):")
        test_additive_autokey(ct, m)

    print(f"\n{'=' * 70}")
    print("ADDITIVE VIGENERE: prime(C) = (prime(P) + prime(C_prev)) mod M")
    print(f"{'=' * 70}")
    for m in sorted(set(moduli)):
        print(f"\n  mod {m:4d}:")
        test_vigenere_autokey(ct, m)

    # Multiplicative: only works for prime moduli
    prime_moduli = [m for m in sorted(set(moduli))
                    if m > 1 and all(m % i != 0 for i in range(2, int(m**0.5) + 1))]
    print(f"\n{'=' * 70}")
    print("MULTIPLICATIVE: prime(C) = (prime(C_prev) * prime(P)) mod M")
    print(f"{'=' * 70}")
    for m in prime_moduli:
        print(f"\n  mod {m:4d}:")
        test_multiplicative_autokey(ct, m)

    # Power map with prime moduli
    print(f"\n{'=' * 70}")
    print("POWER MAP: prime(C) = (prime(C_prev) + prime(P))^e mod M")
    print(f"{'=' * 70}")
    for m in prime_moduli[:10]:  # Limit for speed
        for exp in [3, 5, 7, 11]:
            print(f"\n  mod {m:4d}, exp {exp}:")
            test_power_map_autokey(ct, m, exp)


if __name__ == "__main__":
    main()
