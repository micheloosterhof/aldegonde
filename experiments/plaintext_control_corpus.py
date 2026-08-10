#!/usr/bin/env python3
# ABOUTME: Builds runeglish plaintext controls (solved LP sections + frequency-weighted
# ABOUTME: lexicon) and writes their within-word lag-5 delta stats to a JSON.
"""Build genuine runeglish plaintext controls for the lag-5 statistics.

Two independent controls:

1. IN-DOMAIN: the solved sections of the master transcription that decrypt
   with a per-section constant transform (identity / shift / atbash+shift).
   Every candidate transform is scored with the runeglish quadgram table;
   accepted decodes are printed for eyeball verification. This yields
   Cicada's own runeglish (their orthography, their register) with genuine
   word boundaries.

2. LEXICON: the top-N English words by frequency (wordfreq package),
   transliterated to Gematria-Primus runeglish (greedy digraph-first),
   frequency-weighted. Within-word statistics depend only on the word
   multiset, so this is a proper control for within-word questions.

For each control we measure the quantities the mixture discriminator
(within_word_delta_mixture.py) needs:

- within-word distance-5 match rate (and per word length),
- the full 29-bin distribution Q of (P[k+5] - P[k]) mod 29 within words,
- the rate of XY···XY repeats (digraph repeat at distance 5 inside a word),
- for the in-domain control also the unrestricted (stream) lag-5
  difference distribution.

Usage: python experiments/plaintext_control_corpus.py
"""

from __future__ import annotations

import json
import math

from aldegonde import c3301

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
R2I["ᛂ"] = R2I["ᛄ"]  # both glyph variants of J appear in the data files
LETTERS = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J",
           "EO", "P", "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D",
           "A", "AE", "Y", "IA", "EA"]
MASTER = "data/liber-primus__transcription--master.txt"
QUADGRAMS = "src/aldegonde/data/ngrams/runeglish/quadgrams.txt"
OUT_JSON = "experiments/plaintext_control_stats.json"

WORD_END = set(c3301.MARK_CHARS + ",;:!?&$" + c3301.NUMERAL_CHARS)


# ----------------------------------------------------------------- scoring
def load_quadgram_scorer():
    scores: dict[tuple[int, int, int, int], float] = {}
    total = 0
    with open(QUADGRAMS) as f:
        raw = []
        for line in f:
            gram, cnt = line.split()
            c = int(cnt)
            raw.append((tuple(R2I[ch] for ch in gram), c))
            total += c
    floor = math.log10(0.01 / total)
    for gram, c in raw:
        scores[gram] = math.log10(c / total)

    def score(seq: list[int]) -> float:
        if len(seq) < 4:
            return floor
        s = 0.0
        for i in range(len(seq) - 3):
            s += scores.get(tuple(seq[i:i + 4]), floor)
        return s / (len(seq) - 3)

    return score


# ----------------------------------------------------------------- parsing
def parse_sections(path: str) -> list[list[list[int]]]:
    """$-sections as lists of words; '/', '%' and newlines are line wraps."""
    with open(path) as f:
        raw = f.read()
    sections: list[list[list[int]]] = [[]]
    cur: list[int] = []
    for ch in raw:
        if ch in R2I:
            cur.append(R2I[ch])
        elif ch == "$":
            if cur:
                sections[-1].append(cur)
                cur = []
            sections.append([])
        elif ch in WORD_END and cur:
            sections[-1].append(cur)
            cur = []
    if cur:
        sections[-1].append(cur)
    return [s for s in sections if s]


# ------------------------------------------------------------ decrypt scan
def candidate_decodes(section: list[list[int]]):
    """(name, decoded words) for identity/shift/atbash+shift transforms."""
    for shift in range(MOD):
        yield (f"shift-{shift}",
               [[(c - shift) % MOD for c in w] for w in section])
    for shift in range(MOD):
        yield (f"atbash+{shift}",
               [[(MOD - 1 - c - shift) % MOD for c in w] for w in section])


def to_english(words: list[list[int]]) -> str:
    return " ".join("".join(LETTERS[c] for c in w) for w in words)


# ------------------------------------------------------------- statistics
def within_word_stats(words: list[list[int]], weights=None):
    """d=5 pair counts/matches, Q histogram, XY..XY count, by-length rates."""
    if weights is None:
        weights = [1.0] * len(words)
    pairs = matches = 0.0
    q = [0.0] * MOD
    digraph_reps = 0.0
    digraph_opps = 0.0
    by_len: dict[int, list[float]] = {}
    for w, wt in zip(words, weights):
        loc_pairs = max(0, len(w) - 5)
        for k in range(loc_pairs):
            d = (w[k + 5] - w[k]) % MOD
            q[d] += wt
            pairs += wt
            if d == 0:
                matches += wt
        bl = by_len.setdefault(len(w), [0.0, 0.0])
        bl[0] += wt * loc_pairs
        bl[1] += wt * sum(1 for k in range(loc_pairs) if w[k] == w[k + 5])
        for k in range(max(0, len(w) - 6)):
            digraph_opps += wt
            if w[k] == w[k + 5] and w[k + 1] == w[k + 6]:
                digraph_reps += wt
    return {
        "pairs": pairs, "matches": matches,
        "rate": matches / pairs if pairs else 0.0,
        "Q": q,
        "digraph_reps": digraph_reps, "digraph_opps": digraph_opps,
        "by_len": {k: v for k, v in sorted(by_len.items()) if v[0] > 0},
    }


