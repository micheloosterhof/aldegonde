# ABOUTME: Generates Quagmire III ciphertext and runs full cryptanalysis
# ABOUTME: Tests IOC, bigrams, repeats, kappa, and other statistics

"""
Generate Quagmire III autokey ciphertext with A-Z alphabet and analyze it.
"""

import sys  # noqa: I001

sys.path.insert(0, "src")

import random  # noqa: I001

from aldegonde.stats import dist, entropy, repeats
from aldegonde.stats.ioc import ioc as ioc_func
from aldegonde.stats.kappa import print_kappa
from aldegonde.stats.ioc import print_ioc_statistics
from aldegonde.grams import bigram_diagram
from aldegonde.maths import factor
from aldegonde.analysis import friedman

ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


def build_lookup_tables(mixed_alphabet: list[str]) -> tuple[dict[str, int], list[str]]:
    """Build lookup tables for an alphabet."""
    char_to_pos = {c: i for i, c in enumerate(mixed_alphabet)}
    pos_to_char = list(mixed_alphabet)
    return char_to_pos, pos_to_char


def quagmire3_autokey_encrypt(
    plaintext: str,
    mixed_alphabet: list[str],
    primer_pos: int,
    mode: str = "beaufort",
    autokey: str = "ciphertext",
) -> str:
    """Encrypt with Quagmire III autokey cipher."""
    char_to_pos, pos_to_char = build_lookup_tables(mixed_alphabet)
    n = len(pos_to_char)
    ciphertext = []
    k_pos = primer_pos

    for p in plaintext:
        if p not in char_to_pos:
            continue
        p_pos = char_to_pos[p]

        if mode == "beaufort":
            c_pos = (k_pos - p_pos) % n
        elif mode == "vigenere":
            c_pos = (p_pos + k_pos) % n
        else:  # variant
            c_pos = (p_pos - k_pos) % n

        c = pos_to_char[c_pos]
        ciphertext.append(c)

        k_pos = c_pos if autokey == "ciphertext" else p_pos

    return "".join(ciphertext)


def load_plaintext(filename: str = "data/sample_plaintext.txt") -> str:
    """Load and clean plaintext."""
    with open(filename) as f:
        text = f.read().upper()
    return "".join(c for c in text if c in ALPHABET)


def analyze_text(text: str, alphabet: list[str], label: str = "TEXT") -> None:
    """Run full cryptanalysis on text."""
    print(f"\n{'=' * 70}")
    print(f"ANALYSIS: {label}")
    print(f"{'=' * 70}")

    print(f"\nLength: {len(text)} characters")
    print(f"Prime factors: {factor.prime_factors(len(text))}")
    print(f"Factor pairs: {factor.factor_pairs(len(text))[1:-1]}")

    print(f"\nUsed alphabet: {sorted(set(text))} ({len(set(text))} symbols)")

    print(f"\nFirst 100 chars: {text[:100]}")

    print("\n--- FREQUENCY DISTRIBUTION ---")
    dist.print_dist(text)

    print("\n--- ENTROPY ---")
    entropy.shannon_entropy(text)

    print("\n--- IOC STATISTICS ---")
    print_ioc_statistics(text, alphabetsize=26)

    print("\n--- BIGRAM DIAGRAM ---")
    bigram_diagram.print_auto_bigram_diagram(text, alphabet=alphabet)

    print("\n--- KAPPA TESTS ---")
    print_kappa(text, trace=False)
    print_kappa(text, length=2, trace=False)
    print_kappa(text, length=3, trace=False)

    print("\n--- FRIEDMAN TEST ---")
    friedman.friedman_test(text, maxperiod=34)

    print("\n--- REPEAT STATISTICS ---")
    repeats.print_repeat_statistics(text, minimum=2)
    repeats.print_repeat_positions(text, minimum=4)


if __name__ == "__main__":
    random.seed(42)  # Reproducible

    # Load plaintext
    print("Loading plaintext...")
    plaintext = load_plaintext()
    print(f"Plaintext length: {len(plaintext)} characters")

    # Create mixed alphabet
    mixed_alphabet = ALPHABET.copy()
    random.shuffle(mixed_alphabet)

    # Use Q as primer (rare letter, position in mixed alphabet)
    primer_char = "Q"
    primer_idx = mixed_alphabet.index(primer_char)

    # Encryption parameters
    mode = "beaufort"
    autokey = "ciphertext"

    print("\n" + "=" * 70)
    print("ENCRYPTION PARAMETERS")
    print("=" * 70)
    print(f"Mode:           {mode}")
    print(f"Autokey:        {autokey}")
    print(f"Primer:         {primer_char} (index {primer_idx} in mixed alphabet)")
    print(f"Mixed alphabet: {''.join(mixed_alphabet)}")
    print(f"Standard:       {''.join(ALPHABET)}")

    # Encrypt
    ciphertext = quagmire3_autokey_encrypt(
        plaintext, mixed_alphabet, primer_idx, mode, autokey
    )

    print(f"\nPlaintext preview:  {plaintext[:60]}...")
    print(f"Ciphertext preview: {ciphertext[:60]}...")

    # Save ciphertext
    with open("experiments/test_ciphertext.txt", "w") as f:
        f.write(ciphertext)
    print("\nCiphertext saved to experiments/test_ciphertext.txt")

    # Save key info
    with open("experiments/test_key.txt", "w") as f:
        f.write(f"mode={mode}\n")
        f.write(f"autokey={autokey}\n")
        f.write(f"primer_char={primer_char}\n")
        f.write(f"primer_idx={primer_idx}\n")
        f.write(f"mixed_alphabet={''.join(mixed_alphabet)}\n")
        f.write(f"plaintext_length={len(plaintext)}\n")
    print("Key info saved to experiments/test_key.txt")

    # Analyze plaintext
    analyze_text(plaintext, ALPHABET, "PLAINTEXT")

    # Analyze ciphertext
    analyze_text(ciphertext, ALPHABET, "CIPHERTEXT")

    # Compare
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)

    pt_ioc = ioc_func(plaintext) * 26
    ct_ioc = ioc_func(ciphertext) * 26

    print(f"Plaintext IoC (normalized):  {pt_ioc:.3f}")
    print(f"Ciphertext IoC (normalized): {ct_ioc:.3f}")
    print("Random expectation:          1.000")
    print("English expectation:         ~1.73")

    # Check for patterns that might help cryptanalysis
    print("\n--- AUTOKEY CHARACTERISTICS ---")
    print("Ciphertext autokey creates dependencies between adjacent characters.")
    print("This may create distinctive patterns in bigram distributions.")
