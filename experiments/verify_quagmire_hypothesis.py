# ABOUTME: Verify Quagmire III autokey produces LP-like ciphertext properties
# ABOUTME: Tests if the hypothesis matches observed LP statistics

"""
Verification Experiment:

1. Take English plaintext
2. Convert to Runeglish (29 runes via Gematria Primus)
3. Apply Quagmire III ciphertext autokey with various keywords
4. Check if ciphertext has LP-like properties:
   - Doublet rate ~0.6-0.7%
   - Flat frequency distribution (IoC ≈ 1/29)
   - No pattern after single-key autokey decryption (still random)

If these match, the hypothesis is confirmed.
"""

import sys
sys.path.insert(0, 'src')

from collections import Counter
import random
from typing import Sequence

from aldegonde import c3301

# Gematria Primus mapping (digraphs first)
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

ALPHABET = c3301.CICADA_ALPHABET  # 29 runes


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
    mode: str = "beaufort",
    autokey: str = "ciphertext",
) -> str:
    """
    Quagmire III autokey encryption.

    Args:
        plaintext: Runeglish plaintext
        keyword: Keyword for mixed alphabet
        primer: Single rune primer
        alphabet: Base alphabet (29 runes)
        mode: "beaufort" or "vigenere"
        autokey: "ciphertext" or "plaintext"
    """
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

        if mode == "beaufort":
            c_pos = (k_pos - p_pos) % n
        else:  # vigenere
            c_pos = (k_pos + p_pos) % n

        c = pos_to_char[c_pos]
        ciphertext.append(c)

        if autokey == "ciphertext":
            key_char = c
        else:  # plaintext
            key_char = p

    return "".join(ciphertext)


def simple_autokey_decrypt(
    ciphertext: str,
    primer: str,
    alphabet: list[str],
    mode: str = "beaufort",
) -> str:
    """Simple autokey decryption (no keyword, standard alphabet)."""
    n = len(alphabet)
    char_to_pos = {c: i for i, c in enumerate(alphabet)}
    pos_to_char = {i: c for i, c in enumerate(alphabet)}

    plaintext = []
    key_char = primer

    for c in ciphertext:
        if c not in char_to_pos:
            continue
        c_pos = char_to_pos[c]
        k_pos = char_to_pos[key_char]

        if mode == "beaufort":
            p_pos = (k_pos - c_pos) % n
        else:
            p_pos = (c_pos - k_pos) % n

        p = pos_to_char[p_pos]
        plaintext.append(p)
        key_char = c  # ciphertext autokey

    return "".join(plaintext)


def count_doublets(text: str) -> tuple[int, int, float]:
    """Count doublets."""
    if len(text) < 2:
        return 0, 0, 0.0
    count = sum(1 for i in range(len(text) - 1) if text[i] == text[i + 1])
    possible = len(text) - 1
    return count, possible, count / possible


def ioc(text: Sequence) -> float:
    """Calculate IoC."""
    counts = Counter(text)
    n = len(text)
    if n < 2:
        return 0.0
    num = sum(c * (c - 1) for c in counts.values())
    denom = n * (n - 1)
    return num / denom


def frequency_flatness(text: str, alphabet: list[str]) -> float:
    """Measure how flat the frequency distribution is (1.0 = perfectly flat)."""
    counts = Counter(text)
    n = len(text)
    expected = n / len(alphabet)

    # Chi-squared-like measure
    deviations = sum((counts.get(c, 0) - expected) ** 2 for c in alphabet)
    max_deviation = (n - expected) ** 2 + (len(alphabet) - 1) * expected ** 2

    return 1.0 - (deviations / max_deviation) if max_deviation > 0 else 1.0


def load_sample_english() -> str:
    """Load sample English text."""
    try:
        with open("/usr/share/dict/words") as f:
            return f.read()[:100000]  # First 100k chars
    except:
        # Fallback
        return """
        Four score and seven years ago our fathers brought forth on this continent
        a new nation conceived in Liberty and dedicated to the proposition that
        all men are created equal. Now we are engaged in a great civil war testing
        whether that nation or any nation so conceived and so dedicated can long
        endure. We are met on a great battlefield of that war. We have come to
        dedicate a portion of that field as a final resting place for those who
        here gave their lives that that nation might live. It is altogether fitting
        and proper that we should do this. But in a larger sense we cannot dedicate
        we cannot consecrate we cannot hallow this ground. The brave men living
        and dead who struggled here have consecrated it far above our poor power
        to add or detract. The world will little note nor long remember what we
        say here but it can never forget what they did here.
        """ * 20


