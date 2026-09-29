# ABOUTME: Tests whether the body's missing 2-rune blocks are separators lost at line wraps,
# ABOUTME: and records why the obvious follow-up test about separators per line is invalid.
"""If separators went missing at line ends, the line ends would show it.

`block-lengths-have-a-hole-at-two.md` leaves one ordinary explanation standing: the
transcription. The body is laid out in 594 lines of about 22 runes, and a separator
falling at a line break is the easiest kind to lose. Losing one merges two blocks into
one, which is exactly the shape of the deficit.

The test needs the right null, and the right null is length bias. A long block covers
more of a line, so it is more likely to contain a break whatever the scribe did. Lay the
body's own block lengths out over the body's own line lengths in random order and count:

    how many blocks contain a break, and how long they are

If separators were lost at breaks, the real text has both more spanning blocks and
longer ones than the null. Both are measured here.

The second half records a test that does NOT work, so it is not tried again: whether the
number of separators per line is more regular than chance. The null there has to hold the
line lengths fixed while shuffling the blocks, and in a real book the line lengths are
chosen to fit the content. Breaking that link breaks more than the hypothesis, and the
controls show it.

    python line_layout_and_the_hole.py
"""

from __future__ import annotations

import collections
import math
import random
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402
from fingerprint_battery import prose_corpora  # noqa: E402
from lp_plaintext_register import word_lengths  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
LINE = re.compile(r"[/\n]+")


def parse(text: str):
    """Line rune counts, line separator counts, block lengths, and span flags."""
    lines = []
    for line in LINE.split(text):
        n = len(RUNE.findall(line))
        if n:
            lines.append((n, sum(1 for ch in line if ch in c3301.WORD_BOUNDARY)))
    blocks, cur, wrapped = [], 0, False
    for ch in text:
        if RUNE.match(ch):
            cur += 1
        elif ch in "/\n":
            if cur:
                wrapped = True
        elif cur and ch in c3301.WORD_BOUNDARY:
            blocks.append((cur, wrapped))
            cur, wrapped = 0, False
    if cur:
        blocks.append((cur, wrapped))
    return (
        np.array([a for a, _ in lines], float),
        np.array([b for _, b in lines], float),
        blocks,
    )


def wraps_are_ordinary(runes_per_line: np.ndarray, blocks) -> None:
    lengths = [n for n, _ in blocks]
    observed = [n for n, w in blocks if w]
    cuts = set(np.cumsum(runes_per_line)[:-1].astype(int).tolist())
    rng = random.Random(4)
    counts, means = [], []
    for _ in range(500):
        order = lengths[:]
        rng.shuffle(order)
        spans, pos = [], 0
        for length in order:
            if any(pos < c < pos + length for c in cuts):
                spans.append(length)
            pos += length
        counts.append(len(spans))
        means.append(float(np.mean(spans)) if spans else 0.0)
    c, m = np.array(counts, float), np.array(means, float)
    print(
        f"{len(blocks):,} blocks in {len(runes_per_line)} lines of "
        f"{runes_per_line.mean():.1f} runes\n"
    )
    print(f"{'':<26}{'observed':>10}{'length-bias null':>20}{'z':>8}")
    print(
        f"{'blocks spanning a break':<26}{len(observed):>10}"
        f"{f'{c.mean():.1f} +- {c.std():.1f}':>20}"
        f"{(len(observed) - c.mean()) / c.std():>8.2f}"
    )
    om = float(np.mean(observed))
    print(
        f"{'their mean length':<26}{om:>10.3f}"
        f"{f'{m.mean():.3f} +- {m.std():.3f}':>20}"
        f"{(om - m.mean()) / m.std():>8.2f}"
    )
    print(
        "\nBoth are ordinary, and the mean is if anything SHORT. Losing separators at"
        "\nbreaks would make spanning blocks both commoner and longer. Neither happens."
    )

    clean = [n for n, w in blocks if not w]
    f2 = sum(1 for n in clean if n == 2) / len(clean)
    se = math.sqrt(f2 * (1 - f2) / len(clean))
    author = word_lengths()
    af2 = sum(1 for x in author if x == 2) / len(author)
    ase = math.sqrt(af2 * (1 - af2) / len(author))
    print(
        f"\nblocks that touch no line break: {len(clean):,}, fraction at length 2 "
        f"{f2:.4f} +- {se:.4f}"
    )
    print(
        f"  against the author's {af2:.4f} +- {ase:.4f}:  "
        f"z = {(f2 - af2) / math.sqrt(se**2 + ase**2):+.2f}"
    )
    print(
        "  The deficit survives in the blocks the line breaks never touched. This is"
        "\n  a length-biased subset -- it over-samples short blocks -- so its rate sits"
        "\n  above the body's own 0.1588 and still falls far below the author's."
    )


