# ABOUTME: Anatomises the short-word deficit: is it uniform, or does it depend
# ABOUTME: on section, position, segmentation convention or line layout?
"""Where does the short-word deficit live?

The unsolved corpus has proportionally fewer 1-2 rune words than the same
author's solved pages (19.3% against 27.9%, z ~ 4.7,
`word-length-keystream-and-boundaries.md`). Encryption cannot cause it — word
lengths pass through any rune substitution untouched — so either the plaintext
really is that telegraphic, or the word boundaries are not plaintext-faithful.
If they are not, word lengths are key material and cribbing on word identity is
futile, which would undercut the whole enumerative attack.

Before interpreting it, it is worth knowing what KIND of deficit it is:

  * uniform across sections, or concentrated in a few?
  * drifting through the book, or flat?
  * the 1-rune bucket, the 2-rune bucket, or both?
  * a shift of the whole distribution, or a missing short tail?
  * an artifact of the segmentation convention?

That last one is not idle. The repo has two live conventions. `lp_corpus`
breaks words at `- . % & $`; section D of the boundary file argues the correct
segmentation ends words only at `-` and `.`, since 46 of 57 `%` page breaks
fall mid-word. Treating `%` as a boundary SPLITS a word into two shorter
fragments, which inflates the short-word count — so the convention pushes the
deficit in a known direction and the size matters.

Solved comparison: the first 187 lines of the master transcription (the solved
intro pages) plus sections 10-11 of `page0-58.txt` (the AN END page and the
Parable).
"""

from __future__ import annotations

import re
from collections import Counter
from math import sqrt
from pathlib import Path

from scipy import stats

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
CORPUS = ROOT / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
SOLVED_LINES = 187
SHORT = 2
CONVENTIONS = {
    "- . % & $ (lp_corpus)": c3301.MARK_CHARS + "%&$" + c3301.NUMERAL_CHARS,
    "- . (section D)": c3301.MARK_CHARS,
    # The opposite extreme: every line break a word boundary. This OVER-splits,
    # cutting wrapped words into fragments, so it bounds how much the merging
    # convention can possibly be contributing.
    "+ split at line breaks": c3301.MARK_CHARS + "%&$/\n" + c3301.NUMERAL_CHARS,
}


def words(text: str, boundary: str) -> list[int]:
    out, cur = [], 0
    for ch in text:
        if RUNE.match(ch):
            cur += 1
        elif ch in boundary and cur:
            out.append(cur)
            cur = 0
    if cur:
        out.append(cur)
    return out


def corpora() -> tuple[str, str, list[str]]:
    master = MASTER.read_text().split("\n")
    solved_intro = "\n".join(master[:SOLVED_LINES])
    blocks = CORPUS.read_text().split("$")
    unsolved = "$".join(blocks[:10])
    solved = solved_intro + "\n" + "\n".join(blocks[10:])
    return unsolved, solved, blocks[:10]


def short_rate(lengths: list[int]) -> tuple[float, int, int]:
    n = len(lengths)
    k = sum(1 for v in lengths if v <= SHORT)
    return k / n, k, n


def main() -> None:
    unsolved, solved, sections = corpora()

    print("1. the deficit, under every segmentation convention\n")
    print(f"{'convention':>24}{'unsolved':>22}{'solved':>22}{'z':>8}")
    for name, b in CONVENTIONS.items():
        u, s = words(unsolved, b), words(solved, b)
        ur, uk, un = short_rate(u)
        sr, sk, sn = short_rate(s)
        se = sqrt(ur * (1 - ur) / un + sr * (1 - sr) / sn)
        print(
            f"{name:>24}{f'{ur:.1%} ({uk}/{un})':>22}"
            f"{f'{sr:.1%} ({sk}/{sn})':>22}{(sr - ur) / se:>+8.2f}"
        )

    b = CONVENTIONS["- . % & $ (lp_corpus)"]
    u, s = words(unsolved, b), words(solved, b)

    print("\n2. the whole distribution, not just the short tail\n")
    cu, cs = Counter(u), Counter(s)
    print(f"{'runes':>6}{'unsolved':>12}{'solved':>12}{'difference':>12}")
    for n in range(1, 13):
        pu, ps = cu[n] / len(u), cs[n] / len(s)
        print(f"{n:>6}{pu:>12.1%}{ps:>12.1%}{ps - pu:>+12.1%}")
    print(f"{'mean':>6}{sum(u) / len(u):>12.2f}{sum(s) / len(s):>12.2f}")
    ks = stats.ks_2samp(u, s)
    print(f"   Kolmogorov-Smirnov: D = {ks.statistic:.4f}, p = {ks.pvalue:.2e}")

    print("\n3. is the deficit uniform across sections?\n")
    print(f"{'section':>9}{'words':>8}{'short':>8}{'rate':>9}{'z vs solved':>13}")
    rows = []
    sr, _, sn = short_rate(s)
    for i, block in enumerate(sections):
        lengths = words(block, b)
        if len(lengths) < 30:
            continue
        r, k, n = short_rate(lengths)
        se = sqrt(r * (1 - r) / n + sr * (1 - sr) / sn)
        rows.append((k, n))
        print(f"{i:>9}{n:>8}{k:>8}{r:>9.1%}{(sr - r) / se:>+13.2f}")
    pooled = sum(k for k, _ in rows) / sum(n for _, n in rows)
    chi2 = sum((k - n * pooled) ** 2 / (n * pooled * (1 - pooled)) for k, n in rows)
    df = len(rows) - 1
    print(
        f"\n   homogeneity across sections: chi2 = {chi2:.2f} on {df} df, "
        f"p = {stats.chi2.sf(chi2, df):.3f}"
    )

    print("\n4. does it drift through the book?\n")
    quarters = 4
    per = len(u) // quarters
    for q in range(quarters):
        part = u[q * per : (q + 1) * per] if q < quarters - 1 else u[q * per :]
        r, k, n = short_rate(part)
        print(f"   words {q * per:>5}-{q * per + len(part):<5} {r:>7.1%} ({k}/{n})")
    tau = stats.kendalltau(range(len(u)), [1 if v <= SHORT else 0 for v in u])
    print(
        f"   rank correlation of shortness with position: tau = "
        f"{tau.statistic:+.4f}, p = {tau.pvalue:.3f}"
    )


if __name__ == "__main__":
    main()
