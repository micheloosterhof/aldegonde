# ABOUTME: Hill climber attack on Quagmire III ciphertext autokey cipher
# ABOUTME: Uses runeglish quadgram scoring to find the mixed alphabet

"""
Hill climber for Quagmire III ciphertext autokey.

Attack approach:
1. Start with random alphabet arrangement
2. Decrypt LP ciphertext with current key
3. Score result using runeglish quadgrams
4. Swap two letters in alphabet
5. Keep if score improves, else revert
6. Repeat with random restarts
"""

import sys  # noqa: I001

sys.path.insert(0, "src")

import random  # noqa: I001
import multiprocessing as mp
from collections import Counter
from collections.abc import Callable

from aldegonde import c3301
from aldegonde.stats.ioc import ioc

ALPHABET = c3301.CICADA_ALPHABET.copy()


def build_lookup_tables(mixed_alphabet: list[str]) -> tuple[dict[str, int], list[str]]:
    """Build lookup tables for an alphabet. Call once per alphabet."""
    char_to_pos = {c: i for i, c in enumerate(mixed_alphabet)}
    pos_to_char = list(mixed_alphabet)  # List is faster than dict for int keys
    return char_to_pos, pos_to_char


def quagmire3_autokey_decrypt(
    ciphertext: str,
    char_to_pos: dict[str, int],
    pos_to_char: list[str],
    primer_pos: int,
    mode: str = "beaufort",
    autokey: str = "ciphertext",
) -> str:
    """Decrypt Quagmire III autokey cipher.

    Args:
        ciphertext: The ciphertext to decrypt
        char_to_pos: Precomputed char->position lookup
        pos_to_char: Precomputed position->char lookup (list)
        primer_pos: Position of primer in alphabet
        mode: "beaufort" (C = K - P), "vigenere" (C = P + K), or "variant" (C = P - K)
        autokey: "ciphertext" or "plaintext"
    """
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
        else:  # variant beaufort
            p_pos = (c_pos + k_pos) % n

        p = pos_to_char[p_pos]
        plaintext.append(p)

        # Autokey: next key position
        # ciphertext autokey feeds back the cipher position, plaintext the plain
        k_pos = c_pos if autokey == "ciphertext" else p_pos

    return "".join(plaintext)


def score_quadgram(text: str) -> float:
    """Score text using runeglish quadgrams."""
    return c3301.quadgramscore(text)


def score_ioc(text: str) -> float:
    """Score text using normalized IOC (higher = more language-like)."""
    return ioc(text) * 29  # Normalized: random=1.0, language>1.0


def score_ioc_fast(text: str) -> float:
    """Fast IOC scorer - skips validation for speed."""
    counts = Counter(text)
    n = len(text)
    if n < 2:
        return 0.0
    freqsum = sum(v * (v - 1) for v in counts.values())
    return (freqsum / (n * (n - 1))) * 29  # Normalized


def random_alphabet() -> list[str]:
    """Generate random alphabet arrangement."""
    alpha = ALPHABET.copy()
    random.shuffle(alpha)
    return alpha


def swap_two(alphabet: list[str]) -> list[str]:
    """Swap two random positions in alphabet."""
    new_alpha = alphabet.copy()
    i, j = random.sample(range(len(alphabet)), 2)
    new_alpha[i], new_alpha[j] = new_alpha[j], new_alpha[i]
    return new_alpha


