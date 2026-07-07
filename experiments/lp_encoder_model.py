#!/usr/bin/env python3
"""A complete candidate encoder for the unsolved Liber Primus.

The algorithm (the only shape left standing after the 2026 campaign):

    key    : OTP-grade stream K (pad or CSPRNG) -- fresh uniform symbol
             per draw
    emit   : C[i] = P[i] + K[draw] mod 29
    rule A : (anti-doublet, "look 1 back") if the emitted glyph equals
             C[i-1], redraw the key -- complied with ~81% of the time
    rule B : (back-reference, "look 5 back") when the PLAINTEXT repeats
             what was five glyphs back, reuse the key from five back
             instead of drawing:  K := K(i-5)  =>  C[i] = C[i-5], a
             literal ciphertext copy. Applied to contiguous units only:
               - digram  P[i]=P[i-5] & P[i+1]=P[i-4]  (word-internal:
                 ~always; across boundaries: rarely)
               - single  P[i]=P[i-5]                  (word-internal,
                 ~half the time)
               - frame   P[i]=P[i-5] & P[i+4]=P[i-1]  (the 5-window
                 edge bracket, ~quarter of the time, any boundaries)
             A copy is skipped when it would violate rule A.

This script validates the algorithm end-to-end: plaintext is REAL
English (frequency-weighted lexicon words transliterated to runeglish,
sampled to the LP's exact word-length sequence), so the shape
selectivity, word-scoping, and pairs-vs-triplets ratio must emerge from
English morphology rather than from tuned rates. Only four behavioral
compliance probabilities are set; all seventeen fingerprint statistics
plus the shape census are emergent.

Usage: python experiments/lp_encoder_model.py [n_sims]
"""

from __future__ import annotations

import sys
from collections import defaultdict

import numpy as np
from word_scoped_copy_simulator import fingerprint, parse_clean_sections

MOD = 29
D = 5

PARAMS = {
    "doublet_compliance": 0.81,  # rule A: redraw probability on collision
    "p_digram_in": 0.85,         # rule B compliance by unit shape
    "p_digram_x": 0.08,
    "p_single_in": 0.20,
    "p_frame": 0.22,
}


# ---------------------------------------------------------------- plaintext
def lexicon_by_length() -> dict[int, tuple[list[list[int]], np.ndarray]]:
    from wordfreq import top_n_list, word_frequency

    def transliterate(word: str) -> list[int] | None:
        w = word.upper()
        if not w.isalpha():
            return None
        for a, b in (("K", "C"), ("Q", "C"), ("V", "U"), ("Z", "S")):
            w = w.replace(a, b)
        digraphs = {"TH": 2, "EO": 12, "NG": 21, "OE": 22, "AE": 25,
                    "IA": 27, "IO": 27, "EA": 28}
        singles = {"F": 0, "U": 1, "O": 3, "R": 4, "C": 5, "G": 6, "W": 7,
                   "H": 8, "N": 9, "I": 10, "J": 11, "P": 13, "X": 14,
                   "S": 15, "T": 16, "B": 17, "E": 18, "M": 19, "L": 20,
                   "D": 23, "A": 24, "Y": 26}
        out: list[int] = []
        i = 0
        while i < len(w):
            if w[i:i + 2] in digraphs:
                out.append(digraphs[w[i:i + 2]])
                i += 2
            elif w[i] in singles:
                out.append(singles[w[i]])
                i += 1
            else:
                return None
        return out

    pool: dict[int, tuple[list[list[int]], list[float]]] = defaultdict(
        lambda: ([], []))
    for eng in top_n_list("en", 50000):
        runes = transliterate(eng)
        if runes:
            words, weights = pool[len(runes)]
            words.append(runes)
            weights.append(word_frequency(eng, "en"))
    return {length: (words, np.array(weights) / sum(weights))
            for length, (words, weights) in pool.items()}


def sample_plaintext(lens: list[int], pool, rng) -> list[list[int]]:
    """English words matched to the LP word-length sequence."""
    freqs = None  # unigram distribution for padding rare lengths
    all_w = [w for ws, _ in pool.values() for w in ws]
    flat = [c for w in all_w for c in w]
    freqs = np.bincount(flat, minlength=MOD).astype(float)
    freqs /= freqs.sum()
    out = []
    for length in lens:
        if length in pool and len(pool[length][0]) >= 5:
            words, weights = pool[length]
            out.append(words[rng.choice(len(words), p=weights)])
        else:  # no lexicon word of this length: letter-frequency filler
            out.append(rng.choice(MOD, size=length, p=freqs).tolist())
    return out


