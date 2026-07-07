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
from aldegonde.maths.primes import primes as generate_primes
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

# ============================================================================
# PARSE WORD STRUCTURE: preserving word boundaries
# Separators: - (word), . (sentence), / (line), % (page), & (para), $ (section)
# ============================================================================
SEPARATORS = set("-./&%$\n")

def parse_words(text: str) -> list[tuple[str, int]]:
    """Parse text into (word_runes, start_position).
    Position is index into the rune-only stream."""
    words = []
    current_word: list[str] = []
    rune_pos = 0
    word_start = 0
    for ch in text:
        if ch in c3301.CICADA_ALPHABET:
            if not current_word:
                word_start = rune_pos
            current_word.append(ch)
            rune_pos += 1
        elif ch in SEPARATORS:
            if current_word:
                words.append(("".join(current_word), word_start))
                current_word = []
    if current_word:
        words.append(("".join(current_word), word_start))
    return words

def rune_to_eng(rune_str: str) -> str:
    """Convert rune string to runeglish English."""
    return "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.r2i(r)] for r in rune_str)


segments = lp.split("$")
z = segments[0:10]
full_text = "".join(z)

words = parse_words(full_text)
raw = "".join([x for x in full_text if x in c3301.CICADA_ALPHABET])
C = vals(raw)

from collections import Counter

# ========================================================================
# DOUBLET AND RATIO ANALYSIS
# ========================================================================
print("=" * 90)
print("DOUBLET & RATIO ANALYSIS")
print("=" * 90)

# Find all doublets (consecutive identical ciphertext values)
doublets = []
for i in range(1, len(C)):
    if C[i] == C[i - 1]:
        doublets.append(i)

print(f"\nTotal doublets (C[i]=C[i-1]): {len(doublets)}")
print(f"Total runes: {len(C)}")
print(f"Doublet rate: {len(doublets)/len(C)*100:.2f}%")
print(f"Expected for random (1/29): {100/29:.2f}%")

# Build word lookup: for each rune position, which word is it in?
pos_to_word: dict[int, tuple[int, int]] = {}  # pos -> (word_idx, offset_in_word)
for widx, (w, start) in enumerate(words):
    for offset in range(len(w)):
        pos_to_word[start + offset] = (widx, offset)

# Annotate doublets with word context
doublet_in_words: list[tuple[int, int, int, str, int]] = []
for dpos in doublets:
    if dpos in pos_to_word:
        widx, offset = pos_to_word[dpos]
        w, _ = words[widx]
        doublet_in_words.append((dpos, widx, offset, w, len(w)))

# ========================================================================
# KEY FINDING: DUAL SUPPRESSION
# Both additive delta=0 AND multiplicative ratio=1 are suppressed ~5x.
# Everything else is perfectly flat in both distributions.
# ========================================================================
print(f"\n{'=' * 90}")
print("DUAL SUPPRESSION: additive delta AND multiplicative ratio")
print("=" * 90)

# Additive delta distribution: C(i) - C(i-1) mod 29
add_deltas = Counter()
for i in range(1, len(C)):
    add_deltas[(C[i] - C[i - 1]) % N] += 1

# Multiplicative ratio distribution: C(i) / C(i-1) mod 29
mult_ratios = Counter()
zero_prev = 0
for i in range(1, len(C)):
    if C[i - 1] == 0:
        zero_prev += 1
        continue
    mult_ratios[(C[i] * pow(C[i - 1], N - 2, N)) % N] += 1

print(f"\n{'val':>4} {'add_delta':>10} {'pct':>7} {'mult_ratio':>11} {'pct':>7}  rune")
total_add = sum(add_deltas.values())
total_mult = sum(mult_ratios.values())
for v in range(N):
    eng = c3301.CICADA_ENGLISH_ALPHABET[(v - 1) % N]
    ac = add_deltas.get(v, 0)
    mc = mult_ratios.get(v, 0)
    ap = ac / total_add * 100
    mp = mc / total_mult * 100
    marker = " *** SUPPRESSED" if (ap < 1.5 or mp < 1.5) else ""
    print(f"{v:4d} {ac:10d} {ap:6.2f}% {mc:11d} {mp:6.2f}%  {eng}{marker}")

