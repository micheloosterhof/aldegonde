#!/usr/bin/env python3

"""
Liber Primus analysis: GF(29) multiplicative/mixed autokey exploration.
Uses 1-based indexing where EA rune = 29 % 29 = 0.

Explores cipher variants mixing addition and multiplication in GF(29),
including ciphertext autokey, plaintext autokey, and mixed feedback.
"""

from collections import defaultdict

from aldegonde import pasc, masc, auto, c3301
from aldegonde.stats import print_ioc_statistics, print_kappa
from aldegonde.stats import repeats, dist, ngrams, entropy, isomorph
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor, primes, totient, modular, moebius
from aldegonde.analysis import friedman, krakup

N = 29  # GF(29)


def val(rune: str) -> int:
    """Convert rune to 1-based value in GF(29). EA = 0."""
    return (c3301.r2i(rune) + 1) % N


def rune(v: int) -> str:
    """Convert GF(29) value back to rune."""
    return c3301.CICADA_ALPHABET[(v - 1) % N]


def inv(a: int) -> int:
    """Multiplicative inverse in GF(29). Undefined for 0."""
    return pow(a, N - 2, N)  # Fermat's little theorem: a^(p-2) = a^-1 mod p


def vals(text: str) -> list[int]:
    """Convert rune string to list of GF(29) values."""
    return [val(r) for r in text]


def runes(values: list[int]) -> str:
    """Convert list of GF(29) values back to rune string."""
    return "".join(rune(v) for v in values)


# ============================================================================
# CIPHER VARIANT DECRYPTION FUNCTIONS
# Each returns a list of plaintext values given ciphertext values and primers
# Returns None if decryption fails (e.g. division by zero)
# ============================================================================

def decrypt_additive_ct_autokey(C: list[int], primer_c: int) -> list[int] | None:
    """C(i) = P(i) + C(i-1) mod 29  =>  P(i) = C(i) - C(i-1)"""
    P = []
    prev_c = primer_c
    for c in C:
        P.append((c - prev_c) % N)
        prev_c = c
    return P


def decrypt_beaufort_ct_autokey(C: list[int], primer_c: int) -> list[int] | None:
    """C(i) = C(i-1) - P(i) mod 29  =>  P(i) = C(i-1) - C(i)"""
    P = []
    prev_c = primer_c
    for c in C:
        P.append((prev_c - c) % N)
        prev_c = c
    return P


def decrypt_additive_pt_autokey(C: list[int], primer_p: int) -> list[int] | None:
    """C(i) = P(i) + P(i-1) mod 29  =>  P(i) = C(i) - P(i-1)"""
    P = []
    prev_p = primer_p
    for c in C:
        p = (c - prev_p) % N
        P.append(p)
        prev_p = p
    return P


def decrypt_beaufort_pt_autokey(C: list[int], primer_p: int) -> list[int] | None:
    """C(i) = P(i-1) - P(i) mod 29  =>  P(i) = P(i-1) - C(i)"""
    P = []
    prev_p = primer_p
    for c in C:
        p = (prev_p - c) % N
        P.append(p)
        prev_p = p
    return P


def decrypt_mult_ct_autokey(C: list[int], primer_c: int) -> list[int] | None:
    """C(i) = P(i) * C(i-1) mod 29  =>  P(i) = C(i) * inv(C(i-1))"""
    P = []
    prev_c = primer_c
    for c in C:
        if prev_c == 0:
            return None  # Can't invert 0
        P.append((c * inv(prev_c)) % N)
        prev_c = c
    return P


def decrypt_mult_pt_autokey(C: list[int], primer_p: int) -> list[int] | None:
    """C(i) = P(i) * P(i-1) mod 29  =>  P(i) = C(i) * inv(P(i-1))"""
    P = []
    prev_p = primer_p
    for c in C:
        if prev_p == 0:
            return None  # Can't invert 0
        p = (c * inv(prev_p)) % N
        P.append(p)
        prev_p = p
    return P


