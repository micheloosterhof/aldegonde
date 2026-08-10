# ABOUTME: Characterizes the '.' mark process under the 30th-cipher-symbol reading:
# ABOUTME: per-section rates, gap structure, adjacency, and rune context at marks.
import math
import re
import statistics
from pathlib import Path

from aldegonde import c3301

RUNE = re.compile(r"[ᚠ-᛿]")

text = Path("/Users/mich/src/aldegonde/data/page0-58.txt").read_text()
secs = [s for s in text.split("$") if RUNE.search(s)][:10]

print("per-section mark rates (clean sections 0-9):")
tot_r = tot_m = 0
for i, s in enumerate(secs):
    r = len(RUNE.findall(s))
    m = sum(1 for ch in s if ch in c3301.CLUSTER_MARKS)
    tot_r += r
    tot_m += m
    exp = r * 168 / 12956
    # Poisson p for observing <= m if very low, or just report
    p0 = math.exp(-exp) if m == 0 else None
    note = f"  P(0 marks)={p0:.1e}" if p0 is not None else ""
    print(
        f"  sec {i}: {r:5d} runes, {m:3d} marks, rate {m / r:.4f}, expected {exp:.1f}{note}"
    )
print(
    f"  total: {tot_r} runes, {tot_m} marks, rate {tot_m / tot_r:.4f} (1/{tot_r / tot_m:.0f})"
)

# mark positions in the 30-symbol stream (runes + '.'), per section; gaps and '..'
gaps = []
adj = 0
ctx_before = {}
ctx_after = {}
for s in secs:
    stream = [ch for ch in s if RUNE.match(ch) or ch in c3301.CLUSTER_MARKS]
    pos = [i for i, ch in enumerate(stream) if ch in c3301.CLUSTER_MARKS]
    for a, b in zip(pos, pos[1:]):
        gaps.append(b - a)
        if b - a == 1:
            adj += 1
    for p in pos:
        if p > 0 and stream[p - 1] not in c3301.CLUSTER_MARKS:
            ctx_before[stream[p - 1]] = ctx_before.get(stream[p - 1], 0) + 1
        if p + 1 < len(stream) and stream[p + 1] not in c3301.CLUSTER_MARKS:
            ctx_after[stream[p + 1]] = ctx_after.get(stream[p + 1], 0) + 1

print(f"\n'..' adjacent marks: {adj}")
if gaps:
    print(
        f"mark gaps: n={len(gaps)}, mean {statistics.mean(gaps):.1f}, "
        f"cv {statistics.stdev(gaps) / statistics.mean(gaps):.2f} (exponential -> 1.0)"
    )


# chi-square of rune context vs uniform
def chi2(d, n_marks):
    exp = n_marks / 29
    return sum((d.get(r, 0) - exp) ** 2 / exp for r in set(d.keys())), len(d)


for name, d in (("rune before mark", ctx_before), ("rune after mark", ctx_after)):
    n = sum(d.values())
    exp = n / 29
    c2 = sum((v - exp) ** 2 / exp for v in d.values()) + (29 - len(d)) * exp
    print(
        f"{name}: n={n}, distinct {len(d)}/29, chi2 {c2:.1f} (df 28, crit@0.05 ~41.3)"
    )
