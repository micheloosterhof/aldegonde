# ABOUTME: Tests whether REAL runeglish plaintext has {1,4}-selective lag-5
# ABOUTME: pairing on its own -- the coherent (overlay-free) source of the anomaly.
"""Information-theory correction to walk+copy: a deterministic C[i]=C[i-5] copy
destroys P[i]'s information, so the only coherent lag-5 ciphertext match is
where P[i]=P[i-5] AND the alphabet repeats (g^5=id). Then the {1,4} PAIRING in
ciphertext equals the {1,4} pairing of the PLAINTEXT's own lag-5 self-matches.

So the whole question reduces to plaintext: do real runeglish lag-5 within-word
self-matches cluster at separations 1 and 4 more than 2,3,5? If yes, the walk
alone produces both faces and no copy overlay is needed. If no, the
plaintext-through-echo story fails and something else is required.

Pairing definitions (matching lag5-digraph-structure.md): with M[i] =
[x[i]==x[i+5]], a pair at separation d is M[i] and M[i+d] both set. d=1 is a
repeated bigram at distance 5 (XY...XY); d=4 is a repeated (1st,5th)-of-5 frame.
"""

from __future__ import annotations

import random
from collections import Counter

from d5_partial_leak import to_runeglish

DICT = "/usr/share/dict/web2"
RUNE_ORDER = "FU" "TH" "ORCGWHNI" "J" "EO" "PX" "S" "TB" "E" "M" "L" "NG" "OE" "DA" "AE" "Y" "IA" "EA"
# map runeglish tokens to indices 0..28 (order irrelevant for coincidence)
TOKENS = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J", "EO",
          "P", "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D", "A", "AE",
          "Y", "IA", "EA"]
TOK2I = {t: i for i, t in enumerate(TOKENS)}


def pairing(stream: list[int], wid: list[int], within_only: bool) -> Counter:
    """Separation histogram of consecutive lag-5 matches."""
    n = len(stream)
    match = []
    for i in range(n - 5):
        if within_only and wid[i] != wid[i + 5]:
            continue
        if stream[i] == stream[i + 5]:
            match.append(i)
    return Counter(b - a for a, b in zip(match, match[1:]))


def build_stream(words: list[list[str]]) -> tuple[list[int], list[int]]:
    stream, wid = [], []
    for k, w in enumerate(words):
        for t in w:
            if t in TOK2I:
                stream.append(TOK2I[t])
                wid.append(k)
    return stream, wid


def report(name: str, stream, wid) -> None:
    for within in (True, False):
        seps = pairing(stream, wid, within)
        d1, d4 = seps[1], seps[4]
        base = (seps[2] + seps[3] + seps[5]) / 3
        tag = "within-word" if within else "all pairs "
        print(f"  {name} [{tag}]: d1={d1} d4={d4} | d2={seps[2]} d3={seps[3]} "
              f"d5={seps[5]} (mean {base:.1f}) | (d1+d4)/2 vs base: "
              f"{(d1 + d4) / 2:.1f} vs {base:.1f}  ratio {(d1 + d4) / 2 / base:.2f}"
              if base else f"  {name} [{tag}]: sparse")


def main() -> None:
    rng = random.Random(24)
    words = []
    with open(DICT) as f:
        for line in f:
            x = line.strip().upper()
            if x.isalpha() and x.isascii() and len(x) >= 3:
                words.append(x)
    print(f"dictionary words: {len(words)}")

    # real-text-like stream: sample words, convert, concatenate (words carry the
    # within-word morphology that produces lag-5 bigram repeats)
    samp = [to_runeglish(w) for w in rng.sample(words, 60000)]
    samp = [w for w in samp if len(w) >= 6]  # need length >=6 to hold a lag-5 pair
    stream, wid = build_stream(samp)
    print(f"runeglish plaintext stream: {len(stream)} runes, {len(samp)} words (len>=6)")
    print("\nreal runeglish plaintext:")
    report("real", stream, wid)

    # null: shuffle each word's runes (destroys morpheme repeats, keeps length
    # and composition) -- if the {1,4} selectivity vanishes here, it is real
    # morphology, not an artifact
    shuf = []
    for w in samp:
        c = w[:]
        rng.shuffle(c)
        shuf.append(c)
    s2, w2 = build_stream(shuf)
    print("\nshuffled-within-word null (morphology destroyed):")
    report("null", s2, w2)


if __name__ == "__main__":
    main()
