#!/usr/bin/env python3

"""
Liber Primus analysis: GF(29) multiplicative/mixed autokey exploration.
Uses 1-based indexing where EA rune = 29 % 29 = 0.

Explores cipher variants mixing addition and multiplication in GF(29),
including ciphertext autokey, plaintext autokey, and mixed feedback.

On division by zero (EA rune, value 0), falls back to EA since it lives
outside the multiplicative group GF(29)*.
"""

from aldegonde import c3301
from aldegonde.stats import print_ioc_statistics, print_kappa
from aldegonde.stats import repeats, dist, entropy
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor
from aldegonde.analysis import friedman, krakup

N = 29  # GF(29)
EA = 0  # EA rune value (29 % 29 = 0), fallback for div-by-zero


def val(rune: str) -> int:
    """Convert rune to 1-based value in GF(29). EA = 0."""
    return (c3301.r2i(rune) + 1) % N


def rune(v: int) -> str:
    """Convert GF(29) value back to rune."""
    return c3301.CICADA_ALPHABET[(v - 1) % N]


def inv(a: int) -> int:
    """Multiplicative inverse in GF(29). Returns 0 for a=0 (EA fallback)."""
    if a == 0:
        return EA
    return pow(a, N - 2, N)  # Fermat's little theorem


def safe_div(a: int, b: int) -> int:
    """a / b in GF(29). Falls back to EA (0) when b = 0."""
    if b == 0:
        return EA
    return (a * pow(b, N - 2, N)) % N


def vals(text: str) -> list[int]:
    """Convert rune string to list of GF(29) values."""
    return [val(r) for r in text]


def runes(values: list[int]) -> str:
    """Convert list of GF(29) values back to rune string."""
    return "".join(rune(v) for v in values)


# ============================================================================
# CIPHER VARIANT DECRYPTION FUNCTIONS
# Each returns a list of plaintext values given ciphertext values and primers.
# On division by zero, falls back to EA (value 0) instead of aborting.
# ============================================================================

# --- Additive autokeys (no division needed) ---

def decrypt_additive_ct_autokey(C: list[int], primer_c: int) -> list[int]:
    """C(i) = P(i) + C(i-1)  =>  P(i) = C(i) - C(i-1)"""
    P = []
    prev_c = primer_c
    for c in C:
        P.append((c - prev_c) % N)
        prev_c = c
    return P


def decrypt_beaufort_ct_autokey(C: list[int], primer_c: int) -> list[int]:
    """C(i) = C(i-1) - P(i)  =>  P(i) = C(i-1) - C(i)"""
    P = []
    prev_c = primer_c
    for c in C:
        P.append((prev_c - c) % N)
        prev_c = c
    return P


def decrypt_additive_pt_autokey(C: list[int], primer_p: int) -> list[int]:
    """C(i) = P(i) + P(i-1)  =>  P(i) = C(i) - P(i-1)"""
    P = []
    prev_p = primer_p
    for c in C:
        p = (c - prev_p) % N
        P.append(p)
        prev_p = p
    return P


def decrypt_beaufort_pt_autokey(C: list[int], primer_p: int) -> list[int]:
    """C(i) = P(i-1) - P(i)  =>  P(i) = P(i-1) - C(i)"""
    P = []
    prev_p = primer_p
    for c in C:
        p = (prev_p - c) % N
        P.append(p)
        prev_p = p
    return P


# --- Multiplicative autokeys (EA fallback on div-by-zero) ---

def decrypt_mult_ct_autokey(C: list[int], primer_c: int) -> list[int]:
    """C(i) = P(i) * C(i-1)  =>  P(i) = C(i) / C(i-1)"""
    P = []
    prev_c = primer_c
    for c in C:
        P.append(safe_div(c, prev_c))
        prev_c = c
    return P


