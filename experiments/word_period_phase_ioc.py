# ABOUTME: If the per-word base cycles with period 29, words 29 apart share an
# ABOUTME: alphabet. Pools every same-phase position pair, not just equal ones.
"""Michel's test. Assume the per-word base runs on a 29-position disk, so

    base_w == base_{w+29}

Under the walk, c[w][j] = base_w(g^(j mod 5)(p[w][j])). So for two words a
period apart, positions j and j' satisfy

    c[w][j] == c[w+P][j']   <=>   g^(j mod 5)(p[w][j]) == g^(j' mod 5)(p[w+P][j'])

and when **j == j' (mod 5)** the g-powers cancel outright, leaving

    c[w][j] == c[w+P][j']   <=>   p[w][j] == p[w+P][j']

i.e. the coincidence rate is the PLAINTEXT's (~0.060, nIoC ~1.75), not 1/29.
When j != j' (mod 5) the exposed relation is a non-identity power of g and the
rate sits at chance -- a control that needs no external reference.

That is the whole test: same-phase pairs should light up at a true period,
different-phase pairs should not. Pooling every same-phase pair rather than
only j == j' multiplies the available pairs several-fold.

Positive control: at P = 0 the same-phase set IS the within-word d5/d10 echo,
which is independently measured at ~0.048 (long-word-structure.md). If the
harness does not reproduce that, it is wrong.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

N = 29
CHANCE = 1.0 / N
PLAINTEXT = 0.060  # runeglish coincidence; repo controls give 0.0611-0.0636


def build_words(stream: list[int], word_id: list[int]) -> list[list[int]]:
    words: list[list[int]] = []
    for r, w in zip(stream, word_id):
        while w >= len(words):
            words.append([])
        words[w].append(r)
    return words


def phase_counts(
    words: list[list[int]],
    period: int,
    *,
    same_phase: bool,
    first_only: bool = False,
) -> tuple[int, int]:
    """Coincidences between words `period` apart at (same|different) phase."""
    hits = tot = 0
    for w in range(len(words) - period):
        a, b = words[w], words[w + period]
        if period == 0 and same_phase:
            # within one word: unordered pairs at distance divisible by 5
            for j in range(len(a)):
                for k in range(j + 1, len(a)):
                    if (k - j) % 5 == 0:
                        tot += 1
                        hits += a[j] == a[k]
            continue
        if first_only:
            if a and b:
                tot += 1
                hits += a[0] == b[0]
            continue
        for j in range(len(a)):
            for k in range(len(b)):
                if ((j - k) % 5 == 0) == same_phase:
                    tot += 1
                    hits += a[j] == b[k]
    return hits, tot


def z(hits: int, tot: int, p: float) -> float:
    if tot == 0:
        return float("nan")
    return (hits - tot * p) / math.sqrt(tot * p * (1 - p))


def report(label: str, hits: int, tot: int) -> None:
    if tot == 0:
        print(f"  {label:<34} no pairs")
        return
    rate = hits / tot
    print(
        f"  {label:<34} {hits:>6}/{tot:<7} rate {rate:.4f}  nIoC {rate * N:.3f}   "
        f"z(chance)={z(hits, tot, CHANCE):+6.2f}  z(shared)={z(hits, tot, PLAINTEXT):+7.2f}"
    )


def main() -> None:
    stream, word_id = load_clean()
    words = build_words(stream, word_id)
    print(f"corpus: {len(stream)} runes, {len(words)} words")
    print(
        f"chance nIoC = 1.000 (rate {CHANCE:.4f});  shared alphabet ~ nIoC 1.74 "
        f"(rate {PLAINTEXT:.4f})\n"
    )

    # --- positive control: P = 0 is the within-word same-phase echo ----------
    print("POSITIVE CONTROL  (P=0: within-word pairs at distance 5, 10, ...)")
    h, t = phase_counts(words, 0, same_phase=True)
    report("within-word same-phase", h, t)
    assert t > 1500, t
    assert z(h, t, CHANCE) > 2.5, "harness fails to see the known d5 echo"
    print("  -> reproduces the known echo; harness is live\n")

    # --- the test at P = 29 --------------------------------------------------
    print("THE TEST  (assume a 29-word disk: base_w == base_{w+29})")
    h, t = phase_counts(words, 29, same_phase=True, first_only=True)
    report("first letters only, j=j'=0", h, t)
    h, t = phase_counts(words, 29, same_phase=True)
    report("ALL same-phase pairs", h, t)
    h, t = phase_counts(words, 29, same_phase=False)
    report("different-phase (control)", h, t)

    # --- calibrate against the corpus's OWN echo, not a theoretical value ---
    # The P=0 control measures what a shared alphabet actually delivers here,
    # partial leak and register included. That is the fairest yardstick and it
    # needs no external plaintext reference.
    h0, t0 = phase_counts(words, 0, same_phase=True)
    observed_shared = h0 / t0
    h29, t29 = phase_counts(words, 29, same_phase=True)
    print(
        f"\n  self-calibrated: a shared alphabet delivers {observed_shared:.4f} in THIS corpus"
    )
    print(
        f"  P=29 same-phase {h29}/{t29} against that: "
        f"z = {z(h29, t29, observed_shared):+.2f}"
    )

    # --- is 29 special? scan the periods ------------------------------------
    print("\nPERIOD SCAN (same-phase pairs; a true period lights up, nothing else)")
    best = []
    for p in range(1, 121):
        h, t = phase_counts(words, p, same_phase=True)
        if t < 2000:
            continue
        best.append((z(h, t, CHANCE), p, h, t))
    best.sort(reverse=True)
    print("  strongest 6 periods by z vs chance:")
    for zz, p, h, t in best[:6]:
        mark = "   <== 29" if p == 29 else ""
        print(
            f"    P={p:>4}: rate {h / t:.4f}  nIoC {h / t * N:.3f}  z={zz:+5.2f}{mark}"
        )
    print("  weakest 3:")
    for zz, p, h, t in best[-3:]:
        print(f"    P={p:>4}: rate {h / t:.4f}  nIoC {h / t * N:.3f}  z={zz:+5.2f}")
    rank = [p for _, p, _, _ in best].index(29) + 1
    print(f"\n  29 ranks {rank} of {len(best)} periods scanned")
    print(
        f"  max |z| over the scan: {max(abs(b[0]) for b in best):.2f} "
        f"(expected ~{math.sqrt(2 * math.log(len(best))):.2f} for pure noise)"
    )


if __name__ == "__main__":
    main()
