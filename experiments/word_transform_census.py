#!/usr/bin/env python3
"""Word-level transform-pair census.

If the cipher operates per word with a varying per-word key, repeated
plaintext words appear as TRANSFORMED pairs of cipher words rather than
identical ones:

- per-word Caesar shift      -> word2 = word1 + c        (equal delta seqs)
- per-word Beaufort          -> word2 = c - word1        (negated deltas)
- per-word affine            -> word2 = m*word1 + c      (scaled deltas)
- per-word reversal (+shift) -> word2 = rev(word1) + c
- per-word transposition     -> word2 = anagram of word1
- per-word rotation          -> word2 = cyclic shift of word1

For each word length, count observed pairs in each class and compare with
the exact uniform-random expectation. English text repeats words heavily
(THE ~5% of tokens), so any per-word-keyed cipher inflates its class far
above baseline.
"""

import math
from collections import Counter, defaultdict

import numpy as np

from anomaly_scan import parse

N = 29


def pairs_count(counter: Counter) -> int:
    return sum(v * (v - 1) // 2 for v in counter.values())


def cross_count(c1: Counter, c2: Counter, same: bool) -> int:
    """Pairs (x from c1, y from c2) with matching keys; if same=True the
    counters index the same words and unordered pairs are wanted."""
    tot = 0
    for k, v in c1.items():
        if k in c2:
            tot += v * c2[k]
    return tot // 2 if same else tot


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    n = len(stream) - nplain
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= n:
            cw.append(tuple(w))
        total += len(w)

    inv = [0] * N
    for a in range(1, N):
        for b in range(1, N):
            if (a * b) % N == 1:
                inv[a] = b

    rng = np.random.default_rng(2)
    bylen = defaultdict(list)
    for w in cw:
        bylen[len(w)].append(w)

    print(f"{len(cw)} cipher words")
    print(f"{'L':>2} {'n':>4} | {'class':<16} {'obs':>5} {'exp':>8} {'z':>6}")
    grand = defaultdict(lambda: [0, 0.0])
    for L in sorted(bylen):
        ws = bylen[L]
        m = len(ws)
        if m < 30 or L < 3:
            continue
        npairs = m * (m - 1) // 2

        deltas = Counter(tuple((w[i + 1] - w[i]) % N for i in range(L - 1)) for w in ws)
        ident = Counter(ws)

        obs_ident = pairs_count(ident)
        obs_deltaclass = pairs_count(deltas)
        obs_shift = obs_deltaclass - obs_ident

        negdeltas = Counter(
            tuple((-(w[i + 1] - w[i])) % N for i in range(L - 1)) for w in ws
        )
        obs_beaufort = cross_count(deltas, negdeltas, same=True)

        # affine: normalize delta seq by inverse of first nonzero delta
        def affsig(w):
            d = [(w[i + 1] - w[i]) % N for i in range(L - 1)]
            nz = next((x for x in d if x), None)
            if nz is None:
                return None
            mlt = inv[nz]
            return tuple((mlt * x) % N for x in d)

        affs = Counter(s for s in (affsig(w) for w in ws) if s is not None)
        obs_affclass = pairs_count(affs)

        revshift = Counter(
            tuple((-(w[L - 1 - i] - w[L - 2 - i])) % N for i in range(L - 1))
            for w in ws
        )
        obs_revshift = cross_count(deltas, revshift, same=True)

        anag = Counter(tuple(sorted(w)) for w in ws)
        obs_anag = pairs_count(anag) - obs_ident

        rots = Counter()
        for w in ws:
            canon = min(tuple(w[i:] + w[:i]) for i in range(L))
            rots[canon] += 1
        obs_rot = pairs_count(rots) - obs_ident

        # expectations under uniform-random words
        e_ident = npairs / N**L
        e_shift = npairs * 28 / N**L
        e_beaufort = npairs * 29 / N**L
        e_affclass = npairs * (29 * 28) / N**L
        e_revshift = npairs * 29 / N**L
        e_rot = npairs * (L - 1) / N**L
        # anagram: E[#permutations of a random multiset]/29^L via sampling
        samp = rng.integers(0, N, size=(4000, L))
        perms = []
        for row in samp:
            c = Counter(row.tolist())
            p_ = math.factorial(L)
            for v in c.values():
                p_ //= math.factorial(v)
            perms.append(p_)
        e_anag = npairs * (np.mean(perms) - 29**L / 29**L * 0) / N**L - e_ident
        e_anag = max(e_anag, 1e-9)

        rows = [
            ("identity", obs_ident, e_ident),
            ("shift (c!=0)", obs_shift, e_shift),
            ("beaufort", obs_beaufort, e_beaufort),
            ("affine class", obs_affclass, e_affclass),
            ("reversal+shift", obs_revshift, e_revshift),
            ("rotation", obs_rot, e_rot),
            ("anagram", obs_anag, e_anag),
        ]
        for name, o, e in rows:
            z = (o - e) / math.sqrt(e) if e > 0 else float("nan")
            flag = " ***" if abs(z) > 4 and e >= 0.5 else ""
            print(f"{L:>2} {m:>4} | {name:<16} {o:>5} {e:>8.2f} {z:>+6.2f}{flag}")
            grand[name][0] += o
            grand[name][1] += e
        print()

    print("TOTALS (all lengths, analytic uniform null — biased for the")
    print("delta-matching classes by doublet suppression, see below):")
    for name, (o, e) in grand.items():
        z = (o - e) / math.sqrt(e) if e > 0 else float("nan")
        flag = " ***" if abs(z) > 4 else (" *" if abs(z) > 3 else "")
        print(f"  {name:<16} obs={o:>6} exp={e:>9.2f} z={z:+.2f}{flag}")

    # Doublet-corrected Monte Carlo null. The suppressed delta-zero
    # probability inflates every delta-matching class by ~2.3% per rune,
    # enough to fake 4-5 sigma signals against the analytic null above.
    print("\nTOTALS (doublet-corrected Markov MC null, 80 samples):")
    lens = [len(w) for w in cw]
    ntot = sum(lens)

    def totals(wordlist):
        byl = defaultdict(list)
        for w in wordlist:
            byl[len(w)].append(w)
        out = Counter()
        for L, ws in byl.items():
            if len(ws) < 30 or L < 3:
                continue
            deltas = Counter(
                tuple((w[i + 1] - w[i]) % N for i in range(L - 1)) for w in ws
            )
            ident = Counter(ws)
            out["identity"] += pairs_count(ident)
            out["shift (c!=0)"] += pairs_count(deltas) - pairs_count(ident)
            negd = Counter(
                tuple((-(w[i + 1] - w[i])) % N for i in range(L - 1)) for w in ws
            )
            out["beaufort"] += cross_count(deltas, negd, same=True)

            def affsig(w):
                d = [(w[i + 1] - w[i]) % N for i in range(L - 1)]
                nz = next((x for x in d if x), None)
                if nz is None:
                    return None
                mlt = inv[nz]
                return tuple((mlt * x) % N for x in d)

            affs = Counter(s for s in (affsig(w) for w in ws) if s is not None)
            out["affine class"] += pairs_count(affs)
            revs = Counter(
                tuple((-(w[L - 1 - i] - w[L - 2 - i])) % N for i in range(L - 1))
                for w in ws
            )
            out["reversal+shift"] += cross_count(deltas, revs, same=True)
            anag = Counter(tuple(sorted(w)) for w in ws)
            out["anagram"] += pairs_count(anag) - pairs_count(ident)
            rots = Counter(
                min(tuple(w[i:] + w[:i]) for i in range(L)) for w in ws
            )
            out["rotation"] += pairs_count(rots) - pairs_count(ident)
        return out

    obs_tot = totals(cw)
    p_dd = 0.00675
    acc = defaultdict(list)
    for _ in range(80):
        out_ = np.empty(ntot, dtype=np.int64)
        out_[0] = rng.integers(0, N)
        same = rng.random(ntot) < p_dd
        jump = rng.integers(0, N - 1, ntot)
        for i in range(1, ntot):
            out_[i] = (
                out_[i - 1]
                if same[i]
                else (jump[i] if jump[i] < out_[i - 1] else jump[i] + 1)
            )
        sim = []
        k = 0
        for L in lens:
            sim.append(tuple(int(x) for x in out_[k : k + L]))
            k += L
        t = totals(sim)
        for key in obs_tot:
            acc[key].append(t[key])
    for key in obs_tot:
        a = np.array(acc[key])
        z = (obs_tot[key] - a.mean()) / a.std() if a.std() > 0 else float("nan")
        flag = " ***" if abs(z) > 4 else (" *" if abs(z) > 3 else "")
        print(f"  {key:<16} obs={obs_tot[key]:>6} null={a.mean():>9.1f}±{a.std():<6.1f} "
              f"z={z:+.2f}{flag}")


if __name__ == "__main__":
    main()