# ------------------------------------------------------------------ encoder
def encode(pwords: list[list[int]], params: dict, rng) -> np.ndarray:
    p = [c for w in pwords for c in w]
    widx = np.repeat(np.arange(len(pwords)), [len(w) for w in pwords])
    n = len(p)
    c = np.full(n, -1, dtype=np.int64)
    pending: dict[int, int] = {}  # position -> value promised by a frame
    u = rng.random(n)
    u2 = rng.random(n)

    def ok(j: int, v: int) -> bool:
        """Rule A veto: a copy may not create a doublet."""
        return j == 0 or c[j - 1] != v

    for j in range(n):
        if c[j] >= 0:
            continue
        if j in pending:
            v = pending.pop(j)
            if ok(j, v):
                c[j] = v
                continue
        if j >= D:
            # rule B, digram unit
            if (j + 1 < n and p[j] == p[j - D] and p[j + 1] == p[j - D + 1]
                    and c[j + 1] < 0):
                pr = (params["p_digram_in"]
                      if widx[j - D] == widx[j + 1] else params["p_digram_x"])
                if u[j] < pr and ok(j, c[j - D]) and c[j - D + 1] != c[j - D]:
                    c[j] = c[j - D]
                    c[j + 1] = c[j - D + 1]
                    continue
            # rule B, frame unit (edges of the 5-window)
            if (j + 4 < n and p[j] == p[j - D] and p[j + 4] == p[j - 1]
                    and u[j] < params["p_frame"] and ok(j, c[j - D])):
                c[j] = c[j - D]
                pending[j + 4] = int(c[j - 1])
                continue
            # rule B, single glyph (word-internal)
            if (p[j] == p[j - D] and widx[j] == widx[j - D]
                    and u2[j] < params["p_single_in"] and ok(j, c[j - D])):
                c[j] = c[j - D]
                continue
        # normal emission: OTP draw + rule A
        v = int(rng.integers(MOD))
        while j > 0 and v == c[j - 1] and (
                rng.random() < params["doublet_compliance"]):
            v = int(rng.integers(MOD))
        c[j] = v
    return c


# --------------------------------------------------------------------- main
def main() -> None:
    n_sims = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    sections = parse_clean_sections()
    words = [w for s in sections for w in s]
    lens = [len(w) for w in words]
    real_c = np.array([x for w in words for x in w], dtype=np.int64)
    real_w = np.repeat(np.arange(len(words)), lens)
    real = fingerprint(real_c, real_w)

    pool = lexicon_by_length()
    rng = np.random.default_rng(20260707)
    keys = list(real.keys())
    acc = {k: [] for k in keys}
    trigrams = []
    for _ in range(n_sims):
        pwords = sample_plaintext(lens, pool, rng)
        c = encode(pwords, PARAMS, rng)
        fp = fingerprint(c, real_w)
        for k in keys:
            acc[k].append(fp[k])
        m = c[:-D] == c[D:]
        trigrams.append(int((m[:-2] & m[1:-1] & m[2:]).sum()))

    print(f"reference encoder ({n_sims} sims, real-lexicon plaintext, "
          f"{len(PARAMS)} behavioral params) vs LP:")
    print(f"{'stat':>16} {'LP':>7} {'model':>9} {'sd':>6} {'z':>6}")
    for k in keys:
        a = np.array(acc[k], dtype=float)
        z = (real[k] - a.mean()) / a.std() if a.std() else 0.0
        print(f"{k:>16} {real[k]:>7} {a.mean():>9.1f} {a.std():>6.1f} "
              f"{z:>+6.2f}")
    t = np.array(trigrams, dtype=float)
    rm = real_c[:-D] == real_c[D:]
    real_tri = int((rm[:-2] & rm[1:-1] & rm[2:]).sum())
    print(f"{'trigram runs':>16} {real_tri:>7} {t.mean():>9.1f} "
          f"{t.std():>6.1f} {(real_tri-t.mean())/t.std():>+6.2f}")


if __name__ == "__main__":
    main()
