#!/usr/bin/env python3
"""
Targeted EA hypothesis testing.

If a doublet in ciphertext corresponds to EA in plaintext, what cipher
mechanism would produce this? Test various models.

Also: test if doublets are the result of a specific plaintext rune
being encrypted, by checking what the "doublet-causing" plaintext rune
would need to be under various cipher models.
"""

import sys
import math
from collections import Counter, defaultdict

sys.path.insert(0, "src")

from aldegonde import c3301, pasc, auto


def load_and_clean(filepath: str) -> str:
    with open(filepath) as f:
        return f.read()


def clean_runes(text: str) -> str:
    return "".join(c for c in text if c in c3301.CICADA_ALPHABET)


def get_words(text: str) -> list[str]:
    import re
    words = re.split(r'[^' + ''.join(c3301.CICADA_ALPHABET) + r']+', text)
    return [w for w in words if len(w) > 0]


def main() -> None:
    lp_text = load_and_clean("data/page0-58.txt")
    runes = clean_runes(lp_text)
    words = get_words(lp_text)

    EA = "ᛠ"  # index 28
    ALPHABET = c3301.CICADA_ALPHABET

    print("=" * 70)
    print("EA HYPOTHESIS - DETAILED INVESTIGATION")
    print("=" * 70)

    # ================================================================
    # 1. DOUBLET AS IDENTITY ELEMENT TEST
    # ================================================================
    print("\n" + "=" * 70)
    print("1. DOUBLET-IDENTITY HYPOTHESIS")
    print("=" * 70)
    print("If C[i]=C[i+1], what is the INDEX DIFFERENCE of the doubled rune")
    print("relative to its neighbors?")

    doublet_positions = []
    for i in range(len(runes) - 1):
        if runes[i] == runes[i + 1]:
            doublet_positions.append(i)

    # For each doublet, look at C[i-1] and C[i] (the doubled value)
    # If autokey: C[i] = P[i] + C[i-1] mod 29 (vigenere)
    # Then C[i]=C[i+1] means P[i]+C[i-1] = P[i+1]+C[i]
    # So P[i]-P[i+1] = C[i]-C[i-1] (mod 29)
    # If C[i]=C[i+1] and we know C[i-1], then P difference = C[i]-C[i-1]

    print("\nUnder CIPHERTEXT AUTOKEY (Vigenere), C[i]=P[i]+C[i-1] mod 29:")
    print("If C[i]=C[i+1], then P[i+1] = P[i] + C[i-1] - C[i] mod 29")
    print("i.e., the plaintext at the SECOND doublet position equals")
    print("plaintext at first + (C[i-1] - C[i]) mod 29")

    # Under Beaufort autokey: C[i] = C[i-1] - P[i] mod 29
    # C[i]=C[i+1] means C[i-1]-P[i] = C[i]-P[i+1]
    # So P[i+1]-P[i] = C[i]-C[i-1]
    print("\nUnder CIPHERTEXT AUTOKEY (Beaufort), C[i]=C[i-1]-P[i] mod 29:")
    print("If C[i]=C[i+1], then P[i+1]-P[i] = C[i]-C[i-1] mod 29")

    # ================================================================
    # 2. WHAT IF DOUBLETS = specific plaintext rune (not just EA)?
    # ================================================================
    print("\n" + "=" * 70)
    print("2. DOUBLET-CAUSING RUNE HYPOTHESIS")
    print("=" * 70)
    print("Under various cipher models, if a doublet is caused by a specific")
    print("plaintext rune X, what would X need to be?")

    # Under simple Vigenere with running key:
    # C[i] = P[i] + K[i] mod 29
    # C[i]=C[i+1] iff P[i]+K[i] = P[i+1]+K[i+1] mod 29
    # This depends on both P and K, not a single rune.

    # Under CIPHERTEXT autokey (Vigenere):
    # C[i] = P[i] + C[i-1] mod 29
    # C[i]=C[i+1] iff P[i]+C[i-1] = P[i+1]+C[i]
    # iff P[i+1] = P[i] + C[i-1] - C[i] = P[i] - (C[i]-C[i-1])
    # The DIFFERENCE of the doublet from its predecessor determines
    # the plaintext relationship.

    # If C[i]=C[i+1] means P[i+1] = 0 (identity = F rune, index 0):
    # Under Vigenere autokey: 0 = P[i] + C[i-1] - C[i]
    # So P[i] = C[i] - C[i-1] mod 29
    # Let's check what P[i] would be for each doublet:

    print("\nAssuming BEAUFORT AUTOKEY: C[i] = C[i-1] - P[i] mod 29")
    print("Then P[i] = C[i-1] - C[i] mod 29")
    print("At doublet C[i]=C[i+1]: P[i] and P[i+1] both = C[i-1]-C[i] and C[i]-C[i+1]=0")
    print("Wait - for the SECOND rune of the doublet:")
    print("P[i+1] = C[i] - C[i+1] = 0 mod 29 → P[i+1] = ᚠ (F, index 0)")
    print("For the FIRST rune: P[i] = C[i-1] - C[i] mod 29")
    print()
    print("Under Beaufort autokey, the SECOND rune of every doublet would be F (index 0)")
    print("This is a STRONG prediction. Let's check if F makes sense as a common rune.\n")

    print("Assuming VIGENERE AUTOKEY: C[i] = P[i] + C[i-1] mod 29")
    print("P[i] = C[i] - C[i-1] mod 29")
    print("For second rune of doublet: P[i+1] = C[i+1] - C[i] = 0 → P[i+1] = ᚠ (F, index 0)")
    print("Same conclusion: second rune of doublet decrypts to F (index 0) = identity\n")

    # What about if the FIRST rune is the special one?
    print("If it's the FIRST rune that's special:")
    print("Under Vigenere autokey: P[i] = C[i] - C[i-1] mod 29")
    print("And C[i]=C[i+1], so the first rune of doublet decrypts to C[i]-C[i-1]")
    print("These would vary per doublet - NOT a fixed rune.\n")

    # ================================================================
    # 3. TEST: Count what P[i] at first and second doublet position would be
    # ================================================================
    print("=" * 70)
    print("3. COMPUTED PLAINTEXT AT DOUBLET POSITIONS (various models)")
    print("=" * 70)

    BOF = pasc.beaufort_tr(c3301.CICADA_ALPHABET)
    VIG = pasc.vigenere_tr(c3301.CICADA_ALPHABET)

    for model_name, model_formula in [
        ("Vig autokey: P=C[i]-C[i-1]", lambda ci, ci_prev: (c3301.r2i(ci) - c3301.r2i(ci_prev)) % 29),
        ("Beau autokey: P=C[i-1]-C[i]", lambda ci, ci_prev: (c3301.r2i(ci_prev) - c3301.r2i(ci)) % 29),
    ]:
        first_rune_counter = Counter()
        second_rune_counter = Counter()
        for pos in doublet_positions:
            if pos > 0:
                p_first = model_formula(runes[pos], runes[pos-1])
                first_rune_counter[p_first] += 1
            if pos + 1 < len(runes) and pos > 0:
                # Second rune of doublet: C[i+1] with key C[i]
                p_second = model_formula(runes[pos+1], runes[pos])
                second_rune_counter[p_second] += 1

        print(f"\nModel: {model_name}")
        print(f"  Plaintext at FIRST rune of doublet:")
        for idx, cnt in first_rune_counter.most_common(10):
            eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
            print(f"    idx={idx:2d} ({eng:2s}): {cnt}")
        print(f"  Plaintext at SECOND rune of doublet:")
        for idx, cnt in second_rune_counter.most_common(10):
            eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
            print(f"    idx={idx:2d} ({eng:2s}): {cnt}")

    # ================================================================
    # 4. IF DOUBLET = EA IN PLAINTEXT, WHAT CIPHER IS CONSISTENT?
    # ================================================================
    print("\n" + "=" * 70)
    print("4. IF DOUBLET SECOND RUNE = EA IN PLAINTEXT")
    print("=" * 70)
    print("Under what model does the second rune of a doublet decrypt to EA (idx 28)?")
    print()
    print("Under Vigenere autokey: P[i+1] = C[i+1] - C[i] = 0 ≠ 28")
    print("  → NOT consistent with standard Vigenere autokey")
    print()
    print("Under shifted Vigenere autokey with offset K:")
    print("  C[i] = P[i] + C[i-1] + K mod 29")
    print("  Doublet: 0 = P[i+1] + K → P[i+1] = -K = 29-K")
    print("  For P[i+1]=28 (EA): K = 29-28 = 1")
    print("  → Vigenere autokey with constant offset +1 maps doublets to EA")
    print()
    print("Under Beaufort autokey with offset K:")
    print("  C[i] = C[i-1] + K - P[i] mod 29")
    print("  Doublet: 0 = K - P[i+1] → P[i+1] = K")
    print("  For P[i+1]=28 (EA): K = 28")
    print("  → Beaufort autokey with constant offset 28 maps doublets to EA")

    # ================================================================
    # 5. DOUBLET POSITIONS IN WORDS
    # ================================================================
    print("\n" + "=" * 70)
    print("5. WHERE DO DOUBLETS FALL IN WORDS?")
    print("=" * 70)

    # Find doublet positions within words
    doublet_word_pos_start = Counter()  # position from start
    doublet_word_pos_end = Counter()    # position from end
    doublet_word_length = Counter()

    # Map rune positions to word positions
    rune_to_word = {}
    rune_to_pos_in_word = {}
    rune_to_word_length = {}

    rune_idx = 0
    for w_idx, w in enumerate(words):
        for pos_in_word, c in enumerate(w):
            rune_to_word[rune_idx] = w_idx
            rune_to_pos_in_word[rune_idx] = pos_in_word
            rune_to_word_length[rune_idx] = len(w)
            rune_idx += 1

    # This won't perfectly align because of delimiters, so use the clean rune stream
    # and word structure together
    current_pos = 0
    word_positions = []
    for w in words:
        word_positions.append((current_pos, current_pos + len(w) - 1, len(w)))
        current_pos += len(w)

    for pos in doublet_positions:
        # Find which word this doublet falls in
        for w_start, w_end, w_len in word_positions:
            if w_start <= pos <= w_end and w_start <= pos + 1 <= w_end:
                pos_in_word = pos - w_start
                doublet_word_pos_start[pos_in_word] += 1
                doublet_word_pos_end[pos_in_word - w_len] += 1
                doublet_word_length[w_len] += 1
                break

    print("Doublet position from start of word:")
    for pos in sorted(doublet_word_pos_start.keys()):
        print(f"  pos {pos}: {doublet_word_pos_start[pos]}")

    print("\nDoublet position from end of word:")
    for pos in sorted(doublet_word_pos_end.keys()):
        print(f"  pos {pos}: {doublet_word_pos_end[pos]}")

    print("\nWord lengths containing doublets:")
    for length in sorted(doublet_word_length.keys()):
        total_words_of_length = sum(1 for w in words if len(w) == length)
        rate = doublet_word_length[length] / total_words_of_length * 100 if total_words_of_length > 0 else 0
        print(f"  length {length:2d}: {doublet_word_length[length]:3d} doublets in {total_words_of_length:4d} words ({rate:.1f}%)")

    # ================================================================
    # 6. DOUBLET SPACING DISTRIBUTION
    # ================================================================
    print("\n" + "=" * 70)
    print("6. DOUBLET SPACING (distance between consecutive doublets)")
    print("=" * 70)

    spacings = [doublet_positions[i+1] - doublet_positions[i]
                for i in range(len(doublet_positions) - 1)]

    print(f"Min spacing: {min(spacings)}")
    print(f"Max spacing: {max(spacings)}")
    print(f"Mean spacing: {sum(spacings)/len(spacings):.1f}")
    print(f"Expected (geometric with p=0.68%): {1/0.0068:.0f}")

    spacing_dist = Counter(spacings)
    print("\nSpacing distribution (top 20):")
    for sp, cnt in sorted(spacing_dist.items())[:30]:
        print(f"  spacing {sp:4d}: {cnt}")

    # Test if spacings are geometric (memoryless = consistent with independent events)
    # Geometric distribution: P(X=k) = p*(1-p)^(k-1)
    p_doublet = len(doublet_positions) / (len(runes) - 1)
    print(f"\nGeometric test (p={p_doublet:.4f}):")
    print(f"  Expected mean spacing: {1/p_doublet:.1f}")
    print(f"  Observed mean spacing: {sum(spacings)/len(spacings):.1f}")

    # ================================================================
    # 7. BIGRAM AROUND EA
    # ================================================================
    print("\n" + "=" * 70)
    print("7. WHAT BIGRAMS CONTAIN EA?")
    print("=" * 70)

    ea_bigrams_before = Counter()  # X followed by EA
    ea_bigrams_after = Counter()   # EA followed by X

    for i in range(len(runes) - 1):
        if runes[i+1] == EA:
            ea_bigrams_before[runes[i]] += 1
        if runes[i] == EA:
            ea_bigrams_after[runes[i+1]] += 1

    print("Rune BEFORE EA (top 15):")
    for r, cnt in ea_bigrams_before.most_common(15):
        idx = c3301.CICADA_ALPHABET.index(r)
        eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
        print(f"  {r} ({eng:2s}): {cnt}")

    print("\nRune AFTER EA (top 15):")
    for r, cnt in ea_bigrams_after.most_common(15):
        idx = c3301.CICADA_ALPHABET.index(r)
        eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
        print(f"  {r} ({eng:2s}): {cnt}")

    # ================================================================
    # 8. CROSS-WORD BOUNDARY DOUBLET ANALYSIS
    # ================================================================
    print("\n" + "=" * 70)
    print("8. CROSS-WORD BOUNDARY ANALYSIS")
    print("=" * 70)

    cross_boundary = 0
    within_word = 0
    for pos in doublet_positions:
        found_in_word = False
        for w_start, w_end, w_len in word_positions:
            if w_start <= pos and pos + 1 <= w_end:
                found_in_word = True
                break
        if found_in_word:
            within_word += 1
        else:
            cross_boundary += 1

    print(f"Doublets within words: {within_word}")
    print(f"Doublets across word boundaries: {cross_boundary}")
    print(f"Total doublet positions: {len(doublet_positions)}")

    # Show the cross-boundary doublets
    if cross_boundary > 0:
        print("\nCross-boundary doublet details:")
        for pos in doublet_positions:
            found_in_word = False
            for w_start, w_end, w_len in word_positions:
                if w_start <= pos and pos + 1 <= w_end:
                    found_in_word = True
                    break
            if not found_in_word:
                idx = c3301.CICADA_ALPHABET.index(runes[pos])
                eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
                # Find the two words
                for wi, (w_start, w_end, w_len) in enumerate(word_positions):
                    if w_end == pos:
                        word1 = words[wi]
                        word2 = words[wi+1] if wi+1 < len(words) else "?"
                        eng1 = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.CICADA_ALPHABET.index(c)] for c in word1)
                        eng2 = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.CICADA_ALPHABET.index(c)] for c in word2)
                        print(f"  pos={pos}: '{word1}'({eng1}) | '{word2}'({eng2}) - boundary rune: {runes[pos]} ({eng})")
                        break

    # ================================================================
    # 9. WORD-INITIAL/FINAL EA AND DOUBLET CONNECTION
    # ================================================================
    print("\n" + "=" * 70)
    print("9. EA AT WORD BOUNDARIES")
    print("=" * 70)

    ea_starts = sum(1 for w in words if w[0] == EA)
    ea_ends = sum(1 for w in words if w[-1] == EA)
    print(f"Words starting with EA: {ea_starts} / {len(words)} ({ea_starts/len(words)*100:.1f}%)")
    print(f"Words ending with EA: {ea_ends} / {len(words)} ({ea_ends/len(words)*100:.1f}%)")
    print(f"Expected if uniform: {len(words)/29:.0f} ({100/29:.1f}%)")

    # If EA is the "identity" causing doublets at word boundaries:
    # Check: does last rune of word N == first rune of word N+1
    # (which would be a cross-boundary doublet)
    boundary_matches = 0
    for i in range(len(words) - 1):
        if words[i][-1] == words[i+1][0]:
            boundary_matches += 1

    print(f"\nCross-word-boundary rune matches (last=first): {boundary_matches}")
    print(f"Expected random: {len(words)/29:.0f}")

    # ================================================================
    # 10. PRIME VALUE ANALYSIS OF DOUBLETS
    # ================================================================
    print("\n" + "=" * 70)
    print("10. PRIME VALUE ANALYSIS OF DOUBLETS")
    print("=" * 70)

    for pos in doublet_positions[:20]:
        r = runes[pos]
        idx = c3301.CICADA_ALPHABET.index(r)
        prime = c3301.r2v(r)
        eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
        if pos > 0:
            prev_r = runes[pos-1]
            prev_idx = c3301.CICADA_ALPHABET.index(prev_r)
            prev_prime = c3301.r2v(prev_r)
            diff_idx = (idx - prev_idx) % 29
            diff_prime = (prime - prev_prime) % 29
            print(f"  pos={pos:5d}: {prev_r}({prev_idx:2d},p={prev_prime:3d}) → {r}{r}({idx:2d},p={prime:3d})"
                  f" Δidx={diff_idx:2d} Δprime%29={diff_prime:2d}")


if __name__ == "__main__":
    main()
