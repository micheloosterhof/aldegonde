#!/usr/bin/env python3
"""Census of composite lag-5 copy shapes, their plaintext availability,
and the parity/phase of event starts.

Questions this answers (raised against the copy-semantics picture):

1. SHAPE SELECTIVITY. The two confirmed event shapes are the contiguous
   digram repeat XY···XY (matches at separation 1) and the frame repeat
   X···Y X···Y (separation 4). If the mechanism marked plaintext lag-5
   repeats indiscriminately, gapped shapes (X·Y··X·Y at separation 2,
   X··Y·X··Y at separation 3) and composites (XY·AB XY·AB = two digram
   repeats 3 apart; XYZ··XYZ trigram repeats) should appear in
   proportion to their plaintext availability. Measure both sides:
   LP counts per shape vs the frequency-weighted runeglish lexicon's
   opportunity rates (and chance).

2. USAGE FRACTIONS. Under plaintext-repeat back-references the marked
   events are a subset of plaintext opportunities: usage = excess over
   chance / expected plaintext opportunities. A usage fraction over 1 is
   impossible for that branch.

3. PARITY / PHASE. If encryption operated on symbol PAIRS (a digraph
   cipher grid) or any fixed frame, event starts should prefer a parity
   or phase class measured from the grid origin. Test d1/d4 event starts
   and all matches mod 2 and mod 5 from four origins: text start,
   section start, page start, word start.

Usage: python experiments/copy_shape_census.py
"""

from __future__ import annotations

from collections import Counter

from scipy.stats import binomtest

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
D = 5

# shape name -> list of (offset a, offset b) meaning C[i+a] == C[i+a+5]
# for every listed a; span = largest index touched
SHAPES = {
    "digram XY...XY (sep1)": [0, 1],
    "gapped X.Y..X.Y (sep2)": [0, 2],
    "gapped X..Y.X..Y (sep3)": [0, 3],
    "frame X...YX...Y (sep4)": [0, 4],
    "trigram XYZ..XYZ": [0, 1, 2],
    "tetragram WXYZ.WXYZ": [0, 1, 2, 3],
    "double digram XY.ABXY.AB": [0, 1, 3, 4],
}


def parse_full():
    """Clean corpus with word / page / section coordinates."""
    with open(DATA) as f:
        text = f.read()
    stream: list[int] = []
    word_of: list[int] = []
    page_of: list[int] = []
    sec_of: list[int] = []
    word = page = sec = 0
    in_word = False
    for ch in text:
        if ch in R2I:
            stream.append(R2I[ch])
            word_of.append(word)
            page_of.append(page)
            sec_of.append(sec)
            in_word = True
        elif ch == "%":
            if in_word:
                word += 1
                in_word = False
            page += 1
        elif ch == "$":
            if in_word:
                word += 1
                in_word = False
            sec += 1
        elif ch in "-.&" and in_word:
            word += 1
            in_word = False
    keep = [i for i, s in enumerate(sec_of) if s < 10]
    assert len(keep) == 12956
    return ([stream[i] for i in keep], [word_of[i] for i in keep],
            [page_of[i] for i in keep], [sec_of[i] for i in keep])


def shape_counts(c: list[int], word_of: list[int]):
    """LP occurrences of each shape, total and entirely-within-one-word."""
    n = len(c)
    m = [c[i] == c[i + D] if i + D < n else False for i in range(n)]
    out = {}
    for name, offs in SHAPES.items():
        span = max(offs) + D
        total = within = 0
        for i in range(n - span):
            if all(m[i + a] for a in offs):
                total += 1
                if word_of[i] == word_of[i + span]:
                    within += 1
        out[name] = (total, within)
    return out, m


def lexicon_rates():
    """Frequency-weighted plaintext rate of each shape inside words,
    per within-word window of the needed span."""
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

    hits = dict.fromkeys(SHAPES, 0.0)
    opps = dict.fromkeys(SHAPES, 0.0)
    for eng in top_n_list("en", 30000):
        r = transliterate(eng)
        if not r:
            continue
        f = word_frequency(eng, "en")
        for name, offs in SHAPES.items():
            span = max(offs) + D
            for k in range(len(r) - span):
                opps[name] += f
                if all(r[k + a] == r[k + a + D] for a in offs):
                    hits[name] += f
    return {name: (hits[name] / opps[name] if opps[name] else 0.0)
            for name in SHAPES}


