# ABOUTME: Tests whether the cipher's base returns to a common value at any structural
# ABOUTME: boundary -- sentence mark, page break, section break -- and finds it never does.
"""If the cipher restarted at a boundary, the blocks that follow one would share a base.

Two readings of the sentence-mark anomaly (`sentences-do-not-end-long.md`) would be
explained at a stroke if the mark meant something to the cipher rather than only to the
scribe. The most attractive version is a **resynchronisation**: at a mark the base
returns to its initial value and the clock to zero, the way a rotor machine is reset to
a ground setting at the start of each message.

That is directly testable and needs no key. If every block after a mark carries the same
base, then two such blocks agree at position k exactly when their plaintexts agree there,
because the shared base and shared clock cancel:

    c_w[k] = c_w'[k]   iff   base(g^k(p_w[k])) = base(g^k(p_w'[k]))   iff   p_w[k] = p_w'[k]

So position-aligned coincidence over all pairs of boundary-following blocks reads the
plaintext coincidence rate under a restart, and chance under anything else. Real
plaintext is far from uniform at word-initial positions, so the gap is large.

**D12 does not already exclude this.** `base_changes_every_block.py` caps unchanged
edges at 15% of the total; sentence marks are 5.8% of edges, page breaks 1.9%. A restart
confined to boundaries fits inside that cap.

The null is length-matched: boundary-following blocks are drawn from a particular part
of the length distribution, and coincidence depends on length through the number of
aligned positions a pair contributes. Each draw resamples blocks of exactly the observed
lengths from the whole body.

**The positive controls are the point of the experiment**, and they also fix its scope.
Planting each kind of reset at the sentence-mark count:

| planted | z |
|---|---|
| base and clock both reset | **+53** |
| base resets, clock runs on | **+17** |
| clock resets, base runs on | **−1.6 — invisible** |
| nothing resets | +0.5 |

So a null excludes a **base** reset, with or without the clock, and says nothing about a
clock-only one. That blindness is structural rather than a matter of sample size: blocks
carrying different bases coincide at chance whatever their phase, the clock cancels
inside a block, and the base hides it across one. A clock-only reset is invisible to
every key-free channel there is.

The page-break cell carries only 18 blocks, where a planted full reset reaches about
+4σ. That cell excludes a full reset and nothing weaker.

    python does_the_cipher_restart.py
"""

from __future__ import annotations

import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import N_RUNES, order5, prose_corpora  # noqa: E402
from sentences_do_not_end_long import BODY, SENTENCE_MARKS  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
INDEX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
ANNOTATION = re.compile(r"^[\s0-9-]*$")
# page, section and the '&' marker sit on their own lines, so they cannot end a block
# by position alone -- `page-breaks-cut-blocks.md` shows cutting at them puts 34
# spurious fragments into the canonical 2,928
STANDALONE = {"%", "$", "&"}
DRAWS = 200


