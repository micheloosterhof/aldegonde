# ABOUTME: Tests whether the body's short-unit joining follows a deterministic size rule
# ABOUTME: or an inconsistent probabilistic habit, and rejects the deterministic one.
"""The joining is a habit with a rate, not a rule with a threshold.

`does_the_author_ever_join.py` put the author's own joining rate below 1.5% against the
body's 35%, so whatever merges the body's short units is not a convention he otherwise
uses. That makes the *form* of the rule worth knowing, because two very different things
would produce a merge:

- a **habit** -- a scribe who runs short words into their neighbour some of the time,
  with no rule about when;
- a **mechanical step** -- plaintext prepared into units of bounded size before
  enciphering, joining a short word whenever the result still fits.

These are distinguishable. A habit merges independently of the neighbour's length, so
merged units inherit the long tail of the word distribution. A size rule refuses to merge
when the neighbour is long, so the merged mass piles up below the cap and the tail keeps
the author's own shape.

`which_lengths_merge.py` settled which unit gets absorbed (two runes or fewer, not three).
It varied only the absorbed unit's length; the neighbour was never part of any rule.

## Scoring

Raw chi-square is not comparable across rules that move the distribution by different
amounts, so each rule is scored against **its own parametric null**: let that rule be
true, redraw both the 723-word reference and the 2,896-block body from it, refit and
rescore. That is the convention `which_lengths_merge.py` established and the reason its
verdicts held up.

| rule | fitted | chi2 | null, rule true | P |
|---|---|---|---|---|
| forward, probabilistic | q = 0.35 | 18.6 | 24.2 +- 13.0 | 0.70 |
| backward, probabilistic | q = 0.40 | 17.5 | 22.0 +- 12.4 | 0.55 |
| **forward, capped at N** | **N = 4** | **112.4** | **30.0 +- 16.3** | **0.00** |
| to the shorter neighbour | q = 0.30 | 32.5 | 27.0 +- 16.0 | 0.30 |

**The deterministic size rule is dead.** Giving it a probability as well -- merge with
probability q but only if the result fits under N -- does not rescue it: the fit drives N
to the top of the grid, where the cap never binds and the model collapses back to the
plain probabilistic one.

The two directions cannot be separated, and joining to whichever neighbour is shorter
survives weakly. What the experiment settles is the *kind* of rule, not its direction.

    python is_the_joining_mechanical.py [--draws 20]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import word_lengths  # noqa: E402
from what_the_marks_are import blocks_with  # noqa: E402

MAX_LENGTH = 12
WORDS_DRAWN = 3400  # enough words that, after merging, 2,896 blocks remain
ABSORBED = 2  # which_lengths_merge.py: the rule acts on two runes or fewer


def histogram(values) -> np.ndarray:
    counts = np.zeros(MAX_LENGTH + 1)
    for v in values:
        counts[min(int(v), MAX_LENGTH)] += 1
    return counts / counts.sum()


def forward(lengths, params, rng):
    """A short unit merges into the one after it, with probability q."""
    (q,) = params
    out, i = list(lengths), 0
    while i < len(out):
        if out[i] <= ABSORBED and rng.random() < q and i + 1 < len(out):
            out[i] += out.pop(i + 1)
            continue
        i += 1
    return out


def backward(lengths, params, rng):
    """A short unit merges into the one before it, with probability q."""
    (q,) = params
    out, i = list(lengths), 0
    while i < len(out):
        if out[i] <= ABSORBED and rng.random() < q and i > 0:
            out[i - 1] += out.pop(i)
            continue
        i += 1
    return out


def capped(lengths, params, rng):
    """A short unit merges forward whenever the result still fits under N."""
    (n,) = params
    out, i = list(lengths), 0
    while i < len(out):
        if out[i] <= ABSORBED and i + 1 < len(out) and out[i] + out[i + 1] <= n:
            out[i] += out.pop(i + 1)
            continue
        i += 1
    return out


def capped_probabilistic(lengths, params, rng):
    """Both at once: merge with probability q, but only if the result fits under N."""
    q, n = params
    out, i = list(lengths), 0
    while i < len(out):
        if (
            out[i] <= ABSORBED
            and i + 1 < len(out)
            and out[i] + out[i + 1] <= n
            and rng.random() < q
        ):
            out[i] += out.pop(i + 1)
            continue
        i += 1
    return out


def shorter_neighbour(lengths, params, rng):
    """A short unit merges into whichever neighbour is shorter, with probability q."""
    (q,) = params
    out, i = list(lengths), 0
    while i < len(out):
        if out[i] <= ABSORBED and rng.random() < q:
            before = out[i - 1] if i > 0 else None
            after = out[i + 1] if i + 1 < len(out) else None
            if before is not None or after is not None:
                if after is not None and (before is None or after <= before):
                    out[i] += out.pop(i + 1)
                else:
                    out[i - 1] += out.pop(i)
                continue
        i += 1
    return out


def score(model, params, reference, target, n_target, rng, draws=24):
    """Chi-square of `target` against the model driven by `reference` word lengths.

    The reference's own sampling error is carried alongside the target's, which is what
    `reference_noise_in_length_tests.py` showed two earlier results had omitted.
    """
    sims = [
        histogram(
            model([rng.choice(reference) for _ in range(WORDS_DRAWN)], params, rng)
        )
        for _ in range(draws)
    ]
    mean, sd = np.mean(sims, axis=0), np.std(sims, axis=0, ddof=1)
    se = np.sqrt(sd**2 + target * (1 - target) / n_target)
    return float(np.sum(((target - mean) / np.maximum(se, 1e-6)) ** 2))


def fit(model, grid, reference, target, n_target, rng):
    return min(
        ((p, score(model, p, reference, target, n_target, rng)) for p in grid),
        key=lambda t: t[1],
    )


RATES = [(round(q, 2),) for q in np.arange(0.20, 0.60, 0.05)]
RULES = (
    ("forward, probabilistic", forward, RATES),
    ("backward, probabilistic", backward, RATES),
    ("forward, capped at N", capped, [(n,) for n in range(3, 12)]),
    ("to the shorter neighbour", shorter_neighbour, RATES),
)


def main() -> None:
    draws = 20
    for i, arg in enumerate(sys.argv):
        if arg == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    author = word_lengths()
    body = [n for n, _, _ in blocks_with(set("④⑬③⑩"))]
    target, n_body, n_author = histogram(body), len(body), len(author)
    rng = random.Random(11)

    print(f"{n_author} author words against {n_body} body blocks. Each rule is scored")
    print(
        "against its own parametric null: let it be true, redraw the reference and the"
    )
    print(f"body from it, refit and rescore. {draws} draws.\n")
    print(f"{'rule':<30}{'fitted':>9}{'chi2':>8}{'null, rule true':>20}{'P':>7}")
    for name, model, grid in RULES:
        params, observed = fit(model, grid, author, target, n_body, rng)
        nulls = []
        for seed in range(draws):
            r = random.Random(100 + seed)
            reference = [r.choice(author) for _ in range(n_author)]
            synthetic = model(
                [r.choice(author) for _ in range(WORDS_DRAWN)], params, r
            )[:n_body]
            nulls.append(
                fit(model, grid, reference, histogram(synthetic), n_body, r)[1]
            )
        nulls = np.array(nulls)
        shown = tuple(round(float(x), 2) for x in params)
        print(
            f"{name:<30}{str(shown):>9}{observed:>8.1f}"
            f"{f'{nulls.mean():.1f} +- {nulls.std(ddof=1):.1f}':>20}"
            f"{float((nulls >= observed).mean()):>7.2f}"
        )

    grid = [(round(q, 2), n) for q in np.arange(0.2, 0.9, 0.1) for n in range(4, 12)]
    params, observed = fit(capped_probabilistic, grid, author, target, n_body, rng)
    print(
        f"\nGiving the size rule a probability too does not rescue it:"
        f"\n  best fit q = {params[0]:.2f}, N = {params[1]}, chi2 = {observed:.1f}"
        f" -- N runs to the top of the grid,"
        f"\n  where the cap never binds and the model is the plain probabilistic one."
    )

    print(
        "\nThe deterministic size rule is rejected outright. The merge does not consult"
        "\nthe neighbour's length, which is what a preparation step trimming units to a"
        "\nbounded size would have to do. It looks like an inconsistent habit with a rate."
        "\nDirection stays undetermined: forward and backward fit equally well."
    )


if __name__ == "__main__":
    main()
