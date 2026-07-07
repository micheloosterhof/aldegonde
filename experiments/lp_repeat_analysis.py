#!/usr/bin/env python3
"""Analyze repeats in Liber Primus page0-58 data to find key period candidates."""

import math
from collections import Counter, defaultdict
from aldegonde.c3301 import CICADA_ALPHABET
from aldegonde.stats.repeats import repeat_positions

# ── 1. Parse LP data ──────────────────────────────────────────────────────────
with open("data/page0-58.txt", "r") as f:
    raw = f.read()

# Split by "$" to get segments
raw_segments = raw.split("$")

# For each segment, extract only rune characters
rune_set = set(CICADA_ALPHABET)

segments: list[str] = []
for seg in raw_segments:
    runes = "".join(ch for ch in seg if ch in rune_set)
    if runes:
        segments.append(runes)

print(f"Number of segments: {len(segments)}")
for i, seg in enumerate(segments):
    print(f"  Segment {i}: {len(seg)} runes")

# ── 2. Compute absolute positions of each segment's start ─────────────────────
concat = "".join(segments)
print(f"\nTotal concatenated length: {len(concat)} runes")

seg_starts: list[int] = []
pos = 0
for i, seg in enumerate(segments):
    seg_starts.append(pos)
    pos += len(seg)

print("\nSegment start positions (absolute):")
for i, start in enumerate(seg_starts):
    end = start + len(segments[i]) - 1
    print(f"  Segment {i}: start={start}, end={end}, length={len(segments[i])}")

# ── 3. Specific boundary repeats ──────────────────────────────────────────────
print("\n" + "=" * 80)
print("SPECIFIC BOUNDARY REPEATS")
print("=" * 80)

