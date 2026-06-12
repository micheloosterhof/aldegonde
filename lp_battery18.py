#!/usr/bin/env python3
"""Battery 18: i.i.d. uniform runes vs no-zero-step random walk -- which is the LP?

Model IID : c[i] i.i.d. uniform on 29 symbols.
Model WALK: c[i+1] uniform over the 28 symbols != c[i]  (equivalently a random
            walk with uniform nonzero steps), with a 19% lapse rate so that
            doublets appear at the observed 0.66%.

Analytics: lag-k coincidence of WALK = 1/29 + (28/29) * q^k, where q is the
step charactistic coefficient: q = P(step=0) - (1-P(step=0))/28.
IID: 1/29 at every lag. Only lag 1 (huge) and lag 2 (tiny) differ measurably.
"""
import collections
import math
import random
import numpy as np
from lp_structure import parse, flat, N

pages = parse("data/page0-58.txt")[:55]
s = np.array(flat(pages))
n = len(s)

obs = {}
for k in (1, 2, 3, 4):
    obs[k] = int((s[:-k] == s[k:]).sum())

p0 = obs[1] / (n - 1)            # observed doublet rate 0.66%
q = p0 - (1 - p0) / 28           # step char coefficient of lapse-walk
print(f"n={n}, observed doublet rate {p0*100:.2f}%, walk q={q:+.5f}")
print(f"\n{'lag':>3s} {'observed':>9s} {'IID exp':>9s} {'WALK exp':>9s} {'sd':>6s} {'z(IID)':>7s} {'z(WALK)':>7s}")
for k in (1, 2, 3, 4):
    m = n - k
    e_iid = m / N
    p_walk = 1 / N + (28 / N) * (q ** k)
    e_walk = m * p_walk
    sd = math.sqrt(m * (1 / N) * (1 - 1 / N))
    print(f"{k:3d} {obs[k]:9d} {e_iid:9.1f} {e_walk:9.1f} {sd:6.1f} "
          f"{(obs[k]-e_iid)/sd:+7.2f} {(obs[k]-e_walk)/sd:+7.2f}")

# Monte-Carlo check of the analytics + overall fit
random.seed(7)
def sim_iid():
    return np.random.randint(0, N, n)
LAPSE = p0 * N  # lapse draws uniform-29, so doublet rate = LAPSE/29 = p0
def sim_walk():
    out = np.empty(n, dtype=int)
    out[0] = random.randrange(N)
    for i in range(1, n):
        c = random.randrange(N)
        if random.random() >= LAPSE:  # rule applied: forbid repeat
            while c == out[i - 1]:
                c = random.randrange(N)
        out[i] = c
    return out

REP = 300
print("\nMonte-Carlo (300 reps each): lag-2 coincidence count")
for name, gen in (("IID", sim_iid), ("WALK+lapse", sim_walk)):
    v = []
    for _ in range(REP):
        c = gen()
        v.append(int((c[:-2] == c[2:]).sum()))
    v = np.array(v)
    print(f"{name:10s}: mean {v.mean():7.1f} sd {v.std():5.1f}   (LP observed: {obs[2]})")

# power statement
diff = (n - 2) * 28 / N * (q ** 2 - 0)
sd2 = math.sqrt((n - 2) * (1 / N) * (1 - 1 / N))
need = (3 * sd2 / abs(diff)) ** 2 * n if diff != 0 else float("inf")
print(f"\nlag-2 separation between models: {abs(diff):.1f} counts vs noise sd {sd2:.1f}"
      f" -> {abs(diff)/sd2:.2f} sigma at n={n}")
print(f"corpus size needed for a 3-sigma lag-2 verdict: ~{int(need):,} runes "
      f"({need/n:.0f}x the LP)")
