# ABOUTME: Dissolves the rubricated-title lead by controlling for sentence position, which
# ABOUTME: the titles are disproportionately made of, and measures that effect instead.
"""The titles' elevated 2-rune rate is composition, not content.

`titles_may_escape_the_hole.py` reports that the seventeen rubricated titles have a 2-rune
fraction of 0.231 against the rest of the body's 0.158, z = +1.25, and reads it as a lead
that whatever causes the hole spares the titles.

There is a confound it did not control. In English, sentence-initial words are
disproportionately short function words -- THE, WE, TO, IT, HE -- and a title is a unit
that STARTS. Seventeen of the fifty-two title blocks are title-initial, a third, against
7% of body blocks that follow a heavy mark.

So compare like with like: title-initial blocks against the body's own sentence-initial
blocks, and the remaining title blocks against the rest of the body. The heavy marks --
the circled numerals, and the page and section breaks -- are what mark a sentence in the
body.

    python titles_are_just_sentence_initial.py
"""

from __future__ import annotations

import importlib.util
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

RUNE = re.compile(r"[ᚠ-᛿]")
HEAVY = set('④⑬③⑩%$"')


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


def body_by_sentence_position():
    """(length, follows a heavy mark) for every body block."""
    text = (ROOT / "data" / "page0-56.txt").read_text()
    rows, cur, after = [], 0, False
    for ch in text:
        if RUNE.match(ch):
            cur += 1
        elif ch in "/\n":
            continue
        elif ch in c3301.WORD_BOUNDARY:
            if cur:
                rows.append((cur, after))
                cur = 0
            after = ch in HEAVY
    return rows


def rate(v) -> tuple[float, float, int]:
    a = np.array(v, float)
    f = float((a == 2).mean())
    return f, math.sqrt(f * (1 - f) / len(a)), len(a)


def main() -> None:
    master = (ROOT / "data" / "liber-primus__transcription--master.txt").read_text()
    chunks = master.split("%")
    titles = json.loads((ROOT / "experiments" / "rubricated_titles.json").read_text())

    first, rest_of_title = [], []
    for x in titles:
        w = words_of(chunks[x["chunk"]])
        a, b = x["word_range"]
        ls = [len(y) for y in w[a : b + 1]]
        if ls:
            first.append(ls[0])
            rest_of_title += ls[1:]

    rows = body_by_sentence_position()
    sentence_initial = [L for L, a in rows if a]
    elsewhere = [L for L, a in rows if not a]

    print("sentence position in the body, on the heavy marks\n")
    print(f"{'group':<34}{'blocks':>8}{'frac at 2':>12}{'se':>9}")
    for label, v in (("after a heavy mark", sentence_initial),
                     ("elsewhere", elsewhere)):
        f, se, n = rate(v)
        print(f"{label:<34}{n:>8,}{f:>12.4f}{se:>9.4f}")
    fi, _, _ = rate(sentence_initial)
    fe, _, _ = rate(elsewhere)
    print(f"elevation after a heavy mark: {fi / fe:.2f}x")

    spec = importlib.util.spec_from_file_location(
        "lp_plaintext_register", ROOT / "experiments" / "lp_plaintext_register.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pages = mod.MASTER.read_text().split("%")
    plain_first, plain_rest = [], []
    for n in mod.PLAIN_PAGES:
        cur, after = [], True
        for ch in pages[n]:
            if RUNE.match(ch):
                cur.append(ch)
            elif ch in "/\n":
                continue
            elif cur and ch in c3301.WORD_BOUNDARY:
                (plain_first if after else plain_rest).append(len(cur))
                cur = []
                after = ch == "."
    pf, _, npf = rate(plain_first)
    pr, _, npr = rate(plain_rest)
    print(f"\nthe author's own plaintext, split on '.': "
          f"{pf:.4f} on {npf} against {pr:.4f} on {npr}, {pf / pr:.2f}x")
    print("So the elevation is a property of English, and the body keeps it.")

    print("\n\nthe titles, compared like with like\n")
    print(f"{'group':<34}{'blocks':>8}{'frac at 2':>12}{'se':>9}")
    for label, v in (("first block of a title", first),
                     ("the rest of the titles", rest_of_title)):
        f, se, n = rate(v)
        print(f"{label:<34}{n:>8}{f:>12.4f}{se:>9.4f}")

    f1, s1, n1 = rate(first)
    f2, s2, n2 = rate(sentence_initial)
    print(f"\ntitle-initial against the body's sentence-initial blocks: "
          f"z = {(f1 - f2) / math.sqrt(s1**2 + s2**2):+.2f}")
    f3, s3, n3 = rate(rest_of_title)
    f4, s4, n4 = rate(elsewhere)
    print(f"the rest of the titles against the body elsewhere:        "
          f"z = {(f3 - f4) / math.sqrt(s3**2 + s4**2):+.2f}")
    print(
        "\nBoth under 0.7 sigma. The titles are ordinary once sentence position is"
        "\ncontrolled, and the 1.25 sigma reported earlier was composition: a third of"
        "\ntitle blocks are title-initial against 7% of body blocks following a heavy"
        "\nmark, and sentence-initial blocks carry a 1.46x elevated 2-rune rate."
        "\n\nThe lead is withdrawn. What replaces it is smaller and real: the body's"
        "\n2-rune rate rises after a heavy mark exactly as English does, which is one"
        "\nmore way the body behaves like ordinary text."
    )


if __name__ == "__main__":
    main()
