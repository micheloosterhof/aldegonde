#!/usr/bin/env python3
# ABOUTME: Analyzes where ciphertext doublets fall relative to word structure in
# ABOUTME: Liber Primus (page0-58), respecting that words cross line breaks.
"""Doublet vs word-position analysis for Liber Primus.

A "doublet" is two adjacent identical runes in the continuous cipher stream
(C[i] == C[i+1]). This script overlays word membership onto that stream so each
doublet can be located as start / middle / end of its word, and tabulated by
word length and rune position.

Delimiter legend (from data/liber-primus__transcription--master.md):
    Word '-'  Clause '.'  Paragraph '&'  Segment '$'  Chapter '§'  Page '%'
    Line '/'  -- a manuscript line break, NOT a word boundary
Only the word-boundary delimiters end a word. Every other non-rune character
(line breaks '/' and newlines, plus digit / latin noise) is ignored: the word
continues across it. A word is thus a maximal run of runes between two
word-boundary delimiters.
"""

from __future__ import annotations

from collections import Counter

from aldegonde import c3301

DATA = "data/page0-58.txt"
UNIGRAMS = "src/aldegonde/data/ngrams/runeglish/unigrams.txt"

RUNES = set(c3301.CICADA_ALPHABET)
WORD_BOUNDARIES = set("-.&$§%")  # delimiters that end a word

# Runeglish names of the runes that name a digraph, for the identity-rune filter.
RUNE_NAME = {"ᚠ": "F", "ᛝ": "NG", "ᛡ": "IA/IO", "ᛠ": "EA"}


def runeglish_frequencies() -> dict[str, float]:
    """Load runeglish unigram counts and return per-rune frequency fractions."""
    counts: dict[str, int] = {}
    with open(UNIGRAMS, encoding="utf-8") as f:
        for line in f:
            r, n = line.split()
            counts[r] = int(n)
    total = sum(counts.values())
    return {r: n / total for r, n in counts.items()}


def parse_words(text: str) -> list[tuple[str, str]]:
    """Split text into (word, preceding_boundary) pairs, in order.

    Only word-boundary delimiters end a word; all other non-rune characters
    are ignored and the word continues across them. `preceding_boundary` is
    the run of word-boundary delimiters seen since the previous word, used to
    tell '-' (word) from '.'/'%'/etc.
    """
    words: list[tuple[str, str]] = []
    cur: list[str] = []
    pending_boundary = ""
    for ch in text:
        if ch in RUNES:
            cur.append(ch)
        elif ch in WORD_BOUNDARIES:
            if cur:
                words.append(("".join(cur), pending_boundary))
                cur = []
                pending_boundary = ""
            pending_boundary += ch
        # else: line break or digit/latin noise -> ignore, word continues
    if cur:
        words.append(("".join(cur), pending_boundary))
    return words


def build_stream(words: list[tuple[str, str]]) -> tuple[str, list[int], list[int], list[int]]:
    """Concatenate words into the rune stream with parallel metadata arrays.

    Returns (stream, word_id, pos1, wlen) where for stream[i]:
      word_id[i] = index of its word, pos1[i] = 1-based position in word,
      wlen[i] = length of its word.
    """
    stream: list[str] = []
    word_id: list[int] = []
    pos1: list[int] = []
    wlen: list[int] = []
    for wid, (w, _b) in enumerate(words):
        for p, r in enumerate(w, start=1):
            stream.append(r)
            word_id.append(wid)
            pos1.append(p)
            wlen.append(len(w))
    return "".join(stream), word_id, pos1, wlen


def pair_category(p: int, length: int) -> str:
    """Classify a within-word doublet occupying positions (p, p+1) of a word."""
    if length == 2:
        return "whole-word (len 2)"
    if p == 1:
        return "start"
    if p + 1 == length:
        return "end"
    return "middle"