def stream_lag5_q(words: list[list[int]]) -> list[float]:
    stream = [c for w in words for c in w]
    q = [0.0] * MOD
    for i in range(len(stream) - 5):
        q[(stream[i + 5] - stream[i]) % MOD] += 1
    return q


# ------------------------------------------------------------------ main
def main() -> None:
    score = load_quadgram_scorer()
    sections = parse_sections(MASTER)
    print(f"master transcription: {len(sections)} sections, "
          f"{sum(len(w) for s in sections for w in s)} runes total\n")

    accepted: list[list[list[int]]] = []
    for idx, sec in enumerate(sections):
        flat_len = sum(len(w) for w in sec)
        best_name, best_words, best_score = None, None, -99.0
        for name, words in candidate_decodes(sec):
            s = score([c for w in words for c in w])
            if s > best_score:
                best_name, best_words, best_score = name, words, s
        # calibration: constant-transform decodes of the genuinely solved
        # sections score -4.2..-4.8 (short-table quadgram coverage);
        # everything undecoded sits at -6.5 or below. Threshold between.
        ok = best_score > -5.5
        tag = "ACCEPT" if ok else "reject"
        preview = to_english(best_words)[:72]
        print(f"section {idx:>2} ({flat_len:>5} runes) best={best_name:<10}"
              f" score={best_score:>6.2f} {tag}  {preview}")
        if ok:
            accepted.append(best_words)

    words = [w for s in accepted for w in s]
    print(f"\nIN-DOMAIN control: {len(accepted)} sections, {len(words)} words,"
          f" {sum(len(w) for w in words)} runes")
    dom = within_word_stats(words)
    dom["stream_Q"] = stream_lag5_q(words)
    print(f"  within-word d=5: {dom['matches']:.0f}/{dom['pairs']:.0f}"
          f" = {dom['rate']:.4f} (uniform 0.0345)")
    print(f"  XY..XY repeats: {dom['digraph_reps']:.0f}"
          f" / {dom['digraph_opps']:.0f} opportunities"
          f" = {dom['digraph_reps']/max(dom['digraph_opps'],1):.5f}")
    q = dom["Q"]
    tot = sum(q)
    print("  Q (within-word lag-5 delta distribution, x29/uniform):")
    print("   " + " ".join(f"{MOD*v/tot:.2f}" for v in q))

    # ------------------------------------------------------------- lexicon
    try:
        from wordfreq import top_n_list, word_frequency
    except ModuleNotFoundError:
        print("\nLEXICON control skipped: `pip install wordfreq` to enable it.")
        print("(The in-domain control above is the register-matched, load-bearing one.)")
        with open(OUT_JSON, "w") as f:
            json.dump({"in_domain": dom, "lexicon": None}, f)
        print(f"wrote {OUT_JSON} (in-domain only)")
        return

    def transliterate(word: str) -> list[int] | None:
        w = word.upper()
        if not w.isalpha():
            return None
        w = w.replace("K", "C").replace("Q", "C").replace("V", "U")
        w = w.replace("Z", "S")
        out: list[int] = []
        i = 0
        digraphs = {"TH": 2, "EO": 12, "NG": 21, "OE": 22, "AE": 25,
                    "IA": 27, "IO": 27, "EA": 28}
        singles = {"F": 0, "U": 1, "O": 3, "R": 4, "C": 5, "G": 6, "W": 7,
                   "H": 8, "N": 9, "I": 10, "J": 11, "P": 13, "X": 14,
                   "S": 15, "T": 16, "B": 17, "E": 18, "M": 19, "L": 20,
                   "D": 23, "A": 24, "Y": 26}
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

    lex_words: list[list[int]] = []
    lex_weights: list[float] = []
    for eng in top_n_list("en", 30000):
        runes = transliterate(eng)
        if runes:
            lex_words.append(runes)
            lex_weights.append(word_frequency(eng, "en"))
    print(f"\nLEXICON control: {len(lex_words)} transliterated words,"
          f" frequency-weighted")
    lex = within_word_stats(lex_words, lex_weights)
    print(f"  within-word d=5 rate: {lex['rate']:.4f} (uniform 0.0345)")
    print(f"  XY..XY rate per opportunity: "
          f"{lex['digraph_reps']/max(lex['digraph_opps'],1e-12):.5f}")
    qq = lex["Q"]
    tot = sum(qq)
    print("  Q (within-word lag-5 delta distribution, x29/uniform):")
    print("   " + " ".join(f"{MOD*v/tot:.2f}" for v in qq))
    print("  by length (pairs-weight, rate): "
          + ", ".join(f"L{k}:{v[1]/v[0]:.3f}" for k, v in lex["by_len"].items()
                      if k <= 12 and v[0] > 0))

    with open(OUT_JSON, "w") as f:
        json.dump({"in_domain": dom, "lexicon":
                   {k: v for k, v in lex.items() if k != "by_len"}}, f)
    print(f"\nwrote {OUT_JSON}")


if __name__ == "__main__":
    main()
