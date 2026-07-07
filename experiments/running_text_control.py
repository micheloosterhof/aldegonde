#!/usr/bin/env python3
"""Does English-in-runes running text explain the lag-5 event mix?

The lexicon control (plaintext_control_corpus.py) has no word order, so
it measures only WITHIN-word repeat availability. But most of the LP's
paired events cross word boundaries (18/29 digrams, 27/28 frames), and
those can only come from RUNNING-text properties: repeated short words
and repeated boundary patterns at a 5-rune spacing, e.g.

    THE cat THE ...     TH,E +3-rune word  -> digram repeat at lag 5
    AND is AND ...      A,N,D +2-rune word -> trigram repeat at lag 5

This script measures, in genuine running runeglish:

1. the availability of every copy shape (single / digram / trigram /
   frame) at lag 5, split within/cross-word;
2. the same at lags 2..12 -- is 5 a SPECIAL distance for English
   self-repetition, or an arbitrary designer choice?
3. what word geometry produces the lag-5 digram and frame repeats
   (repeated whole words? which ones?);
4. whether one usage profile maps English availability onto the LP's
   observed event mix (9 in-word + 20 cross digrams, 28 frames).

Running-text sources: (a) Cicada's own solved sections (2,058 runes,
real word order, small); (b) bag-of-words text sampled iid from the
frequency-weighted lexicon (600k runes, no syntax but correct word
frequencies -- good to first order for repeated-function-word
geometry).

Usage: python experiments/running_text_control.py
"""

from __future__ import annotations

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
R2I["ᛂ"] = R2I["ᛄ"]
MASTER = "data/liber-primus__transcription--master.txt"
DATA = "data/page0-58.txt"
LETTERS = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J",
           "EO", "P", "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D",
           "A", "AE", "Y", "IA", "EA"]

SOLVED_PLAIN = {  # section -> constant transform (from plaintext_control_corpus)
    0: ("atbash", 0), 2: ("shift", 0), 3: ("atbash", 26),
    4: ("shift", 0), 6: ("shift", 0), 18: ("shift", 0),
}


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


def cicada_running_words() -> list[list[int]]:
    """Decoded plaintext words of the six constant-transform sections,
    in original order (real running runeglish)."""
    with open(MASTER) as f:
        raw = f.read()
    words: list[list[int]] = []
    for idx, sec in enumerate(raw.split("$")):
        if idx not in SOLVED_PLAIN:
            continue
        kind, shift = SOLVED_PLAIN[idx]
        cur: list[int] = []
        for ch in sec:
            if ch in R2I:
                c = R2I[ch]
                p = (MOD - 1 - c - shift) % MOD if kind == "atbash" \
                    else (c - shift) % MOD
                cur.append(p)
            elif ch in "-.&" and cur:
                words.append(cur)
                cur = []
        if cur:
            words.append(cur)
    return words


def bag_of_words(n_runes: int, rng) -> list[list[int]]:
    from wordfreq import top_n_list, word_frequency
    lex: list[list[int]] = []
    weights: list[float] = []
    for eng in top_n_list("en", 30000):
        r = transliterate(eng)
        if r:
            lex.append(r)
            weights.append(word_frequency(eng, "en"))
    w = np.array(weights)
    w /= w.sum()
    out = []
    total = 0
    while total < n_runes:
        word = lex[rng.choice(len(lex), p=w)]
        out.append(word)
        total += len(word)
    return out


