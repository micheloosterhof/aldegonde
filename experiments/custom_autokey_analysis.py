# ABOUTME: Analyze properties of custom alphabet autokey ciphers
# ABOUTME: Investigates doublet suppression in keyed Beaufort/Vigenère autokey

"""
Analysis of Custom Alphabet Autokey Ciphers

Key question: Does a Quagmire-style autokey produce ciphertext with:
1. Near-random distribution
2. Suppressed doublets
3. Properties matching the Liber Primus?
"""

from collections import Counter
from collections.abc import Sequence
import random
from typing import TypeVar

T = TypeVar("T")


def mixed_alphabet(keyword: str, alphabet: str) -> str:
    """Create a mixed alphabet from a keyword."""
    seen = set()
    result = []
    for c in keyword.upper():
        if c in alphabet and c not in seen:
            result.append(c)
            seen.add(c)
    for c in alphabet:
        if c not in seen:
            result.append(c)
            seen.add(c)
    return "".join(result)


def quagmire3_autokey_encrypt(
    plaintext: str,
    keyword: str,
    primer: str,
    alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
) -> str:
    """
    Quagmire III ciphertext autokey encryption.

    - Mixed alphabet from keyword for both row and column
    - Beaufort-style: C = K - P (in mixed alphabet positions)
    - Ciphertext autokey: next key = current ciphertext
    """
    mixed = mixed_alphabet(keyword, alphabet)
    n = len(alphabet)

    # Map characters to positions in mixed alphabet
    char_to_pos = {c: i for i, c in enumerate(mixed)}
    pos_to_char = {i: c for i, c in enumerate(mixed)}

    ciphertext = []
    key_char = primer

    for p in plaintext.upper():
        if p not in char_to_pos:
            continue
        p_pos = char_to_pos[p]
        k_pos = char_to_pos[key_char]
        # Beaufort: C = K - P
        c_pos = (k_pos - p_pos) % n
        c = pos_to_char[c_pos]
        ciphertext.append(c)
        key_char = c  # Ciphertext autokey

    return "".join(ciphertext)


def quagmire3_autokey_decrypt(
    ciphertext: str,
    keyword: str,
    primer: str,
    alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
) -> str:
    """
    Quagmire III ciphertext autokey decryption.

    Beaufort is self-reciprocal: P = K - C
    """
    mixed = mixed_alphabet(keyword, alphabet)
    n = len(alphabet)

    char_to_pos = {c: i for i, c in enumerate(mixed)}
    pos_to_char = {i: c for i, c in enumerate(mixed)}

    plaintext = []
    key_char = primer

    for c in ciphertext.upper():
        if c not in char_to_pos:
            continue
        c_pos = char_to_pos[c]
        k_pos = char_to_pos[key_char]
        # Beaufort decrypt: P = K - C
        p_pos = (k_pos - c_pos) % n
        p = pos_to_char[p_pos]
        plaintext.append(p)
        key_char = c  # Ciphertext autokey

    return "".join(plaintext)


def count_doublets(text: Sequence[T]) -> tuple[int, int, float]:
    """Count doublets and return (count, possible, rate)."""
    if len(text) < 2:
        return 0, 0, 0.0
    count = sum(1 for i in range(len(text) - 1) if text[i] == text[i + 1])
    possible = len(text) - 1
    return count, possible, count / possible if possible > 0 else 0.0


def ioc(text: Sequence[T]) -> float:
    """Calculate Index of Coincidence."""
    counts = Counter(text)
    n = len(text)
    if n < 2:
        return 0.0
    numerator = sum(c * (c - 1) for c in counts.values())
    denominator = n * (n - 1)
    return numerator / denominator


