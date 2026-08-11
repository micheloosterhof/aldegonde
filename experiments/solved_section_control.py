# ABOUTME: Negative control: within-word d5 rate on the encrypted-but-solved
# ABOUTME: Vigenere-class master-transcription sections.
"""Negative control: within-word d=5 statistics on solved-section ciphertext.

The master transcription's solved-but-encrypted sections (the Vigenère /
interrupted-key pages: WELCOME etc.) are real Cicada ciphertext over the
same register of runeglish plaintext, produced WITHOUT any distance-5
mechanics (keys of length 8/13, no copy rule). If the unsolved corpus's
within-word d=5 excess (4.92%, delta-0 only) were an artifact of
runeglish-in-runes + word tokenization, these sections would show it too.

Also compares the position-in-word profile of matches against the
English-morphology prediction: under plaintext-repeat back-references,
matched positions should follow where English words actually repeat
letters at distance 5 (computed from the frequency-weighted lexicon).

Usage: python experiments/solved_section_control.py
"""

from __future__ import annotations

from collections import Counter

from scipy.stats import binomtest

from aldegonde import c3301

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
R2I["ᛂ"] = R2I["ᛄ"]
MASTER = "data/liber-primus__transcription--master.txt"
UNSOLVED = "data/page0-56.txt"
WORD_END = set(c3301.MARK_CHARS + ",;:!?&$%" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS)
D = 5

# encrypted solved sections of the master transcription (constant-transform
# decodes fail; community solutions are Vigenère DIUINITY with interrupts
# etc.) -- see plaintext_control_corpus.py output for the section map
ENCRYPTED_SOLVED = {1, 5, 7}


def parse_sections(path: str, boundaries: set[str]) -> list[list[list[int]]]:
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
        elif ch in boundaries and cur:
            sections[-1].append(cur)
            cur = []
    if cur:
        sections[-1].append(cur)
    return [s for s in sections if s]


def d5_stats(words: list[list[int]], label: str) -> None:
    pairs = matches = 0
    reps = opps = 0
    for w in words:
        for k in range(len(w) - D):
            pairs += 1
            matches += int(w[k] == w[k + D])
        for k in range(len(w) - D - 1):
            opps += 1
            reps += int(w[k] == w[k + D] and w[k + 1] == w[k + D + 1])
    bt = binomtest(matches, pairs, 1 / MOD) if pairs else None
    p = bt.pvalue if bt else 1.0
    print(
        f"{label}: {matches}/{pairs} = "
        f"{matches / max(pairs, 1):.4f} (binom p={p:.3f} vs 1/29); "
        f"XY..XY {reps}/{opps}"
    )


def main() -> None:
    # master transcription: '%' is a line break here (not a page break),
    # so it must NOT close words; only '-' '.' '&' '$' do.
    master = parse_sections(
        MASTER, set(c3301.MARK_CHARS + "&" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS)
    )
    print(f"master transcription: {len(master)} sections")
    enc = [w for i, s in enumerate(master) if i in ENCRYPTED_SOLVED for w in s]
    n_runes = sum(len(w) for w in enc)
    print(
        f"\nencrypted-solved control (sections {sorted(ENCRYPTED_SOLVED)}, "
        f"{n_runes} runes, {len(enc)} words)"
    )
    d5_stats(enc, "  within-word d=5")
    for i in sorted(ENCRYPTED_SOLVED):
        d5_stats(master[i], f"  section {i}")

    # sanity: the unsolved corpus with the same machinery
    unsolved = parse_sections(
        UNSOLVED, set(c3301.MARK_CHARS + "&%" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS)
    )[:10]
    uw = [w for s in unsolved for w in s]
    print(f"\nunsolved corpus sanity ({sum(len(w) for w in uw)} runes)")
    d5_stats(uw, "  within-word d=5")

    # position-in-word profile: LP matches vs lexicon plaintext repeats
    from wordfreq import top_n_list, word_frequency

    def transliterate(word: str) -> list[int] | None:
        w = word.upper()
        if not w.isalpha():
            return None
        for a, b in (("K", "C"), ("Q", "C"), ("V", "U"), ("Z", "S")):
            w = w.replace(a, b)
        digraphs = {
            "TH": 2,
            "EO": 12,
            "NG": 21,
            "OE": 22,
            "AE": 25,
            "IA": 27,
            "IO": 27,
            "EA": 28,
        }
        singles = {
            c: i
            for i, c in enumerate(
                [
                    "F",
                    "U",
                    None,
                    "O",
                    "R",
                    "C",
                    "G",
                    "W",
                    "H",
                    "N",
                    "I",
                    "J",
                    None,
                    "P",
                    "X",
                    "S",
                    "T",
                    "B",
                    "E",
                    "M",
                    "L",
                    None,
                    None,
                    "D",
                    "A",
                    None,
                    "Y",
                    None,
                    None,
                ]
            )
            if c
        }
        out: list[int] = []
        i = 0
        while i < len(w):
            if w[i : i + 2] in digraphs:
                out.append(digraphs[w[i : i + 2]])
                i += 2
            elif w[i] in singles:
                out.append(singles[w[i]])
                i += 1
            else:
                return None
        return out

    lex_pos_pairs: Counter = Counter()
    lex_pos_reps: Counter = Counter()
    for eng in top_n_list("en", 30000):
        runes = transliterate(eng)
        if not runes:
            continue
        f = word_frequency(eng, "en")
        for k in range(len(runes) - D):
            lex_pos_pairs[k] += f
            if runes[k] == runes[k + D]:
                lex_pos_reps[k] += f

    lp_pos_pairs: Counter = Counter()
    lp_pos_match: Counter = Counter()
    for w in uw:
        for k in range(len(w) - D):
            lp_pos_pairs[k] += 1
            lp_pos_match[k] += int(w[k] == w[k + D])

    print("\nposition-in-word profile (match rate by start position k):")
    print(f"{'k':>3} {'LP rate':>9} {'lexicon plaintext rate':>23}")
    for k in range(7):
        lp = lp_pos_match[k] / lp_pos_pairs[k] if lp_pos_pairs[k] else 0
        lx = lex_pos_reps[k] / lex_pos_pairs[k] if lex_pos_pairs[k] else 0
        print(f"{k:>3} {lp:>9.4f} {lx:>23.4f}")


if __name__ == "__main__":
    main()
