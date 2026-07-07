#!/usr/bin/env python3
"""
Deep statistical analysis of Liber Primus ciphertext.

Investigates:
1. Doublet context - what runes appear around doublets
2. EA rune hypothesis - does EA correlate with doublet positions
3. Bigram asymmetry - is AB vs BA frequency different
4. Positional patterns - do doublet rates vary by position in words
5. Word-level statistics - word length distribution vs English
6. Conditional probabilities - P(rune | previous rune)
7. Cribbing analysis - what English words could map to observed patterns
8. Delta stream doublet analysis
9. Transition matrix analysis
"""

import sys
import math
from collections import Counter, defaultdict

sys.path.insert(0, "src")

from aldegonde import c3301


def load_and_clean(filepath: str) -> str:
    with open(filepath) as f:
        return f.read()


def clean_runes(text: str) -> str:
    return "".join(c for c in text if c in c3301.CICADA_ALPHABET)


def get_words(text: str) -> list[str]:
    """Extract words (delimited by - . / % & $ and newlines)."""
    import re
    # Split on non-rune characters
    words = re.split(r'[^' + ''.join(c3301.CICADA_ALPHABET) + r']+', text)
    return [w for w in words if len(w) > 0]


def main() -> None:
    lp_text = load_and_clean("data/page0-58.txt")
    runes = clean_runes(lp_text)
    words = get_words(lp_text)

    print("=" * 70)
    print("DEEP STATISTICAL ANALYSIS OF LIBER PRIMUS")
    print("=" * 70)
    print(f"Total runes: {len(runes)}, Total words: {len(words)}")

    EA = "ᛠ"  # EA rune, index 28
    EA_IDX = 28

    # ================================================================
    # 1. DOUBLET CONTEXT ANALYSIS
    # ================================================================
    print("\n" + "=" * 70)
    print("1. DOUBLET CONTEXT ANALYSIS")
    print("=" * 70)

    doublet_positions = []
    for i in range(len(runes) - 1):
        if runes[i] == runes[i + 1]:
            doublet_positions.append(i)

    print(f"Total doublets: {len(doublet_positions)}")

    # What rune comes BEFORE each doublet?
    before_doublet = Counter()
    after_doublet = Counter()
    doublet_rune = Counter()
    for pos in doublet_positions:
        doublet_rune[runes[pos]] += 1
        if pos > 0:
            before_doublet[runes[pos - 1]] += 1
        if pos + 2 < len(runes):
            after_doublet[runes[pos + 2]] += 1

    print("\nRune that forms doublet (which rune is doubled):")
    for rune, cnt in doublet_rune.most_common():
        idx = c3301.CICADA_ALPHABET.index(rune)
        eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
        print(f"  {rune} ({eng:2s}) idx={idx:2d}: {cnt:3d} doublets")

    print("\nRune appearing BEFORE doublet:")
    for rune, cnt in before_doublet.most_common(10):
        idx = c3301.CICADA_ALPHABET.index(rune)
        eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
        print(f"  {rune} ({eng:2s}): {cnt}")

    print("\nRune appearing AFTER doublet:")
    for rune, cnt in after_doublet.most_common(10):
        idx = c3301.CICADA_ALPHABET.index(rune)
        eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
        print(f"  {rune} ({eng:2s}): {cnt}")

    # ================================================================
    # 2. EA RUNE HYPOTHESIS
    # ================================================================
    print("\n" + "=" * 70)
    print("2. EA RUNE HYPOTHESIS")
    print("=" * 70)
    print("Testing: Does EA (ᛠ) appear as the first or second rune of doublets?")

    ea_as_first = sum(1 for pos in doublet_positions if runes[pos] == EA)
    # EA is the doublet rune itself (both positions are EA)
    print(f"\nEA IS the doubled rune: {ea_as_first} times (out of {len(doublet_positions)} doublets)")

    # More interesting: does EA appear adjacent to doublets?
    ea_before = sum(1 for pos in doublet_positions if pos > 0 and runes[pos - 1] == EA)
    ea_after = sum(1 for pos in doublet_positions if pos + 2 < len(runes) and runes[pos + 2] == EA)
    print(f"EA appears immediately BEFORE doublet: {ea_before}")
    print(f"EA appears immediately AFTER doublet: {ea_after}")

    # Test: if we assume EA in plaintext causes the doublet, what would that mean?
    # Count EA frequency in ciphertext
    ea_count = runes.count(EA)
    ea_freq = ea_count / len(runes)
    print(f"\nEA frequency in ciphertext: {ea_count} ({ea_freq*100:.2f}%)")
    print(f"Doublet rate: {len(doublet_positions)/(len(runes)-1)*100:.2f}%")

    # Hypothesis: if the cipher produces a doublet exactly when plaintext has EA
    # Then we'd expect #doublets ≈ #EA_in_plaintext
    # EA in English runeglish appears rarely (each, ear, eat, etc.)
    print(f"\nIf doublets = EA occurrences in plaintext:")
    print(f"  Expected EA frequency in runeglish: ~1-3%")
    print(f"  Observed doublet rate: {len(doublet_positions)/(len(runes)-1)*100:.3f}%")
    print(f"  This is LOW for EA but could work if EA is very rare in runeglish")

    # Check: what rune does EA appear as in the FIRST position of doublets
    # vs what rune appears in position BEFORE a doublet when that rune is EA
    print("\nDetailed doublet-EA correlation:")
    for pos in doublet_positions:
        ctx_before = runes[pos-1] if pos > 0 else "^"
        ctx_after = runes[pos+2] if pos+2 < len(runes) else "$"
        doubled = runes[pos]
        idx = c3301.CICADA_ALPHABET.index(doubled)
        ea_marker = " <-- EA" if doubled == EA else ""
        ea_before_m = " [EA before]" if ctx_before == EA else ""
        ea_after_m = " [EA after]" if ctx_after == EA else ""
        print(f"  pos={pos:5d}: ...{ctx_before}{doubled}{doubled}{ctx_after}... (idx={idx:2d}){ea_marker}{ea_before_m}{ea_after_m}")

    # ================================================================
    # 3. TRANSITION MATRIX ANALYSIS
    # ================================================================
    print("\n" + "=" * 70)
    print("3. TRANSITION MATRIX - P(C[i] | C[i-1])")
    print("=" * 70)

    transitions = defaultdict(lambda: defaultdict(int))
    for i in range(len(runes) - 1):
        transitions[runes[i]][runes[i + 1]] += 1

    # Compute diagonal vs off-diagonal
    total_trans = len(runes) - 1
    diagonal_sum = sum(transitions[r][r] for r in c3301.CICADA_ALPHABET)
    off_diagonal_sum = total_trans - diagonal_sum

    print(f"Diagonal (doublets): {diagonal_sum} ({diagonal_sum/total_trans*100:.2f}%)")
    print(f"Off-diagonal: {off_diagonal_sum} ({off_diagonal_sum/total_trans*100:.2f}%)")
    print(f"Expected diagonal (random): {total_trans/29:.0f} ({100/29:.2f}%)")

    # Check if off-diagonal is uniform
    print("\nOff-diagonal uniformity check:")
    off_diag_counts = []
    for r1 in c3301.CICADA_ALPHABET:
        for r2 in c3301.CICADA_ALPHABET:
            if r1 != r2:
                off_diag_counts.append(transitions[r1][r2])

    mean_off = sum(off_diag_counts) / len(off_diag_counts)
    var_off = sum((x - mean_off)**2 for x in off_diag_counts) / len(off_diag_counts)
    std_off = var_off ** 0.5
    print(f"  Off-diagonal mean: {mean_off:.2f}")
    print(f"  Off-diagonal std: {std_off:.2f}")
    print(f"  Expected mean (uniform): {total_trans / (29*28):.2f}")
    print(f"  CV (coefficient of variation): {std_off/mean_off:.3f}")

    # Per-rune: which rune has highest/lowest self-transition?
    print("\nSelf-transition rate per rune:")
    for r in c3301.CICADA_ALPHABET:
        total_from_r = sum(transitions[r][r2] for r2 in c3301.CICADA_ALPHABET)
        self_rate = transitions[r][r] / total_from_r if total_from_r > 0 else 0
        idx = c3301.CICADA_ALPHABET.index(r)
        eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
        bar = "*" * transitions[r][r]
        print(f"  {r} ({eng:2s}): {transitions[r][r]:2d}/{total_from_r:3d} = {self_rate*100:5.2f}% {bar}")

    # ================================================================
    # 4. BIGRAM ASYMMETRY
    # ================================================================
    print("\n" + "=" * 70)
    print("4. BIGRAM ASYMMETRY - is freq(AB) ≈ freq(BA)?")
    print("=" * 70)

    bigrams_counter = Counter()
    for i in range(len(runes) - 1):
        bigrams_counter[runes[i] + runes[i+1]] += 1

    # Check asymmetry
    asymmetry_scores = []
    for r1 in c3301.CICADA_ALPHABET:
        for r2 in c3301.CICADA_ALPHABET:
            if r1 < r2:
                ab = bigrams_counter[r1 + r2]
                ba = bigrams_counter[r2 + r1]
                if ab + ba > 0:
                    asym = abs(ab - ba) / (ab + ba)
                    asymmetry_scores.append((r1, r2, ab, ba, asym))

    asymmetry_scores.sort(key=lambda x: -x[4])
    print("Most asymmetric bigrams (top 20):")
    for r1, r2, ab, ba, asym in asymmetry_scores[:20]:
        i1 = c3301.CICADA_ALPHABET.index(r1)
        i2 = c3301.CICADA_ALPHABET.index(r2)
        e1 = c3301.CICADA_ENGLISH_ALPHABET[i1]
        e2 = c3301.CICADA_ENGLISH_ALPHABET[i2]
        print(f"  {r1}{r2} ({e1}{e2})={ab:3d} vs {r2}{r1} ({e2}{e1})={ba:3d}  asym={asym:.3f}")

    avg_asym = sum(s[4] for s in asymmetry_scores) / len(asymmetry_scores)
    print(f"\nAverage asymmetry: {avg_asym:.4f}")
    print(f"Expected for random text: ~0.15-0.20 (sampling variation)")

    # ================================================================
    # 5. WORD LENGTH DISTRIBUTION
    # ================================================================
    print("\n" + "=" * 70)
    print("5. WORD LENGTH DISTRIBUTION")
    print("=" * 70)

    word_lengths = [len(w) for w in words]
    length_dist = Counter(word_lengths)
    print(f"Total words: {len(words)}")
    print(f"Mean word length: {sum(word_lengths)/len(word_lengths):.2f}")
    print(f"Max word length: {max(word_lengths)}")

    print("\nLength distribution:")
    for length in sorted(length_dist.keys()):
        pct = length_dist[length] / len(words) * 100
        bar = "#" * int(pct)
        print(f"  {length:2d}: {length_dist[length]:4d} ({pct:5.1f}%) {bar}")

    # English word lengths in runeglish: "the"=2 runes (ᚦᛖ), "and"=3, etc.
    print("\nCommon English words in runeglish length:")
    test_words = {"the": 2, "and": 3, "of": 2, "to": 2, "a": 1, "in": 2, "is": 2,
                  "it": 2, "that": 4, "for": 3, "was": 3, "on": 2, "are": 3,
                  "with": 3, "this": 3, "be": 2, "not": 3, "but": 3}
    for word, rlen in sorted(test_words.items(), key=lambda x: x[1]):
        print(f"  '{word}' -> {rlen} runes")

    # ================================================================
    # 6. DOUBLETS IN WORD CONTEXT
    # ================================================================
    print("\n" + "=" * 70)
    print("6. DOUBLETS IN WORD CONTEXT")
    print("=" * 70)

    # Find doublets within words vs across word boundaries
    words_with_doublets = 0
    doublets_in_words = 0
    for w in words:
        has_doublet = False
        for i in range(len(w) - 1):
            if w[i] == w[i + 1]:
                doublets_in_words += 1
                has_doublet = True
        if has_doublet:
            words_with_doublets += 1

    # Now check cross-word-boundary doublets
    # We need to reconstruct the word sequence and check boundaries
    print(f"Doublets within words: {doublets_in_words}")
    print(f"Words containing doublets: {words_with_doublets} / {len(words)}")

    # Show words that contain doublets
    print("\nWords containing doublets:")
    for w in words:
        for i in range(len(w) - 1):
            if w[i] == w[i + 1]:
                idx = c3301.CICADA_ALPHABET.index(w[i])
                eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
                # Convert whole word
                word_eng = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.CICADA_ALPHABET.index(c)] for c in w)
                print(f"  '{w}' ({word_eng}) - doubled {w[i]} ({eng}) at pos {i}")

    # ================================================================
    # 7. DELTA STREAM ANALYSIS
    # ================================================================
    print("\n" + "=" * 70)
    print("7. DELTA STREAM ANALYSIS")
    print("=" * 70)

    indices = [c3301.r2i(r) for r in runes]

    # Delta = difference between consecutive runes mod 29
    deltas = [(indices[i+1] - indices[i]) % 29 for i in range(len(indices) - 1)]
    delta_dist = Counter(deltas)

    print("Delta (C[i+1] - C[i] mod 29) distribution:")
    for d in range(29):
        cnt = delta_dist[d]
        pct = cnt / len(deltas) * 100
        marker = " <-- ZERO (doublet)" if d == 0 else ""
        bar = "#" * int(pct * 3)
        print(f"  Δ={d:2d}: {cnt:4d} ({pct:5.2f}%) {bar}{marker}")

    # Delta of deltas (second differences)
    delta2 = [(deltas[i+1] - deltas[i]) % 29 for i in range(len(deltas) - 1)]
    delta2_dist = Counter(delta2)
    print(f"\nSecond difference (Δ²) at 0: {delta2_dist[0]} ({delta2_dist[0]/len(delta2)*100:.2f}%)")
    print(f"Expected random: {len(delta2)/29:.0f} ({100/29:.2f}%)")

    # Doublets in delta stream
    delta_doublets = sum(1 for i in range(len(deltas) - 1) if deltas[i] == deltas[i+1])
    print(f"\nDoublets in delta stream: {delta_doublets}")
    print(f"Expected random: {len(deltas)/29:.0f}")
    print(f"Ratio: {delta_doublets / (len(deltas)/29):.3f}")

    # ================================================================
    # 8. SKIP-PATTERN ANALYSIS
    # ================================================================
    print("\n" + "=" * 70)
    print("8. SKIP-PATTERN DOUBLET ANALYSIS")
    print("=" * 70)
    print("Checking: C[i] == C[i+k] rates for various k")

    for k in range(1, 60):
        matches = sum(1 for i in range(len(runes) - k) if runes[i] == runes[i + k])
        expected = (len(runes) - k) / 29
        ratio = matches / expected
        sigma = (matches - expected) / (expected ** 0.5)
        marker = " ***" if abs(sigma) > 3 else ""
        if k <= 30 or abs(sigma) > 2:
            print(f"  skip={k:2d}: {matches:4d} (expected {expected:.0f}, ratio={ratio:.3f}, σ={sigma:+.1f}){marker}")

    # ================================================================
    # 9. POSITION-IN-WORD ANALYSIS
    # ================================================================
    print("\n" + "=" * 70)
    print("9. RUNE FREQUENCY BY POSITION IN WORD")
    print("=" * 70)

    # First rune of words
    first_rune = Counter(w[0] for w in words if len(w) > 0)
    last_rune = Counter(w[-1] for w in words if len(w) > 0)

    print("First rune of words (top 10):")
    for rune, cnt in first_rune.most_common(10):
        idx = c3301.CICADA_ALPHABET.index(rune)
        eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
        print(f"  {rune} ({eng:2s}): {cnt:4d} ({cnt/len(words)*100:.1f}%)")

    print("\nLast rune of words (top 10):")
    for rune, cnt in last_rune.most_common(10):
        idx = c3301.CICADA_ALPHABET.index(rune)
        eng = c3301.CICADA_ENGLISH_ALPHABET[idx]
        print(f"  {rune} ({eng:2s}): {cnt:4d} ({cnt/len(words)*100:.1f}%)")

    # Is first/last rune distribution uniform?
    from scipy.stats import chisquare
    first_counts = [first_rune.get(r, 0) for r in c3301.CICADA_ALPHABET]
    last_counts = [last_rune.get(r, 0) for r in c3301.CICADA_ALPHABET]
    chi2_first, p_first = chisquare(first_counts)
    chi2_last, p_last = chisquare(last_counts)
    print(f"\nFirst rune chi2={chi2_first:.2f}, p={p_first:.5f}")
    print(f"Last rune  chi2={chi2_last:.2f}, p={p_last:.5f}")

    # ================================================================
    # 10. EA-SPECIFIC ANALYSIS
    # ================================================================
    print("\n" + "=" * 70)
    print("10. EA-SPECIFIC POSITIONAL ANALYSIS")
    print("=" * 70)

    ea_positions = [i for i, r in enumerate(runes) if r == EA]
    print(f"EA occurrences: {len(ea_positions)}")

    # Where does EA appear relative to doublets?
    # For each doublet, find nearest EA
    distances_to_ea = []
    for dpos in doublet_positions:
        min_dist = min(abs(dpos - epos) for epos in ea_positions)
        distances_to_ea.append(min_dist)

    if distances_to_ea:
        print(f"\nDistance from doublet to nearest EA:")
        dist_counter = Counter(distances_to_ea)
        for d in sorted(dist_counter.keys())[:20]:
            print(f"  distance={d}: {dist_counter[d]} doublets")

    # EA as specific position in words
    ea_word_pos = Counter()
    ea_word_pos_last = Counter()
    for w in words:
        for i, c in enumerate(w):
            if c == EA:
                ea_word_pos[i] += 1
                ea_word_pos_last[i - len(w)] += 1

    print(f"\nEA position in word (from start):")
    for pos in sorted(ea_word_pos.keys()):
        print(f"  pos {pos}: {ea_word_pos[pos]}")

    print(f"\nEA position in word (from end):")
    for pos in sorted(ea_word_pos_last.keys()):
        print(f"  pos {pos}: {ea_word_pos_last[pos]}")

    # ================================================================
    # 11. CRIBBING ANALYSIS
    # ================================================================
    print("\n" + "=" * 70)
    print("11. CRIBBING ANALYSIS")
    print("=" * 70)

    # Word length=1 analysis
    single_rune_words = [w for w in words if len(w) == 1]
    print(f"\nSingle-rune words: {len(single_rune_words)}")
    print(f"Distribution: {Counter(single_rune_words).most_common()}")
    print("In English, single-letter words are: 'a' and 'I'")
    print("In runeglish: 'a'=ᚪ (1 rune), 'I'=ᛁ (1 rune)")

    # Word length=2 analysis
    two_rune_words = [w for w in words if len(w) == 2]
    print(f"\n2-rune words: {len(two_rune_words)}")
    two_dist = Counter(two_rune_words)
    print(f"Most common 2-rune words (top 15):")
    for w, cnt in two_dist.most_common(15):
        eng = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.CICADA_ALPHABET.index(c)] for c in w)
        print(f"  {w} ({eng}): {cnt}")

    # Isomorphic pattern analysis for common English words
    print("\nIsomorphic pattern check:")
    print("Looking for words with repeated rune patterns...")

    # Words with pattern ABAB, ABBA, etc.
    pattern_words = defaultdict(list)
    for w in words:
        if len(w) >= 3:
            # Create pattern
            mapping = {}
            pattern = []
            next_id = 0
            for c in w:
                if c not in mapping:
                    mapping[c] = next_id
                    next_id += 1
                pattern.append(mapping[c])
            pattern_words[tuple(pattern)].append(w)

    # Show interesting patterns
    print("\nWords with repeated-letter patterns (3+ runes):")
    interesting = [(p, ws) for p, ws in pattern_words.items()
                   if len(set(p)) < len(p) and len(ws) >= 2]
    interesting.sort(key=lambda x: -len(x[1]))
    for pattern, ws in interesting[:20]:
        sample = ws[:5]
        sample_eng = []
        for w in sample:
            eng = "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.CICADA_ALPHABET.index(c)] for c in w)
            sample_eng.append(f"{w}({eng})")
        print(f"  pattern {pattern}: {len(ws)} words, e.g. {', '.join(sample_eng)}")

    # ================================================================
    # 12. ENTROPY BY POSITION
    # ================================================================
    print("\n" + "=" * 70)
    print("12. CONDITIONAL ENTROPY H(C[i] | C[i-1])")
    print("=" * 70)

    # H(C[i] | C[i-1]) - if there's a dependency, this should be less than H(C[i])
    # For a Markov chain with suppressed diagonal:
    # H(C) = log2(29) ≈ 4.858
    # H(C[i]|C[i-1]) with diagonal suppressed ≈ log2(28) ≈ 4.807

    # Compute conditional entropy
    total_bigrams = sum(bigrams_counter.values())
    cond_entropy = 0.0
    for r1 in c3301.CICADA_ALPHABET:
        row_total = sum(transitions[r1][r2] for r2 in c3301.CICADA_ALPHABET)
        if row_total == 0:
            continue
        p_r1 = row_total / total_bigrams
        for r2 in c3301.CICADA_ALPHABET:
            if transitions[r1][r2] > 0:
                p_r2_given_r1 = transitions[r1][r2] / row_total
                cond_entropy -= p_r1 * p_r2_given_r1 * math.log2(p_r2_given_r1)

    marginal_entropy = -sum(
        (runes.count(r)/len(runes)) * math.log2(runes.count(r)/len(runes))
        for r in c3301.CICADA_ALPHABET if runes.count(r) > 0
    )

    print(f"H(C) marginal entropy:     {marginal_entropy:.4f} bits")
    print(f"H(C[i]|C[i-1]):           {cond_entropy:.4f} bits")
    print(f"Mutual information I:      {marginal_entropy - cond_entropy:.4f} bits")
    print(f"Expected H if uniform:     {math.log2(29):.4f} bits")
    print(f"Expected H if no-doublet:  {math.log2(28):.4f} bits")
    print(f"Difference from log2(28):  {cond_entropy - math.log2(28):.4f} bits")

    # ================================================================
    # 13. RUNS TEST
    # ================================================================
    print("\n" + "=" * 70)
    print("13. RUNS ANALYSIS (ascending/descending)")
    print("=" * 70)

    # Count runs (consecutive increases or decreases in index value)
    runs = 1
    current_direction = None
    run_lengths = []
    current_run = 1
    for i in range(len(indices) - 1):
        direction = "up" if indices[i+1] > indices[i] else ("down" if indices[i+1] < indices[i] else "same")
        if direction == current_direction:
            current_run += 1
        else:
            if current_direction is not None:
                run_lengths.append(current_run)
            current_run = 1
            current_direction = direction
            runs += 1
    run_lengths.append(current_run)

    print(f"Total runs: {runs}")
    print(f"Expected runs (random): ~{2*(len(indices)-1)/3:.0f}")
    run_dist = Counter(run_lengths)
    print(f"Run length distribution:")
    for length in sorted(run_dist.keys()):
        print(f"  length {length}: {run_dist[length]}")

    # ================================================================
    # 14. AUTOCORRELATION OF INDEX SEQUENCE
    # ================================================================
    print("\n" + "=" * 70)
    print("14. AUTOCORRELATION OF INDEX SEQUENCE")
    print("=" * 70)

    mean_idx = sum(indices) / len(indices)
    var_idx = sum((x - mean_idx)**2 for x in indices) / len(indices)

    for lag in range(1, 51):
        cov = sum((indices[i] - mean_idx) * (indices[i+lag] - mean_idx)
                  for i in range(len(indices) - lag)) / (len(indices) - lag)
        autocorr = cov / var_idx
        marker = " ***" if abs(autocorr) > 0.03 else ""
        if lag <= 30 or abs(autocorr) > 0.02:
            print(f"  lag={lag:2d}: autocorr={autocorr:+.4f}{marker}")

    # ================================================================
    # 15. CHI-SQUARE TEST ON BIGRAMS (EXCLUDING DIAGONAL)
    # ================================================================
    print("\n" + "=" * 70)
    print("15. BIGRAM UNIFORMITY (excluding diagonal)")
    print("=" * 70)

    off_diag_bigrams = []
    for r1 in c3301.CICADA_ALPHABET:
        for r2 in c3301.CICADA_ALPHABET:
            if r1 != r2:
                off_diag_bigrams.append(bigrams_counter.get(r1+r2, 0))

    chi2_bi, p_bi = chisquare(off_diag_bigrams)
    print(f"Chi-square test on {len(off_diag_bigrams)} off-diagonal bigrams:")
    print(f"  chi2={chi2_bi:.2f}, p={p_bi:.5f}")
    print(f"  Mean count: {sum(off_diag_bigrams)/len(off_diag_bigrams):.2f}")
    print(f"  Std count: {(sum((x - sum(off_diag_bigrams)/len(off_diag_bigrams))**2 for x in off_diag_bigrams) / len(off_diag_bigrams))**0.5:.2f}")


if __name__ == "__main__":
    main()