def decrypt_mult_pt_autokey(C: list[int], primer_p: int) -> list[int]:
    """C(i) = P(i) * P(i-1)  =>  P(i) = C(i) / P(i-1)"""
    P = []
    prev_p = primer_p
    for c in C:
        p = safe_div(c, prev_p)
        P.append(p)
        prev_p = p
    return P


# --- Mixed additive + multiplicative with two primers ---

def decrypt_pp_plus_c(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i)*P(i-1) + C(i-1)  =>  P(i) = (C(i)-C(i-1)) / P(i-1)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div((c - prev_c) % N, prev_p)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_plus_cp(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i) + C(i-1)*P(i-1)  =>  P(i) = C(i) - C(i-1)*P(i-1)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = (c - prev_c * prev_p) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_pc_plus_p(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i)*C(i-1) + P(i-1)  =>  P(i) = (C(i)-P(i-1)) / C(i-1)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div((c - prev_p) % N, prev_c)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_times_c_plus_p(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i)*(C(i-1)+P(i-1))  =>  P(i) = C(i) / (C(i-1)+P(i-1))"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div(c, (prev_c + prev_p) % N)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_times_c_minus_p(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i)*(C(i-1)-P(i-1))  =>  P(i) = C(i) / (C(i-1)-P(i-1))"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div(c, (prev_c - prev_p) % N)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_cp_minus_p(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = C(i-1)*P(i-1) - P(i)  =>  P(i) = C(i-1)*P(i-1) - C(i)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = (prev_c * prev_p - c) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_pp_times_c(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i)*P(i-1)*C(i-1)  =>  P(i) = C(i) / (P(i-1)*C(i-1))"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div(c, (prev_p * prev_c) % N)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


# --- Additional mixed variants ---

def decrypt_p_plus_c_times_c(C: list[int], primer_c: int) -> list[int]:
    """C(i) = P(i) + C(i-1)*C(i-2)  =>  P(i) = C(i) - C(i-1)*C(i-2)"""
    P = []
    prev_c2 = EA
    prev_c1 = primer_c
    for c in C:
        p = (c - prev_c1 * prev_c2) % N
        P.append(p)
        prev_c2 = prev_c1
        prev_c1 = c
    return P


def decrypt_p_times_c_plus_c(C: list[int], primer_c: int) -> list[int]:
    """C(i) = P(i)*C(i-1) + C(i-2)  =>  P(i) = (C(i)-C(i-2)) / C(i-1)"""
    P = []
    prev_c2 = EA
    prev_c1 = primer_c
    for c in C:
        p = safe_div((c - prev_c2) % N, prev_c1)
        P.append(p)
        prev_c2 = prev_c1
        prev_c1 = c
    return P


def decrypt_pc_plus_cp(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i)*C(i-1) + C(i-1)*P(i-1)  =>  C(i) = C(i-1)*(P(i)+P(i-1))
       P(i)+P(i-1) = C(i)/C(i-1)  =>  P(i) = C(i)/C(i-1) - P(i-1)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = (safe_div(c, prev_c) - prev_p) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_times_pp(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i)*(P(i-1)+C(i-1))  =>  P(i) = C(i) / (P(i-1)+C(i-1))
       Same as decrypt_p_times_c_plus_p but listing explicitly for clarity."""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div(c, (prev_p + prev_c) % N)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_cp_plus_pp(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = C(i-1)*P(i) + P(i)*P(i-1) = P(i)*(C(i-1)+P(i-1))
       => P(i) = C(i) / (C(i-1)+P(i-1))"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div(c, (prev_c + prev_p) % N)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_c_times_p_plus_p(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = C(i-1)*P(i-1) + P(i)  =>  P(i) = C(i) - C(i-1)*P(i-1)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = (c - prev_c * prev_p) % N
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_plus_pp(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i) + P(i-1)*P(i-1)  =>  P(i) = C(i) - P(i-1)^2
       Uses plaintext autokey with quadratic feedback."""
    P = []
    prev_p = primer_p
    for c in C:
        p = (c - prev_p * prev_p) % N
        P.append(p)
        prev_p = p
    return P


def decrypt_c_plus_pp(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = C(i-1) + P(i)*P(i-1)  [user's suggestion]
       P(i)*P(i-1) = C(i) - C(i-1)
       P(i) = (C(i)-C(i-1)) / P(i-1)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div((c - prev_c) % N, prev_p)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_c_minus_pp(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = C(i-1) - P(i)*P(i-1)
       P(i)*P(i-1) = C(i-1) - C(i)
       P(i) = (C(i-1)-C(i)) / P(i-1)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div((prev_c - c) % N, prev_p)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_pp_minus_c(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i)*P(i-1) - C(i-1)
       P(i)*P(i-1) = C(i) + C(i-1)
       P(i) = (C(i)+C(i-1)) / P(i-1)"""
    P = []
    prev_c = primer_c
    prev_p = primer_p
    for c in C:
        p = safe_div((c + prev_c) % N, prev_p)
        P.append(p)
        prev_c = c
        prev_p = p
    return P


def decrypt_p_plus_c_times_p(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i) + C(i-1)*P(i)  = P(i)*(1+C(i-1))
       P(i) = C(i) / (1+C(i-1))"""
    P = []
    prev_c = primer_c
    for c in C:
        p = safe_div(c, (1 + prev_c) % N)
        P.append(p)
        prev_c = c
    return P


def decrypt_p_times_1_plus_p(C: list[int], primer_p: int) -> list[int]:
    """C(i) = P(i) * (1 + P(i-1))  =>  P(i) = C(i) / (1 + P(i-1))"""
    P = []
    prev_p = primer_p
    for c in C:
        p = safe_div(c, (1 + prev_p) % N)
        P.append(p)
        prev_p = p
    return P


def decrypt_p_times_c(C: list[int], primer_c: int, primer_p: int) -> list[int]:
    """C(i) = P(i) * C(i-1) (pure multiplicative ct autokey, 2-primer version)
       P(i) = C(i) / C(i-1)"""
    P = []
    prev_c = primer_c
    for c in C:
        p = safe_div(c, prev_c)
        P.append(p)
        prev_c = c
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
    print("PHASE 1: SINGLE-PRIMER GF(29) VARIANTS")
    print("EA fallback: div-by-zero => EA (val 0, outside GF(29)*)")
    print("=" * 90)

    results: list[tuple[float, str, int, str]] = []

    single_primer_funcs_ct: list[tuple[str, object]] = [
        ("P+Ci-1 (add ct)", decrypt_additive_ct_autokey),
        ("Ci-1-P (beau ct)", decrypt_beaufort_ct_autokey),
        ("P*Ci-1 (mult ct)", decrypt_mult_ct_autokey),
        ("P+Ci-1*Ci-2", decrypt_p_plus_c_times_c),
        ("P*Ci-1+Ci-2", decrypt_p_times_c_plus_c),
    ]
    single_primer_funcs_pt: list[tuple[str, object]] = [
        ("P+Pi-1 (add pt)", decrypt_additive_pt_autokey),
        ("Pi-1-P (beau pt)", decrypt_beaufort_pt_autokey),
        ("P*Pi-1 (mult pt)", decrypt_mult_pt_autokey),
        ("P*(1+Pi-1)", decrypt_p_times_1_plus_p),
    ]

    for name, func in single_primer_funcs_ct:
        for pv in range(N):
            pt = runes(func(C, pv))
            score = c3301.quadgramscore(pt)
            results.append((score, name, pv, pt))

    for name, func in single_primer_funcs_pt:
        for pv in range(N):
            pt = runes(func(C, pv))
            score = c3301.quadgramscore(pt)
            results.append((score, name, pv, pt))

    results.sort(key=lambda x: x[0], reverse=True)

    print(f"\n{'Rank':>4} {'Score':>10} {'Variant':<20} {'Primer':>6} {'Decrypted (first 60 runeglish)'}")
    print("-" * 110)
    for rank, (score, name, pv, pt) in enumerate(results[:40], 1):
        pt_eng = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.r2i(r)] for r in pt[:60])
        print(f"{rank:4d} {score:10.2f} {name:<20} {pv:>6} {pt_eng}")

    # ========================================================================
    # PHASE 2: Two-primer variants (29x29 = 841 trials each)
    # All with EA fallback on div-by-zero
    # ========================================================================
    print("\n" + "=" * 90)
    print("PHASE 2: TWO-PRIMER GF(29) MIXED VARIANTS (841 trials each)")
    print("EA fallback: div-by-zero => EA (val 0, outside GF(29)*)")
    print("=" * 90)

    results2: list[tuple[float, str, int, int, str]] = []

    two_primer_funcs = [
        # User's suggestion and variations
        ("C+P*Pi-1", decrypt_c_plus_pp),         # C(i) = C(i-1) + P(i)*P(i-1)
        ("C-P*Pi-1", decrypt_c_minus_pp),         # C(i) = C(i-1) - P(i)*P(i-1)
        ("P*Pi-1-C", decrypt_pp_minus_c),         # C(i) = P(i)*P(i-1) - C(i-1)
        ("P*Pi-1+C", decrypt_pp_plus_c),          # C(i) = P(i)*P(i-1) + C(i-1)
        # Mixed additive + multiplicative
        ("P+C*Pi-1", decrypt_p_plus_cp),          # C(i) = P(i) + C(i-1)*P(i-1)
        ("C*Pi-1+P", decrypt_c_times_p_plus_p),   # C(i) = C(i-1)*P(i-1) + P(i)
        ("C*Pi-1-P", decrypt_cp_minus_p),         # C(i) = C(i-1)*P(i-1) - P(i)
        ("P*C+Pi-1", decrypt_pc_plus_p),          # C(i) = P(i)*C(i-1) + P(i-1)
        # Multiplicative with sum/diff key
        ("P*(C+Pi-1)", decrypt_p_times_c_plus_p), # C(i) = P(i)*(C(i-1)+P(i-1))
        ("P*(C-Pi-1)", decrypt_p_times_c_minus_p),# C(i) = P(i)*(C(i-1)-P(i-1))
        # Triple products
        ("P*Pi-1*C", decrypt_pp_times_c),         # C(i) = P(i)*P(i-1)*C(i-1)
        # Factored forms
        ("C*(P+Pi-1)", decrypt_pc_plus_cp),       # C(i) = C(i-1)*(P(i)+P(i-1))
        # Quadratic feedback
        ("P+Pi-1^2", decrypt_p_plus_pp),          # C(i) = P(i) + P(i-1)^2
        # P with scaled ct
        ("P+C*P", decrypt_p_plus_c_times_p),      # C(i) = P(i)*(1+C(i-1))
    ]

    for func_name, func in two_primer_funcs:
        for pc in range(N):
            for pp in range(N):
                pt = runes(func(C, pc, pp))
                score = c3301.quadgramscore(pt)
                results2.append((score, func_name, pc, pp, pt))

    results2.sort(key=lambda x: x[0], reverse=True)

    print(f"\n{'Rank':>4} {'Score':>10} {'Variant':<18} {'Pc':>3} {'Pp':>3} {'Decrypted (first 60 runeglish)'}")
    print("-" * 120)
    for rank, (score, name, pc, pp, pt) in enumerate(results2[:60], 1):
        pt_eng = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.r2i(r)] for r in pt[:60])
        print(f"{rank:4d} {score:10.2f} {name:<18} {pc:>3} {pp:>3} {pt_eng}")

    # ========================================================================
    # PHASE 3: Full analysis on overall best
    # ========================================================================
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
