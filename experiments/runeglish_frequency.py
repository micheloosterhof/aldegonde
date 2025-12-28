# ABOUTME: Calculate expected Runeglish frequencies from English text
# ABOUTME: Maps English to Gematria Primus and computes symbol frequencies

"""
Calculate what Runeglish frequencies look like when English text
is converted through the Gematria Primus.

The key insight: in PLAINTEXT (Runeglish), rare digraphs like
EO, AE, IA, OE, X, J would have very low frequencies (~0.5-1%).

If the autokey identity character is one of these, doublet rate
would match the observed 0.68%.
"""

import sys
sys.path.insert(0, 'src')

from collections import Counter
import re


# Gematria Primus mapping (simplified - digraphs first, then single letters)
# Order matters: check digraphs before single letters
GEMATRIA_RULES = [
    ("ing", "ᛝ"),   # ING -> NG rune (special case)
    ("ng", "ᛝ"),    # NG
    ("th", "ᚦ"),    # TH
    ("ea", "ᛠ"),    # EA
    ("eo", "ᛇ"),    # EO
    ("oe", "ᛟ"),    # OE
    ("ae", "ᚫ"),    # AE
    ("ia", "ᛡ"),    # IA
    ("io", "ᛡ"),    # IO (same rune as IA)
    ("f", "ᚠ"),
    ("u", "ᚢ"),
    ("o", "ᚩ"),
    ("r", "ᚱ"),
    ("c", "ᚳ"),
    ("k", "ᚳ"),     # K -> C rune
    ("g", "ᚷ"),
    ("w", "ᚹ"),
    ("h", "ᚻ"),
    ("n", "ᚾ"),
    ("i", "ᛁ"),
    ("j", "ᛄ"),
    ("p", "ᛈ"),
    ("x", "ᛉ"),
    ("s", "ᛋ"),
    ("z", "ᛋ"),     # Z -> S rune
    ("t", "ᛏ"),
    ("b", "ᛒ"),
    ("e", "ᛖ"),
    ("m", "ᛗ"),
    ("l", "ᛚ"),
    ("d", "ᛞ"),
    ("a", "ᚪ"),
    ("y", "ᚣ"),
    ("q", "ᚳ"),     # Q -> C rune (usually QU)
    ("v", "ᚢ"),     # V -> U rune
]

RUNE_NAMES = {
    "ᚠ": "F", "ᚢ": "U", "ᚦ": "TH", "ᚩ": "O", "ᚱ": "R", "ᚳ": "C/K",
    "ᚷ": "G", "ᚹ": "W", "ᚻ": "H", "ᚾ": "N", "ᛁ": "I", "ᛄ": "J",
    "ᛇ": "EO", "ᛈ": "P", "ᛉ": "X", "ᛋ": "S/Z", "ᛏ": "T", "ᛒ": "B",
    "ᛖ": "E", "ᛗ": "M", "ᛚ": "L", "ᛝ": "NG", "ᛟ": "OE", "ᛞ": "D",
    "ᚪ": "A", "ᚫ": "AE", "ᚣ": "Y", "ᛡ": "IA/IO", "ᛠ": "EA",
}


def english_to_runeglish(text: str) -> str:
    """Convert English text to Runeglish using Gematria Primus."""
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
            # Skip non-alphabetic characters
            i += 1
    return "".join(result)


def analyze_runeglish_frequencies(text: str) -> list[tuple[str, int, float]]:
    """Analyze frequencies of runes in Runeglish text."""
    runeglish = english_to_runeglish(text)
    counts = Counter(runeglish)
    total = len(runeglish)

    result = []
    for rune, count in counts.items():
        freq = count / total if total > 0 else 0
        name = RUNE_NAMES.get(rune, "?")
        result.append((rune, name, count, freq))

    return sorted(result, key=lambda x: x[3])  # Sort by frequency


# Sample English texts of varying styles
SAMPLE_TEXTS = {
    "gettysburg": """Four score and seven years ago our fathers brought forth on this
        continent a new nation conceived in Liberty and dedicated to the proposition
        that all men are created equal Now we are engaged in a great civil war testing
        whether that nation or any nation so conceived and so dedicated can long endure""",

    "philosophy": """The unexamined life is not worth living Knowledge is the food of
        the soul The only true wisdom is in knowing you know nothing I cannot teach
        anybody anything I can only make them think There is only one good knowledge
        and one evil ignorance""",

    "technical": """The algorithm processes each input sequentially applying the
        transformation function to generate output The complexity is logarithmic
        in the worst case scenario Memory usage scales linearly with input size
        Exception handling provides robust error recovery mechanisms""",
}


if __name__ == "__main__":
    print("=" * 70)
    print("Runeglish Frequency Analysis")
    print("=" * 70)

    # Combine all sample texts
    all_text = " ".join(SAMPLE_TEXTS.values())

    # Also try loading a larger corpus if available
    try:
        with open("/usr/share/dict/words") as f:
            dictionary = f.read()
        all_text += " " + dictionary
        print("(Including system dictionary for larger sample)")
    except:
        pass

    print(f"\nTotal English characters: {len(all_text)}")

    runeglish = english_to_runeglish(all_text)
    print(f"Total runes: {len(runeglish)}")

    freqs = analyze_runeglish_frequencies(all_text)

    print("\n--- Runeglish Frequencies (sorted by ascending frequency) ---")
    print("(Rarest first - these are candidates for identity character)\n")

    for rune, name, count, freq in freqs:
        marker = ""
        if freq < 0.01:
            marker = " <-- VERY RARE (<1%)"
        elif freq < 0.02:
            marker = " <-- RARE (<2%)"
        print(f"  {rune} ({name:5s}): {count:6d} = {freq*100:5.2f}%{marker}")

    print("\n--- Candidates for Identity Character ---")
    print("(Runes with frequency close to observed doublet rate of 0.68%)\n")

    for rune, name, count, freq in freqs:
        if freq < 0.015:  # Under 1.5%
            print(f"  {rune} ({name}): {freq*100:.2f}%")

    print("\n" + "=" * 70)
    print("Key Finding:")
    print("=" * 70)
    print("""
If the autokey cipher uses a keyword that places a rare digraph
(like EO, AE, IA/IO, OE, X, or J) at position 0 in the mixed alphabet,
the doublet rate would match this character's plaintext frequency.

For ~0.68% doublet rate, the identity character would need to appear
about 0.68% of the time in the Runeglish plaintext.

Candidates: EO, AE, IA/IO, X, J (all under 1% in typical English)
""")