def hill_climb(
    ciphertext: str,
    max_iterations: int = 10000,
    primer_idx: int = 0,
    mode: str = "beaufort",
    autokey: str = "ciphertext",
    *,
    verbose: bool = True,
    restart_threshold: int = 500,
    score_fn: Callable[[str], float] = score_quadgram,
) -> tuple[list[str], float, str]:
    """
    Hill climb to find best alphabet.

    Args:
        ciphertext: The ciphertext to attack
        max_iterations: Maximum iterations per climb
        primer_idx: Index of primer in mixed alphabet
        mode: "beaufort", "vigenere", or "variant"
        autokey: "ciphertext" or "plaintext"
        verbose: Print progress
        restart_threshold: Restart after this many iterations without improvement
        score_fn: Scoring function (score_quadgram or score_ioc)

    Returns: (best_alphabet, best_score, best_plaintext)
    """
    # Start with random alphabet
    current_alphabet = random_alphabet()
    char_to_pos, pos_to_char = build_lookup_tables(current_alphabet)

    current_plaintext = quagmire3_autokey_decrypt(
        ciphertext, char_to_pos, pos_to_char, primer_idx, mode, autokey
    )
    current_score = score_fn(current_plaintext)

    best_alphabet = current_alphabet.copy()
    best_score = current_score
    best_plaintext = current_plaintext

    no_improve_count = 0

    for iteration in range(max_iterations):
        # Try swapping two letters
        new_alphabet = swap_two(current_alphabet)
        new_char_to_pos, new_pos_to_char = build_lookup_tables(new_alphabet)

        new_plaintext = quagmire3_autokey_decrypt(
            ciphertext, new_char_to_pos, new_pos_to_char, primer_idx, mode, autokey
        )
        new_score = score_fn(new_plaintext)

        if new_score > current_score:
            current_alphabet = new_alphabet
            char_to_pos, pos_to_char = new_char_to_pos, new_pos_to_char
            current_score = new_score
            current_plaintext = new_plaintext
            no_improve_count = 0

            if new_score > best_score:
                best_alphabet = new_alphabet.copy()
                best_score = new_score
                best_plaintext = new_plaintext

                if verbose:
                    print(f"[{iteration:5d}] Score: {best_score:.2f}")
                    print(f"        {best_plaintext[:60]}...")
        else:
            no_improve_count += 1

        # Random restart if stuck
        if no_improve_count > restart_threshold:
            current_alphabet = random_alphabet()
            char_to_pos, pos_to_char = build_lookup_tables(current_alphabet)
            current_plaintext = quagmire3_autokey_decrypt(
                ciphertext, char_to_pos, pos_to_char, primer_idx, mode, autokey
            )
            current_score = score_fn(current_plaintext)
            no_improve_count = 0
            if verbose:
                print(f"[{iteration:5d}] Random restart")

    return best_alphabet, best_score, best_plaintext


def run_single_climb(args: tuple) -> tuple:
    """Worker function for parallel execution."""
    (
        ciphertext,
        max_iterations,
        primer_idx,
        mode,
        autokey,
        restart_threshold,
        score_fn_name,
    ) = args

    # Select scoring function by name (can't pickle lambdas)
    if score_fn_name == "ioc_fast":
        score_fn = score_ioc_fast
    elif score_fn_name == "ioc":
        score_fn = score_ioc
    else:
        score_fn = score_quadgram

    alphabet, score, plaintext = hill_climb(
        ciphertext,
        max_iterations=max_iterations,
        primer_idx=primer_idx,
        mode=mode,
        autokey=autokey,
        verbose=False,
        restart_threshold=restart_threshold,
        score_fn=score_fn,
    )

    # Calculate IOC for result
    pt_ioc = ioc(plaintext) * 29

    return (alphabet, score, plaintext, mode, primer_idx, pt_ioc)


def load_lp() -> str:
    """Load LP ciphertext."""
    with open("data/page0-58.txt") as f:
        text = f.read()
    return "".join(c for c in text if c in ALPHABET)


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


