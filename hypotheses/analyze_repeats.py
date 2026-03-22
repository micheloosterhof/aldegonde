# ABOUTME: Analysis of repeated n-grams in unsolved LP ciphertext.
# ABOUTME: Tests what repeats imply about cipher state and mechanism.

"""Analysis of repeated n-grams and their implications for cipher models.

A repeated ciphertext sequence constrains the cipher: under any cipher
C[i] = f(C[i-1], P[i], state[i]), a repeated sequence means the inputs
must be related. This script analyzes what those relationships are.
"""

from __future__ import annotations

import math
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "src")

from aldegonde import c3301

ALPHABET = c3301.CICADA_ALPHABET
ENG = c3301.CICADA_ENGLISH_ALPHABET
N = len(ALPHABET)


def load(filepath: str = "data/page0-58.txt") -> tuple[list[int], str]:
    """Load as (index_stream, raw_text)."""
    with open(filepath) as f:
        raw = f.read()
    indices = [c3301.r2i(c) for c in raw if c in ALPHABET]
    return indices, raw


def rune_pos_to_raw_pos(raw: str, rune_pos: int) -> int:
    """Map rune stream position to raw text position."""
    count = 0
    for i, ch in enumerate(raw):
        if ch in ALPHABET:
            if count == rune_pos:
                return i
            count += 1
    return len(raw)


def extract_raw_context(raw: str, rune_pos: int, before: int = 20, after: int = 20) -> str:
    """Get raw text context around a rune position."""
    raw_pos = rune_pos_to_raw_pos(raw, rune_pos)
    start = max(0, raw_pos - before)
    end = min(len(raw), raw_pos + after)
    return raw[start:end].replace("\n", "/")


def find_repeats(indices: list[int], min_n: int = 5, max_n: int = 10) -> dict[int, list[tuple[tuple[int, ...], list[int]]]]:
    """Find all repeated n-grams, grouped by n."""
    result: dict[int, list[tuple[tuple[int, ...], list[int]]]] = {}
    for n in range(min_n, max_n + 1):
        ngrams: dict[tuple[int, ...], list[int]] = defaultdict(list)
        for i in range(len(indices) - n + 1):
            gram = tuple(indices[i:i + n])
            ngrams[gram].append(i)
        repeats = [(k, v) for k, v in ngrams.items() if len(v) > 1]
        if repeats:
            result[n] = repeats
    return result


def expected_repeats(text_len: int, alphabet_size: int, n: int) -> float:
    """Expected number of repeated n-grams in random text."""
    num_positions = text_len - n + 1
    num_possible = alphabet_size ** n
    # Birthday approximation: E[collisions] ≈ C(m,2) / num_possible
    pairs = num_positions * (num_positions - 1) / 2
    return pairs / num_possible


def analyze_repeat_context(
    indices: list[int], raw: str, positions: list[int], gram_len: int,
) -> None:
    """Detailed analysis of a repeated n-gram at given positions."""
    gram = tuple(indices[positions[0]:positions[0] + gram_len])
    rune_str = "".join(c3301.i2r(g) for g in gram)
    eng_str = "".join(ENG[g] for g in gram)

    print(f"\n  Repeated {gram_len}-gram: {rune_str} [{eng_str}]")
    print(f"  Positions: {positions}, spacing: {positions[1] - positions[0]}")

    for occ_idx, pos in enumerate(positions):
        # Preceding rune
        if pos > 0:
            prev = indices[pos - 1]
            prev_str = f"{c3301.i2r(prev)}({ENG[prev]}, idx={prev})"
        else:
            prev_str = "(start)"

        # Following rune
        end = pos + gram_len
        if end < len(indices):
            foll = indices[end]
            foll_str = f"{c3301.i2r(foll)}({ENG[foll]}, idx={foll})"
        else:
            foll_str = "(end)"

        # Raw context with word boundaries
        ctx = extract_raw_context(raw, pos, before=15, after=gram_len * 3 + 10)

        print(f"\n  Occurrence {occ_idx + 1} at position {pos}:")
        print(f"    Preceding: {prev_str}")
        print(f"    Following: {foll_str}")
        print(f"    Raw context: ...{ctx}...")

    # Check if preceding rune matches
    prevs = [indices[p - 1] if p > 0 else -1 for p in positions]
    if prevs[0] == prevs[1]:
        print(f"\n  Preceding rune MATCHES: {c3301.i2r(prevs[0])}")
        print("  => Under any f(C[i-1], P[i]) cipher, plaintext is IDENTICAL")
        print("     at both occurrences for the ENTIRE repeat.")
    else:
        print(f"\n  Preceding rune DIFFERS: {c3301.i2r(prevs[0])} vs {c3301.i2r(prevs[1])}")
        print("  => Under f(C[i-1], P[i]) cipher, plaintext DIFFERS at")
        print("     position 0 but is IDENTICAL from position 1 onwards")
        print("     (because C[i-1] is inside the repeat from that point).")

    # Decrypt under standard Beaufort/Vigenere autokey (for reference)
    print(f"\n  Decryption under standard Beaufort autokey (disproved, for reference):")
    for occ_idx, pos in enumerate(positions):
        pt = []
        for j in range(gram_len):
            i = pos + j
            prev_c = indices[i - 1] if i > 0 else 0
            p = (prev_c - indices[i]) % N
            pt.append(p)
        eng_dec = "".join(ENG[p] for p in pt)
        print(f"    Occ {occ_idx + 1}: {eng_dec} (indices: {pt})")

    # Word boundary analysis
    print(f"\n  Word boundary analysis:")
    for occ_idx, pos in enumerate(positions):
        raw_pos = rune_pos_to_raw_pos(raw, pos)
        # Walk back to find word start
        word_start = raw_pos
        while word_start > 0 and raw[word_start - 1] in ALPHABET:
            word_start -= 1
        # Extract words overlapping the repeat
        raw_end = rune_pos_to_raw_pos(raw, pos + gram_len - 1)
        while raw_end < len(raw) - 1 and raw[raw_end + 1] in ALPHABET:
            raw_end += 1
        fragment = raw[word_start:raw_end + 1]
        # Split into words
        words = re.split(r'[^' + ''.join(ALPHABET) + r']+', fragment)
        words = [w for w in words if w]
        word_lens = [len(w) for w in words]
        word_engs = [
            "".join(ENG[c3301.r2i(c)] for c in w)
            for w in words
        ]
        print(f"    Occ {occ_idx + 1}: words={word_engs}, lengths={word_lens}")


