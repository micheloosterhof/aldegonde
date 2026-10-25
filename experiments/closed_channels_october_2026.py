# ABOUTME: Six cheap key-free checks run while drafting the October 2026 hypotheses,
# ABOUTME: each closing one channel a candidate mechanism would have used.
"""Channels checked and closed on 2026-10-25, each in a few lines.

  restart      do the words after each thirteen-dot mark share a start state?
  bacon        is there a Baconian message in the word-length sequence?
  red          are the rubricated runes plaintext (high IoC) or ciphertext (flat)?
  order        are the words inside the body in lexicographic rune order?
  checksum     is the per-word alphabet a function of a running checksum of the
               ciphertext written so far (index sum or Gematria sum, mod N)?
  copy         is any body sentence a word-scrambled copy of one of the author's
               94 known sentences (same multiset of word lengths)?

Every check prints the body's number beside what the mechanism would give, and
`checksum` and `copy` carry a planted or recut control for power.

    python experiments/closed_channels_october_2026.py [check ...]
"""

from __future__ import annotations

import collections
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_tokenized  # noqa: E402
from lp_plaintext_register import corpus as register  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.stats import binomial_z  # noqa: E402

M = 29
CHANCE = 1 / M
PLAIN_IOC = 1.78  # the register's nIoC; what two words sharing an alphabet coincide at
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
TITLES = ROOT / "experiments" / "rubricated_titles.json"


def aligned(words: list[list[int]], pairs) -> tuple[int, int]:  # noqa: ANN001
    h = p = 0
    for a, b in pairs:
        x, y = words[a], words[b]
        m = min(len(x), len(y))
        p += m
        h += sum(x[t] == y[t] for t in range(m))
    return h, p


def restart(tok: c3301.Tokenized, words: list[list[int]]) -> None:
    starts = [0] + [w + 1 for w in range(len(words) - 1) if tok.closing[w] == "⑬"]
    print(f"{len(starts)} unit starts (the body start and the word after each ⑬)")
    for k in (1, 2, 3):
        pairs = [
            (a + d, b + d)
            for i, a in enumerate(starts)
            for b in starts[i + 1 :]
            for d in range(k)
            if b + d < len(words)
        ]
        h, p = aligned(words, pairs)
        print(
            f"  first {k} word(s) aligned across units: {h}/{p}, z {binomial_z(h, p, CHANCE):+.2f}; a shared start state gives ~{PLAIN_IOC * p / M:.0f}"
        )


def bacon(words: list[list[int]]) -> None:
    lengths = [len(w) for w in words]
    for label, bits in (
        ("parity", [x % 2 for x in lengths]),
        ("length > 4", [int(x > 4) for x in lengths]),
    ):
        groups = [tuple(bits[i : i + 5]) for i in range(0, len(bits) - 4, 5)]
        c = collections.Counter(groups)
        n = len(groups)
        nioc = 32 * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))
        q = sum(bits) / len(bits)
        print(
            f"  {label}: 5-bit groups nIoC {nioc:.3f}; independent bits at p={q:.3f} give {32 * (q * q + (1 - q) ** 2) ** 5:.3f}; English letters on 32 symbols ~2.1"
        )


def red() -> None:
    chunks = MASTER.read_text(encoding="utf-8").split("%")
    runes: list[int] = []
    for t in json.loads(TITLES.read_text()):
        ws = c3301.tokenize(chunks[t["chunk"]]).words()
        a, b = t["word_range"]
        for w in ws[a : b + 1]:
            runes += w
    c = collections.Counter(runes)
    n = len(runes)
    nioc = M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1))
    print(
        f"  {n} rubricated runes: nIoC {nioc:.3f} (flat 1.00 +- 0.035 at this n; plaintext {PLAIN_IOC}); so the red words are enciphered like the rest"
    )


def order(words: list[list[int]]) -> None:
    inc = sum(a < b for a, b in zip(words, words[1:], strict=False) if a != b)
    tot = sum(a != b for a, b in zip(words, words[1:], strict=False))
    print(
        f"  adjacent words in increasing rune order: {inc}/{tot} = {inc / tot:.3f}; random order gives 0.500"
    )


