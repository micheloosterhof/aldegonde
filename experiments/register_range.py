# ABOUTME: Measures the 2-rune word fraction across twenty-two English registers, to test
# ABOUTME: whether any real register reaches the body's rate or whether it sits below all.
"""If the hole at length 2 is register, some register has to be there.

`block-lengths-have-a-hole-at-two.md` shows the body has 0.159 of its blocks at two
runes against 0.242 of the author's own words, z = -4.33. The standing objection is that
the body is 58 pages of unknown content and the solved pages are front matter, so the
two could simply be different kinds of writing.

That objection is testable. The 2-rune class in runeglish is the top function words --
THE is a single rune plus E -- so its frequency is exactly what varies between registers.
Measure it across every English text in the cache and see how wide the range really is.

The cache spans scripture, verse, philosophy, mysticism and novels: the King James
Bible, Paradise Lost, Beowulf, the Divine Comedy, the Tao Teh King, the Dhammapada, the
Kybalion, Zarathustra, Blake, Emerson, Thoreau, Plato, Marcus Aurelius, the Mabinogion,
Gibran. If the body's rate is inside that range the objection stands. If it is outside,
the register reading needs a kind of English nobody wrote.

One comparison does most of the work on its own, and it is in the output: Beowulf has
the body's mean word length to two decimals and nothing like its 2-rune fraction.

    python register_range.py
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import compact_state_models as csm  # noqa: E402
from fingerprint_battery import lp_words  # noqa: E402
from lp_plaintext_register import word_lengths  # noqa: E402

CAP = 12
MIN_WORDS = 3000


def title_of(path: Path) -> str:
    head = path.read_text(errors="replace")[:4000].split("\n")
    for line in head:
        if line.lower().startswith("title:"):
            return line.split(":", 1)[1].strip()[:26]
    return path.stem


def lengths_of(path: Path) -> list[int]:
    """Runeglish word lengths, with the Gutenberg boilerplate trimmed off."""
    words = []
    for word in csm.prose_words(path):
        runes = csm.to_runeglish(word)
        if runes:
            words.append(len(runes))
    trim = len(words) // 10
    return words[trim : len(words) - trim]


def histogram(lengths) -> tuple[np.ndarray, int]:
    c = collections.Counter(min(x, CAP) for x in lengths)
    return np.array([c[k] for k in range(1, CAP + 1)], float), sum(c.values())


def main() -> None:
    body_h, n_body = histogram(len(w) for w in lp_words())
    body_f2 = body_h[1] / n_body
    body_mean = float(sum((i + 1) * body_h[i] for i in range(CAP)) / n_body)
    solved = word_lengths()
    solved_f2 = sum(1 for x in solved if x == 2) / len(solved)

    rows = []
    for path in sorted(csm.BOOK_CACHE.glob("pg*.txt")):
        lens = lengths_of(path)
        if len(lens) < MIN_WORDS:
            continue
        h, n = histogram(lens)
        # chi2 of the body against this register's shape, all twelve cells
        e = h / n * n_body
        chi = float((((body_h - e) ** 2) / np.maximum(e, 1e-9)).sum())
        resid2 = (body_h[1] - e[1]) / np.sqrt(max(e[1], 1e-9))
        rows.append((
            h[1] / n,
            title_of(path),
            n,
            float(sum((i + 1) * h[i] for i in range(CAP)) / n),
            chi,
            resid2,
        ))

    print(f"body: {n_body:,} blocks, fraction at length 2 = {body_f2:.4f}, "
          f"mean {body_mean:.2f}")
    print(f"the author's own solved pages: {len(solved)} words, "
          f"fraction {solved_f2:.4f}\n")
    print(f"{'register':>28}{'words':>9}{'frac 2':>9}{'mean':>7}"
          f"{'chi2 vs body':>14}{'resid at 2':>12}")
    for f2, title, n, mean, chi, r2 in sorted(rows):
        print(f"{title:>28}{n:>9,}{f2:>9.4f}{mean:>7.2f}{chi:>14.1f}{r2:>12.1f}")

    f = np.array([r[0] for r in rows])
    print(f"\n{len(rows)} registers: min {f.min():.4f}, max {f.max():.4f}, "
          f"median {np.median(f):.4f}")
    print(f"  the author's solved pages sit at {solved_f2:.4f}, "
          f"the {int((f < solved_f2).mean() * 100)}th percentile of that range")
    print(f"  registers at or below the body's {body_f2:.4f}: "
          f"{int((f <= body_f2).sum())}")

    best = min(rows, key=lambda r: r[4])
    print(f"\nbest-fitting register overall: {best[1]}, chi2 {best[4]:.1f} on 11 df, "
          f"residual at length 2 {best[5]:+.1f}")

    match = min(rows, key=lambda r: abs(r[3] - body_mean))
    print(
        f"\nAnd the register whose MEAN matches the body's: {match[1]}, mean "
        f"{match[3]:.2f} against {body_mean:.2f},\nyet its 2-rune fraction is "
        f"{match[0]:.4f} against {body_f2:.4f}. Matching the mean does not"
        f"\nmatch the shape, so the body's lengths are not simply a wordier register."
    )


if __name__ == "__main__":
    main()
