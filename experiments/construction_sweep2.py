# ABOUTME: Broad construction sweep with a GRADED DJU-BEI score, so a slightly
# ABOUTME: wrong model ranks candidates instead of rejecting all of them.
"""Second construction sweep: more families, and a filter that degrades.

The first sweep refuted keyword-grid g against keyword-disk sigma over 121M
pairs. Its weakness was the filter: DJU-BEI demanded an exact permutation
identity M_1477 == M_2926, which rejects the true key outright if the walk model
is even slightly wrong -- and the model is labelled plausible, not confirmed.

So score instead of reject. The base returns exactly when M_DJU^-1 o M_BEI is
the identity, i.e. has 29 fixed points. Counting those fixed points gives 0..29
and turns an all-or-nothing test into a ranking: a construction that nearly
returns scores 20-something, and if the model is off by a detail the truth
should still rank high rather than vanish.

Families swept, far wider than the first pass:

  g:      layouts from keyword fill, Gematria prime order, totient order,
          index order and their reverses; filled row-major or boustrophedon;
          grid rotated by 1..4 along columns or rows
  sigma:  mixed 29-disk turned by any step 1..28, over the same layouts

Every candidate still has to satisfy the crib, which is model-light: it uses
only that base_w is a bijection within a word and that base_1 = base_0 o g^2 o
sigma. The report shows the score distribution, so a spike anywhere above the
noise floor is visible even when nothing reaches 29.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from construction_search import (  # noqa: E402
    HEAVY_DOUBLERS,
    crib_ok,
    keyword_alphabet,
    keywords,
)
from walk_verifier import (  # noqa: E402
    BEI,
    DJU,
    compose,
    inverse,
    load_words,
    order,
    step_products,
)

from aldegonde import c3301  # noqa: E402

M = 29
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET


def layouts(kws: list[str]) -> list[tuple[str, list[int]]]:
    """Every rune ordering a designer might plausibly lay in a grid."""
    out: list[tuple[str, list[int]]] = []
    by_prime = sorted(range(M), key=lambda i: c3301.r2v(c3301.CICADA_ALPHABET[i]))
    out.append(("prime-value", by_prime))
    out.append(("prime-value-rev", by_prime[::-1]))
    out.append(("index", list(range(M))))
    out.append(("index-rev", list(range(M))[::-1]))
    for kw in kws:
        base = keyword_alphabet(kw)
        if base is None:
            continue
        out.append((kw, base))
        out.append((f"{kw}-rev", base[::-1]))
    return out


def grid(layout: list[int], *, by_column: bool, rotate: int, snake: bool) -> np.ndarray:
    """25 runes into a 5x5 grid; one axis rotated by `rotate`; 4 runes fixed."""
    cells = list(layout[:25])
    if snake:  # boustrophedon fill: every other row laid right to left
        for r in range(1, 5, 2):
            cells[r * 5 : r * 5 + 5] = cells[r * 5 : r * 5 + 5][::-1]
    perm = np.arange(M)
    for a in range(5):
        cycle = (
            [cells[r * 5 + a] for r in range(5)]
            if by_column
            else [cells[a * 5 + c] for c in range(5)]
        )
        for i, x in enumerate(cycle):
            perm[x] = cycle[(i + rotate) % 5]
    return perm


def disk(layout: list[int], step: int) -> np.ndarray:
    perm = np.arange(M)
    for i, x in enumerate(layout):
        perm[x] = layout[(i + step) % M]
    return perm


def return_score(g: np.ndarray, sigma: np.ndarray, lengths: list[int]) -> int:
    """Fixed points of M_DJU^-1 o M_BEI: 29 means the base returned exactly."""
    Ms = step_products(g, sigma, lengths)
    rel = compose(inverse(Ms[DJU]), Ms[BEI])
    return int(np.sum(rel == np.arange(M)))


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    words = load_words()
    lengths = [len(w) for w in words]
    kws = keywords(limit)
    lays = layouts(kws)
    print(f"layouts: {len(lays)}   (keyword fills, prime and index orders, reversed)")

    g_pool: list[tuple[str, np.ndarray, dict[int, int]]] = []
    built = 0
    for name, layout in lays:
        for by_column in (True, False):
            for rotate in (1, 2, 3, 4):
                for snake in (False, True):
                    built += 1
                    g = grid(layout, by_column=by_column, rotate=rotate, snake=snake)
                    if order(g) != 5:
                        continue
                    if {i for i in range(M) if g[i] == i} & HEAVY_DOUBLERS:
                        continue
                    ok, pinned = crib_ok(g)
                    if not ok:
                        continue
                    tag = f"{name}/{'col' if by_column else 'row'}{rotate}"
                    g_pool.append((tag + ("/snake" if snake else ""), g, pinned))
    print(
        f"g constructions built {built:,}; surviving the crib and doubler tests:"
        f" {len(g_pool):,}\n"
    )
    if not g_pool:
        return

    scores: Counter[int] = Counter()
    best: list[tuple[int, str, str]] = []
    pairs = 0
    for tag, g, pinned in g_pool:
        for name, layout in lays:
            for step in range(1, M):
                sigma = disk(layout, step)
                if any(sigma[s] != t for s, t in pinned.items()):
                    continue
                pairs += 1
                sc = return_score(g, sigma, lengths)
                scores[sc] += 1
                if sc >= 20:
                    best.append((sc, tag, f"{name}/+{step}"))
    print(f"(g, sigma) pairs scored (crib-consistent): {pairs:,}\n")
    print("DJU-BEI return score  (29 = the base returns exactly)")
    for sc in sorted(scores, reverse=True)[:12]:
        bar = "#" * min(50, scores[sc] * 50 // max(scores.values()))
        print(f"  {sc:>3}: {scores[sc]:>9,}  {bar}")
    # a permutation drawn at random has Poisson(1) fixed points: mean 1, and
    # P(k) = 1/(e k!). If the observed spread matches that, the score carries no
    # signal at all -- the constructions are behaving like random permutations.
    import math

    total = sum(scores.values())
    print("\n  observed vs a random permutation (Poisson(1))")
    print(f"  {'fp':>3}{'observed':>10}{'expected':>10}")
    for k in range(7):
        exp = total / math.e / math.factorial(k)
        print(f"  {k:>3}{scores.get(k, 0):>10,}{exp:>10.0f}")
    mean = sum(k * n for k, n in scores.items()) / total
    print(f"  mean fixed points: observed {mean:.3f}, random permutation 1.000")

    if best:
        print("\nhigh scorers:")
        for sc, tag, sname in sorted(best, reverse=True)[:15]:
            print(f"  score {sc:>3}  g={tag}  sigma={sname}")
    else:
        print("\nnothing scored 20 or above; the top of the distribution is noise")


if __name__ == "__main__":
    main()
