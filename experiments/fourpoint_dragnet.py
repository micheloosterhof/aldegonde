#!/usr/bin/env python3
# ABOUTME: Broad 4-point statistic dragnet over the LP corpus with a global
# ABOUTME: Monte Carlo that pays the full look-elsewhere tax.
"""4-point statistic dragnet with global Monte Carlo (look-elsewhere paid).

Motivation: the lag-5 pairing is a 4th-order correlation invisible to 1/2/3-
point tests. This asks whether OTHER 4-point templates hide structure, over
a 399-template family: P (two equal-lag coincidences s apart), V (one
position matching two others), X (cross-lag coincidences at adjacent
positions).

Result - negative, and it does NOT strengthen the lag-5 finding:
- The two strongest templates in the entire family are exactly the known
  lag-5 components, P(5,1) z=+3.47 and P(5,4) z=+3.21. No new template
  outranks them.
- But over 399 templates the global max-z of +3.47 is reached by the
  doublet-suppressed null in 17/40 trials (global p ~ 0.43). Paying the
  full look-elsewhere tax for this wider family, the lag-5 signal is NOT
  globally significant; the fairer 174-cell scan (p~0.033, fresh-look) was
  already the most favorable honest framing, and widening the search only
  dilutes it. The dragnet manufactured no artifact #4 - it found nothing
  the prior analysis had not already isolated.
- The strong NEGATIVE tail (X(3,2), X(8,7), X(11,10) at z~-3.9, obs~0) is
  the doublet-suppression artifact: X(L, L-1) algebraically requires
  c[i]==c[i+1], a doublet, so its count is ~0 by construction. Not new
  structure.
- A soft, non-rigorous observation (NOT a claim): the constant 5 recurs in
  several top templates (X(5,10), X(7,5), V(5,14), X(4,5)). This is exactly
  the kind of pattern the look-elsewhere correction exists to discount, and
  it does not survive it.

Conclusion: 4th-order structure is exhausted too. The corpus's only
statistically defensible departures from randomness remain doublet
suppression and the single lag-5 pairing - and the latter sits right at the
edge of significance, not beyond it."""

import random
from math import sqrt

import numpy as np

from aldegonde import c3301

AB = c3301.CICADA_ALPHABET
N = 29

with open("data/page0-58.txt") as f:
    raw = f.read()
parts = raw.split("%")
keep = [i for i, p in enumerate(parts) if any(c in AB for c in p)][:-2]
text = "".join(x for i in keep for x in parts[i] if x in AB)
n = len(text)
A0 = np.array([c3301.r2i(c) for c in text])

# ---- the 4-point family ----
# Family P (parallel): coincidence c[i]==c[i+L] AND c[i+s]==c[i+s+L]
#   two equal-lag matches s apart. (L in 2..20, s in 1..8)
# Family V (vee / shared vertex): c[i]==c[i+L] AND c[i]==c[i+L2]
#   one position equals two others. (L < L2, both 2..14)
# Family R (ABAB repeat): c[i]==c[i+p] AND c[i+1]==c[i+p+1] is just P with s=1;
#   add the genuine 4-gram repeat: c[i..i+1]==c[j..j+1] handled by P.
# Family X (cross-lag at a position): c[i]==c[i+L] AND c[i+1]==c[i+1+L2], L!=L2

def stat_P(a, L, s):
    M = a[:-L] == a[L:]
    return int(np.sum(M[:len(M) - s] & M[s:]))

def exp_P(L, s):
    m = n - L
    return (m - s) / (N * N)

def stat_V(a, L, L2):
    lim = n - L2
    return int(np.sum((a[:lim] == a[L:L + lim]) & (a[:lim] == a[L2:L2 + lim])))

def exp_V(L, L2):
    return (n - L2) / (N * N)

def stat_X(a, L, L2):
    lim = n - max(L, L2) - 1
    return int(np.sum((a[:lim] == a[L:L + lim]) &
                      (a[1:1 + lim] == a[1 + L2:1 + L2 + lim])))

def exp_X(L, L2):
    return (n - max(L, L2) - 1) / (N * N)

def all_stats(a):
    """Return dict label->(obs, exp, z) for the whole family."""
    out = {}
    for L in range(2, 21):
        for s in range(1, 9):
            o, e = stat_P(a, L, s), exp_P(L, s)
            out[("P", L, s)] = (o, e, (o - e) / sqrt(e))
    for L in range(2, 15):
        for L2 in range(L + 1, 16):
            o, e = stat_V(a, L, L2), exp_V(L, L2)
            out[("V", L, L2)] = (o, e, (o - e) / sqrt(e))
    for L in range(2, 15):
        for L2 in range(2, 15):
            if L == L2:
                continue
            o, e = stat_X(a, L, L2), exp_X(L, L2)
            out[("X", L, L2)] = (o, e, (o - e) / sqrt(e))
    return out

obs = all_stats(A0)
ntests = len(obs)
ranked = sorted(obs.items(), key=lambda kv: -kv[1][2])
print(f"4-point family: {ntests} templates")
print("top 12 by z:")
for lab, (o, e, z) in ranked[:12]:
    print(f"  {str(lab):16s}: obs {o:3d} exp {e:5.1f} z={z:+.2f}")
print("most negative 3:")
for lab, (o, e, z) in ranked[-3:]:
    print(f"  {str(lab):16s}: obs {o:3d} exp {e:5.1f} z={z:+.2f}")

# ---- global Monte Carlo: max |z| over the family under doublet-suppressed null ----
rate = sum(1 for i in range(n - 1) if text[i] == text[i + 1]) / (n - 1)

def gen():
    out = [random.randrange(N)]
    for _ in range(n - 1):
        if random.random() < rate:
            out.append(out[-1])
        else:
            c = random.randrange(N - 1)
            if c >= out[-1]:
                c += 1
            out.append(c)
    return np.array(out)

obs_maxz = ranked[0][1][2]
# the known lag-5 P-statistics, for reference
known = max(obs[("P", 5, 1)][2], obs[("P", 5, 4)][2])
TRIALS = 40
null_max = []
for _ in range(TRIALS):
    st = all_stats(gen())
    null_max.append(max(v[2] for v in st.values()))
null_max.sort()
exceed = sum(1 for v in null_max if v >= obs_maxz)
print(f"\nobserved family max z = {obs_maxz:.2f} ({ranked[0][0]})")
print(f"null max-z over family: median {null_max[TRIALS//2]:.2f}, "
      f"95th pct {null_max[int(TRIALS*0.95)]:.2f}")
print(f"global P(null max >= observed) = {exceed}/{TRIALS}")
print(f"(lag-5 reference: best P-stat z = {known:.2f})")
