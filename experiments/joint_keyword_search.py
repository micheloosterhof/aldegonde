#!/usr/bin/env python3
# ABOUTME: Joint enumeration of keyword-derived (g, sigma) candidates for the
# ABOUTME: Quagmire walk, through the cheap filters and the 2-rune verifier.
"""Enumerate the keyword key space and filter it.

`mixed-alphabet-vigenere.md` leaves both halves enumerable: ~12,064
keyword alphabets clear the within-word diagonal and ~130 keyword disks
are consistent with the 23 seam doublets. This walks the joint space
through filters in increasing cost order:

  1. JOINT doublet count. Within-word doublets come from the g schedule,
     seam doublets from sigma, and the two must sum to the observed 86:
     10,028*r_g + 2,927*r_sigma ~ 86 (Poisson sd 9.3). This is much
     tighter than either rate alone, because sigma's ~0.010 already
     spends ~29 of the 86.
  2. Parity: the DJU-BEI return needs sigma even.
  3. Base diversity: >= ~600 distinct bases over the real length
     sequence (`sigma-power-step.md`), which kills sigma too close to
     the g-family.
  4. DJU-BEI state return: base_1477 == base_2926 (full-return reading).
  5. Survivors go to the 2-rune word verifier, which recovers base_0 and
     scores the decryption (`no-known-plaintext-foothold.md`).
"""

from __future__ import annotations  # noqa: I001

import math
import random
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from ea_direction_test import PROSE_CACHE, prose_words  # noqa: E402
from keyword_exhaustion import DICT, alphabets, kw_runes  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from sigma_algebraic_floor import tables  # noqa: E402

M = 29
OBS_DOUBLETS = 86
N_WITHIN = 10028
N_SEAM = 2927
TOL = 2.0            # sigmas of Poisson slack on the joint doublet count


def compose(a, b):
    return [a[b[x]] for x in range(M)]


def inverse(p):
    q = [0] * M
    for i, v in enumerate(p):
        q[v] = i
    return q


def disk(K, delta):
    pos = inverse(K)
    return [K[(pos[x] + delta) % M] for x in range(M)]


def parity_even(p):
    seen = [False] * M
    swaps = 0
    for i in range(M):
        if seen[i]:
            continue
        L = 0
        j = i
        while not seen[j]:
            seen[j] = True
            j = p[j]
            L += 1
        swaps += L - 1
    return swaps % 2 == 0


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    words = [d[k] for k in sorted(d)]
    lens = [len(w) for w in words]
    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    pools: dict[int, list[list[int]]] = {}
    for w in prose_words(prose_path):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if r:
            pools.setdefault(len(r), []).append(r)
    cross, within = tables(lens, pools, rng)

    ph = Counter()
    for w in words:
        for j in range(1, len(w)):
            ph[j % 5] += 1
    tot = sum(ph.values())
    [ph[p] / tot for p in range(5)]

    vocab = [x.strip() for x in Path(DICT).read_text().splitlines()
             if 4 <= len(x.strip()) <= 12 and x.strip().isalpha()
             and x.strip().isascii()]
    print(f"vocabulary {len(vocab):,} words x 4 rules")

    # ---- sigma candidates: keyword disks consistent with 23 seam doublets
    sig = []
    for word in vocab:
        seq = kw_runes(word)
        if not seq:
            continue
        for rname, K in alphabets(seq):
            pos = inverse(K)
            for dl in range(1, M):
                p = [K[(pos[x] + dl) % M] for x in range(M)]
                r = sum(cross[p[y]][y] for y in range(M))
                if r <= 0.0118 and parity_even(p):
                    sig.append((r, word, rname, dl, p))
    sig.sort(key=lambda t: t[0])
    print(f"sigma candidates (cross-word <= 0.0118, even parity): {len(sig):,}")

    # ---- g candidates: keyword alphabets with a schedule in the band
    #      the JOINT constraint fixes what r_g must be, given r_sigma
    gcand = []
    for word in vocab:
        seq = kw_runes(word)
        if not seq:
            continue
        for rname, K in alphabets(seq):
            pos = inverse(K)
            costs = [sum(within[K[(pos[x] + t) % M]][x] for x in range(M))
                     for t in range(M)]
            if min(costs[1:]) > 0.0063:
                continue
            gcand.append((min(costs[1:]), word, rname, K, costs))
    gcand.sort(key=lambda t: t[0])
    print(f"g candidates (within-word floor <= 0.0063): {len(gcand):,}")

    # ---- joint doublet filter
    #
    # r_g is the alphabet's FLOOR: the cheapest non-identity turn. A real
    # schedule picks five offsets summing to 0 (mod 29), so it can only
    # cost MORE than that floor, never less. The filter is therefore
    # one-sided -- reject a pair only when its cheapest possible joint
    # total already overshoots the observed count. A pair sitting far
    # below the window is not excluded; it simply needs a dearer schedule.
    sd = math.sqrt(OBS_DOUBLETS)
    hi = OBS_DOUBLETS + TOL * sd
    print(f"\njoint filter: min achievable 10028*r_g + 2927*r_sigma <= {hi:.0f}")
    n_sig = min(len(sig), 400)
    if n_sig < len(sig):
        print(f"  NOTE: sigma list capped at {n_sig:,} of {len(sig):,}")
    pairs = 0
    viable = []
    for r_s, sw, sr, sdl, _sp in sig[:n_sig]:
        need = (OBS_DOUBLETS - N_SEAM * r_s) / N_WITHIN
        if need <= 0:
            continue
        for r_g, gw, gr, _K, _costs in gcand:
            pairs += 1
            tot_d = N_WITHIN * r_g + N_SEAM * r_s
            if tot_d <= hi:
                viable.append((tot_d, gw, gr, sw, sr, sdl, r_g, r_s))
    print(f"  pairs examined: {pairs:,}")
    print(f"  passing the joint doublet count: {len(viable):,}")
    if viable:
        viable.sort(key=lambda t: abs(t[0] - OBS_DOUBLETS))
        print(f"\n  {'total':>7} {'g keyword':<16}{'sigma keyword':<16}"
              f"{'r_g':>8}{'r_sig':>8}")
        for v in viable[:10]:
            print(f"  {v[0]:>7.1f} {v[1]:<16}{v[3]:<16}{v[6]:>8.4f}{v[7]:>8.4f}")
        need_lo = (OBS_DOUBLETS - N_SEAM * sig[0][0]) / N_WITHIN
        print(f"\n  with the best sigma (r={sig[0][0]:.4f}, {sig[0][1]}), the "
              f"g schedule must supply r_g = {need_lo:.4f}")


if __name__ == "__main__":
    main()
