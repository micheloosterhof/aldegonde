# ABOUTME: Hill climber attack on Quagmire III ciphertext autokey cipher (A-Z alphabet)
# ABOUTME: Uses English quadgram scoring to find the mixed alphabet

"""
Hill climber for Quagmire III ciphertext autokey with A-Z alphabet.

Attack approach:
1. Start with random alphabet arrangement
2. Decrypt ciphertext with current key
3. Score result using English quadgrams
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

from aldegonde.stats.ioc import ioc

ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

# English quadgram frequencies (log probabilities) - simplified for demo
# In production, load from file
ENGLISH_QUADGRAMS: dict[str, float] = {}


QUADGRAM_FLOOR = -10.0  # Floor for unseen quadgrams


def load_english_quadgrams() -> None:
    """Load English quadgram frequencies from aldegonde data."""
    global ENGLISH_QUADGRAMS, QUADGRAM_FLOOR
    import math

    try:
        # Use aldegonde's English quadgrams (counts)
        with open("src/aldegonde/data/ngrams/english/quadgrams.txt") as f:
            counts = {}
            total = 0
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    counts[parts[0]] = int(parts[1])
                    total += int(parts[1])

        # Convert to log probabilities
        for qg, count in counts.items():
            ENGLISH_QUADGRAMS[qg] = math.log10(count / total)

        # Floor for unseen quadgrams
        QUADGRAM_FLOOR = math.log10(0.01 / total)
    except FileNotFoundError:
        pass


def score_quadgram(text: str) -> float:
    """Score text using English quadgram log probabilities."""
    if not ENGLISH_QUADGRAMS:
        load_english_quadgrams()

    score = 0.0
    for i in range(len(text) - 3):
        qg = text[i : i + 4]
        score += ENGLISH_QUADGRAMS.get(qg, QUADGRAM_FLOOR)
    return score


def build_lookup_tables(mixed_alphabet: list[str]) -> tuple[dict[str, int], list[str]]:
    """Build lookup tables for an alphabet. Call once per alphabet."""
    char_to_pos = {c: i for i, c in enumerate(mixed_alphabet)}
    pos_to_char = list(mixed_alphabet)
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


def score_ioc_fast(text: str) -> float:
    """Fast IOC scorer - skips validation for speed."""
    counts = Counter(text)
    n = len(text)
    if n < 2:
        return 0.0
    freqsum = sum(v * (v - 1) for v in counts.values())
    return (freqsum / (n * (n - 1))) * 26  # Normalized for 26-letter alphabet


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
    score_fn: Callable[[str], float] = score_ioc_fast,
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
        score_fn: Scoring function

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
    if score_fn_name == "quadgram":
        load_english_quadgrams()  # Ensure loaded in worker
        score_fn = score_quadgram
    else:
        score_fn = score_ioc_fast

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
    pt_ioc = ioc(plaintext) * 26

    return (alphabet, score, plaintext, mode, primer_idx, pt_ioc)


def quagmire3_autokey_encrypt(
    plaintext: str,
    mixed_alphabet: list[str],
    primer_pos: int,
    mode: str = "beaufort",
    autokey: str = "ciphertext",
) -> str:
    """Encrypt with Quagmire III autokey cipher.

    Args:
        plaintext: The plaintext to encrypt
        mixed_alphabet: The mixed alphabet (key)
        primer_pos: Position of primer in alphabet
        mode: "beaufort", "vigenere", or "variant"
        autokey: "ciphertext" or "plaintext"
    """
    char_to_pos, pos_to_char = build_lookup_tables(mixed_alphabet)
    n = len(pos_to_char)
    ciphertext = []
    k_pos = primer_pos

    for p in plaintext:
        if p not in char_to_pos:
            continue
        p_pos = char_to_pos[p]

        if mode == "beaufort":
            # Beaufort: C = K - P, so encrypt same as decrypt
            c_pos = (k_pos - p_pos) % n
        elif mode == "vigenere":
            # Vigenere: C = P + K
            c_pos = (p_pos + k_pos) % n
        else:  # variant beaufort
            # Variant: C = P - K
            c_pos = (p_pos - k_pos) % n

        c = pos_to_char[c_pos]
        ciphertext.append(c)

        # Autokey: next key position
        k_pos = c_pos if autokey == "ciphertext" else p_pos

    return "".join(ciphertext)


def create_test_ciphertext(
    plaintext_file: str = "data/sample_plaintext.txt",
) -> tuple[str, list[str], int, str, str]:
    """Create test ciphertext with known parameters.

    Returns: (ciphertext, alphabet, primer_idx, mode)
    """
    # Try to load plaintext
    try:
        with open(plaintext_file) as f:
            plaintext = f.read().upper()
    except FileNotFoundError:
        # Use default sample text
        plaintext = """
        THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG
        PACKMY BOXWITHFIVEDOZENLIQUORJUGS
        HOWVEXINGLYQUICKDAFTZEBRASJUMP
        THEFIVEBOXINGWIZARDSJUMPQUICKLY
        SPHINXOFBLACKQUARTZJUDGEMYVOW
        """

    # Clean to A-Z only
    plaintext = "".join(c for c in plaintext if c in ALPHABET)

    # Create random mixed alphabet
    mixed_alphabet = ALPHABET.copy()
    random.shuffle(mixed_alphabet)

    # Use rare letter as primer (Q, Z, X, J are rare)
    # Find position of Q in mixed alphabet
    primer_char = "Q"
    primer_idx = mixed_alphabet.index(primer_char)

    # Choose mode
    mode = "beaufort"

    # Encrypt
    ciphertext = quagmire3_autokey_encrypt(
        plaintext, mixed_alphabet, primer_idx, mode, "ciphertext"
    )

    return ciphertext, mixed_alphabet, primer_idx, mode, plaintext


if __name__ == "__main__":
    # Configuration - more aggressive
    MAX_ITERATIONS = 100000
    RESTART_THRESHOLD = 1000

    # Create test ciphertext
    print("=" * 70)
    print("CREATING TEST CIPHERTEXT")
    print("=" * 70)

    random.seed(42)  # Reproducible
    ciphertext, true_alphabet, true_primer, true_mode, plaintext = (
        create_test_ciphertext()
    )

    print(f"Plaintext length:  {len(plaintext)}")
    print(f"Ciphertext length: {len(ciphertext)}")
    print(f"True mode:         {true_mode}")
    print(f"True primer index: {true_primer} ({ALPHABET[true_primer]})")
    print(f"True alphabet:     {''.join(true_alphabet)}")
    print(f"\nPlaintext preview:  {plaintext[:60]}...")
    print(f"Ciphertext preview: {ciphertext[:60]}...")

    # Save ciphertext for analysis
    with open("experiments/test_ciphertext.txt", "w") as f:
        f.write(ciphertext)
    print("\nCiphertext saved to experiments/test_ciphertext.txt")

    # Parallel configuration
    NUM_WORKERS = mp.cpu_count()

    # Focus on correct mode for testing (beaufort with primer 0)
    # Run 10 parallel instances with different random seeds
    modes = ["beaufort"]
    primer_indices = [0]  # Just the correct primer
    num_parallel_runs = 10
    total_combos = num_parallel_runs

    print("\n" + "=" * 70)
    print("QUAGMIRE III HILL CLIMBER (A-Z)")
    print("=" * 70)
    print(f"Ciphertext length:  {len(ciphertext)}")
    print(f"Modes:              {', '.join(modes)}")
    print(f"Primers:            {len(primer_indices)} (all)")
    print(f"Total combinations: {total_combos}")
    print(f"Max iterations:     {MAX_ITERATIONS}")
    print(f"Restart threshold:  {RESTART_THRESHOLD}")
    print(f"Est. restarts/run:  ~{MAX_ITERATIONS // RESTART_THRESHOLD}")
    print("Autokey:            ciphertext")
    print("Scoring:            quadgram")
    print(f"Workers:            {NUM_WORKERS}")
    print("=" * 70)

    # Load quadgrams before forking workers
    load_english_quadgrams()
    print(f"Loaded {len(ENGLISH_QUADGRAMS)} quadgrams")

    # Build list of all jobs - multiple runs with same params but different random states
    jobs = []
    for _ in range(num_parallel_runs):
        for mode in modes:
            for primer_idx in primer_indices:
                jobs.append(
                    (
                        ciphertext,
                        MAX_ITERATIONS,
                        primer_idx,
                        mode,
                        "ciphertext",
                        RESTART_THRESHOLD,
                        "quadgram",
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
        alphabet, score, pt, mode, primer_idx, pt_ioc = result

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
            alphabet, score, pt, mode_name, primer_idx, pt_ioc = best_by_mode[mode]
            print(
                f"Best {mode:8}: primer={ALPHABET[primer_idx]} score={score:.3f} IoC={pt_ioc:.3f}"
            )
            print(f"  Plaintext: {pt[:60]}...")

    print("\n" + "=" * 70)
    print("BEST OVERALL RESULT")
    print("=" * 70)

    if best_overall:
        alphabet, score, pt, mode, primer_idx, pt_ioc = best_overall
        print(f"Mode: {mode}")
        print("Autokey: ciphertext")
        print(f"Primer index: {primer_idx} ({ALPHABET[primer_idx]})")
        print(f"Score: {score:.2f}")
        print(f"IoC: {pt_ioc:.3f} (normalized, random=1.0)")
        print(f"\nRecovered alphabet: {''.join(alphabet)}")
        print(f"True alphabet:      {''.join(true_alphabet)}")
        print(f"Match: {alphabet == true_alphabet}")
        print("\nRecovered plaintext preview:")
        print(pt[:200])
        print("\nTrue plaintext preview:")
        print(plaintext[:200])
