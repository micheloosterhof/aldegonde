# ABOUTME: Measures sentence-length dispersion across ten English registers, showing the
# ABOUTME: body's mark spacing is ordinary and withdrawing the under-recording hypothesis.
"""The body's mark spacing is not over-dispersed. Ten registers say so; one did not.

`what-the-marks-space-like` compared the body's span-length dispersion against **Pride
and Prejudice alone** and found it high -- CV 0.972 against 0.771 -- and read that as
leaning towards the marks not falling at sentence ends, at 3:1 to 33:1. It flagged the
weakness in its own text: "the loud number depends on Austen standing in for the LP's
register". `the-marks-may-be-under-recorded.md` then built a hypothesis on that
dispersion plus the low mark rate.

Both rest on one book. Measuring sentence length in blocks -- after the body's own
joining model, so the unit matches -- across the ten prose registers this project already
uses:

| register | sentences | mean | CV |
|---|---|---|---|
| pg1342 | 5,850 | 16.04 | 0.846 |
| pg205 | 3,305 | 25.38 | 0.832 |
| pg16643 | 4,284 | 16.12 | 0.824 |
| pg2945 | 2,194 | 20.20 | 0.730 |
| pg4363 | 1,475 | 32.84 | 0.941 |
| pg3296 | 2,895 | 27.87 | 0.761 |
| pg1497 | 7,182 | 21.53 | 0.898 |
| pg14209 | 1,135 | 21.50 | 0.645 |
| pg2680 | 2,526 | 20.78 | 0.931 |
| pg131 | 2,600 | 15.97 | **1.068** |
| **the LP body** | **148** | **19.57** | **0.972 +- 0.145** |
| the LP author's pages | 92 | 7.86 | 0.738 |

English registers run **0.645 to 1.068**, mean 0.848 +- 0.120. The body sits at
**z = +0.66** and one register exceeds it. Its mean span of 19.6 blocks is ordinary too,
against a register range of 16.0 to 32.8.

## Two consequences

**The over-dispersion is not real, so `the-marks-may-be-under-recorded.md` loses both its
motivations.** That hypothesis was built to explain a low mark rate and a high dispersion
with one parameter. Neither needs explaining: the body's spacing is ordinary prose, and
the author's pages are short because they are aphoristic -- "A WARNNG.", "WELCOME.",
"SOME WISDOM." -- at 7.86 blocks a span. p = 1.

**The shape evidence narrows.** Mean-normalised, two-sample KS:

    the body against all ten registers pooled   D = 0.095, P = 0.134
    the body against random placement           D = 0.064, P = 0.580

English is no longer rejected. Against individual registers the body survives 3 of 10 at
P > 0.05, which is what a sample of 148 spans against a wide register spread should look
like. Random still fits better, but the ratio is nearer 4:1 than the 33:1 recorded
against Austen alone.

    python sentence_length_across_registers.py
"""

from __future__ import annotations

import math
import pathlib
import random
import re
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import IDX_ENG, to_runeglish  # noqa: E402
from profile_around_a_mark import author_spans  # noqa: E402
from sentences_do_not_end_long import join  # noqa: E402
from what_the_marks_space_like import (  # noqa: E402
    body_spans,
    cv,
    cv_jackknife,
    random_spans,
)

REGISTERS = (1342, 205, 16643, 2945, 4363, 3296, 1497, 14209, 2680, 131)
JOIN_RATE = 0.40
CACHE = pathlib.Path(tempfile.gettempdir())


def fetch(number: int) -> pathlib.Path | None:
    path = CACHE / f"pg{number}.txt"
    if path.exists() and path.stat().st_size > 50_000:
        return path
    for url in (
        f"https://www.gutenberg.org/files/{number}/{number}-0.txt",
        f"https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt",
        f"https://www.gutenberg.org/files/{number}/{number}.txt",
    ):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                data = response.read()
        except (urllib.error.URLError, OSError, TimeoutError):
            continue
        if len(data) > 50_000:
            path.write_bytes(data)
            return path
    return None


def sentence_blocks(path, rng) -> np.ndarray:
    """Sentence length in BLOCKS, after applying the body's own joining model."""
    text = path.read_text(encoding="utf-8", errors="replace")
    trim = len(text) // 10
    out = []
    for sentence in re.split(r"[.!?]+", text[trim : len(text) - trim]):
        words = [
            len([c for c in to_runeglish(w.upper()) if c in IDX_ENG])
            for w in re.findall(r"[A-Za-z']+", sentence)
        ]
        words = [n for n in words if n]
        if words:
            out.append(len(join(words, JOIN_RATE, rng, forward=True)))
    return np.array([n for n in out if n > 0], float)


def main() -> None:
    rng = random.Random(3301)
    spans, n_blocks = body_spans()
    observed, observed_se = cv_jackknife(spans)
    author = np.array([len(s) for s in author_spans()], float)

    print("Sentence length in blocks, after the body's joining model.\n")
    print(f"{'register':<14}{'sentences':>11}{'mean':>8}{'CV':>9}")
    lengths = {}
    for number in REGISTERS:
        path = fetch(number)
        if path is None:
            print(f"pg{number:<12}{'unavailable':>11}")
            continue
        v = sentence_blocks(path, rng)
        lengths[number] = v
        print(f"pg{number:<12}{len(v):>11,}{v.mean():>8.2f}{cv(v):>9.3f}")

    spread = np.array([cv(v) for v in lengths.values()])
    print(
        f"\n{'across the registers':<14}{'':>11}{'':>8}"
        f"{f'{spread.mean():.3f} +- {spread.std(ddof=1):.3f}':>9}"
    )
    print(f"{'range':<14}{'':>11}{'':>8}{f'{spread.min():.3f}-{spread.max():.3f}':>9}")
    print(
        f"\n{'the LP body':<14}{len(spans):>11}{spans.mean():>8.2f}"
        f"{f'{observed:.3f}':>9} +- {observed_se:.3f}"
    )
    print(f"{'the author':<14}{len(author):>11}{author.mean():>8.2f}{cv(author):>9.3f}")
    z = (observed - spread.mean()) / math.hypot(observed_se, spread.std(ddof=1))
    print(f"\n  the body against the register spread: z = {z:+.2f}")
    print(
        f"  registers reaching the body's CV: {int((spread >= observed).sum())} of "
        f"{len(spread)}"
    )

    def norm(v):
        return v / v.mean()

    pooled = np.concatenate(list(lengths.values()))
    random_pool = np.concatenate(
        [random_spans(random.Random(i), n_blocks, len(spans)) for i in range(40)]
    )
    print("\nMean-normalised shape, two-sample KS.\n")
    print(f"{'against':<26}{'D':>8}{'P':>9}")
    for label, v in (("all ten registers", pooled), ("random placement", random_pool)):
        ks = stats.ks_2samp(norm(spans), norm(v))
        print(f"{label:<26}{ks.statistic:>8.3f}{ks.pvalue:>9.3f}")
    survive = sum(
        1
        for v in lengths.values()
        if stats.ks_2samp(norm(spans), norm(v)).pvalue > 0.05
    )
    print(
        f"\n  individual registers the body survives at P > 0.05: {survive} of "
        f"{len(lengths)}"
    )

    print(
        "\nThe body's spacing is ordinary prose on both the mean and the dispersion, so"
        "\nthe under-recording hypothesis loses both facts it was built to explain, and"
        "\nthe author's short spans are simply aphoristic writing. English is no longer"
        "\nrejected on shape either: the 33:1 recorded against Austen alone was that one"
        "\nbook standing in for a spread running 0.645 to 1.068."
    )


if __name__ == "__main__":
    main()
