#!/usr/bin/env python3
"""Forensics on the '.' mark process in the unsolved LP.

The sentence-final test showed '.' does not mark English sentence ends.
So what places it? Tested here:

1. Layout coupling: distance of each '.' from its line end; rate of '.'
   at exact line end vs the '-' baseline; solved-pages control.
2. Inter-mark distances (runes and words): shape (geometric vs humped),
   dispersion, autocorrelation, prime bias (Cicada), favored residues.
3. Block checksums: sums of rune indices and GP values between
   consecutive marks (mod 29 uniformity, primality of GP sums).
4. Mark rune-positions: primality, residues mod 29.
5. Doublets per block vs Poisson.
"""

import math
import re
from collections import Counter

import numpy as np
from scipy.stats import chi2 as chi2_dist

from anomaly_scan import parse
from aldegonde import c3301

N = 29
RUNESET = set("".join(c3301.CICADA_ALPHABET))


def is_prime(x: int) -> bool:
    if x < 2:
        return False
    for p in range(2, int(x**0.5) + 1):
        if x % p == 0:
            return False
    return True


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    C = np.array(stream[:-nplain], dtype=np.int64)
    n = len(C)

    u = open("data/page0-58.txt").read()
    u_cipher = u[: u.rfind("$")]

    print("=== 1. LAYOUT COUPLING ===")
    # rate of '.' immediately before a line break vs '-' baseline
    dot_eol = len(re.findall(r"\./", u_cipher))
    dot_all = u_cipher.count(".")
    dash_eol = len(re.findall(r"-/", u_cipher))
    dash_all = u_cipher.count("-")
    print(f"  unsolved: '.' at line end {dot_eol}/{dot_all} = "
          f"{100*dot_eol/dot_all:.1f}%   '-' at line end {dash_eol}/{dash_all} = "
          f"{100*dash_eol/dash_all:.1f}%")
    # binomial comparison
    p0 = dash_eol / dash_all
    z = (dot_eol - dot_all * p0) / math.sqrt(dot_all * p0 * (1 - p0))
    print(f"  '.' line-end excess vs '-' baseline: z={z:+.2f}")
    # solved control
    master = open("data/liber-primus__transcription--master.txt").read()
    count = 0
    cut = 0
    for i, ch in enumerate(master):
        if ch in RUNESET:
            count += 1
            if count == 2797:
                cut = i + 1
                break
    solved = master[:cut]
    sd_eol = len(re.findall(r"\./", solved))
    sd_all = solved.count(".")
    sh_eol = len(re.findall(r"-/", solved))
    sh_all = solved.count("-")
    p0s = sh_eol / sh_all
    zs = (sd_eol - sd_all * p0s) / math.sqrt(sd_all * p0s * (1 - p0s))
    print(f"  solved:   '.' at line end {sd_eol}/{sd_all} = "
          f"{100*sd_eol/sd_all:.1f}%   '-' at line end {sh_eol}/{sh_all} = "
          f"{100*sh_eol/sh_all:.1f}%  (z={zs:+.2f})")
    # distance of each '.' from line end, in runes
    dists = []
    cur_after = 0
    # walk the raw text per line
    for line in u_cipher.split("/"):
        rpos = [i for i, ch in enumerate(line) if ch in RUNESET]
        runes_total = len(rpos)
        seen = 0
        for ch in line:
            if ch in RUNESET:
                seen += 1
            elif ch == ".":
                dists.append(runes_total - seen)
    dd = np.array(dists)
    print(f"  '.' distance from line end (runes): mean={dd.mean():.1f} "
          f"(uniform on ~22-rune lines would be ~10.5); "
          f"share at 0 = {100*np.mean(dd == 0):.1f}%")
    hist = Counter(int(min(x, 10)) for x in dd)
    print(f"  histogram 0..10+: {[hist.get(k, 0) for k in range(11)]}")

    print("\n=== 2. INTER-MARK DISTANCES ===")
    mark_pos = [i for i in range(n - 1) if seps[i] == "s"]
    mp = np.array(mark_pos)
    gaps = np.diff(mp)
    print(f"  {len(mp)} marks; gaps (runes): mean={gaps.mean():.1f} "
          f"median={np.median(gaps):.0f} min={gaps.min()} max={gaps.max()} "
          f"cv={gaps.std()/gaps.mean():.2f} (exponential -> 1.0)")
    # autocorrelation of gaps
    x = gaps - gaps.mean()
    r1 = float(np.dot(x[:-1], x[1:]) / np.dot(x, x))
    print(f"  gap autocorrelation lag1: r={r1:+.3f} (z~{r1*math.sqrt(len(gaps)):+.2f})")
    # prime bias of gaps
    pr = sum(1 for g in gaps if is_prime(int(g)))
    # null: fraction of primes among plausible gap values, weighted by gaps
    rng = np.random.default_rng(1)
    sims = []
    for _ in range(400):
        sim = rng.permutation(gaps) + rng.integers(-3, 4, len(gaps))
        sims.append(sum(1 for g in sim if is_prime(int(abs(g)))))
    print(f"  prime gaps: {pr} of {len(gaps)} (jittered null {np.mean(sims):.1f}"
          f"±{np.std(sims):.1f}, z={(pr-np.mean(sims))/np.std(sims):+.2f})")
    # word-count gaps
    rune_word = []
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= n:
            cw.append(w)
        total += len(w)
    for i, w in enumerate(cw):
        rune_word.extend([i] * len(w))
    wgaps = np.diff([rune_word[i] for i in mark_pos])
    pwr = sum(1 for g in wgaps if is_prime(int(g)))
    sims = []
    for _ in range(400):
        sim = rng.permutation(wgaps) + rng.integers(-2, 3, len(wgaps))
        sims.append(sum(1 for g in sim if is_prime(int(abs(g)))))
    print(f"  sentence lengths (words): prime count {pwr} of {len(wgaps)} "
          f"(jittered null {np.mean(sims):.1f}±{np.std(sims):.1f}, "
          f"z={(pwr-np.mean(sims))/np.std(sims):+.2f})")

    print("\n=== 3. BLOCK CHECKSUMS ===")
    blocks = []
    prev = 0
    for i in mark_pos:
        blocks.append(C[prev : i + 1])
        prev = i + 1
    blocks.append(C[prev:])
    bsum = [int(b.sum()) % N for b in blocks if len(b)]
    c = np.bincount(bsum, minlength=N)
    m = len(bsum)
    stat = ((c - m / N) ** 2 / (m / N)).sum()
    print(f"  block rune-index sums mod 29: chi2={stat:.1f} "
          f"p={chi2_dist.sf(stat, N-1):.3f} (n={m})")
    GP = np.array([c3301.r2v(c3301.CICADA_ALPHABET[i]) for i in range(N)])
    gsum = [int(GP[b].sum()) for b in blocks if len(b)]
    gpr = sum(1 for g in gsum if is_prime(g))
    sims = []
    for _ in range(400):
        sim = [int(GP[rng.integers(0, N, len(b))].sum()) for b in blocks if len(b)]
        sims.append(sum(1 for g in sim if is_prime(g)))
    print(f"  block GP sums prime: {gpr} of {len(gsum)} "
          f"(null {np.mean(sims):.1f}±{np.std(sims):.1f}, "
          f"z={(gpr-np.mean(sims))/np.std(sims):+.2f})")
    gm = [g % N for g in gsum]
    c = np.bincount(gm, minlength=N)
    stat = ((c - len(gm) / N) ** 2 / (len(gm) / N)).sum()
    print(f"  block GP sums mod 29: chi2={stat:.1f} p={chi2_dist.sf(stat, N-1):.3f}")

    print("\n=== 4. MARK POSITIONS ===")
    pp = sum(1 for i in mp if is_prime(int(i)))
    pp1 = sum(1 for i in mp if is_prime(int(i) + 1))
    dens = sum(1.0 / math.log(max(int(i), 3)) for i in mp)
    print(f"  mark rune-positions prime (0-idx): {pp}; (1-idx): {pp1}; "
          f"expected ~{dens:.1f}")
    c = np.bincount(mp % N, minlength=N)
    stat = ((c - len(mp) / N) ** 2 / (len(mp) / N)).sum()
    print(f"  positions mod 29: chi2={stat:.1f} p={chi2_dist.sf(stat, N-1):.3f}")

    print("\n=== 5. DOUBLETS PER BLOCK ===")
    dbl_pos = [i for i in range(n - 1) if C[i] == C[i + 1]]
    per_block = Counter()
    bidx = np.searchsorted(mp, dbl_pos, side="left")
    for b in bidx:
        per_block[int(b)] += 1
    counts = [per_block.get(i, 0) for i in range(len(blocks))]
    lam = sum(counts) / len(counts)
    var = np.var(counts)
    print(f"  doublets per block: mean={lam:.2f} var={var:.2f} "
          f"Fano={var/lam:.2f} (Poisson->1; blocks vary in length so >1 expected)")


if __name__ == "__main__":
    main()