def analyze_autokey_properties(
    plaintext: str,
    keyword: str,
    primer: str,
    alphabet: str = "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
) -> dict:
    """Analyze the statistical properties of autokey ciphertext."""
    ciphertext = quagmire3_autokey_encrypt(plaintext, keyword, primer, alphabet)

    mixed = mixed_alphabet(keyword, alphabet)
    identity_char = mixed[0]  # Character at position 0 in mixed alphabet

    # Count identity character in plaintext
    plain_clean = "".join(c for c in plaintext.upper() if c in alphabet)
    identity_count = plain_clean.count(identity_char)
    identity_rate = identity_count / len(plain_clean) if plain_clean else 0

    # Doublets in ciphertext
    ct_doublets, ct_possible, ct_doublet_rate = count_doublets(ciphertext)

    # Doublets in plaintext
    pt_doublets, pt_possible, pt_doublet_rate = count_doublets(plain_clean)

    return {
        "keyword": keyword,
        "primer": primer,
        "mixed_alphabet": mixed,
        "identity_char": identity_char,
        "plaintext_length": len(plain_clean),
        "ciphertext_length": len(ciphertext),
        "plaintext_ioc": ioc(plain_clean),
        "ciphertext_ioc": ioc(ciphertext),
        "plaintext_doublet_rate": pt_doublet_rate,
        "ciphertext_doublet_rate": ct_doublet_rate,
        "identity_char_frequency": identity_rate,
        "expected_random_doublet_rate": 1 / len(alphabet),
        "doublet_suppression_factor": (1 / len(alphabet)) / ct_doublet_rate if ct_doublet_rate > 0 else float('inf'),
    }


def generate_english_like_text(length: int) -> str:
    """Generate pseudo-English text for testing."""
    # Approximate English letter frequencies
    freq = {
        'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0, 'N': 6.7,
        'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3, 'L': 4.0, 'C': 2.8,
        'U': 2.8, 'M': 2.4, 'W': 2.4, 'F': 2.2, 'G': 2.0, 'Y': 2.0,
        'P': 1.9, 'B': 1.5, 'V': 1.0, 'K': 0.8, 'J': 0.15, 'X': 0.15,
        'Q': 0.10, 'Z': 0.07
    }
    letters = list(freq.keys())
    weights = list(freq.values())
    return "".join(random.choices(letters, weights=weights, k=length))


if __name__ == "__main__":
    # Test with English-like text
    print("=" * 70)
    print("Custom Alphabet Autokey Analysis")
    print("=" * 70)

    # Generate test plaintext
    plaintext = generate_english_like_text(10000)

    print(f"\nPlaintext length: {len(plaintext)}")
    print(f"Plaintext IoC: {ioc(plaintext):.4f} (English ~0.067)")
    print(f"Plaintext doublet rate: {count_doublets(plaintext)[2]:.4f}")

    # Test different keywords
    keywords = ["DIVINITY", "FIRFUMFERENFE", "CICADA", "PRIMUS", "A"]

    for kw in keywords:
        print(f"\n--- Keyword: {kw} ---")
        result = analyze_autokey_properties(plaintext, kw, "A")

        print(f"Mixed alphabet: {result['mixed_alphabet'][:15]}...")
        print(f"Identity char (pos 0): {result['identity_char']}")
        print(f"Identity char frequency in plaintext: {result['identity_char_frequency']:.4f}")
        print(f"Ciphertext IoC: {result['ciphertext_ioc']:.4f} (random = {1/26:.4f})")
        print(f"Ciphertext doublet rate: {result['ciphertext_doublet_rate']:.4f}")
        print(f"Expected random: {result['expected_random_doublet_rate']:.4f}")
        print(f"Doublet suppression: {result['doublet_suppression_factor']:.1f}x")

    # What if we deliberately avoid the identity character?
    print("\n" + "=" * 70)
    print("Test: Plaintext that avoids identity character")
    print("=" * 70)

    keyword = "DIVINITY"
    mixed = mixed_alphabet(keyword, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    identity = mixed[0]  # 'D' for DIVINITY

    # Create plaintext that avoids 'D'
    plaintext_no_d = plaintext.replace(identity, "")

    result = analyze_autokey_properties(plaintext_no_d, keyword, "A")
    print(f"\nKeyword: {keyword}")
    print(f"Identity char: {identity}")
    print(f"Plaintext with {identity} removed")
    print(f"Ciphertext doublet rate: {result['ciphertext_doublet_rate']:.6f}")
    print(f"Doublet suppression: {result['doublet_suppression_factor']:.1f}x")

    print("\n" + "=" * 70)
    print("Key Finding:")
    print("=" * 70)
    print("""
In ciphertext autokey with a keyed tableau (Quagmire III style):
- Doublet rate = frequency of identity character in plaintext
- Identity character = first letter of mixed alphabet = first letter of keyword

If the plaintext rarely contains the first letter of the keyword,
ciphertext will have very few doublets.

For Liber Primus with 5-6x doublet suppression:
- The identity character appears ~0.6% of the time (vs ~3.5% expected)
- This could happen if:
  1. The keyword starts with a rare letter in the plaintext
  2. The plaintext is encoded to avoid a specific character
  3. Multiple encryption layers are involved
""")