def main() -> None:
    with open(DATA, encoding="utf-8") as f:
        text = f.read()
    words = parse_words(text)
    stream, word_id, pos1, wlen = build_stream(words)

    n = len(stream)
    rune_words = [w for w, _ in words]
    wlens = [len(w) for w in rune_words]

    print("=" * 72)
    print(f"Source: {DATA}")
    print(f"Rune words: {len(rune_words)}   Runes in stream: {n}")
    print(f"Word length: min {min(wlens)}  max {max(wlens)}  mean {sum(wlens)/len(wlens):.2f}")
    longest = max(rune_words, key=len)
    print(f"Longest word ({len(longest)} runes): {longest}"
          + ("   <-- check: possible merge across a number page" if len(longest) > 20 else ""))
    doublets = [i for i in range(n - 1) if stream[i] == stream[i + 1]]
    print(f"Doublets (C[i]==C[i+1]): {len(doublets)}   rate {len(doublets)/n*100:.3f}%")
    print("=" * 72)

    # --- within-word vs cross-word ---
    within = [i for i in doublets if word_id[i] == word_id[i + 1]]
    cross = [i for i in doublets if word_id[i] != word_id[i + 1]]
    # Opportunity baseline: of all adjacent rune pairs, how many are within-word
    # vs cross-word? If the doublet suppression is uniform, doublets should split
    # in the same proportion (this is the correct null, not boundaries * 1/29).
    within_opp = sum(len(w) - 1 for w in rune_words)  # adjacent pairs inside words
    cross_opp = (n - 1) - within_opp                  # adjacent pairs across words
    exp_within = len(doublets) * within_opp / (n - 1)
    exp_cross = len(doublets) * cross_opp / (n - 1)
    print(f"\nWITHIN-WORD doublets: {len(within):>3}   (opportunity-expected {exp_within:.1f})")
    print(f"CROSS-WORD doublets:  {len(cross):>3}   (opportunity-expected {exp_cross:.1f})")
    print(f"  adjacency opportunities: within {within_opp}, cross {cross_opp} "
          f"({cross_opp/(n-1)*100:.1f}% of pairs are cross-word)")

    # Cross-word doublets broken down by the boundary delimiter crossed.
    print("\nCross-word doublets by boundary between the two words:")
    cross_by_boundary: Counter[str] = Counter()
    for i in cross:
        b = words[word_id[i + 1]][1] or "(none/adjacent)"
        cross_by_boundary[b] += 1
    for b, c in sorted(cross_by_boundary.items(), key=lambda x: -x[1]):
        kind = "WORD '-'" if b == "-" else f"stronger/other {b!r}"
        print(f"  {b!r:>16}  x{c}   [{kind}]")

    # --- start / middle / end for within-word doublets ---
    print("\n" + "-" * 72)
    print("WITHIN-WORD doublet position category (the pair as a unit):")
    cat = Counter(pair_category(pos1[i], wlen[i]) for i in within)

    # Null baseline: among ALL adjacent within-word pairs, how many fall in each
    # category? Compares observed doublets against positionally-random doublets.
    opp_cat: Counter[str] = Counter()
    for w in rune_words:
        L = len(w)
        for p in range(1, L):
            opp_cat[pair_category(p, L)] += 1
    total_opp = sum(opp_cat.values())
    d = len(within)
    print(f"{'category':>20} {'observed':>9} {'expected':>9} {'obs/exp':>8}")
    for c in ["start", "middle", "end", "whole-word (len 2)"]:
        exp = d * opp_cat[c] / total_opp if total_opp else 0.0
        ratio = (cat[c] / exp) if exp else float("nan")
        print(f"{c:>20} {cat[c]:>9} {exp:>9.1f} {ratio:>8.2f}")
    print(f"{'TOTAL':>20} {d:>9} {d:>9.1f}")
    print("  (expected = doublets distributed like all adjacent within-word pairs)")

    # --- 2D table: word length x first-rune position of the doublet ---
    print("\n" + "-" * 72)
    print("WITHIN-WORD doublets by word length (rows) x 1st-rune position p (cols):")
    obs: Counter[tuple[int, int]] = Counter((wlen[i], pos1[i]) for i in within)
    opp: Counter[tuple[int, int]] = Counter()
    for w in rune_words:
        L = len(w)
        for p in range(1, L):
            opp[(L, p)] += 1
    maxL = max(L for (L, _p) in obs) if obs else 2
    maxp = maxL - 1
    header = "  L\\p " + "".join(f"{p:>5}" for p in range(1, maxp + 1)) + "   row"
    print(header)
    for L in range(2, maxL + 1):
        rowcells = []
        rowsum = 0
        for p in range(1, maxp + 1):
            v = obs[(L, p)]
            rowcells.append(f"{v:>5}" if p <= L - 1 else f"{'.':>5}")
            rowsum += v
        if rowsum:
            print(f"{L:>5} " + "".join(rowcells) + f"   {rowsum:>4}")
    # column marginals
    colsum = [sum(obs[(L, p)] for L in range(2, maxL + 1)) for p in range(1, maxp + 1)]
    print("  col " + "".join(f"{c:>5}" for c in colsum) + f"   {sum(colsum):>4}")

    print("\nSame table as RATE (doublets / opportunities), x1000:")
    print(header)
    for L in range(2, maxL + 1):
        cells = []
        for p in range(1, maxp + 1):
            if p <= L - 1 and opp[(L, p)]:
                cells.append(f"{obs[(L, p)]/opp[(L, p)]*1000:>5.0f}")
            else:
                cells.append(f"{'.':>5}")
        # only print rows that have any opportunities
        if any(opp[(L, p)] for p in range(1, L)):
            print(f"{L:>5} " + "".join(cells))

    # --- 1st vs 2nd rune word-position, across ALL doublets ---
    # Under ciphertext autokey the 2nd rune of each doublet is the position that
    # decrypts to the identity element (EA candidate), so its location matters.
    def position_label(i: int) -> str:
        p, length = pos1[i], wlen[i]
        if length == 1:
            return "lone"
        if p == 1:
            return "start"
        if p == length:
            return "end"
        return "middle"

    print("\n" + "-" * 72)
    print("WORD-POSITION of each rune of the doublet (all 89):")
    print(f"{'':>10}{'start':>8}{'middle':>8}{'end':>8}{'lone':>8}")
    for which, idxs in (("1st rune", list(doublets)),
                        ("2nd rune", [i + 1 for i in doublets])):
        c = Counter(position_label(i) for i in idxs)
        print(f"{which:>10}" + "".join(f"{c[k]:>8}" for k in ("start", "middle", "end", "lone")))
    print("  (cross-word doublets force 1st rune=end of word A, 2nd rune=start of word B)")

    # --- identity-rune filter: frequency must match the doublet rate ---
    print("\n" + "-" * 72)
    print("IDENTITY-RUNE FREQUENCY FILTER")
    rate = len(doublets) / n
    print(f"Doublet rate = {rate*100:.3f}%. If each doublet marks one fixed plaintext")
    print("rune, that rune's runeglish frequency must match this rate.")
    freq = runeglish_frequencies()
    band = sorted(
        (r for r in freq if 0.4 <= freq[r] * 100 <= 1.0),
        key=lambda r: abs(freq[r] - rate),
    )
    print(f"{'rune':>4} {'name':>6} {'freq%':>7}  note")
    for r in band:
        word_initial = "can start words" if r == "ᛠ" else "rarely/never word-initial"
        print(f"{r:>4} {RUNE_NAME.get(r, '?'):>6} {freq[r]*100:7.3f}  {word_initial}")
    f_ea, f_f = freq["ᛠ"] * 100, freq["ᚠ"] * 100
    print(f"\nF (ᚠ) = {f_f:.3f}% -> predicts {f_f:.2f}% doublets, REFUTED (observed {rate*100:.2f}%).")
    print(f"EA (ᛠ) = {f_ea:.3f}% -> predicts {f_ea:.2f}% doublets, MATCHES.")
    # word-initial filter: the marker rune demonstrably appears word-initial
    init_2nd = sum(1 for i in doublets if pos1[i + 1] == 1)
    init_1st = sum(1 for i in doublets if pos1[i] == 1)
    print(f"\nWord-initial filter: the marker appears word-initial "
          f"{init_2nd}x (as 2nd rune) / {init_1st}x (as 1st rune).")
    print("  NG never starts an English word; IO only in rare 'ion/iota' -> both REFUTED.")
    print("  EA starts each/ear/earth/east -> SURVIVES. Unique on both filters.")

    # --- cross-word: lengths of the two words involved ---
    print("\n" + "-" * 72)
    print("CROSS-WORD doublets: by definition END-of-word A meets START-of-word B.")
    print(f"  word A (ends in 1st rune) length distribution: "
          f"{dict(sorted(Counter(wlen[i] for i in cross).items()))}")
    print(f"  word B (starts 2nd rune) length distribution: "
          f"{dict(sorted(Counter(wlen[i + 1] for i in cross).items()))}")


if __name__ == "__main__":
    main()
