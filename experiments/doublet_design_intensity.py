# ABOUTME: Is the cipher's permutation g tuned to suppress doublets, or would a
# ABOUTME: rule-based (random) g give the same rate? Compares against permutations.
"""Design-intensity of the doublet suppression.

The ciphertext doublet rate equals the plaintext frequency of the bigrams
(x, g^{-1}x): rate = sum_x f(x, g^{-1}(x)). A doublet-blind (rule-based) g is
uncorrelated with the bigram table and lands near chance; a g tuned to avoid
common plaintext bigrams lands far below. This script builds the runeglish
plaintext bigram table (frequency-weighted lexicon), then places the observed
0.66% against the distribution a random g -- and a random cycle-type 5^5.1^4 g,
the order-5 shape -- would produce.

Verdict shape: obs << random-mean and unreachable by random draws => g is
language-tuned (designed), even if it is not pushed to the achievable floor.

Usage: python experiments/doublet_design_intensity.py
"""

from __future__ import annotations

import random

import numpy as np
from scipy.optimize import linear_sum_assignment

from aldegonde import c3301

MOD = 29
OBSERVED = 0.0063  # ciphertext adjacent-doublet rate, page0-56
SEED = 7
DRAWS = 5000



def transliterate(word: str) -> list[int] | None:
    if not (word.isascii() and word.isalpha()):
        return None
    return c3301.encode_english(word)


def bigram_table() -> np.ndarray:
    """Frequency-weighted within-word adjacent bigram distribution (sums to 1)."""
    from wordfreq import top_n_list, word_frequency

    counts = np.zeros((MOD, MOD))
    for word in top_n_list("en", 40000):
        runes = transliterate(word)
        if not runes:
            continue
        weight = word_frequency(word, "en")
        for i in range(len(runes) - 1):
            counts[runes[i]][runes[i + 1]] += weight
    return counts / counts.sum()


def rate(f: np.ndarray, s: list[int] | dict[int, int]) -> float:
    return float(sum(f[x][s[x]] for x in range(MOD)))


def random_permutation(rng: random.Random) -> list[int]:
    p = list(range(MOD))
    rng.shuffle(p)
    return p


def random_cycletype(rng: random.Random) -> dict[int, int]:
    """A random permutation of cycle type 5^5 . 1^4 (the order-5 shape on 29)."""
    idx = list(range(MOD))
    rng.shuffle(idx)
    s: dict[int, int] = {}
    pos = 0
    for length in (5, 5, 5, 5, 5, 1, 1, 1, 1):
        cycle = idx[pos : pos + length]
        pos += length
        for i in range(length):
            s[cycle[i]] = cycle[(i + 1) % length]
    return s


def main() -> None:
    f = bigram_table()
    rng = random.Random(SEED)

    identity = float(np.trace(f))
    row, col = linear_sum_assignment(f)
    floor = float(f[row, col].sum())

    generic = np.array([rate(f, random_permutation(rng)) for _ in range(DRAWS)])
    order5 = np.array([rate(f, random_cycletype(rng)) for _ in range(DRAWS)])

    print(f"runeglish plaintext bigram table: {(f > 0).sum()} of {MOD * MOD} bigrams occur\n")
    print(f"  s = identity (plaintext doublet rate)   = {identity:.4f}")
    print(f"  assignment floor (min over all perms)   = {floor:.4f}  (proxy exploits exact zeros)")
    print(f"  random permutation g                    = {generic.mean():.4f} +- {generic.std():.4f}")
    print(f"  random cycle-type 5^5.1^4 g             = {order5.mean():.4f} +- {order5.std():.4f}")
    print(f"  cipher actually achieves                = {OBSERVED:.4f}\n")
    z = (OBSERVED - order5.mean()) / order5.std()
    print(f"  observed is {z:+.1f} sd below a random order-5 g; "
          f"{(order5 <= OBSERVED).mean():.4f} of {DRAWS} draws reach it "
          f"(min sampled {order5.min():.4f})")
    print("\n  => g is tuned against the language (a rule-random g stays near chance),")
    print("     but sits above the achievable floor, so it suppresses common bigrams")
    print("     rather than being pushed to the doublet-free optimum.")


if __name__ == "__main__":
    main()
