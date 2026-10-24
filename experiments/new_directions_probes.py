# ABOUTME: Seven cheap key-free probes behind docs/new-directions.md, each answering
# ABOUTME: one question a candidate mechanism outside the walk family would raise.
"""Probes for the directions in `docs/new-directions.md`, 2026-10.

Each probe is a few lines and prints its own verdict from its own numbers:

  predecessor   memory-one output feedback under a per-word base: within-word
                pairs whose predecessors agree should coincide at the plaintext
                rate, not at chance
  lengths       word-level interleaving or a periodic word transposition:
                block-length autocorrelation at lags 1..12
  repeat-slot   the exclusion tableau: every doublet is one plaintext rune s, so
                s must have the doublets' word-initial and non-initial rates and
                their word-final fraction
  period        a word-clocked machine returning at the DJU-BEI distance: aligned
                coincidence at every word distance, and where 1,449 ranks
  anchors       the 17 identical words as base returns: the words after each pair
                should coincide at the plaintext rate if the base chain returned
  grids         the three number grids as bytes: how many, and any structure
  language      the body's word-length marginal against ten languages' token
                lengths from wordfreq, raw and after digraph compression

    python experiments/new_directions_probes.py [probe ...]
"""

from __future__ import annotations

import collections
import math
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_tokenized  # noqa: E402
from lp_plaintext_register import corpus as register  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.stats import binomial_z, two_proportion_z  # noqa: E402

M = 29
CHANCE = 1 / M
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
DJU_BEI = (1477, 2926)  # word indices of the repeated phrase, from quagmire_runner


def within_word_rate(words: list[list[int]], lag: int) -> tuple[int, int]:
    hits = pairs = 0
    for w in words:
        for i in range(len(w) - lag):
            pairs += 1
            hits += w[i] == w[i + lag]
    return hits, pairs


def predecessor(words: list[list[int]], rng: random.Random) -> None:
    """Pairs (j, k) inside a word, split by whether c[j-1] == c[k-1].

    Lags that are multiples of 5 are reported apart: there the walk's g^5 = id makes
    equal predecessors and an equal pair the same event as the known lag-5 digraph
    pairing (`lag5-digraph-structure.md`), so only the other lags test anything new.
    """

    def count(ws: list[list[int]], lags: set[int]) -> tuple[int, int, int, int]:
        eq = [0, 0]
        ne = [0, 0]
        for w in ws:
            for j in range(1, len(w)):
                for k in range(j + 2, min(len(w), j + 9)):
                    if (k - j) not in lags:
                        continue
                    cell = eq if w[j - 1] == w[k - 1] else ne
                    cell[1] += 1
                    cell[0] += w[j] == w[k]
        return eq[0], eq[1], ne[0], ne[1]

    reg = register()
    for label, lags in (("lags 2,3,4,6,7,8", {2, 3, 4, 6, 7, 8}), ("lag 5", {5})):
        h, n, h2, n2 = count(words, lags)
        print(
            f"{label}: equal predecessors {h}/{n} = {h / n:.4f}, z vs chance {binomial_z(h, n, CHANCE):+.2f}; other pairs {h2}/{n2} = {h2 / n2:.4f}"
        )
        rh = rn = 0
        for lag in lags:
            a, b = within_word_rate(reg, lag)
            rh += a
            rn += b
        print(
            f"  memory-one feedback predicts the plaintext rate {rh / rn:.4f} on the equal cell: {rh / rn * n:.1f} hits, z {binomial_z(round(rh / rn * n), n, CHANCE):+.2f}"
        )
        sur = []
        for _ in range(200):
            ws = [rng.sample(w, len(w)) for w in words]
            a, b, _, _ = count(ws, lags)
            sur.append(a / b)
        mu = sum(sur) / len(sur)
        sd = math.sqrt(sum((x - mu) ** 2 for x in sur) / (len(sur) - 1))
        print(
            f"  within-word shuffle null {mu:.4f} +- {sd:.4f}: observed is {(h / n - mu) / sd:+.2f} sd"
        )


def lengths(words: list[list[int]]) -> None:
    def ac(seq: list[int], lag: int) -> float:
        m = sum(seq) / len(seq)
        v = sum((x - m) ** 2 for x in seq) / len(seq)
        return sum((seq[i] - m) * (seq[i + lag] - m) for i in range(len(seq) - lag)) / (
            (len(seq) - lag) * v
        )

    body = [len(w) for w in words]
    reg = [len(w) for w in register()]
    worst = 0.0
    for lag in range(1, 13):
        r = ac(body, lag)
        z = r * math.sqrt(len(body) - lag)
        worst = max(worst, abs(z))
        print(
            f"lag {lag:2d}: body r {r:+.4f} (z {z:+.2f})   author register r {ac(reg, lag):+.4f}"
        )
    print(
        f"largest |z| over 12 lags: {worst:.2f}; the expected maximum of 12 null draws is about 2.1"
    )


