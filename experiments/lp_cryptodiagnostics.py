#!/usr/bin/env python3
"""Comprehensive cryptodiagnostics battery for the unsolved Liber Primus pages.

Reads data/page0-58.txt and runs a structured battery of statistical tests:

  A. Corpus parsing and verification (rune/word/section counts)
  B. Baseline global statistics (frequencies, entropy, IOC, kappa, doublets)
  C. Homogeneity across sections, pages, and sliding windows; cross-section kappa
  D. Word-structure diagnostics (position-in-word, repeated words, isomorphs,
     boundary effects, word sums)
  E. Doublet micro-structure (value distribution, context, position in word)
  F. Higher-order randomness (bigram asymmetry, n-gram repeats, delta streams,
     compression, mutual information at lags, interleave tests)
  G. Targeted split tests for open hypotheses (reverse-direction autokey,
     word-sum keying, column streams)
  H. Heavy scans (prime-totient shift offsets, key-reuse at all lags,
     running-key candidates) — needs numpy, takes a few minutes

Null models use either exact uniform expectations or shuffle baselines.

Key findings from the 2026-06 run are written up in
hypotheses/cryptodiagnostics-page0-58.md.

Usage:  python experiments/lp_cryptodiagnostics.py [sections...]
        where sections is any subset of A B C D E F G H (default: A-G)
"""

from __future__ import annotations

import bz2
import lzma
import math
import random
import sys
import zlib
from collections import Counter, defaultdict

from scipy.stats import chisquare, kstest, norm, poisson

from aldegonde import c3301

M = 29  # alphabet size
RUNES = set(c3301.CICADA_ALPHABET)
R2I = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
GP_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59,
             61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109]

DATA = "data/page0-58.txt"


# ---------------------------------------------------------------- parsing

def parse(path: str = DATA):
    """Parse the transcription into runes, words, sections, pages.

    '/' and newline are line-wrap continuations (words span them).
    Every other non-rune character is a word boundary. '$' additionally
    delimits sections and '%' pages.
    """
    with open(path) as f:
        text = f.read()

    runes: list[int] = []          # full rune stream as 0-28 indices
    words: list[list[int]] = []    # words as lists of indices
    word_section: list[int] = []   # section number of each word
    word_gapchars: list[str] = []  # separator chars seen before each word
    sections: list[list[int]] = [[]]
    pages: list[list[int]] = [[]]

    cur: list[int] = []
    gap: list[str] = []

    def endword() -> None:
        nonlocal cur
        if cur:
            words.append(cur)
            word_section.append(len(sections) - 1)
            word_gapchars.append("".join(gap))
            cur = []
        gap.clear()

    for ch in text:
        if ch in RUNES:
            i = R2I[ch]
            cur.append(i)
            runes.append(i)
            sections[-1].append(i)
            pages[-1].append(i)
        elif ch in "/\n":
            continue  # line wrap, not a word boundary
        else:
            endword()
            gap.append(ch)
            if ch == "$":
                sections.append([])
            if ch == "%":
                pages.append([])
    endword()

    sections = [s for s in sections if s]
    pages = [p for p in pages if p]
    return runes, words, word_section, word_gapchars, sections, pages


# ---------------------------------------------------------------- helpers

def ioc(seq) -> float:
    n = len(seq)
    if n < 2:
        return 0.0
    c = Counter(seq)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def kappa(seq, skip: int) -> tuple[int, int, float]:
    """Coincidences at distance `skip`: (hits, trials, z-score vs 1/29)."""
    hits = sum(1 for i in range(len(seq) - skip) if seq[i] == seq[i + skip])
    trials = len(seq) - skip
    p = 1 / M
    mu, sd = trials * p, math.sqrt(trials * p * (1 - p))
    return hits, trials, (hits - mu) / sd


def shannon(seq) -> float:
    n = len(seq)
    c = Counter(seq)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def chi2_uniform(counts, total=None):
    obs = list(counts)
    return chisquare(obs)


def z2p(z: float) -> float:
    return 2 * norm.sf(abs(z))


def pack(seq) -> bytes:
    return bytes(seq)