def state_propagation_analysis(
    indices: list[int], pos_a: int, pos_b: int, gram_len: int,
) -> None:
    """Analyze how state differences propagate through the repeat.

    Under C[i] = C[i-1] - P[i] * k(state), if the state differs at
    position 0 of the repeat, how does the difference propagate?
    """
    print(f"\n  State propagation analysis:")
    print(f"  Under C[i] = C[i-1] - P[i] * k(state[i]) mod {N}:")

    prev_a = indices[pos_a - 1] if pos_a > 0 else 0
    prev_b = indices[pos_b - 1] if pos_b > 0 else 0

    if prev_a == prev_b:
        print("  Preceding rune matches. Under f(C[i-1], P[i]):")
        print("  All positions have identical plaintext. No constraint on extra state.")
        return

    print(f"  C[{pos_a}-1] = {prev_a} ({ENG[prev_a]}), "
          f"C[{pos_b}-1] = {prev_b} ({ENG[prev_b]})")

    # Under plain Beaufort: P = (C[i-1] - C[i]) mod N
    p_a0 = (prev_a - indices[pos_a]) % N
    p_b0 = (prev_b - indices[pos_b]) % N
    print(f"\n  Position 0 (first rune of repeat):")
    print(f"    Under Beaufort: P_a = {ENG[p_a0]} ({p_a0}), P_b = {ENG[p_b0]} ({p_b0})")
    print(f"    Plaintext DIFFERS (different C[i-1], same C[i])")

    print(f"\n  If state[i] depends on P[i-1] (prev plaintext):")
    print(f"    state_a[1] = f(P_a[0]) = f({ENG[p_a0]})")
    print(f"    state_b[1] = f(P_b[0]) = f({ENG[p_b0]})")
    print(f"    States differ at position 1 => P[1] may also differ")
    print(f"    => Difference can propagate through entire repeat")
    print(f"    For same ciphertext with different states:")
    print(f"    P_a[j] * k(state_a[j]) = P_b[j] * k(state_b[j]) at each position j")
    print(f"    This is a chain of equations in GF(29) that must hold simultaneously.")

    print(f"\n  If state[i] depends on C[i-1] only (disproved single-autokey):")
    print(f"    From position 1 onwards, C[i-1] matches => P matches")
    print(f"    Only position 0 differs")

    print(f"\n  If state[i] depends on C[i-1] and C[i-2]:")
    prev2_a = indices[pos_a - 2] if pos_a > 1 else 0
    prev2_b = indices[pos_b - 2] if pos_b > 1 else 0
    print(f"    C[i-2]: {ENG[prev2_a]} vs {ENG[prev2_b]} — "
          f"{'MATCH' if prev2_a == prev2_b else 'DIFFER'}")
    if prev2_a != prev2_b:
        print(f"    Positions 0 and 1 may have different state => different P")
        print(f"    From position 2 onwards: C[i-1] and C[i-2] both match => P matches")

    print(f"\n  If state[i] depends on running sum of ciphertext:")
    sum_a = sum(indices[max(0, pos_a - 100):pos_a]) % N
    sum_b = sum(indices[max(0, pos_b - 100):pos_b]) % N
    print(f"    Running sums at start: {sum_a} vs {sum_b} — "
          f"{'MATCH' if sum_a == sum_b else 'DIFFER'}")
    if sum_a != sum_b:
        diff = (sum_a - sum_b) % N
        print(f"    Difference: {diff}")
        print(f"    Running sum diverges by a constant throughout the repeat")
        print(f"    Every position has different state => every position may have different P")


