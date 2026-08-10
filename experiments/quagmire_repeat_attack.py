# ABOUTME: Attack on Quagmire III ciphertext autokey using repeat analysis
# ABOUTME: Exploits the structure that identical CT sequences reveal identical PT sequences

"""
Repeat-Based Attack on Quagmire III Ciphertext Autokey

Key insight: When identical ciphertext sequences appear at positions i and j:
- If the preceding ciphertext chars differ (C[i-1] != C[j-1])
- Then: pos[P[i]] - pos[P[j]] = pos[C[i-1]] - pos[C[j-1]]
- And: P[i+1:] == P[j+1:] (remaining plaintext is IDENTICAL)

This gives us:
1. Constraint equations on the alphabet
2. Knowledge of where identical plaintext sequences appear
3. A validation criterion: decrypted repeats must be consistent
"""

import sys  # noqa: I001
sys.path.insert(0, 'src')

import random  # noqa: I001
import multiprocessing as mp
from collections import defaultdict
from dataclasses import dataclass

from aldegonde import c3301
from aldegonde.stats.ioc import ioc

ALPHABET = c3301.CICADA_ALPHABET.copy()
ALPHABET_SIZE = len(ALPHABET)  # 29


@dataclass
class RepeatInfo:
    """Information about a ciphertext repeat."""
    sequence: str
    positions: list[int]
    preceding_chars: list[str]
    constraints: list[tuple[str, str]]  # (prev1, prev2) pairs with different chars


def find_repeats(ciphertext: str, min_length: int = 4, max_length: int = 15) -> dict[str, list[int]]:
    """Find all repeated sequences in ciphertext."""
    repeats = defaultdict(list)

    for length in range(min_length, min(max_length + 1, len(ciphertext))):
        for i in range(len(ciphertext) - length + 1):
            seq = ciphertext[i:i + length]
            repeats[seq].append(i)

    # Filter to sequences that appear multiple times
    return {seq: positions for seq, positions in repeats.items() if len(positions) >= 2}


def extract_constraints(ciphertext: str, repeats: dict[str, list[int]]) -> list[RepeatInfo]:
    """Extract constraint information from repeats."""
    results = []

    for seq, positions in repeats.items():
        if len(seq) < 4:
            continue

        # Get preceding characters for each position
        preceding = []
        for pos in positions:
            if pos > 0:
                preceding.append((pos, ciphertext[pos - 1]))
            else:
                preceding.append((pos, None))

        # Find pairs with different preceding chars (these give constraints)
        constraints = []
        for i in range(len(preceding)):
            for j in range(i + 1, len(preceding)):
                pos_i, prev_i = preceding[i]
                pos_j, prev_j = preceding[j]

                if prev_i is not None and prev_j is not None and prev_i != prev_j:
                    constraints.append((prev_i, prev_j))

        if constraints:
            results.append(RepeatInfo(
                sequence=seq,
                positions=positions,
                preceding_chars=[p[1] for p in preceding if p[1] is not None],
                constraints=constraints
            ))

    return results


def build_lookup_tables(mixed_alphabet: list[str]) -> tuple[dict[str, int], list[str]]:
    """Build lookup tables for an alphabet."""
    char_to_pos = {c: i for i, c in enumerate(mixed_alphabet)}
    pos_to_char = list(mixed_alphabet)
    return char_to_pos, pos_to_char


def quagmire3_decrypt(
    ciphertext: str,
    char_to_pos: dict[str, int],
    pos_to_char: list[str],
    primer_pos: int,
    mode: str = "beaufort",
) -> str:
    """Decrypt Quagmire III ciphertext autokey."""
    n = len(pos_to_char)
    plaintext = []
    k_pos = primer_pos

    for c in ciphertext:
        if c not in char_to_pos:
            continue
        c_pos = char_to_pos[c]

        if mode == "beaufort":
            p_pos = (k_pos - c_pos) % n
        elif mode == "vigenere":
            p_pos = (c_pos - k_pos) % n
        else:  # variant
            p_pos = (c_pos + k_pos) % n

        plaintext.append(pos_to_char[p_pos])
        k_pos = c_pos  # ciphertext autokey

    return "".join(plaintext)


