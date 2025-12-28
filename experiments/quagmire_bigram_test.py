# ABOUTME: Test bigram patterns in Quagmire III autokey ciphertext
# ABOUTME: Compare with LP ciphertext bigram structure

"""
Generate Quagmire III autokey ciphertext and analyze bigram patterns.
"""

import sys
sys.path.insert(0, 'src')

from collections import Counter
from aldegonde import c3301
from aldegonde.grams import bigram_diagram

# Gematria Primus mapping
GEMATRIA_RULES = [
    ("ing", "ᛝ"), ("ng", "ᛝ"), ("th", "ᚦ"), ("ea", "ᛠ"), ("eo", "ᛇ"),
    ("oe", "ᛟ"), ("ae", "ᚫ"), ("ia", "ᛡ"), ("io", "ᛡ"),
    ("f", "ᚠ"), ("u", "ᚢ"), ("o", "ᚩ"), ("r", "ᚱ"), ("c", "ᚳ"),
    ("k", "ᚳ"), ("g", "ᚷ"), ("w", "ᚹ"), ("h", "ᚻ"), ("n", "ᚾ"),
    ("i", "ᛁ"), ("j", "ᛄ"), ("p", "ᛈ"), ("x", "ᛉ"), ("s", "ᛋ"),
    ("z", "ᛋ"), ("t", "ᛏ"), ("b", "ᛒ"), ("e", "ᛖ"), ("m", "ᛗ"),
    ("l", "ᛚ"), ("d", "ᛞ"), ("a", "ᚪ"), ("y", "ᚣ"), ("q", "ᚳ"),
    ("v", "ᚢ"),
]

ALPHABET = c3301.CICADA_ALPHABET


def english_to_runeglish(text: str) -> str:
    """Convert English text to Runeglish."""
    text = text.lower()
    result = []
    i = 0
    while i < len(text):
        matched = False
        for pattern, rune in GEMATRIA_RULES:
            if text[i:i+len(pattern)] == pattern:
                result.append(rune)
                i += len(pattern)
                matched = True
                break
        if not matched:
            i += 1
    return "".join(result)


def mixed_alphabet(keyword: str, alphabet: list[str]) -> list[str]:
    """Create mixed alphabet from keyword."""
    seen = set()
    result = []
    for c in keyword:
        if c in alphabet and c not in seen:
            result.append(c)
            seen.add(c)
    for c in alphabet:
        if c not in seen:
            result.append(c)
            seen.add(c)
    return result


def quagmire3_autokey_encrypt(
    plaintext: str,
    keyword: str,
    primer: str,
    alphabet: list[str],
) -> str:
    """Quagmire III ciphertext autokey (Beaufort mode)."""
    mixed = mixed_alphabet(keyword, alphabet)
    n = len(alphabet)
    char_to_pos = {c: i for i, c in enumerate(mixed)}
    pos_to_char = {i: c for i, c in enumerate(mixed)}

    ciphertext = []
    key_char = primer

    for p in plaintext:
        if p not in char_to_pos:
            continue
        p_pos = char_to_pos[p]
        k_pos = char_to_pos[key_char]
        c_pos = (k_pos - p_pos) % n  # Beaufort
        c = pos_to_char[c_pos]
        ciphertext.append(c)
        key_char = c  # ciphertext autokey

    return "".join(ciphertext)


def load_sample_english() -> str:
    """Load sample English text."""
    try:
        with open("/usr/share/dict/words") as f:
            return f.read()[:50000]
    except:
        return "the quick brown fox jumps over the lazy dog " * 1000


if __name__ == "__main__":
    # Load and convert English
    english = load_sample_english()
    runeglish = english_to_runeglish(english)

    # Use NG-first keyword (matches LP doublet rate best)
    keyword = "ᛝᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛟᛞᚪᚫᚣᛡᛠ"

    # Encrypt
    ciphertext = quagmire3_autokey_encrypt(runeglish, keyword, keyword[0], ALPHABET)

    print("=" * 70)
    print("Quagmire III Autokey Ciphertext - Bigram Analysis")
    print("=" * 70)
    print(f"\nPlaintext length: {len(runeglish)} runes")
    print(f"Ciphertext length: {len(ciphertext)} runes")

    # Count doublets
    doublets = sum(1 for i in range(len(ciphertext)-1) if ciphertext[i] == ciphertext[i+1])
    print(f"Doublets: {doublets} ({doublets/(len(ciphertext)-1)*100:.3f}%)")

    print("\n" + "=" * 70)
    print("BIGRAM DIAGRAM (Quagmire III Autokey Ciphertext)")
    print("=" * 70 + "\n")

    bigram_diagram.print_auto_bigram_diagram(ciphertext, alphabet=ALPHABET)

    # Now compare with plaintext bigrams
    print("\n" + "=" * 70)
    print("BIGRAM DIAGRAM (Runeglish Plaintext for comparison)")
    print("=" * 70 + "\n")

    bigram_diagram.print_auto_bigram_diagram(runeglish, alphabet=ALPHABET)
