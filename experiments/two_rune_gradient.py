#!/usr/bin/env python3
# ABOUTME: Validates the 2-rune-word log-likelihood objective as a hill-climb
# ABOUTME: gradient for the walk key, on simulated ciphertext with a known key.
"""Does the 2-rune word class give a usable fitness gradient?

The walk's attack barrier is that n-gram fitness stays flat until the key
is nearly correct. The 2-rune words offer a sharper objective: in
runeglish THE is `ᚦᛖ`, and the class is dominated by eight function
words (69% of tokens), so decrypting the 465 two-rune words under a
candidate key and scoring them against the register distribution should
reward partial correctness — a transposition error in base_0 corrupts
only 2 of 29 rune images, so most words still decrypt.

Validation on SIMULATED ciphertext with a known key (the honest order:
if the objective cannot recover a key we planted, it cannot recover a
real one):

  Stage 1: g and sigma known, recover base_0 by hill-climb from random.
  Stage 2: sigma known, recover base_0 and g.
  Stage 3: nothing known.

Reports recovered-vs-true agreement and the plaintext recovery rate, and
prints the score gap between the true key and random keys — the quantity
that decides whether a gradient exists at all.
"""

from __future__ import annotations

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
from lp_corpus import load_clean  # noqa: E402

M = 29


def compose(a, b):
    return [a[b[x]] for x in range(M)]


def inverse(p):
    q = [0] * M
    for i, v in enumerate(p):
        q[v] = i
    return q


def rand_order5(rng):
    pts = list(range(M))
    rng.shuffle(pts)
    g = list(range(M))
    for c in range(5):
        cy = pts[c * 5 : (c + 1) * 5]
        for i in range(5):
            g[cy[i]] = cy[(i + 1) % 5]
    return g


def conjugate(p, a, b):
    t = list(range(M))
    t[a], t[b] = b, a
    return [t[p[t[x]]] for x in range(M)]


def bases(base0, g, sigma, lens):
    """Per-word base permutations."""
    gp = [list(range(M))]
    for _ in range(4):
        gp.append(compose(g, gp[-1]))
    out, base = [], base0[:]
    for L in lens:
        out.append(base)
        base = compose(base, compose(gp[(L - 1) % 5], sigma))
    return out


def encrypt(words, base0, g, sigma):
    gp = [list(range(M))]
    for _ in range(4):
        gp.append(compose(g, gp[-1]))
    out, base = [], base0[:]
    for w in words:
        out.append([base[gp[j % 5][p]] for j, p in enumerate(w)])
        base = compose(base, compose(gp[(len(w) - 1) % 5], sigma))
    return out


