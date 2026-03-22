# ABOUTME: Search for per-C[i-2] multiplier table for multiplicative autokey.
# ABOUTME: Tests whether ANY multiplier function g(C[i-2]) produces English.

"""Search for the optimal multiplier table for multiplicative autokey.

Under C[i] = C[i-1] - P[i] * g(C[i-2]) mod 29, the function g maps
each possible C[i-2] value to a non-zero multiplier. Instead of
parameterizing g with a simple formula, we search for the BEST
multiplier independently for each of the 29 possible C[i-2] values.

For each C[i-2] value, we try all 28 non-zero multipliers and pick
the one that produces the best IOC on the positions where that C[i-2]
value occurs. Then we combine all the best multipliers into a complete
table and score the full plaintext.

This is the most general test of the multiplicative w=2 model.
"""

from __future__ import annotations

import sys
from collections import Counter, defaultdict

sys.path.insert(0, "src")

from aldegonde import c3301
from aldegonde.stats.ioc import ioc as compute_ioc

ALPHABET = c3301.CICADA_ALPHABET
ENG = c3301.CICADA_ENGLISH_ALPHABET
N = len(ALPHABET)

# Precompute inverses
INVERSES = [0] * N
for i in range(1, N):
    INVERSES[i] = pow(i, N - 2, N)


def load() -> list[int]:
    with open("data/page0-58.txt") as f:
        text = f.read()
    return [c3301.r2i(c) for c in text if c in ALPHABET]


def search_w2_multiplicative(ct: list[int]) -> None:
    """Search for optimal g(C[i-2]) multiplier table."""
    n = len(ct)

    # Group positions by C[i-2]
    groups: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for i in range(2, n):
        # (C[i-1], C[i], position)
        groups[ct[i - 2]].append((ct[i - 1], ct[i], i))

    print(f"{'=' * 70}")
    print("Searching for optimal g(C[i-2]) multiplier table")
    print(f"Model: C[i] = C[i-1] - P[i] * g(C[i-2]) mod {N}")
    print(f"{'=' * 70}\n")

    best_table: dict[int, int] = {}
    best_iocs: dict[int, float] = {}

    for ct2_val in range(N):
        positions = groups[ct2_val]
        if not positions:
            best_table[ct2_val] = 1
            best_iocs[ct2_val] = 1 / N
            continue

        best_mult = 1
        best_ioc = 0.0

        for mult in range(1, N):
            inv_mult = INVERSES[mult]
            pt_vals = [((prev_c - c) * inv_mult) % N for prev_c, c, _ in positions]
            if len(pt_vals) >= 2:
                ioc_val = compute_ioc(pt_vals)
            else:
                ioc_val = 0.0
            if ioc_val > best_ioc:
                best_ioc = ioc_val
                best_mult = mult

        best_table[ct2_val] = best_mult
        best_iocs[ct2_val] = best_ioc

        rune = c3301.i2r(ct2_val)
        eng = ENG[ct2_val]
        print(f"  C[i-2]={ct2_val:2d} ({rune}/{eng:>2}): "
              f"best mult={best_mult:2d}, IOC={best_ioc:.6f} "
              f"(n={len(positions)}, random={1/N:.4f})")

    # Compute full plaintext with the optimal table
    print(f"\n{'=' * 70}")
    print("Full plaintext with optimal multiplier table")
    print(f"{'=' * 70}\n")

    pt = [0, 0]  # First two positions don't have C[i-2]
    for i in range(2, n):
        mult = best_table[ct[i - 2]]
        p = ((ct[i - 1] - ct[i]) * INVERSES[mult]) % N
        pt.append(p)

    full_ioc = compute_ioc(pt[2:])
    qg = c3301.quadgramscore("".join(c3301.i2r(p) for p in pt[2:]))

    print(f"  Full plaintext IOC: {full_ioc:.6f} (random: {1/N:.6f})")
    print(f"  Quadgram score: {qg:.1f}")
    print(f"  Mean per-group IOC: {sum(best_iocs.values()) / N:.6f}")

    # First 60 runes as English
    eng_pt = "".join(ENG[p] for p in pt[2:62])
    print(f"  First 60 runes: {eng_pt}")

    # Letter frequency of full plaintext
    freq = Counter(pt[2:])
    print(f"\n  Letter frequencies:")
    for idx in range(N):
        count = freq.get(idx, 0)
        pct = 100 * count / (n - 2)
        bar = "#" * int(pct * 2)
        print(f"    {ENG[idx]:>2} ({idx:2d}): {pct:5.2f}% {bar}")


