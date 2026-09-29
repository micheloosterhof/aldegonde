# ABOUTME: Closes the standing tension between the four-dot's gap law and its missing
# ABOUTME: lengthening, by testing what the thinning model actually requires.
"""The gap law says thinned sentence ends. The rank statistic says how many. They collide.

Two facts about the four-dot have sat in tension all session.

**The spacing fits thinned sentence ends.** `are_the_four_dot_gaps_memoryless.py` scores
the gaps between four-dots against four generators and the author's own spans thinned to
p = 0.357 wins: log-likelihood -239.07 against -240.52 for his unthinned spans, -241.08
for a memoryless placement and -242.11 for English sentences. That is 4.3 to 1 over the
next arm.

**The lengthening is absent.** The block before a four-dot does not lengthen, and
`is_there_any_order_inside_a_span.py` puts that with no reference at all: the body's
span-final block reads 0.481 in rank against 0.500 for a random block of the same span,
where the author's reads 0.647.

These have been described here as consistent -- one about spacing, one about content. They
are not, and the thinning model is what makes them collide.

## What thinning actually requires

Thinning says the author wrote sentences as he always does and **marked only some of the
ends**. Every four-dot then sits at a real sentence end; what varies is how many ends get
a mark. So thinning predicts the fraction of four-dots at genuine sentence ends is
**exactly 1**, not 0.357 -- p is the share of ENDS that are marked, not the share of MARKS
that are ends.

`the_rank_of_the_last_block.py` measures that fraction directly, with the author's lift as
the unit. This asks what it says about f = 1.

## Result: thinning is excluded at seven sigma

| corpus | spans | mean rank | a random block of the same spans | lift |
|---|---|---|---|---|
| the author | 68 | 0.647 | 0.500 +- 0.030 | **+0.147** |
| the body | 129 | 0.481 | 0.500 +- 0.023 | **-0.019** |

Taking the author's lift as one genuine sentence end's worth:

    fraction of four-dots at a genuine sentence end:  -0.131 +- 0.156

| model | predicted f | sigma away |
|---|---|---|
| **thinning: every mark is a sentence end** | 1.000 | **7.2** |
| a mixture at the layout rate | 0.106 | 1.5 |
| no four-dot is a sentence end | 0.000 | 0.8 |

## The distinction that was being elided

Thinning's parameter **p = 0.357 is the share of sentence ENDS that carry a mark**. It is
not the share of MARKS that sit at ends -- that is 1 by construction, because a thinned
process marks a subset of real ends and nothing else.

Reading p as though it described the marks is what made the gap law and the missing
lengthening look compatible. They are not: thinning needs f = 1 and the corpus gives
-0.131 +- 0.156.

## What this resolves

The standing tension in this directory -- the spacing saying "thinned sentence ends" while
the content says "not sentence ends" -- resolves by **the spacing losing**. The gap law's
4.3-to-1 preference for thinned author spans, on 137 gaps, is a coincidence of shape
rather than evidence for a mechanism. A 4.3-to-1 likelihood ratio is a weak preference and
this is what a weak preference looks like when a sharp test arrives.

What survives is unchanged: a small mixture at around the layout rate sits 1.5 sigma away
and no four-dot being a sentence end sits 0.8 sigma away. Neither is excluded and the
corpus cannot separate them.

    python the_thinning_model_is_dead.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from body_parse import spans  # noqa: E402
from the_gap_depends_on_span_length import author_spans  # noqa: E402

MIN_SPAN = 4
DRAWS = 6000


def scaled_rank(span, value) -> float:
    below = sum(1 for x in span if x < value)
    equal = sum(1 for x in span if x == value)
    return (below + (equal + 1) / 2) / (len(span) + 1)


def lift(rows, rng):
    observed = float(np.mean([scaled_rank(s, s[-1]) for s in rows]))
    null = np.array(
        [
            np.mean([scaled_rank(s, s[rng.integers(len(s))]) for s in rows])
            for _ in range(DRAWS)
        ]
    )
    return observed, float(null.mean()), float(null.std(ddof=1))


def main() -> None:
    rng = np.random.default_rng(3301)
    body = spans({"④"}, minimum=MIN_SPAN)
    author = [s for s in author_spans() if len(s) >= MIN_SPAN]

    a_obs, a_null, a_sd = lift(author, rng)
    b_obs, b_null, b_sd = lift(body, rng)
    unit = a_obs - a_null

    print(
        f"{'corpus':<16}{'spans':>7}{'mean rank':>11}{'a random block':>18}{'lift':>9}"
    )
    print(
        f"{'the author':<16}{len(author):>7}{a_obs:>11.3f}{f'{a_null:.3f} +- {a_sd:.3f}':>18}{unit:>+9.3f}"
    )
    print(
        f"{'the body':<16}{len(body):>7}{b_obs:>11.3f}{f'{b_null:.3f} +- {b_sd:.3f}':>18}{b_obs - b_null:>+9.3f}"
    )

    f = (b_obs - b_null) / unit
    sf = b_sd / abs(unit)
    print(f"\nfraction of four-dots at a genuine sentence end: {f:+.3f} +- {sf:.3f}")

    print(f"\n{'model':<40}{'predicted f':>13}{'sigma away':>13}")
    for label, predicted in (
        ("thinning: every mark is a sentence end", 1.0),
        ("a mixture at the layout rate", 0.106),
        ("no four-dot is a sentence end", 0.0),
    ):
        print(f"{label:<40}{predicted:>13.3f}{abs(predicted - f) / sf:>13.1f}")

    print(
        "\n  Thinning is excluded. Its own definition forces every mark onto a sentence"
        "\n  end, and the rank statistic says essentially none of them are."
        "\n\n  So the gap law's 4.3-to-1 preference for thinned author spans is a"
        "\n  coincidence of shape on 137 gaps, not evidence for the mechanism. The"
        "\n  tension between spacing and lengthening resolves by the spacing losing."
    )


if __name__ == "__main__":
    main()
