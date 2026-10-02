# ABOUTME: Locates the DJU-BEI repeat in the body and finds its second occurrence is the
# ABOUTME: final six runes, which rules out the one direct test of the return hypothesis.
"""Four results hang on this repeat being a state return. The obvious test is impossible.

`dju-bei-needs-a-product-step.md`, `sigma-is-even.md` and
`dju-bei-favours-the-continuous-clock.md` all condition on the DJU-BEI repeat being a
genuine state return. The direct test is to look at what follows: if the state really
recurred, the two continuations run with the same base and phase, so their runes coincide
at the PLAINTEXT rate (1.79x chance) rather than at chance, for as long as the block
lengths keep the clocks aligned.

There is nothing to look at. The second occurrence is the last six runes of the body.

    python dju_bei_position.py
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ENG = c3301.CICADA_ENGLISH_ALPHABET


def main() -> None:
    stream, wid = load_clean()
    n = len(stream)
    windows = [tuple(stream[i : i + 6]) for i in range(n - 5)]
    counts = collections.Counter(windows)
    repeated = [k for k, v in counts.items() if v > 1]
    assert len(repeated) == 1, f"expected one repeated 6-gram, found {len(repeated)}"
    a, b = (i for i, x in enumerate(windows) if x == repeated[0])

    print(f"clean body: {n:,} runes in {wid[-1] + 1:,} blocks")
    print(f"repeat {''.join(ENG[x] for x in repeated[0])} at rune offsets {a} and {b}")
    print(f"  blocks {wid[a]} and {wid[b]}, of {wid[-1]}")
    print(f"  runes after the second occurrence: {n - b - 6}")
    print(
        f"  blocks occupied by the second occurrence: "
        f"{sorted({wid[i] for i in range(b, n)})}"
    )

    master = (
        (ROOT / "data" / "liber-primus__transcription--master.txt")
        .read_text()
        .split("%")
    )
    total = 0
    for k in range(15, 71):
        if not RUNE.search(master[k]):
            continue
        c = sum(1 for ch in master[k] if RUNE.match(ch))
        if total <= b < total + c:
            print(
                f"  master chunk {k}, offset {b - total} of {c}, "
                f"{total + c - b - 6} runes left in the chunk"
            )
        total += c

    p = 6 / (n - 5)
    print(
        f"\nSo the second occurrence is the FINAL six runes of the unsolved body -- the"
        f"\nlast two blocks of {wid[-1] + 1:,}, ending master chunk 70, which is the last"
        "\nbody chunk before the solved AN END page."
        "\n\nTwo consequences."
        "\n\n1. The state-continuation test cannot be run. There is no text after the"
        "\n   second occurrence, so the sharpest check on the return hypothesis -- the"
        "\n   one thing that would separate a state return from a coincidence -- is"
        "\n   unavailable. The four results downstream stay conditional."
        f"\n\n2. The position is not random. Given that a repeat exists, its landing in"
        f"\n   the final six runes has probability {p:.5f}, about 1 in {1 / p:,.0f}. A"
        "\n   chance reading of the repeat now has to explain the position as well, and"
        "\n   a deliberate reading -- a closing refrain, a colophon, a signature -- does"
        "\n   so for free."
        "\n\nThe position was noticed after the fact and should be weighed as such."
    )


if __name__ == "__main__":
    main()
