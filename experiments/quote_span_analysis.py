# ABOUTME: Measures the seven quoted spans in the unsolved Liber Primus: their
# ABOUTME: lengths, and how their boundaries sit against the '.' marks.
"""What the quotation marks bracket.

Fourteen marks pair into seven spans (`contraction-cribs.md`). This asks two
things of them:

  1. Are the spans the length of English quoted speech, or arbitrary?
  2. Do the span edges land on '.' marks more than chance allows?

Question 2 bears on what the '.' marks are. `word-length-keystream-and-boundaries.md`
finds they carry no English sentence-final signature but do cluster at line
ends, and proposes they may be a mixture of real sentence ends and non-linguistic
marks. Quote placement is an independent probe: in English, quoted speech opens
and closes at sentence boundaries far more often than at word boundaries.

The line-end confound is controlled: '.' marks already sit at line ends 19.9% of
the time against a 3.7% baseline, so if quotes also favoured line ends the
adjacency could be induced by layout rather than language.
"""

from __future__ import annotations

import re
from math import comb
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
SEPARATORS = c3301.MARK_CHARS
BOUNDARY = c3301.MARK_CHARS + "%&$" + c3301.NUMERAL_CHARS


def clean_text() -> str:
    """Sections 0-9: excludes the solved AN END page and the Parable."""
    return "$".join(CORPUS.read_text().split("$")[:10])


def scan() -> tuple[list[dict], int, int]:
    """Quote records plus the corpus counts of '-' and '.' boundaries."""
    text = clean_text()
    quotes: list[dict] = []
    runes = words = dots = dashes = 0
    started = False
    for i, char in enumerate(text):
        if RUNE.match(char):
            runes += 1
            started = True
            continue
        if char in BOUNDARY:
            if char in c3301.CLUSTER_MARKS:
                dots += 1
            elif char in c3301.WORD_MARKS:
                dashes += 1
            if started:
                words += 1
                started = False
            continue
        if char != '"':
            continue
        # the separator this mark attaches to, looking outward
        before = next((c for c in reversed(text[:i]) if c in SEPARATORS or RUNE.match(c)), "")
        after = next((c for c in text[i + 1:] if c in SEPARATORS or RUNE.match(c)), "")
        opening = before in SEPARATORS
        # a line wrap '/' immediately after the mark means it sits at a line end
        trailing = text[i + 1:i + 3]
        quotes.append(
            {
                "at": i,
                "rune": runes,
                "word": words,
                "kind": "open" if opening else "close",
                "sep": before if opening else after,
                "line_end": "/" in trailing,
            }
        )
    return quotes, dashes, dots


