# ABOUTME: Tests whether the body's blocks lengthen before a sentence mark the way
# ABOUTME: real English words do, and finds that they do not.
"""English sentences end on a long word. The body's sentences do not.

`titles_are_just_sentence_initial.py` established that the body's heavy marks really
mark sentences: blocks just after one carry the same excess of short units that
sentence-initial words carry in English. That gives a second, sharper probe the marks
now make available -- the position just *before* a mark.

In English the sentence-final word is systematically longer than an interior word. It
is a content word: a noun or a verb, rarely a two-letter function word. Pride and
Prejudice puts the final word **+1.00 runes** above its own interior mean, and the LP's
own author is stronger still -- **0 of 85** sentence-final words on the sixteen solved
pages are two runes long, against 27% of interior words.

The body's blocks do not do this. The block before a circled numeral runs **-0.21 runes**
against the body's own interior: no lengthening at all.

Joining is the explanation to rule out first, and it is not neutral. The body joins
units of two runes or less to a neighbour at q ~ 0.40
(`short-units-are-written-joined.md`). Joining removes short units, and the interior
cell holds more of them than the final cell does, so it lifts the interior mean further
and genuinely *shrinks* the gap. Running that model forward on Austen at its fitted rate
leaves **+0.79 +- 0.04**, not +1.00 -- and reproduces the body's interior mean of 4.49
on the way, a check it was never asked to pass. Even q = 0.70, far above the fitted
value, only reaches +0.59. The observed -0.21 +- 0.18 is **5.5 sigma** below the joined
prediction.

That leaves four readings, and the experiment prints what separates them:

1. the body's plaintext has no sentence-final lengthening, unlike both reference texts;
2. the circled numerals are not sentence marks -- but then the sentence-*initial* match
   against the author (z = +0.83) is a coincidence, and it is printed here as a control;
3. a block adjacent to a mark is not a word but a cipher-cut remainder, whose length is
   drawn from the ordinary block distribution. This predicts a difference of zero;
4. the marks *open* rather than close. A numeral labelling the verse that follows it
   terminates nothing, so the block before it is mid-sentence and flat by construction,
   while the block after it still starts a unit of text. This explains both cells at
   once and is the most economical reading -- though four distinct numerals, one of
   them 139 of 174, is the shape of punctuation rather than of numbering.

Reading 3 sits against `blocks-are-still-words.md`, which read the *marginal* length
distribution as words rather than cuts. They are compatible: that file excludes a
**natural** cutting rule, not cuts in general, and a rule word-shaped in its marginal
but mechanical at a sentence edge is exactly the unnatural rule it declines to exclude.

    python sentences_do_not_end_long.py
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
import tempfile
import urllib.request
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import IDX_ENG, to_runeglish  # noqa: E402
from lp_plaintext_register import MASTER, PLAIN_PAGES, TRIPLES  # noqa: E402

from aldegonde import c3301  # noqa: E402

BODY = ROOT / "data" / "page0-56.txt"
PROSE_URL = "https://www.gutenberg.org/files/1342/1342-0.txt"
PROSE = Path(tempfile.gettempdir()) / "pg1342.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
SENTENCE_MARKS = set("④⑬③⑩")


def content(chunk: str) -> str:
    """The transcription's rune lines, without its numeric annotation lines.

    Lines like `3258-3222-3152-3038` carry no runes and sit between a mark and the
    block that follows it, so leaving them in clears the sentence-initial flag.
    """
    return "\n".join(l for l in chunk.replace("/", "\n").split("\n") if RUNE.search(l))


def blocks(chunk: str, marks: set[str]) -> list[tuple[int, bool, bool]]:
    """(length, follows a mark, precedes a mark) for each block of runes."""
    return [row[:3] for row in walk(chunk, marks)]


def walk(chunk: str, marks: set[str]) -> list[tuple[int, bool, bool, bool]]:
    """(length, follows a mark, precedes a mark, is line-final) for each block.

    A line break never ends a block -- the transcription breaks long units across
    lines without a separator -- so it only records that the block which just ended
    was the last one on its line.
    """
    out: list[tuple[int, bool, bool, bool]] = []
    length, initial, pending, newline = 0, True, None, False
    for ch in content(chunk):
        if RUNE.match(ch):
            if pending is not None:
                out.append((*pending, newline))
                pending = None
            newline, length = False, length + 1
        elif ch == "\n":
            newline = True
        elif ch in c3301.WORD_BOUNDARY:
            if length:
                if pending is not None:
                    out.append((*pending, newline))
                    newline = False
                pending, length = (length, initial, ch in marks), 0
            initial = ch in marks
    if pending is not None:
        out.append((*pending, newline))
    if length:
        out.append((length, initial, True, True))
    return out


def author_words() -> list[tuple[int, bool, bool]]:
    """The sixteen solved pages, where the sentence mark is a period."""
    pages = MASTER.read_text().split("%")
    rows: list[tuple[int, bool, bool]] = []
    for n in PLAIN_PAGES:
        rows += blocks(pages[n], {"."})
    for t in json.loads(TRIPLES.read_text()):
        rows += blocks(pages[t["page"]], {"."})
    return rows


def prose_text() -> str:
    """Pride and Prejudice, fetched to the same cache the other experiments use."""
    if not PROSE.exists():
        print(f"downloading {PROSE_URL} -> {PROSE}")
        urllib.request.urlretrieve(PROSE_URL, PROSE)
    return PROSE.read_text(encoding="utf-8", errors="replace")


def prose_words() -> list[tuple[int, bool, bool]]:
    """Ordinary English prose through the same runeglish pipeline."""
    text = prose_text()
    trim = len(text) // 10
    rows: list[tuple[int, bool, bool]] = []
    for sentence in re.split(r"[.!?]+", text[trim : len(text) - trim]):
        words = [
            [IDX_ENG[c] for c in to_runeglish(w.upper()) if c in IDX_ENG]
            for w in re.findall(r"[A-Za-z']+", sentence)
        ]
        words = [w for w in words if w]
        if len(words) < 3:
            continue
        rows.append((len(words[0]), True, False))
        rows.append((len(words[-1]), False, True))
        rows += [(len(w), False, False) for w in words[1:-1]]
    return rows


def cells(rows):
    """interior, sentence-initial and sentence-final lengths, kept disjoint."""
    return (
        np.array([l for l, i, f in rows if not i and not f], float),
        np.array([l for l, i, f in rows if i and not f], float),
        np.array([l for l, i, f in rows if f and not i], float),
    )


def mean_gap(v, mid):
    """How much longer this cell runs than the same text's interior."""
    d = float(v.mean() - mid.mean())
    se = math.sqrt(v.var(ddof=1) / len(v) + mid.var(ddof=1) / len(mid))
    return d, se


