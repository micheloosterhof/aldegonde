#!/usr/bin/env python3
# ABOUTME: Tests whether LP doublets cluster by position (word-phase, absolute,
# ABOUTME: word index, distance-from-end) -- locating the stay-slot hold, if fixed.
"""In the stay-slot model a within-word doublet can only appear on a HOLD step
(the alphabet is frozen, so a plaintext doublet shows through). So the placement
of the actual doublets is the placement of the holds:

  * doublets clustered at one position-in-word mod 5  -> FIXED hold slot
  * doublets flat over position                       -> keyed hold, or order-5-g

We compute the doublet RATE (doublets / eligible adjacent pairs) in each bin so
exposure is accounted for, and chi-square each axis for uniformity. Clean corpus,
sections 0-9 of data/page0-58.txt.
"""

from __future__ import annotations

from collections import defaultdict

from experiments.within_word_position_decomposition import load_words


def chi2_uniform_rate(bins: dict[object, tuple[int, int]]) -> tuple[float, int, float]:
    """bins: label -> (eligible, doublets). Chi-square that the rate is uniform
    across bins given exposure. Returns (chi2, dof, p_approx)."""
    from scipy.stats import chi2 as chi2dist

    tot_n = sum(n for n, _ in bins.values())
    tot_k = sum(k for _, k in bins.values())
    if tot_n == 0 or tot_k == 0:
        return 0.0, 0, 1.0
    p = tot_k / tot_n
    chi = 0.0
    for n, k in bins.values():
        e = p * n
        if e > 0:
            chi += (k - e) ** 2 / e
    dof = max(1, len(bins) - 1)
    return chi, dof, float(chi2dist.sf(chi, dof))


def report(title: str, bins: dict[object, tuple[int, int]], order=None) -> None:
    keys = order if order is not None else sorted(bins)
    chi, dof, pv = chi2_uniform_rate(bins)
    verdict = "FLAT" if pv > 0.05 else "CLUSTERED"
    print(f"\n{title}   chi2={chi:.2f} dof={dof} p={pv:.3f} [{verdict}]")
    print(f"  {'bin':<10} {'elig':>6} {'dbl':>4} {'rate':>8}")
    for k in keys:
        if k not in bins:
            continue
        n, d = bins[k]
        rate = d / n if n else 0.0
        bar = "#" * round(rate / 0.002)
        print(f"  {str(k):<10} {n:>6} {d:>4} {rate:>8.4f}  {bar}")


def main() -> None:
    words = load_words()
    nwords = len(words)

    # within-word adjacent pairs, tagged with every placement axis
    wordphase: dict[int, list[int]] = defaultdict(lambda: [0, 0])   # j%5 (0-idx)
    fromend: dict[int, list[int]] = defaultdict(lambda: [0, 0])     # (L-1-j)%5
    absphase: dict[int, list[int]] = defaultdict(lambda: [0, 0])    # abs pos %5
    widxphase: dict[int, list[int]] = defaultdict(lambda: [0, 0])   # word index %5
    bylen: dict[int, list[int]] = defaultdict(lambda: [0, 0])       # word length
    region: dict[str, list[int]] = defaultdict(lambda: [0, 0])      # text thirds
    seam: list[int] = [0, 0]

    abs_pos = 0
    ntotal = sum(len(w) for w in words)
    for wi, w in enumerate(words):
        L = len(w)
        for j in range(L):
            if j >= 1:
                is_d = int(w[j] == w[j - 1])
                for tbl, key in (
                    (wordphase, j % 5),
                    (fromend, (L - 1 - j) % 5),
                    (absphase, (abs_pos + j) % 5),
                    (widxphase, wi % 5),
                    (bylen, L),
                ):
                    tbl[key][0] += 1
                    tbl[key][1] += is_d
                reg = ("early" if abs_pos + j < ntotal / 3 else
                       "mid" if abs_pos + j < 2 * ntotal / 3 else "late")
                region[reg][0] += 1
                region[reg][1] += is_d
        # seam pair: last rune of this word vs first of next
        if wi + 1 < nwords and w:
            nxt = words[wi + 1]
            if nxt:
                seam[0] += 1
                seam[1] += w[-1] == nxt[0]
        abs_pos += L

    print(f"words {nwords}, runes {ntotal}")
    tk = sum(t[1] for t in wordphase.values())
    tn = sum(t[0] for t in wordphase.values())
    print(f"within-word doublets {tk}/{tn} = {tk/tn:.4f}; "
          f"seam {seam[1]}/{seam[0]} = {seam[1]/seam[0]:.4f}")

    report("position-in-word mod 5 (0-indexed j) -- the hold slot if fixed",
           {k: tuple(v) for k, v in wordphase.items()}, order=range(5))
    report("distance-from-word-end mod 5 -- hold if end-anchored",
           {k: tuple(v) for k, v in fromend.items()}, order=range(5))
    report("absolute text position mod 5",
           {k: tuple(v) for k, v in absphase.items()}, order=range(5))
    report("word index mod 5",
           {k: tuple(v) for k, v in widxphase.items()}, order=range(5))
    report("text region (thirds)",
           {k: tuple(v) for k, v in region.items()}, order=["early", "mid", "late"])
    report("word length",
           {k: tuple(v) for k, v in bylen.items()},
           order=sorted(bylen))


if __name__ == "__main__":
    main()
