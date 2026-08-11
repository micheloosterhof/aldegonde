# ABOUTME: Discriminates the hold model from a key-event trigger via the
# ABOUTME: position-in-word profile of doublets: exposed plaintext doubles must
# ABOUTME: follow the plaintext double-letter profile; a key event is baseline-flat.
"""Doublet position profile: plaintext doubles vs ciphertext doublets.

Under the stay-slot hold (`stay-slot-hold.md`, `length-clocked-walk.md`)
a within-word ciphertext doublet IS a plaintext double letter exposed by
the hold (uniform 1-in-5 thinning — the corpus shows no positional mod-5
frame, consistent with per-word phase drift). Thinning preserves the
position profile, so the doublets' position-in-word distribution must
match the plaintext double-letter profile — in English strongly END-heavy
and START-poor (ALL, SEE, WILL; almost nothing opens with a double).
A trigger uncorrelated with plaintext content (rare KEY event) predicts
the flat adjacency baseline instead.

Plaintext registers: the recovered solved-section plaintext (same author,
word boundaries preserved through the per-segment decryptions) and
runeglish-encoded English prose (Gutenberg #1342, token-weighted).
Prediction for the 63 LP within-word doublets: per-category plaintext
doublet RATES applied to LP's per-category adjacency OPPORTUNITIES,
compared against the observed counts by G-test; same for the flat model.
"""

from __future__ import annotations

import math
import sys
import urllib.request
from collections import Counter
from pathlib import Path

from aldegonde import c3301

BOUNDARY_CHARS = frozenset(
    c3301.MARK_CHARS + "%" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS
)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish  # noqa: E402, I001
from ea_direction_test import PROSE_CACHE, PROSE_URL, prose_words  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from solved_plaintext_running_key import (  # noqa: E402
    RUNES,
    R2I,
    SOLVED_RUNES,  # noqa: E402
    beam_vigenere,
)

M = 29
CATS = ("start", "middle", "end", "whole-word")


def pair_cat(p0: int, length: int) -> str:
    """Category of the adjacency (p0, p0+1), 0-based, within a word."""
    if length == 2:
        return "whole-word"
    if p0 == 0:
        return "start"
    if p0 + 2 == length:
        return "end"
    return "middle"


def profile(words: list[list[int]]) -> tuple[Counter, Counter]:
    """(doublet counts, adjacency opportunities) per category."""
    dbl: Counter = Counter()
    opp: Counter = Counter()
    for w in words:
        L = len(w)
        for p in range(L - 1):
            c = pair_cat(p, L)
            opp[c] += 1
            if w[p] == w[p + 1]:
                dbl[c] += 1
    return dbl, opp


def solved_plain_words() -> list[list[int]]:
    """Solved-region plaintext as words: decrypt each segment, re-split on
    the transcription's word boundaries."""
    text = (ROOT / "data/liber-primus__transcription--master.txt").read_text()
    segs: list[list[int]] = [[]]  # rune indices per segment
    wlens: list[list[int]] = [[]]  # word lengths per segment
    cur = 0
    count = 0
    for ch in text:
        if count >= SOLVED_RUNES:
            break
        if ch in RUNES:
            segs[-1].append(R2I[ch])
            cur += 1
            count += 1
        elif ch in BOUNDARY_CHARS:
            if cur:
                wlens[-1].append(cur)
                cur = 0
        elif ch in "&$":
            if cur:
                wlens[-1].append(cur)
                cur = 0
            if segs[-1]:
                segs.append([])
                wlens.append([])
    if cur:
        wlens[-1].append(cur)
    segs = [s for s in segs if s]
    wlens = [w for w in wlens if w]

    def decrypt(k: int, ct: list[int]) -> list[int]:
        if k == 0:
            return [(28 - c) % M for c in ct]
        if k in (5, 6):
            return [(28 * c + 2) % M for c in ct]
        if k == 10:
            return beam_vigenere(ct, "FIRFUMFERENFE")[0]
        return ct  # identity segments

    # segments 1+2 share one Vigenere key stream
    pt12 = beam_vigenere(segs[1] + segs[2], "DIUINITY")[0]
    plains = {1: pt12[: len(segs[1])], 2: pt12[len(segs[1]) :]}
    words: list[list[int]] = []
    for k, (ct, wl) in enumerate(zip(segs, wlens)):
        pt = plains.get(k) or decrypt(k, ct)
        pos = 0
        for L in wl:
            words.append(pt[pos : pos + L])
            pos += L
        assert pos == len(pt), (k, pos, len(pt))
    return words


