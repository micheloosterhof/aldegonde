#!/usr/bin/env python3
"""Word-lattice probes.

1. LENGTH-CONTEXT KEYED CIPHER TEST: if the keystream is a function of the
   local word-length pattern (own word length, position in word, neighbor
   word lengths), then runes sharing a context bucket share key, and their
   pairwise ciphertext coincidence rate rises from 1/29 toward the
   plaintext IoC (~0.06+). Motivated by the DJU-BEI repeat, whose length
   context (2, [3,3], 2) matches at both occurrences.

2. BOUNDARY AUTHENTICITY: real English word-length sequences carry
   sequential structure (short function words alternate with content
   words). Compare lag correlations / mutual information of the length
   sequence in the unsolved cipher vs the solved pages vs shuffled
   controls. A structureless cipher length-sequence would mean the
   boundaries are synthetic.

3. Doublet-containing word lengths vs the EA-lexicon expectation.
"""

import math
from collections import Counter, defaultdict

import numpy as np
from scipy.stats import chi2_contingency

from anomaly_scan import parse
from aldegonde import c3301

N = 29
RUNESET = set("".join(c3301.CICADA_ALPHABET))


def bucket_kappa(runes_with_keys):
    """Total within-bucket pairwise coincidence rate."""
    buckets = defaultdict(list)
    for key, r in runes_with_keys:
        buckets[key].append(r)
    hits = 0
    opp = 0
    for vals in buckets.values():
        m = len(vals)
        if m < 2:
            continue
        c = Counter(vals)
        hits += sum(v * (v - 1) // 2 for v in c.values())
        opp += m * (m - 1) // 2
    if opp == 0:
        return 0.0, 0.0, 0
    rate = hits / opp
    sd = math.sqrt((1 / N) * (1 - 1 / N) / opp)
    z = (rate - 1 / N) / sd
    return rate, z, opp


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    n = len(stream) - nplain
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= n:
            cw.append(w)
        total += len(w)
    lens = [len(w) for w in cw]
    nw = len(cw)
    print(f"{nw} cipher words, {sum(lens)} runes")

    print("\n=== 1. LENGTH-CONTEXT KEYED CIPHER TEST ===")
    cap = 9  # cap lengths to keep buckets populated
    schemes = {
        "(pos,wlen)": lambda i, j: (j, min(lens[i], cap)),
        "(pos,wlen,prev)": lambda i, j: (
            j, min(lens[i], cap), min(lens[i - 1], cap) if i > 0 else -1),
        "(pos,wlen,next)": lambda i, j: (
            j, min(lens[i], cap),
            min(lens[i + 1], cap) if i < nw - 1 else -1),
        "(pos,wlen,prev,next)": lambda i, j: (
            j, min(lens[i], cap),
            min(lens[i - 1], cap) if i > 0 else -1,
            min(lens[i + 1], cap) if i < nw - 1 else -1),
        "(pos,wlen,prev,prev2)": lambda i, j: (
            j, min(lens[i], cap),
            min(lens[i - 1], cap) if i > 0 else -1,
            min(lens[i - 2], cap) if i > 1 else -1),
    }
    for name, fkey in schemes.items():
        rk = []
        for i, w in enumerate(cw):
            for j, r in enumerate(w):
                rk.append((fkey(i, j), r))
        rate, z, opp = bucket_kappa(rk)
        flag = " ***" if abs(z) > 4 else ""
        print(f"  {name:<24} rate={rate:.5f} (1/29={1/N:.5f}) "
              f"pairs={opp} z={z:+.2f}{flag}")
    print("  (a length-keyed cipher would push rate toward ~0.06+)")

    print("\n=== 2. BOUNDARY AUTHENTICITY: length-sequence structure ===")
    # solved pages word lengths (merged convention)
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
    sl = []
    cur = 0
    for ch in solved:
        if ch in RUNESET:
            cur += 1
        elif ch in "-.%&$":
            if cur:
                sl.append(cur)
            cur = 0
    if cur:
        sl.append(cur)

    def perm_test(seq, lag, reps=4000, seed=1):
        s = np.array(seq, float)
        m = len(s)
        x = s - s.mean()
        obs = float(np.dot(x[:-lag], x[lag:]) / np.dot(x, x))
        rng = np.random.default_rng(seed)
        null = np.empty(reps)
        for k in range(reps):
            p = rng.permutation(s)
            xx = p - p.mean()
            null[k] = np.dot(xx[:-lag], xx[lag:]) / np.dot(xx, xx)
        return obs, (obs - null.mean()) / null.std()

    def lag_stats(seq, label):
        out = []
        for lag in (1, 2, 3):
            r, z = perm_test(seq, lag)
            out.append(f"lag{lag} r={r:+.3f} z={z:+.2f}")
        print(f"  {label} (n={len(seq)}): " + "; ".join(out))

    # English register references (natural prose word lengths) for context:
    # English word-length autocorrelation is register-dependent and can be
    # either sign, so it does NOT give a one-sided test.
    import glob
    import re
    eng = ""
    for f in glob.glob("hypotheses/*.md"):
        eng += open(f).read()
    eng_lens = [len(t) for t in re.findall(r"[A-Za-z]+", eng)]

    lag_stats(lens, "unsolved cipher  ")
    lag_stats(sl, "solved LP pages  ")
    lag_stats(eng_lens, "English prose ref")
    print("  NOTE: solved LP pages are negative, generic English prose is")
    print("  positive — English autocorrelation is register-dependent, so")
    print("  the unsolved ~0 cannot by itself prove synthetic boundaries.")
    # register-matched difference: solved LP vs unsolved (same author/work)
    r_u, _ = perm_test(lens, 1)
    r_s, _ = perm_test(sl, 1)
    sd_diff = math.sqrt(1 / len(lens) + 1 / len(sl))
    print(f"  register-matched lag-1 diff (solved {r_s:+.3f} vs unsolved "
          f"{r_u:+.3f}): z={(r_s - r_u) / sd_diff:+.2f}")

    # fraction of 1-2 rune words adjacent to other 1-2 rune words
    def short_adj(seq):
        s = [x <= 2 for x in seq]
        both = sum(1 for a, b in zip(s[:-1], s[1:]) if a and b)
        p = np.mean(s)
        exp = (len(s) - 1) * p * p
        sd = math.sqrt(exp * (1 - p * p))
        return both, exp, (both - exp) / sd
    for seq, label in ((lens, "unsolved"), (sl, "solved")):
        b, e, z = short_adj(seq)
        print(f"  {label}: adjacent short-short words {b} vs {e:.0f} exp "
              f"(z={z:+.2f})")

    print("\n=== 3. DOUBLET WORD LENGTHS ===")
    # word length distribution of doublet-containing words
    cipher = [r for w in cw for r in w]
    # map rune index -> word
    widx = []
    for i, w in enumerate(cw):
        widx.extend([i] * len(w))
    dwords = set()
    for i in range(len(cipher) - 1):
        if cipher[i] == cipher[i + 1] and widx[i] == widx[i + 1]:
            dwords.add(widx[i])
    dl = [min(lens[i], cap) for i in dwords]
    # baseline: probability a word of length L contains a doublet ~ (L-1)
    base = Counter()
    for L in lens:
        base[min(L, cap)] += (L - 1)
    tot = sum(base.values())
    obs = Counter(dl)
    print(f"  {len(dwords)} doublet-containing words")
    print(f"  {'len':>4} {'obs':>4} {'exp(opportunity)':>17}")
    for L in sorted(base):
        e = len(dwords) * base[L] / tot
        print(f"  {L:>4} {obs.get(L, 0):>4} {e:>17.1f}")


if __name__ == "__main__":
    main()
