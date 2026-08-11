# ABOUTME: Tests the accumulator autokey hypothesis (key = running sum of prior
# ABOUTME: ciphertext) by direct decryption of the clean corpus over all 29 primers.
"""Accumulator autokey: S[i] = (S[i-1] + C[i-1]) mod 29, with S[0] a primer.

Beaufort form:  C[i] = (S[i] - P[i]) mod 29  ->  P[i] = (S[i] - C[i]) mod 29
Vigenere form:  C[i] = (P[i] + S[i]) mod 29  ->  P[i] = (C[i] - S[i]) mod 29

Both are deterministic given the primer, so decryption is exhaustive over the
29 primers. Changing the primer only shifts every recovered P[i] by a constant,
which leaves the IoC unchanged, so a single IoC per form settles the question:
English-like runeglish has normalized IoC ~1.6-1.8; random text sits at 1.0.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "page0-56.txt"
RUNE = re.compile(r"[ᚠ-᛿]")


def clean_sections(text: str) -> list[str]:
    sections = [s for s in text.split("$") if RUNE.search(s)]
    return ["".join(RUNE.findall(s)) for s in sections[:10]]


def nioc(seq: list[int]) -> float:
    n = len(seq)
    counts = Counter(seq)
    return 29 * sum(c * (c - 1) for c in counts.values()) / (n * (n - 1))


def decrypt(cipher: list[int], primer: int, *, beaufort: bool) -> list[int]:
    plain = []
    s = primer
    for i, c in enumerate(cipher):
        if i > 0:
            s = (s + cipher[i - 1]) % 29
        plain.append((s - c) % 29 if beaufort else (c - s) % 29)
    return plain


def main() -> None:
    alphabet = sorted({r for s in clean_sections(DATA.read_text()) for r in s})
    index = {r: i for i, r in enumerate(alphabet)}
    assert len(alphabet) == 29
    for name, beaufort in (("beaufort", True), ("vigenere", False)):
        worst = 0.0
        for section in clean_sections(DATA.read_text()):
            cipher = [index[r] for r in section]
            for primer in range(29):
                worst = max(worst, nioc(decrypt(cipher, primer, beaufort=beaufort)))
        print(
            f"{name}: max per-section nIoC over all 29 primers = {worst:.4f} "
            f"(random ~1.0, English ~1.6-1.8)"
        )


if __name__ == "__main__":
    main()