def body_blocks(marks: set[str]) -> list[tuple[list[int], bool]]:
    """Each block as rune indices, with a flag for whether a boundary precedes it.

    A standalone marker never cuts a block. Where a separator already closed the block
    the marker is a genuine boundary and the next block is flagged; where runes stand
    either side the block continues across it and nothing is flagged, because there is
    no block that "follows" the marker in the sense the test needs.
    """
    text = "\n".join(
        line
        for line in BODY.read_text().replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    out: list[tuple[list[int], bool]] = []
    current: list[int] = []
    initial = True
    for ch in text:
        if RUNE.match(ch):
            current.append(INDEX[ch])
        elif ch == "\n":
            continue
        elif ch in STANDALONE:
            if not current:
                initial = ch in marks
        elif ch in c3301.WORD_BOUNDARY:
            if current:
                out.append((current, initial))
                current = []
            initial = ch in marks
    if current:
        out.append((current, initial))
    return out


def aligned_rate(blocks: list[list[int]]) -> tuple[int, int]:
    """Coincidences at equal positions, over every pair in the set."""
    hits = trials = 0
    for a in range(len(blocks)):
        for b in range(a + 1, len(blocks)):
            x, y = blocks[a], blocks[b]
            for k in range(min(len(x), len(y))):
                trials += 1
                hits += x[k] == y[k]
    return hits, trials


def length_matched_null(pool, lengths, rng, draws=DRAWS):
    """Resample blocks of exactly the observed lengths from the whole body."""
    by_length: dict[int, list[list[int]]] = {}
    for b in pool:
        by_length.setdefault(len(b), []).append(b)
    out = []
    for _ in range(draws):
        sample = [rng.choice(by_length[n]) for n in lengths]
        hits, trials = aligned_rate(sample)
        out.append(hits / trials)
    return np.array(out)


def compose(p, q):
    return [p[q[i]] for i in range(len(p))]


def power(p, k):
    out = list(range(len(p)))
    for _ in range(k):
        out = compose(p, out)
    return out


def simulate(plain, mark_every, rng, mode):
    """The length-clocked walk, resetting base, clock, both or neither at a boundary."""
    g = order5(rng)
    powers = [power(g, k) for k in range(5)]
    sigma = rng.sample(range(N_RUNES), N_RUNES)
    base_0 = rng.sample(range(N_RUNES), N_RUNES)
    base, clock, following = list(base_0), 0, False
    cipher, flags = [], []
    for w, word in enumerate(plain):
        flags.append(following)
        cipher.append([base[powers[(clock + j) % 5][p]] for j, p in enumerate(word)])
        clock += len(word)
        base = compose(base, compose(powers[(clock - 1) % 5], sigma))
        following = w % mark_every == mark_every - 1
        if following:
            if mode in ("both", "base"):
                base = list(base_0)
            if mode in ("both", "clock"):
                clock = 0
    return cipher, flags


def score(selected, pool, rng, label, out_width=20):
    hits, trials = aligned_rate(selected)
    observed = hits / trials
    null = length_matched_null(pool, [len(b) for b in selected], rng)
    z = (observed - null.mean()) / null.std(ddof=1)
    print(
        f"{label:<34}{len(selected):>8}{observed:>12.4f}"
        f"{f'{null.mean():.4f} +- {null.std(ddof=1):.4f}':>{out_width}}{z:>+8.2f}"
    )
    return z


def main() -> None:
    rng = random.Random(3301)
    print("Position-aligned coincidence among the blocks that FOLLOW a boundary.")
    print("A shared base would read the plaintext rate; chance is 1/29 = 0.0345.\n")
    print(f"{'boundary':<34}{'blocks':>8}{'observed':>12}{'matched null':>20}{'z':>8}")
    for label, marks in (
        ("a sentence mark", SENTENCE_MARKS),
        ("a page break", {"%"}),
        ("a page or section break", {"%", "$"}),
        ("any boundary at all", SENTENCE_MARKS | {"%", "$", "&"}),
    ):
        blocks = body_blocks(marks)
        following = [b for b, flag in blocks if flag]
        if len(following) < 12:
            print(f"{label:<34}{len(following):>8}{'too few':>12}")
            continue
        score(following, [b for b, _ in blocks], rng, label)

    print(
        "\nWhat can the test see? Plant each kind of reset at the sentence-mark count.\n"
    )
    print(
        f"{'planted reset':<34}{'blocks':>8}{'observed':>12}{'matched null':>20}{'z':>8}"
    )
    plain = prose_corpora(2896, 1)[0]
    for mode, label in (
        ("both", "base and clock both reset"),
        ("base", "base resets, clock runs on"),
        ("clock", "clock resets, base runs on"),
        ("none", "nothing resets"),
    ):
        cipher, flags = simulate(plain, 17, random.Random(7), mode)
        score([c for c, f in zip(cipher, flags) if f], cipher, rng, label)

    print("\nAnd at the page-break count, where only 18 blocks are available.\n")
    print(
        f"{'planted reset':<34}{'blocks':>8}{'observed':>12}{'matched null':>20}{'z':>8}"
    )
    for mode, label in (
        ("both", "base and clock both reset"),
        ("none", "nothing resets"),
    ):
        cipher, flags = simulate(plain, 150, random.Random(7), mode)
        score([c for c, f in zip(cipher, flags) if f], cipher, rng, label)

    print(
        "\nAt the sentence-mark count a base reset is unmissable whether or not the clock"
        "\ngoes with it, and the body shows nothing: the base does not return at a mark."
        "\n\nTwo limits, both real. At the page-break count only 18 blocks are available"
        "\nand the planted reset reaches about +4 sigma, so that cell excludes a full"
        "\nreset and nothing weaker. And the test is BLIND to a clock-only reset (-1.70"
        "\non a planted one), because blocks with different bases coincide at chance"
        "\nwhatever their phase. A clock-only reset is invisible to every key-free"
        "\nchannel: the clock cancels inside a block and the base hides it across one."
    )


if __name__ == "__main__":
    main()