def two_rune_logodds(v, mid):
    """Odds of a two-rune unit here against the interior, Haldane-corrected."""
    a = float((v == 2).sum()) + 0.5
    b = len(v) - a + 1.0
    c = float((mid == 2).sum()) + 0.5
    d = len(mid) - c + 1.0
    return math.log(a * d / (b * c)), math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)


def main() -> None:
    texts = {
        "Pride and Prejudice": prose_words(),
        "the LP author, 16 pages": author_words(),
        "the LP body": blocks(BODY.read_text(), SENTENCE_MARKS),
    }
    stats: dict[tuple[str, str], tuple[float, float]] = {}

    print("Mean unit length against the same text's own interior.\n")
    print(f"{'text':<26}{'position':<10}{'units':>8}{'mean':>8}{'gap vs interior':>19}")
    for name, rows in texts.items():
        mid, ini, fin = cells(rows)
        print(f"{name:<26}{'interior':<10}{len(mid):>8,}{mid.mean():>8.2f}{'':>19}")
        for pos, v in (("initial", ini), ("final", fin)):
            d, se = mean_gap(v, mid)
            stats[name, pos] = (d, se)
            print(
                f"{'':<26}{pos:<10}{len(v):>8,}{v.mean():>8.2f}"
                f"{f'{d:+.2f} +- {se:.2f}':>19}"
            )

    print("\nOdds of a two-rune unit, same cells.\n")
    print(f"{'text':<26}{'position':<10}{'at 2':>8}{'log odds ratio':>19}")
    for name, rows in texts.items():
        mid, ini, fin = cells(rows)
        for pos, v in (("initial", ini), ("final", fin)):
            lo, se = two_rune_logodds(v, mid)
            stats[name, pos + " odds"] = (lo, se)
            print(
                f"{name:<26}{pos:<10}{int((v == 2).sum()):>8}"
                f"{f'{lo:+.2f} +- {se:.2f}':>19}"
            )

    print(
        "\nThe body against each reference. 'final' is the test, 'initial' the control.\n"
    )
    print(f"{'statistic':<20}{'position':<10}{'vs Austen':>12}{'vs the author':>16}")
    for label, key in (("mean length", ""), ("two-rune odds", " odds")):
        for pos in ("initial", "final"):
            lb, sb = stats["the LP body", pos + key]
            row = f"{label:<20}{pos:<10}"
            for ref in ("Pride and Prejudice", "the LP author, 16 pages"):
                la, sa = stats[ref, pos + key]
                row += (
                    f"{(lb - la) / math.hypot(sa, sb):>+12.2f}"
                    if ref.startswith("P")
                    else f"{(lb - la) / math.hypot(sa, sb):>+16.2f}"
                )
            print(row)

    robustness()
    joining_forward()

    print(
        "\nThe control passes and the test fails. Blocks after a mark carry the same"
        "\nexcess of short units that English sentence-initial words carry, so the marks"
        "\nare sentence marks. Blocks before a mark carry none of the lengthening that"
        "\nEnglish sentence-final words carry."
        "\n\nJoining shrinks the gap but does not close it: at its fitted rate it"
        "\npredicts +0.79, and at a rate well above fitted it still predicts +0.59."
        "\nEither the body's plaintext ends sentences unlike any English reference,"
        "\nor the block adjacent to a mark is not a word."
    )