def check_repeat_consistency(
    ciphertext: str,
    alphabet: list[str],
    repeat_info: RepeatInfo,
    primer_pos: int,
) -> bool:
    """
    Check if a repeat decrypts consistently.

    For a valid alphabet, chars 2+ of the decrypted repeat should be identical
    at all repeat positions.
    """
    char_to_pos, pos_to_char = build_lookup_tables(alphabet)

    decrypted_tails = []
    for pos in repeat_info.positions:
        if pos == 0:
            # First position uses primer
            k_pos = primer_pos
        else:
            prev_char = ciphertext[pos - 1]
            if prev_char not in char_to_pos:
                continue
            k_pos = char_to_pos[prev_char]

        # Decrypt this occurrence
        pt = quagmire3_decrypt(
            repeat_info.sequence,
            char_to_pos,
            pos_to_char,
            k_pos,
        )

        if len(pt) > 1:
            decrypted_tails.append(pt[1:])  # Chars 2+ should match

    # All tails should be identical
    if len(decrypted_tails) < 2:
        return True

    return all(t == decrypted_tails[0] for t in decrypted_tails)


def score_quadgram(text: str) -> float:
    """Score text using runeglish quadgrams."""
    return c3301.quadgramscore(text)


def score_with_repeat_penalty(
    ciphertext: str,
    alphabet: list[str],
    primer_pos: int,
    repeat_infos: list[RepeatInfo],
    mode: str = "beaufort",
    sample_size: int = 20,
) -> float:
    """Score alphabet using quadgrams + repeat consistency penalty."""
    char_to_pos, pos_to_char = build_lookup_tables(alphabet)

    # Decrypt full text
    plaintext = quagmire3_decrypt(ciphertext, char_to_pos, pos_to_char, primer_pos, mode)

    # Base score from quadgrams
    base_score = score_quadgram(plaintext)

    # Penalty for inconsistent repeats (sample for speed)
    penalty = 0
    sample = repeat_infos[:sample_size] if len(repeat_infos) > sample_size else repeat_infos
    for ri in sample:
        if not check_repeat_consistency(ciphertext, alphabet, ri, primer_pos):
            penalty += 500  # Larger penalty per inconsistent repeat

    return base_score - penalty


def hill_climb(
    ciphertext: str,
    repeat_infos: list[RepeatInfo],
    max_iterations: int = 50000,
    primer_idx: int = 0,
    mode: str = "beaufort",
    restart_threshold: int = 1000,
    *,
    use_repeat_penalty: bool = True,
) -> tuple[list[str], float, str]:
    """Hill climb to find best alphabet, using repeat constraints."""

    def score_fn(alphabet):
        if use_repeat_penalty and repeat_infos:
            return score_with_repeat_penalty(
                ciphertext, alphabet, primer_idx, repeat_infos, mode
            )
        char_to_pos, pos_to_char = build_lookup_tables(alphabet)
        pt = quagmire3_decrypt(ciphertext, char_to_pos, pos_to_char, primer_idx, mode)
        return score_quadgram(pt)

    # Start with random alphabet
    current_alphabet = ALPHABET.copy()
    random.shuffle(current_alphabet)
    current_score = score_fn(current_alphabet)

    best_alphabet = current_alphabet.copy()
    best_score = current_score

    no_improve_count = 0

    for _iteration in range(max_iterations):
        # Swap two letters
        i, j = random.sample(range(ALPHABET_SIZE), 2)
        new_alphabet = current_alphabet.copy()
        new_alphabet[i], new_alphabet[j] = new_alphabet[j], new_alphabet[i]

        new_score = score_fn(new_alphabet)

        if new_score > current_score:
            current_alphabet = new_alphabet
            current_score = new_score
            no_improve_count = 0

            if new_score > best_score:
                best_alphabet = new_alphabet.copy()
                best_score = new_score
        else:
            no_improve_count += 1

        # Random restart if stuck
        if no_improve_count > restart_threshold:
            current_alphabet = ALPHABET.copy()
            random.shuffle(current_alphabet)
            current_score = score_fn(current_alphabet)
            no_improve_count = 0

    # Get final plaintext
    char_to_pos, pos_to_char = build_lookup_tables(best_alphabet)
    best_plaintext = quagmire3_decrypt(ciphertext, char_to_pos, pos_to_char, primer_idx, mode)

    return best_alphabet, best_score, best_plaintext


def run_single_climb(args: tuple) -> tuple:
    """Worker function for parallel execution."""
    (ciphertext, repeat_infos_data, max_iterations, primer_idx, mode,
     restart_threshold, use_repeat_penalty) = args

    # Reconstruct RepeatInfo objects (can't pickle dataclasses directly in some cases)
    repeat_infos = [
        RepeatInfo(sequence=d['seq'], positions=d['pos'],
                   preceding_chars=d['prev'], constraints=d['cons'])
        for d in repeat_infos_data
    ]

    alphabet, score, plaintext = hill_climb(
        ciphertext,
        repeat_infos,
        max_iterations=max_iterations,
        primer_idx=primer_idx,
        mode=mode,
        restart_threshold=restart_threshold,
        use_repeat_penalty=use_repeat_penalty,
    )

    # Calculate IOC for result
    pt_ioc = ioc(plaintext) * ALPHABET_SIZE

    # Count consistent repeats
    consistent = sum(
        1 for ri in repeat_infos
        if check_repeat_consistency(ciphertext, alphabet, ri, primer_idx)
    )

    return (alphabet, score, plaintext, mode, primer_idx, pt_ioc, consistent, len(repeat_infos))