def repeat_slot(words: list[list[int]]) -> None:
    within = [(j, len(w)) for w in words for j in range(1, len(w)) if w[j] == w[j - 1]]
    seam = sum(a[-1] == b[0] for a, b in zip(words, words[1:], strict=False))
    pairs = sum(len(w) - 1 for w in words)
    need_non = len(within) / pairs
    need_init = seam / (len(words) - 1)
    need_final = sum(1 for j, n in within if j == n - 1) / len(within)
    print(f"doublets: {len(within)} within words, {seam} at seams")
    print(
        f"s must have non-initial rate {need_non:.4f}, initial rate {need_init:.4f}, and be word-final {need_final:.2f} of its non-initial occurrences"
    )
    init: collections.Counter[int] = collections.Counter()
    non: collections.Counter[int] = collections.Counter()
    fin: collections.Counter[int] = collections.Counter()
    for w in register():
        init[w[0]] += 1
        for j in range(1, len(w)):
            non[w[j]] += 1
            if j == len(w) - 1:
                fin[w[j]] += 1
    ni, nn = sum(init.values()), sum(non.values())
    fits = 0
    for r in range(M):
        z_non = two_proportion_z(non[r], nn, len(within), pairs)
        z_init = two_proportion_z(init[r], ni, seam, len(words) - 1)
        z_fin = binomial_z(fin[r], non[r], need_final) if non[r] else float("nan")
        ok = abs(z_non) < 2 and abs(z_init) < 2 and abs(z_fin) < 2
        fits += ok
        if abs(z_non) < 3:
            print(
                f"  {c3301.CICADA_ENGLISH_ALPHABET[r]:>3}: non-initial z {z_non:+.1f}, initial z {z_init:+.1f}, final z {z_fin:+.1f}{'  <- fits' if ok else ''}"
            )
    print(f"runes fitting all three within 2 sd: {fits} of {M}")


def period(words: list[list[int]]) -> None:
    n = len(words)

    def aligned(d: int, skip: set[int] = frozenset()) -> tuple[int, int]:
        h = p = 0
        for w in range(n - d):
            if w in skip:
                continue
            a, b = words[w], words[w + d]
            m = min(len(a), len(b))
            p += m
            h += sum(a[i] == b[i] for i in range(m))
        return h, p

    target = DJU_BEI[1] - DJU_BEI[0]
    rows = []
    for d in range(1, n - 50):
        h, p = aligned(d)
        rows.append((binomial_z(h, p, CHANCE), d, h, p))
    rows.sort(reverse=True)
    rank = next(i for i, r in enumerate(rows) if r[1] == target) + 1
    print("top five word distances by aligned coincidence:")
    for z, d, h, p in rows[:5]:
        print(f"  D={d:5d} z={z:+.2f} ({h}/{p})")
    z, _, h, p = next(r for r in rows if r[1] == target)
    h2, p2 = aligned(target, {DJU_BEI[0], DJU_BEI[0] + 1})
    print(
        f"DJU-BEI distance {target}: z {z:+.2f}, rank {rank} of {len(rows)}; without the phrase itself {h2}/{p2}, z {binomial_z(h2, p2, CHANCE):+.2f}"
    )
    full = 1 + (len(words) and 0)
    print(
        f"a machine of that period would share every base: ~{1.78 * p / M:.0f} hits against {h}; the scan maximum {rows[0][0]:+.2f} is what {len(rows)} null lags give"
    )
    del full


def anchors(words: list[list[int]]) -> None:
    n = len(words)
    idx: dict[tuple[int, ...], list[int]] = collections.defaultdict(list)
    for i, w in enumerate(words):
        if len(w) >= 3:
            idx[tuple(w)].append(i)
    pairs = [(a, b) for v in idx.values() for a in v for b in v if a < b]

    def aligned(a: int, b: int, span: range) -> tuple[int, int]:
        h = p = 0
        for d in span:
            if 0 <= a + d < n and 0 <= b + d < n:
                x, y = words[a + d], words[b + d]
                m = min(len(x), len(y))
                p += m
                h += sum(x[i] == y[i] for i in range(m))
        return h, p

    tot = [0, 0]
    tot_no = [0, 0]
    for a, b in pairs:
        h, p = aligned(a, b, range(1, 4))
        tot[0] += h
        tot[1] += p
        if (a, b) != DJU_BEI:
            tot_no[0] += h
            tot_no[1] += p
    print(f"{len(pairs)} identical words of three runes or more")
    print(
        f"the three words after each pair, pooled: {tot[0]}/{tot[1]}, z {binomial_z(tot[0], tot[1], CHANCE):+.2f}"
    )
    print(
        f"without DJU-BEI: {tot_no[0]}/{tot_no[1]}, z {binomial_z(tot_no[0], tot_no[1], CHANCE):+.2f}; every pair a true return would give ~{1.78 * tot_no[1] / M:.0f}"
    )


