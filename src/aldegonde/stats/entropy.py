"""Entropy related functions."""

import math
from collections import Counter
from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def shannon_entropy(ciphertext: Sequence[T], base: int = 2) -> float:
    """Shannon entropy. by default in bits."""
    f = Counter(ciphertext)
    N = len(ciphertext)
    H: float = 0.0
    for v in f.values():
        H = H - v / N * math.log(v / N, base)
    print(f"Shannon Entropy = {H:.3f} bits (size={N})")
    return H


def shannon2_entropy(ciphertext: Sequence[T], base: int = 2, cut: int = 0) -> float:
    """Shannon entropy. by default in bits."""
    N = len(ciphertext)
    if N < 3:
        return 0.0
    l: list[tuple[T, ...]] = []
    if cut == 0:
        for i in range(N - 1):
            l.append((ciphertext[i], ciphertext[i + 1]))
    elif cut in (1, 2):
        for i in range(cut - 1, N - 1, 2):
            l.append((ciphertext[i], ciphertext[i + 1]))
    else:
        raise ValueError
    f = Counter(l)
    H: float = 0.0
    for v in f.values():
        H = H - v / N * math.log(v / N, base)
    print(f"S = {H:.3f} bits (size={N})")
    return H
