# ABOUTME: Crib analysis for single-letter words under ciphertext autokey.
# ABOUTME: Tests whether single-letter words are consistent with "a"/"I" model.

"""Crib analysis for single-letter words under ciphertext autokey with custom TR.

Under ciphertext autokey: C[i] = TR[C[i-1]][P[i]]

Single-letter words in English are almost exclusively "a" (rune A, index 24)
or "I" (rune I, index 10). If this model is correct, grouping single-letter
words by their preceding ciphertext rune C[i-1] should produce at most 2
distinct C[i] values per group: one for "a" and one for "I".

If any group has 3+ distinct values, either:
- The model is wrong
- There are other single-letter words ("O", etc.)
- The autokey resets at some boundaries
"""

from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "src")

from aldegonde import c3301

ALPHABET = c3301.CICADA_ALPHABET
IDX_A = c3301.r2i("ᚪ")  # "a" -> rune A, index 24
IDX_I = c3301.r2i("ᛁ")  # "I" -> rune I, index 10
IDX_EA = c3301.r2i("ᛠ")  # EA, index 28 (identity under 1-based)


def load_ciphertext(filepath: str) -> str:
    with open(filepath) as f:
        return f.read()


def extract_rune_stream(text: str) -> list[int]:
    """Extract continuous rune stream as library indices, ignoring delimiters."""
    return [c3301.r2i(c) for c in text if c in ALPHABET]


def extract_words_with_positions(text: str) -> list[tuple[int, list[int]]]:
    """Extract words as (start_position_in_rune_stream, [rune_indices]).

    Returns the position of the first rune of each word within the continuous
    rune stream.
    """
    words = []
    rune_pos = 0
    in_word = False
    current_word_start = 0
    current_word_runes: list[int] = []

    for char in text:
        if char in ALPHABET:
            if not in_word:
                current_word_start = rune_pos
                current_word_runes = []
                in_word = True
            current_word_runes.append(c3301.r2i(char))
            rune_pos += 1
        else:
            if in_word:
                words.append((current_word_start, current_word_runes))
                in_word = False
    if in_word:
        words.append((current_word_start, current_word_runes))
    return words


