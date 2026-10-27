# ABOUTME: Asks whether the body's short units were joined to a neighbour before or after the
# ABOUTME: words were permuted, by what the joined block's length marginal says about the partner.
"""Were the short units joined in the author's order, or after the shuffle?

`short-units-are-written-joined.md` fits the body's block-length marginal with units of
two runes or fewer joined to a neighbour at q = 0.40. `the-words-are-transposed-within-
sentences.md` finds the words permuted within each span. The two operations do not
commute in what they leave in the lengths:

- **joined before the shuffle**: the partner of a function word is the word that follows
  (or precedes) it in English -- after THE, OF, A the next word is a content word, longer
  than average and almost never another short unit;
- **joined after the shuffle**: the partner is a random word of the span, with the
  marginal's own 24% short units, so more blocks of three and four runes and fewer long
  ones.

The shuffle itself leaves the marginal alone, so the marginal reads the order of
operations and nothing else. Three models, each run on the author's 68 solved sentences
in their written order: join forward (the short unit absorbed into the following word),
join backward (into the preceding word, the rule `which_lengths_merge.py` fitted), and
shuffle within the sentence first, then join (direction immaterial). Each is fitted on q,
scored by chi-square on the body's twelve-bin histogram, and priced against its own
parametric null (reference sentences resampled, a synthetic body drawn under the model,
refitted), as in `which_lengths_merge.py`. The model comparison is the difference of the
two chi-squares, priced under each model in turn.

    python experiments/joining_before_or_after_the_shuffle.py [--draws 60]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from reference_noise_in_length_tests import CAP, GRID, histogram  # noqa: E402
from sentences_do_not_end_long import join  # noqa: E402
from the_gap_depends_on_span_length import author_spans  # noqa: E402
from within_word_d5 import parse_clean_sections  # noqa: E402

SEED = 20261028
POOL_WORDS = 6000


def before_forward(sentences, q, rng):
    return [x for s in sentences for x in join(list(s), q, rng, forward=True)]


def before_backward(sentences, q, rng):
    return [x for s in sentences for x in join(list(s), q, rng, forward=False)]


def after(sentences, q, rng):
    out = []
    for s in sentences:
        s = list(s)
        rng.shuffle(s)
        out.extend(join(s, q, rng, forward=True))
    return out


MODELS = {
    "joined before the shuffle, forward": before_forward,
    "joined before the shuffle, backward": before_backward,
    "shuffled, then joined": after,
}


def fit(sentences, model, target: np.ndarray, reps: int = 25, seed: int = 0):
    """Best chi-square over q of the model's expected histogram against `target`."""
    n_target = target.sum()
    best, best_q = float("inf"), None
    for q in GRID:
        h, n = np.zeros(CAP), 0
        for t in range(reps):
            m = model(sentences, float(q), random.Random(seed * 997 + t))
            h += histogram(m)
            n += len(m)
        e = h / n * n_target
        c = float((((target - e) ** 2) / np.maximum(e, 1e-9)).sum())
        if c < best:
            best, best_q = c, float(q)
    return best, best_q


def resample(sentences, rng, words: int):
    """Sentences drawn with replacement until about `words` words."""
    out, n = [], 0
    while n < words:
        s = sentences[rng.randrange(len(sentences))]
        out.append(s)
        n += len(s)
    return out


def main() -> None:
    draws = 60
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])
    rng = random.Random(SEED)
    author = author_spans()
    n_author = sum(len(s) for s in author)
    body = histogram(
        [
            len(w)
            for sec in parse_clean_sections(str(ROOT / "data/page0-56.txt"))
            for w in sec
        ]
    )
    n_body = int(body.sum())
    print(f"author: {len(author)} sentences, {n_author} words; body: {n_body} blocks\n")

    # the partner's length under each model, at q = 1 so every short unit is joined
    print("what a joined block is made of (q = 1, every short unit joined):")
    for name, model in MODELS.items():
        parts = []
        for t in range(40):
            r = random.Random(t)
            joined = model(author, 1.0, r)
            parts.append(sum(1 for x in joined if x <= 4) / len(joined))
        print(f"  {name:<38} share of blocks 4 runes or shorter {np.mean(parts):.3f}")

    print(f"\n{'model':<38}{'best q':>8}{'chi2':>8}{'null, model true':>22}{'P':>7}")
    obs = {}
    nulls = {}
    for name, model in MODELS.items():
        c, q = fit(author, model, body)
        obs[name] = (c, q)
        rows = []
        for b in range(draws):
            ref = resample(author, rng, n_author)
            synth = histogram(
                model(resample(author, rng, POOL_WORDS), q, random.Random(b))[:n_body]
            )
            rows.append(
                [fit(ref, m, synth, reps=6, seed=b)[0] for m in MODELS.values()]
            )
        nulls[name] = np.array(rows)
        own = nulls[name][:, list(MODELS).index(name)]
        print(
            f"{name:<38}{q:>8.2f}{c:>8.1f}"
            f"{f'{own.mean():.1f} +- {own.std():.1f}':>22}{(own >= c).mean():>7.2f}"
        )

    names = list(MODELS)
    print(
        "\nmodel comparison: chi2(shuffled, then joined) - chi2(joined before, forward)"
    )
    d_obs = obs[names[2]][0] - obs[names[0]][0]
    print(f"  observed {d_obs:+.1f}")
    for truth in (names[0], names[2]):
        d = nulls[truth][:, 2] - nulls[truth][:, 0]
        side = (d >= d_obs).mean() if truth == names[0] else (d <= d_obs).mean()
        print(
            f"  if '{truth}' is true: {d.mean():+.1f} +- {d.std():.1f}; P(as far as observed) = {side:.2f}"
        )
    print("\nsame, against the backward joining")
    d_obs = obs[names[2]][0] - obs[names[1]][0]
    print(f"  observed {d_obs:+.1f}")
    for truth in (names[1], names[2]):
        d = nulls[truth][:, 2] - nulls[truth][:, 1]
        side = (d >= d_obs).mean() if truth == names[1] else (d <= d_obs).mean()
        print(
            f"  if '{truth}' is true: {d.mean():+.1f} +- {d.std():.1f}; P(as far as observed) = {side:.2f}"
        )


if __name__ == "__main__":
    main()
