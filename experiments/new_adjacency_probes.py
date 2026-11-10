# ABOUTME: Probes the reading that the 86 doublets are NEW adjacencies made after a strict
# ABOUTME: no-repeat rule: block reversal, inserted nulls, and what each does to lengths.
"""If the cipher never repeats a rune, where do 86 repeats come from?

The body's doublet rate is 0.193 of chance. Every reading so far makes the preventer
imperfect (it fails one time in five) or tunes a relation to that rate. A third reading
makes the preventer perfect and the survivors an after-effect: any step applied AFTER a
strict no-repeat stream that puts two runes side by side which were not side by side
before makes a doublet there at the chance rate 1/29. So

    doublet rate = f / 29,    f = share of adjacent pairs that are new adjacencies

and the body says f = 0.193. Three ways to make new adjacencies, and what each predicts:

  1. Reversal of fixed blocks of b runes (or boustrophedon rows of width b). One pair in
     b is new, so b = 5 fits (89 doublets), and EVERY doublet sits on a block edge: the
     doublet positions fall in one residue class mod b under the right index.
  2. Nulls inserted at a share nu of the final runes. Each null makes two new pairs, so
     nu = f / 2 = 0.096, with no free parameter. Then (a) the blocks are longer than the
     plaintext's words by 1 / (1 - nu); (b) if the nulls sit where a rule puts them, every
     doublet touches a null position; (c) the two runes either side of a null were
     neighbours in the no-repeat stream and so are never equal, which lowers the lag-2
     coincidence rate by the share nu.
  3. Deletion of a share of the stream. Not testable from the body.

Also here, because it uses the same length marginal: the 2-rune hole (row E3) against
the single reading "THE is written joined to the next word".

    python experiments/new_adjacency_probes.py
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import lp_corpus  # noqa: E402
import lp_plaintext_register  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.maths import primes  # noqa: E402
from aldegonde.stats import binomial_z  # noqa: E402

M = 29
SEED = 20261113
BLOCKS = (4, 5, 6, 7)
MULTIPLES = range(3, 16)
TOP = 12  # length classes 1..11 and 12+


def origins(tok) -> dict[str, np.ndarray]:
    """Index of every rune under each counting rule: runes only or runes and separators,
    from the start of the body or of each section, page, line or word."""
    n = len(tok.stream)
    word = np.array(tok.word)
    runes = np.arange(n)
    with_sep = runes + word

    def restart(label, idx):
        out = np.zeros(n, dtype=np.int64)
        start = 0
        for i in range(n):
            if i and label[i] != label[i - 1]:
                start = idx[i]
            out[i] = idx[i] - start
        return out

    out = {"runes, body": runes, "runes+separators, body": with_sep}
    for name, label in (
        ("section", np.array(tok.section)),
        ("page", np.array(tok.page)),
        ("line", np.array(tok.line)),
        ("word", word),
    ):
        out[f"runes, {name}"] = restart(label, runes)
        if name != "word":
            out[f"runes+separators, {name}"] = restart(label, with_sep)
    return out


def block_reversal(doublets, idx_map, n_pairs) -> None:
    print("1. Reversal of fixed blocks: do the doublets sit in one residue class?")
    rate = len(doublets) / n_pairs
    print(
        f"   {len(doublets)} doublets, f = {rate * M:.3f}; a block of b predicts "
        + ", ".join(f"b={b}: {n_pairs / b / M:.0f}" for b in BLOCKS)
    )
    best = (0.0, "", 0, 0)
    for b in BLOCKS:
        for name, idx in idx_map.items():
            counts = np.bincount(idx[doublets] % b, minlength=b)
            share = counts.max() / len(doublets)
            if share > best[0]:
                best = (share, name, b, int(counts.max()))
    print(
        f"   largest share of the doublets in one class, over {len(BLOCKS)} block sizes "
        f"and {len(idx_map)} index rules: {best[0]:.2f} ({best[3]} of {len(doublets)}; "
        f"b = {best[2]}, {best[1]}). The reading needs 1.00."
    )
    print(
        f"   Verdict: {'open' if best[0] > 0.9 else 'excluded for these index rules'}.\n"
    )


def null_rules(doublets, idx_map, n) -> None:
    print("2b. Nulls at ruled positions: does a rule cover every doublet?")
    limit = 2 * n + 10
    sets: dict[str, np.ndarray] = {}
    flag = np.zeros(limit, dtype=bool)
    flag[list(primes(limit))] = True
    sets["prime"] = flag
    sq = np.zeros(limit, dtype=bool)
    sq[np.arange(1, int(limit**0.5)) ** 2] = True
    sets["square"] = sq
    fib = np.zeros(limit, dtype=bool)
    a, b = 1, 2
    while a < limit:
        fib[a] = True
        a, b = b, a + b
    sets["fibonacci"] = fib
    for k in MULTIPLES:
        m = np.zeros(limit, dtype=bool)
        m[::k] = True
        sets[f"multiple of {k}"] = m
    best = (0.0, "", "", 0, 0.0)
    count = 0
    for sname, s in sets.items():
        for iname, idx in idx_map.items():
            for base in (0, 1):
                is_null = s[idx + base]
                touch = is_null[1:] | is_null[:-1]
                covered = float(touch[doublets - 1].mean())
                count += 1
                if covered > best[0] and touch.mean() < 0.5:
                    best = (covered, sname, iname, base, float(touch.mean()))
    print(
        f"   {count} rules (primes, squares, Fibonacci, multiples of 3 to 15; "
        f"{len(idx_map)} index rules; counting from 0 or 1). Best cover among rules "
        f"touching under half the pairs: {best[0]:.2f} of the doublets "
        f"({best[1]}, {best[2]}, from {best[3]}; it touches {best[4]:.2f} of all pairs). "
        f"A true rule covers 1.00."
    )
    print(
        f"   Verdict: {'open' if best[0] > 0.95 else 'no ruled null position among these'}.\n"
    )


def length_fits(rng: random.Random, nu: float) -> None:
    print("2a. Inserted nulls, and THE joined, against the block-length marginal")
    reg = [list(w) for w in lp_plaintext_register.corpus()]
    the = list(c3301.encode_english("THE"))
    body_words = lp_corpus.load_words(join_pages=True)
    body = Counter(min(len(w), TOP) for w in body_words)
    nb = len(body_words)
    body_mean = sum(len(w) for w in body_words) / nb

    def join_the(words):
        out, i = [], 0
        while i < len(words):
            if words[i] == the and i + 1 < len(words):
                out.append(words[i] + words[i + 1])
                i += 2
            else:
                out.append(words[i])
                i += 1
        return out

    def with_nulls(words, share):
        out = []
        for w in words:
            length = 0
            for _ in w:
                while rng.random() < share:
                    length += 1
                length += 1
            out.append(length)
        return out

    def report(label, lengths):
        counts = Counter(min(x, TOP) for x in lengths)
        total = sum(counts.values())
        # two-sample chi-square with the model's size taken as the register's: the
        # model's sampling error is the register's, whatever the number of draws
        size = len(reg)
        chi = 0.0
        for k in range(1, TOP + 1):
            a, b = body[k], counts[k] / total * size
            if a + b == 0:
                continue
            ea, eb = (a + b) * nb / (nb + size), (a + b) * size / (nb + size)
            chi += (a - ea) ** 2 / ea + (b - eb) ** 2 / eb
        print(
            f"   {label:<44}{sum(lengths) / total:>7.3f}{counts[2] / total:>9.3f}{chi:>9.1f}"
        )

    print(f"   {'model':<44}{'mean':>7}{'2-rune':>9}{'chi2':>9}   ({TOP - 1} df)")
    print(f"   {'the body':<44}{body_mean:>7.3f}{body[2] / nb:>9.3f}")
    report("the author's words as written", [len(w) for w in reg])
    draws = 300
    report(
        f"nulls at {nu:.3f} of the final runes (from f)",
        [x for _ in range(draws) for x in with_nulls(reg, nu)],
    )
    report("THE joined to the next word", [len(w) for w in join_the(reg)])
    report(
        f"THE joined, then nulls at {nu:.3f}",
        [x for _ in range(draws) for x in with_nulls(join_the(reg), nu)],
    )
    reg_mean = sum(len(w) for w in reg) / len(reg)
    print(
        f"   nulls at f/2 predict a mean block of {reg_mean / (1 - nu):.3f} against the "
        f"body's {body_mean:.3f}, with no parameter fitted to lengths.\n"
    )


def lag_two(stream: np.ndarray, nu: float) -> None:
    print("2c. Inserted nulls lower the lag-2 coincidence rate by the null share")
    hits = int((stream[:-2] == stream[2:]).sum())
    pairs = len(stream) - 2
    z_chance = binomial_z(hits, pairs, 1 / M)
    z_nulls = binomial_z(hits, pairs, (1 - nu) / M)
    print(
        f"   lag 2: {hits} of {pairs:,}; against chance z {z_chance:+.2f}; against the "
        f"null reading's {(1 - nu) / M * pairs:.0f} z {z_nulls:+.2f}"
    )
    verdict = "disfavoured" if z_nulls > 1.64 else "not separated"
    print(
        f"   Verdict: random nulls after a strict preventer are {verdict} by lag 2.\n"
    )


def main() -> None:
    rng = random.Random(SEED)
    tok = lp_corpus.load_tokenized()
    stream = np.array(tok.stream)
    n = len(stream)
    doublets = np.flatnonzero(stream[1:] == stream[:-1]) + 1
    f = len(doublets) / (n - 1) * M
    nu = f / 2
    print(
        f"body: {n:,} runes, {len(doublets)} doublets, f = {f:.3f} of chance; nulls would "
        f"be nu = f/2 = {nu:.3f} of the runes\n"
    )
    idx_map = origins(tok)
    block_reversal(doublets, idx_map, n - 1)
    length_fits(rng, nu)
    null_rules(doublets, idx_map, n)
    lag_two(stream, nu)


if __name__ == "__main__":
    main()