def runes_to_english(text: str) -> str:
    """Convert runes to English letter names."""
    result = []
    for r in text:
        if r in ALPHABET:
            idx = ALPHABET.index(r)
            result.append(c3301.CICADA_ENGLISH_ALPHABET[idx])
        else:
            result.append(r)
    return "".join(result)


def load_lp(*, exclude_last_pages: bool = True) -> str:
    """Load LP ciphertext.

    Args:
        exclude_last_pages: If True, exclude pages 56-57 (last 180 runes)
                           which are encrypted differently.
    """
    with open("data/page0-58.txt") as f:
        text = f.read()
    lp = "".join(c for c in text if c in ALPHABET)
    if exclude_last_pages:
        # Pages 56-57 are encrypted differently - exclude last 180 runes
        return lp[:-180]
    return lp


def print_repeat_analysis(ciphertext: str, repeat_infos: list[RepeatInfo]) -> None:
    """Print analysis of found repeats."""
    print("\n" + "=" * 70)
    print("REPEAT ANALYSIS")
    print("=" * 70)

    # Sort by sequence length (longest first)
    sorted_infos = sorted(repeat_infos, key=lambda x: -len(x.sequence))

    print(f"\nFound {len(sorted_infos)} significant repeats with constraint potential\n")

    # Show longest repeats
    print("Longest repeats with different preceding chars:")
    for ri in sorted_infos[:10]:
        print(f"\n  '{ri.sequence}' ({len(ri.sequence)} runes)")
        print(f"  Positions: {ri.positions}")
        print(f"  Preceding: {ri.preceding_chars}")
        print(f"  Constraints: {len(ri.constraints)} pairs")

    # Count total unique constraint pairs
    all_pairs = set()
    for ri in repeat_infos:
        for c1, c2 in ri.constraints:
            pair = tuple(sorted([c1, c2]))
            all_pairs.add(pair)

    print(f"\n\nTotal unique constraint pairs: {len(all_pairs)}")


