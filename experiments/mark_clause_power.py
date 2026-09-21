# ABOUTME: Power check for mark_clause_lengths: would its test detect genuine clause
# ABOUTME: structure at the unsolved pages' sparser mark rate, or is the null result empty?
"""A negative result is only worth having if the test could have come out positive.

`mark_clause_lengths.py` finds that the solved pages' clause marks reject a random
placement null (cv 0.74, p = 0.0026) and the unsolved pages' marks do not (cv 0.81,
p = 0.14). That is only evidence about the unsolved marks if the same test, at the
unsolved pages' mark count and rate, would have caught clause structure had it been
there.

The unsolved pages carry marks half as densely as the solved ones -- one per 18.6
words against one per 8.9 -- and a sparser process is harder to distinguish from
random. So plant clause structure at the unsolved rate and measure how often the
test sees it.

The planted structure is the solved pages' own segment-length distribution, scaled
to the unsolved mean. That keeps the SHAPE of real English clause lengths from this
very book and changes only the rate, which is the thing that differs.

    python mark_clause_power.py [--trials 300] [--draws 2000]
"""

from __future__ import annotations

import random
import statistics
import sys

from mark_clause_lengths import collect, pages

TRIALS = 300
DRAWS = 2000


def planted(rng: random.Random, template: list[int], n: int, mean: float) -> list[int]:
    """`n` segment lengths with the template's shape, rescaled to `mean` words."""
    scale = mean / statistics.mean(template)
    out = []
    for _ in range(n):
        x = round(rng.choice(template) * scale)
        out.append(max(1, x))
    return out


def geometric(rng: random.Random, n: int, mean: float) -> list[int]:
    """The machinery null: independent marks give geometric word gaps."""
    p = 1 / mean
    out = []
    for _ in range(n):
        k = 1
        while rng.random() > p and k < 200:
            k += 1
        out.append(k)
    return out


def pvalue(segs: list[int], rng: random.Random, draws: int) -> float:
    """p for 'cv this low or lower' against geometric gaps at the same mean."""
    cv = statistics.pstdev(segs) / statistics.mean(segs)
    mean = statistics.mean(segs)
    hits = 0
    for _ in range(draws):
        null = geometric(rng, len(segs), mean)
        if statistics.pstdev(null) / statistics.mean(null) <= cv:
            hits += 1
    return (hits + 1) / (draws + 1)


def main() -> None:
    trials, draws = TRIALS, DRAWS
    for i, a in enumerate(sys.argv):
        if a == "--trials" and i + 1 < len(sys.argv):
            trials = int(sys.argv[i + 1])
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    allp = pages()
    solved = [p for p in allp if "." in p]
    unsolved = [p for p in allp if any(c in p for c in "④⑩⑬")]
    template, s_words, s_marks = collect(solved)
    u_segs, u_words, u_marks = collect(unsolved)
    u_mean = statistics.mean(u_segs)

    print(
        f"template: {len(template)} solved-page clause lengths, "
        f"mean {statistics.mean(template):.1f} words, "
        f"cv {statistics.pstdev(template) / statistics.mean(template):.2f}"
    )
    print(f"planting {u_marks} segments at the unsolved mean of {u_mean:.1f} words\n")

    rng = random.Random(3301)
    for label, n, mean in (
        ("unsolved, all glyphs", u_marks, u_mean),
        ("unsolved, 4-dot only", 141, u_words / 141),
    ):
        wins = 0
        for _ in range(trials):
            segs = planted(rng, template, n, mean)
            if pvalue(segs, rng, draws) < 0.05:
                wins += 1
        print(
            f"{label:<24} real clause structure detected at p<0.05 in "
            f"{wins / trials:.0%} of {trials} plants"
        )

    print("\nfor comparison, the observed values:")
    for label, segs in (("unsolved, all glyphs", u_segs),):
        cv = statistics.pstdev(segs) / statistics.mean(segs)
        print(f"  {label:<22} cv {cv:.2f}")
    print(
        f"  solved template        cv {statistics.pstdev(template) / statistics.mean(template):.2f}"
    )


if __name__ == "__main__":
    main()
