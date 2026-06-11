#!/usr/bin/env python3
"""Structural alignment probes for the unsolved LP.

1. Keystream-restart tests: align sections/pages/lines at their starts and
   count coincidences (catches key restart at structural boundaries).
2. Periodicity in word-index and line-index space (key advances per word or
   per line instead of per rune).
3. Long-period column IoC (rune-space periods up to 700).
4. Serial dependence of the delta stream.
5. Stratified d=1 contingency (within-word vs cross-word).
6. Isomorph statistics.
7. Doublet micro-structure: identity of doubled rune, position in line.
8. Line/page checksums mod 29.
"""

import math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2 as chi2_dist
from scipy.stats import chi2_contingency

from anomaly_scan import parse, ioc

N = 29


def coincidence_z(pairs):
    hits = sum(1 for x, y in pairs)
    return hits


def align_test(units, label, max_units=None):
    """Count coincidences between every pair of units aligned at start."""
    units = [u for u in units if len(u) >= 5]
    if max_units:
        units = units[:max_units]
    hits = opp = 0
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            a, b = units[i], units[j]
            L = min(len(a), len(b))
            opp += L
            hits += sum(1 for k in range(L) if a[k] == b[k])
    if opp == 0:
        return
    exp = opp / N
    sd = math.sqrt(opp * (1 / N) * (1 - 1 / N))
    z = (hits - exp) / sd
    flag = " ***" if abs(z) > 4 else (" *" if abs(z) > 3 else "")
    print(f"  {label}: pairs-opportunities={opp} hits={hits} exp={exp:.1f} "
          f"z={z:+.2f}{flag}")
    # also right-aligned
    hits = opp = 0
    for i in range(len(units)):
        for j in range(i + 1, len(units)):
            a, b = units[i], units[j]
            L = min(len(a), len(b))
            opp += L
            hits += sum(1 for k in range(1, L + 1) if a[-k] == b[-k])
    exp = opp / N
    sd = math.sqrt(opp * (1 / N) * (1 - 1 / N))
    z = (hits - exp) / sd
    flag = " ***" if abs(z) > 4 else (" *" if abs(z) > 3 else "")
    print(f"  {label} (right-aligned): hits={hits} exp={exp:.1f} z={z:+.2f}{flag}")


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = stream[:-nplain]
    # rebuild structures without the parable
    sections = sections[:-1]
    # words/lines/pages of parable are at the end
    parable_words = 0
    acc = 0
    for w in reversed(words):
        acc += len(w)
        parable_words += 1
        if acc >= nplain:
            break
    words = words[:-parable_words]
    # crude trim for lines/pages: drop trailing units summing to ~nplain
    def trim(units):
        acc = 0
        k = 0
        for u in reversed(units):
            acc += len(u)
            k += 1
            if acc >= nplain:
                break
        return units[:-k]
    lines = trim(lines)
    pages = trim(pages)
    n = len(cipher)
    print(f"cipher: {n} runes, {len(words)} words, {len(lines)} lines, "
          f"{len(pages)} pages, {len(sections)} sections")

    print("\n=== 1. KEYSTREAM-RESTART ALIGNMENT ===")
    align_test(sections, "sections aligned at start")
    align_test(pages, "pages aligned at start")
    align_test(lines, "lines aligned at start")
    # words aligned at start, same length only (already done) and all:
    align_test([w for w in words], "words aligned at start")

    print("\n=== 2. PERIODICITY IN WORD/LINE INDEX SPACE ===")
    # assign each rune its word index; column = word index mod k; IoC per column
    rune_word = []
    for wi, w in enumerate(words):
        rune_word.extend([wi] * len(w))
    rune_word = np.array(rune_word)
    arr = np.array(cipher[: len(rune_word)])
    print("  word-index periods (mean column nIoC, exp 1.0):")
    best = []
    for k in range(2, 41):
        cols = [arr[rune_word % k == c] for c in range(k)]
        m = float(np.mean([ioc(list(col)) * N for col in cols if len(col) > 30]))
        best.append((abs(m - 1), k, m))
    best.sort(reverse=True)
    for _, k, m in best[:5]:
        print(f"    k={k}: mean nIoC={m:.4f}")
    rune_line = []
    for li, l in enumerate(lines):
        rune_line.extend([li] * len(l))
    rune_line = np.array(rune_line)
    arr2 = np.array(cipher[: len(rune_line)])
    print("  line-index periods:")
    best = []
    for k in range(2, 31):
        cols = [arr2[rune_line % k == c] for c in range(k)]
        m = float(np.mean([ioc(list(col)) * N for col in cols if len(col) > 30]))
        best.append((abs(m - 1), k, m))
    best.sort(reverse=True)
    for _, k, m in best[:5]:
        print(f"    k={k}: mean nIoC={m:.4f}")

    print("\n=== 3. LONG-PERIOD COLUMN IOC (rune space) ===")
    arr = np.array(cipher)
    best = []
    for k in range(2, 701):
        cols = [arr[i::k] for i in range(k)]
        m = float(np.mean([ioc(list(col)) * N for col in cols]))
        # z-score: each column IoC has variance; approximate by simulation-free
        best.append((m, k))
    best.sort(reverse=True)
    print("  top 8 periods by mean column nIoC:")
    for m, k in best[:8]:
        ncol = n / k
        print(f"    k={k}: mean nIoC={m:.4f} (col len ~{ncol:.0f})")
    print(f"  bottom 3: {[(k, round(m,4)) for m, k in best[-3:]]}")

    print("\n=== 4. DELTA STREAM SERIAL DEPENDENCE ===")
    d = [(cipher[i + 1] - cipher[i]) % N for i in range(n - 1)]
    a = d[:-1]
    b = d[1:]
    joint = np.zeros((N, N))
    np.add.at(joint, (a, b), 1)
    stat, p, dof, _ = chi2_contingency(joint + 1e-9)
    print(f"  delta[i] vs delta[i+1] contingency: chi2={stat:.1f} dof={dof} p={p:.4f}")
    # excluding rows/cols 0 (doublet-driven)
    sub = joint[1:, 1:]
    stat, p, dof, _ = chi2_contingency(sub + 1e-9)
    print(f"  excluding delta=0: chi2={stat:.1f} dof={dof} p={p:.4f}")

    print("\n=== 5. STRATIFIED d=1 CONTINGENCY ===")
    within = [(cipher[i], cipher[i + 1]) for i in range(n - 1) if seps[i] == ""]
    cross = [(cipher[i], cipher[i + 1]) for i in range(n - 1) if seps[i] in ("w", "l")]
    for pairs, label in ((within, "within-word"), (cross, "cross-word")):
        joint = np.zeros((N, N))
        for x, y in pairs:
            joint[x, y] += 1
        stat, p, dof, _ = chi2_contingency(joint + 1e-9)
        print(f"  {label} ({len(pairs)} pairs): chi2={stat:.1f} p={p:.4f}")
        # off-diagonal only
        mask = ~np.eye(N, dtype=bool)
        od = joint.copy()
        np.fill_diagonal(od, 0)
        row = od.sum(axis=1)
        col = od.sum(axis=0)
        tot = od.sum()
        exp = np.outer(row, col) / tot
        statod = float(np.nansum(np.where(mask, (od - exp) ** 2 / np.where(exp > 0, exp, 1), 0)))
        print(f"    off-diagonal quasi-chi2={statod:.1f} (dof~{28*28-1})")

    print("\n=== 6. ISOMORPHS ===")
    # NOTE: this baseline is uniform random text; see isomorph_corrected.py
    # for the doublet-corrected null, which removes the apparent anomaly.
    from aldegonde.stats.isomorph import print_isomorph_statistics
    print_isomorph_statistics(cipher)

    print("\n=== 7. DOUBLET MICRO-STRUCTURE ===")
    dpos = [i for i in range(n - 1) if cipher[i] == cipher[i + 1]]
    ident = Counter(cipher[i] for i in dpos)
    counts = [ident[i] for i in range(N)]
    exp = len(dpos) / N
    stat = sum((c - exp) ** 2 / exp for c in counts)
    p = chi2_dist.sf(stat, N - 1)
    print(f"  doubled-rune identity: chi2={stat:.1f} p={p:.4f}")
    print(f"  counts: {counts}")
    # position within line
    pos_in_line = {}
    k = 0
    for li, l in enumerate(lines):
        for j in range(len(l)):
            pos_in_line[k] = (j, len(l))
            k += 1
    rel = [pos_in_line[i][0] / max(pos_in_line[i][1] - 1, 1) for i in dpos if i in pos_in_line]
    print(f"  doublet relative position in line: mean={np.mean(rel):.3f} (exp 0.5), n={len(rel)}")

    print("\n=== 8. LINE/PAGE CHECKSUMS MOD 29 ===")
    lsums = [sum(l) % N for l in lines]
    c = np.bincount(lsums, minlength=N)
    m = len(lsums)
    stat = ((c - m / N) ** 2 / (m / N)).sum()
    print(f"  line sums mod 29: chi2={stat:.1f} p={chi2_dist.sf(stat, N-1):.4f}")
    psums = [sum(p_) % N for p_ in pages]
    c = np.bincount(psums, minlength=N)
    m = len(psums)
    stat = ((c - m / N) ** 2 / (m / N)).sum()
    print(f"  page sums mod 29: chi2={stat:.1f} p={chi2_dist.sf(stat, N-1):.4f} "
          f"(n={m}, low power)")
    print(f"  page sums: {sorted(psums)}")


if __name__ == "__main__":
    main()
