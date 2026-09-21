# ABOUTME: Positive control for the d5 echo, using the front matter's known-key ciphers to
# ABOUTME: show a stream cipher leaks across word boundaries where the body's echo does not.
"""Is the body's within-word-only echo a real signature, or just what ciphertext does?

The LP's d5 echo is elevated inside words (1.43x chance) and flat across word
boundaries (1.01x). That asymmetry is read as the key state being anchored to words.
The reading has never had a positive control: nothing showed what a cipher WITHOUT
word anchoring looks like on this corpus.

`solved-page-testbed.md` supplies one. Pages 1, 2, 12 and 13 are keyed Vigenere with
known key lengths 8 and 13, from the same author and book. A Vigenere key advances
with position and knows nothing about words, so its echo must cross word boundaries
freely. If it does, the body's flat cross-word channel is a positive signature rather
than a generic property of ciphertext.

Two measurements:

  recovery   kappa on the full stream at every lag, to check the method finds the
             known key lengths before it is trusted on the body
  anchoring  the same echo measured within words and across word boundaries, for the
             known ciphers and for the body

    python echo_architecture_control.py
"""

from __future__ import annotations

import math
import re
import sys
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

M = 29
RUNE = re.compile(r"[ᚠ-᛿]")
WRAP = "/\n"
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}


def words_of(ns: list[int]) -> list[list[int]]:
    pages = (
        (ROOT / "data" / "liber-primus__transcription--master.txt")
        .read_text()
        .split("%")
    )
    out: list[list[int]] = []
    for n in ns:
        cur: list[int] = []
        for ch in pages[n]:
            if RUNE.match(ch):
                cur.append(IDX[ch])
            elif ch in WRAP:
                continue
            elif cur:
                out.append(cur)
                cur = []
        if cur:
            out.append(cur)
    return out


def body_words() -> list[list[int]]:
    stream, wid = load_clean()
    out, cur, last = [], [], wid[0]
    for r, w in zip(stream, wid):
        if w != last:
            out.append(cur)
            cur, last = [], w
        cur.append(r)
    out.append(cur)
    return out


def kappa_z(stream: list[int], d: int) -> float:
    n = len(stream) - d
    hits = sum(1 for i in range(n) if stream[i] == stream[i + d])
    return (hits - n / M) / math.sqrt(n * (1 / M) * (1 - 1 / M))


def split_echo(words: list[list[int]], d: int):
    """(within-word, cross-boundary) hits and pairs at distance d."""
    hw = pw = 0
    for w in words:
        for i in range(len(w) - d):
            pw += 1
            hw += w[i] == w[i + d]
    stream, owner = [], []
    for k, w in enumerate(words):
        for r in w:
            stream.append(r)
            owner.append(k)
    hc = pc = 0
    for i in range(len(stream) - d):
        if owner[i] != owner[i + d]:
            pc += 1
            hc += stream[i] == stream[i + d]
    return (hw, pw), (hc, pc)


def cell(hits: int, pairs: int) -> str:
    if pairs < 20:
        return f"{'-':>10}{'-':>8}"
    z = (hits / pairs - 1 / M) / math.sqrt((1 / M) * (1 - 1 / M) / pairs)
    return f"{(hits / pairs) * M:>10.2f}{z:>+8.2f}"


def main() -> None:
    groups = [
        ("pages 1+2, key length 8", words_of([1, 2]), 8),
        ("pages 12+13, key length 13", words_of([12, 13]), 13),
        ("the unsolved body", body_words(), 5),
    ]
    print("key-length recovery: best kappa lag on the full stream\n")
    for label, words, true_d in groups:
        stream = [r for w in words for r in w]
        best = sorted(((kappa_z(stream, d), d) for d in range(1, 21)), reverse=True)
        top = "  ".join(f"d={d} z={z:+.1f}" for z, d in best[:3])
        print(f"  {label:<28} truth d={true_d:<3} {top}")

    print("\nword anchoring: the same echo within words and across boundaries\n")
    print(f"{'corpus':<28}{'d':>3}{'within x':>10}{'z':>8}{'cross x':>10}{'z':>8}")
    for label, words, d in groups:
        (hw, pw), (hc, pc) = split_echo(words, d)
        print(f"{label:<28}{d:>3}{cell(hw, pw)}{cell(hc, pc)}")
    print(
        "\nThe known Vigenere ciphers leak ACROSS word boundaries, because a positional"
        "\nkey knows nothing about words. The body does not. Its flat cross-word channel"
        "\nis therefore a positive signature of a word-anchored key state, not something"
        "\nciphertext does on its own."
    )


if __name__ == "__main__":
    main()