if __name__ == "__main__":
    print("=" * 70)
    print("Quagmire III Autokey Hypothesis Verification")
    print("=" * 70)

    # Load English text
    english = load_sample_english()
    runeglish = english_to_runeglish(english)

    print(f"\nPlaintext (Runeglish): {len(runeglish)} runes")
    print(f"Plaintext IoC: {ioc(runeglish):.4f}")
    print(f"Plaintext doublet rate: {count_doublets(runeglish)[2]*100:.2f}%")

    # LP target values
    print("\n--- LP Target Values ---")
    print("Doublet rate: 0.68%")
    print("IoC: ~0.0345 (1/29)")
    print("Frequency: flat (all runes 3-4%)")

    # Test different keywords
    keywords_to_test = [
        # Keywords starting with rare digraphs
        "ᛝᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛟᛞᚪᚫᚣᛡᛠ",  # NG first
        "ᚹᚠᚢᚦᚩᚱᚳᚷᛝᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛟᛞᚪᚫᚣᛡᛠ",  # W first
        "ᚦᚠᚢᛝᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛟᛞᚪᚫᚣᛡᛠ",  # TH first
        "ᛠᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡ",  # EA first
        "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ",  # F first (standard)
        "ᛖᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛝᛗᛚᛟᛞᚪᚫᚣᛡᛠ",  # E first (common)
    ]

    keyword_names = ["NG-first", "W-first", "TH-first", "EA-first", "F-first", "E-first"]

    print("\n--- Testing Keywords ---")
    print(f"{'Keyword':<10} {'Identity':<8} {'Doublet%':>10} {'IoC':>8} {'Flatness':>10} {'Match?':>8}")
    print("-" * 60)

    for kw, name in zip(keywords_to_test, keyword_names):
        # Encrypt
        ciphertext = quagmire3_autokey_encrypt(
            runeglish, kw, kw[0], ALPHABET, mode="beaufort", autokey="ciphertext"
        )

        # Analyze ciphertext
        _, _, doublet_rate = count_doublets(ciphertext)
        ct_ioc = ioc(ciphertext)
        flatness = frequency_flatness(ciphertext, ALPHABET)

        # Check if matches LP
        match = "✓" if 0.004 < doublet_rate < 0.012 and 0.030 < ct_ioc < 0.040 else "✗"

        identity = kw[0]
        identity_name = c3301.CICADA_ENGLISH_ALPHABET[ALPHABET.index(identity)]

        print(f"{name:<10} {identity_name:<8} {doublet_rate*100:>9.2f}% {ct_ioc:>8.4f} {flatness:>10.4f} {match:>8}")

    # Detailed analysis of best candidate
    print("\n" + "=" * 70)
    print("Detailed Analysis: NG-first keyword")
    print("=" * 70)

    kw = keywords_to_test[0]  # NG first
    ciphertext = quagmire3_autokey_encrypt(
        runeglish, kw, kw[0], ALPHABET, mode="beaufort", autokey="ciphertext"
    )

    print(f"\nCiphertext length: {len(ciphertext)}")
    print(f"Ciphertext IoC: {ioc(ciphertext):.4f} (target: 0.0345)")
    print(f"Ciphertext doublet rate: {count_doublets(ciphertext)[2]*100:.3f}% (target: 0.68%)")

    # Frequency distribution
    print("\n--- Ciphertext Frequency Distribution ---")
    counts = Counter(ciphertext)
    total = len(ciphertext)
    freqs = sorted([(c, counts[c]/total) for c in ALPHABET], key=lambda x: x[1])

    print(f"Min: {freqs[0][0]} = {freqs[0][1]*100:.2f}%")
    print(f"Max: {freqs[-1][0]} = {freqs[-1][1]*100:.2f}%")
    print(f"Range: {(freqs[-1][1] - freqs[0][1])*100:.2f}%")

    # Test single-key autokey decryption (without knowing the keyword)
    print("\n--- Single-Key Autokey Decryption Test ---")
    print("(Testing if ciphertext can be decrypted with simple autokey)")

    for primer_idx in range(0, 29, 7):  # Sample a few primers
        primer = ALPHABET[primer_idx]
        decrypted = simple_autokey_decrypt(ciphertext, primer, ALPHABET)
        dec_ioc = ioc(decrypted)
        _, _, dec_doublet = count_doublets(decrypted)

        primer_name = c3301.CICADA_ENGLISH_ALPHABET[primer_idx]
        print(f"  Primer {primer_name}: IoC={dec_ioc:.4f}, doublet={dec_doublet*100:.2f}%")

    print("\n" + "=" * 70)
    print("Conclusion")
    print("=" * 70)
    print("""
If the ciphertext shows:
  ✓ Doublet rate ~0.6-0.7%
  ✓ IoC ~0.034 (flat distribution)
  ✓ Single-key decryption still shows random (no plaintext patterns)

Then the Quagmire III autokey hypothesis is CONFIRMED.
The keyword's first character determines the doublet rate.
""")
