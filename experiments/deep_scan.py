#!/usr/bin/env python3
"""Deeper anomaly battery for the unsolved LP.

A. Word-length-sequence repeated runs — a cipher-independent PLAINTEXT
   channel: repeated plaintext passages repeat their word-length pattern
   regardless of how the runes are encrypted.
B. Cross-correlation of the unsolved stream against the solved pages'
   rune stream (keystream / pad reuse check).
C. Bigram antisymmetry: count(a,b) vs count(b,a).
D. Full contingency of rune value vs position-in-line / position-in-page.
E. Within-word delta concentration (per-word coherent shift test).
F. Stationarity: rune x section contingency; per-rune positional KS.
G. Shortest window containing all 29 runes (embedded key table check).
H. Sentence-initial/final rune distributions.
I. FFT of the word-length sequence (meter/verse check).
"""

import math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2 as chi2_dist
from scipy.stats import chi2_contingency, kstest

from anomaly_scan import parse
from aldegonde import c3301

N = 29
RUNESET = set("".join(c3301.CICADA_ALPHABET))


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = np.array(stream[:-nplain])
    n = len(cipher)
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= n:
            cw.append(w)
        total += len(w)
    lens = np.array([len(w) for w in cw])
    nw = len(lens)
    print(f"cipher: {n} runes, {nw} words")

    print("\n=== A. WORD-LENGTH-SEQUENCE REPEATED RUNS ===")
    # longest repeated k-gram in the word-length sequence vs MC with
    # shuffled word lengths (preserves length distribution, kills order)
    def longest_rep(seq):
        best = 0
        k = max(best, 4)
        while True:
            d = defaultdict(int)
            found = False
            for i in range(len(seq) - k + 1):
                t = tuple(seq[i : i + k])
                d[t] += 1
                if d[t] > 1:
                    found = True
            if not found:
                return k - 1
            k += 1

    def count_reps(seq, k):
        d = Counter(tuple(seq[i : i + k]) for i in range(len(seq) - k + 1))
        return sum(v * (v - 1) // 2 for v in d.values())

    obs_longest = longest_rep(list(lens))
    rng = np.random.default_rng(3)
    mc_longest = []
    mc_counts8 = []
    for _ in range(200):
        sh = lens.copy()
        rng.shuffle(sh)
        mc_longest.append(longest_rep(list(sh)))
        mc_counts8.append(count_reps(list(sh), 8))
    obs8 = count_reps(list(lens), 8)
    mc_longest = np.array(mc_longest)
    mc_counts8 = np.array(mc_counts8)
    print(f"  longest repeated word-length run: obs={obs_longest} "
          f"mc mean={mc_longest.mean():.1f} max={mc_longest.max()} "
          f"P(>=obs)={(mc_longest >= obs_longest).mean():.3f}")
    print(f"  repeated 8-grams: obs={obs8} mc mean={mc_counts8.mean():.1f} "
          f"sd={mc_counts8.std():.1f} z={(obs8 - mc_counts8.mean()) / mc_counts8.std():+.2f}")
    # show the longest run(s)
    k = obs_longest
    d = defaultdict(list)
    for i in range(nw - k + 1):
        d[tuple(lens[i : i + k])].append(i)
    for t, v in d.items():
        if len(v) > 1:
            print(f"  longest run {t} at word indices {v}")

    print("\n=== B. CROSS-CORRELATION VS SOLVED STREAM ===")
    master = open("data/liber-primus__transcription--master.txt").read()
    solved_runes = []
    cnt = 0
    for ch in master:
        if ch in RUNESET:
            cnt += 1
            if cnt > 2797:
                break
            solved_runes.append(c3301.r2i(ch))
    s = np.array(solved_runes)
    m = len(s)
    # count coincidences at every alignment via FFT over one-hot channels
    L = n + m
    fftlen = 1 << (L - 1).bit_length()
    tot = np.zeros(fftlen)
    for r in range(N):
        a = (cipher == r).astype(float)
        b = (s == r).astype(float)
        fa = np.fft.rfft(a, fftlen)
        fb = np.fft.rfft(b[::-1], fftlen)
        tot += np.fft.irfft(fa * fb, fftlen)
    # alignment t: overlap length
    hits = tot[: n + m - 1]
    overlap = np.array([min(i + 1, m, n, n + m - 1 - i) for i in range(n + m - 1)])
    mask = overlap >= 200
    z = (hits[mask] - overlap[mask] / N) / np.sqrt(overlap[mask] * (1 / N) * (1 - 1 / N))
    print(f"  alignments tested: {mask.sum()}, max z={z.max():+.2f} min z={z.min():+.2f} "
          f"(expected max ~{math.sqrt(2 * math.log(mask.sum())):.1f})")

    print("\n=== C. BIGRAM ANTISYMMETRY ===")
    J = np.zeros((N, N))
    np.add.at(J, (cipher[:-1], cipher[1:]), 1)
    stat = 0.0
    dof = 0
    for a in range(N):
        for b in range(a + 1, N):
            tot_ab = J[a, b] + J[b, a]
            if tot_ab > 0:
                stat += (J[a, b] - J[b, a]) ** 2 / tot_ab
                dof += 1
    print(f"  antisymmetry chi2={stat:.1f} dof={dof} p={chi2_dist.sf(stat, dof):.4f}")

    print("\n=== D. RUNE VS POSITION-IN-LINE / POSITION-IN-PAGE ===")
    pos_line = []
    for l in lines:
        for j, r in enumerate(l):
            pos_line.append((min(j, 20), r))
    tab = np.zeros((21, N))
    for j, r in pos_line:
        tab[j, r] += 1
    stat, p, dof, _ = chi2_contingency(tab)
    print(f"  rune x pos-in-line (0..20+): chi2={stat:.1f} dof={dof} p={p:.4f}")
    tab2 = np.zeros((21, N))
    for l in lines:
        for j, r in enumerate(l[1:], 1):  # exclude line-initial (known bias)
            tab2[min(j, 20), r] += 1
    stat, p, dof, _ = chi2_contingency(tab2[1:])
    print(f"  rune x pos-in-line excl col 0: chi2={stat:.1f} dof={dof} p={p:.4f}")
    pos_page = []
    for pg in pages:
        for j, r in enumerate(pg):
            pos_page.append((min(j // 25, 11), r))
    tab = np.zeros((12, N))
    for j, r in pos_page:
        tab[j, r] += 1
    stat, p, dof, _ = chi2_contingency(tab)
    print(f"  rune x pos-in-page (25-rune bands): chi2={stat:.1f} dof={dof} p={p:.4f}")

    print("\n=== E. WITHIN-WORD DELTA CONCENTRATION ===")
    # If each word had a coherent progressive shift, within-word deltas
    # would cluster per word. Statistic: mean resultant length of deltas
    # per word (circular), averaged over words of len>=4.
    def mean_resultant(ws):
        rs = []
        for w in ws:
            if len(w) >= 4:
                dl = np.diff(w) % N
                ang = 2 * np.pi * dl / N
                rs.append(abs(np.exp(1j * ang).mean()))
        return float(np.mean(rs))
    obs_r = mean_resultant(cw)
    rng = np.random.default_rng(5)
    mc = []
    for _ in range(200):
        sim = [rng.integers(0, N, len(w)) for w in cw]
        mc.append(mean_resultant(sim))
    mc = np.array(mc)
    print(f"  mean resultant length: obs={obs_r:.4f} mc={mc.mean():.4f}±{mc.std():.4f} "
          f"z={(obs_r - mc.mean()) / mc.std():+.2f}")

    print("\n=== F. STATIONARITY ===")
    secs = [s_ for s_ in sections[:-1] if len(s_) >= 300]
    tab = np.zeros((len(secs), N))
    for i, s_ in enumerate(secs):
        for r in s_:
            tab[i, r] += 1
    stat, p, dof, _ = chi2_contingency(tab)
    print(f"  rune x section ({len(secs)} sections >=300): chi2={stat:.1f} dof={dof} p={p:.4f}")
    worst = []
    for r in range(N):
        posr = np.where(cipher == r)[0] / n
        stat_ks = kstest(posr, "uniform")
        worst.append((stat_ks.pvalue, r))
    worst.sort()
    print(f"  per-rune positional KS, 3 lowest p: "
          f"{[(c3301.CICADA_ALPHABET[r], round(p_, 4)) for p_, r in worst[:3]]} "
          f"(29 tests, Bonferroni 0.0017)")

    print("\n=== G. SHORTEST ALL-29 WINDOW ===")
    best = (10**9, -1)
    last = {}
    count = 0
    # sliding minimal window containing all 29 symbols
    left = 0
    have = Counter()
    distinct = 0
    for right in range(n):
        have[int(cipher[right])] += 1
        if have[int(cipher[right])] == 1:
            distinct += 1
        while distinct == N:
            if right - left + 1 < best[0]:
                best = (right - left + 1, left)
            have[int(cipher[left])] -= 1
            if have[int(cipher[left])] == 0:
                distinct -= 1
            left += 1
    rng = np.random.default_rng(9)
    mcb = []
    for _ in range(100):
        sim = rng.integers(0, N, n)
        bb = 10**9
        left = 0
        have = Counter()
        distinct = 0
        for right in range(n):
            have[int(sim[right])] += 1
            if have[int(sim[right])] == 1:
                distinct += 1
            while distinct == N:
                bb = min(bb, right - left + 1)
                have[int(sim[left])] -= 1
                if have[int(sim[left])] == 0:
                    distinct -= 1
                left += 1
        mcb.append(bb)
    mcb = np.array(mcb)
    print(f"  shortest window with all 29 runes: obs={best[0]} at {best[1]} | "
          f"mc mean={mcb.mean():.1f} min={mcb.min()} P(<=obs)={(mcb <= best[0]).mean():.3f}")

    print("\n=== H. SENTENCE-INITIAL/FINAL RUNES ===")
    si = [stream[i + 1] for i, sp in enumerate(seps[: n - 1]) if sp == "s"]
    sf = [stream[i] for i, sp in enumerate(seps[: n - 1]) if sp == "s"]
    for name, vals in (("sentence-initial", si), ("sentence-final", sf)):
        c = Counter(vals)
        m_ = len(vals)
        counts = [c[i] for i in range(N)]
        stat = sum((x - m_ / N) ** 2 / (m_ / N) for x in counts)
        print(f"  {name}: n={m_} chi2={stat:.1f} p={chi2_dist.sf(stat, N - 1):.4f}")

    print("\n=== I. WORD-LENGTH SEQUENCE SPECTRUM ===")
    x = lens - lens.mean()
    X = np.abs(np.fft.rfft(x)) ** 2 / len(x)
    pw = X[1:]
    peak = pw.max() / pw.mean()
    print(f"  max power / mean = {peak:.1f} "
          f"(white-noise expectation ~{math.log(len(pw)):.1f})")


if __name__ == "__main__":
    main()