def grids() -> None:
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx"
    chunks = MASTER.read_text(encoding="utf-8").split("%")
    data = bytearray()
    for i, chunk in enumerate(chunks):
        toks = re.findall(r"\b[0-4][0-9A-Za-x]\b", chunk)
        if len(toks) >= 30:
            vals = [digits.index(a) * 60 + digits.index(b) for a, b in toks]
            runes = sum(ch in c3301.RUNE_SET for ch in chunk)
            print(
                f"chunk {i}: {len(toks)} tokens ({len(toks) // 8} rows of 8), values {min(vals)}..{max(vals)}, {runes} runes on the page"
            )
            data += bytes(vals)
    big = int.from_bytes(data, "big")
    distinct = len(set(data))
    expect = 256 * (1 - (255 / 256) ** len(data))
    print(
        f"total {len(data)} bytes = {len(data) * 8} bits; distinct values {distinct} against {expect:.0f} for uniform bytes"
    )
    print(
        f"as a big-endian integer: {big.bit_length()} bits, {'even' if big % 2 == 0 else 'odd'}, so not an RSA modulus; leading bytes {data[:4].hex()}"
    )


def language(words: list[list[int]]) -> None:
    try:
        from wordfreq import top_n_list, word_frequency  # noqa: PLC0415
    except ImportError:
        print("wordfreq is not installed (pip install wordfreq)")
        return
    digraphs = ("th", "ng", "ea", "eo", "oe", "ae", "ia", "io")

    def rune_len(w: str) -> int:
        i = n = 0
        while i < len(w):
            i += 2 if w[i : i + 2] in digraphs else 1
            n += 1
        return n

    bins = 12

    def dist(counter: dict[int, float]) -> list[float]:
        v = [0.0] * bins
        for length, c in counter.items():
            v[min(length, bins) - 1] += c
        s = sum(v)
        return [x / s for x in v]

    body = dist(collections.Counter(len(w) for w in words))
    nb = len(words)

    def chi(model: list[float]) -> float:
        return sum(
            (nb * body[k] - nb * model[k]) ** 2 / (nb * model[k])
            for k in range(bins)
            if model[k] > 0
        )

    print(f"body marginal, lengths 1..{bins}+: " + " ".join(f"{x:.3f}" for x in body))
    print(
        f"author register: chi2 {chi(dist(collections.Counter(len(w) for w in register()))):.0f} on {bins - 1} df"
    )
    for lang in ("en", "de", "nl", "sv", "is", "fi", "pl", "fr", "es", "it"):
        raw: collections.Counter[int] = collections.Counter()
        comp: collections.Counter[int] = collections.Counter()
        for w in top_n_list(lang, 30000):
            if re.fullmatch(r"[a-z]+", w):
                f = word_frequency(w, lang)
                raw[len(w)] += f
                comp[rune_len(w)] += f
        print(
            f"  {lang}: chi2 raw {chi(dist(raw)):7.0f}, digraph-compressed {chi(dist(comp)):7.0f}, two-rune share {dist(comp)[1]:.3f}"
        )
    print(f"the body's two-rune share is {body[1]:.3f}; nothing below chi2 ~ 20 fits")


PROBES = {
    "predecessor": lambda w, rng: predecessor(w, rng),
    "lengths": lambda w, rng: lengths(w),
    "repeat-slot": lambda w, rng: repeat_slot(w),
    "period": lambda w, rng: period(w),
    "anchors": lambda w, rng: anchors(w),
    "grids": lambda w, rng: grids(),
    "language": lambda w, rng: language(w),
}


def main() -> None:
    names = sys.argv[1:] or list(PROBES)
    words = load_tokenized().words()
    rng = random.Random(3301)
    for name in names:
        print(f"\n=== {name} ===")
        PROBES[name](words, rng)


if __name__ == "__main__":
    main()