def main() -> None:
    text = load_ciphertext("data/page0-58.txt")
    rune_stream = extract_rune_stream(text)
    words = extract_words_with_positions(text)

    print(f"Total runes: {len(rune_stream)}")
    print(f"Total words: {len(words)}")

    # Find single-letter words and their preceding ciphertext rune
    single_letter: list[tuple[int, int, int]] = []  # (prev_ct, ct, position)
    skipped = 0
    for start_pos, rune_indices in words:
        if len(rune_indices) != 1:
            continue
        ct = rune_indices[0]
        if start_pos == 0:
            skipped += 1
            continue
        prev_ct = rune_stream[start_pos - 1]
        single_letter.append((prev_ct, ct, start_pos))

    print(f"\nSingle-letter words: {len(single_letter)} (skipped {skipped} at start)")

    # Group by preceding ciphertext rune
    groups: dict[int, list[int]] = defaultdict(list)
    for prev_ct, ct, _pos in single_letter:
        groups[prev_ct].append(ct)

    # Analysis: how many distinct C[i] values per C[i-1] group?
    print("\n" + "=" * 70)
    print("GROUPS BY PRECEDING CIPHERTEXT RUNE")
    print("=" * 70)
    print(f"{'C[i-1]':>8} {'rune':>5} {'count':>6} {'distinct':>9} {'values'}")
    print("-" * 70)

    max_distinct = 0
    groups_over_2 = 0
    for prev_idx in range(29):
        if prev_idx not in groups:
            continue
        values = groups[prev_idx]
        distinct = len(set(values))
        max_distinct = max(max_distinct, distinct)
        if distinct > 2:
            groups_over_2 += 1
        counter = Counter(values)
        top = counter.most_common()
        val_str = ", ".join(
            f"{c3301.i2r(v)}({c3301.CICADA_ENGLISH_ALPHABET[v]})={cnt}"
            for v, cnt in top
        )
        print(
            f"{prev_idx:>8} {c3301.i2r(prev_idx):>5} {len(values):>6} "
            f"{distinct:>9}   {val_str}"
        )

    print("-" * 70)
    print(f"Max distinct values in any group: {max_distinct}")
    print(f"Groups with >2 distinct values: {groups_over_2}")

    if max_distinct <= 2:
        print("\nAll groups have <= 2 distinct values.")
        print("CONSISTENT with single-letter words being 'a' and 'I' only.")
    else:
        print(f"\n{groups_over_2} groups have >2 distinct values.")
        print("This means either:")
        print("  - There are other single-letter words beyond 'a' and 'I'")
        print("  - The autokey model or TR assumption is wrong")
        print("  - The autokey resets at some boundaries")

    # Try to deduce TR columns for "a" (idx 24) and "I" (idx 10)
    # For each group with exactly 2 values, the more common one is likely "a"
    print("\n" + "=" * 70)
    print("ATTEMPTING TO DEDUCE TR COLUMNS")
    print("=" * 70)

    # For groups with 1 value: all words are the same letter (likely "a")
    # For groups with 2 values: majority is "a", minority is "I" (or vice versa)
    tr_col_a: dict[int, int] = {}  # TR[prev_ct][24] = ct
    tr_col_i: dict[int, int] = {}  # TR[prev_ct][10] = ct
    ambiguous = 0

    for prev_idx in range(29):
        if prev_idx not in groups:
            continue
        values = groups[prev_idx]
        counter = Counter(values)
        distinct_vals = list(counter.keys())

        if len(distinct_vals) == 1:
            # All same — likely all "a"
            tr_col_a[prev_idx] = distinct_vals[0]
        elif len(distinct_vals) == 2:
            # Majority = "a", minority = "I"
            v1, c1 = counter.most_common()[0]
            v2, c2 = counter.most_common()[1]
            tr_col_a[prev_idx] = v1
            tr_col_i[prev_idx] = v2
        else:
            ambiguous += 1

    print(f"\nDeduced TR column for 'a' (plaintext index {IDX_A}):")
    print(f"  Cells filled: {len(tr_col_a)} / 29")
    for prev_idx in sorted(tr_col_a):
        ct_idx = tr_col_a[prev_idx]
        print(
            f"  TR[{prev_idx:2d} ({c3301.i2r(prev_idx)})][{IDX_A}] = "
            f"{ct_idx:2d} ({c3301.i2r(ct_idx)})"
        )

    print(f"\nDeduced TR column for 'I' (plaintext index {IDX_I}):")
    print(f"  Cells filled: {len(tr_col_i)} / 29")
    for prev_idx in sorted(tr_col_i):
        ct_idx = tr_col_i[prev_idx]
        print(
            f"  TR[{prev_idx:2d} ({c3301.i2r(prev_idx)})][{IDX_I}] = "
            f"{ct_idx:2d} ({c3301.i2r(ct_idx)})"
        )

    # Validate: in a Latin square, each value appears exactly once per column.
    # So the "a" column should have 29 distinct values, and the "I" column too.
    a_values = list(tr_col_a.values())
    i_values = list(tr_col_i.values())
    a_dupes = [v for v, c in Counter(a_values).items() if c > 1]
    i_dupes = [v for v, c in Counter(i_values).items() if c > 1]

    print(f"\nLatin square check:")
    print(f"  Column 'a': {len(a_values)} cells, "
          f"{'no' if not a_dupes else len(a_dupes)} duplicate values"
          f"{'' if not a_dupes else ' -> CONTRADICTION'}")
    print(f"  Column 'I': {len(i_values)} cells, "
          f"{'no' if not i_dupes else len(i_dupes)} duplicate values"
          f"{'' if not i_dupes else ' -> CONTRADICTION'}")

    if a_dupes:
        print(f"\n  Duplicate values in 'a' column: "
              f"{[c3301.i2r(v) for v in a_dupes]}")
        print("  This means the majority-vote assignment is wrong for some")
        print("  groups, or the model is wrong.")

    # Also check: identity column (EA)
    # If TR has right identity at EA (index 28): TR[x][28] = x for all x
    # Doublets give us this: for each doublet at position (i, i+1),
    # C[i] = C[i+1] means P[i+1] = EA (index 28)
    # So TR[C[i]][28] = C[i+1] = C[i] -> TR[x][28] = x. Trivially confirmed.
    print("\n" + "=" * 70)
    print("IDENTITY COLUMN CHECK (EA = index 28)")
    print("=" * 70)
    doublets = []
    for pos in range(len(rune_stream) - 1):
        if rune_stream[pos] == rune_stream[pos + 1]:
            doublets.append(rune_stream[pos])

    doublet_runes = set(doublets)
    print(f"Doublets found: {len(doublets)}")
    print(f"Distinct rune values in doublets: {len(doublet_runes)} / 29")
    missing = set(range(29)) - doublet_runes
    if missing:
        print(f"Runes never appearing as doublets: "
              f"{[c3301.i2r(v) for v in sorted(missing)]}")
        print("(With only 89 doublets, some runes missing is expected)")
    print("All doublets are trivially consistent with TR[x][28] = x")


if __name__ == "__main__":
    main()
