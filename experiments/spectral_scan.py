#!/usr/bin/env python3
"""Spectral and residual probes for the unsolved LP.

1. DFT scan: for each multiplier m, FFT of exp(2*pi*i*m*C[k]/29).
   Detects additive periodic structure at ANY real frequency.
2. Quadratic position functionals: (C[i] - a*i^2 - b*i) mod 29 uniformity.
3. Vertical (grid) adjacency on pages: doublets and contingency.
4. Line-alignment coincidence profile by column.
5. Control: line-initial rune distribution in SOLVED sections of master.
6. Isomorph statistics.
7. Compressibility vs random baseline.
"""

import math
import zlib
from collections import Counter

import numpy as np
from scipy.stats import chi2 as chi2_dist

from anomaly_scan import parse
from aldegonde import c3301

N = 29
ALPH = c3301.CICADA_ALPHABET


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = np.array(stream[:-nplain])
    n = len(cipher)
    print(f"cipher: {n} runes")

    print("\n=== 1. DFT SCAN (28 multipliers x all frequencies) ===")
    peaks = []
    for m in range(1, N):
        x = np.exp(2j * np.pi * m * cipher / N)
        X = np.fft.fft(x)
        power = np.abs(X[1 : n // 2]) ** 2 / n  # exclude DC
        # under null, power ~ Exp(1) per bin
        top = np.argsort(power)[-3:]
        for t in top:
            peaks.append((power[t], m, t + 1))
    peaks.sort(reverse=True)
    nbins = 28 * (n // 2 - 1)
    thresh = math.log(nbins) + 3  # ~p=0.05 for max of nbins exponentials
    print(f"  bins tested: {nbins}, significance threshold ~{thresh:.1f}")
    for power, m, f in peaks[:10]:
        period = n / f
        print(f"  power={power:.1f} multiplier={m} freq-bin={f} (period {period:.2f})")

    print("\n=== 2. QUADRATIC POSITION FUNCTIONALS ===")
    idx = np.arange(n)
    i2 = (idx * idx) % N
    hits = []
    for a in range(N):
        for b in range(N):
            if a == 0 and b == 0:
                continue
            f = (cipher - a * i2 - b * idx) % N
            counts = np.bincount(f, minlength=N)
            stat = ((counts - n / N) ** 2 / (n / N)).sum()
            p = chi2_dist.sf(stat, N - 1)
            if p < 1e-5:
                hits.append((p, a, b))
    print(f"  significant (p<1e-5 of 840 tests): {hits if hits else 'none'}")

    print("\n=== 3. VERTICAL GRID ADJACENCY ===")
    # rebuild lines per page (without parable)
    # parse() gives flat lines; we need page->lines. reparse simply:
    data = open("data/page0-58.txt").read().replace("\n", "")
    pages_lines = []
    cur_page = []
    cur_line = []
    for ch in data:
        if ch in ALPH:
            cur_line.append(c3301.r2i(ch))
        elif ch == "/":
            cur_page.append(cur_line)
            cur_line = []
        elif ch in "%&$":
            if cur_line:
                cur_page.append(cur_line)
                cur_line = []
            if cur_page:
                pages_lines.append(cur_page)
                cur_page = []
    if cur_line:
        cur_page.append(cur_line)
    if cur_page:
        pages_lines.append(cur_page)
    pages_lines = pages_lines[:-1]  # drop parable page
    vhits = vopp = 0
    joint = np.zeros((N, N))
    for pl in pages_lines:
        for l1, l2 in zip(pl, pl[1:]):
            L = min(len(l1), len(l2))
            for c in range(L):
                vopp += 1
                vhits += l1[c] == l2[c]
                joint[l1[c], l2[c]] += 1
    exp = vopp / N
    sd = math.sqrt(vopp * (1 / N) * (1 - 1 / N))
    print(f"  vertical doublets: obs={vhits} exp={exp:.1f} z={(vhits-exp)/sd:+.2f}")
    from scipy.stats import chi2_contingency
    stat, p, dof, _ = chi2_contingency(joint + 1e-9)
    print(f"  vertical contingency: chi2={stat:.1f} dof={dof} p={p:.4f}")

    print("\n=== 4. LINE-ALIGNMENT COINCIDENCE PROFILE ===")
    lns = [l for l in lines if len(l) >= 5]
    # exclude parable lines (last ~5)
    for col in range(10):
        vals = [l[col] for l in lns if len(l) > col]
        c = Counter(vals)
        m = len(vals)
        pairs = m * (m - 1) / 2
        hits = sum(v * (v - 1) // 2 for v in c.values())
        exp = pairs / N
        sd = math.sqrt(pairs * (1 / N))
        print(f"  col {col}: n={m} coincident-pairs={hits} exp={exp:.0f} "
              f"z={(hits-exp)/sd:+.2f}")

    print("\n=== 5. CONTROL: SOLVED SECTIONS LINE-INITIAL BIAS ===")
    # The solved pages are the FIRST 2797 runes of the master transcription;
    # page0-58.txt is the remaining 13,136 runes (verified by substring
    # match: page0-58 starts at rune offset 2797 of the master).
    master = open("data/liber-primus__transcription--master.txt").read()
    count = 0
    cut = None
    for i, ch in enumerate(master):
        if ch in "".join(ALPH):
            count += 1
            if count == 2797:
                cut = i + 1
                break
    solved = master[:cut]
    sol_lines = []
    cur = []
    for ch in solved:
        if ch in "".join(ALPH):
            cur.append(c3301.r2i(ch))
        elif ch == "/":
            if cur:
                sol_lines.append(cur)
            cur = []
    if cur:
        sol_lines.append(cur)
    li = Counter(l[0] for l in sol_lines if l)
    m = sum(li.values())
    counts = np.array([li[i] for i in range(N)])
    stat = ((counts - m / N) ** 2 / (m / N)).sum()
    print(f"  solved-section lines: {m}, line-initial chi2={stat:.1f} "
          f"p={chi2_dist.sf(stat, N-1):.5f}")
    print(f"  counts: {counts.tolist()}")

    print("\n=== 6. ISOMORPHS ===")
    from aldegonde.stats.isomorph import print_isomorph_statistics
    print_isomorph_statistics(list(cipher))

    print("\n=== 7. COMPRESSIBILITY ===")
    raw = bytes(int(x) for x in cipher)
    comp = len(zlib.compress(raw, 9))
    rng = np.random.default_rng(0)
    rand_sizes = []
    for _ in range(20):
        r = bytes(rng.integers(0, N, n).astype(np.uint8).tolist())
        rand_sizes.append(len(zlib.compress(r, 9)))
    print(f"  cipher zlib: {comp}, random mean: {np.mean(rand_sizes):.0f} "
          f"sd {np.std(rand_sizes):.1f} z={(comp-np.mean(rand_sizes))/np.std(rand_sizes):+.2f}")


if __name__ == "__main__":
    main()
