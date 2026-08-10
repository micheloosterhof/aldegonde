#!/usr/bin/env python3
# ABOUTME: Decides the 1st-vs-2nd-rune (keystream direction) question for the
# ABOUTME: EA-marker hypothesis: EA's word-position profile in real runeglish
# ABOUTME: prose vs the word-position splits of the LP doublet runes.
"""EA direction test (doublet-marker-rune-ea.md, Predictions).

IF each ciphertext doublet marks plaintext EA at one of its two positions,
the marked rune's word-position split (initial/medial/final) must match
EA's profile in word-bounded runeglish prose. The ngram tables carry no
word boundaries; this script builds the profile from real prose (Project
Gutenberg #1342, the same text behind the d5 full-leak reference),
token-weighted, encoded with the shared digraph rules.

Compares the profile against BOTH doublet-rune splits from the clean corpus
(sections 0-9, 86 doublets; experiments/doublet_word_position.py):
2nd rune = 23/44/19 start/middle/end, 1st rune = 12/51/23. Whichever side
matches EA's profile is the keystream direction — conditional, as always,
on the unproven marker premise.
"""

from __future__ import annotations

import sys
import tempfile
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from d5_partial_leak import to_runeglish
from doublet_word_position import DATA, RUNES, build_stream, parse_words

PROSE_URL = "https://www.gutenberg.org/files/1342/1342-0.txt"
PROSE_CACHE = Path(tempfile.gettempdir()) / "pg1342.txt"


def prose_words(path: Path) -> list[str]:
    words: list[str] = []
    for raw in path.read_text(encoding="utf-8").split():
        w = "".join(c for c in raw if c.isalpha()).upper()
        if w and w.isascii():
            words.append(w)
    return words


def ea_profile(words: list[str]) -> tuple[Counter[str], int]:
    """Token-weighted word-position counts of EA in runeglish prose."""
    cat: Counter[str] = Counter()
    total = 0
    for w in words:
        runes = to_runeglish(w)
        n = len(runes)
        for j, r in enumerate(runes):
            if r != "EA":
                continue
            total += 1
            if n == 1:
                cat["lone"] += 1
            elif j == 0:
                cat["start"] += 1
            elif j == n - 1:
                cat["end"] += 1
            else:
                cat["middle"] += 1
    return cat, total


def chi2_gof(obs: list[int], frac: list[float]) -> tuple[float, float]:
    """Chi-square goodness of fit of obs counts against fractions."""
    n = sum(obs)
    exp = [n * f for f in frac]
    stat = sum((o - e) ** 2 / e for o, e in zip(obs, exp) if e > 0)
    # df = len(obs) - 1; survival via scipy if present, else Wilson-Hilferty
    try:
        from scipy.stats import chi2 as chi2_dist

        p = float(chi2_dist.sf(stat, len(obs) - 1))
    except ImportError:  # pragma: no cover
        import math

        k = len(obs) - 1
        z = ((stat / k) ** (1 / 3) - (1 - 2 / (9 * k))) / math.sqrt(2 / (9 * k))
        p = 0.5 * math.erfc(z / math.sqrt(2))
    return stat, p


def main() -> None:
    if len(sys.argv) > 1:
        prose_path = Path(sys.argv[1])
    else:
        prose_path = PROSE_CACHE
        if not prose_path.exists():
            print(f"downloading {PROSE_URL} -> {prose_path}")
            urllib.request.urlretrieve(PROSE_URL, prose_path)

    words = prose_words(prose_path)
    cat, total = ea_profile(words)
    runes_total = sum(len(to_runeglish(w)) for w in words)
    print(
        f"prose: {len(words)} word tokens, {runes_total} runes, "
        f"{total} EA tokens ({total / runes_total * 100:.3f}%)"
    )
    keys = ("start", "middle", "end")
    frac = [cat[k] / total for k in keys]
    print(
        "EA profile (token-weighted): "
        + "  ".join(f"{k} {cat[k]} ({cat[k] / total * 100:.1f}%)" for k in keys)
        + f"  lone {cat['lone']}"
    )

    # LP doublet-rune splits, clean corpus
    with open(DATA, encoding="utf-8") as f:
        text = f.read()
    text = "$".join([s for s in text.split("$") if RUNES & set(s)][:10])
    lp_words = parse_words(text)
    stream, word_id, pos1, wlen = build_stream(lp_words)
    doublets = [i for i in range(len(stream) - 1) if stream[i] == stream[i + 1]]

    def label(i: int) -> str:
        if wlen[i] == 1:
            return "lone"
        if pos1[i] == 1:
            return "start"
        if pos1[i] == wlen[i]:
            return "end"
        return "middle"

    baseline = Counter(label(i) for i in range(len(stream)))
    base_frac = [baseline[k] / len(stream) for k in keys]

    print(f"\nLP clean corpus: {len(stream)} runes, {len(doublets)} doublets")
    print(
        f"{'split':>10} {'start':>6} {'middle':>7} {'end':>5} | "
        f"{'chi2 vs EA':>10} {'p':>7} | {'chi2 vs base':>12} {'p':>7}"
    )
    for name, idxs in (("1st rune", doublets), ("2nd rune", [i + 1 for i in doublets])):
        c = Counter(label(i) for i in idxs)
        obs = [c[k] for k in keys]
        s_ea, p_ea = chi2_gof(obs, frac)
        s_b, p_b = chi2_gof(obs, base_frac)
        print(
            f"{name:>10} {obs[0]:>6} {obs[1]:>7} {obs[2]:>5} | "
            f"{s_ea:>10.2f} {p_ea:>7.3f} | {s_b:>12.2f} {p_b:>7.3f}"
        )
    print(
        f"{'all runes':>10} "
        f"{baseline['start']:>6} {baseline['middle']:>7} {baseline['end']:>5}"
        f"   (baseline fractions "
        + "/".join(f"{f * 100:.1f}%" for f in base_frac)
        + ")"
    )
    print(f"{'EA prose':>10} " + " ".join(f"{f * 100:>5.1f}%" for f in frac))


if __name__ == "__main__":
    main()
