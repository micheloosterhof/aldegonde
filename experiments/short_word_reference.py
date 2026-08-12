# ABOUTME: Checks the 2-rune deficit against a large external English reference
# ABOUTME: instead of the 698-word solved sample, and calibrates the converter.
"""Is the short-word deficit an artifact of a noisy reference?

`word-length-keystream-and-boundaries.md` calls the 2-rune deficit "the hardest
single fact in the boundary question": the unsolved corpus is 15.9% 2-rune
words against 24% in the solved pages, a gap no segmentation convention closes.
It also names the weakness -- the solved side is only ~700 words, so "a better
register reference could move this materially".

This supplies one. English word lengths carried into runeglish over the 50,000
commonest words, weighted by token frequency, give an independent estimate that
does not depend on the solved sample at all.

The obvious objection is transliteration convention: if this converter contracts
digraphs more eagerly than the Liber Primus scribe did, it would manufacture
short words and the comparison would be worthless. That is checkable without any
decrypted plaintext, because the solved pages are themselves runeglish in the
book's own convention -- so the converter's English estimate and the solved rune
text should agree. They do, to 0.26 points against a standard error of 1.61.

With the convention calibrated the deficit does not soften: it is z = -9.9
against the large reference, where the solved comparison gave +4.9. The
reference was never the problem, and better register data will not dissolve
this. Either the plaintext really does use a third fewer 2-rune function words
than the same author's solved writing, or the word boundaries are not
plaintext-faithful.
"""

from __future__ import annotations

import sys
from collections import Counter
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from runeglish_frequency import english_to_runeglish  # noqa: E402
from walk_verifier import load_words  # noqa: E402

from aldegonde import c3301  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
SOLVED_LINES = 187  # the solved intro pages, as in short_word_deficit.py
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}


def rune_word_lengths(text: str) -> list[int]:
    """Word lengths in runes, splitting on the mark alphabet."""
    out: list[int] = []
    cur = 0
    for ch in text:
        if ch in IDX:
            cur += 1
        elif ch in c3301.WORD_BOUNDARY and cur:
            out.append(cur)
            cur = 0
    if cur:
        out.append(cur)
    return out


def english_lengths() -> tuple[Counter[int], float]:
    """Frequency-weighted runeglish word-length distribution of English."""
    from wordfreq import top_n_list, word_frequency

    dist: Counter[int] = Counter()
    total = 0.0
    for word in top_n_list("en", 50000):
        if not word.isalpha():
            continue
        runes = "".join(c for c in english_to_runeglish(word.upper()) if c in IDX)
        if not runes:
            continue
        f = word_frequency(word, "en")
        dist[len(runes)] += f
        total += f
    return dist, total


def share(lengths: list[int], n: int) -> float:
    return sum(1 for length in lengths if length == n) / len(lengths)


def main() -> None:
    solved = rune_word_lengths("\n".join(MASTER.read_text().split("\n")[:SOLVED_LINES]))
    unsolved = [len(w) for w in load_words()]
    dist, total = english_lengths()

    s2, u2 = share(solved, 2), share(unsolved, 2)
    e2 = dist[2] / total
    se_solved = sqrt(s2 * (1 - s2) / len(solved))

    print("2-rune word share")
    print(f"  solved LP rune text   {100 * s2:>6.2f}%   n = {len(solved):,}")
    print(f"  English via converter {100 * e2:>6.2f}%   50,000 words, freq-weighted")
    print(f"  unsolved LP           {100 * u2:>6.2f}%   n = {len(unsolved):,}")

    gap = abs(e2 - s2)
    verdict = "AGREE" if gap < 2 * se_solved else "DISAGREE"
    print(
        f"\nconvention calibration: converter vs solved differ by {100 * gap:.2f}"
        f" points, solved SE {100 * se_solved:.2f}  ->  {verdict}"
    )
    if verdict == "DISAGREE":
        print("  the converter does not share the book's convention; comparison void")
        return

    z = (u2 - e2) / sqrt(e2 * (1 - e2) / len(unsolved))
    print(f"unsolved against the calibrated reference: z = {z:+.1f}")

    print(f"\n{'runes':>6}{'unsolved':>10}{'English':>10}{'solved':>9}")
    su = Counter(unsolved)
    ss = Counter(solved)
    for length in range(1, 10):
        print(
            f"{length:>6}{100 * su[length] / len(unsolved):>9.1f}%"
            f"{100 * dist[length] / total:>9.1f}%"
            f"{100 * ss[length] / len(solved):>8.1f}%"
        )
    print("\nThe reference was not the weak link. Whatever explains the deficit,")
    print("it is not the size of the solved sample.")


if __name__ == "__main__":
    main()
