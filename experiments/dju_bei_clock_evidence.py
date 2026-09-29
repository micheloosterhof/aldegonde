# ABOUTME: Reads the DJU-BEI rune gap as evidence on the clock convention, which the
# ABOUTME: coincidence channel cannot settle with this corpus.
"""The return divides by five, and only one clock convention needs it to.

`clock-convention-is-out-of-reach.md` prices the two channels that bear on whether the
letter phase resets at each block or runs continuously, and finds the sharpest of them a
quarter the size it would need to be -- 14 times the corpus. So the question sits open,
and it is worth five bits on the sigma order bound.

The DJU-BEI return speaks to it, and had not been read that way.

Under a **continuous** clock, the alphabet at a block start is `base_w o g^(A_w mod 5)`
where A_w is the cumulative rune count. Two occurrences produce identical ciphertext only
if the bases agree AND the phases agree, so the rune gap must be divisible by 5.

Under a **reset** clock, every block starts at phase 0, so only the bases need agree and
the gap is unconstrained.

The rune gap is 6,395 = 5 x 1,279.

    python dju_bei_clock_evidence.py
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402


def main() -> None:
    stream, wid = load_clean()
    windows = [tuple(stream[i : i + 6]) for i in range(len(stream) - 5)]
    counts = collections.Counter(windows)
    repeats = [k for k, v in counts.items() if v > 1]
    print(f"repeated 6-grams in the body: {len(repeats)}")
    for k in repeats:
        pos = [i for i, x in enumerate(windows) if x == k]
        rune_gap = pos[1] - pos[0]
        block_gap = wid[pos[1]] - wid[pos[0]]
        print(f"  rune offsets {pos}, rune gap {rune_gap}, block gap {block_gap}")
        print(
            f"  rune gap mod 5 = {rune_gap % 5}   ({rune_gap} = 5 x {rune_gap // 5})"
            if rune_gap % 5 == 0
            else ""
        )

    print(
        "\nUnder a continuous clock a state return REQUIRES the rune gap to be divisible"
        "\nby 5; under a reset clock it does not. The gap is divisible by 5, which is"
        "\ncertain under one hypothesis and one chance in five under the other:"
        "\n\n    likelihood ratio 5 : 1 in favour of the continuous clock"
        "\n\nconditional, as everything downstream of this repeat is, on the return being"
        "\ngenuine rather than the 1-in-2,700 coincidence. The rune gap is invariant"
        "\nunder every tokenization audited, so unlike the word gap this reading does not"
        "\ndepend on which marks advance the clock."
    )


if __name__ == "__main__":
    main()