def separators_per_line_is_not_a_test(sets: dict[str, str]) -> None:
    """A test that looks decisive and is not. Recorded so it is not repeated."""
    rng = random.Random(12)

    def stats(runes, seps, blocks, draws=400):
        acc = np.cumsum(runes)
        sds, cors = [], []
        for _ in range(draws):
            order = blocks[:]
            rng.shuffle(order)
            c = collections.Counter(np.searchsorted(acc, np.cumsum(order), side="left"))
            v = np.array([c.get(i, 0) for i in range(len(runes))], float)
            sds.append(v.std())
            cors.append(np.corrcoef(runes, v)[0, 1])
        return (
            (seps.std() - np.mean(sds)) / np.std(sds),
            np.corrcoef(runes, seps)[0, 1],
            float(np.mean(cors)),
            (np.corrcoef(runes, seps)[0, 1] - np.mean(cors)) / np.std(cors),
        )

    print("\n\nThe separators-per-line test, and why it is invalid\n")
    print(
        f"{'text':<28}{'lines':>6}{'sd z':>8}{'corr obs':>10}{'corr null':>11}{'z':>8}"
    )
    for label, text in sets.items():
        runes, seps, blocks = parse(text)
        if len(runes) < 30:
            continue
        sd_z, co, cn, c_z = stats(runes, seps, [n for n, _ in blocks])
        print(
            f"{label:<28}{len(runes):>6}{sd_z:>8.2f}{co:>10.3f}{cn:>11.3f}{c_z:>8.2f}"
        )

    for k, plain in enumerate(prose_corpora(2928, 3)):
        lengths = [len(w) for w in plain]
        total, rem, ll = sum(lengths), sum(lengths), []
        while rem > 0:
            x = min(rem, max(6, int(rng.gauss(21.8, 2.6))))
            ll.append(x)
            rem -= x
        runes = np.array(ll, float)
        acc = np.cumsum(runes)
        c = collections.Counter(np.searchsorted(acc, np.cumsum(lengths), side="left"))
        seps = np.array([c.get(i, 0) for i in range(len(runes))], float)
        sd_z, co, cn, c_z = stats(runes, seps, lengths)
        print(
            f"{'prose control ' + str(k):<28}{len(runes):>6}{sd_z:>8.2f}"
            f"{co:>10.3f}{cn:>11.3f}{c_z:>8.2f}"
        )

    print(
        "\nThe body reads sd z about -4 and corr z about -8, which looked like separators"
        "\nplaced by the line rather than by the text. Two controls kill it. Ordinary"
        "\nprose laid out the same way reads sd z between -3 and -5, the same as the body."
        "\nAnd the book's own PLAINTEXT front matter reads corr z about -21, more extreme"
        "\nthan the body by a wide margin."
        "\n\nThe reason is the null. It holds the line lengths fixed and shuffles the"
        "\nblocks, but a scribe chooses where to break a line to fit what is on it, so"
        "\nline length and content are not independent. The null breaks that link as well"
        "\nas the hypothesis, and manufactures a coupling the real text never had."
    )


def main() -> None:
    body = (ROOT / "data" / "page0-56.txt").read_text()
    runes, _, blocks = parse(body)
    wraps_are_ordinary(runes, blocks)
    master = (ROOT / "data" / "liber-primus__transcription--master.txt").read_text()
    chunks = master.split("%")
    separators_per_line_is_not_a_test(
        {
            "body (pages 0-56)": body,
            "front matter, all 15": "\n".join(chunks[:15]),
            "front matter, plaintext": "\n".join(
                chunks[i] for i in (3, 8, 9, 10, 11, 14)
            ),
            "front matter, enciphered": "\n".join(
                chunks[i] for i in (0, 1, 2, 4, 5, 6, 7, 12, 13)
            ),
        }
    )


if __name__ == "__main__":
    main()
