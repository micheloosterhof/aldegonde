#!/usr/bin/env python3
# ABOUTME: Tests whether doublets (boundaries) and lag-5 events (group edges)
# ABOUTME: are consistent with a single shared {5,6} group tiling.
"""Do doublets and lag-5 events sit on the SAME {5,6} group grid?

If both phenomena come from one group structure, then doublets mark group
boundaries and d4 events mark 5-group extents, so every close
doublet-to-event distance must be a {5,6}-expressible sum. Informative
distances are <= 19 (everything >= 20 is always expressible); chance
consistency for unrelated positions is ~47%; a shared grid demands 100%.

Result: REJECTED. Doublet-vs-d4-anchor consistency is 4/22 = 18%, below
even the unrelated-null (50% +/- 16%); binomial P(<=4 | 22, 0.47) ~ 0.006.
Close encounters include a doublet 1 position from a d4 anchor and several
at distances 3, 7-class, 9 - impossible on a shared grid. d1 conventions
score at chance (60%). Cross-event d4 pairs: 0/2.

Conclusion: the doublet suppression and the lag-5 copy events do NOT share
a group grid. The two appearances of "5" are separate phenomena: doublet
avoidance is memoryless ~1/5 acceptance (or an independent structure), and
the lag-5 echoes are a distinct mechanism. The unified single-grid
five-block model is dead; its components survive separately.
"""

import random
import statistics as st

from aldegonde import c3301

AB = c3301.CICADA_ALPHABET
N = 29

with open("data/page0-58.txt") as f:
    raw = f.read()
parts = raw.split("%")
keep = [i for i, p in enumerate(parts) if any(c in AB for c in p)][:-2]
text = "".join(x for i in keep for x in parts[i] if x in AB)
n = len(text)

dpos = [i for i in range(n - 1) if text[i] == text[i + 1]]
M = [text[i] == text[i + 5] for i in range(n - 5)]
d1ev = [i for i in range(len(M) - 1) if M[i] and M[i + 1]]
d4ev = [i for i in range(len(M) - 4) if M[i] and M[i + 4]]

# {5,6}-expressible differences (0 = same boundary is consistent)
def expressible(upto: int) -> set[int]:
    ok = {0}
    for v in range(5, upto + 1):
        if v - 5 in ok or v - 6 in ok:
            ok.add(v)
    return ok

OK = expressible(40)
WINDOW = 19  # only differences <= 19 are informative

def consistency(boundaries_a: list[int], boundaries_b: list[int],
                *, exclude_same: bool = False) -> tuple[int, int]:
    """Count informative close pairs and how many are {5,6}-consistent."""
    inf = cons = 0
    bs = sorted(set(boundaries_b))
    for a in boundaries_a:
        for b in bs:
            d = abs(a - b)
            if d == 0 and exclude_same:
                continue
            if d <= WINDOW:
                inf += 1
                if d in OK:
                    cons += 1
    return inf, cons

# boundary hypotheses
B_doublet = [i + 1 for i in dpos]
# d4 event at j: 5-groups [j..j+4],[j+5..j+9] -> boundaries j, j+5, j+10
B_d4 = [b for j in d4ev for b in (j, j + 5, j + 10)]
# d1 event at j, two interpretations:
B_d1_start = [b for j in d1ev for b in (j, j + 5, j + 10)]   # copy at group start
B_d1_flank = [b for j in d1ev for b in (j + 1, j + 6)]       # boundary-flanking

print(f"{len(dpos)} doublets, {len(d1ev)} d1, {len(d4ev)} d4 events")
print(f"non-expressible diffs in 1..19: "
      f"{sorted(set(range(1,20)) - OK)} (10/19 -> chance ~47%)")

tests = [
    ("doublet vs doublet", B_doublet, B_doublet, True),  # noqa: FBT003
    ("doublet vs d4-grid", B_doublet, B_d4, False),
    ("doublet vs d1-grid(start)", B_doublet, B_d1_start, False),
    ("doublet vs d1-grid(flank)", B_doublet, B_d1_flank, False),
    ("d4-grid vs d4-grid (cross-event)", None, None, None),  # special below
    ("d1(start) vs d4", B_d1_start, B_d4, False),
]

for name, A, B, ex in tests:
    if A is None:
        # cross-event d4 pairs: anchor boundaries of different events
        inf = cons = 0
        for x in range(len(d4ev)):
            for y in range(x + 1, len(d4ev)):
                d = abs(d4ev[x] - d4ev[y])
                if 0 < d <= WINDOW:
                    inf += 1
                    if d in OK:
                        cons += 1
        print(f"{name}: {cons}/{inf} consistent")
        continue
    inf, cons = consistency(A, B, exclude_same=ex)
    if name == "doublet vs doublet":
        inf, cons = inf // 2, cons // 2  # symmetric double count
    print(f"{name}: {cons}/{inf} consistent")

# null: random event positions, same counts
print("\nnull (random event positions, 2000 trials), doublet vs d4-grid:")
obs_inf, obs_cons = consistency(B_doublet, B_d4)
rates = []
for _ in range(2000):
    rj = random.sample(range(n - 10), len(d4ev))
    rb = [b for j in rj for b in (j, j + 5, j + 10)]
    i_, c_ = consistency(B_doublet, rb)
    if i_:
        rates.append(c_ / i_)

print(f"  observed {obs_cons}/{obs_inf} = "
      f"{obs_cons/obs_inf if obs_inf else float('nan'):.2f}; "
      f"null rate {st.mean(rates):.2f} +/- {st.stdev(rates):.2f}")

# d1+d4 combined grids vs doublets, both d1 conventions
for nm, b1 in (("start", B_d1_start), ("flank", B_d1_flank)):
    i_, c_ = consistency(B_doublet, b1 + B_d4)
    print(f"doublets vs all events ({nm}): {c_}/{i_} consistent")

# list the actual close doublet-event encounters for inspection
print("\nclose encounters (doublet boundary vs d4 anchor, distance <= 19):")
for i in dpos:
    for j in d4ev:
        d = abs((i + 1) - j)
        if d <= WINDOW:
            print(f"  doublet@{i} d4@{j} delta(anchor)={j-(i+1)} "
                  f"{'OK' if abs(j-(i+1)) in OK or abs((i+1)-j) in OK else 'X'}")
for i in dpos:
    for j in d1ev:
        d = abs((i + 1) - j)
        if d <= WINDOW:
            print(f"  doublet@{i} d1@{j} delta={j-(i+1)}")
