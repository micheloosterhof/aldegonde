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
# DOUBLET ANALYSIS
# In additive ct autokey: C(i) = P(i) + C(i-1)  =>  P(i) = C(i) - C(i-1)
# When C(i) = C(i-1) (doublet), P(i) = 0 = EA.
# So ciphertext doublets pin P(i) = EA for additive autokey.
#
# For Beaufort: P(i) = C(i-1) - C(i), doublet => P(i) = 0 = EA. Same.
#
# For multiplicative ct autokey: C(i) = P(i) * C(i-1)
#   P(i) = C(i) / C(i-1). When C(i)=C(i-1), P(i) = 1 (not 0).
#   So doublet => P(i) = 1 for multiplicative.
#
# For C(i) = C(i-1) + P(i)*P(i-1):
#   P(i)*P(i-1) = C(i) - C(i-1) = 0 when doublet
#   So either P(i)=0 (EA) or P(i-1)=0 (EA) at doublets.
#
# This means: at every doublet, we know the plaintext or get a
# strong constraint. We can check if the word boundaries are
# consistent with EA appearing at those positions.
# ========================================================================
print("=" * 90)
print("DOUBLET ANALYSIS: C(i) = C(i-1) implies P(i) = EA for additive autokey")
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

# For each word, check if any doublet position falls inside it.
# If it does, and it's additive autokey, then that position in
# the decrypted word = EA.
print(f"\n--- Where do doublets land in words? ---")
print("(For additive autokey, doublet pos => plaintext EA at that pos)")

# Build word lookup: for each rune position, which word is it in?
pos_to_word: dict[int, tuple[int, int]] = {}  # pos -> (word_idx, offset_in_word)
for widx, (w, start) in enumerate(words):
    for offset in range(len(w)):
        pos_to_word[start + offset] = (widx, offset)

# Annotate doublets with word context
doublet_in_words: list[tuple[int, int, int, str, int]] = []  # (pos, word_idx, offset, word, word_len)
for dpos in doublets:
    if dpos in pos_to_word:
        widx, offset = pos_to_word[dpos]
        w, _ = words[widx]
        doublet_in_words.append((dpos, widx, offset, w, len(w)))

# How many doublets fall at word boundaries?
doublet_at_word_start = sum(1 for _, _, off, _, _ in doublet_in_words if off == 0)
doublet_at_word_end = sum(1 for _, _, off, _, wl in doublet_in_words if off == wl - 1)
doublet_at_word_mid = len(doublet_in_words) - doublet_at_word_start - doublet_at_word_end

print(f"\nDoublets at word start (offset 0): {doublet_at_word_start}")
print(f"Doublets at word end (last pos):   {doublet_at_word_end}")
print(f"Doublets at word middle:           {doublet_at_word_mid}")

# For additive autokey: doublet means EA at that position.
# EA is the 29th rune (index 28). In runeglish it maps to 'EA'.
# If EA appears at start of a word, the word starts with 'EA'.
# If EA appears mid-word, the word contains 'EA'.
# 'EA' is actually common in English: EACH, FEAR, HEART, NEAR, etc.
# And EA as a rune represents the phoneme /ea/ in runeglish.

# Show the word context for first 50 doublets
print(f"\nFirst 50 doublets with word context:")
print(f"{'Pos':>6} {'C[i]':>5} {'WIdx':>5} {'Off':>4} {'WLen':>5} {'Cipher word':<20} {'If additive: EA at off'}")
print("-" * 80)
for dpos, widx, offset, w, wl in doublet_in_words[:50]:
    eng = rune_to_eng(w)
    # Show what the word looks like with EA inserted at offset
    ea_marker = eng[:offset*2] + "[EA]" + eng[(offset+1)*2:]  # approximate
    print(f"{dpos:6d} {C[dpos]:5d} {widx:5d} {offset:4d} {wl:5d} {eng:<20} EA at position {offset}")

# ========================================================================
# KEY INSIGHT: For multiplicative mixed autokey like C(i) = C(i-1) + P(i)*P(i-1):
# Doublet => P(i)*P(i-1) = 0  =>  P(i)=EA OR P(i-1)=EA
# So at a doublet, one of two adjacent plaintext positions is EA.
# If we have consecutive doublets (triplet in ciphertext),
# then we know both positions are EA.
# ========================================================================

# Find triplets (3+ consecutive identical values)
triplets = []
i = 0
while i < len(C) - 2:
    if C[i] == C[i+1] == C[i+2]:
        start = i
        while i < len(C) - 1 and C[i] == C[i+1]:
            i += 1
        triplets.append((start, i + 1))  # (start, end_exclusive)
    else:
        i += 1