if __name__ == "__main__":
    # Configuration
    MAX_ITERATIONS = 20000
    RESTART_THRESHOLD = 500
    TEST_LENGTH = 729  # First chapter size
    SCORE_FN = score_ioc_fast  # score_quadgram, score_ioc, or score_ioc_fast
    SCORE_NAME = (
        "IOC-fast"
        if score_ioc_fast == SCORE_FN
        else ("IOC" if score_ioc == SCORE_FN else "quadgram")
    )

    # Load LP
    lp = load_lp()

    # Use first segment for faster testing
    segments = lp.split("$") if "$" in lp else [lp]
    test_text = lp[:TEST_LENGTH]

    # All variations to test - ciphertext autokey only (plaintext gives more repeats)
    modes = ["vigenere", "beaufort", "variant"]
    primer_indices = list(range(29))  # All 29 primers
    total_combos = len(modes) * len(primer_indices)

    # Parallel configuration
    NUM_WORKERS = mp.cpu_count()

    # Print configuration
    print("=" * 70)
    print("QUAGMIRE III HILL CLIMBER (PARALLEL)")
    print("=" * 70)
    print(f"LP length:          {len(lp)} runes")
    print(f"Test length:        {len(test_text)} runes")
    print(f"Modes:              {', '.join(modes)}")
    print(f"Primers:            {len(primer_indices)} (all)")
    print(f"Total combinations: {total_combos}")
    print(f"Max iterations:     {MAX_ITERATIONS}")
    print(f"Restart threshold:  {RESTART_THRESHOLD}")
    print(f"Est. restarts/run:  ~{MAX_ITERATIONS // RESTART_THRESHOLD}")
    print("Autokey:            ciphertext")
    print(f"Scoring:            {SCORE_NAME}")
    print(f"Workers:            {NUM_WORKERS}")
    print("=" * 70)

    # Build list of all jobs
    jobs = []
    for mode in modes:
        for primer_idx in primer_indices:
            jobs.append(
                (
                    test_text,
                    MAX_ITERATIONS,
                    primer_idx,
                    mode,
                    "ciphertext",
                    RESTART_THRESHOLD,
                    SCORE_NAME.lower().replace("-", "_"),  # Convert to function name
                )
            )

    print(f"\nRunning {len(jobs)} jobs across {NUM_WORKERS} workers...")

    # Run in parallel
    with mp.Pool(NUM_WORKERS) as pool:
        results = pool.map(run_single_climb, jobs)

    print("All jobs complete.\n")

    # Process results
    best_overall = None
    best_overall_score = float("-inf")
    best_by_mode: dict[str, tuple] = {}

    for result in results:
        alphabet, score, plaintext, mode, primer_idx, pt_ioc = result

        # Track best per mode
        if mode not in best_by_mode or score > best_by_mode[mode][1]:
            best_by_mode[mode] = result

        # Track overall best
        if score > best_overall_score:
            best_overall_score = score
            best_overall = result

    # Print results by mode
    for mode in modes:
        if mode in best_by_mode:
            alphabet, score, plaintext, mode_name, primer_idx, pt_ioc = best_by_mode[
                mode
            ]
            primer_name = c3301.CICADA_ENGLISH_ALPHABET[primer_idx]
            print(
                f"Best {mode:8}: primer={primer_name:2} score={score:.3f} IoC={pt_ioc:.3f}"
            )
            print(f"  English: {runes_to_english(plaintext[:60])}...")

    print("\n" + "=" * 70)
    print("BEST OVERALL RESULT")
    print("=" * 70)

    if best_overall:
        alphabet, score, plaintext, mode, primer_idx, pt_ioc = best_overall
        primer_name = c3301.CICADA_ENGLISH_ALPHABET[primer_idx]
        print(f"Mode: {mode}")
        print("Autokey: ciphertext")
        print(f"Primer index: {primer_idx} ({primer_name} = {alphabet[primer_idx]})")
        print(f"Score: {score:.2f}")
        print(f"IoC: {pt_ioc:.3f} (normalized, random=1.0)")
        print(f"\nAlphabet (runes): {''.join(alphabet)}")
        print(f"Alphabet (english): {runes_to_english(''.join(alphabet))}")
        print("\nPlaintext preview (runes):")
        print(plaintext[:200])
        print("\nPlaintext preview (english):")
        print(runes_to_english(plaintext[:200]))
