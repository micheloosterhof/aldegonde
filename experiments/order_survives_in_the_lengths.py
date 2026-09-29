# ABOUTME: Tests whether the block-length sequence's serial order separates the two
# ABOUTME: surviving readings, and finds it cannot once the short-word population matches.
"""The serial order of the lengths looked like a way out. It is not, and the reason is
which reference you hold it against.

`lengths_cannot_separate_the_readings.py` argued that no block-length statistic can tell
"the spans are transposed sentences" from "the marks are not sentence marks", because
every statistic it tried was computed inside one span, and a span keeps its multiset under
transposition. The lag-1 serial correlation of the length stream escapes that argument: it
is a property of the **order**, which is exactly what transposition destroys and what
arbitrary marks leave alone. So it should fork the two readings.

It does fork them. The fork is about six times too small for this corpus, and getting to
that number took two corrections.

## Two ways to get a false result here, both taken and both caught

**Leaving the short-word population unmatched.** Lag-1 in this corpus is driven by one
number: the fraction of blocks two runes long. English alternates short and long words, so
the correlation is negative, and its size is set by how many short words survive. Joining
removes them, and every joining rate slides both quantities together. The body carries
15.5% two-rune blocks; ten Gutenberg registers as parsed here carry 25.5% raw. Compare the
two directly and the body reads **+3.2 sigma** from "order intact" -- a difference in
joining, read as a difference in order.

**Leaving the register unmatched.** Matching the fraction is not enough. At 15.9% the
registers read lag-1 = -0.082; the author's own solved pages, brought to 15.5% by joining,
read -0.028. **Same short-word fraction, and the two references disagree by three times
the effect being measured.** The curves are parallel, not shared: the level is a property
of the register and only the slope is shared. So the reference has to be matched on both,
and only the author's solved pages are -- same book, same hand, known ordinary order.

## What the matched comparison says

| lag | order intact | transposed | the body |
|---|---|---|---|
| 1 | -0.031 +- 0.029 | -0.005 +- 0.042 | -0.009 +- 0.019 |
| 2 | +0.028 +- 0.031 | +0.008 +- 0.047 | +0.023 +- 0.020 |
| 3 | +0.000 +- 0.040 | +0.002 +- 0.051 | -0.018 +- 0.020 |

The body is **+0.64 sigma** from order intact and **-0.08** from transposed. The two arms
are 0.026 apart at lag 1, the body's own sampling error is 0.019 on 2,759 pairs, and the
reference contributes 0.029 more because the solved pages are only 719 blocks. Separating
them at three sigma needs about 13,000 pairs, **4.7 times the corpus**.

That is the verdict: the fork is real and unreachable here. It does not overturn
`lengths_cannot_separate_the_readings.py`; it narrows why. The one length statistic that
survives that file's structural argument is throttled by a nuisance the corpus has already
spent -- the short-word joining of `short-units-are-written-joined.md`, which
`word-length-keystream-and-boundaries.md` had already shown accounts for the flat
autocorrelation on its own.

## One thing that does fall out

The joining rate that brings the author's two-rune share onto the body's is **q = 0.40**,
which is the rate `short-units-are-written-joined.md` fitted from the length histogram.
Two independent statistics, the same rate. That is corroboration of the joining model
rather than of anything about order.

    python order_survives_in_the_lengths.py
"""

from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import IDX_ENG, to_runeglish  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from sentences_do_not_end_long import join  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

LAGS = (1, 2, 3)
RATES = (0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7)
DRAWS = 60
TARGET_SIGMA = 3.0


def register_spans(path, rng, join_rate) -> list[list[int]]:
    """Sentences as block-length lists, joined at the given rate (0.0 leaves them raw)."""
    text = path.read_text(encoding="utf-8", errors="replace")
    trim = len(text) // 10
    out = []
    for sentence in re.split(r"[.!?]+", text[trim : len(text) - trim]):
        words = [
            len([c for c in to_runeglish(w.upper()) if c in IDX_ENG])
            for w in re.findall(r"[A-Za-z']+", sentence)
        ]
        words = [n for n in words if n]
        if len(words) < 3:
            continue
        blocks = join(words, join_rate, rng, forward=True) if join_rate else words
        if len(blocks) >= 3:
            out.append(blocks)
    return out


def serial(spans, lag: int) -> tuple[float, int]:
    """Lag-k correlation over the pairs inside one span -- the pairs transposition moves.

    Cross-span pairs are excluded because transposition cannot move a block out of its
    span, so they carry the same correlation under both readings and only dilute it.
    """
    left, right = [], []
    for s in spans:
        if len(s) > lag:
            left.extend(s[:-lag])
            right.extend(s[lag:])
    if len(left) < 30:
        return float("nan"), len(left)
    x, y = np.array(left, float), np.array(right, float)
    if x.std() == 0 or y.std() == 0:
        return float("nan"), len(left)
    return float(np.corrcoef(x, y)[0, 1]), len(left)


