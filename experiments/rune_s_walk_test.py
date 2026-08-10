#!/usr/bin/env python3
# ABOUTME: Quantifies the rune-S echo under the length-clocked walk: simulated
# ABOUTME: distribution of the max echoed-rune concentration, plus the unigram
# ABOUTME: arithmetic that kills fixed-channel escapes (rune-s-lag5-echo.md).
"""What does the walk predict for the rune-S echo?

The S anomaly: 11 of the 102 within-word d5 coincidence pairs echo the
single ciphertext rune S (p = 2.4e-6 against a frequency-weighted,
position-controlled null). That null is the right one for
identity-preserving mechanisms. Under the WALK, however, the echoed
ciphertext rune is base_w(g^j(p)) — scrambled per word — so echo
identities are near-uniform and the relevant question is
P(max rune count >= 11 | ~102 pairs, ~uniform over 29). This script:

  1. simulates the walk (register plaintext, LP word-length structure,
     random tuned g / sigma / base0) and measures the joint distribution
     of (total within-word d5 pairs, max echoed-rune count);
  2. reports P(max >= 11) conditioned on totals near the LP's 102;
  3. runs the unigram arithmetic that closes the fixed-channel escape:
     a plaintext rune q fixed by g and sigma maps to the constant
     base0(q), so carrying k echoes needs freq(q) ~ sqrt(k / (2073 e))
     (>= 4%), while S's flat unigram count (434 vs 446.8 expected in the
     clean corpus) allows a constant channel of at most ~0.25%.
"""

from __future__ import annotations

import random
import sys
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from d5_partial_leak import to_runeglish  # noqa: E402
from doublet_position_profile import IDX_ENG  # noqa: E402
from ea_direction_test import PROSE_CACHE, PROSE_URL, prose_words  # noqa: E402
from lp_corpus import load_clean  # noqa: E402
from sigma_power_kill import encrypt, random_order5  # noqa: E402

M = 29
SIMS = 400


def main() -> None:
    rng = random.Random(3301)

    # LP word-length structure and observed statistic
    stream, wid = load_clean()
    lp_lens = list(Counter(wid).values())
    echoed: Counter = Counter()
    for i in range(len(stream) - 5):
        if stream[i] == stream[i + 5] and wid[i] == wid[i + 5]:
            echoed[stream[i]] += 1
    lp_total = sum(echoed.values())
    lp_max = max(echoed.values())
    print(f"LP: {lp_total} within-word d5 pairs, max rune count {lp_max} "
          f"(S), S unigram {sum(1 for r in stream if r == echoed.most_common(1)[0][0])} "
          f"vs {len(stream) / M:.1f} expected")

    # register plaintext re-cut to LP word lengths
    prose_path = Path(sys.argv[1]) if len(sys.argv) > 1 else PROSE_CACHE
    if not prose_path.exists():
        print(f"downloading {PROSE_URL} -> {prose_path}")
        urllib.request.urlretrieve(PROSE_URL, prose_path)
    prose_stream = [IDX_ENG[t] for w in prose_words(prose_path)
                    for t in to_runeglish(w)]

    def cut_words(offset: int) -> list[list[int]]:
        out, pos = [], offset
        for L in lp_lens:
            out.append(prose_stream[pos:pos + L])
            pos += L
        return out

    totals, maxima, cond = [], [], []
    for _s in range(SIMS):
        words = cut_words(rng.randrange(len(prose_stream) - sum(lp_lens)))
        g = random_order5(rng)
        sigma = list(range(M))
        rng.shuffle(sigma)
        base0 = list(range(M))
        rng.shuffle(base0)
        ct = encrypt(words, base0, g, sigma)
        e: Counter = Counter()
        for w in ct:
            for j in range(len(w) - 5):
                if w[j] == w[j + 5]:
                    e[w[j]] += 1
        tot = sum(e.values())
        mx = max(e.values()) if e else 0
        totals.append(tot)
        maxima.append(mx)
        if abs(tot - lp_total) <= 20:
            cond.append(mx)

    import statistics as st
    print(f"\nwalk simulation ({SIMS} runs, random tuned g / sigma / base0):")
    print(f"  total pairs: mean {st.mean(totals):.0f} "
          f"(LP {lp_total}); max-rune: mean {st.mean(maxima):.1f}, "
          f"P(max >= {lp_max}) = "
          f"{sum(1 for m in maxima if m >= lp_max) / len(maxima):.3f}")
    if cond:
        print(f"  conditioned on total within ±20 of LP ({len(cond)} runs): "
              f"P(max >= {lp_max}) = "
              f"{sum(1 for m in cond if m >= lp_max) / len(cond):.3f}")

    # fixed-channel arithmetic
    n = len(stream)
    s_count = 434
    allow = (446.8 - s_count) + 2 * (n / M * (1 - 1 / M)) ** 0.5
    phi_max = max(allow, 0) / (n * (1 - 1 / M))
    import math
    phi_need = math.sqrt(11 / (2073 * 1.6))
    print(f"\nfixed-channel escape: needs freq(q) ~ {phi_need * 100:.1f}% to "
          f"carry 11 echoes; S's flat unigram allows <= {phi_max * 100:.2f}% "
          f"-> excluded by a factor ~{phi_need / max(phi_max, 1e-9):.0f} in "
          f"frequency (~{(phi_need / max(phi_max, 1e-9)) ** 2:.0f}x in pairs)")


if __name__ == "__main__":
    main()