if __name__ == "__main__":
    # Configuration for overnight run
    MAX_ITERATIONS = 100000
    RESTART_THRESHOLD = 2000
    TEST_LENGTH = 0  # 0 = full LP

    # Load LP
    print("=" * 70)
    print("QUAGMIRE III REPEAT-BASED ATTACK")
    print("=" * 70)

    lp = load_lp()
    test_text = lp if TEST_LENGTH == 0 else lp[:TEST_LENGTH]

    print(f"\nLP length:          {len(lp)} runes")
    print(f"Test length:        {len(test_text)} runes")

    # Find repeats
    print("\nFinding repeats...")
    repeats = find_repeats(test_text, min_length=4, max_length=12)
    print(f"Total repeated sequences: {len(repeats)}")

    # Extract constraint information
    repeat_infos = extract_constraints(test_text, repeats)
    print(f"Repeats with constraint potential: {len(repeat_infos)}")

    # Print analysis
    print_repeat_analysis(test_text, repeat_infos)

    # Prepare data for parallel workers
    repeat_infos_data = [
        {'seq': ri.sequence, 'pos': ri.positions,
         'prev': ri.preceding_chars, 'cons': ri.constraints}
        for ri in repeat_infos
    ]

    # Parallel configuration
    NUM_WORKERS = mp.cpu_count()
    modes = ["beaufort", "vigenere", "variant"]
    # All 29 primers for thorough overnight run
    primer_indices = list(range(ALPHABET_SIZE))

    print("\n" + "=" * 70)
    print("HILL CLIMBING WITH REPEAT CONSTRAINTS")
    print("=" * 70)
    print(f"Modes:              {', '.join(modes)}")
    print(f"Primers:            {len(primer_indices)} (all)")
    print(f"Max iterations:     {MAX_ITERATIONS}")
    print(f"Restart threshold:  {RESTART_THRESHOLD}")
    print(f"Workers:            {NUM_WORKERS}")
    print("Repeat penalty:     enabled")
    print("=" * 70)

    # Build jobs
    jobs = []
    for mode in modes:
        for primer_idx in primer_indices:
            jobs.append((
                test_text,
                repeat_infos_data,
                MAX_ITERATIONS,
                primer_idx,
                mode,
                RESTART_THRESHOLD,
                True,  # use_repeat_penalty
            ))

    print(f"\nRunning {len(jobs)} jobs across {NUM_WORKERS} workers...")

    # Run in parallel
    with mp.Pool(NUM_WORKERS) as pool:
        results = pool.map(run_single_climb, jobs)

    print("All jobs complete.\n")

    # Process results
    best_overall = None
    best_overall_score = float('-inf')
    best_by_mode: dict[str, tuple] = {}

    for result in results:
        alphabet, score, plaintext, mode, primer_idx, pt_ioc, consistent, total_repeats = result

        if mode not in best_by_mode or score > best_by_mode[mode][1]:
            best_by_mode[mode] = result

        if score > best_overall_score:
            best_overall_score = score
            best_overall = result

    # Print results by mode
    print("Best results by mode:")
    for mode in modes:
        if mode in best_by_mode:
            alphabet, score, plaintext, mode_name, primer_idx, pt_ioc, consistent, total = best_by_mode[mode]
            primer_name = c3301.CICADA_ENGLISH_ALPHABET[primer_idx]
            print(f"\n  {mode:8}: primer={primer_name:2} score={score:.1f} IoC={pt_ioc:.3f} repeats={consistent}/{total}")
            print(f"            {runes_to_english(plaintext[:50])}...")

    print("\n" + "=" * 70)
    print("BEST OVERALL RESULT")
    print("=" * 70)

    if best_overall:
        alphabet, score, plaintext, mode, primer_idx, pt_ioc, consistent, total = best_overall
        primer_name = c3301.CICADA_ENGLISH_ALPHABET[primer_idx]

        print(f"Mode:             {mode}")
        print(f"Primer:           {primer_idx} ({primer_name})")
        print(f"Score:            {score:.1f}")
        print(f"IoC:              {pt_ioc:.3f} (normalized)")
        print(f"Consistent reps:  {consistent}/{total}")

        print(f"\nAlphabet (runes):   {''.join(alphabet)}")
        print(f"Alphabet (english): {runes_to_english(''.join(alphabet))}")

        print("\nPlaintext preview (runes):")
        for i in range(0, min(200, len(plaintext)), 50):
            print(f"  {plaintext[i:i+50]}")

        print("\nPlaintext preview (english):")
        english_pt = runes_to_english(plaintext[:200])
        for i in range(0, min(200, len(english_pt)), 50):
            print(f"  {english_pt[i:i+50]}")

    # Save results to file
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"experiments/repeat_attack_results_{timestamp}.txt"

    with open(results_file, "w") as f:
        f.write("QUAGMIRE III REPEAT-BASED ATTACK RESULTS\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write(f"Max iterations: {MAX_ITERATIONS}\n")
        f.write(f"Restart threshold: {RESTART_THRESHOLD}\n")
        f.write(f"Test length: {len(test_text)} runes\n")
        f.write(f"Repeats with constraints: {len(repeat_infos)}\n")
        f.write("\n" + "=" * 70 + "\n")
        f.write("TOP 10 RESULTS BY SCORE\n")
        f.write("=" * 70 + "\n\n")

        # Sort all results by score
        sorted_results = sorted(results, key=lambda x: -x[1])

        for i, result in enumerate(sorted_results[:10]):
            alphabet, score, pt, mode, primer_idx, pt_ioc, consistent, total = result
            primer_name = c3301.CICADA_ENGLISH_ALPHABET[primer_idx]
            f.write(f"Rank {i+1}:\n")
            f.write(f"  Mode: {mode}, Primer: {primer_idx} ({primer_name})\n")
            f.write(f"  Score: {score:.1f}, IoC: {pt_ioc:.3f}\n")
            f.write(f"  Consistent repeats: {consistent}/{total}\n")
            f.write(f"  Alphabet: {''.join(alphabet)}\n")
            f.write(f"  Alphabet (eng): {runes_to_english(''.join(alphabet))}\n")
            f.write("  Plaintext (first 300 chars, english):\n")
            eng_pt = runes_to_english(pt[:300])
            for j in range(0, 300, 60):
                f.write(f"    {eng_pt[j:j+60]}\n")
            f.write("\n")

        # Also save full plaintext for best result
        if best_overall:
            alphabet, score, pt, mode, primer_idx, pt_ioc, consistent, total = best_overall
            f.write("=" * 70 + "\n")
            f.write("FULL PLAINTEXT (BEST RESULT)\n")
            f.write("=" * 70 + "\n")
            f.write(f"Runes:\n{pt}\n\n")
            f.write(f"English:\n{runes_to_english(pt)}\n")

    print(f"\nResults saved to: {results_file}")