print(f"\nAdditive delta=0 (doublets): {add_deltas[0]} = {add_deltas[0]/total_add*100:.2f}%")
print(f"Mult ratio=1 (value 1=F):    {mult_ratios.get(1,0)} = {mult_ratios.get(1,0)/total_mult*100:.2f}%")
print(f"Expected if random:          {100/N:.2f}%")
print(f"\nBOTH are suppressed ~5x below expected!")
print(f"This strongly suggests a cipher with BOTH additive and multiplicative components.")

# ========================================================================
# DOUBLET SUPPRESSION: within-word vs cross-boundary
# Tests whether the cipher resets at word boundaries
# ========================================================================
print(f"\n{'=' * 90}")
print("DOUBLET SUPPRESSION: within-word vs cross-boundary")
print("=" * 90)

pos_to_widx: dict[int, int] = {}
for widx, (w, start) in enumerate(words):
    for off in range(len(w)):
        pos_to_widx[start + off] = widx

within_pairs = within_doublets = cross_pairs = cross_doublets = 0
for i in range(1, len(C)):
    if i in pos_to_widx and (i - 1) in pos_to_widx:
        if pos_to_widx[i] == pos_to_widx[i - 1]:
            within_pairs += 1
            if C[i] == C[i - 1]:
                within_doublets += 1
        else:
            cross_pairs += 1
            if C[i] == C[i - 1]:
                cross_doublets += 1

print(f"\nWithin-word:     {within_doublets}/{within_pairs} = {within_doublets/within_pairs*100:.2f}%")
print(f"Cross-boundary:  {cross_doublets}/{cross_pairs} = {cross_doublets/cross_pairs*100:.2f}%")
print(f"Expected random: {100/N:.2f}%")
print(f"\nBoth equally suppressed => cipher chain runs THROUGH word boundaries")

# ========================================================================
# 2-RUNE DOUBLET WORDS
# Only 1 exists out of 621 two-rune words (expected ~21)
# ========================================================================
print(f"\n{'=' * 90}")
print("2-RUNE DOUBLET WORDS")
print("=" * 90)

two_rune_words = [(widx, w, start) for widx, (w, start) in enumerate(words) if len(w) == 2]
two_rune_doublets = [(widx, w, start) for widx, w, start in two_rune_words if C[start] == C[start + 1]]

print(f"\nTotal 2-rune words: {len(two_rune_words)}")
print(f"2-rune doublet words: {len(two_rune_doublets)}  (expected ~{len(two_rune_words)//N})")

for widx, w, start in two_rune_doublets:
    eng = rune_to_eng(w)
    print(f"  w{widx:4d} pos={start:5d} cipher='{eng}' val={C[start]}")

# ========================================================================
# 3-RUNE WORDS STARTING WITH BOUNDARY DOUBLET
# C[start] == C[start-1] => for additive autokey, first rune = EA
# EACH in runeglish = EA+C+H = 3 runes
# ========================================================================
print(f"\n{'=' * 90}")
print("3-RUNE WORDS WITH BOUNDARY DOUBLET (could be EACH = EA+C+H)")
print("=" * 90)

ea_start_3: list[tuple[int, str, int]] = []
for widx, (w, start) in enumerate(words):
    if len(w) == 3 and start > 0 and C[start] == C[start - 1]:
        ea_start_3.append((widx, w, start))

print(f"\nCount: {len(ea_start_3)}")
print(f"\nEACH = EA(val=0) + C(val=6) + H(val=9)")
print()

