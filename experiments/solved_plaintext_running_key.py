#!/usr/bin/env python3
# ABOUTME: Closes the open running-key gap in running-key-text.md: recovers the
# ABOUTME: solved early pages' plaintext (known systems, fitness-verified) and
# ABOUTME: slides it as a running key against the clean unsolved corpus.
"""Solved-section plaintexts as running-key candidates.

The solved early pages (first 2,797 runes of the master transcription) were
never tested as running keys — only their CIPHERTEXT was (via the full
master slide in lp_cryptodiagnostics H3). This script recovers each solved
segment's plaintext with its known system:

  seg 0           atbash                      "A WARNING BELIEUE NOTHNG..."
  segs 1+2        Vigenere DIUINITY,          "WELCOME WELCOME PILGRIM..."
                  F-interrupts (beam-searched: 11 interrupts)
  segs 3,4,7,8,9  identity (unencrypted)      "SOME WISDOM...", "CNOW THIS...",
      11,12                                   "THE LOSS OF DIUINITY...", ...
  segs 5,6        affine 28x+2 (atbash+2)     "A COAN A MAN DECIDED...",
                                              "AN INSTRUCTIAN DO FOUR..."
  seg 10          Vigenere FIRFUMFERENFE,     "A COAN DURNG A LESSON..."
                  F-interrupts (2)

Each decryption is verified by trigram fitness (all land in the plaintext
band, -3.3..-4.0, vs ciphertext -6.5..-7.3) and by reading the printed
transliteration. The concatenated plaintext (forward and reversed) is then
slid against the clean corpus at every alignment, Vigenere (C-K) and
Beaufort (C+K), reporting max |z(nIoC)| against a shuffled-key null.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301
from lp_corpus import load_clean

M = 29
RUNES = set(c3301.CICADA_ALPHABET)
R2I = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
ENG = c3301.CICADA_ENGLISH_ALPHABET
ALPHA = c3301.CICADA_ALPHABET
SOLVED_RUNES = 2797  # the solved early pages of the master transcription

# trigram log-prob fitness (same table as englishness_scan.py)
TRI: dict[str, float] = {}
with open(ROOT / "src/aldegonde/data/ngrams/runeglish/trigrams.txt") as fh:
    for line in fh:
        k, v = line.split()
        TRI[k] = int(v)
_total = sum(TRI.values())
FLOOR = math.log10(0.01 / _total)
LOGP = {k: math.log10(v / _total) for k, v in TRI.items()}


def fitness(idx: list[int]) -> float:
    runes = [ALPHA[i] for i in idx]
    if len(runes) < 3:
        return FLOOR
    s = sum(LOGP.get("".join(runes[i:i + 3]), FLOOR)
            for i in range(len(runes) - 2))
    return s / (len(runes) - 2)


def translit(idx: list[int]) -> str:
    return "".join(ENG[i] for i in idx)


def keyword_indices(word: str) -> list[int]:
    out = []
    i = 0
    while i < len(word):
        for ln in (2, 1):
            seg = word[i:i + ln]
            if seg in ENG:
                out.append(ENG.index(seg))
                i += ln
                break
        else:
            i += 1
    return out


def beam_vigenere(ct: list[int], keyword: str) -> tuple[list[int], int]:
    """Vigenere decrypt with optional F-interrupts (ciphertext F = plaintext
    F, key pauses), choosing interrupt positions by trigram-fitness beam
    search over the key phase."""
    kw = keyword_indices(keyword)
    L = len(kw)
    beams: dict[int, tuple[float, list[int], int]] = {0: (0.0, [], 0)}
    for c in ct:
        new: dict[int, tuple[float, list[int], int]] = {}
        for j, (sc, pt, ni) in beams.items():
            opts = [((c - kw[j % L]) % M, (j + 1) % L, 0)]
            if c == 0:
                opts.append((0, j, 1))
            for p, j2, isint in opts:
                pt2 = pt + [p]
                sc2 = sc + (LOGP.get("".join(ALPHA[x] for x in pt2[-3:]), FLOOR)
                            if len(pt2) >= 3 else 0.0)
                if j2 not in new or sc2 > new[j2][0]:
                    new[j2] = (sc2, pt2, ni + isint)
        beams = new
    _, pt, ni = max(beams.values(), key=lambda t: t[0])
    return pt, ni


def solved_segments() -> list[list[int]]:
    text = (ROOT / "data/liber-primus__transcription--master.txt").read_text()
    segs: list[list[int]] = [[]]
    count = 0
    for ch in text:
        if count >= SOLVED_RUNES:
            break
        if ch in RUNES:
            segs[-1].append(R2I[ch])
            count += 1
        elif ch in "&$" and segs[-1]:
            segs.append([])
    return [s for s in segs if s]


def recover_plaintext(segs: list[list[int]]) -> list[int]:
    out: list[int] = []

    def add(name: str, pt: list[int]) -> None:
        print(f"  {name:<28} {len(pt):>4} runes  fit {fitness(pt):.3f}  "
              f"{translit(pt)[:60]}")
        out.extend(pt)

    add("seg0 atbash", [(28 - c) % M for c in segs[0]])
    pt, ni = beam_vigenere(segs[1] + segs[2], "DIUINITY")
    add(f"seg1+2 vig-DIUINITY ({ni} int)", pt)
    for k in (3, 4):
        add(f"seg{k} identity", segs[k])
    for k in (5, 6):
        add(f"seg{k} affine 28x+2", [(28 * c + 2) % M for c in segs[k]])
    for k in (7, 8, 9):
        add(f"seg{k} identity", segs[k])
    pt, ni = beam_vigenere(segs[10], "FIRFUMFERENFE")
    add(f"seg10 vig-FIRFUMFERENFE ({ni} int)", pt)
    for k in (11, 12):
        add(f"seg{k} identity", segs[k])
    return out


def zioc(v: np.ndarray) -> float:
    m = len(v)
    cc = np.bincount(v, minlength=M)
    obs = float((cc * (cc - 1)).sum()) / (m * (m - 1))
    sd = math.sqrt(2 * (M - 1)) / (M * math.sqrt(m * (m - 1)))
    return (obs - 1 / M) / sd


def slide(clean: np.ndarray, key: np.ndarray) -> tuple[float, str, int]:
    n, m = len(clean), len(key)
    best = (0.0, "", -1)
    for off in range(n - m):
        seg = clean[off:off + m]
        for tag, v in (("V", (seg - key) % M), ("B", (seg + key) % M)):
            z = abs(zioc(v))
            if z > best[0]:
                best = (z, tag, off)
    return best


def main() -> None:
    segs = solved_segments()
    print(f"solved region: {sum(map(len, segs))} runes in {len(segs)} segments")
    plaintext = recover_plaintext(segs)
    print(f"recovered plaintext: {len(plaintext)} runes, "
          f"overall fitness {fitness(plaintext):.3f}")

    clean = np.array(load_clean()[0])
    key = np.array(plaintext)
    print(f"\nrunning-key slide vs clean corpus ({len(clean)} runes):")
    for name, kk in (("solved-plaintext", key),
                     ("solved-plaintext-rev", key[::-1])):
        z, tag, off = slide(clean, kk)
        print(f"  {name}: max |z| = {z:.1f} ({tag}) at offset {off}")

    rng = random.Random(3301)
    null = []
    for _ in range(5):
        perm = list(range(len(key)))
        rng.shuffle(perm)
        z, _, _ = slide(clean, key[perm])
        null.append(z)
    print(f"  shuffled-key null max |z| over {len(null)} trials: "
          f"{min(null):.1f}-{max(null):.1f}")


if __name__ == "__main__":
    main()
