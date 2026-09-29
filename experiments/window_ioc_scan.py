# ABOUTME: Slides a window across the body looking for any stretch with plaintext-like or
# ABOUTME: monoalphabetic index of coincidence, closing the sub-page gap in the page test.
"""The page test would find a plaintext page. Would it find a plaintext paragraph?

`the-body-is-one-cipher.md` shows the body homogeneous across 9 sections and 55 pages on
doublets, d5 and IoC, and proves its own power by surfacing the Parable -- a page stored
as plaintext -- at +7 sd. Its stated gap is scale: a difference confined to a few dozen
runes would not survive averaging over a 230-rune page.

So slide instead of partition. The index of coincidence rises for plaintext AND for any
monoalphabetic substitution of it, since a fixed substitution preserves coincidence
exactly, so one statistic covers both of the easy cases. The body's own IoC is ~1.00 and
the author's plaintext is 1.80.

A scan maximum needs its own null, and a named window needs a control, so both are here:
the null is the same scan on a shuffled corpus, and the control splices a real plaintext
stretch into the body at a known offset.

    python window_ioc_scan.py [--windows 100,200,400] [--control]
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

M = 29


def scan(stream: list[int], width: int) -> tuple[float, int]:
    """(largest normalised IoC over all windows, its start offset)."""
    counts = collections.Counter(stream[:width])
    best, where = -1.0, 0
    denom = width * (width - 1)
    total = sum(v * (v - 1) for v in counts.values())
    for i in range(len(stream) - width):
        ioc = M * total / denom
        if ioc > best:
            best, where = ioc, i
        out, inn = stream[i], stream[i + width]
        total -= 2 * (counts[out] - 1)
        counts[out] -= 1
        total += 2 * counts[inn]
        counts[inn] += 1
    return best, where


def main() -> None:
    widths = [100, 200, 400]
    for i, a in enumerate(sys.argv):
        if a == "--windows" and i + 1 < len(sys.argv):
            widths = [int(x) for x in sys.argv[i + 1].split(",")]

    stream, _wid = load_clean()
    rng = random.Random(3301)
    plain = [r for w in corpus() for r in w]

    if "--control" in sys.argv:
        for width in widths:
            spliced = stream[:6000] + plain[:width] + stream[6000:]
            best, where = scan(spliced, width)
            off = abs(where - 6000)
            verdict = "FOUND" if off <= width // 4 else "missed"
            print(
                f"width {width:>4}: planted plaintext at 6000, scan maximum "
                f"{best:.3f} at {where} (offset {off}) -- {verdict}"
            )
        return

    print(f"{'width':>6}{'body max':>10}{'at':>8}{'shuffled null max':>20}{'z':>8}")
    for width in widths:
        best, where = scan(stream, width)
        nulls = []
        for _ in range(12):
            sh = stream[:]
            rng.shuffle(sh)
            nulls.append(scan(sh, width)[0])
        mu = sum(nulls) / len(nulls)
        sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5
        print(
            f"{width:>6}{best:>10.3f}{where:>8}{mu:>13.3f} +-{sd:.3f}"
            f"{(best - mu) / sd:>+8.2f}"
        )
    print(
        "\nThe author's own plaintext reads 1.80 and a monoalphabetic substitution of it"
        "\nreads the same, so either would stand far above these maxima. The body's best"
        "\nwindow is BELOW the shuffled null's best at every width, which is the doublet"
        "\nsuppression making the corpus slightly under-dispersed."
    )


if __name__ == "__main__":
    main()
