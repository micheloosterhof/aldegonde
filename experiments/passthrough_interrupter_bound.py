# ABOUTME: Bounds how much of the unsolved body could be a pass-through interrupter, using
# ABOUTME: the flat unigram distribution; excludes the literal form of 3301's own device.
"""3301 uses an interrupter. Does the unsolved body use the same one?

`solved-page-testbed.md` establishes the device from the author's own solved pages:
on pages 1, 2, 12 and 13 a ciphertext ᚠ can be a literal plaintext F that consumes no
key letter. Pages 1 and 2 carry nine such interrupts in 515 runes, a rate of 1.75%.

That form of interrupter is PASS-THROUGH: the rune bypasses encipherment and appears
in the ciphertext as itself. So it must show up in the unigram distribution. If a
fraction q of the body's runes were pass-through copies of some rune x, then

    rate(x) = q + (1 - q) / 29     hence     q = (rate(x) - 1/29) / (1 - 1/29)

and the body's flat unigrams (`flat-ioc.md`, chi2 26.4 on 28 df) turn that into an
upper bound on q for every rune at once. No key, no model and no search is needed --
the bound follows from the frequency table.

The scope is narrow and worth stating precisely. This bounds only interrupters that
EMIT the rune. A clock perturbation that skips a key step while still enciphering the
rune (the `quagmire-dodge.md` and `interrupted-walk.md` families) leaves no unigram
trace and is untouched by this measurement.

    python passthrough_interrupter_bound.py
"""

from __future__ import annotations

import collections
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
P0 = 1 / M
ENG = c3301.CICADA_ENGLISH_ALPHABET


def bounds(stream: list[int]) -> list[tuple[float, float, int, int]]:
    """(q_hat, 95% one-sided upper bound, count, rune) for every rune."""
    n = len(stream)
    counts = collections.Counter(stream)
    out = []
    for i in range(M):
        rate = counts[i] / n
        q = (rate - P0) / (1 - P0)
        se = math.sqrt(rate * (1 - rate) / n) / (1 - P0)
        out.append((q, q + 1.645 * se, counts[i], i))
    return out


def main() -> None:
    stream, _wid = load_clean()
    n = len(stream)
    rows = bounds(stream)
    worst = max(rows, key=lambda t: t[1])

    print(f"unsolved body: {n:,} runes\n")
    print(f"{'rune':>5}{'count':>7}{'rate':>9}{'q_hat':>9}{'q upper':>10}{'runes':>8}")
    for q, up, count, i in sorted(rows, key=lambda t: -t[1])[:5]:
        print(
            f"{ENG[i]:>5}{count:>7}{count / n:>9.3%}{q:>9.4f}{up:>10.4f}{up * n:>8.0f}"
        )
    f_row = next(r for r in rows if r[3] == 0)
    print(
        f"\nthe author's own interrupter, F: q <= {f_row[1]:.4f} "
        f"({f_row[1] * n:.0f} runes of {n:,})"
    )
    print(
        f"the loosest bound over all 29 runes: {ENG[worst[3]]} at q <= {worst[1]:.4f} "
        f"({worst[1] * n:.0f} runes)"
    )
    print(
        "\nagainst 1.75% (9 interrupts in 515 runes) on solved pages 1 and 2, so a"
        f"\npass-through interrupter is excluded in the body by a factor of "
        f"{0.0175 / worst[1]:.1f} even at its most favourable rune."
    )
    print(
        "\nScope: this bounds only interrupters that EMIT the rune. A clock skip that"
        "\nstill enciphers the rune leaves no unigram trace and is not touched here."
    )


if __name__ == "__main__":
    main()
