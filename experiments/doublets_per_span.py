# ABOUTME: Tests whether the doublet deficit was made by choosing each span's word order, by
# ABOUTME: the dispersion of doublet counts per four-dot span and their trend with span length.
"""Could the word permutation be the doublet avoider?

Each block's alphabets depend on its position, so permuting a sentence's words changes
every doublet in it, inside blocks and at seams. An encipherer who tried orderings until a
sentence came out nearly doublet-free would get the body's fourfold deficit with no rule
at run time. Selection on the count leaves two marks that a per-rune preventer does not:

- **under-dispersion**: spans are pushed toward the same low count, so the variance of
  doublets per span falls below its mean (a hard cap of one gives a Fano factor near
  0.4; a per-pair rule gives 1);
- **a length gradient**: with a fixed number of tries, long spans keep more doublets per
  pair than short ones, because a long span is harder to clear.

Both are read against a binomial null in which every adjacent pair inside a span is a
doublet independently at the body's own pooled rate, and against a planted selector:
best-of-k orderings at the chance rate, with k set so the total matches the body's.

    python experiments/doublets_per_span.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from frame_feature_nulls import Layout  # noqa: E402
from within_word_d5 import M, parse_clean_sections  # noqa: E402

SEED = 20261028
DRAWS = 20000
MARK = "④"
CHANCE = 1 / M


def spans_of_runes(path: Path) -> list[list[int]]:
    """Rune streams of the four-dot spans, each closed by a mark or a section end."""
    layout = Layout(path)
    stream = [r for sec in parse_clean_sections(str(path)) for w in sec for r in w]
    assert len(stream) == len(layout.word)
    out, cur = [], []
    for i, r in enumerate(stream):
        cur.append(r)
        last_of_word = i + 1 == len(stream) or layout.word[i + 1] != layout.word[i]
        section_end = i + 1 == len(stream) or layout.section[i + 1] != layout.section[i]
        if last_of_word and (layout.closer[layout.word[i]] == MARK or section_end):
            out.append(cur)
            cur = []
    return out


def doublets(span: list[int]) -> int:
    return sum(a == b for a, b in zip(span, span[1:]))


def dispersion(counts: np.ndarray, expected: np.ndarray) -> float:
    return float(((counts - expected) ** 2 / expected).sum())


def summarise(label: str, counts: np.ndarray, pairs: np.ndarray, rng) -> None:
    rate = counts.sum() / pairs.sum()
    expected = pairs * rate
    fano = counts.var(ddof=1) / counts.mean()
    d_obs = dispersion(counts, expected)
    sims = rng.binomial(pairs[None, :], rate, size=(DRAWS, len(pairs)))
    d_null = np.array([dispersion(s, expected) for s in sims])
    fano_null = sims.var(axis=1, ddof=1) / sims.mean(axis=1)
    hist = np.bincount(counts, minlength=4)
    hist = np.append(hist[:3], hist[3:].sum())
    hist_null = np.array(
        [
            (sims == 0).sum(1).mean(),
            (sims == 1).sum(1).mean(),
            (sims == 2).sum(1).mean(),
            (sims >= 3).sum(1).mean(),
        ]
    )
    order = np.argsort(pairs)
    terciles = np.array_split(order, 3)
    trend = [counts[t].sum() / pairs[t].sum() for t in terciles]
    trend_null = [(sims[:, t].sum(1) / pairs[t].sum()).std() for t in terciles]
    print(
        f"\n{label}: {len(counts)} spans, {counts.sum()} doublets on {pairs.sum()} pairs"
    )
    print(
        f"  Fano factor {fano:.3f}  (binomial null {fano_null.mean():.3f} +- {fano_null.std():.3f},"
        f" P(<= obs) = {(fano_null <= fano).mean():.3f})"
    )
    print(
        f"  dispersion statistic {d_obs:.1f} on {len(counts) - 1} df"
        f"  (null {d_null.mean():.1f} +- {d_null.std():.1f}, P(<= obs) = {(d_null <= d_obs).mean():.3f})"
    )
    print(
        "  spans with 0 / 1 / 2 / 3+ doublets: "
        + " / ".join(f"{int(h)}" for h in hist)
        + "   expected "
        + " / ".join(f"{h:.1f}" for h in hist_null)
    )
    print(
        "  doublets per pair by span-length tercile (short, middle, long): "
        + ", ".join(f"{t:.4f} +- {s:.4f}" for t, s in zip(trend, trend_null))
    )


def planted_selector(pairs: np.ndarray, target: int, rng) -> tuple[np.ndarray, int]:
    """Best-of-k doublet counts at the chance rate, k chosen so the mean total is `target`."""
    k = 1
    while True:
        totals = [
            rng.binomial(pairs[None, :], CHANCE, size=(k, len(pairs))).min(axis=0).sum()
            for _ in range(200)
        ]
        if np.mean(totals) <= target or k > 200:
            break
        k += 1
    counts = rng.binomial(pairs[None, :], CHANCE, size=(k, len(pairs))).min(axis=0)
    return counts, k


def main() -> None:
    rng = np.random.default_rng(SEED)
    spans = spans_of_runes(ROOT / "data/page0-56.txt")
    counts = np.array([doublets(s) for s in spans])
    pairs = np.array([len(s) - 1 for s in spans])
    boundary = sum(a[-1] == b[0] for a, b in zip(spans, spans[1:]))
    print(
        f"{len(spans)} spans; doublets inside spans {counts.sum()}, across span boundaries {boundary}"
        f" ({len(spans) - 1} boundary pairs, chance {(len(spans) - 1) * CHANCE:.1f})"
    )
    summarise("the body", counts, pairs, rng)

    planted, k = planted_selector(pairs, int(counts.sum()), rng)
    summarise(
        f"planted selector, best of k = {k} orderings at chance", planted, pairs, rng
    )


if __name__ == "__main__":
    main()
