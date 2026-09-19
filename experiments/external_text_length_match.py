# ABOUTME: Slides public-domain texts against the unsolved corpus by word-length
# ABOUTME: sequence, to find a quoted passage without any key or cipher model.
"""Searches known books for a passage whose word lengths match the unsolved text.

Word lengths survive encipherment, so a quoted passage shows as a run of matching
word lengths whatever the cipher is. `crib_phrase_search.py` does this for phrases
3301 has already published; this does it for whole books 3301 is known to have
drawn on, and for books a text addressed to "pilgrims" might quote. A hit of a few
dozen words would be a contiguous known-plaintext crib, which identifies the cipher
under any model.

Each book is carried into runeglish (word lengths counted in runes) and slid along
the 2,928 unsolved words. For every alignment the matches in a 30-word window are
counted. Two unrelated texts agree on a word's length about one time in six, so a
window scores ~5 of 30; 22 of 30 is reached by chance about once per 1e11
alignments. The tolerance for 8 mismatches absorbs transliteration choices
(ING as one rune or two, IO, EA) and the corpus's merged short words.

**Result (2026-09-19): negative.** Across 22 books and 2.4 million words no window
reaches 20 of 30; the best are the chance tail (Walden: 5 windows at 18, none
higher). The unsolved text does not quote 30 or more consecutive words from Emerson's
Essays, Blake, the Mabinogion, the King James Bible, the Tao Te Ching, Nietzsche,
Walden, the Kybalion, Marcus Aurelius, the Dhammapada, The Prophet, The Pilgrim's
Progress, Paradise Lost, Dante, Beowulf, Augustine or the Republic. Liber AL and
Jung's Seven Sermons are not on Project Gutenberg and were not scanned.

Run with no arguments for the self-test (a planted passage with one length in six
altered must be found). `--run` fetches the books and scans them.
"""

from __future__ import annotations

import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from runeglish_frequency import english_to_runeglish  # noqa: E402

WINDOW = 30
REPORT_FROM = 20  # matches in a window worth printing
SIGNIFICANT = 22
CACHE = Path(tempfile.gettempdir()) / "lp_external_texts"
BOOKS = {  # Project Gutenberg ebook numbers
    16643: "Emerson, Essays First Series (Self-Reliance, Circles)",
    2945: "Emerson, Essays Second Series",
    45315: "Blake, The Marriage of Heaven and Hell",
    1934: "Blake, Songs of Innocence and of Experience",
    5160: "The Mabinogion",
    10: "King James Bible",
    216: "Tao Te Ching",
    1998: "Nietzsche, Thus Spake Zarathustra",
    4363: "Nietzsche, Beyond Good and Evil",
    205: "Thoreau, Walden",
    14209: "The Kybalion",
    2680: "Marcus Aurelius, Meditations",
    2017: "The Dhammapada",
    58585: "Gibran, The Prophet",
    131: "Bunyan, The Pilgrim's Progress",
    20: "Milton, Paradise Lost",
    8800: "Dante, The Divine Comedy",
    16328: "Beowulf",
    3296: "Augustine, Confessions",
    1497: "Plato, The Republic",
    3301: "ebook number 3301",
    1033: "ebook number 1033",
}


def lp_lengths() -> np.ndarray:
    _stream, wid = load_clean()
    return np.bincount(wid).astype(np.int8)


def text_lengths(text: str) -> tuple[np.ndarray, list[str]]:
    """Runeglish length of every word, and the words themselves."""
    words = re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?", text)
    kept, lengths = [], []
    for word in words:
        n = len(english_to_runeglish(word.replace("'", "")))
        if n:
            kept.append(word)
            lengths.append(n)
    return np.array(lengths, dtype=np.int8), kept


def window_matches(lp: np.ndarray, book: np.ndarray):
    """Yield (matches, lp_start, book_start) for every window at or above REPORT_FROM.

    Row i holds whether LP word i matches each book word; the running sum along a
    diagonal over the last WINDOW rows is the match count of one aligned window.
    """
    n = len(book)
    rows = np.zeros((WINDOW, n), dtype=np.int8)
    diagonal = np.zeros(n, dtype=np.int8)
    for i, length in enumerate(lp):
        row = (book == length).astype(np.int8)
        shifted = np.zeros(n, dtype=np.int8)
        shifted[1:] = diagonal[:-1]
        leaving = np.zeros(n, dtype=np.int8)
        if i >= WINDOW:
            leaving[WINDOW:] = rows[i % WINDOW][: n - WINDOW]
        diagonal = shifted + row - leaving
        rows[i % WINDOW] = row
        if i >= WINDOW - 1:
            for j in np.nonzero(diagonal >= REPORT_FROM)[0]:
                if j >= WINDOW - 1:
                    yield int(diagonal[j]), i - WINDOW + 1, int(j) - WINDOW + 1


def best_hits(lp: np.ndarray, book: np.ndarray, keep: int = 5):
    """Strongest windows, one per neighbourhood."""
    hits = sorted(window_matches(lp, book), reverse=True)
    chosen: list[tuple[int, int, int]] = []
    for hit in hits:
        if all(
            abs(hit[1] - c[1]) > WINDOW or abs(hit[2] - c[2]) > WINDOW for c in chosen
        ):
            chosen.append(hit)
        if len(chosen) == keep:
            break
    return chosen


def self_test() -> None:
    rng = random.Random(3301)
    lp = lp_lengths()
    book = np.array(rng.choices(list(lp), k=50000), dtype=np.int8)
    passage = lp[1200:1260].copy()
    for k in range(0, 60, 6):
        passage[k] += 1
    book[31000:31060] = passage
    top = best_hits(lp, book, keep=1)[0]
    print(
        f"planted passage: best window {top[0]}/{WINDOW} at LP word {top[1]}, book word {top[2]}"
    )
    assert top[0] >= SIGNIFICANT, "planted passage not found"
    assert abs((top[2] - top[1]) - (31000 - 1200)) == 0, "found at the wrong alignment"
    print("self-test passed")


def fetch(number: int) -> str | None:
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f"pg{number}.txt"
    if not path.exists():
        url = f"https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt"
        subprocess.run(
            ["curl", "-sL", "--max-time", "120", "-o", str(path), url], check=False
        )  # noqa: S603, S607
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    return text if len(text) > 5000 and "<html" not in text[:500].lower() else None


def run() -> None:
    lp = lp_lengths()
    print(
        f"{len(lp)} unsolved words; window {WINDOW}, chance ~5, significant from {SIGNIFICANT}\n"
    )
    for number, title in BOOKS.items():
        text = fetch(number)
        if text is None:
            print(f"{title}: not fetched")
            continue
        book, words = text_lengths(text)
        hits = best_hits(lp, book)
        best = f"{hits[0][0]}/{WINDOW}" if hits else f"below {REPORT_FROM}/{WINDOW}"
        flag = "  <== SIGNIFICANT" if hits and hits[0][0] >= SIGNIFICANT else ""
        print(f"{title}: {len(book):,} words, best window {best}{flag}", flush=True)
        for matches, lp_start, book_start in hits:
            if matches >= SIGNIFICANT:
                print(
                    f"    {matches}/{WINDOW} at LP word {lp_start}: {' '.join(words[book_start : book_start + WINDOW])}"
                )


if __name__ == "__main__":
    if "--run" in sys.argv:
        run()
    else:
        self_test()