def search_w3_multiplicative(ct: list[int]) -> None:
    """Search with g(C[i-2], C[i-3]) — using the SUM C[i-2]+C[i-3] as key."""
    n = len(ct)

    # Group positions by (C[i-2] + C[i-3]) mod 29
    groups: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for i in range(3, n):
        key = (ct[i - 2] + ct[i - 3]) % N
        groups[key].append((ct[i - 1], ct[i], i))

    print(f"\n{'=' * 70}")
    print("Searching for optimal g(C[i-2]+C[i-3]) multiplier table")
    print(f"Model: C[i] = C[i-1] - P[i] * g((C[i-2]+C[i-3]) mod {N}) mod {N}")
    print(f"{'=' * 70}\n")

    best_table: dict[int, int] = {}
    best_iocs: dict[int, float] = {}

    for key_val in range(N):
        positions = groups[key_val]
        if not positions:
            best_table[key_val] = 1
            best_iocs[key_val] = 1 / N
            continue

        best_mult = 1
        best_ioc = 0.0

        for mult in range(1, N):
            inv_mult = INVERSES[mult]
            pt_vals = [((prev_c - c) * inv_mult) % N for prev_c, c, _ in positions]
            if len(pt_vals) >= 2:
                ioc_val = compute_ioc(pt_vals)
            else:
                ioc_val = 0.0
            if ioc_val > best_ioc:
                best_ioc = ioc_val
                best_mult = mult

        best_table[key_val] = best_mult
        best_iocs[key_val] = best_ioc

    # Compute full plaintext
    pt = [0, 0, 0]
    for i in range(3, n):
        key = (ct[i - 2] + ct[i - 3]) % N
        mult = best_table[key]
        p = ((ct[i - 1] - ct[i]) * INVERSES[mult]) % N
        pt.append(p)

    full_ioc = compute_ioc(pt[3:])
    qg = c3301.quadgramscore("".join(c3301.i2r(p) for p in pt[3:]))
    mean_ioc = sum(best_iocs.values()) / N

    print(f"  Full plaintext IOC: {full_ioc:.6f} (random: {1/N:.6f})")
    print(f"  Quadgram score: {qg:.1f}")
    print(f"  Mean per-group IOC: {mean_ioc:.6f}")

    eng_pt = "".join(ENG[p] for p in pt[3:63])
    print(f"  First 60 runes: {eng_pt}")


def search_additive_table(ct: list[int]) -> None:
    """Search for optimal additive offset per C[i-2] value.

    P[i] = (C[i-1] - C[i] + g(C[i-2])) mod 29
    """
    n = len(ct)

    groups: dict[int, list[tuple[int, int, int]]] = defaultdict(list)
    for i in range(2, n):
        groups[ct[i - 2]].append((ct[i - 1], ct[i], i))

    print(f"\n{'=' * 70}")
    print("Searching for optimal additive offset table per C[i-2]")
    print(f"Model: P[i] = (C[i-1] - C[i] + g(C[i-2])) mod {N}")
    print(f"{'=' * 70}\n")

    best_table: dict[int, int] = {}

    for ct2_val in range(N):
        positions = groups[ct2_val]
        if not positions:
            best_table[ct2_val] = 0
            continue

        best_offset = 0
        best_ioc = 0.0

        for offset in range(N):
            pt_vals = [((prev_c - c + offset) % N) for prev_c, c, _ in positions]
            if len(pt_vals) >= 2:
                ioc_val = compute_ioc(pt_vals)
            else:
                ioc_val = 0.0
            if ioc_val > best_ioc:
                best_ioc = ioc_val
                best_offset = offset

        best_table[ct2_val] = best_offset

    # Full plaintext
    pt = [0, 0]
    for i in range(2, n):
        offset = best_table[ct[i - 2]]
        p = (ct[i - 1] - ct[i] + offset) % N
        pt.append(p)

    full_ioc = compute_ioc(pt[2:])
    qg = c3301.quadgramscore("".join(c3301.i2r(p) for p in pt[2:]))

    print(f"  Full plaintext IOC: {full_ioc:.6f} (random: {1/N:.6f})")
    print(f"  Quadgram score: {qg:.1f}")

    eng_pt = "".join(ENG[p] for p in pt[2:62])
    print(f"  First 60 runes: {eng_pt}")


def main() -> None:
    ct = load()
    print(f"Ciphertext: {len(ct)} runes\n")

    search_w2_multiplicative(ct)
    search_additive_table(ct)
    search_w3_multiplicative(ct)


if __name__ == "__main__":
    main()
