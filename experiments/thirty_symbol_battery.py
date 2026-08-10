# ABOUTME: Compares distance statistics (doublets, kappa, lag-5 pairing, DJU-BEI
# ABOUTME: arithmetic) between the mark-stripped stream and the 30-symbol stream.
"""Tests the thirty-symbol-disk hypothesis: if '.' is a real cipher symbol
occupying a stream position, distance statistics computed on the 30-symbol
stream (runes + '.') should be at least as sharp as on the mark-stripped
29-symbol stream. Clean corpus, sections 0-9 of data/page0-58.txt.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from aldegonde import c3301

DATA = Path(__file__).resolve().parent.parent / "data" / "page0-58.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
DJU_BEI = "ᛞᛄᚢᛒᛖᛁ"


def sections(text: str) -> list[str]:
    return [s for s in text.split("$") if RUNE.search(s)][:10]


def stream(section: str, *, with_marks: bool) -> str:
    def keep(ch):
        return RUNE.match(ch) or (with_marks and ch in c3301.CLUSTER_MARKS)

    return "".join(ch for ch in section if keep(ch))


def kappa(s: str, lag: int) -> tuple[int, int, float]:
    n = len(s) - lag
    hits = sum(1 for i in range(n) if s[i] == s[i + lag])
    freqs = Counter(s)
    p = sum(c * c for c in freqs.values()) / (len(s) ** 2)
    z = (hits - n * p) / (n * p * (1 - p)) ** 0.5
    return hits, n, z


def pair_separations(s: str, lag: int = 5) -> Counter:
    matches = [i for i in range(len(s) - lag) if s[i] == s[i + lag]]
    return Counter(b - a for a, b in zip(matches, matches[1:]))


def doublets(s: str) -> int:
    return sum(1 for i in range(len(s) - 1) if s[i] == s[i + 1])


def main() -> None:
    secs = sections(DATA.read_text())
    for with_marks, name in (
        (False, "29-symbol (marks stripped)"),
        (True, "30-symbol (marks as positions)"),
    ):
        parts = [stream(s, with_marks=with_marks) for s in secs]
        full = "".join(parts)
        print(f"=== {name}: {len(full)} symbols ===")
        d = doublets(full)
        mark_flank = sum(
            1
            for i in range(len(full) - 2)
            if full[i + 1] in c3301.CLUSTER_MARKS and full[i] == full[i + 2]
        )
        note = f" (X.X identical-rune-around-mark: {mark_flank})" if with_marks else ""
        print(f"doublets: {d}{note}")
        for lag in (1, 5, 6, 11):
            hits, n, z = kappa(full, lag)
            print(f"kappa lag {lag}: {hits}/{n}  z={z:+.2f}")
        seps = pair_separations(full)
        total_matches = len([i for i in range(len(full) - 5) if full[i] == full[i + 5]])
        mark_matches = (
            sum(
                1
                for i in range(len(full) - 5)
                if full[i] == full[i + 5] and full[i] in c3301.CLUSTER_MARKS
            )
            if with_marks
            else 0
        )
        print(
            f"lag-5 matches: {total_matches}"
            + (f" (of which mark==mark: {mark_matches})" if with_marks else "")
        )
        print(
            "lag-5 match-pair separations:",
            {k: seps[k] for k in sorted(seps) if k <= 6},
        )
        t5 = seps[1] + seps[4]
        print(f"T5 = d1 + d4 pairs = {seps[1]} + {seps[4]} = {t5}")
        print()

    # small-gap tail of the mark process (dead-zone check, doublet parallel)
    full30 = "".join(stream(s, with_marks=True) for s in secs)
    marks = [i for i, ch in enumerate(full30) if ch in c3301.CLUSTER_MARKS]
    gaps = [b - a for a, b in zip(marks, marks[1:])]
    mean_gap = sum(gaps) / len(gaps)
    small = sorted(g for g in gaps if g <= 12)
    expect_small = len(gaps) * (1 - 2.718281828 ** (-12 / mean_gap))
    print(
        f"mark gaps: min {min(gaps)}, gaps <= 12: {small} "
        f"(exponential expectation ~{expect_small:.1f})"
    )
    print()

    # DJU-BEI arithmetic under mark-inclusive counting (6-gram, start to start;
    # the 7th matching rune of the second occurrence is the first rune of the
    # solved section 10, outside the clean corpus)
    full29 = "".join(stream(s, with_marks=False) for s in secs)
    a29 = full29.find(DJU_BEI)
    b29 = full29.find(DJU_BEI, a29 + 1)
    # map rune offsets into the 30-symbol stream
    rune_positions = [i for i, ch in enumerate(full30) if ch not in c3301.CLUSTER_MARKS]
    a30, b30 = rune_positions[a29], rune_positions[b29]
    marks_between = sum(1 for ch in full30[a30:b30] if ch in c3301.CLUSTER_MARKS)
    print(f"DJU-BEI rune offsets {a29}/{b29}, stripped distance {b29 - a29}")
    print(
        f"30-symbol offsets {a30}/{b30}, distance {b30 - a30} "
        f"({marks_between} marks in between)"
    )
    for n, label in ((b29 - a29, "stripped"), (b30 - a30, "30-symbol")):
        f, k, factors = n, 2, []
        while k * k <= f:
            while f % k == 0:
                factors.append(k)
                f //= k
            k += 1
        if f > 1:
            factors.append(f)
        print(f"  {label} distance {n} = {' x '.join(map(str, factors))}")


if __name__ == "__main__":
    main()
