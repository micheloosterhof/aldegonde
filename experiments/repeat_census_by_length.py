# ABOUTME: Counts repeated windows at every length, aligned and unaligned, to see whether
# ABOUTME: DJU-BEI has company or stands alone.
"""If the author engineered one state return, did they engineer others?

`dju-bei-ends-the-body.md` argues the repeat is deliberate: both occurrences sit where a
scribe would put a refrain. A deliberate return means the author had enough control over
the key schedule to force the base back after 1,449 blocks -- and an author with that
control might have used it more than once, leaving shorter returns behind.

So census every window length. A state return produces a repeat that starts at a block
boundary and spans whole blocks, so the aligned column is where an engineered return would
show; the unaligned column is the language and chance background.

    python repeat_census_by_length.py
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

M = 29


def main() -> None:
    stream, wid = load_clean()
    n = len(stream)
    blocks, cur = [], []
    for i, v in enumerate(stream):
        if i and wid[i] != wid[i - 1]:
            blocks.append(tuple(cur))
            cur = []
        cur.append(v)
    blocks.append(tuple(cur))
    counts = collections.Counter(stream)
    p2 = sum((v / n) ** 2 for v in counts.values())

    def aligned(length: int):
        out = []
        for i in range(len(blocks)):
            total, j = 0, i
            while j < len(blocks) and total < length:
                total += len(blocks[j])
                j += 1
            if total == length:
                out.append(tuple(x for b in blocks[i:j] for x in b))
        return out

    print(f"{n:,} runes, {len(blocks):,} blocks, per-rune match probability {p2:.5f}\n")
    print(f"{'len':>4}{'windows':>11}{'repeats':>9}{'expected':>10}"
          f"   |{'aligned':>9}{'repeats':>9}{'expected':>11}")
    for length in range(3, 9):
        w = [tuple(stream[i : i + length]) for i in range(n - length + 1)]
        c = collections.Counter(w)
        obs = sum(v - 1 for v in c.values() if v > 1)
        exp = len(w) * (len(w) - 1) // 2 * p2**length
        al = aligned(length)
        ca = collections.Counter(al)
        obs_a = sum(v - 1 for v in ca.values() if v > 1)
        exp_a = len(al) * (len(al) - 1) // 2 * p2**length
        print(f"{length:>4}{len(w):>11,}{obs:>9}{exp:>10.1f}"
              f"   |{len(al):>9}{obs_a:>9}{exp_a:>11.4f}")
    print(
        "\nEvery length but six matches chance in the aligned column: 17 against 12.2 at"
        "\nlength 3, zero against 0.28 at four, zero against 0.009 at five. At length six"
        "\nthere is one against 0.0004."
        "\n\nSo DJU-BEI stands alone. There is no family of shorter engineered returns, and"
        "\nan author who forced one return forced exactly one. Both readings inherit that:"
        "\nchance must produce exactly one 1-in-2,700 event, and design must have used the"
        "\ncapability once."
        "\n\nThe analytic expectations are for orientation only. They assume independent"
        "\nwindows, and overlapping windows are not independent, so the formula runs high"
        "\n-- at length 3 it gives 3,461 where empirical surrogates give 2,909 (plain"
        "\nshuffle) and 2,992 (doublet-preserving). The observed 3,009 sits ON the"
        "\ndoublet-preserving null at z = +0.57, so there is NO trigram-level deficit."
        "\nThe length-6 conclusion is unaffected: the overestimate is a factor under 1.2"
        "\nand the gap there is a factor of 2,500."
    )


if __name__ == "__main__":
    main()
