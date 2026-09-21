# ABOUTME: Computes the unicity distance of each key model against the body's 12,956 runes,
# ABOUTME: separating families whose difficulty is search from families that are unbreakable.
"""Which key models can 12,956 runes determine at all?

Every attack in this directory is a search. Before searching it is worth asking which
key models the available ciphertext could in principle pin down, because a model whose
key carries more entropy than the ciphertext carries redundancy has MANY consistent
solutions and no amount of cleverness distinguishes them.

Shannon's unicity distance is U = H(key) / D, with D the plaintext redundancy per
symbol -- here log2(29) minus the entropy of the author's own runeglish, measured on
the 1,796 runes of recovered plaintext rather than imported from English.

The body offers 12,956 runes, and `data/` holds no more: the master transcription's
15,933 runes are the front matter's 2,797 plus page0-58's 13,136, of which the solved
AN END page and the plaintext Parable account for the 180 beyond the clean 12,956.

D is the uncertain input, so every model is reported across a range of it.

    python unicity_distance.py
"""

from __future__ import annotations

import collections
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRIPLES = ROOT / "experiments" / "solved_page_triples.json"
M = 29
BODY_RUNES = 12_956
PERM_BITS = math.log2(math.factorial(M))


def conditional_entropy(seq: list[int], order: int) -> float:
    ctx = collections.Counter(
        tuple(seq[i : i + order]) for i in range(len(seq) - order)
    )
    joint = collections.Counter(
        tuple(seq[i : i + order + 1]) for i in range(len(seq) - order)
    )
    n = sum(joint.values())
    return -sum(v / n * math.log2(v / ctx[k[:-1]]) for k, v in joint.items())


def models() -> list[tuple[str, float]]:
    return [
        ("walk: base_0 + g + sigma", 3 * PERM_BITS),
        ("odometer: alphabet + schedule + 2 dials", PERM_BITS + 7 * math.log2(M)),
        ("per-word SHIFT base", 2928 * math.log2(M)),
        ("per-word base from a 1,000-element group", 2928 * math.log2(1000)),
        ("per-word arbitrary permutation", 2928 * PERM_BITS),
    ]


def main() -> None:
    plain = [r for t in json.loads(TRIPLES.read_text()) for r in t["plaintext_runes"]]
    h1 = conditional_entropy(plain, 0)
    h2 = conditional_entropy(plain, 1)
    print(f"author's plaintext: {len(plain):,} runes")
    print(
        f"  log2(29) = {math.log2(M):.2f}   H(unigram) = {h1:.2f}   H(|1 prev) = {h2:.2f}"
    )
    print(
        "\nD is the uncertain input. H(|1 prev) overstates the entropy of real English,"
    )
    print("so the true D is at the high end and the verdicts below are conservative.\n")

    ds = [math.log2(M) - h2, 2.4, 2.9]
    labels = [f"D={d:.2f}" for d in ds]
    print(f"{'key model':<42}{'H(key)':>11}" + "".join(f"{x:>12}" for x in labels))
    for name, h in models():
        row = f"{name:<42}{h:>11,.0f}"
        for d in ds:
            u = h / d
            row += f"{u:>9,.0f}{'  ok' if u < BODY_RUNES else '  NO'}"
        print(row)
    print(
        f"\n'ok' = unicity distance below the {BODY_RUNES:,} runes available, so the key is"
    )
    print(
        "determined in principle. 'NO' = more key entropy than the ciphertext can pin,"
    )
    print("so many keys give sensible plaintext and none is distinguishable.")


if __name__ == "__main__":
    main()