def main() -> None:
    quotes, dashes, dots = scan()
    total = dashes + dots
    base = dots / total
    print(f"corpus boundaries: {dashes} '-' and {dots} '.'  -> '.' is {base:.1%}\n")

    text = clean_text()
    print("the seven spans")
    print(f"{'#':>2} {'words':>6} {'runes':>6} {'. inside':>9}  {'opens on':>9} {'closes on':>10}")
    spans = list(zip(quotes[::2], quotes[1::2]))
    lengths = []
    for n, (a, b) in enumerate(spans, 1):
        inner = text[a["at"] + 1:b["at"]]
        # words are maximal runs of runes; line wraps and page breaks are not
        # boundaries, but they are also never inside a run, so splitting on
        # every non-rune would over-count words that wrap. Merge those first.
        merged = re.sub(r"[/\n%&]", "", inner)
        words = len([w for w in re.split(r"[^ᚠ-᛿]", merged) if w])
        lengths.append(words)
        print(
            f"{n:>2} {words:>6} {b['rune'] - a['rune']:>6} "
            f"{sum(1 for c in inner if c in c3301.CLUSTER_MARKS):>9}"
            f"  {a['sep']:>9} {b['sep']:>10}"
        )
    print(f"\nspan lengths in words: {sorted(lengths)}")
    print(f"   median {sorted(lengths)[len(lengths) // 2]}, range {min(lengths)}-{max(lengths)}")

    # A span that wraps one '.'-delimited unit should not straddle a '.'.
    inside = sum(
        sum(1 for ch in text[a["at"] + 1:b["at"]] if ch in c3301.CLUSTER_MARKS)
        for a, b in spans
    )
    internal = sum(lengths) - len(spans)          # boundaries strictly inside spans
    exp_inside = internal * base
    p_inside = sum(
        comb(internal, k) * base**k * (1 - base) ** (internal - k)
        for k in range(inside + 1)
    )
    print(f"\n'.' marks strictly inside spans: {inside} across {internal} internal boundaries")
    print(f"   expected {exp_inside:.1f};  P(<= {inside}) = {p_inside:.3f}")

    hits = sum(1 for q in quotes if q["sep"] in c3301.CLUSTER_MARKS)
    print(f"\nspan edges landing on a '.' mark: {hits} of {len(quotes)}")
    print(f"   expected under random word boundaries: {base * len(quotes):.1f}")
    p = sum(
        comb(len(quotes), k) * base**k * (1 - base) ** (len(quotes) - k)
        for k in range(hits, len(quotes) + 1)
    )
    print(f"   P(>= {hits}) = {p:.3g}")

    # The null assumes quotes pick word boundaries uniformly. Rather than model
    # every layout effect, ask how strong one would have to be to matter.
    lo, hi = base, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        tail = sum(
            comb(len(quotes), k) * mid**k * (1 - mid) ** (len(quotes) - k)
            for k in range(hits, len(quotes) + 1)
        )
        lo, hi = (lo, mid) if tail > 0.05 else (mid, hi)
    print(f"   robustness: '.' would have to be {lo:.0%} of boundaries at "
          f"quote-eligible positions ({lo / base:.1f}x the corpus rate) before")
    print(f"   {hits} of {len(quotes)} stopped being surprising at p=0.05.")
    print("   The strongest layout coupling on record is '.' at line ends, 3.7x.")

    opens = [q for q in quotes if q["kind"] == "open"]
    closes = [q for q in quotes if q["kind"] == "close"]
    n_open = sum(1 for q in opens if q["sep"] in c3301.CLUSTER_MARKS)
    n_close = sum(1 for q in closes if q["sep"] in c3301.CLUSTER_MARKS)
    print(f"   opens on a cluster mark: {n_open} of {len(opens)}")
    print(f"   closes on a cluster mark: {n_close} of {len(closes)}")

    at_line_end = sum(1 for q in quotes if q["line_end"])
    print(f"\nlayout confound: {at_line_end} of {len(quotes)} marks sit at a line end")
    print("   ('.' marks sit at line ends 19.9% of the time, '-' marks 3.7%)")

    # If the '.' marks are a mixture of real sentence ends and filler, the ones
    # a quote attaches to should be the real ones, and the English signature is
    # a long word before the mark.
    print("\nmixture probe: word length before '.' marks")
    marked = {q["at"] for q in quotes}
    tagged, other = [], []
    text = clean_text()
    length = 0
    for i, char in enumerate(text):
        if RUNE.match(char):
            length += 1
        elif char in BOUNDARY:
            if char in c3301.CLUSTER_MARKS and length:
                near = any(abs(i - m) <= 2 for m in marked)
                (tagged if near else other).append(length)
            if char in BOUNDARY:
                length = 0
        elif char in "'\"":
            continue
    def mean(v: list[int]) -> float:
        return sum(v) / len(v) if v else float("nan")

    print(f"   quote-adjacent marks (n={len(tagged)}): mean {mean(tagged):.2f}")
    print(f"   all other marks     (n={len(other)}): mean {mean(other):.2f}")
    print("   corpus word mean 4.42; solved-page sentence finals 5.56")
    print("   n is far too small to decide; reported so it is not mistaken for support")


if __name__ == "__main__":
    main()
