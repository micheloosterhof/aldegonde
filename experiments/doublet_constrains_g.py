# ABOUTME: Uses the exact identity between the within-word doublet rate and the plaintext
# ABOUTME: bigram mass on g's graph to measure how tuned g must be: about 7.8 bits.
"""How special does the letter step have to be?

Under the walk the alphabet at within-word position j is `base_w . g^j`, so the
relation between adjacent positions is

    A_(j+1)^-1 . A_j = (base.g^(j+1))^-1 . (base.g^j) = g^-1

constant in both the word and the position. A ciphertext doublet is `c_j = c_(j+1)`,
which means `p_(j+1) = g^-1(p_j)` -- the plaintext pair lies on the GRAPH of g^-1, not
that g^-1 fixes a point. So the within-word doublet rate is exactly

    sum_x P(p_j = x, p_(j+1) = g^-1(x))

the plaintext bigram mass that g^-1 selects. `--validate` checks this on planted walks
before anything is concluded from it; an earlier attempt at this file's argument used
fixed points instead of the graph and was wrong, so the check is not ceremonial.

With the identity in hand, the question becomes quantitative: what fraction of order-5
permutations select as little plaintext bigram mass as the body shows? The bigram
distribution is the author's own (`lp-plaintext-register.md`), not imported prose.

    python doublet_constrains_g.py [--draws 200000] [--validate]
"""

from __future__ import annotations

import collections
import json
import math
import random
import re
import sys
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

M = 29
RUNE = re.compile(r"[ᚠ-᛿]")
WRAP = "/\n"
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
PLAIN_PAGES = (3, 8, 9, 10, 11, 14)


def _pages() -> list[str]:
    return (
        (ROOT / "data" / "liber-primus__transcription--master.txt")
        .read_text()
        .split("%")
    )


def words_of(page: str, key: list[int] | None = None) -> list[list[int]]:
    out: list[list[int]] = []
    cur: list[int] = []
    for ch in page:
        if RUNE.match(ch):
            r = IDX[ch]
            cur.append(key[r] if key else r)
        elif ch in WRAP:
            continue
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def plaintext_words() -> list[list[int]]:
    pages = _pages()
    triples = json.loads(
        (ROOT / "experiments" / "solved_page_triples.json").read_text()
    )
    words = []
    for t in triples:
        if t["cipher"] == "monoalphabetic":
            words += words_of(pages[t["page"]], t["key"])
    for n in PLAIN_PAGES:
        words += words_of(pages[n])
    return words


def bigrams(words: list[list[int]]) -> dict[tuple[int, int], float]:
    counts: collections.Counter = collections.Counter()
    total = 0
    for w in words:
        for i in range(len(w) - 1):
            counts[(w[i], w[i + 1])] += 1
            total += 1
    return {k: v / total for k, v in counts.items()}


def body_rate() -> tuple[int, int]:
    stream, wid = load_clean()
    words, cur, last = [], [], wid[0]
    for r, w in zip(stream, wid):
        if w != last:
            words.append(cur)
            cur, last = [], w
        cur.append(r)
    words.append(cur)
    h = p = 0
    for w in words:
        for i in range(len(w) - 1):
            p += 1
            h += w[i] == w[i + 1]
    return h, p


def order5(rng: random.Random) -> list[int]:
    q = list(range(M))
    rng.shuffle(q)
    g = list(range(M))
    for c in range(5):
        cyc = q[c * 5 : (c + 1) * 5]
        for i in range(5):
            g[cyc[i]] = cyc[(i + 1) % 5]
    return g


def selected_mass(g: list[int], P: dict) -> float:
    inv = [0] * M
    for i, v in enumerate(g):
        inv[v] = i
    return sum(P.get((x, inv[x]), 0.0) for x in range(M))


def validate(words, P, rng) -> None:
    print("validation: plant a walk, compare its doublet rate to the identity\n")
    print(f"{'trial':>6}{'identity':>11}{'observed':>11}")
    for t in range(5):
        g = order5(rng)
        h = p = 0
        for w in words:
            base = list(range(M))
            rng.shuffle(base)
            ct = []
            for j, x in enumerate(w):
                y = x
                for _ in range(j % 5):
                    y = g[y]
                ct.append(base[y])
            for j in range(len(ct) - 1):
                p += 1
                h += ct[j] == ct[j + 1]
        print(f"{t:>6}{selected_mass(g, P):>11.5f}{h / p:>11.5f}")
    print()


def main() -> None:
    draws = 200_000
    for i, a in enumerate(sys.argv):
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])
    rng = random.Random(3301)
    words = plaintext_words()
    P = bigrams(words)
    if "--validate" in sys.argv:
        validate(words, P, rng)

    hits, pairs = body_rate()
    obs = hits / pairs
    print(
        f"body within-word doublets: {hits}/{pairs} = {obs:.5f} ({obs * M:.3f}x chance)"
    )
    vals = [selected_mass(order5(rng), P) for _ in range(draws)]
    vals.sort()
    mu = sum(vals) / len(vals)
    sd = (sum((v - mu) ** 2 for v in vals) / len(vals)) ** 0.5
    below = sum(1 for v in vals if v <= obs) / len(vals)
    print(f"\nrandom order-5 g over {draws:,} draws: mean {mu:.5f}, sd {sd:.5f}")
    print(
        f"fraction selecting mass <= the body's rate: {below:.4f} (1 in {1 / below:,.0f})"
    )
    print(f"so the doublet rate alone constrains g by {math.log2(1 / below):.1f} bits")
    print(
        "\nCaveat: the bigram table is 1,477 pairs over 841 cells, so it is sparse and a"
        "\nrandom g often selects empty cells. That makes low sums EASIER to reach by"
        "\nchance, so the 1-in-215 is an upper bound on the fraction and the bit count is"
        "\na lower bound on the constraint."
    )


if __name__ == "__main__":
    main()
