# ABOUTME: Compare LP ciphertext bigrams with synthetic Quagmire III ciphertext
# ABOUTME: Verify LP matches the pattern of autokey-encrypted text

import sys
sys.path.insert(0, 'src')

from aldegonde import c3301
from aldegonde.grams import bigram_diagram

ALPHABET = c3301.CICADA_ALPHABET


def load_lp() -> str:
    """Load LP ciphertext."""
    with open("data/page0-58.txt") as f:
        text = f.read()
    return "".join(c for c in text if c in ALPHABET)


if __name__ == "__main__":
    lp = load_lp()

    print("=" * 70)
    print("LIBER PRIMUS CIPHERTEXT - Bigram Analysis")
    print("=" * 70)
    print(f"\nLength: {len(lp)} runes")

    # Count doublets
    doublets = sum(1 for i in range(len(lp)-1) if lp[i] == lp[i+1])
    print(f"Doublets: {doublets} ({doublets/(len(lp)-1)*100:.3f}%)")

    print("\n")
    bigram_diagram.print_auto_bigram_diagram(lp, alphabet=ALPHABET)
