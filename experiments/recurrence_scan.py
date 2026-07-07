#!/usr/bin/env python3
"""Recurrence-relation and remaining structural probes.

O. Linear recurrence scan: uniformity of a*C[i] + b*C[i+d1] + c*C[i+d2]
   mod 29 for all coefficient triples and small lag pairs, plus 4-term
   +-1 tap combinations. Catches additive recurrent keystreams
   (lagged Fibonacci, LFSR taps) that defeat all pairwise tests.
P. Sentence-restart alignment (sentences aligned at start/end).
Q. Same-length word-pair coincidence rates (key depending on word length).
R. Page-grid (2D) alignment between consecutive pages; diagonal adjacency;
   boustrophedon adjacency.
S. Doublet pair-distance spectrum.
T. Word (first,last) rune joint; word-initial digraphs vs mid-word
   digraphs (two-sample).
"""

import math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2 as chi2_dist
from scipy.stats import chi2_contingency

from anomaly_scan import parse
from aldegonde import c3301

N = 29
RUNESET = set("".join(c3301.CICADA_ALPHABET))


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = np.array(stream[:-nplain], dtype=np.int64)
    n = len(cipher)
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= n:
            cw.append(w)
        total += len(w)

    print("=== O. LINEAR RECURRENCE SCAN ===")
    lag_pairs = [(1, 2), (1, 3), (2, 3), (1, 4), (2, 4), (3, 4),
                 (1, 5), (2, 5), (5, 10), (7, 11)]
    worst = []
    ntests = 0
    for d1, d2 in lag_pairs:
        x = cipher[: n - d2]
        y = cipher[d1 : n - d2 + d1]
        z = cipher[d2:]
        m = len(x)
        for a in range(1, N):
            ya = (x + a * y) % N
            for b in range(1, N):
                f = (ya + b * z) % N
                counts = np.bincount(f, minlength=N)
                stat = ((counts - m / N) ** 2 / (m / N)).sum()
                ntests += 1
                worst.append((stat, d1, d2, a, b))
        worst.sort(reverse=True)
        worst = worst[:5]
    thresh = chi2_dist.isf(0.01 / ntests, N - 1)
    print(f"  3-term: {ntests} tests, Bonferroni chi2 threshold {thresh:.1f}")
    for stat, d1, d2, a, b in worst:
        p = chi2_dist.sf(stat, N - 1)
        print(f"    lags ({d1},{d2}) coeffs (1,{a},{b}): chi2={stat:.1f} "
              f"raw p={p:.2e}{' ***' if stat > thresh else ''}")
    # 4-term +-1 taps
    worst4 = []
    ntests4 = 0
    for a_ in range(1, 11):
        for b_ in range(a_ + 1, 12):
            for c_ in range(b_ + 1, 13):
                base = cipher[: n - c_]
                xa = cipher[a_ : n - c_ + a_]
                xb = cipher[b_ : n - c_ + b_]
                xc = cipher[c_:]
                m = len(base)
                for s1 in (1, N - 1):
                    for s2 in (1, N - 1):
                        for s3 in (1, N - 1):
                            f = (base + s1 * xa + s2 * xb + s3 * xc) % N
                            counts = np.bincount(f, minlength=N)
                            stat = ((counts - m / N) ** 2 / (m / N)).sum()
                            ntests4 += 1
                            worst4.append((stat, a_, b_, c_, s1, s2, s3))
                worst4.sort(reverse=True)
                worst4 = worst4[:3]
    thresh4 = chi2_dist.isf(0.01 / ntests4, N - 1)
    print(f"  4-term +-1 taps: {ntests4} tests, threshold {thresh4:.1f}")
    for stat, a_, b_, c_, s1, s2, s3 in worst4:
        print(f"    taps (0,{a_},{b_},{c_}) signs (+,{'+' if s1==1 else '-'},"
              f"{'+' if s2==1 else '-'},{'+' if s3==1 else '-'}): chi2={stat:.1f}"
              f"{' ***' if stat > thresh4 else ''}")

    print("\n=== P. SENTENCE-RESTART ALIGNMENT ===")
    # split cipher into sentences using seps
    sentences = []
    cur = [int(cipher[0])]
    for i in range(n - 1):
        if seps[i] == "s":
            sentences.append(cur)
            cur = []
        cur.append(int(cipher[i + 1]))
    sentences.append(cur)
    sentences = [s_ for s_ in sentences if len(s_) >= 10]
    hits = opp = 0
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            a, b = sentences[i], sentences[j]
            L = min(len(a), len(b), 40)
            opp += L
            hits += sum(1 for k in range(L) if a[k] == b[k])
    exp = opp / N
    sd = math.sqrt(opp * (1 / N) * (1 - 1 / N))
    print(f"  {len(sentences)} sentences, start-aligned: hits={hits} "
          f"exp={exp:.1f} z={(hits - exp) / sd:+.2f}")
    hits = opp = 0
    for i in range(len(sentences)):
        for j in range(i + 1, len(sentences)):
            a, b = sentences[i], sentences[j]
            L = min(len(a), len(b), 40)
            opp += L
            hits += sum(1 for k in range(1, L + 1) if a[-k] == b[-k])
    print(f"  end-aligned: hits={hits} exp={exp:.1f} z={(hits - exp) / sd:+.2f}")

    print("\n=== Q. SAME-LENGTH WORD-PAIR COINCIDENCES ===")
    bylen = defaultdict(list)
    for w in cw:
        bylen[len(w)].append(w)
    for L in sorted(bylen):
        ws = bylen[L]
        if len(ws) < 30 or L < 2:
            continue
        arr = np.array(ws)
        hits = 0
        opp = 0
        # all pairs, vectorized per position
        for pos in range(L):
            col = arr[:, pos]
            c = np.bincount(col, minlength=N)
            hits += int((c * (c - 1) // 2).sum())
            opp += len(ws) * (len(ws) - 1) // 2
        exp = opp / N
        sd = math.sqrt(opp * (1 / N) * (1 - 1 / N))
        z = (hits - exp) / sd
        print(f"  len {L}: {len(ws)} words, positional coincident pairs "
              f"{hits} exp {exp:.0f} z={z:+.2f}")

    print("\n=== R. PAGE-GRID 2D ALIGNMENT ===")
    data = open("data/page0-58.txt").read().replace("\n", "")
    pages_lines = []
    cur_page = []
    cur_line = []
    for ch in data:
        if ch in RUNESET:
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
    pages_lines = pages_lines[:-1]
    hits = opp = 0
    for p1, p2 in zip(pages_lines, pages_lines[1:]):
        for l1, l2 in zip(p1, p2):
            L = min(len(l1), len(l2))
            opp += L
            hits += sum(1 for k in range(L) if l1[k] == l2[k])
    exp = opp / N
    sd = math.sqrt(opp * (1 / N) * (1 - 1 / N))
    print(f"  consecutive pages, same (line,col): hits={hits} exp={exp:.1f} "
          f"z={(hits - exp) / sd:+.2f}")
    # diagonal adjacency within pages
    for dc, name in ((-1, "down-left"), (1, "down-right")):
        hits = opp = 0
        for pl in pages_lines:
            for l1, l2 in zip(pl, pl[1:]):
                for k in range(len(l1)):
                    if 0 <= k + dc < len(l2):
                        opp += 1
                        hits += l1[k] == l2[k + dc]
        exp = opp / N
        sd = math.sqrt(opp * (1 / N) * (1 - 1 / N))
        print(f"  diagonal {name}: hits={hits} exp={exp:.1f} z={(hits - exp) / sd:+.2f}")
    # boustrophedon adjacency: line end <-> next line end
    hits = opp = 0
    deltas = Counter()
    for pl in pages_lines:
        for l1, l2 in zip(pl, pl[1:]):
            if l1 and l2:
                opp += 1
                hits += l1[-1] == l2[-1]
                deltas[(l2[-1] - l1[-1]) % N] += 1
    exp = opp / N
    sd = math.sqrt(opp * (1 / N) * (1 - 1 / N))
    print(f"  boustrophedon (line-end to line-end): hits={hits} exp={exp:.1f} "
          f"z={(hits - exp) / sd:+.2f}")

    print("\n=== S. DOUBLET PAIR-DISTANCE SPECTRUM ===")
    dpos = np.array([i for i in range(n - 1) if cipher[i] == cipher[i + 1]])
    dists = Counter()
    for i in range(len(dpos)):
        for j in range(i + 1, len(dpos)):
            dists[int(dpos[j] - dpos[i])] += 1
    mx = max(dists.values())
    npairs = len(dpos) * (len(dpos) - 1) // 2
    lam = npairs / (n - 1)
    # P(max multiplicity >= mx) via Poisson tail x n
    from scipy.stats import poisson
    pmax = 1 - poisson.cdf(mx - 1, lam) ** (n - 1)
    print(f"  doublet pairs: {npairs}, max same-distance multiplicity {mx} "
          f"(lambda={lam:.3f}, P(max>=obs)~{pmax:.3f})")
    top = sorted(dists.items(), key=lambda x: -x[1])[:5]
    print(f"  top distances: {top}")

    print("\n=== T. WORD JOINT DISTRIBUTIONS ===")
    J = np.zeros((N, N))
    for w in cw:
        if len(w) >= 2:
            J[w[0], w[-1]] += 1
    stat, p, dof, _ = chi2_contingency(J + 1e-9)
    print(f"  (first,last) rune joint: chi2={stat:.1f} dof={dof} p={p:.4f}")
    # word-initial digraph vs mid-word digraph two-sample (disjoint strata:
    # mid = neither first nor final digraph of its word)
    D1 = np.zeros((N, N))
    D2 = np.zeros((N, N))
    Df = np.zeros((N, N))
    for w in cw:
        for j in range(len(w) - 1):
            if j == 0:
                D1[w[j], w[j + 1]] += 1
            elif j == len(w) - 2:
                Df[w[j], w[j + 1]] += 1
            else:
                D2[w[j], w[j + 1]] += 1
    tab = np.vstack([D1.ravel(), D2.ravel()])
    keep = tab.sum(axis=0) > 0
    stat, p, dof, _ = chi2_contingency(tab[:, keep])
    print(f"  word-initial vs mid-word digraphs (two-sample): chi2={stat:.1f} "
          f"dof={dof} p={p:.4f}")
    tab = np.vstack([Df.ravel(), D2.ravel()])
    keep = tab.sum(axis=0) > 0
    stat, p, dof, _ = chi2_contingency(tab[:, keep])
    print(f"  word-final vs mid-word digraphs (two-sample): chi2={stat:.1f} "
          f"dof={dof} p={p:.4f}")


if __name__ == "__main__":
    main()
