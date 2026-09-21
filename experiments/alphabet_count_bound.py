# ABOUTME: Turns the body's flat IoC into a lower bound on how many distinct alphabets any
# ABOUTME: cipher must visit, which excludes extending the solved front matter's short keys.
"""How many alphabets must the body's cipher visit? At least ~950.

`solved-page-testbed.md` solves the front matter with short keyed Vigenere --
DIVINITY (8 runes) and FIRFUMFERENFE (13) -- plus an interrupted keystream. The
obvious next hypothesis is that the body is the same scheme with more interrupts, and
it has a superficial appeal: interrupts scramble the key phase, which would destroy
the periodicity the body conspicuously lacks (`no-periodicity.md`).

It does not survive the index of coincidence, and the reason is that interrupts
scramble phase without adding alphabets.

Two positions drawn at random share an alphabet with probability 1/L, where L is the
effective number of distinct alphabets (the inverse collision probability). When they
share one, the runes agree at the plaintext rate I_p; otherwise at 1/29. So

    IoC = 1 + (I_p - 1) / L        hence        L = (I_p - 1) / (IoC - 1)

I_p is taken from the author's own plaintext (`lp-plaintext-register.md`), not from
imported prose. The body's IoC is measured with its own simulated error bar, which at
12,956 runes is tight because the pair count grows as n^2 -- the standard error of the
IoC falls as 1/n, not 1/sqrt(n).

The bound constrains every model in this directory, not just the Vigenere one: any
mechanism must make two random positions collide in alphabet less than about one time
in a thousand.

    python alphabet_count_bound.py [--draws 2000]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

from aldegonde.stats import ioc  # noqa: E402

M = 29


def main() -> None:
    draws = 2000
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    stream, _wid = load_clean()
    n = len(stream)
    obs = ioc(stream) * M

    rng = random.Random(3301)
    nulls = [ioc([rng.randrange(M) for _ in range(n)]) * M for _ in range(draws)]
    mu = sum(nulls) / len(nulls)
    sd = (sum((x - mu) ** 2 for x in nulls) / len(nulls)) ** 0.5

    plain = [r for w in corpus() for r in w]
    i_p = ioc(plain) * M

    print(f"body: {n:,} runes, normalised IoC {obs:.4f}, simulated SE {sd:.4f}")
    print(f"plaintext IoC from the LP's own words: {i_p:.3f}\n")
    print(f"{'confidence':<18}{'IoC upper':>11}{'L >=':>10}")
    for label, z in (("point estimate", 0.0), ("95% one-sided", 1.645), ("99%", 2.326)):
        up = obs + z * sd
        low = (i_p - 1) / (up - 1) if up > 1 else float("inf")
        shown = "infinite" if low == float("inf") else f"{low:,.0f}"
        print(f"{label:<18}{up:>11.4f}{shown:>10}")

    print("\nwhat the solved front matter supplies:")
    for word, length in (("DIVINITY", 8), ("FIRFUMFERENFE", 13)):
        print(f"  {word:<16}{length:>4} alphabets")
    print(
        "\nSo the front matter's scheme is short of the body's requirement by about two"
        "\norders of magnitude, and adding interrupts does not help: an interrupt moves"
        "\nthe key phase, it does not create an alphabet the key does not already have."
    )


if __name__ == "__main__":
    main()