def prose_sentences() -> list[list[int]]:
    """Austen's word lengths, kept grouped by sentence so joining runs in sequence."""
    text = prose_text()
    trim = len(text) // 10
    out = []
    for sentence in re.split(r"[.!?]+", text[trim : len(text) - trim]):
        lengths = [
            len([c for c in to_runeglish(w.upper()) if c in IDX_ENG])
            for w in re.findall(r"[A-Za-z']+", sentence)
        ]
        lengths = [n for n in lengths if n]
        if len(lengths) >= 3:
            out.append(lengths)
    return out


def join(
    sentence: list[int], q: float, rng: random.Random, *, forward: bool
) -> list[int]:
    """Merge each unit of two runes or less into a neighbour with probability q."""
    out, i = list(sentence), 0
    while i < len(out):
        j = i + 1 if forward else i - 1
        if out[i] <= 2 and rng.random() < q and 0 <= j < len(out):
            out[j] += out[i]
            out.pop(i)
            continue
        i += 1
    return out


def sentence_gap(sentences):
    """Final-word mean minus interior mean, over sentences of three words or more."""
    kept = [s for s in sentences if len(s) >= 3]
    fin = np.array([s[-1] for s in kept], float)
    mid = np.array([x for s in kept for x in s[1:-1]], float)
    se = math.hypot(
        fin.std(ddof=1) / math.sqrt(len(fin)), mid.std(ddof=1) / math.sqrt(len(mid))
    )
    return float(fin.mean() - mid.mean()), se, float(mid.mean())


def joining_forward() -> None:
    """Run the body's own joining model forward on English and see what gap it leaves.

    Joining is not neutral here. It removes short units, and the interior cell holds
    more of them than the final cell does, so it lifts the interior mean further and
    *shrinks* the gap. The question is whether it shrinks it far enough.
    """
    sentences = prose_sentences()
    print(
        "\nThe body joins units of two runes or less at q ~ 0.40. Run that model"
        "\nforward on Austen: it shrinks the gap, and the question is by how much.\n"
    )
    print(f"{'model':<46}{'interior':>10}{'final gap':>18}")
    gap, se, mid = sentence_gap(sentences)
    print(f"{'Austen, untouched':<46}{mid:>10.2f}{f'{gap:+.2f} +- {se:.2f}':>18}")
    rng = random.Random(3301)
    fitted = None
    for q in (0.40, 0.55, 0.70):
        for forward in (True, False):
            gap, se, mid = sentence_gap(
                [join(s, q, rng, forward=forward) for s in sentences]
            )
            where = "following" if forward else "preceding"
            print(
                f"{f'joined q={q:.2f}, into the {where} unit':<46}"
                f"{mid:>10.2f}{f'{gap:+.2f} +- {se:.2f}':>18}"
            )
            if q == 0.40 and forward:
                fitted = (gap, se)

    rows = walk(BODY.read_text(), SENTENCE_MARKS)
    length = np.array([r[0] for r in rows], float)
    keep = np.array([r[2] and not r[1] for r in rows])
    base = np.array([not r[1] and not r[2] for r in rows])
    observed = float(length[keep].mean() - length[base].mean())
    se_obs = math.hypot(
        length[keep].std(ddof=1) / math.sqrt(keep.sum()),
        length[base].std(ddof=1) / math.sqrt(base.sum()),
    )
    print(
        f"\n{'the LP body, observed':<46}"
        f"{float(length[base].mean()):>10.2f}{f'{observed:+.2f} +- {se_obs:.2f}':>18}"
    )
    print(
        f"\nJoining at the fitted rate leaves {fitted[0]:+.2f} +- {fitted[1]:.2f}, and it"
        f"\nreproduces the body's interior mean on the way, which is a check it was not"
        f"\nasked to pass. The body reads {observed:+.2f} +- {se_obs:.2f}:"
        f" z = {(observed - fitted[0]) / math.hypot(se_obs, fitted[1]):+.2f}."
        f"\nEven q = 0.70, far above the fitted value, does not reach the observation."
    )