def find_in_segment(seg_idx: int, pattern: str) -> list[int]:
    """Find all occurrences of pattern in a segment, return local positions."""
    seg = segments[seg_idx]
    positions = []
    start = 0
    while True:
        idx = seg.find(pattern, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + 1
    return positions

def to_english_approx(runes: str) -> str:
    """Convert runes to approximate English letters for display."""
    eng_map = dict(zip(CICADA_ALPHABET, [
        "F","U","TH","O","R","C","G","W","H","N","I","J","EO","P","X",
        "S","T","B","E","M","L","NG","OE","D","A","AE","Y","IA","EA"
    ]))
    return "".join(eng_map.get(r, "?") for r in runes)

# Define the specific repeats to check
boundary_repeats = [
    ("DJUBEI", "ᛞᛄᚢᛒᛖᛁ", [(9, "END"), (6, 28)]),
    ("NGEAFN", "ᛝᛠᚠᚾ", [(4, "END"), (0, 575), (6, 360)]),
    ("JXEAG", "ᛄᛉᛠᚷ", [(1, "END"), (6, 96)]),
    ("NCUB", "ᚾᚳᚢᛒ", [(4, "START+3"), (2, 889)]),
    ("OAAEH", "ᚩᚪᚫᚻ", [(6, "START+5"), (8, 2134)]),
]

print(f"\n{'Repeat':<12} {'Runes':<10} {'Eng':<12} {'Seg':<5} {'Local Pos':<12} {'Abs Pos':<10} {'Distance':<10}")
print("-" * 80)

for name, rune_pattern, locations in boundary_repeats:
    eng = to_english_approx(rune_pattern)
    # Find all occurrences in the entire concatenated text
    all_abs_positions = []
    search_start = 0
    while True:
        idx = concat.find(rune_pattern, search_start)
        if idx == -1:
            break
        all_abs_positions.append(idx)
        search_start = idx + 1

    # Map each abs position back to segment
    abs_positions_with_seg = []
    for abs_pos in all_abs_positions:
        for si in range(len(segments) - 1, -1, -1):
            if abs_pos >= seg_starts[si]:
                local = abs_pos - seg_starts[si]
                abs_positions_with_seg.append((si, local, abs_pos))
                break

    for si, local, abs_pos in abs_positions_with_seg:
        seg_len = len(segments[si])
        pos_desc = f"{local}"
        if local < 10:
            pos_desc += " (START)"
        elif local >= seg_len - len(rune_pattern) - 5:
            pos_desc += " (END)"
        print(f"{name:<12} {rune_pattern:<10} {eng:<12} {si:<5} {pos_desc:<12} {abs_pos:<10}")

    # Print distances between all pairs
    if len(all_abs_positions) > 1:
        for i in range(len(all_abs_positions)):
            for j in range(i + 1, len(all_abs_positions)):
                d = all_abs_positions[j] - all_abs_positions[i]
                print(f"  -> distance between pos {all_abs_positions[i]} and {all_abs_positions[j]}: {d} (factors: ", end="")
                factors = []
                for f in range(2, min(d + 1, 200)):
                    if d % f == 0:
                        factors.append(f)
                print(f"{factors[:20]})")
    print()

# ── 4. ALL repeats of length 4+ in entire LP ──────────────────────────────────
print("\n" + "=" * 80)
print("ALL REPEATS OF LENGTH 4+ IN ENTIRE CONCATENATED LP")
print("=" * 80)

all_distances: list[int] = []
all_repeat_info: list[tuple[str, int, list[int], list[int]]] = []

for length in range(4, 11):
    reps = repeat_positions(concat, length=length)
    if not reps:
        continue
    print(f"\n--- Length {length}: {len(reps)} repeated n-grams ---")
    for ngram_str, positions in sorted(reps.items(), key=lambda x: -len(x[1])):
        # Map positions to segments
        seg_info = []
        for p in positions:
            for si in range(len(segments) - 1, -1, -1):
                if p >= seg_starts[si]:
                    seg_info.append(si)
                    break

        # Compute pairwise distances
        dists = []
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                d = positions[j] - positions[i]
                dists.append(d)
                all_distances.append(d)

        eng_approx = to_english_approx(ngram_str.replace("(", "").replace(")", "").replace("'", "").replace(",", "").replace(" ", ""))
        print(f"  {ngram_str}  count={len(positions)}  positions={positions}  segs={seg_info}  distances={dists}")

# ── 5. GCD analysis ───────────────────────────────────────────────────────────
print("\n" + "=" * 80)
print("GCD / FACTOR ANALYSIS OF ALL REPEAT DISTANCES")
print("=" * 80)

print(f"\nTotal pairwise distances: {len(all_distances)}")

# Count factors of each distance
factor_counts: Counter = Counter()
for d in all_distances:
    if d == 0:
        continue
    for f in range(2, min(d + 1, 500)):
        if d % f == 0:
            factor_counts[f] += 1

# Also compute GCDs of all pairs of distances
gcd_counts: Counter = Counter()
for i in range(len(all_distances)):
    for j in range(i + 1, min(len(all_distances), i + 500)):  # limit for speed
        g = math.gcd(all_distances[i], all_distances[j])
        if g > 1:
            gcd_counts[g] += 1

print("\n--- Factor frequency (how many distances are divisible by factor f) ---")
print(f"{'Factor':<10} {'Count':<10} {'% of distances':<15}")
print("-" * 40)
total_d = len(all_distances)
for f, count in factor_counts.most_common(50):
    if f <= 100:
        pct = 100.0 * count / total_d if total_d > 0 else 0
        print(f"{f:<10} {count:<10} {pct:.1f}%")

# Focus on small factors that are period candidates
print("\n--- Top period candidates (factors 2-60) ---")
print(f"{'Period':<10} {'# distances divisible':<25} {'% of distances':<15}")
print("-" * 55)
for period in range(2, 61):
    count = factor_counts.get(period, 0)
    pct = 100.0 * count / total_d if total_d > 0 else 0
    bar = "#" * int(pct / 2)
    print(f"{period:<10} {count:<25} {pct:.1f}% {bar}")

# Expected percentage for random: 1/f for factor f
print("\n--- Factors with highest excess over random expectation ---")
print(f"{'Period':<10} {'Observed %':<15} {'Expected %':<15} {'Excess':<15}")
print("-" * 60)
candidates = []
for period in range(2, 61):
    count = factor_counts.get(period, 0)
    obs_pct = 100.0 * count / total_d if total_d > 0 else 0
    exp_pct = 100.0 / period
    excess = obs_pct - exp_pct
    candidates.append((period, obs_pct, exp_pct, excess))

candidates.sort(key=lambda x: -x[3])
for period, obs, exp, excess in candidates[:20]:
    print(f"{period:<10} {obs:.1f}%{'':<10} {exp:.1f}%{'':<10} {excess:+.1f}%")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print("\nTop 10 period candidates by factor frequency:")
small_factors = [(f, c) for f, c in factor_counts.most_common() if 2 <= f <= 60]
for f, c in small_factors[:10]:
    pct = 100.0 * c / total_d
    print(f"  Period {f}: {c}/{total_d} distances ({pct:.1f}%)")
