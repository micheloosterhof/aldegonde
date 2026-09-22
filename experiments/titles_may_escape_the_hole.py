# ABOUTME: Asks whether the rubricated titles show the body's hole at length two, and finds
# ABOUTME: they look like ordinary English instead -- a lead at 1.25 sigma on 52 blocks.
"""The hole at length two has only ever been tested against text outside the body.

`block-lengths-have-a-hole-at-two.md` compares the body's block lengths with the author's
own plaintext, with twenty-two English registers, and across the body's nine sections.
Every one of those contrasts is between the body and something outside it.

The seventeen rubricated titles are inside it. They sit on the same pages, in the same
hand, marked in red, and `rubricated_titles.json` records where each begins and ends. If
the hole is a property of the body's text, the titles should share it. If the titles look
like ordinary English, whatever causes the hole spares them.

Fifty-two blocks is not many, and the file says what the answer is worth.

    python titles_may_escape_the_hole.py
"""

from __future__ import annotations

import collections
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402
from fingerprint_battery import lp_words  # noqa: E402
from lp_plaintext_register import word_lengths  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
CAP = 10


def words_of(chunk: str):
    out, cur = [], []
    for ch in chunk:
        if RUNE.match(ch):
            cur.append(ch)
        elif ch in "/\n":
            continue
        elif cur and ch in c3301.WORD_BOUNDARY:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def histogram(v) -> np.ndarray:
    c = collections.Counter(min(x, CAP) for x in v)
    return np.array([c[k] for k in range(1, CAP + 1)], float)


def main() -> None:
    master = (ROOT / "data" / "liber-primus__transcription--master.txt").read_text()
    chunks = master.split("%")
    titles = json.loads((ROOT / "experiments" / "rubricated_titles.json").read_text())

    title_lengths = []
    print(f"{'page':>5}{'chunk':>6}{'runes':>6}  block lengths")
    for x in titles:
        w = words_of(chunks[x["chunk"]])
        a, b = x["word_range"]
        ls = [len(y) for y in w[a : b + 1]]
        title_lengths += ls
        print(f"{x['page']:>5}{x['chunk']:>6}{x['runes']:>6}  {ls}")

    body = [len(w) for w in lp_words()]
    rest = body[:]
    for length in title_lengths:
        if length in rest:
            rest.remove(length)

    A, B = histogram(title_lengths), histogram(rest)
    na, nb = A.sum(), B.sum()
    print(f"\n{'len':>4}{'titles':>10}{'body minus titles':>20}")
    for i in range(CAP):
        print(f"{i + 1:>4}{A[i] / na:>10.3f}{B[i] / nb:>20.4f}")
    print(f"{'mean':>4}{sum((i + 1) * A[i] for i in range(CAP)) / na:>10.2f}"
          f"{sum((i + 1) * B[i] for i in range(CAP)) / nb:>20.2f}")

    chi, df = 0.0, 0
    for i in range(CAP):
        tot = A[i] + B[i]
        if tot < 8:
            continue
        ea, eb = tot * na / (na + nb), tot * nb / (na + nb)
        chi += (A[i] - ea) ** 2 / ea + (B[i] - eb) ** 2 / eb
        df += 1
    fa, fb = A[1] / na, B[1] / nb
    se = math.sqrt(fa * (1 - fa) / na + fb * (1 - fb) / nb)
    author = word_lengths()
    f_auth = sum(1 for x in author if x == 2) / len(author)
    sa = math.sqrt(f_auth * (1 - f_auth) / len(author))

    print(f"\ntwo-sample chi2 over the whole distribution: {chi:.1f} on {df - 1} df")
    print(f"\n{'comparison':<40}{'fraction at 2':>16}{'z':>8}")
    print(f"{'the titles':<40}{f'{fa:.3f} +- {math.sqrt(fa * (1 - fa) / na):.3f}':>16}")
    print(f"{'against the rest of the body':<40}{fb:>16.3f}{(fa - fb) / se:>8.2f}")
    zz = (fa - f_auth) / math.sqrt(fa * (1 - fa) / na + sa**2)
    print(f"{chr(34)+'against the author own plaintext'+chr(34):<40}"
          f"{f_auth:>16.3f}{zz:>8.2f}")

    # se scales as 1/sqrt(n), so reaching 3 sigma needs (se / target_se)^2 times as many
    need = (se / ((fa - fb) / 3)) ** 2 * na
    print(
        f"\nThe titles are indistinguishable from the author's ordinary plaintext and sit"
        f"\n{(fa - fb) / se:.2f} sigma from the rest of the body. On {int(na)} blocks that is a"
        "\nlead, not a finding, and two things weigh against reading it as one."
        "\n\nTitles are short phrases, and short phrases carry FEWER function words than"
        "\nrunning text, so the register confound points the opposite way to the"
        "\nobservation rather than explaining it -- which makes the lead more interesting"
        "\nand not less, but it is still a confound."
        "\n\nAnd the whole-distribution chi2 shows nothing at all, so only the length-2"
        "\ncell carries the signal, which is where one would look first."
        f"\n\nTo reach three sigma this needs about {need:.0f} title blocks against the"
        f" {int(na)} that exist,\nroughly six times as many rubricated titles as have been"
        " identified."
    )


if __name__ == "__main__":
    main()
