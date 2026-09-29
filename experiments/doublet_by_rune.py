# ABOUTME: Asks whether the doublet suppression varies by rune, and measures that the
# ABOUTME: question is unanswerable because the per-block base scrambles the value.
"""A tempting discriminator that does not work, recorded so it is not tried again.

The body suppresses adjacent repeats to 0.19 of chance. Two mechanisms are on the books:
an explicit rule that fires on equality, and a tuned letter step whose graph happens to
sit on low-mass plaintext pairs (`quagmire-dodge.md` against `length-clocked-walk.md`).

They look like they should differ per rune. A rule that fires on equality is
value-independent, so it should suppress every rune equally; a tuned diagonal has 29
different entries and should not.

**The test has no power, and the reason is structural.** Under the walk, adjacent
positions carry `base o g^j` and `base o g^(j+1)`, so a ciphertext doublet at value x
needs `g^j(p_i) = g^(j+1)(p_(i+1))`, that is `p_i = g(p_(i+1))`. The plaintext condition
is about g, but the ciphertext VALUE it lands on is `base(g^j(p_i))` -- and base changes
every block while j runs over five phases. The value is scrambled before it is observed.

So the per-rune profile is uninformative about g by construction, and the measurement
below confirms it: planted walks give the same homogeneity as the body.

    python doublet_by_rune.py
"""

from __future__ import annotations

import collections
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
ENG = c3301.CICADA_ENGLISH_ALPHABET


def profile(ct: list[int]) -> tuple[float, float, list[tuple[int, float, int]]]:
    """(homogeneity chi2 of the suppression across runes, pooled factor, rows)."""
    n = len(ct)
    counts = collections.Counter(ct)
    obs = collections.Counter()
    for i in range(n - 1):
        if ct[i] == ct[i + 1]:
            obs[ct[i]] += 1
    rows = [(obs[x], counts[x] * (counts[x] - 1) / (n - 1), x) for x in range(M)]
    total_o = sum(o for o, _e, _x in rows)
    total_e = sum(e for _o, e, _x in rows)
    if total_o == 0:
        return 0.0, 0.0, rows
    k = total_o / total_e
    chi = sum((o - k * e) ** 2 / (k * e) for o, e, _x in rows if k * e > 0)
    return chi, k, rows


def planted_walk(rng: random.Random, words: list[list[int]]) -> list[int]:
    """Per-block base, per-letter step of order 5. No doublet rule of any kind."""
    cycles = list(range(M))
    rng.shuffle(cycles)
    g = list(range(M))
    for c in range(5):
        block = cycles[c * 5 : (c + 1) * 5]
        for a, b in zip(block, block[1:] + block[:1]):
            g[a] = b
    out: list[int] = []
    for i in range(2928):
        word = words[i % len(words)]
        base = list(range(M))
        rng.shuffle(base)
        step = list(range(M))
        for p in word:
            out.append(base[step[p]])
            step = [g[x] for x in step]
    return out


def main() -> None:
    stream, _wid = load_clean()
    chi, k, rows = profile(stream)
    print(f"body: {len(stream):,} runes, pooled suppression factor {k:.4f}")
    print(
        f"  homogeneity of suppression across runes: chi2 {chi:.1f} on 28 df "
        f"(5% crit 41.3)"
    )
    ranked = sorted(rows, key=lambda r: -(r[0] - k * r[1]) / math.sqrt(k * r[1] or 1))
    for o, e, x in ranked[:2] + ranked[-2:]:
        print(
            f"    {ENG[x]:>3}  observed {o:>2}  expected {k * e:>5.2f}  "
            f"z {(o - k * e) / math.sqrt(k * e):+.2f}"
        )

    print("\npower check: the same statistic on planted walks with NO doublet rule")
    rng = random.Random(12)
    words = corpus()
    for trial in range(4):
        ct = planted_walk(rng, words)
        c, kk, _r = profile(ct)
        print(f"  walk {trial}: suppression {kk:.3f}, homogeneity chi2 {c:.1f}")
    print(
        "\nThe planted walks land in the same homogeneity range as the body, so the"
        "\nstatistic cannot tell a tuned diagonal from an explicit rule. What the"
        "\ncontrol does show is the suppression itself: a plain walk gives 0.74 to 1.40"
        "\nwhere the body gives 0.19, which is doublet-suppression-requires-design.md"
        "\nreproduced from a different direction."
    )


if __name__ == "__main__":
    main()
