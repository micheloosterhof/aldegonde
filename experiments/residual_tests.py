#!/usr/bin/env python3
"""Residual probes: line-initial bias correlation (solved vs unsolved),
doublet value-level context, digraphic kappa at all shifts, sentence stats.
"""

import math
from collections import Counter

import numpy as np
from scipy.stats import pearsonr, spearmanr, chi2 as chi2_dist, ks_2samp

from anomaly_scan import parse
from aldegonde import c3301

N = 29
ALPH = c3301.CICADA_ALPHABET
RUNESET = set("".join(ALPH))


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    cipher = np.array(stream[:-nplain])
    n = len(cipher)

    print("=== LINE-INITIAL BIAS: unsolved vs solved correlation ===")
    # unsolved line-initial counts (excluding parable lines)
    lns = lines[:-5]
    cu = Counter(l[0] for l in lns if l)
    unsolved = np.array([cu[i] for i in range(N)], dtype=float)
    # The solved pages are the FIRST 2797 runes of the master transcription;
    # page0-58.txt (13,136 runes) is the remainder.
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
    sol_lines = []
    cur = []
    for ch in solved:
        if ch in RUNESET:
            cur.append(c3301.r2i(ch))
        elif ch == "/":
            if cur:
                sol_lines.append(cur)
            cur = []
    if cur:
        sol_lines.append(cur)
    cs = Counter(l[0] for l in sol_lines if l)
    solvedv = np.array([cs[i] for i in range(N)], dtype=float)
    r, p = pearsonr(unsolved, solvedv)
    rs, ps = spearmanr(unsolved, solvedv)
    print(f"  unsolved counts: {unsolved.astype(int).tolist()}")
    print(f"  solved counts:   {solvedv.astype(int).tolist()}")
    print(f"  pearson r={r:.3f} p={p:.5f}; spearman r={rs:.3f} p={ps:.5f}")
    # line-FINAL too
    cuf = Counter(l[-1] for l in lns if l)
    csf = Counter(l[-1] for l in sol_lines if l)
    uf = np.array([cuf[i] for i in range(N)], dtype=float)
    sf = np.array([csf[i] for i in range(N)], dtype=float)
    r, p = pearsonr(uf, sf)
    print(f"  line-final pearson r={r:.3f} p={p:.5f}")

    print("\n=== DOUBLET VALUE-LEVEL CONTEXT ===")
    dpos = [i for i in range(n - 1) if cipher[i] == cipher[i + 1]]
    print(f"  doublets: {len(dpos)}")
    ident = Counter(int(cipher[i]) for i in dpos)
    counts = [ident[i] for i in range(N)]
    exp = len(dpos) / N
    stat = sum((c - exp) ** 2 / exp for c in counts)
    print(f"  doubled-rune identity: chi2={stat:.1f} p={chi2_dist.sf(stat, N-1):.4f}")
    print(f"  counts: {counts}")
    # C[i+2]-C[i] and C[i-1]-C[i] at doublets
    after = [(int(cipher[i + 2]) - int(cipher[i])) % N for i in dpos if i + 2 < n]
    before = [(int(cipher[i - 1]) - int(cipher[i])) % N for i in dpos if i > 0]
    for name, vals in (("delta after doublet", after), ("delta before doublet", before)):
        c = Counter(vals)
        counts = [c[i] for i in range(N)]
        m = len(vals)
        stat = sum((x - m / N) ** 2 / (m / N) for x in counts)
        print(f"  {name}: n={m} chi2={stat:.1f} p={chi2_dist.sf(stat, N-1):.4f} "
              f"(note 0 suppressed by no-triplet)")
    # doublet position mod 29, mod 7
    for mod in (7, 29):
        c = Counter(i % mod for i in dpos)
        counts = [c[i] for i in range(mod)]
        m = len(dpos)
        stat = sum((x - m / mod) ** 2 / (m / mod) for x in counts)
        print(f"  doublet positions mod {mod}: chi2={stat:.1f} "
              f"p={chi2_dist.sf(stat, mod-1):.4f}")

    print("\n=== DIGRAPHIC/TRIGRAPHIC KAPPA AT ALL SHIFTS ===")
    arr = cipher
    big = arr[:-1] * N + arr[1:]
    tri = arr[:-2] * N * N + arr[1:-1] * N + arr[2:]
    for name, seq, alpha in (("digraphic", big, N * N), ("trigraphic", tri, N**3)):
        zs = []
        worst = []
        for s in range(2, len(seq) // 2):
            m = len(seq) - s
            hits = int(np.count_nonzero(seq[:-s] == seq[s:]))
            exp = m / alpha
            sd = math.sqrt(m * (1 / alpha) * (1 - 1 / alpha))
            z = (hits - exp) / sd
            zs.append(z)
            worst.append((abs(z), s, hits, exp))
        zs = np.array(zs)
        worst.sort(reverse=True)
        print(f"  {name}: {len(zs)} shifts, mean z={zs.mean():+.3f} sd={zs.std():.3f}, "
              f"expected max ~{math.sqrt(2*math.log(len(zs))):.1f}")
        for absz, s, hits, exp in worst[:4]:
            print(f"    shift {s}: hits={hits} exp={exp:.1f} z={(hits-exp)/math.sqrt(exp):+.2f}")

    print("\n=== SENTENCE / WORD STRUCTURE (consistent conventions) ===")
    # Both the solved prefix and the unsolved section wrap words across line
    # breaks (bare '/' mid-word). Compare both texts under the SAME
    # convention. merge_lines=True joins line-wrapped words ('/' ignored);
    # False treats '/' as a word boundary.
    u_raw = open("data/page0-58.txt").read()
    u_cipher = u_raw[: u_raw.rfind("$")]  # drop the plaintext parable

    def word_lengths(text: str, *, merge_lines: bool) -> list[int]:
        seps_ = "-.%&$" + ("" if merge_lines else "/")
        out: list[int] = []
        cur = 0
        for ch in text:
            if ch in RUNESET:
                cur += 1
            elif ch in seps_:
                if cur:
                    out.append(cur)
                cur = 0
        if cur:
            out.append(cur)
        return out

    def sentence_lengths(text: str) -> list[int]:
        """Sentence lengths in (line-merged) words."""
        out: list[int] = []
        nw = 0
        cur = 0
        for ch in text:
            if ch in RUNESET:
                cur = 1
            elif ch in "-%&$":
                if cur:
                    nw += 1
                cur = 0
            elif ch == ".":
                if cur:
                    nw += 1
                cur = 0
                if nw:
                    out.append(nw)
                nw = 0
        if cur:
            nw += 1
        if nw:
            out.append(nw)
        return out

    for merge in (True, False):
        uw = word_lengths(u_cipher, merge_lines=merge)
        sw = word_lengths(solved, merge_lines=merge)
        ks, p = ks_2samp(uw, sw)
        print(f"  words (merge_lines={merge}): unsolved n={len(uw)} "
              f"mean={np.mean(uw):.2f} | solved n={len(sw)} "
              f"mean={np.mean(sw):.2f} | KS D={ks:.3f} p={p:.2e}")
    su = sentence_lengths(u_cipher)
    ss = sentence_lengths(solved)
    ks, p = ks_2samp(su, ss)
    print(f"  sentences: unsolved n={len(su)} mean={np.mean(su):.1f} "
          f"median={np.median(su)} | solved n={len(ss)} mean={np.mean(ss):.1f} "
          f"median={np.median(ss)} | KS D={ks:.3f} p={p:.2e}")


if __name__ == "__main__":
    main()
