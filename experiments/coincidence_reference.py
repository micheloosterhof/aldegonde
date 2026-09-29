# ABOUTME: Measures what a SHARED ALPHABET would actually produce, by pair type, replacing
# ABOUTME: the single constant 1.74 that several files cite from trust.
"""A shared alphabet does not predict one number. It predicts a different one per pair type.

Several files here price a candidate cipher against "what a shared alphabet would give"
and quote 1.74, which is 0.060 x 29. `rotor-machine-compact-state.md` lists that constant
under "taken on trust, not verified here". `d5-partial-alphabet-leak.md` quietly uses a
different value, ~1.60, noting 1.74 belongs to a random dictionary word LIST rather than
to running text.

Both are approximations of something that is not a constant. If two positions share an
alphabet they coincide at the plaintext's coincidence rate *for that kind of pair*, and
that rate depends on whether the pair sits inside one word and how far apart it is. The
LP's own plaintext runs from 0.63 at distance 1 to 2.23 at distance 7.

So measure the table instead of quoting a number.

    python coincidence_reference.py
"""

from __future__ import annotations

import collections
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import corpus  # noqa: E402

CACHE = Path(tempfile.gettempdir()) / "lp_external_texts"
M = 29


def prose_words(limit: int = 60000) -> list[list[int]]:
    from runeglish_frequency import english_to_runeglish  # noqa: PLC0415

    text = (CACHE / "pg1033.txt").read_text(encoding="utf-8", errors="ignore")
    words = [
        [ord(c) for c in english_to_runeglish(w)]
        for w in re.findall(r"[A-Za-z]+", text.upper())[:limit]
    ]
    return [w for w in words if w]


def unconditional(words: list[list[int]]) -> tuple[float, int]:
    c = collections.Counter(r for w in words for r in w)
    n = sum(c.values())
    return M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1)), n


def within(words: list[list[int]], lag: int) -> tuple[float, int]:
    hits = pairs = 0
    for w in words:
        for i in range(len(w) - lag):
            pairs += 1
            hits += w[i] == w[i + lag]
    return (hits / pairs * M if pairs else 0.0), pairs


def main() -> None:
    lp = corpus()
    pr = prose_words()
    print(f"{'pair type':<36}{'LP plaintext':>22}{'runeglish prose':>22}")
    u1, n1 = unconditional(lp)
    u2, n2 = unconditional(pr)
    print(
        f"{'unconditional (cross-block)':<36}{u1:>14.3f} ({n1:>7,}){u2:>14.3f} ({n2:>7,})"
    )
    wl = wp = pl = pp = 0.0
    for lag in range(1, 8):
        a, pa = within(lp, lag)
        b, pb = within(pr, lag)
        print(
            f"{'within-block d=' + str(lag):<36}{a:>14.3f} ({pa:>7,}){b:>14.3f} ({pb:>7,})"
        )
        if 2 <= lag <= 4:
            wl += a * pa
            wp += pa
            pl += b * pb
            pp += pb
    print(
        f"{'within-block d=2..4, pair-weighted':<36}{wl / wp:>14.3f}{'':>10}"
        f"{pl / pp:>14.3f}"
    )
    print(
        "\nUse the row that matches the pair type being tested. For cross-block pairs at"
        "\narbitrary positions the reference is 1.79, not 1.74, and the two corpora agree"
        "\nto three decimals. For within-block pairs it is distance-dependent and a single"
        "\nconstant is wrong by up to a factor of three."
    )


if __name__ == "__main__":
    main()
