#!/usr/bin/env python3
"""Sentence-mark forensics + mismatch-tolerant repeat extension.

1. SENTENCE CHANNEL: '.' density per section; sentence-length shape
   (geometric = memoryless placement vs English hump); sentence-initial /
   sentence-final word lengths (English: initial words short THE/A/WE,
   final words long content words) — an authenticity probe at the
   sentence level, with the solved pages as register control.

2. NEAR-REPEATS: every prior repeat search demanded exactness. Any
   10-gram pair with <=1 mismatch must contain an exact 5-gram seed, and
   any 12-gram pair with <=2 mismatches an exact 4-gram seed. So extend
   ALL exact 4/5-gram repeat pairs with mismatch tolerance and report any
   that grow into long near-matches (expected under null: ~zero).

3. Repeat census on the doublet-DELETED stream (a doublet inside a
   repeated passage would have split it; deletion rejoins it).
"""

import math
from collections import Counter, defaultdict

import numpy as np

from anomaly_scan import parse
from aldegonde import c3301

N = 29
RUNESET = set("".join(c3301.CICADA_ALPHABET))


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    C = np.array(stream[:-nplain], dtype=np.int64)
    n = len(C)
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= n:
            cw.append(w)
        total += len(w)
    lens = [len(w) for w in cw]

    print("=== 1. SENTENCE CHANNEL ===")
    # '.' density per section (words per sentence mark)
    # walk seps to assign sentence marks to sections
    bounds = np.cumsum([len(s) for s in sections[:-1]])
    marks_per_sec = Counter()
    for i, sp in enumerate(seps[: n - 1]):
        if sp == "s":
            sec = int(np.searchsorted(bounds, i, side="right"))
            marks_per_sec[sec] += 1
    print("  '.' marks per section (runes/mark):")
    for si, s in enumerate(sections[:-1]):
        m = marks_per_sec.get(si, 0)
        rate = len(s) / m if m else float("inf")
        print(f"    section {si:2d}: {m:3d} marks, {len(s):5d} runes "
              f"({rate:.0f} runes/mark)" + ("  <- NO MARKS" if m == 0 and len(s) > 200 else ""))

    # sentence lengths in words (unsolved)
    slens = []
    curw = 0
    widx = 0
    runes_seen = 0
    wlen_iter = iter(lens)
    cur_rem = next(wlen_iter)
    for i in range(n - 1):
        # advance word position
        cur_rem -= 1
        if cur_rem == 0:
            curw += 1
            try:
                cur_rem = next(wlen_iter)
            except StopIteration:
                cur_rem = 10**9
        if seps[i] == "s":
            slens.append(curw)
            curw = 0
    slens = [x for x in slens if x > 0]
    arr = np.array(slens)
    print(f"\n  unsolved sentence lengths: n={len(arr)} mean={arr.mean():.1f} "
          f"median={np.median(arr):.0f} max={arr.max()}")
    # geometric fit: for geometric, mean ~ sd and mode = 1; English humped
    print(f"    sd={arr.std():.1f} (geometric predicts sd~mean), "
          f"share of 1-3 word sentences = {np.mean(arr <= 3):.2%} "
          f"(geometric with this mean predicts ~{1 - (1 - 1/arr.mean())**3:.2%})")

    # sentence-initial / final word lengths
    first_w = []
    last_w = []
    curw_list = []
    wi = 0
    pos = 0
    # rebuild word index per rune
    rune_word = []
    for i, L in enumerate(lens):
        rune_word.extend([i] * L)
    sent_start_word = 0
    for i in range(n - 1):
        if seps[i] == "s":
            wend = rune_word[i]
            wnext = rune_word[i + 1]
            last_w.append(lens[wend])
            first_w.append(lens[wnext])
    rng = np.random.default_rng(2)
    la = np.array(lens, float)

    def perm_z(vals, pop, reps=20000):
        vals = np.array(vals, float)
        obs = vals.mean()
        null = np.array([rng.choice(pop, size=len(vals), replace=False).mean()
                         for _ in range(reps)])
        return obs, (obs - null.mean()) / null.std()

    o, z = perm_z(first_w, la)
    print(f"\n  sentence-INITIAL word length: mean={o:.2f} "
          f"(overall {la.mean():.2f}) permutation z={z:+.2f}, n={len(first_w)}")
    o, z = perm_z(last_w, la)
    print(f"  sentence-FINAL   word length: mean={o:.2f} permutation z={z:+.2f}")
    fshort = np.mean(np.array(last_w) <= 2)
    print(f"  finals that are 1-2 runes: {100*fshort:.1f}% "
          f"(overall {100*np.mean(la <= 2):.1f}%)")
    print("  English predicts final >> overall (content words end sentences)")

    # solved-pages control
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
    sw = []
    cur = 0
    sfirst, slast = [], []
    words_s = []
    prev_break = "s"
    for ch in solved:
        if ch in RUNESET:
            cur += 1
        elif ch in "-.%&$":
            if cur:
                words_s.append((cur, prev_break == "s"))
                cur = 0
            prev_break = "s" if ch == "." else "w"
    if cur:
        words_s.append((cur, prev_break == "s"))
    sol_lens = [L for L, _ in words_s]
    sol_first = [L for L, isf in words_s if isf]
    # final = word before a '.' : recompute
    sol_final = []
    cur = 0
    pend = None
    for ch in solved:
        if ch in RUNESET:
            cur += 1
        elif ch in "-.%&$":
            if cur:
                pend = cur
                cur = 0
            if ch == "." and pend:
                sol_final.append(pend)
    sa = np.array(sol_lens, float)
    o, z = perm_z(sol_final, sa)
    print(f"  SOLVED control: final mean={o:.2f} (overall {sa.mean():.2f}) "
          f"permutation z={z:+.2f}, n={len(sol_final)}; finals 1-2 runes: "
          f"{100*np.mean(np.array(sol_final) <= 2):.1f}% "
          f"(overall {100*np.mean(sa <= 2):.1f}%)")
    eff_u = np.mean(last_w) - la.mean()
    eff_s = np.mean(sol_final) - sa.mean()
    se_u = la.std() / math.sqrt(len(last_w))
    se_s = sa.std() / math.sqrt(len(sol_final))
    zc = (eff_s - eff_u) / math.sqrt(se_u**2 + se_s**2)
    print(f"  CONTRAST (solved {eff_s:+.2f} vs unsolved {eff_u:+.2f}): "
          f"z={zc:+.2f} -> the '.' marks in the unsolved section do NOT "
          f"select English sentence-final words")

    print("\n=== 2. NEAR-REPEAT EXTENSION ===")
    def extend_with_mismatches(i, j, k_allowed):
        """Maximal window around seed allowing k mismatches total."""
        # expand greedily left and right
        left = 0
        right = 0
        mis = 0
        li, lj = i - 1, j - 1
        ri, rj = i, j
        # first count exact seed run to the right
        while ri < n and rj < n and C[ri] == C[rj]:
            ri += 1
            rj += 1
        while li >= 0 and lj >= 0 and C[li] == C[lj]:
            li -= 1
            lj -= 1
        length = ri - li - 1
        # now extend through mismatches
        while mis < k_allowed:
            # try right
            best = None
            if ri < n - 1 and rj < n - 1:
                e = 0
                while ri + 1 + e < n and rj + 1 + e < n and C[ri + 1 + e] == C[rj + 1 + e]:
                    e += 1
                best = ("R", e)
            if li > 0 and lj > 0:
                e = 0
                while li - 1 - e >= 0 and lj - 1 - e >= 0 and C[li - 1 - e] == C[lj - 1 - e]:
                    e += 1
                if best is None or e > best[1]:
                    best = ("L", e)
            if best is None or best[1] == 0:
                break
            mis += 1
            if best[0] == "R":
                ri += 1 + best[1]
                rj += 1 + best[1]
            else:
                li -= 1 + best[1]
                lj -= 1 + best[1]
            length = ri - li - 1
        return li + 1, lj + 1, length, mis

    seeds = defaultdict(list)
    for i in range(n - 4):
        seeds[tuple(C[i : i + 4])].append(i)
    found = {}
    for v in seeds.values():
        if len(v) < 2 or len(v) > 30:
            continue
        for a in range(len(v)):
            for b in range(a + 1, len(v)):
                i, j = v[a], v[b]
                i0, j0, L, mis = extend_with_mismatches(i, j, 2)
                if L >= 11:
                    key = (i0, j0)
                    if key not in found or found[key][0] < L:
                        found[key] = (L, mis)
    # null expectation for L>=11 with <=2 mismatches: ~C(n,2)*C(10,2)*p^9*q^2
    pairs = n * (n - 1) / 2
    exp11 = pairs * math.comb(10, 2) * (1 / N) ** 9 * (28 / 29) ** 2
    print(f"  near-repeats len>=11 with <=2 mismatches: {len(found)} "
          f"(rough null expectation ~{exp11:.2f})")
    for (i0, j0), (L, mis) in sorted(found.items(), key=lambda x: -x[1][0])[:8]:
        s1 = "".join(c3301.CICADA_ALPHABET[x] for x in C[i0 : i0 + L])
        s2 = "".join(c3301.CICADA_ALPHABET[x] for x in C[j0 : j0 + L])
        print(f"    {i0} & {j0} (d={j0-i0}) len={L} mis={mis}")
        print(f"      {s1}")
        print(f"      {s2}")

    print("\n=== 3. REPEATS ON DOUBLET-DELETED STREAM ===")
    keep = np.ones(n, dtype=bool)
    keep[1:][C[1:] == C[:-1]] = False
    D = C[keep]
    nd = len(D)
    for L in (6, 7):
        dd = defaultdict(int)
        for i in range(nd - L + 1):
            dd[tuple(D[i : i + L])] += 1
        npairs = sum(v * (v - 1) // 2 for v in dd.values())
        exp = (nd - L + 1) ** 2 / 2 / N**L
        print(f"  L={L}: {npairs} repeated pairs (exp~{exp:.2f})")
        if L == 7 and npairs:
            for k, v in dd.items():
                if v > 1:
                    print(f"    {''.join(c3301.CICADA_ALPHABET[x] for x in k)}")


if __name__ == "__main__":
    main()
