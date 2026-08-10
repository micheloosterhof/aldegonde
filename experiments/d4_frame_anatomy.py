#!/usr/bin/env python3
# ABOUTME: Anatomizes the d4 frame events (lag-5 match pairs at separation 4) as
# ABOUTME: candidate walk wiring equations: per-leg boundary counts and the
# ABOUTME: implied sigma-g relations, with consistency and null checks.
"""d4 frame anatomy: can the residual lag-5 face become key equations?

Under the length-clocked walk, alphabet(w, j) = base0 . W_w . g^(j mod 5)
with W_w the running product of (g^((L_v-1) mod 5) . sigma). A lag-5 match
read as ALPHABET COINCIDENCE between its two ends forces

    prod_{v=w1}^{w2-1} (g^(a_v) sigma) = g^((j1-j2) mod 5),   a_v=(L_v-1)%5

across the b = w2-w1 crossed boundaries:

  b=0  identity = g^0        -- always true: the within-word echo.
  b=1  g^a sigma = g^m       -- IMPOSSIBLE (sigma not in <g>,
                                sigma-power-step.md). One-boundary legs
                                cannot be alphabet coincidences.
  b=2  sigma g^a sigma = g^t -- CAUTION: the pair (a, t) is a tautology of
                                the geometry, not data. Distance 5 forces
                                5 = (L1-j1) + Lmid + j2, which makes
                                t = a+2 (mod 5) identically for every b=2
                                leg. The only information the events carry
                                is WHICH middle-length class a they fall
                                in: alphabet coincidence would enrich
                                exactly the class(es) whose fixed relation
                                R_a: sigma g^a sigma = g^(a+2) holds.
  b>=3 deeper words          -- recorded raw.

This script lists every d4 event's two legs with (b, a-vector, m), then
runs the two real tests: (1) is any middle-length class enriched among the
b=2 legs over its base rate in random distance-5 geometry, and (2) do the
events' leg-boundary counts (and the count of fully-explainable events,
both legs b in {0,2}) differ from the random-position null at all.
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lp_corpus import load_clean

M5 = 5


def main() -> None:
    stream, wid = load_clean()
    n = len(stream)
    # word lengths and within-word positions
    wlen: Counter = Counter(wid)
    pos = []
    last = None
    p = 0
    for w in wid:
        p = p + 1 if w == last else 0
        last = w
        pos.append(p)

    match = [stream[i] == stream[i + 5] for i in range(n - 5)]
    events = [i for i in range(len(match) - 4) if match[i] and match[i + 4]]
    print(f"d4 events (match pairs at separation 4): {len(events)}")

    lens_by_word = {w: wlen[w] for w in wlen}

    def leg(x: int):
        w1, w2 = wid[x], wid[x + 5]
        b = w2 - w1
        j1, j2 = pos[x], pos[x + 5]
        m = (j1 - j2) % M5
        avec = [(lens_by_word[v] - 1) % M5 for v in range(w1, w2)]
        return b, avec, m

    bcount: Counter = Counter()
    b2_relations = []
    print(f"\n{'event':>6} {'leg':>4} {'b':>2} {'a-vector':>12} {'m':>2}  note")
    for i in events:
        for tag, x in (("A", i), ("B", i + 4)):
            b, avec, m = leg(x)
            bcount[b] += 1
            note = ""
            if b == 1:
                note = "impossible as alphabet coincidence"
            elif b == 2:
                a2 = avec[1]
                t = (m - avec[0]) % M5
                b2_relations.append((a2, t))
                note = f"sigma g^{a2} sigma = g^{t}"
            print(f"{i:>6} {tag:>4} {b:>2} {str(avec):>12} {m:>2}  {note}")

    print(f"\nleg boundary counts: {dict(sorted(bcount.items()))}")

    # random-position null for the b distribution
    rng = random.Random(3301)
    null_b: Counter = Counter()
    trials = 20000
    for _ in range(trials):
        x = rng.randrange(n - 9)
        w1, w2 = wid[x], wid[x + 5]
        null_b[w2 - w1] += 1
    total_legs = sum(bcount.values())
    print("b-distribution vs random-position null:")
    for b in sorted(set(bcount) | set(null_b)):
        e = null_b[b] / trials * total_legs
        print(f"  b={b}: obs {bcount[b]:>3}  exp {e:6.1f}")

    # Test 1: middle-length-class enrichment among b=2 legs.
    obs_a = Counter(a for a, _t in b2_relations)
    null_a: Counter = Counter()
    for _ in range(trials):
        x = rng.randrange(n - 5)
        if wid[x + 5] - wid[x] == 2:
            null_a[(lens_by_word[wid[x] + 1] - 1) % M5] += 1
    tot_null = sum(null_a.values())
    print("\nTest 1 — b=2 legs by middle-length class a (obs vs base rate):")
    for a in range(M5):
        e = null_a[a] / tot_null * len(b2_relations) if tot_null else 0
        print(f"  a={a} (Lmid={a + 1}): obs {obs_a[a]:>2}  exp {e:5.1f}")

    # Test 2: events whose BOTH legs avoid b=1 (the only walk-explainable
    # configuration), vs random-geometry expectation.
    def legs_ok(i: int) -> bool:
        return all(leg(x)[0] != 1 for x in (i, i + 4))

    obs_ok = sum(1 for i in events if legs_ok(i))
    null_ok = sum(1 for _ in range(trials) if legs_ok(rng.randrange(n - 9)))
    print(
        f"\nTest 2 — events with both legs walk-explainable (b in 0,2): "
        f"{obs_ok}/{len(events)} vs {null_ok / trials * len(events):.1f} "
        f"expected from geometry alone"
    )

    # Test 3 — the direct R_a test, independent of the d4 pairing: if
    # sigma g^a sigma = g^(a+2) holds for some a, then EVERY lag-5 pair at
    # b=2 / middle-class-a geometry is an alphabet coincidence and matches
    # at the plaintext coincidence rate (~0.058) instead of 1/29 = 0.0345.
    # b=1 cells must all sit at 1/29 (alphabet coincidence impossible).
    print("\nTest 3 — mono lag-5 match rate by geometry cell:")
    print(f"{'cell':>16} {'pairs':>6} {'match':>6} {'rate':>7} {'z vs 1/29':>9}")
    cells: Counter = Counter()
    hits: Counter = Counter()
    for x in range(n - 5):
        b = wid[x + 5] - wid[x]
        if b == 2:
            key = f"b=2 a={(lens_by_word[wid[x] + 1] - 1) % M5}"
        elif b == 1:
            key = "b=1 (all)"
        elif b == 0:
            key = "b=0 (echo)"
        else:
            key = f"b={b}"
        cells[key] += 1
        hits[key] += match[x] if x < len(match) else 0
    p0 = 1 / 29
    for key in sorted(cells):
        m_, o_ = hits[key], cells[key]
        sd = (o_ * p0 * (1 - p0)) ** 0.5
        print(f"{key:>16} {o_:>6} {m_:>6} {m_ / o_:>7.4f} {(m_ - o_ * p0) / sd:>+9.2f}")


if __name__ == "__main__":
    main()