print(f"\n\nTriplets (3+ consecutive identical): {len(triplets)}")
for start, end in triplets[:20]:
    length = end - start
    if start in pos_to_word:
        widx, off = pos_to_word[start]
        w, _ = words[widx]
        eng = rune_to_eng(w)
        print(f"  pos={start}-{end-1} len={length} val={C[start]} word={eng}")

# ========================================================================
# DOUBLET POSITION ANALYSIS WITHIN WORDS
# For C(i) = C(i-1) + P(i)*P(i-1), doublet => P(i)*P(i-1) = 0.
# In a word of length L, if doublet at offset k (1<=k<L):
#   P(k)=EA or P(k-1)=EA
# If word has no doublets, no EA in word (likely for short common words).
# ========================================================================

# Count words with/without doublets
words_with_doublets = set()
for dpos, widx, offset, w, wl in doublet_in_words:
    words_with_doublets.add(widx)

print(f"\n\nWords containing a doublet: {len(words_with_doublets)} of {len(words)}")
print(f"Words WITHOUT any doublet: {len(words) - len(words_with_doublets)}")

# Short words without doublets - these have NO EA in the plaintext
# (for the C(i) = C(i-1) + P(i)*P(i-1) model)
no_doublet_1 = [(w, pos) for i, (w, pos) in enumerate(words) if len(w) == 1 and i not in words_with_doublets]
no_doublet_2 = [(w, pos) for i, (w, pos) in enumerate(words) if len(w) == 2 and i not in words_with_doublets]

print(f"\n1-rune words with NO doublet (no EA constraint): {len(no_doublet_1)}")
for w, pos in no_doublet_1:
    eng = rune_to_eng(w)
    v = val(w)
    print(f"  pos={pos:5d} cipher={eng} val={v}")

print(f"\n2-rune words with NO doublet: {len(no_doublet_2)} (showing first 20)")
for w, pos in no_doublet_2[:20]:
    eng = rune_to_eng(w)
    v = [val(r) for r in w]
    print(f"  pos={pos:5d} cipher={eng} vals={v}")

# ========================================================================
# EA POSITION MAP: For additive autokey, map where EA must appear
# ========================================================================
print(f"\n\n{'=' * 90}")
print("EA POSITION MAP (additive ct autokey: doublet => P[i] = EA)")
print("Show how EA falls within word boundaries")
print("=" * 90)

# For each word, show its plaintext pattern with EA marked
print(f"\nFirst 100 words with EA annotations:")
for widx in range(min(100, len(words))):
    w, start = words[widx]
    eng = rune_to_eng(w)
    # Build pattern: show which positions are pinned to EA
    pattern = list(eng)
    ea_positions_in_word = []
    for dpos, dwidx, offset, _, _ in doublet_in_words:
        if dwidx == widx:
            ea_positions_in_word.append(offset)
    if ea_positions_in_word:
        # Build display with EA marked
        display = ""
        for j, r in enumerate(w):
            if j in ea_positions_in_word:
                display += "[EA]"
            else:
                display += rune_to_eng(r)
        print(f"  w{widx:4d} pos={start:5d} len={len(w):2d} cipher={eng:<15} pattern={display}")

# ========================================================================
# MULTIPLICATIVE ANALYSIS: C(i)=C(i-1)+P(i)*P(i-1)
# Doublet at pos i => P(i)*P(i-1) = 0 => P(i)=EA or P(i-1)=EA
# Check consistency: if word starts at a doublet (offset 0),
# then P(0) of word = EA, or last rune of previous word = EA.
# ========================================================================
print(f"\n\n{'=' * 90}")
print("MULTIPLICATIVE MIXED AUTOKEY: C(i) = C(i-1) + P(i)*P(i-1)")
print("Doublet => P(i)*P(i-1) = 0 => P(i)=EA OR P(i-1)=EA")
print("=" * 90)

# For this model, we can try to propagate EA assignments.
# At each doublet, either current or previous position is EA.
# If a word starts with a doublet and the previous word ends with EA,
# that's consistent. Otherwise the first rune of the word = EA.

# Let's analyze: given word boundaries, how many assignments are forced?
# Start with doublets and see which are at word boundaries
print("\nDoublets at word starts (first rune of word):")
boundary_doublets = [(dpos, widx, offset, w, wl) for dpos, widx, offset, w, wl in doublet_in_words if offset == 0]
print(f"  Count: {len(boundary_doublets)}")
for dpos, widx, offset, w, wl in boundary_doublets[:20]:
    eng = rune_to_eng(w)
    # Previous word
    if widx > 0:
        pw, pstart = words[widx - 1]
        peng = rune_to_eng(pw)
        print(f"  pos={dpos:5d} word='{eng}' prev_word='{peng}' => '{eng}' starts with EA, or '{peng}' ends with EA")