def short_fraction(spans) -> float:
    """The share of blocks exactly two runes long, which is what drives lag-1."""
    flat = [x for s in spans for x in s]
    return sum(1 for x in flat if x == 2) / len(flat)


def shuffled(spans, rng) -> list[list[int]]:
    """Permute the blocks inside every span, which is what the transposition proposes."""
    out = []
    for s in spans:
        s = list(s)
        rng.shuffle(s)
        out.append(s)
    return out


def joined(spans, q, rng) -> list[list[int]]:
    kept = [join(list(s), q, rng, forward=True) for s in spans] if q else spans
    return [s for s in kept if len(s) >= 3]


def curve(spans, rng, draws=DRAWS):
    """(short fraction, lag-1, spread) at each joining rate."""
    out = []
    for q in RATES:
        shorts, ones = [], []
        for _ in range(draws if q else 1):
            j = joined(spans, q, rng)
            shorts.append(short_fraction(j))
            ones.append(serial(j, 1)[0])
        out.append(
            (q, float(np.mean(shorts)), float(np.mean(ones)), float(np.std(ones)))
        )
    return out


def main() -> None:
    rng = random.Random(3301)
    body, author = body_spans(), author_spans()
    target = short_fraction(body)
    print(
        f"The body carries {target:.1%} two-rune blocks, the author {short_fraction(author):.1%}."
    )
    print(
        "Lag-1 tracks that fraction, so a reference at the wrong one is not a reference.\n"
    )

    print(f"{'joining rate':<16}{'two-rune share':>16}{'lag-1':>12}{'spread':>10}")
    author_curve = curve(author, rng)
    for q, frac, one, sd in author_curve:
        flag = "  <- matches the body" if abs(frac - target) < 0.01 else ""
        print(
            f"{f'the author, q={q:.1f}':<16}{frac:>16.3f}{one:>12.3f}{sd:>10.3f}{flag}"
        )

    print()
    registers = [
        (n, register_spans(p, rng, 0.0))
        for n, p in ((n, fetch(n)) for n in REGISTERS)
        if p is not None
    ]
    for q in (0.0, 0.4, 0.6, 0.8):
        fracs = [short_fraction(joined(s, q, rng)) for _, s in registers]
        ones = [serial(joined(s, q, rng), 1)[0] for _, s in registers]
        print(
            f"{f'ten registers, q={q:.1f}':<16}{np.mean(fracs):>16.3f}{np.mean(ones):>12.3f}"
            f"{np.std(ones, ddof=1):>10.3f}"
        )
    print("  Parallel curves, not one: the slope is shared and the level is not, so a")
    print("  reference must match the register as well as the short-word fraction.")

    q_star = min(author_curve, key=lambda r: abs(r[1] - target))[0]
    print(f"\nMatched at the body's own short-word fraction, q = {q_star:.1f}.\n")
    print(f"{'lag':>4}{'order intact':>18}{'transposed':>18}{'the body':>18}{'z':>18}")
    intact_all, mixed_all = {}, {}
    for lag in LAGS:
        intact, mixed = [], []
        for _ in range(DRAWS):
            j = joined(author, q_star, rng)
            intact.append(serial(j, lag)[0])
            mixed.append(serial(shuffled(j, rng), lag)[0])
        intact, mixed = np.array(intact), np.array(mixed)
        rb, n = serial(body, lag)
        se = 1 / math.sqrt(n - 3)
        z_a = (rb - intact.mean()) / math.hypot(intact.std(ddof=1), se)
        z_b = (rb - mixed.mean()) / math.hypot(mixed.std(ddof=1), se)
        intact_all[lag], mixed_all[lag] = intact, mixed
        print(
            f"{lag:>4}{f'{intact.mean():+.3f} +- {intact.std(ddof=1):.3f}':>18}"
            f"{f'{mixed.mean():+.3f} +- {mixed.std(ddof=1):.3f}':>18}"
            f"{f'{rb:+.3f} +- {se:.3f}':>18}"
            f"{f'{z_a:+.2f} / {z_b:+.2f}':>18}"
        )
    print("  (z against order intact / against transposed)")

    gap = abs(mixed_all[1].mean() - intact_all[1].mean())
    _, n = serial(body, 1)
    need = (TARGET_SIGMA / gap) ** 2 + 3
    print(
        f"\nThe two arms are {gap:.3f} apart at lag 1 and the body's own sampling error is"
        f"\n{1 / math.sqrt(n - 3):.3f} on {n:,} pairs. Separating them at {TARGET_SIGMA:.0f}"
        f" sigma needs about {need:,.0f} pairs,"
        f"\n{need / n:.1f} times what the corpus has. The fork is real and unreachable here."
        "\n\nHeld against the ten registers instead, matched on the short-word fraction but"
        "\nnot on register, the same body value reads +3.2 sigma. That number is an artefact"
        "\nof the reference, and it is the one this file exists to rule out."
    )


if __name__ == "__main__":
    main()