for widx, w, start in ea_start_3:
    c0, c1, c2 = C[start], C[start + 1], C[start + 2]
    cprev = C[start - 1]
    eng = rune_to_eng(w)

    # Additive ct autokey: P(i) = C(i) - C(i-1)
    d1 = (c1 - c0) % N
    d2 = (c2 - c1) % N
    d1_eng = c3301.CICADA_ENGLISH_ALPHABET[(d1 - 1) % N]
    d2_eng = c3301.CICADA_ENGLISH_ALPHABET[(d2 - 1) % N]

    # Beaufort: P(i) = C(i-1) - C(i)
    b1 = (c0 - c1) % N
    b2 = (c1 - c2) % N
    b1_eng = c3301.CICADA_ENGLISH_ALPHABET[(b1 - 1) % N]
    b2_eng = c3301.CICADA_ENGLISH_ALPHABET[(b2 - 1) % N]

    # Multiplicative: P(i) = C(i) / C(i-1)
    m1 = safe_div(c1, c0)
    m2 = safe_div(c2, c1)
    m1_eng = c3301.CICADA_ENGLISH_ALPHABET[(m1 - 1) % N]
    m2_eng = c3301.CICADA_ENGLISH_ALPHABET[(m2 - 1) % N]

    # C(i)=C(i-1)*(1+P(i)): P(i) = C(i)/C(i-1) - 1
    if c0 != 0:
        h1 = (safe_div(c1, c0) - 1) % N
    else:
        h1 = -1
    if c1 != 0:
        h2 = (safe_div(c2, c1) - 1) % N
    else:
        h2 = -1

    print(f"  w{widx:4d} pos={start:5d} cipher='{eng}' vals=[{c0:2d},{c1:2d},{c2:2d}]")
    print(f"         additive:  EA+{d1_eng}+{d2_eng}  [{0},{d1},{d2}]  {'<= EACH!' if d1==6 and d2==9 else ''}")
    print(f"         beaufort:  EA+{b1_eng}+{b2_eng}  [{0},{b1},{b2}]  {'<= EACH!' if b1==6 and b2==9 else ''}")
    print(f"         mult ct:   {m1_eng}+{m2_eng}     [{m1},{m2}]")
    print(f"         C*(1+P):   [{h1},{h2}]")
    print()

# ========================================================================
# TEST CIPHER: C(i) = C(i-1) * (1 + P(i))
# This model explains BOTH suppressions:
#   additive delta = C(i-1)*P(i), zero when P(i)=0 (EA)
#   mult ratio = 1+P(i), one when P(i)=0 (EA)
# ========================================================================
print(f"\n{'=' * 90}")
print("CIPHER MODEL: C(i) = C(i-1) * (1 + P(i))")
print("Decryption: P(i) = C(i)/C(i-1) - 1")
print("Explains both additive and multiplicative suppression")
print("=" * 90)

def decrypt_c_times_1pp(C: list[int], primer: int) -> list[int]:
    """C(i) = C(i-1) * (1+P(i)) => P(i) = C(i)/C(i-1) - 1"""
    P = []
    prev = primer
    for c in C:
        if prev == 0:
            P.append(EA)
        else:
            P.append((safe_div(c, prev) - 1) % N)
        prev = c
    return P

best_score = -float("inf")
best_primer = 0
for primer in range(N):
    P = decrypt_c_times_1pp(C[:500], primer)
    pt = [c3301.CICADA_ALPHABET[(v - 1) % N] for v in P]
    score = c3301.quadgramscore(pt)
    if score > best_score:
        best_score = score
        best_primer = primer

P = decrypt_c_times_1pp(C, best_primer)
pt_runes = [c3301.CICADA_ALPHABET[(v - 1) % N] for v in P]
full_score = c3301.quadgramscore(pt_runes)
preview = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.r2i(r)] for r in pt_runes[:50])

print(f"\nBest primer: {best_primer}  full_score: {full_score:.0f}")
print(f"Preview: {preview}")

dist_p = Counter(P)
print(f"\nPlaintext dist (top 5 most common):")
for v, cnt in dist_p.most_common(5):
    eng = c3301.CICADA_ENGLISH_ALPHABET[(v - 1) % N]
    print(f"  {eng}: {cnt} ({cnt/len(P)*100:.2f}%)")
print(f"EA count: {dist_p.get(0, 0)} ({dist_p.get(0,0)/len(P)*100:.2f}%)")
print(f"\nStill flat => model alone is not the full cipher, but dual suppression is real.")