def g_test(obs: Counter, pred: dict[str, float]) -> tuple[float, float]:
    n = sum(obs[c] for c in CATS)
    tot = sum(pred[c] for c in CATS)
    exp = {c: n * pred[c] / tot for c in CATS}
    if any(obs[c] > 0 and exp[c] == 0 for c in CATS):
        return math.inf, 0.0  # events observed in a zero-probability cell
    g = 2 * sum(obs[c] * math.log(obs[c] / exp[c]) for c in CATS if obs[c] > 0)
    try:
        from scipy.stats import chi2

        p = float(chi2.sf(g, len([c for c in CATS if exp[c] > 0]) - 1))
    except ImportError:  # pragma: no cover
        p = float("nan")
    return g, p


def show(name: str, dbl: Counter, opp: Counter) -> dict[str, float]:
    tot_d, tot_o = sum(dbl.values()), sum(opp.values())
    rates = {}
    print(
        f"\n{name}: {tot_d} doublets / {tot_o} adjacencies ({tot_d / tot_o * 100:.2f}%)"
    )
    print(
        f"{'category':>12} {'dbl':>5} {'opp':>7} {'rate%':>7} {'share%':>7} "
        f"{'opp-share%':>10}"
    )
    for c in CATS:
        rates[c] = dbl[c] / opp[c] if opp[c] else 0.0
        print(
            f"{c:>12} {dbl[c]:>5} {opp[c]:>7} {rates[c] * 100:>7.2f} "
            f"{(dbl[c] / tot_d * 100 if tot_d else 0):>7.1f} "
            f"{opp[c] / tot_o * 100:>10.1f}"
        )
    return rates


def main() -> None:
    # LP ciphertext side
    stream, wid = load_clean()
    lp_words: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        lp_words.setdefault(w, []).append(stream[i])
    lp_dbl, lp_opp = profile(list(lp_words.values()))
    show("LP ciphertext (clean corpus)", lp_dbl, lp_opp)

    # plaintext registers
    solved = solved_plain_words()
    r_solved = show("solved-pages plaintext", *profile(solved))

    prose_path = PROSE_CACHE
    if len(sys.argv) > 1:
        prose_path = Path(sys.argv[1])
    elif not prose_path.exists():
        print(f"downloading {PROSE_URL} -> {prose_path}")
        urllib.request.urlretrieve(PROSE_URL, prose_path)
    prose = [[IDX_ENG[t] for t in to_runeglish(w)] for w in prose_words(prose_path)]
    prose = [w for w in prose if w]
    r_prose = show("prose runeglish (Gutenberg 1342)", *profile(prose))

    # predictions for the LP doublets
    print("\npredictions for the LP within-word doublets:")
    flat = {c: float(lp_opp[c]) for c in CATS}
    for name, rates in (
        ("hold model (solved rates)", r_solved),
        ("hold model (prose rates)", r_prose),
        ("key event (flat baseline)", dict.fromkeys(CATS, 1.0)),
    ):
        pred = {c: lp_opp[c] * rates[c] for c in CATS} if "hold" in name else flat
        n = sum(lp_dbl[c] for c in CATS)
        tot = sum(pred.values())
        exp = {c: n * pred[c] / tot for c in CATS}
        g, p = g_test(lp_dbl, pred)
        cells = "  ".join(f"{c} {exp[c]:.1f}" for c in CATS)
        print(f"  {name:<26} G={g:6.2f} p={p:.4f}   expected: {cells}")


# rune-name -> index for the prose encoder output; IO is the IA rune
from aldegonde import c3301  # noqa: E402

BOUNDARY_CHARS = frozenset(
    c3301.MARK_CHARS + "%" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS
)

IDX_ENG = {name: i for i, name in enumerate(c3301.CICADA_ENGLISH_ALPHABET)}
IDX_ENG["IO"] = IDX_ENG["IA"]


if __name__ == "__main__":
    main()
