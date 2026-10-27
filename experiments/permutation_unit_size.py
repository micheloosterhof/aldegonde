# ABOUTME: Bounds the size of the unit the words were permuted within, from below, by what a
# ABOUTME: permutation within k-word units leaves of the sentence-final long block at the mark.
"""How small could the permutation unit be?

The rubricated titles bound the unit from above: each title is a contiguous run of red
blocks, so no permutation carried a word out of its span. This bounds it from below. If
the words were permuted within consecutive units of k words, the sentence's long final
word stays inside the last unit, and the block before the mark keeps about one k-th of
the sentence-final lift. The body's pre-mark block is not lifted at all against a random
block of its own span, so small k is excluded and the question is how small.

The statistic is the last block's excess over the mean block of its span, E. Planted on
the author's solved sentences (joined at q = 0.40) and on joined prose at the body's span
lengths: units of k words counted from the end of the sentence, words permuted within
each unit, E averaged over draws. The body's E is read with a bootstrap over spans, and
each k is scored by how far the body sits below the planted value.

    python experiments/permutation_unit_size.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from order_survives_in_the_lengths import register_spans  # noqa: E402
from sentence_length_across_registers import REGISTERS, fetch  # noqa: E402
from sentences_do_not_end_long import join  # noqa: E402
from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: E402

SEED = 20261028
JOIN_RATE = 0.40
MIN_SPAN = 6
UNITS = (1, 2, 3, 4, 5, 6, 8, 10, 15, 0)  # 0 = the whole span
DRAWS = 200
BOOT = 2000


def permuted(span: list[int], k: int, rng: random.Random) -> list[int]:
    """Words permuted within units of k counted from the end; k = 0 permutes the span."""
    s = list(span)
    if k == 0 or k >= len(s):
        rng.shuffle(s)
        return s
    out = []
    cut = len(s) % k
    for start in ([0] if cut else []) + list(range(cut, len(s), k)):
        unit = s[start : start + k] if start else s[:cut]
        rng.shuffle(unit)
        out.extend(unit)
    return out


def excess(spans) -> float:
    """Mean over spans of (last block - mean block of the span)."""
    return float(np.mean([s[-1] - np.mean(s) for s in spans]))


def planted(spans, k: int, rng) -> tuple[float, float]:
    values = [excess([permuted(s, k, rng) for s in spans]) for _ in range(DRAWS)]
    return float(np.mean(values)), float(np.std(values, ddof=1))


def bootstrap(spans, rng) -> tuple[float, float]:
    e = np.array([s[-1] - np.mean(s) for s in spans])
    boots = [np.mean(rng.choice(e, len(e))) for _ in range(BOOT)]
    return float(e.mean()), float(np.std(boots, ddof=1))


def main() -> None:
    rng = random.Random(SEED)
    nrng = np.random.default_rng(SEED)
    body = [s for s in body_spans() if len(s) >= MIN_SPAN]
    author = [
        s
        for s in (join(list(s), JOIN_RATE, rng, forward=True) for s in author_spans())
        if len(s) >= MIN_SPAN
    ]
    prose = []
    for number in REGISTERS[:5]:
        path = fetch(number)
        if path is not None:
            prose += [
                s for s in register_spans(path, rng, JOIN_RATE) if len(s) >= MIN_SPAN
            ]
    # prose spans at the body's span-length distribution: match by resampling
    lengths = [len(s) for s in body]
    by_len: dict[int, list] = {}
    for s in prose:
        by_len.setdefault(len(s), []).append(s)
    matched = []
    for n in lengths:
        pool = by_len.get(n) or by_len.get(n - 1) or by_len.get(n + 1)
        if pool:
            matched.append(pool[rng.randrange(len(pool))])

    e_body, se_body = bootstrap(body, nrng)
    e_author, se_author = bootstrap(author, nrng)
    e_prose, se_prose = bootstrap(matched, nrng)
    print(
        f"spans of {MIN_SPAN}+ blocks: body {len(body)} (mean {np.mean(lengths):.1f} blocks),"
        f" author joined {len(author)}, prose joined and length-matched {len(matched)}"
    )
    print("\nlast block minus the span mean, as written:")
    print(f"  the body     {e_body:+.3f} +- {se_body:.3f}")
    print(f"  the author   {e_author:+.3f} +- {se_author:.3f}")
    print(f"  prose        {e_prose:+.3f} +- {se_prose:.3f}")

    print(
        f"\n{'unit k':>8}{'author planted':>18}{'z body':>9}{'prose planted':>18}{'z body':>9}"
    )
    for k in UNITS:
        ea, sa = planted(author, k, rng)
        ep, sp = planted(matched, k, rng)
        za = (e_body - ea) / (se_body**2 + sa**2) ** 0.5
        zp = (e_body - ep) / (se_body**2 + sp**2) ** 0.5
        label = "whole span" if k == 0 else str(k)
        print(
            f"{label:>8}{ea:>+12.3f} +- {sa:.3f}{za:>9.2f}{ep:>+12.3f} +- {sp:.3f}{zp:>9.2f}"
        )
    print(
        "\n  k = 1 is the order as written; the planted value at each k is what the body's"
        "\n  pre-mark block would read if the words had been permuted within k-word units."
    )


if __name__ == "__main__":
    main()