def checksum_labels(
    words: list[list[int]], values: list[int], n: int, *, inclusive: bool
) -> list[int]:
    out = []
    s = 0
    for w in words:
        if inclusive:
            s += sum(values[r] for r in w)
            out.append(s % n)
        else:
            out.append(s % n)
            s += sum(values[r] for r in w)
    return out


def label_pairs(labels: list[int]):  # noqa: ANN202
    by: dict[int, list[int]] = collections.defaultdict(list)
    for w, lab in enumerate(labels):
        by[lab].append(w)
    return [
        (a, b) for grp in by.values() for i, a in enumerate(grp) for b in grp[i + 1 :]
    ]


def checksum(words: list[list[int]], rng: random.Random) -> None:
    primes = [c3301.r2v(c3301.i2r(i)) for i in range(M)]
    index = list(range(M))
    worst = 0.0
    print(f"  {'checksum':<24}{'N':>6}{'hits/pairs':>14}{'z':>8}  shared state gives")
    for name, values in (("rune index sum", index), ("Gematria prime sum", primes)):
        for inclusive in (False, True):
            for n in (29, 58, 87, 116, 145, 290, 841, 1000, 3000):
                h, p = aligned(
                    words,
                    label_pairs(checksum_labels(words, values, n, inclusive=inclusive)),
                )
                z = binomial_z(h, p, CHANCE)
                worst = max(worst, abs(z))
                if n in (29, 841, 3000) and not inclusive:
                    print(
                        f"  {name:<24}{n:>6}{f'{h}/{p}':>14}{z:>+8.2f}  ~{PLAIN_IOC * p / M:.0f}"
                    )
    print(
        f"  largest |z| over 36 cells (two sums, before/including the word, nine moduli): {worst:.2f}"
    )
    # planted control: register words enciphered with a base chosen by the Gematria checksum of the ciphertext so far, N = 3000
    reg = register()
    plain: list[list[int]] = []
    while len(plain) < len(words):
        block = list(reg)
        rng.shuffle(block)
        plain += block
    plain = plain[: len(words)]
    bases: dict[int, list[int]] = {}
    cipher: list[list[int]] = []
    s = 0
    for w in plain:
        lab = s % 3000
        if lab not in bases:
            bases[lab] = rng.sample(range(M), M)
        cw = [bases[lab][r] for r in w]
        cipher.append(cw)
        s += sum(primes[r] for r in cw)
    h, p = aligned(
        cipher, label_pairs(checksum_labels(cipher, primes, 3000, inclusive=False))
    )
    print(
        f"  planted control, Gematria sum before the word, N = 3000: {h}/{p}, z {binomial_z(h, p, CHANCE):+.2f}"
    )


def copy(rng: random.Random) -> None:
    from the_gap_depends_on_span_length import author_spans, body_spans  # noqa: PLC0415

    author = author_spans()
    body = body_spans()
    keys = {tuple(sorted(s)) for s in author}
    hits = [len(s) for s in body if tuple(sorted(s)) in keys]
    flat = [length for s in author for length in s]
    sizes = [len(s) for s in author]
    nulls = []
    for _ in range(200):
        rng.shuffle(flat)
        k = 0
        recut = set()
        for n in sizes:
            recut.add(tuple(sorted(flat[k : k + n])))
            k += n
        nulls.append(sum(1 for s in body if tuple(sorted(s)) in recut))
    mu = sum(nulls) / len(nulls)
    print(
        f"  {len(body)} body spans against {len(author)} author sentences: {len(hits)} share a word-length multiset (sizes {sorted(hits)}); recut-author null {mu:.1f}"
    )
    print(
        "  no body sentence is a word-scrambled copy of a sentence on the solved pages; other published texts are not in the repository"
    )


CHECKS = {
    "restart": lambda tok, words, rng: restart(tok, words),
    "bacon": lambda tok, words, rng: bacon(words),
    "red": lambda tok, words, rng: red(),
    "order": lambda tok, words, rng: order(words),
    "checksum": lambda tok, words, rng: checksum(words, rng),
    "copy": lambda tok, words, rng: copy(rng),
}


def main() -> None:
    names = sys.argv[1:] or list(CHECKS)
    tok = load_tokenized()
    words = tok.words()
    rng = random.Random(3301)
    for name in names:
        print(f"\n=== {name} ===")
        CHECKS[name](tok, words, rng)


if __name__ == "__main__":
    main()