def robustness() -> None:
    """The gap survives the two layout confounds that could manufacture it."""
    raw = BODY.read_text()
    rows = walk(raw, SENTENCE_MARKS)
    a = np.array(rows, float)
    length, ini, fin, eol = a[:, 0], a[:, 1] > 0, a[:, 2] > 0, a[:, 3] > 0

    def cell(sel):
        v = length[sel]
        return len(v), float(v.mean()), float(v.std(ddof=1) / math.sqrt(len(v)))

    print("\nRobustness. A mark could sit where the layout already shortens a block.\n")
    print(f"{'cell':<34}{'blocks':>8}{'mean':>8}{'se':>7}")
    for lab, sel in (
        ("interior, mid-line", ~ini & ~fin & ~eol),
        ("interior, line-final", ~ini & ~fin & eol),
        ("mark-final, mid-line", fin & ~ini & ~eol),
        ("mark-final, line-final", fin & ~ini & eol),
    ):
        n, m, se = cell(sel)
        print(f"{lab:<34}{n:>8,}{m:>8.2f}{se:>7.2f}")

    share = (fin & ~ini & ~eol).sum() / (fin & ~ini).sum()
    _, mid_line, se_mid = cell(~ini & ~fin & ~eol)
    _, at_eol, se_eol = cell(~ini & ~fin & eol)
    matched = share * mid_line + (1 - share) * at_eol
    se_matched = math.hypot(share * se_mid, (1 - share) * se_eol)
    _, observed, se_obs = cell(fin & ~ini)
    gap, se_gap = observed - matched, math.hypot(se_obs, se_matched)
    print(
        f"\nline-position-matched gap: {gap:+.2f} +- {se_gap:.2f}"
        f"   (Austen z = {(gap - 1.00) / math.hypot(se_gap, 0.04):+.2f})"
    )

    # pages are the heterogeneous unit, so each final block is compared against its
    # own page's interior and the error comes from a jackknife over pages
    per_page, weight = [], []
    for page in raw.split("%"):
        rows = walk(page, SENTENCE_MARKS)
        mid = [l for l, i, f, _ in rows if not i and not f]
        end = [l for l, i, f, _ in rows if f and not i]
        if len(mid) >= 5 and end:
            per_page.append(float(np.mean(end) - np.mean(mid)))
            weight.append(float(len(end)))
    per_page, weight = np.array(per_page), np.array(weight)

    def pooled(mask):
        return float((per_page[mask] * weight[mask]).sum() / weight[mask].sum())

    keep = np.ones(len(per_page), bool)
    drop = np.array(
        [pooled(keep & (np.arange(len(per_page)) != k)) for k in range(len(per_page))]
    )
    est = pooled(keep)
    se = math.sqrt((len(drop) - 1) / len(drop) * ((drop - drop.mean()) ** 2).sum())
    print(
        f"page-matched gap:          {est:+.2f} +- {se:.2f}"
        f"   ({len(per_page)} pages, {int(weight.sum())} blocks)"
    )
    print(
        "\nNeither confound carries it: the gap is the same mid-line and at a line"
        "\nend, and the same within a page as across the book."
    )


if __name__ == "__main__":
    main()
