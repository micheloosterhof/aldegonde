#!/usr/bin/env python3
# ABOUTME: Tests whether group-length tilings ({5,6} etc.) can place every
# ABOUTME: doublet on a group boundary, incl. strict alternation patterns.
"""Can a {5,6}-style group tiling place all doublets on boundaries?

Under the five-block boundary model every doublet must sit on a group
boundary, so each gap between consecutive doublets must be a sum of group
lengths. For {5,6} the non-representable gaps are {1,2,3,4,7,8,9,13,14,19}
(all gaps >= 20 fit), making small gaps the only test.

Results:
- Strict periodic patterns (5,6,5,6 alternating etc.) are dead: the best
  phase captures only 25/86 doublets (a strict tiling must capture all 86).
- Free-choice {5,6} tiling, continuous across pages: 83/85 gaps fit. The
  only violations are two gaps of exactly 7: GG->IAIA at 5770/5777 (page
  24) and THTH->JJ at 8630/8637 (page 35). Adding 7 to the length set
  ({5,6,7}) fits all gaps.
- Page resets are excluded: the WW doublet at the very first rune pair of
  page 50 would need a length-1 group under reset-at-page; under
  continuous flow it is unconstrained (page 50 also begins mid-word).
- Honest null: conditioned on the known absence of gaps <= 5, the small
  gaps show chance-level expressibility (2/7 infeasible vs ~34% expected
  under a random small-gap distribution), so free-choice tiling is
  CONSISTENT with the data but only strict patterns are actually excluded.
"""


import random

from aldegonde import c3301

AB = c3301.CICADA_ALPHABET
N = 29

with open("data/page0-58.txt") as f:
    raw = f.read()
parts = raw.split("%")
keep = [i for i, p in enumerate(parts) if any(c in AB for c in p)][:-2]
pages = ["".join(x for x in parts[i] if x in AB) for i in keep]
text = "".join(pages)
n = len(text)
dpos = [i for i in range(n - 1) if text[i] == text[i + 1]]
gaps = [b - a for a, b in zip(dpos, dpos[1:])]

# page boundary positions (global index of first rune of each page)
page_starts = []
acc = 0
for p in pages:
    page_starts.append(acc)
    acc += len(p)

def expressible_set(lengths: tuple[int, ...], upto: int) -> set[int]:
    ok = {0}
    for v in range(1, upto + 1):
        if any(v - L in ok for L in lengths if v >= L):
            ok.add(v)
    return ok

# which page is a position on?
def page_of(i: int) -> int:
    for k in range(len(page_starts) - 1, -1, -1):
        if i >= page_starts[k]:
            return k
    return 0

print(f"{len(dpos)} doublets, {len(gaps)} gaps; gaps < 25: "
      f"{sorted(g for g in gaps if g < 25)}")

LSETS = [(5, 6), (4, 5, 6), (4, 5), (5, 6, 7), (4, 6), (3, 4, 5, 6, 7)]
print("\n=== A. continuous tiling (no resets): every gap must be expressible ===")
for ls in LSETS:
    ok = expressible_set(ls, max(gaps) + 1)
    bad = [g for g in gaps if g not in ok]
    # also the offset from text start to first doublet boundary
    first = dpos[0] + 1
    head = "" if first in ok else f" (+ first offset {first} infeasible)"
    print(f"  lengths {ls}: {len(bad)} infeasible gaps {sorted(set(bad))[:8]}{head}")

print("\n=== B. groups reset at page starts: constraints only within pages ===")
for ls in LSETS:
    ok = expressible_set(ls, n)
    bad = 0
    badlist = []
    for k, pg in enumerate(pages):
        a = page_starts[k]
        dz = [i - a for i in dpos if a <= i < a + len(pg) - 1]
        prev = None
        for q in dz:
            need = q + 1 if prev is None else q - prev
            if need not in ok:
                bad += 1
                badlist.append((k, need))
            prev = q
    print(f"  lengths {ls}: {bad} infeasible constraints {badlist[:6]}")

print("\n=== C. null comparison: how often would random positions pass? ===")

ok56 = expressible_set((5, 6), n)
def count_bad(positions: list[int]) -> int:
    bad = 0
    for k, pg in enumerate(pages):
        a = page_starts[k]
        dz = sorted(i - a for i in positions if a <= i < a + len(pg) - 1)
        prev = None
        for q in dz:
            need = q + 1 if prev is None else q - prev
            if need not in ok56:
                bad += 1
            prev = q
    return bad

obs_bad = count_bad(dpos)
trials = 2000
worse = sum(1 for _ in range(trials)
            if count_bad(sorted(random.sample(range(n - 1), len(dpos)))) <= obs_bad)
print(f"  observed infeasible-with-page-reset ({{5,6}}): {obs_bad}")
print(f"  random-position null: P(<= observed) = {worse/trials:.3f}")

print("\n=== D. strict periodic patterns (boundaries at fixed residues) ===")
# pattern P of lengths repeating: boundaries at cumsum mod sum(P)
def residues(pat: tuple[int, ...]) -> tuple[int, set[int]]:
    s = sum(pat)
    res = set()
    c = 0
    for L in pat:
        c += L
        res.add(c % s)
    return s, res

for pat in [(5, 6), (6, 5), (5,), (6,), (5, 5, 6), (5, 6, 6), (5, 6, 5, 6, 6)]:
    s, res = residues(pat)
    # global phase unknown: find best phase
    best = 0
    for ph in range(s):
        hits = sum(1 for i in dpos if (i + 1 - ph) % s in res)
        best = max(best, hits)
    exp = len(dpos) * len(res) / s
    print(f"  pattern {pat} (period {s}): best phase hits {best}/{len(dpos)} "
          f"(chance ~{exp:.0f})")