def decrypt_pp_plus_c(C: list[int], primer_c: int, primer_p: int) -> list[int] | None:
    """C(i) = P(i)*P(i-1) + C(i-1) mod 29  =>  P(i)*P(i-1) = C(i)-C(i-1)
       P(i) = (C(i)-C(i-1)) * inv(P(i-1))"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        if prev_p == 0:
            return None
        p = ((c - prev_c) * inv(prev_p)) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_plus_cp(C: list[int], primer_c: int, primer_p: int) -> list[int] | None:
    """C(i) = P(i) + C(i-1)*P(i-1) mod 29  =>  P(i) = C(i) - C(i-1)*P(i-1)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = (c - prev_c * prev_p) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_pc_plus_p(C: list[int], primer_c: int, primer_p: int) -> list[int] | None:
    """C(i) = P(i)*C(i-1) + P(i-1) mod 29  =>  P(i) = (C(i)-P(i-1)) * inv(C(i-1))"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        if prev_c == 0:
            return None
        p = ((c - prev_p) * inv(prev_c)) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_times_c_plus_p(C: list[int], primer_c: int, primer_p: int) -> list[int] | None:
    """C(i) = P(i)*(C(i-1)+P(i-1)) mod 29  =>  P(i) = C(i) * inv(C(i-1)+P(i-1))"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        key = (prev_c + prev_p) % N
        if key == 0:
            return None
        p = (c * inv(key)) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_times_c_minus_p(C: list[int], primer_c: int, primer_p: int) -> list[int] | None:
    """C(i) = P(i)*(C(i-1)-P(i-1)) mod 29  =>  P(i) = C(i) * inv(C(i-1)-P(i-1))"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        key = (prev_c - prev_p) % N
        if key == 0:
            return None
        p = (c * inv(key)) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_cp_minus_p(C: list[int], primer_c: int, primer_p: int) -> list[int] | None:
    """C(i) = C(i-1)*P(i-1) - P(i) mod 29  =>  P(i) = C(i-1)*P(i-1) - C(i)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = (prev_c * prev_p - c) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_pp_times_c(C: list[int], primer_c: int, primer_p: int) -> list[int] | None:
    """C(i) = P(i)*P(i-1)*C(i-1) mod 29  =>  P(i) = C(i) * inv(P(i-1)*C(i-1))"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        key = (prev_p * prev_c) % N
        if key == 0:
            return None
        p = (c * inv(key)) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_plus_c_times_c(C: list[int], primer_c: int) -> list[int] | None:
    """C(i) = P(i) + C(i-1)*C(i-2) mod 29  =>  P(i) = C(i) - C(i-1)*C(i-2)
       Uses two ciphertext history values. primer_c = C(-1), C(-2) = 0."""
    P = []
    prev_c2 = 0  # C(-2)
    prev_c1 = primer_c  # C(-1)
    for c in C:
        p = (c - prev_c1 * prev_c2) % N
        P.append(p)
        prev_c2 = prev_c1
        prev_c1 = c
    return P


def decrypt_p_sq_plus_c(C: list[int], primer_c: int, primer_p: int) -> list[int] | None:
    """C(i) = P(i)^2 + C(i-1) mod 29
       P(i)^2 = C(i) - C(i-1) mod 29
       P(i) = sqrt(C(i) - C(i-1)) in GF(29)
       Note: not all elements have square roots in GF(29). Since 29 ≡ 1 mod 4,
       -1 is a QR. Exactly 15 elements are QRs (including 0)."""
    # Precompute square roots in GF(29)
    sqrt_table: dict[int, list[int]] = {}
    for x in range(N):
        sq = (x * x) % N
        sqrt_table.setdefault(sq, []).append(x)
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        target = (c - prev_c) % N
        if target not in sqrt_table:
            return None  # No square root exists
        # Use the root closest to prev_p as heuristic? Or try both?
        # For now, pick the root that gives best continuation
        roots = sqrt_table[target]
        p = min(roots, key=lambda r: abs(r - prev_p))  # heuristic
        P.append(p)
        prev_c = c
        prev_p = p
    return P


# ============================================================================
# MAIN
# ============================================================================

with open("data/page0-58.txt") as f:
    lp = f.read()

segments = lp.split("$")
z = segments[0:10]
y = ["".join(z)]

print(f"{len(segments)} segments")
for seg_idx, s in enumerate(y):
    if len(s) == 0:
        continue
    print(f"\n\nNEW SEGMENT {seg_idx} **************")

    raw = "".join([x for x in s if x in c3301.CICADA_ALPHABET])
    C = vals(raw)

    print("RAW:")
    c3301.print_all(raw, limit=30)
    print(f"length: {len(raw)} symbols")

    # ========================================================================
    # PHASE 1: Single-primer variants (29 trials each)
    # ========================================================================
    print("\n" + "=" * 90)
    print("PHASE 1: SINGLE-PRIMER GF(29) VARIANTS (29 trials each)")
    print("=" * 90)

    single_primer_variants: list[tuple[str, str]] = []
    # (name, type): type is "ct" for ciphertext primer, "pt" for plaintext primer

    results: list[tuple[float, str, int, str]] = []  # (score, name, primer_val, plaintext_runes)

    # --- Additive autokeys ---
    for primer_val in range(N):
        P = decrypt_additive_ct_autokey(C, primer_val)
        if P is not None:
            pt = runes(P)
            score = c3301.quadgramscore(pt)
            results.append((score, "P+Ci-1 (add ct)", primer_val, pt))

    for primer_val in range(N):
        P = decrypt_beaufort_ct_autokey(C, primer_val)
        if P is not None:
            pt = runes(P)
            score = c3301.quadgramscore(pt)
            results.append((score, "Ci-1-P (beau ct)", primer_val, pt))

    for primer_val in range(N):
        P = decrypt_additive_pt_autokey(C, primer_val)
        if P is not None:
            pt = runes(P)
            score = c3301.quadgramscore(pt)
            results.append((score, "P+Pi-1 (add pt)", primer_val, pt))

    for primer_val in range(N):
        P = decrypt_beaufort_pt_autokey(C, primer_val)
        if P is not None:
            pt = runes(P)
            score = c3301.quadgramscore(pt)
            results.append((score, "Pi-1-P (beau pt)", primer_val, pt))

    # --- Multiplicative autokeys ---
    for primer_val in range(N):
        P = decrypt_mult_ct_autokey(C, primer_val)
        if P is not None:
            pt = runes(P)
            score = c3301.quadgramscore(pt)
            results.append((score, "P*Ci-1 (mult ct)", primer_val, pt))

    for primer_val in range(N):
        P = decrypt_mult_pt_autokey(C, primer_val)
        if P is not None:
            pt = runes(P)
            score = c3301.quadgramscore(pt)
            results.append((score, "P*Pi-1 (mult pt)", primer_val, pt))

    # --- C(i-1)*C(i-2) variant (single primer) ---
    for primer_val in range(N):
        P = decrypt_p_plus_c_times_c(C, primer_val)
        if P is not None:
            pt = runes(P)
            score = c3301.quadgramscore(pt)
            results.append((score, "P+Ci-1*Ci-2", primer_val, pt))

    results.sort(key=lambda x: x[0], reverse=True)

    print(f"\n{'Rank':>4} {'Score':>10} {'Variant':<20} {'Primer':>6} {'Decrypted (first 50 runeglish)'}")
    print("-" * 100)
    for rank, (score, name, pv, pt) in enumerate(results[:40], 1):
        pt_eng = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.r2i(r)] for r in pt[:50])
        print(f"{rank:4d} {score:10.2f} {name:<20} {pv:>6} {pt_eng}")

    # ========================================================================
    # PHASE 2: Two-primer variants (29x29 = 841 trials each)
    # ========================================================================
    print("\n" + "=" * 90)
    print("PHASE 2: TWO-PRIMER GF(29) MIXED VARIANTS (841 trials each)")
    print("=" * 90)

    results2: list[tuple[float, str, int, int, str]] = []

    two_primer_funcs = [
        ("P*Pi-1+Ci-1", decrypt_pp_plus_c),
        ("P+Ci-1*Pi-1", decrypt_p_plus_cp),
        ("P*Ci-1+Pi-1", decrypt_pc_plus_p),
        ("P*(Ci-1+Pi-1)", decrypt_p_times_c_plus_p),
        ("P*(Ci-1-Pi-1)", decrypt_p_times_c_minus_p),
        ("Ci-1*Pi-1-P", decrypt_cp_minus_p),
        ("P*Pi-1*Ci-1", decrypt_pp_times_c),
    ]

    for func_name, func in two_primer_funcs:
        for pc in range(N):
            for pp in range(N):
                P = func(C, pc, pp)
                if P is not None:
                    pt = runes(P)
                    score = c3301.quadgramscore(pt)
                    results2.append((score, func_name, pc, pp, pt))

    results2.sort(key=lambda x: x[0], reverse=True)

    print(f"\n{'Rank':>4} {'Score':>10} {'Variant':<18} {'Pc':>3} {'Pp':>3} {'Decrypted (first 50 runeglish)'}")
    print("-" * 110)
    for rank, (score, name, pc, pp, pt) in enumerate(results2[:50], 1):
        pt_eng = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.r2i(r)] for r in pt[:50])
        print(f"{rank:4d} {score:10.2f} {name:<18} {pc:>3} {pp:>3} {pt_eng}")

    # ========================================================================
    # PHASE 3: Full analysis on overall best
    # ========================================================================
    # Combine all results and pick the best
    all_results: list[tuple[float, str, str]] = []
    for score, name, pv, pt in results:
        all_results.append((score, f"{name} primer={pv}", pt))
    for score, name, pc, pp, pt in results2:
        all_results.append((score, f"{name} pc={pc},pp={pp}", pt))

    all_results.sort(key=lambda x: x[0], reverse=True)

    best_score, best_desc, seg = all_results[0]

    print(f"\n\n{'=' * 90}")
    print(f"FULL ANALYSIS OF BEST RESULT")
    print(f"{'=' * 90}")
    print(f"Cipher: {best_desc}")
    print(f"Score: {best_score:.2f}\n")

    print("DECRYPTED:")
    c3301.print_all(seg, limit=30)

    if len(seg) == 0:
        print("EMPTY SEGMENT")
        continue
    print(f"used alphabet: {set(seg)} ({len(set(seg))} symbols)")
    print(f"length: {len(seg)} symbols")
    print(f"   prime factors =: {factor.prime_factors(len(seg))}")
    print(f"   factor pairs  =: {factor.factor_pairs(len(seg))[1:-1]}")
    dist.print_dist(seg)
    entropy.shannon_entropy(seg)
    print_ioc_statistics(seg, alphabetsize=29)
    bigram_diagram.print_auto_bigram_diagram(seg, alphabet=c3301.CICADA_ALPHABET)
    print_kappa(seg, trace=False)
    print_kappa(seg, length=2, trace=False)
    print_kappa(seg, length=3, trace=False)
    friedman.friedman_test(seg, maxperiod=34)
    repeats.print_repeat_statistics(seg, minimum=2)
    repeats.print_repeat_positions(seg, minimum=5)
    krakup.print_krakup_analysis(seg, min_period=2, max_period=40, window_size=100, step=10)