def header(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


# ---------------------------------------------------------------- sections

def section_a(runes, words, word_section, sections, pages):
    header("A. CORPUS PARSING AND VERIFICATION")
    print(f"runes: {len(runes)}   words: {len(words)}   "
          f"sections: {len(sections)}   pages: {len(pages)}")
    print(f"section lengths: {[len(s) for s in sections]}")
    wl = Counter(len(w) for w in words)
    print("word lengths:", dict(sorted(wl.items())))
    mean_wl = sum(len(w) for w in words) / len(words)
    print(f"mean word length: {mean_wl:.3f}")

    # contamination check: section 10 is the solved AN END page
    # (C - (p_n - 1) mod 29), section 11 is the unencrypted Parable.
    if len(sections) >= 12:
        primes = []
        x = 2
        while len(primes) < len(sections[10]):
            if all(x % p for p in primes if p * p <= x):
                primes.append(x)
            x += 1
        dec = [(c - (primes[i] - 1)) % M for i, c in enumerate(sections[10])]
        eng = "".join(c3301.CICADA_ENGLISH_ALPHABET[i] for i in dec[:24])
        print(f"\nsection 10 decrypted with C-(p_n-1): {eng}...")
        par = "".join(c3301.CICADA_ENGLISH_ALPHABET[i] for i in sections[11][:18])
        print(f"section 11 read as plaintext: {par}...")
        print("=> sections 10 (AN END, solved) and 11 (Parable, plaintext) "
              "are NOT unsolved ciphertext; clean cipher corpus is "
              f"sections 0-9 ({sum(len(s) for s in sections[:10])} runes)")


def section_b(runes):
    header("B. BASELINE GLOBAL STATISTICS")
    n = len(runes)
    c = Counter(runes)
    counts = [c[i] for i in range(M)]
    stat, p = chi2_uniform(counts)
    print(f"unigram chi-sq vs uniform: {stat:.1f} (df=28), p={p:.3f}")
    print(f"min/max rune count: {min(counts)}/{max(counts)} "
          f"(expected {n / M:.0f})")
    h1 = shannon(runes)
    big = [(runes[i], runes[i + 1]) for i in range(n - 1)]
    tri = [tuple(runes[i:i + 3]) for i in range(n - 2)]
    h2 = shannon(big)
    h3 = shannon(tri)
    print(f"entropy H1={h1:.4f} (max {math.log2(M):.4f}), "
          f"H2/2={h2 / 2:.4f}, H3/3={h3 / 3:.4f}")
    print(f"conditional H(X2|X1)={h2 - h1:.4f}, H(X3|X1X2)={h3 - h2:.4f}")
    print(f"IOC mono={ioc(runes):.5f} (1/29={1 / M:.5f})  "
          f"di={ioc(big):.6f} (1/841={1 / M**2:.6f})  "
          f"tri={ioc(tri):.7f} (1/24389={1 / M**3:.7f})")

    doublets = [i for i in range(n - 1) if runes[i] == runes[i + 1]]
    triplets = [i for i in range(n - 2)
                if runes[i] == runes[i + 1] == runes[i + 2]]
    exp_d = (n - 1) / M
    print(f"doublets: {len(doublets)} (expected {exp_d:.0f}, "
          f"rate {len(doublets) / (n - 1):.4%} vs 1/29={1 / M:.4%}, "
          f"suppression x{exp_d / len(doublets):.2f})")
    print(f"triplets: {len(triplets)} (expected {(n - 2) / M**2:.1f})")

    print("\nkappa by skip (z-score vs random):")
    flagged = []
    for s in range(1, 61):
        hits, trials, z = kappa(runes, s)
        mark = " ***" if abs(z) > 3 else ""
        if abs(z) > 2.5:
            flagged.append((s, hits, z))
        if s <= 12 or abs(z) > 2.5:
            print(f"  skip {s:3d}: {hits:4d}/{trials}  z={z:+6.2f}{mark}")
    print(f"flagged skips (|z|>2.5): {[(s, f'{z:+.1f}') for s, _, z in flagged]}")


def section_c(runes, sections, pages):
    header("C. HOMOGENEITY: SECTIONS, PAGES, SLIDING WINDOWS")
    print(f"{'sec':>3} {'len':>5} {'IOC':>7} {'doubl':>5} {'d-rate':>7} "
          f"{'chi2-p':>7} {'H1':>6}")
    for i, s in enumerate(sections):
        d = sum(1 for j in range(len(s) - 1) if s[j] == s[j + 1])
        cc = Counter(s)
        stat, p = chi2_uniform([cc[k] for k in range(M)])
        print(f"{i:>3} {len(s):>5} {ioc(s):>7.4f} {d:>5} "
              f"{d / (len(s) - 1):>7.3%} {p:>7.3f} {shannon(s):>6.3f}")

    # doublet-rate homogeneity across sections (chi-sq on counts)
    dcounts = [sum(1 for j in range(len(s) - 1) if s[j] == s[j + 1])
               for s in sections]
    trials = [len(s) - 1 for s in sections]
    tot_d, tot_t = sum(dcounts), sum(trials)
    exp = [tot_d * t / tot_t for t in trials]
    stat = sum((o - e) ** 2 / e for o, e in zip(dcounts, exp))
    print(f"\nsection doublet homogeneity: chi-sq {stat:.1f} "
          f"(df={len(sections) - 1}), "
          f"poisson sf check p={1 - poisson.cdf(max(dcounts), max(exp)):.3f}")

    # sliding window IOC and doublet rate
    win, step = 500, 250
    print("\nsliding window (500 runes): pos  IOC  doublets")
    worst = []
    for start in range(0, len(runes) - win + 1, step):
        w = runes[start:start + win]
        d = sum(1 for j in range(win - 1) if w[j] == w[j + 1])
        worst.append((d, start, ioc(w)))
    ds = [d for d, _, _ in worst]
    print(f"  doublets per window: min {min(ds)}, max {max(ds)}, "
          f"mean {sum(ds) / len(ds):.2f}")
    iocs = [i3 for _, _, i3 in worst]
    print(f"  IOC per window: min {min(iocs):.4f}, max {max(iocs):.4f}")

    # cross-section kappa: key reuse between sections?
    print("\ncross-section kappa (align section i vs j at offset 0):")
    zs = []
    for i in range(len(sections)):
        for j in range(i + 1, len(sections)):
            a, b = sections[i], sections[j]
            L = min(len(a), len(b))
            hits = sum(1 for k in range(L) if a[k] == b[k])
            mu = L / M
            sd = math.sqrt(L * (1 / M) * (1 - 1 / M))
            z = (hits - mu) / sd
            zs.append((abs(z), i, j, z))
    zs.sort(reverse=True)
    for _absz, i, j, z in zs[:5]:
        print(f"  sec {i} vs {j}: z={z:+.2f}")
    print(f"  max |z| = {zs[0][0]:.2f} over {len(zs)} pairs "
          f"(Bonferroni 0.05 threshold ~ {norm.isf(0.025 / len(zs)):.2f})")


def section_d(runes, words, word_section, rng):
    header("D. WORD-STRUCTURE DIAGNOSTICS")

    # D1: per-position-in-word stats (from start and from end)
    print("D1. rune distribution by position in word (chi-sq p, IOC):")
    for label, keyf in (("from start", lambda w, k: k),
                        ("from end", lambda w, k: len(w) - 1 - k)):
        groups = defaultdict(list)
        for w in words:
            for k, r in enumerate(w):
                groups[keyf(w, k)].append(r)
        for pos in sorted(groups)[:6]:
            g = groups[pos]
            cc = Counter(g)
            stat, p = chi2_uniform([cc[k] for k in range(M)])
            print(f"  {label} pos {pos}: n={len(g):5d}  IOC={ioc(g):.4f}  "
                  f"flat-p={p:.3f}")

    # D2: IOC per (word length, position) cell
    print("\nD2. IOC by (word length, position) — flag cells with z>3:")
    flags = 0
    for wl in range(1, 11):
        ws = [w for w in words if len(w) == wl]
        if len(ws) < 20:
            continue
        for k in range(wl):
            g = [w[k] for w in ws]
            i3 = ioc(g)
            nn = len(g)
            # z for IOC vs 1/29 under uniform: var of coincidences
            pairs = nn * (nn - 1) / 2
            mu = pairs / M
            sd = math.sqrt(pairs * (1 / M) * (1 - 1 / M))
            hits = i3 * pairs
            z = (hits - mu) / sd
            if abs(z) > 3:
                flags += 1
                print(f"  len {wl} pos {k}: n={nn} IOC={i3:.4f} z={z:+.1f}")
    print(f"  flagged cells: {flags}")

    # D3: repeated ciphertext words vs shuffle null
    print("\nD3. repeated ciphertext words (by length):")
    def count_repeats(ws):
        by_len = defaultdict(Counter)
        for w in ws:
            by_len[len(w)][tuple(w)] += 1
        return {L: sum(v - 1 for v in c.values() if v > 1)
                for L, c in by_len.items()}

    obs = count_repeats(words)
    # null: shuffle all runes, re-cut into same word lengths
    null = defaultdict(list)
    flat = list(runes)
    lens = [len(w) for w in words]
    for _ in range(30):
        rng.shuffle(flat)
        it = iter(flat)
        ws = [[next(it) for _ in range(L)] for L in lens]
        for L, v in count_repeats(ws).items():
            null[L].append(v)
    for L in sorted(set(obs) | set(null)):
        if L > 12:
            continue
        nv = null.get(L, [0])
        mu = sum(nv) / len(nv)
        sd = math.sqrt(sum((x - mu) ** 2 for x in nv) / len(nv)) or 1.0
        o = obs.get(L, 0)
        mark = " ***" if abs(o - mu) > 3 * sd and o > 0 else ""
        print(f"  len {L:2d}: repeats obs={o:4d}  null={mu:7.1f}±{sd:5.1f}{mark}")

    # D4: within-word isomorph patterns (internal repeats at distance d)
    print("\nD4. within-word repeats at distance d (obs vs (n_d)/29):")
    for d in range(1, 6):
        hits = trials = 0
        for w in words:
            for k in range(len(w) - d):
                trials += 1
                hits += w[k] == w[k + d]
        if trials:
            mu = trials / M
            sd = math.sqrt(trials * (1 / M) * (1 - 1 / M))
            print(f"  d={d}: {hits}/{trials} z={(hits - mu) / sd:+.2f}")

    # D5: cross-boundary vs within-word bigram coincidence
    print("\nD5. boundary effects:")
    cross = [(words[i][-1], words[i + 1][0]) for i in range(len(words) - 1)]
    ch = sum(1 for a, b in cross if a == b)
    mu = len(cross) / M
    sd = math.sqrt(len(cross) * (1 / M) * (1 - 1 / M))
    print(f"  last-rune==first-rune across boundary: {ch}/{len(cross)} "
          f"z={(ch - mu) / sd:+.2f}")
    first = [w[0] for w in words]
    last = [w[-1] for w in words]
    cf = Counter(first)
    cl = Counter(last)
    _, pf = chi2_uniform([cf[k] for k in range(M)])
    _, pl = chi2_uniform([cl[k] for k in range(M)])
    print(f"  first-rune flatness p={pf:.3f}, last-rune flatness p={pl:.3f}")
    # consecutive identical words
    same = sum(1 for i in range(len(words) - 1) if words[i] == words[i + 1])
    print(f"  identical consecutive words: {same}")

    # D6: word sums
    print("\nD6. word sums:")
    sums = [sum(w) % M for w in words]
    cs = Counter(sums)
    stat, p = chi2_uniform([cs[k] for k in range(M)])
    print(f"  word sum mod 29 flatness: chi-sq {stat:.1f}, p={p:.3f}")
    gp = [sum(GP_PRIMES[r] for r in w) for w in words]
    # primality of GP word sums vs shuffle null
    def isprime(x):
        if x < 2:
            return False
        return all(x % q != 0 for q in range(2, int(x ** 0.5) + 1))
    obs_p = sum(1 for x in gp if isprime(x))
    nulls = []
    for _ in range(30):
        rng.shuffle(flat)
        it = iter(flat)
        nulls.append(sum(1 for L in lens
                         if isprime(sum(GP_PRIMES[next(it)] for _ in range(L)))))
    mu = sum(nulls) / len(nulls)
    sd = math.sqrt(sum((x - mu) ** 2 for x in nulls) / len(nulls)) or 1.0
    print(f"  GP word sums prime: obs={obs_p}  null={mu:.1f}±{sd:.1f} "
          f"z={(obs_p - mu) / sd:+.2f}")

    # D7: single-rune words
    ones = [w[0] for w in words if len(w) == 1]
    print(f"\nD7. single-rune words: {len(ones)}, "
          f"distinct values {len(set(ones))}, IOC={ioc(ones):.4f}")

    # D8: coincidence z by (word length, distance) heatmap
    print("\nD8. coincidence z by (word length L, distance d), |z|>=2 shown:")
    print("      " + "".join(f"d={d:<6}" for d in range(1, 10)))
    for wl in range(3, 15):
        ws = [w for w in words if len(w) == wl]
        row = f"L={wl:<3} "
        for d in range(1, 10):
            hits = trials = 0
            for w in ws:
                for k in range(wl - d):
                    trials += 1
                    hits += w[k] == w[k + d]
            if trials < 25:
                row += " " * 8
                continue
            mu = trials / M
            sd = math.sqrt(trials * (1 / M) * (1 - 1 / M))
            z = (hits - mu) / sd
            row += f"{z:+5.1f}   " if abs(z) >= 2 else "   .    "
        print(row)


def section_e(runes, words):
    header("E. DOUBLET MICRO-STRUCTURE")
    n = len(runes)
    dpos = [i for i in range(n - 1) if runes[i] == runes[i + 1]]
    vals = [runes[i] for i in dpos]
    cv = Counter(vals)
    stat, p = chi2_uniform([cv[k] for k in range(M)])
    print(f"doublet rune values: {len(dpos)} doublets, "
          f"distinct {len(cv)}, flatness p={p:.3f}")
    print("  counts:", [cv[k] for k in range(M)])

    # context: rune before and after a doublet
    before = Counter(runes[i - 1] for i in dpos if i > 0)
    after = Counter(runes[i + 2] for i in dpos if i + 2 < n)
    _, pb = chi2_uniform([before[k] for k in range(M)])
    _, pa = chi2_uniform([after[k] for k in range(M)])
    print(f"rune before doublet flatness p={pb:.3f}, after p={pa:.3f}")

    # delta between doublet value and neighbors
    db = Counter((runes[i] - runes[i - 1]) % M for i in dpos if i > 0)
    _, pdb = chi2_uniform([db[k] for k in range(M)])
    print(f"(doublet - preceding) mod 29 flatness p={pdb:.3f}")

    # doublet position within word
    pos_in_word = []
    idx = 0
    starts = {}
    for w in words:
        for k in range(len(w)):
            starts[idx + k] = (k, len(w))
        idx += len(w)
    within = cross = 0
    for i in dpos:
        k1, L1 = starts[i]
        k2, L2 = starts[i + 1]
        if k2 == k1 + 1:
            within += 1
            pos_in_word.append(k1)
        else:
            cross += 1
    print(f"within-word doublets: {within}, cross-boundary: {cross}")
    print(f"  first-rune offset of within-word doublets: "
          f"{sorted(Counter(pos_in_word).items())}")

    # gaps
    gaps = [b - a for a, b in zip(dpos, dpos[1:])]
    if gaps:
        mean = sum(gaps) / len(gaps)
        ks = kstest(gaps, "expon", args=(0, mean))
        print(f"gaps: n={len(gaps)} mean={mean:.1f} min={min(gaps)} "
              f"KS-vs-exp p={ks.pvalue:.3f}")


def section_f(runes, rng):
    header("F. HIGHER-ORDER RANDOMNESS")
    n = len(runes)

    # F1: bigram matrix asymmetry
    cnt = Counter((runes[i], runes[i + 1]) for i in range(n - 1))
    stat = 0.0
    cells = 0
    for a in range(M):
        for b in range(a + 1, M):
            x, y = cnt[(a, b)], cnt[(b, a)]
            if x + y > 0:
                stat += (x - y) ** 2 / (x + y)
                cells += 1
    print(f"F1. bigram asymmetry chi-sq {stat:.1f} (df={cells}), "
          f"p={1 - __import__('scipy.stats', fromlist=['chi2']).chi2.cdf(stat, cells):.3f}")

    # F2: n-gram repeats vs birthday expectation
    print("F2. repeated n-grams (distinct n-grams occurring >= 2x):")
    for k in range(3, 9):
        grams = Counter(tuple(runes[i:i + k]) for i in range(n - k + 1))
        rep = sum(1 for v in grams.values() if v > 1)
        nn = n - k + 1
        exp = nn * (nn - 1) / 2 / M ** k  # expected repeated pairs
        print(f"  {k}-grams: {rep} repeated (expected pairs ~{exp:.1f})")
    # longest repeat
    best = 0
    k = 8
    while True:
        grams = defaultdict(list)
        for i in range(n - k + 1):
            grams[tuple(runes[i:i + k])].append(i)
        hit = {g: pos for g, pos in grams.items() if len(pos) > 1}
        if not hit:
            break
        best = k
        bestpos = hit
        k += 1
    if best:
        print(f"  longest repeat: {best}-gram at "
              f"{list(bestpos.values())}")

    # F3: delta streams
    print("F3. delta streams:")
    for skip in (1, 2):
        d = [(runes[i + skip] - runes[i]) % M for i in range(n - skip)]
        cd = Counter(d)
        stat, p = chi2_uniform([cd[k] for k in range(M)])
        dd = sum(1 for i in range(len(d) - 1) if d[i] == d[i + 1])
        mu = (len(d) - 1) / M
        sd = math.sqrt((len(d) - 1) * (1 / M) * (1 - 1 / M))
        print(f"  skip {skip}: flat-p={p:.3f} IOC={ioc(d):.5f} "
              f"delta-doublets z={(dd - mu) / sd:+.2f} "
              f"(=2nd-difference zeros / 3-term APs)")

    # F4: compression vs shuffled baseline
    print("F4. compression (bytes; lower than null = structure):")
    data = pack(runes)
    base = {"zlib": len(zlib.compress(data, 9)),
            "bz2": len(bz2.compress(data, 9)),
            "lzma": len(lzma.compress(data, preset=9))}
    nulls = defaultdict(list)
    flat = list(runes)
    for _ in range(20):
        rng.shuffle(flat)
        d2 = pack(flat)
        nulls["zlib"].append(len(zlib.compress(d2, 9)))
        nulls["bz2"].append(len(bz2.compress(d2, 9)))
        nulls["lzma"].append(len(lzma.compress(d2, preset=9)))
    for k, v in base.items():
        mu = sum(nulls[k]) / len(nulls[k])
        sd = math.sqrt(sum((x - mu) ** 2 for x in nulls[k]) / len(nulls[k])) or 1.0
        print(f"  {k}: obs={v} null={mu:.0f}±{sd:.1f} z={(v - mu) / sd:+.2f}")

    # F5: mutual information at lags (with shuffle baseline)
    print("F5. mutual information I(X_i; X_i+lag) in millibits:")
    def mi(seq, lag):
        joint = Counter((seq[i], seq[i + lag]) for i in range(len(seq) - lag))
        tot = len(seq) - lag
        px = Counter(seq[:-lag])
        py = Counter(seq[lag:])
        s = 0.0
        for (a, b), v in joint.items():
            s += v / tot * math.log2(v / tot / (px[a] / tot * py[b] / tot))
        return s * 1000
    null_mi = []
    for _ in range(10):
        rng.shuffle(flat)
        null_mi.append(mi(flat, 1))
    mu = sum(null_mi) / len(null_mi)
    print(f"  shuffle baseline (bias): {mu:.1f} mb")
    for lag in (1, 2, 3, 4, 5, 10, 20, 29, 58):
        print(f"  lag {lag:3d}: {mi(runes, lag):6.1f} mb")

    # F6: interleave test — split into k streams by index mod k
    print("F6. interleaved streams (index mod k): doublet z per stream:")
    for k in (2, 3, 4, 5):
        zs = []
        for off in range(k):
            s = runes[off::k]
            _, _, z = kappa(s, 1)
            zs.append(f"{z:+.1f}")
        print(f"  k={k}: {zs}")


def section_g(runes, words, rng):
    header("G. TARGETED SPLIT TESTS (open hypotheses)")
    n = len(runes)

    # G1: split by FOLLOWING rune (reverse-direction autokey)
    print("G1. split C[i] by C[i+1] (reverse autokey): IOC per group")
    groups = defaultdict(list)
    for i in range(n - 1):
        groups[runes[i + 1]].append(runes[i])
    iocs = [ioc(g) for g in groups.values()]
    print(f"  mean IOC {sum(iocs) / len(iocs):.4f} "
          f"min {min(iocs):.4f} max {max(iocs):.4f} (random=0.0345, "
          f"runeglish~0.06)")

    # G2: split by C[i-2] and C[i+2]
    for off, lab in ((-2, "C[i-2]"), (2, "C[i+2]")):
        groups = defaultdict(list)
        for i in range(n):
            j = i + off
            if 0 <= j < n:
                groups[runes[j]].append(runes[i])
        iocs = [ioc(g) for g in groups.values()]
        print(f"G2. split by {lab}: mean IOC {sum(iocs) / len(iocs):.4f} "
              f"max {max(iocs):.4f}")

    # G3: word-sum keying — group word runes by previous word's sum mod 29
    print("G3. group runes by (prev word sum mod 29, position): IOC")
    groups = defaultdict(list)
    for i in range(1, len(words)):
        k = sum(words[i - 1]) % M
        for pos, r in enumerate(words[i][:4]):
            groups[(k, pos)].append(r)
    iocs = [(ioc(g), len(g), key) for key, g in groups.items() if len(g) >= 30]
    iocs.sort(reverse=True)
    mean = sum(x for x, _, _ in iocs) / len(iocs)
    print(f"  cells>=30: {len(iocs)}, mean IOC {mean:.4f}, "
          f"top: {[(f'{x:.3f}', l, k) for x, l, k in iocs[:3]]}")

    # G4: group by previous word's LAST rune and position
    print("G4. group runes by (prev word last rune, position): IOC")
    groups = defaultdict(list)
    for i in range(1, len(words)):
        k = words[i - 1][-1]
        for pos, r in enumerate(words[i][:3]):
            groups[(k, pos)].append(r)
    iocs = [(ioc(g), len(g)) for g in groups.values() if len(g) >= 30]
    mean = sum(x for x, _ in iocs) / len(iocs)
    print(f"  cells>=30: {len(iocs)}, mean IOC {mean:.4f}, "
          f"max {max(x for x, _ in iocs):.4f}")

    # G5: column streams — first/last runes of words as their own stream
    print("G5. word-column streams:")
    for lab, stream in (("first runes", [w[0] for w in words]),
                        ("last runes", [w[-1] for w in words]),
                        ("2nd runes", [w[1] for w in words if len(w) > 1])):
        h, t, z = kappa(stream, 1)
        print(f"  {lab}: n={len(stream)} IOC={ioc(stream):.4f} "
              f"adjacent-coincidence z={z:+.2f}")

    # G6: word-length sequence structure
    lens = [len(w) for w in words]
    h, t, z = kappa(lens, 1)
    print(f"G6. word-length sequence: IOC={ioc(lens):.4f} "
          f"adjacent-equal z={z:+.2f} (vs shuffled)")
    null = []
    ll = list(lens)
    for _ in range(50):
        rng.shuffle(ll)
        null.append(sum(1 for i in range(len(ll) - 1) if ll[i] == ll[i + 1]))
    mu = sum(null) / len(null)
    sd = math.sqrt(sum((x - mu) ** 2 for x in null) / len(null)) or 1.0
    obs = sum(1 for i in range(len(lens) - 1) if lens[i] == lens[i + 1])
    print(f"  adjacent equal lengths: obs={obs} null={mu:.1f}±{sd:.1f} "
          f"z={(obs - mu) / sd:+.2f}")


def section_h(sections):
    header("H. HEAVY SCANS (prime shifts, key reuse, running keys)")
    import numpy as np

    clean = np.array([x for s in sections[:10] for x in s])
    n = len(clean)
    print(f"clean corpus (sections 0-9): {n} runes")

    def zioc(st):
        m = len(st)
        cc = np.bincount(st, minlength=M).astype(np.float64)
        coinc = (cc * (cc - 1)).sum() / 2
        pairs = m * (m - 1) / 2
        return float((coinc - pairs / M)
                     / math.sqrt(pairs * (1 / M) * (1 - 1 / M)))

    # H1: prime-totient shift with any starting offset, both signs
    nprimes = 16000 + max(len(s) for s in sections)
    primes = []
    x = 2
    while len(primes) < nprimes:
        if all(x % p for p in primes if p * p <= x):
            primes.append(x)
        x += 1
    P = np.array(primes)
    print("\nH1. prime-shift offset scan, offsets 0..15999, both signs "
          "(IOC ~0.06 would be a hit):")
    for si, s in enumerate(sections[:10]):
        a = np.array(s)
        m = len(a)
        best = 0.0
        for sign in (1, -1):
            for off in range(16000):
                shifts = (P[off:off + m] - 1) % M
                d = (a - sign * shifts) % M
                cc = np.bincount(d, minlength=M).astype(np.float64)
                v = float((cc * (cc - 1)).sum()) / (m * (m - 1))
                best = max(best, v)
        print(f"  sec {si} (n={m}): best IOC {best:.4f}")

    # H2: key reuse at every lag (difference=Vigenere, sum=Beaufort)
    print("\nH2. diff/sum IOC at all lags (per-lag z, flag |z|>4.5):")
    for tag, op in (("diff", lambda x, y: (y - x) % M),
                    ("sum", lambda x, y: (y + x) % M)):
        flags = []
        for lag in range(1, n - 1000):
            z = zioc(op(clean[:-lag], clean[lag:]))
            if abs(z) > 4.5 and lag != 1:
                flags.append((lag, round(z, 1)))
        print(f"  {tag}: flags {flags} "
              f"(noise max over ~12k lags is ~4.5-5)")

    # H3: running keys — parable and full master transcription
    print("\nH3. running-key candidates at all alignments:")
    parable = np.array(sections[11]) if len(sections) > 11 else None
    keys = []
    if parable is not None:
        keys += [("parable", parable), ("parable-rev", parable[::-1])]
    try:
        with open("data/liber-primus__transcription--master.txt") as f:
            mast = np.array([R2I[ch] for ch in f.read() if ch in RUNES])
        keys.append(("master", mast))
    except FileNotFoundError:
        pass
    for name, key in keys:
        m = len(key)
        best = []
        if m <= n:
            for off in range(n - m):
                seg = clean[off:off + m]
                best.append((abs(zioc((seg - key) % M)), "V", off))
                best.append((abs(zioc((seg + key) % M)), "B", off))
        else:
            for off in range(m - 500):
                L = min(n, m - off)
                seg, kk = clean[:L], key[off:off + L]
                best.append((abs(zioc((seg - kk) % M)), "V", off))
                best.append((abs(zioc((seg + kk) % M)), "B", off))
        best.sort(reverse=True)
        print(f"  {name}: top {[(f'{z:.1f}', t, o) for z, t, o in best[:3]]}"
              " (shuffled-key null max is 5-8; master self-match at 2797 "
              "is the page0-58 subset)" if name == "master" else
              f"  {name}: top {[(f'{z:.1f}', t, o) for z, t, o in best[:3]]}")


def main() -> None:
    rng = random.Random(3301)
    runes, words, word_section, word_gapchars, sections, pages = parse()
    which = {a.upper() for a in sys.argv[1:]} or set("ABCDEFG")
    if "A" in which:
        section_a(runes, words, word_section, sections, pages)
    if "B" in which:
        section_b(runes)
    if "C" in which:
        section_c(runes, sections, pages)
    if "D" in which:
        section_d(runes, words, word_section, rng)
    if "E" in which:
        section_e(runes, words)
    if "F" in which:
        section_f(runes, rng)
    if "G" in which:
        section_g(runes, words, rng)
    if "H" in which:
        section_h(sections)


if __name__ == "__main__":
    main()
