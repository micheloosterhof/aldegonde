"""Entropy related functions"""

from collections import Counter
import math

from ..structures import sequence


def shannon_entropy(ciphertext: sequence.Sequence, base: int = 2) -> float:
    """
    shannon entropy. by default in bits.
    """
    f = Counter(ciphertext)
    N = len(ciphertext)
    H: float = 0.0
    for v in f.values():
        H = H - v / N * math.log(v / N, base)
    print(f"Shannon Entropy = {H:.3f} bits (size={N})")
    return H


def shannon2_entropy(runes: sequence.Sequence, base: int = 2, cut: int = 0) -> float:
    """
    shannon entropy. by default in bits.
    """
    N = len(runes)
    if N < 3:
        return 0.0
    l: list = []
    if cut == 0:
        for i in range(0, N - 1):
            l.append(f"{runes[i]}-{runes[i+1]}")
    elif cut in (1, 2):
        for i in range(cut - 1, N - 1, 2):
            l.append(f"{runes[i]}-{runes[i+1]}")
    else:
        raise Exception
    f = Counter(l)
    H: float = 0.0
    for v in f.values():
        H = H - v / N * math.log(v / N, base)
    print(f"S = {H:.3f} bits (size={N})")
    return H