def score(cipher2, idx2, base0, g, sigma, lens, table, floor):
    """Sum of log P_register over the decrypted 2-rune words."""
    bs = bases(base0, g, sigma, lens)
    ginv = inverse(g)
    total = 0.0
    for k, i in enumerate(idx2):
        binv = inverse(bs[i])
        c0, c1 = cipher2[k]
        p0 = binv[c0]
        p1 = ginv[binv[c1]]
        total += table.get((p0, p1), floor)
    return total


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    lens = [len(d[k]) for k in sorted(d)]

    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    pools: dict[int, list[list[int]]] = {}
    two_counts: Counter = Counter()
    for w in prose_words(prose_path):
        r = [IDX_ENG[t] for t in to_runeglish(w)]
        if not r:
            continue
        pools.setdefault(len(r), []).append(r)
        if len(r) == 2:
            two_counts[(r[0], r[1])] += 1
    tot = sum(two_counts.values())
    table = {k: math.log(v / tot) for k, v in two_counts.items()}
    floor = math.log(0.2 / tot)
    print(
        f"register 2-rune vocabulary: {len(two_counts)} types, {tot} tokens; "
        f"top: {sorted(two_counts.values(), reverse=True)[:5]}"
    )

    # plaintext matched to the LP length structure
    plain = []
    for L in lens:
        LL = L
        while LL not in pools and max(pools) > LL:
            LL += 1
        plain.append(rng.choice(pools[LL])[:L])
    idx2 = [i for i, w in enumerate(plain) if len(w) == 2]
    print(f"simulated corpus: {len(plain)} words, {len(idx2)} of length 2")
    the = sum(1 for i in idx2 if tuple(plain[i]) == (IDX_ENG["TH"], IDX_ENG["E"]))
    print(f"  planted THE count: {the}")

    # true key
    g_true = rand_order5(rng)
    sigma_true = list(range(M))
    rng.shuffle(sigma_true)
    base_true = list(range(M))
    rng.shuffle(base_true)
    cipher = encrypt(plain, base_true, g_true, sigma_true)
    cipher2 = [tuple(cipher[i]) for i in idx2]

    true_score = score(cipher2, idx2, base_true, g_true, sigma_true, lens, table, floor)
    rnd_scores = []
    for _ in range(200):
        b = list(range(M))
        rng.shuffle(b)
        rnd_scores.append(
            score(cipher2, idx2, b, g_true, sigma_true, lens, table, floor)
        )
    mu = sum(rnd_scores) / len(rnd_scores)
    print(f"\nscore of TRUE key:   {true_score:10.1f}")
    print(f"score of random base_0: {mu:10.1f} (best of 200: {max(rnd_scores):.1f})")
    print(
        f"  gap = {true_score - mu:.1f} nats over {len(idx2)} words "
        f"({(true_score - mu) / len(idx2):.3f} per word)"
    )

    # Stage 1: recover base_0 with g, sigma known
    print("\nStage 1: hill-climb base_0 (g, sigma known)")
    best = list(range(M))
    rng.shuffle(best)
    bs_score = score(cipher2, idx2, best, g_true, sigma_true, lens, table, floor)
    for restart in range(8):
        cur = list(range(M))
        rng.shuffle(cur)
        cur_s = score(cipher2, idx2, cur, g_true, sigma_true, lens, table, floor)
        improved = True
        while improved:
            improved = False
            for a in range(M):
                for b in range(a + 1, M):
                    cand = cur[:]
                    cand[a], cand[b] = cand[b], cand[a]
                    s = score(
                        cipher2, idx2, cand, g_true, sigma_true, lens, table, floor
                    )
                    if s > cur_s + 1e-9:
                        cur, cur_s = cand, s
                        improved = True
        agree = sum(1 for x in range(M) if cur[x] == base_true[x])
        hits = 0
        bs = bases(cur, g_true, sigma_true, lens)
        ginv = inverse(g_true)
        for k, i in enumerate(idx2):
            binv = inverse(bs[i])
            c0, c1 = cipher2[k]
            if (binv[c0], ginv[binv[c1]]) == (IDX_ENG["TH"], IDX_ENG["E"]):
                hits += 1
        print(
            f"  restart {restart}: score {cur_s:9.1f} "
            f"(true {true_score:.1f})  base_0 agreement {agree:>2}/29  "
            f"THE decrypts {hits:>3} (planted {the})"
        )
        if cur_s > bs_score:
            best, bs_score = cur, cur_s
        if agree == M:
            print("  -> EXACT key recovery")
            break

    # Stages 2 and 3: unknown g (order-5 preserving moves) and/or sigma
    def anneal(fix_g, fix_sigma, iters=60000, label=""):
        b = list(range(M))
        rng.shuffle(b)
        g = g_true[:] if fix_g else rand_order5(rng)
        sg = sigma_true[:] if fix_sigma else list(range(M))
        if not fix_sigma:
            rng.shuffle(sg)
        cur = score(cipher2, idx2, b, g, sg, lens, table, floor)
        best_all = (cur, b[:], g[:], sg[:])
        T0, T1 = 40.0, 0.5
        for it in range(iters):
            T = T0 * (T1 / T0) ** (it / iters)
            which = rng.random()
            nb, ng, nsg = b, g, sg
            if which < 0.5 or (fix_g and fix_sigma):
                x, y = rng.sample(range(M), 2)
                nb = b[:]
                nb[x], nb[y] = nb[y], nb[x]
            elif which < 0.75 and not fix_g:
                x, y = rng.sample(range(M), 2)
                ng = conjugate(g, x, y)
            elif not fix_sigma:
                x, y = rng.sample(range(M), 2)
                nsg = sg[:]
                nsg[x], nsg[y] = nsg[y], nsg[x]
            else:
                x, y = rng.sample(range(M), 2)
                nb = b[:]
                nb[x], nb[y] = nb[y], nb[x]
            s = score(cipher2, idx2, nb, ng, nsg, lens, table, floor)
            if s > cur or rng.random() < math.exp((s - cur) / T):
                b, g, sg, cur = nb, ng, nsg, s
                if s > best_all[0]:
                    best_all = (s, b[:], g[:], sg[:])
        s, b, g, sg = best_all
        ab = sum(1 for x in range(M) if b[x] == base_true[x])
        ag = sum(1 for x in range(M) if g[x] == g_true[x])
        asg = sum(1 for x in range(M) if sg[x] == sigma_true[x])
        print(
            f"  {label}: score {s:9.1f} (true {true_score:.1f})  "
            f"base_0 {ab:>2}/29  g {ag:>2}/29  sigma {asg:>2}/29"
        )

    print("\nStage 2: anneal base_0 + g (sigma known)")
    anneal(fix_g=False, fix_sigma=True, label="run")
    print("\nStage 3: anneal base_0 + g + sigma (nothing known)")
    anneal(fix_g=False, fix_sigma=False, label="run")

    # Stage 4: the landscape probe. Stage 1 shows base_0 is easy GIVEN
    # (g, sigma), so the real question is whether score*(g, sigma) — the
    # score after fitting base_0 — has any gradient. If one transposition
    # in sigma already scores like a random key, no local search over
    # (g, sigma) can work and the attack must enumerate them instead.
    def fit_base(g, sg, restarts=2, sweeps=3):
        best = -1e18
        for _ in range(restarts):
            cur = list(range(M))
            rng.shuffle(cur)
            cs = score(cipher2, idx2, cur, g, sg, lens, table, floor)
            for _ in range(sweeps):
                imp = False
                for a in range(M):
                    for b in range(a + 1, M):
                        cand = cur[:]
                        cand[a], cand[b] = cand[b], cand[a]
                        v = score(cipher2, idx2, cand, g, sg, lens, table, floor)
                        if v > cs + 1e-9:
                            cur, cs, imp = cand, v, True
                if not imp:
                    break
            best = max(best, cs)
        return best

    def perturb(p, n):
        q = p[:]
        for _ in range(n):
            a, b = rng.sample(range(M), 2)
            q[a], q[b] = q[b], q[a]
        return q

    print("\nStage 4: landscape probe — score*(g,sigma) after fitting base_0")
    print(f"  true (g, sigma):            {fit_base(g_true, sigma_true):9.1f}")
    for n in (1, 2, 4):
        v = max(fit_base(g_true, perturb(sigma_true, n)) for _ in range(3))
        print(f"  sigma off by {n} swap(s):      {v:9.1f}")
    v = max(
        fit_base(conjugate(g_true, *rng.sample(range(M), 2)), sigma_true)
        for _ in range(3)
    )
    print(f"  g off by 1 conjugation:     {v:9.1f}")
    v = max(fit_base(rand_order5(rng), perturb(sigma_true, M)) for _ in range(3))
    print(f"  random (g, sigma):          {v:9.1f}")


if __name__ == "__main__":
    main()
