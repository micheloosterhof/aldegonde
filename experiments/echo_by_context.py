# ABOUTME: Checks that the within-block distance-5 sharing is the same in every layout context:
# ABOUTME: closing glyph, preceding glyph, line wrap, section, against one pooled rate.
"""Is the five-apart sharing universal across contexts?

The within-block d5 rate is a single pooled number. If the sharing were switched on or
off by something the scribe wrote -- the glyph that closes the block, the glyph before
it, whether the block wraps a line -- the rate would differ by context. Each context's
rate is compared with the pooled rate (binomial z) and the contexts of one kind are
tested for homogeneity (chi-square over unequal exposures). Section by section is on
record as positive in 8 of 9; it is repeated here for completeness.

    python experiments/echo_by_context.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from aldegonde import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from frame_feature_nulls import PLAIN_SEPARATOR, Layout  # noqa: E402
from within_word_d5 import parse_clean_sections  # noqa: E402

LAG = 5


def glyph_class(g: str) -> str:
    return g if g in (PLAIN_SEPARATOR, "④", "⑬", "%") else "other"


def main() -> None:
    layout = Layout(ROOT / "data/page0-56.txt")
    sections = parse_clean_sections(str(ROOT / "data/page0-56.txt"))
    words = [w for s in sections for w in s]
    starts = []
    pos = 0
    for w in words:
        starts.append(pos)
        pos += len(w)

    contexts: dict[str, dict[str, list[int]]] = defaultdict(
        lambda: defaultdict(lambda: [0, 0])
    )
    for k, w in enumerate(words):
        pairs = len(w) - LAG
        if pairs <= 0:
            continue
        hits = sum(w[i] == w[i + LAG] for i in range(pairs))
        s = starts[k]
        keys = {
            "closing glyph": glyph_class(layout.closer[k]),
            "preceding glyph": glyph_class(layout.closer[k - 1]) if k else "start",
            "line wrap": "wraps"
            if any(layout.line_start[s + i] for i in range(1, len(w)))
            else "one line",
            "opens a line": "yes" if layout.line_start[s] else "no",
            "section": str(layout.section[s]),
        }
        for kind, value in keys.items():
            contexts[kind][value][0] += hits
            contexts[kind][value][1] += pairs

    total_hits = sum(
        sum(w[i] == w[i + LAG] for i in range(len(w) - LAG))
        for w in words
        if len(w) > LAG
    )
    total_pairs = sum(len(w) - LAG for w in words if len(w) > LAG)
    pooled = total_hits / total_pairs
    print(f"within-block d5: {total_hits} of {total_pairs} = {pooled:.4f}\n")
    for kind, table in contexts.items():
        rows = sorted(table.items(), key=lambda kv: -kv[1][1])
        print(f"{kind}")
        for value, (hits, pairs) in rows:
            z = stats.binomial_z(hits, pairs, pooled)
            print(
                f"  {value:<10} {hits:>4} / {pairs:<5} {hits / pairs:.4f}  z {z:>+5.2f}"
            )
        usable = {value: (pairs, hits) for value, (hits, pairs) in rows if pairs >= 30}
        if len(usable) >= 2:
            r = stats.rate_uniformity(usable)
            print(f"  homogeneity: chi2 {r.chi2:.1f} on {r.df} df, p = {r.p:.2f}\n")
        else:
            print()


if __name__ == "__main__":
    main()
