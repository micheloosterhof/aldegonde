#!/usr/bin/env python3
"""Battery 4: anatomy of the 89 doublets + runeglish plaintext reference."""
import collections
import math
from lp_structure import RUNES, R2I, N, nioc

# --- runeglish reference stats from ngram tables ---
big = {}
tot = 0
with open("src/aldegonde/data/ngrams/runeglish/bigrams.txt") as f:
    for line in f:
        g, c = line.split()
        g = g.replace("ᛂ", "ᛄ")  # alternate glyph for the same rune
        big[g] = int(c)
        tot += int(c)
dbl = sum(v for g, v in big.items() if g[0] == g[1])
print(f"runeglish plaintext doublet rate: {dbl/tot:.4f} (uniform would be {1/29:.4f})")
# doublet rate by rune
dd = {g[0]: v / tot for g, v in big.items() if g[0] == g[1]}
print("top plaintext doubled runes:", sorted(dd.items(), key=lambda kv: -kv[1])[:6])
# plaintext lag-1 difference dist
ddist = collections.Counter()
for g, v in big.items():
    ddist[(R2I[g[1]] - R2I[g[0]]) % N] += v
print("plaintext diff dist (top/bottom):")
sd = sorted(ddist.items(), key=lambda kv: -kv[1])
print("  most common diffs:", [(k, round(v/tot, 3)) for k, v in sd[:5]])
print("  least common diffs:", [(k, round(v/tot, 4)) for k, v in sd[-5:]])

# --- parse raw text keeping ALL separators, track doublet contexts ---
with open("data/page0-58.txt") as f:
    raw = f.read()

# walk the rune stream; remember what separators occurred between runes
prev = None
between = ""
doublets = []  # (index, rune, separators-between, context)
idx = 0
positions = []  # (rune, separators_before_this_rune)
page = 0
for ch in raw:
    if ch in R2I:
        positions.append((R2I[ch], between, page))
        between = ""
    elif ch in "-./%&$\n" or ch.isalnum():
        between += ch
        if ch == "%":
            page += 1

n = len(positions)
print(f"\ntotal runes: {n}")
sep_kinds = collections.Counter()
dbl_sep_kinds = collections.Counter()
for i in range(1, n):
    r, sep, pg = positions[i]
    kind = "none"
    if "%" in sep or "$" in sep:
        kind = "page/seg"
    elif "." in sep:
        kind = "sentence"
    elif "-" in sep:
        kind = "word"
    elif "/" in sep or "\n" in sep:
        kind = "line"
    sep_kinds[kind] += 1
    if positions[i - 1][0] == r:
        dbl_sep_kinds[kind] += 1
print("pair-separator kinds:", dict(sep_kinds))
print("doublet pairs by separator kind:", dict(dbl_sep_kinds))
for kind in sep_kinds:
    e = sep_kinds[kind] / N
    o = dbl_sep_kinds.get(kind, 0)
    z = (o - e) / math.sqrt(sep_kinds[kind] * (1/N) * (1 - 1/N))
    print(f"  {kind:9s}: obs {o:3d} exp {e:6.1f} z={z:+6.2f}")

print("\ndoublet rune identity:")
dr = collections.Counter()
dpg = collections.Counter()
for i in range(1, n):
    if positions[i - 1][0] == positions[i][0]:
        dr[RUNES[positions[i][0]]] += 1
        dpg[positions[i][2]] += 1
print(dict(dr))
print("doublets per page:", dict(sorted(dpg.items())))

# conditional doublet rate per rune: P(next==r | cur==r) vs base
print("\nper-rune doublet z-scores (within full stream):")
cnt = collections.Counter(p[0] for p in positions)
for r in range(N):
    occ = sum(1 for i in range(n - 1) if positions[i][0] == r)
    o = sum(1 for i in range(n - 1) if positions[i][0] == r and positions[i + 1][0] == r)
    e = occ / N
    z = (o - e) / math.sqrt(occ * (1/N) * (1 - 1/N))
    print(f"{RUNES[r]} occ={occ:3d} dbl={o:2d} exp={e:4.1f} z={z:+5.2f}", end="   " if (r + 1) % 3 else "\n")
print()