def shape_rates(words: list[list[int]], lags=None):
    """Per-site rates of each shape at each lag, within/cross split at
    lag 5, plus the repeated-word inventory behind lag-5 digrams."""
    if lags is None:
        lags = range(2, 13)
    p = [c for w in words for c in w]
    word_of = [i for i, w in enumerate(words) for _ in w]
    word_start = {}
    for pos, wi in enumerate(word_of):
        word_start.setdefault(wi, pos)
    n = len(p)
    res = {}
    for lag in lags:
        m = [p[i] == p[i + lag] for i in range(n - lag)]
        mono = sum(m) / len(m)
        dig = sum(1 for i in range(len(m) - 1) if m[i] and m[i + 1])
        tri = sum(1 for i in range(len(m) - 2)
                  if m[i] and m[i + 1] and m[i + 2])
        frm = sum(1 for i in range(len(m) - 4) if m[i] and m[i + 4])
        res[lag] = (mono, dig / (len(m) - 1), tri / (len(m) - 2),
                    frm / (len(m) - 4))
    # lag-5 within/cross split + repeated-word inventory
    lag = 5
    m = [p[i] == p[i + lag] for i in range(n - lag)]
    dig_in = dig_x = frm_in = frm_x = 0
    word_hits = {}
    for i in range(len(m) - 1):
        if m[i] and m[i + 1]:
            if word_of[i] == word_of[min(i + 6, n - 1)]:
                dig_in += 1
            else:
                dig_x += 1
                # is this a repeated whole 2-rune word? source word check
                wi = word_of[i]
                if (word_start[wi] == i and len(words[wi]) == 2
                        and words[wi] == words[word_of[i + 5]]):
                    key = "".join(LETTERS[c] for c in words[wi])
                    word_hits[key] = word_hits.get(key, 0) + 1
    for i in range(len(m) - 4):
        if m[i] and m[i + 4]:
            if word_of[i] == word_of[min(i + 9, n - 1)]:
                frm_in += 1
            else:
                frm_x += 1
    sites = len(m) - 1
    return res, (dig_in / sites, dig_x / sites, frm_in / sites,
                 frm_x / sites), word_hits, n


def main() -> None:
    rng = np.random.default_rng(20260707)

    print("=== Cicada solved running text (2,058 runes, real order) ===")
    cw = cicada_running_words()
    res_c, split_c, words_c, n_c = shape_rates(cw)
    print(f"  {sum(len(w) for w in cw)} runes, {len(cw)} words")

    print("\n=== bag-of-words English (600k runes, iid word sampling) ===")
    bw = bag_of_words(600_000, rng)
    res_b, split_b, words_b, n_b = shape_rates(bw)

    print("\nper-site rates x 1000 (mono, digram, trigram, frame) by lag:")
    print(f"{'lag':>4} | {'Cicada running':^30} | {'bag-of-words':^30}")
    for lag in range(2, 13):
        c = res_c[lag]
        b = res_b[lag]
        print(f"{lag:>4} | {c[0]*1000:6.1f} {c[1]*1000:6.2f} "
              f"{c[2]*1000:6.2f} {c[3]*1000:6.2f} | "
              f"{b[0]*1000:6.1f} {b[1]*1000:6.2f} {b[2]*1000:6.2f} "
              f"{b[3]*1000:6.2f}")
    print("(uniform-random baselines: mono 34.5, digram/frame 1.19, "
          "trigram 0.04)")

    print("\nlag-5 shape split per site x 1000 "
          "(digram-in, digram-cross, frame-in, frame-cross):")
    print(f"  Cicada running: {split_c[0]*1000:.2f} {split_c[1]*1000:.2f} "
          f"{split_c[2]*1000:.2f} {split_c[3]*1000:.2f}")
    print(f"  bag-of-words  : {split_b[0]*1000:.2f} {split_b[1]*1000:.2f} "
          f"{split_b[2]*1000:.2f} {split_b[3]*1000:.2f}")

    print("\nrepeated 2-rune words behind cross-word lag-5 digram repeats "
          "(bag-of-words, top 10):")
    for k, v in sorted(words_b.items(), key=lambda x: -x[1])[:10]:
        print(f"  {k}: {v}")

    # ---- map availability onto the LP event mix
    n_lp = 12956
    chance = n_lp / 841
    print(f"\n=== availability -> LP mix (chance per shape ~{chance:.1f}, "
          f"n={n_lp}) ===")
    for label, split in (("Cicada", split_c), ("bag-of-words", split_b)):
        av_din = split[0] * n_lp
        av_dx = split[1] * n_lp
        av_f = (split[2] + split[3]) * n_lp
        print(f"  {label}: available digram-in {av_din:.1f}, "
              f"digram-cross {av_dx:.1f}, frame {av_f:.1f}")
        print("    LP observed:  digram-in 9 (chance ~1.5), "
              "digram-cross ~18 (chance ~12), frame 28 (chance 15.4)")
        if av_dx > 0:
            # marked events sit ON TOP of chance ciphertext coincidences,
            # so usage = (observed - chance) / plaintext availability
            print(f"    implied usage: digram-in {7.5/max(av_din,.1):.2f}, "
                  f"digram-cross {6.4/max(av_dx,.1):.2f}, "
                  f"frame {12.6/max(av_f,.1):.2f}")


if __name__ == "__main__":
    main()
