# ABOUTME: Extends the plaintext register from eleven pages to sixteen and reports what
# ABOUTME: every quantity calibrated against it does when the extra 919 runes arrive.
"""`corpus()` dropped the five keyed pages for a reason that does not apply to it.

`lp_plaintext_register.corpus()` returned 486 words and 1,963 runes: six pages
transcribed as plaintext plus five monoalphabetic pages, whose key is a 29-rune
substitution and so position-preserving. Its comment said the interrupted Vigenere and
prime running key pages "carry a keystream, not a substitution, and must not be applied
here".

That is right about applying a KEY to a ciphertext and irrelevant to this function,
because `solved_page_triples.json` stores the recovered plaintext directly in
`plaintext_runes`. Every solved page is position-aligned -- an interrupt holds the key
index but still emits a rune -- so the plaintext can be split at the ciphertext's own
separators. Checked for all ten triples.

The register is therefore 723 words and 2,882 runes, a 47% increase, and it now agrees
with `word_lengths()`, which has counted all sixteen pages since it was written.

This prints what moves. Nothing here changes a conclusion; the point is that every
number calibrated against the author's own register was drawn from two thirds of it.

    python register_is_bigger.py
"""

from __future__ import annotations

import collections
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import corpus  # noqa: E402

from aldegonde import c3301  # noqa: E402

ENG = c3301.CICADA_ENGLISH_ALPHABET
M = 29


def within(words, lag: int) -> tuple[int, int]:
    hits = pairs = 0
    for w in words:
        for i in range(len(w) - lag):
            pairs += 1
            hits += w[i] == w[i + lag]
    return hits, pairs


def repeat_pairs(words, minimum: int) -> int:
    c = collections.Counter(tuple(w) for w in words if len(w) >= minimum)
    return sum(k * (k - 1) // 2 for k in c.values())


def phrase_pairs(words) -> int:
    c = collections.Counter(
        (tuple(a), tuple(b)) for a, b in zip(words, words[1:]) if len(a) + len(b) >= 6
    )
    return sum(k * (k - 1) // 2 for k in c.values())


def main() -> None:
    old, new = corpus(keyed=False), corpus(keyed=True)
    print(
        f"{'quantity':<32}{'11 pages':>11}{'16 pages':>11}{'change':>10}"
        f"{'new error':>11}"
    )

    def row(label, a, b, err=None):
        e = f"+- {err:.4f}" if err else ""
        print(f"{label:<32}{a:>11.4f}{b:>11.4f}{b - a:>+10.4f}{e:>11}")

    row("words", len(old), len(new))
    row("runes", sum(len(w) for w in old), sum(len(w) for w in new))
    row(
        "mean word length",
        sum(len(w) for w in old) / len(old),
        sum(len(w) for w in new) / len(new),
    )
    row(
        "fraction at length 2",
        sum(1 for w in old if len(w) == 2) / len(old),
        sum(1 for w in new if len(w) == 2) / len(new),
    )

    def stream_d1(words):
        s = [r for w in words for r in w]
        return sum(1 for i in range(len(s) - 1) if s[i] == s[i + 1]) / (len(s) - 1)

    n_new = sum(len(w) for w in new)
    row(
        "stream doublet rate",
        stream_d1(old),
        stream_d1(new),
        math.sqrt((1 / M) * (1 - 1 / M) / (n_new - 1)),
    )
    for lag in (1, 5):
        a, b = within(old, lag), within(new, lag)
        r = b[0] / b[1]
        row(
            f"within-word d{lag}  ({a[1]}->{b[1]} pairs)",
            a[0] / a[1],
            r,
            math.sqrt(r * (1 - r) / b[1]),
        )

    counts = [collections.Counter(r for w in x for r in w) for x in (old, new)]
    totals = [sum(c.values()) for c in counts]
    iocs = [
        sum(v * (v - 1) for v in c.values()) / (t * (t - 1))
        for c, t in zip(counts, totals)
    ]
    row("unigram IoC", iocs[0], iocs[1])
    for rune in ("F", "E", "O", "A", "TH"):
        i = ENG.index(rune)
        row(f"{rune} rate", counts[0][i] / totals[0], counts[1][i] / totals[1])
    row("repeat pairs of 3+ runes", repeat_pairs(old, 3), repeat_pairs(new, 3))
    row("repeated 6+ rune phrases", phrase_pairs(old), phrase_pairs(new))

    print(
        "\nThe one that matters most is d5. It is measured on the words long enough to"
        "\nhave a lag-5 pair, which the old register barely had: 261 pairs against 382"
        "\nnow. The estimate moves from 0.0575 to 0.0733, and since `g` has order 5 a"
        "\nclean walk would put the body's d5 at the same value. The body reads 0.0492"
        "\n+- 0.0048, which is now 1.7 sigma below the author's plaintext rather than"
        "\n0.5. That is a lead for the clock-perturbing families, not a finding."
    )


if __name__ == "__main__":
    main()
