#!/usr/bin/env python3
# ABOUTME: Family-blind re-assessment of the lag-5 observation: cluster
# ABOUTME: decomposition, locality, fair 2D (lag x separation) scan, deltas.
"""Fresh look at the lag-5 observation: clusters, locality, fair 2D scan.

Re-examines the lag-5 paired-match anomaly without the hand-picked {1, L-1}
pattern family. Findings (recorded in lag5-digraph-structure.md):

- The top two cells of the full 174-cell (L=2..30, d=1..6) pair-count grid
  are (5,1)=29 and (5,4)=28, both at lag 5; the family-blind Monte Carlo
  probability that any single lag carries two cells jointly >= (29,28) is
  ~0.033 — the fairest global significance, weaker than the family-chosen
  p ~= 0.01.
- Cluster decomposition: the excess is ~20 isolated two-match objects at
  separations 1 or 4 plus one size-6 cluster (page 50); three-clusters are
  at chance; removing the page-50 cluster leaves d1=27/d4=26.
- The signal is corpus-wide (z=+3.67 without section 4).
- The lag-5 delta histogram is otherwise uniform; delta=0 ties with
  delta=23. Only the pairing is anomalous.
"""

import random
from collections import Counter
from math import sqrt

from aldegonde import c3301

AB = c3301.CICADA_ALPHABET
ENG = c3301.CICADA_ENGLISH_ALPHABET
N = 29
r2i = c3301.r2i

with open("data/page0-58.txt") as f:
    raw = f.read()
parts = raw.split("%")
keep = [i for i, p in enumerate(parts) if any(c in AB for c in p)][:-2]
text = "".join(x for i in keep for x in parts[i] if x in AB)
n = len(text)
sections = [s for s in ("".join(x for x in t if x in AB)
                        for t in raw.split("$")[:10]) if s]
sec_bounds = []
acc = 0
for s in sections:
    sec_bounds.append((acc, acc + len(s)))
    acc += len(s)

M = [text[i] == text[i + 5] for i in range(n - 5)]
mpos = [i for i, v in enumerate(M) if v]

# ---- A. maximal clusters (consecutive matches within distance <= 4) ----
print("=== A. maximal clusters of lag-5 matches (gaps <= 4) ===")
clusters = []
cur = [mpos[0]]
for p in mpos[1:]:
    if p - cur[-1] <= 4:
        cur.append(p)
    else:
        clusters.append(cur)
        cur = [p]
clusters.append(cur)
sizes = Counter(len(c) for c in clusters)
print(f"cluster size distribution: {sorted(sizes.items())}")
multi = [c for c in clusters if len(c) >= 2]
print(f"multi-match clusters: {len(multi)}; their gap patterns and content:")
for c in multi:
    gapspat = tuple(b - a for a, b in zip(c, c[1:]))
    i0, i1 = c[0], c[-1] + 6
    seg = text[i0:i1]
    eng = "".join(f"{ENG[r2i(x)]:>3s}" for x in seg)
    sec = next(k for k, (a, b) in enumerate(sec_bounds) if a <= c[0] < b)
    print(f"  pos {c[0]:5d} sec {sec} gaps {gapspat}: {eng}")

# null comparison of cluster-size distribution
trials = 300
null_sizes = Counter()
p1 = len(mpos) / len(M)
for _ in range(trials):
    sim = sorted(random.sample(range(len(M)), len(mpos)))
    cur = [sim[0]]
    for p in sim[1:]:
        if p - cur[-1] <= 4:
            cur.append(p)
        else:
            null_sizes[len(cur)] += 1
            cur = [p]
    null_sizes[len(cur)] += 1
print("null cluster sizes (per realization): "
      + ", ".join(f"{k}:{v/trials:.1f}" for k, v in sorted(null_sizes.items())))

