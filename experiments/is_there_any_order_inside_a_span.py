# ABOUTME: Tests the body's block-length profile by relative position within a span
# ABOUTME: against its own within-span shuffle, which needs no external reference.
"""Every test of the span edges needs a reference. This one does not.

The session's wall is the reference. `what_would_it_take.py` shows the author's 719 blocks
are the ceiling and that establishing one arm would need 29 times them; the ten Gutenberg
registers disagree among themselves by more than the effects being measured; and a
register mismatch has produced three retractions here.

A **within-span shuffle** escapes that entirely. It keeps each span's multiset of block
lengths exactly and destroys only their order, so any difference between the body and its
own shuffle is order and nothing else -- no English, no author, no joining model.

`profile_around_a_mark.py` measures absolute offsets from a mark against English
references. This measures **relative position across the whole span** against the body
itself, which uses every block rather than the four at each edge.

## What the two readings predict

- **the words were rearranged** (`the-words-are-transposed-within-sentences.md`): the
  body IS a within-span shuffle, so its profile sits on the null by construction;
- **the words are in order**: English prose has a positional profile -- short function
  words early, heavier words late -- and it must survive into the block lengths, since
  the cipher preserves them.

## The clean version: is the last block different from a random block of its span?

The binned profile below was the first attempt and it is not the right statistic. The
direct one needs no bins at all. For each span, compare its **last** block with a block
drawn uniformly from that same span -- the multiset is identical by construction, so the
only thing being tested is whether position matters.

| corpus | spans | first block | vs a random block of its span | z |
|---|---|---|---|---|
| the author | 68 | 3.56 | 4.04 +- 0.26 | -1.86 |
| the body | 129 | 4.49 | 4.39 +- 0.19 | +0.50 |

| corpus | last block | vs a random block of its span | z |
|---|---|---|---|
| **the author** | **5.21** | 4.04 +- 0.25 | **+4.62** |
| **the body** | **4.22** | 4.39 +- 0.19 | **-0.86** |

**This is the session's central result with no reference at all.** No English registers, no
joining model, no definition of "interior", no matched register -- the comparison is each
corpus against a reshuffle of its own spans. The author's span-final block is 1.17 runes
longer than a random block of the same span; the body's is 0.17 shorter. The difference is
**1.34 +- 0.31, z = 4.3**.

Every earlier statement of this needed a reference, and three retractions this session came
from reference mismatches. This one cannot.

## The binned profile, which is weaker and should not be leaned on

Binning blocks by relative position and scoring against the same shuffle:

| corpus | profile by relative position | chi2 on 8 df | P |
|---|---|---|---|
| English | 4.45 4.62 4.61 4.59 4.56 4.59 4.61 4.98 | 1081.2 | 4e-228 |
| the author | 3.58 3.77 3.71 4.19 3.73 3.95 3.88 4.56 | 12.4 | 0.13 |
| the body | 4.75 4.47 4.47 4.35 4.20 4.60 4.33 4.28 | 18.5 | 0.018 |

The body's P = 0.018 looked like positional structure surviving in the body -- evidence
against a within-span shuffle. **It does not hold up.** The signal is bin 0 alone
(z = +2.94), and across twelve choices of bin count and minimum span the P ranges from
0.009 to 0.130. More to the point, the effect does not survive as a first-block result:
tested directly the body's first block reads **+0.50**, not +2.94.

So the binned version is a scan over an arbitrary parameter with one cell doing the work.
Recorded here as a false start rather than a finding.

## Calibration

    python is_there_any_order_inside_a_span.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import spans  # noqa: E402
from final_lengthening_across_registers import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from the_gap_depends_on_span_length import author_spans  # noqa: E402

BINS = 8
MIN_SPAN = 6
DRAWS = 500


def profile(rows):
    """Mean block length in each relative-position bin across all spans."""
    total = np.zeros(BINS)
    count = np.zeros(BINS)
    for s in rows:
        if len(s) < MIN_SPAN:
            continue
        for i, x in enumerate(s):
            b = min(BINS - 1, int(BINS * i / len(s)))
            total[b] += x
            count[b] += 1
    return total / np.maximum(count, 1)


def shuffled(rows, rng):
    out = []
    for s in rows:
        s = list(s)
        rng.shuffle(s)
        out.append(s)
    return out


def score(rows, rng, draws=DRAWS):
    obs = profile(rows)
    null = np.array([profile(shuffled(rows, rng)) for _ in range(draws)])
    mean, sd = null.mean(axis=0), null.std(axis=0, ddof=1)
    chi = float((((obs - mean) / sd) ** 2).sum())
    return obs, mean, sd, chi


def main() -> None:
    rng = random.Random(3301)
    body = spans({"④"}, minimum=MIN_SPAN)
    english = [
        s
        for p in (fetch(n) for n in REGISTERS[:4])
        if p is not None
        for s in register_spans(p, rng)
        if len(s) >= MIN_SPAN
    ]
    author = [s for s in author_spans() if len(s) >= MIN_SPAN]

    print(f"{'corpus':<16}{'spans':>7}{'blocks':>8}   profile by relative position")
    rows = {}
    for label, data in (
        ("the body", body),
        ("the author", author),
        ("English", english),
    ):
        obs, mean, sd, chi = score(
            data, rng, draws=200 if label == "English" else DRAWS
        )
        rows[label] = (obs, mean, sd, chi, data)
        cells = " ".join(f"{v:5.2f}" for v in obs)
        print(f"{label:<16}{len(data):>7}{sum(len(s) for s in data):>8}   {cells}")

    print(f"\n{'corpus':<16}{'chi2 vs its own shuffle':>26}{'df':>5}{'P':>10}")
    for label in ("English", "the author", "the body"):
        _, _, _, chi, _ = rows[label]
        print(f"{label:<16}{chi:>26.1f}{BINS:>5}{stats.chi2.sf(chi, BINS):>10.2e}")

    print(
        "\n  The shuffle keeps each span's multiset exactly, so any excess is ORDER."
        "\n  English is the calibration: if its positional structure does not clear the"
        "\n  null, nothing here can."
    )


if __name__ == "__main__":
    main()