def main() -> None:
    c, word_of, page_of, sec_of = parse_full()
    n = len(c)
    counts, m = shape_counts(c, word_of)
    lex = lexicon_rates()

    print("=== shape census: LP observed vs chance vs plaintext availability ===")
    print(f"{'shape':>26} {'LP tot':>6} {'LP in-word':>10} "
          f"{'chance/site':>11} {'plaintext/site':>14} {'in-word sites':>13}")
    word_sites = {}
    for name, offs in SHAPES.items():
        span = max(offs) + D
        sites = sum(1 for i in range(n - span)
                    if word_of[i] == word_of[i + span])
        word_sites[name] = sites
        chance = (1 / MOD) ** len(offs)
        tot, win = counts[name]
        print(f"{name:>26} {tot:>6} {win:>10} {chance:>11.6f} "
              f"{lex[name]:>14.6f} {sites:>13}")

    print("\n=== in-word excess vs plaintext availability (usage fractions) ===")
    for name, offs in SHAPES.items():
        sites = word_sites[name]
        chance = sites * (1 / MOD) ** len(offs)
        avail = sites * lex[name]
        tot, win = counts[name]
        excess = win - chance
        usage = excess / (avail - chance) if avail > chance else float("nan")
        print(f"{name:>26}: in-word {win:>3} vs chance {chance:6.2f}; "
              f"plaintext offers {avail:6.2f}; usage = {usage:+.2f}")

    # ---------------------------------------------------------- parity/phase
    d1 = [i for i in range(len(m) - 1) if m[i] and m[i + 1]]
    d4 = [i for i in range(len(m) - 4) if m[i] and m[i + 4]]
    matches = [i for i in range(len(m)) if m[i]]

    word_start: dict[int, int] = {}
    page_start: dict[int, int] = {}
    sec_start: dict[int, int] = {}
    for i in range(n):
        word_start.setdefault(word_of[i], i)
        page_start.setdefault(page_of[i], i)
        sec_start.setdefault(sec_of[i], i)

    origins = {
        "text": lambda i: i,
        "section": lambda i: i - sec_start[sec_of[i]],
        "page": lambda i: i - page_start[page_of[i]],
        "word": lambda i: i - word_start[word_of[i]],
    }
    groups = {"d1 events": d1, "d4 events": d4, "all matches": matches}

    print("\n=== parity / phase of event starts ===")
    for gname, idxs in groups.items():
        print(f"{gname} (n={len(idxs)}):")
        for oname, fn in origins.items():
            offs = [fn(i) for i in idxs]
            base = [fn(i) for i in range(n)]
            for mod in (2, 5):
                got = Counter(o % mod for o in offs)
                exp = Counter(o % mod for o in base)
                tot_exp = sum(exp.values())
                # chi2 against the opportunity distribution
                chi = sum((got.get(r, 0) - len(offs) * exp[r] / tot_exp) ** 2
                          / (len(offs) * exp[r] / tot_exp)
                          for r in range(mod))
                if mod == 2:
                    p_even = exp[0] / tot_exp
                    bt = binomtest(got.get(0, 0), len(offs), p_even)
                    print(f"  from {oname:>7} mod 2: even {got.get(0, 0):>3}"
                          f"/{len(idxs)} (expect {len(idxs)*p_even:.1f}), "
                          f"p = {bt.pvalue:.3f}")
                else:
                    from scipy.stats import chi2 as chi2_dist
                    p = 1 - chi2_dist.cdf(chi, mod - 1)
                    cells = " ".join(str(got.get(r, 0)) for r in range(mod))
                    print(f"  from {oname:>7} mod 5: [{cells}] "
                          f"chi2 = {chi:.1f}, p = {p:.3f}")

    # ------------------------------------------- trigram:digram ratio check
    tot2, win2 = counts["digram XY...XY (sep1)"]
    tot3, win3 = counts["trigram XYZ..XYZ"]
    r_lex = lex["trigram XYZ..XYZ"] / lex["digram XY...XY (sep1)"]
    print("\n=== pairs vs triplets ===")
    print(f"LP in-word digram repeats {win2}, trigram repeats {win3} "
          f"(ratio {win3/max(win2,1):.2f})")
    print(f"plaintext lexicon ratio trigram/digram per site: {r_lex:.3f}")
    chance3 = word_sites["trigram XYZ..XYZ"] / MOD ** 3
    print(f"trigram chance expectation in-word: {chance3:.3f}; "
          f"if digram-excess usage applied to trigram availability: "
          f"{(win2 - word_sites['digram XY...XY (sep1)']/MOD**2) * r_lex:.1f}"
          f" expected marked trigrams (before double counting)")


if __name__ == "__main__":
    main()