# ---- B. locality: T(5) excluding section 4 (and 4+8) ----
print("\n=== B. is the signal corpus-wide or local? ===")
def T5_in(rangelist: list[tuple[int, int]]) -> tuple[int, float]:
    t = 0
    m_eff = 0
    for a, b in rangelist:
        mv = [text[i] == text[i + 5] for i in range(a, min(b - 5, n - 5))]
        mm = len(mv)
        m_eff += mm
        t += sum(1 for i in range(mm - 1) if mv[i] and mv[i + 1])
        t += sum(1 for i in range(mm - 4) if mv[i] and mv[i + 4])
    exp = 2 * m_eff / (N * N)
    return t, exp

full = [(0, n)]
no4 = [(a, b) for k, (a, b) in enumerate(sec_bounds) if k != 4]
no48 = [(a, b) for k, (a, b) in enumerate(sec_bounds) if k not in (4, 8)]
only4 = [sec_bounds[4]]
for name, rl in (("full corpus", full), ("without sec 4", no4),
                 ("without sec 4+8", no48), ("section 4 only", only4)):
    t, exp = T5_in(rl)
    z = (t - exp) / sqrt(exp)
    print(f"  {name:18s}: T5={t:3d} exp={exp:5.1f} z={z:+.2f}")

# ---- C. fair 2D scan: pair counts for all (lag L, separation d) cells ----
print("\n=== C. fair 2D scan, L in 2..30 x d in 1..6 ===")
def cell_counts(s: str) -> dict[tuple[int, int], int]:
    out = {}
    sn = len(s)
    for lag in range(2, 31):
        mv = [s[i] == s[i + lag] for i in range(sn - lag)]
        mm = len(mv)
        for d in range(1, 7):
            out[(lag, d)] = sum(1 for i in range(mm - d) if mv[i] and mv[i + d])
    return out

obs_cells = cell_counts(text)
exp_cell = (n - 10) / (N * N)
ranked = sorted(obs_cells.items(), key=lambda kv: -kv[1])
print("top 6 cells (L,d):", [(k, v) for k, v in ranked[:6]], f"(exp ~{exp_cell:.0f})")
# Monte Carlo: P(some lag L has TWO cells among d=1..6 with counts >= obs pair)
obs_pair = sorted((obs_cells[(5, 1)], obs_cells[(5, 4)]))
def doublet_suppressed(length: int, rate: float) -> str:
    out = [random.randrange(N)]
    for _ in range(length - 1):
        if random.random() < rate:
            out.append(out[-1])
        else:
            c = random.randrange(N - 1)
            if c >= out[-1]:
                c += 1
            out.append(c)
    return "".join(AB[c] for c in out)

rate = sum(1 for i in range(n - 1) if text[i] == text[i + 1]) / (n - 1)
trials = 60
hits = 0
for _ in range(trials):
    sim = doublet_suppressed(n, rate)
    cells = cell_counts(sim)
    found = False
    for lag in range(2, 31):
        vals = sorted((cells[(lag, d)] for d in range(1, 7)), reverse=True)
        if vals[1] >= obs_pair[0] and vals[0] >= obs_pair[1]:
            found = True
            break
    hits += found
print(f"P(any lag has two cells >= ({obs_pair[1]},{obs_pair[0]})) "
      f"= {hits}/{trials}")

# ---- F. full delta histogram at lag 5 vs control lags ----
print("\n=== F. delta distribution at lag 5 (is only delta=0 special?) ===")
for lag in (4, 5, 6):
    deltas = Counter((r2i(text[i + lag]) - r2i(text[i])) % N
                     for i in range(n - lag))
    tot = n - lag
    exp = tot / N
    top = sorted(deltas.items(), key=lambda kv: -kv[1])[:3]
    z0 = (deltas[0] - exp) / sqrt(exp * (1 - 1 / N))
    chi = sum((v - exp) ** 2 / exp for v in deltas.values())
    print(f"  lag {lag}: delta=0 z={z0:+.2f}; top deltas {top}; "
          f"chi2={chi:.1f} (df 28)")