def main() -> None:
    indices, raw = load()
    n = len(indices)
    print(f"Ciphertext: {n} runes")

    # Expected repeats under random model
    print(f"\n{'Expected vs observed repeats':=^70}")
    for ngram_len in range(5, 9):
        expected = expected_repeats(n, N, ngram_len)
        print(f"  {ngram_len}-gram: expected {expected:.2f} repeats in random text")

    # Find actual repeats
    repeats = find_repeats(indices, min_n=5, max_n=8)

    for ngram_len in sorted(repeats.keys()):
        grams = repeats[ngram_len]
        print(f"\n{'=' * 70}")
        print(f"REPEATED {ngram_len}-GRAMS: {len(grams)} found")
        print(f"{'=' * 70}")

        for gram, positions in grams:
            analyze_repeat_context(indices, raw, positions, ngram_len)
            if len(positions) == 2:
                state_propagation_analysis(indices, positions[0], positions[1], ngram_len)

    # Special analysis: the big 7-gram repeat
    print(f"\n{'=' * 70}")
    print("DEEP ANALYSIS: 7-gram repeat ᛞᛄᚢᛒᛖᛁᚫ")
    print(f"{'=' * 70}")

    pos_a, pos_b = 6555, 12950

    # What section/page are these in?
    # Count page breaks (&) before each position
    rune_count = 0
    pages_a, pages_b = 0, 0
    sections_a, sections_b = 0, 0
    for ch in raw:
        if ch in ALPHABET:
            rune_count += 1
        elif ch == '&':
            if rune_count <= pos_a:
                pages_a += 1
            if rune_count <= pos_b:
                pages_b += 1
        elif ch == '$':
            if rune_count <= pos_a:
                sections_a += 1
            if rune_count <= pos_b:
                sections_b += 1

    print(f"\n  Position {pos_a}: after page break #{pages_a}, section #{sections_a}")
    print(f"  Position {pos_b}: after page break #{pages_b}, section #{sections_b}")

    # Extended context (±20 runes as English)
    for pos, label in [(pos_a, "A"), (pos_b, "B")]:
        start = max(0, pos - 10)
        end = min(n, pos + 17)
        ctx_eng = "".join(ENG[indices[i]] for i in range(start, end))
        ctx_runes = "".join(c3301.i2r(indices[i]) for i in range(start, end))
        marker = pos - start
        print(f"\n  Context {label} (pos {pos}):")
        print(f"    Runes:   {ctx_runes[:marker]}[{ctx_runes[marker:marker+7]}]{ctx_runes[marker+7:]}")
        print(f"    English: {ctx_eng[:marker]}[{ctx_eng[marker:marker+7]}]{ctx_eng[marker+7:]}")
        print(f"    Raw:     ...{extract_raw_context(raw, pos, 20, 30)}...")

    # Try all 29 offsets for Beaufort and report the plaintext
    print(f"\n  Plaintext of the overlapping 6 inner runes (pos 1-6 of repeat)")
    print(f"  under Beaufort autokey with various offsets:")
    print(f"  These 6 runes decrypt identically at both occurrences")
    print(f"  regardless of offset (C[i-1] matches from position 1).\n")

    inner_ct = [indices[pos_a + j] for j in range(1, 7)]
    inner_prev = [indices[pos_a + j - 1] for j in range(1, 7)]
    # These are inside the repeat, so C[i-1] is always the previous repeat rune

    for offset in range(N):
        pt = [(prev - c + offset) % N for prev, c in zip(inner_prev, inner_ct)]
        eng = "".join(ENG[p] for p in pt)
        # Check if it could be English
        has_common = any(ENG[p] in ("E", "T", "A", "O", "I", "N", "S", "H", "R") for p in pt)
        marker = " <--" if eng.replace("TH", "T").replace("NG", "N").replace("EA", "E").isalpha() else ""
        print(f"    offset={offset:2d}: {eng}{marker}")


if __name__ == "__main__":
    main()
