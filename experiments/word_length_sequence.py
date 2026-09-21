# ABOUTME: Measures transition structure in the word-length sequence, which no substitution
# ABOUTME: can touch, and finds the body carries a tenth of what the author's plaintext does.
"""Word lengths are not enciphered. So they can be read directly, and they do not fit.

Every cipher this project still entertains is position-preserving: the ciphertext has the
same runes in the same places, so the sequence of word lengths passes through untouched.
Whatever the body's plaintext is, its word-length sequence is visible in the clear.

English word lengths are strongly serially dependent -- short function words alternate
with long content words -- so that sequence should carry structure. The statistic is the
G^2 of the length-transition table, bucketed at 6+, against a surrogate that shuffles the
same lengths. Reported per pair so corpora of different sizes can be compared.

    prose, six Gutenberg books carried into runeglish     0.0484 +- 0.0159
    the LP's own solved plaintext, 723 words              0.0387 +- 0.0105
    the unsolved body, 2,928 words                        0.0037 +- 0.0023

The two references agree with each other and the body is an order of magnitude below
both, on six times the plaintext's data.

The obvious mechanism is tested and fails. Merging adjacent words -- what
`separator-loss-is-selective.md` proposes -- removes only about a third of the structure
at the merge rate that matches the body's mean word length, and moves the 2-rune share
from 0.228 to 0.209 where the body sits at 0.159.

The merge family is then swept properly. Merging only SHORT words is the version that
could work, because it removes exactly the short-long alternation that creates the
structure. It reproduces the body's length histogram at q = 0.3 and its length sequence
only at q = 0.9, and those are different corpora.

Segmentation is the obvious alternative explanation, so it is swept rather than assumed:
sixteen tokenization conventions, crossing line wraps, multi-dot marks, page marks and
quotes. Every one gives essentially zero.

`--perturb` sweeps the other length-perturbation families -- nulls inserted at a rate,
and a fixed pad per word -- for the same reason the merge family was swept. They fail the
same way: whatever matches the histogram leaves five times too much order.

`--jackknife` checks the reference, which is the load-bearing half of the comparison.
`--types` tests the list reading in its natural form: a list of distinct vocabulary items
is TYPE-weighted, not token-weighted, and looks nothing like the body. `--sort` tests the
most natural compact permutation, which turns out to CREATE order rather than destroy it.
`--floor` asks how low real English can go at the body's size, over sixty matched windows,
and `--intrapage` asks whether the anomaly survives dropping every cross-page transition.

    python word_length_sequence.py [--merge] [--shape] [--tokenize] [--perturb]
                                   [--jackknife] [--types] [--sort] [--floor] [--intrapage]
"""

from __future__ import annotations

import collections
import math
import random
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import MASTER, PLAIN_PAGES, words_of  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
CACHE = Path(tempfile.gettempdir()) / "lp_external_texts"
CAP = 6


def g2(seqs: list[list[int]]) -> tuple[float, int]:
    """G^2 of the length-transition table, and the pair count. Sequences are kept
    separate so no transition is counted across a page or section boundary."""
    pairs = [(min(a, CAP), min(b, CAP)) for s in seqs for a, b in zip(s, s[1:])]
    tab = collections.Counter(pairs)
    ra = collections.Counter(a for a, _ in pairs)
    rb = collections.Counter(b for _, b in pairs)
    n = len(pairs)
    out = 0.0
    for (a, b), o in tab.items():
        e = ra[a] * rb[b] / n
        if o and e:
            out += 2 * o * math.log(o / e)
    return out, n


def excess_per_pair(
    seqs: list[list[int]], rng: random.Random, draws: int = 200, within: bool = False
):
    """(excess G^2 per pair, its standard error) against a length-shuffling surrogate.

    The default surrogate pools the lengths and redeals them into the same sequence
    shapes, which does NOT preserve each sequence's own marginal -- so heterogeneity
    between pages could masquerade as transition structure. `within` shuffles inside
    each sequence instead, which preserves it. The two agree here (0.0395 against
    0.0382 for the plaintext reference, 0.0037 either way for the body), so the
    default is kept for its larger surrogate sample.
    """
    obs, n = g2(seqs)
    flat = [x for s in seqs for x in s]
    sur = []
    for _ in range(draws):
        if within:
            resh = []
            for s in seqs:
                t = s[:]
                rng.shuffle(t)
                resh.append(t)
            sur.append(g2(resh)[0])
            continue
        t = flat[:]
        rng.shuffle(t)
        it = iter(t)
        sur.append(g2([[next(it) for _ in s] for s in seqs])[0])
    mu = sum(sur) / len(sur)
    sd = (sum((x - mu) ** 2 for x in sur) / len(sur)) ** 0.5
    return (obs - mu) / n, sd / n, obs, mu, n


def body_sequences() -> list[list[int]]:
    text = (ROOT / "data" / "page0-56.txt").read_text()
    out = []
    for s in [x for x in text.split("$") if RUNE.search(x)][:10]:
        seq, cur = [], 0
        for ch in s:
            if RUNE.match(ch):
                cur += 1
            elif ch in "/\n":
                continue
            elif cur and ch in c3301.WORD_BOUNDARY:
                seq.append(cur)
                cur = 0
        if cur:
            seq.append(cur)
        out.append(seq)
    return out


def plaintext_sequences() -> list[list[int]]:
    """One sequence per solved page. Vigenere pages are position-preserving, so their
    ciphertext word lengths are the plaintext's."""
    import json  # noqa: PLC0415

    pages = MASTER.read_text().split("%")
    seqs = [[len(w) for w in words_of(pages[n])] for n in PLAIN_PAGES]
    for t in json.loads((ROOT / "experiments" / "solved_page_triples.json").read_text()):
        key = t["key"] if t["cipher"] == "monoalphabetic" else None
        seqs.append([len(w) for w in words_of(pages[t["page"]], key)])
    return seqs


def prose_sequences(limit: int = 20000) -> list[tuple[str, list[int]]]:
    from runeglish_frequency import english_to_runeglish  # noqa: PLC0415

    out = []
    for b in sorted(CACHE.glob("pg*.txt"))[:6]:
        text = b.read_text(encoding="utf-8", errors="ignore")
        words = re.findall(r"[A-Za-z']+", text.upper())[:limit]
        lens = [len(english_to_runeglish(w.replace("'", ""))) for w in words]
        out.append((b.name, [x for x in lens if x]))
    return out


MULTI = {chr(0x2460 + i) for i in range(1, 20)}  # circled 2..20, the multi-dot marks


def tokenize(wrap: bool, multi: bool, pct: bool, quote: bool) -> list[list[int]]:
    """Body word lengths under one convention for which marks break a word."""
    text = (ROOT / "data" / "page0-56.txt").read_text()
    out = []
    for s in [x for x in text.split("$") if RUNE.search(x)][:10]:
        seq, cur = [], 0
        for ch in s:
            if RUNE.match(ch):
                cur += 1
                continue
            if ch in "/\n":
                brk = wrap
            elif ch in MULTI:
                brk = multi
            elif ch == "%":
                brk = pct
            elif ch == '"':
                brk = quote
            else:
                brk = ch in c3301.WORD_BOUNDARY
            if brk and cur:
                seq.append(cur)
                cur = 0
        if cur:
            seq.append(cur)
        out.append(seq)
    return out


def tokenize_sweep(rng: random.Random) -> None:
    """Is the missing structure a segmentation artifact? No, under any convention."""
    import itertools  # noqa: PLC0415

    print(f"{'wrap':>6}{'multi':>7}{'%':>5}{chr(34):>5}{'words':>8}{'mean':>7}"
          f"{'2-rune':>9}{'excess/pair':>15}")
    best = None
    for w, m, p, q in itertools.product([False, True], repeat=4):
        seqs = tokenize(w, m, p, q)
        flat = [x for s in seqs for x in s]
        e, se, _o, _mu, _n = excess_per_pair(seqs, rng, draws=60)
        if best is None or e > best[0]:
            best = (e, se, w, m, p, q)
        print(
            f"{str(w):>6}{str(m):>7}{str(p):>5}{str(q):>5}{len(flat):>8,}"
            f"{sum(flat) / len(flat):>7.2f}"
            f"{sum(1 for x in flat if x == 2) / len(flat):>9.3f}{e:>10.4f}+-{se:.4f}"
        )
    print(
        f"\nbest of sixteen: {best[0]:.4f} +- {best[1]:.4f}, against a language"
        "\nreference of 0.0397 +- 0.0101 (the LP's own plaintext) and 0.0484 +- 0.0160"
        "\n(prose). The repo's own convention is the best of the sixteen and is still an"
        "\norder of magnitude short. Breaking at line wraps brings the MEAN closest to"
        "\nlanguage, 4.07 against 3.99, and drives the order further to zero -- and that"
        "\nconvention is known to be wrong from the solved pages, where words demonstrably"
        "\nflow across wraps."
    )


def floor_probe(rng: random.Random) -> None:
    """The register objection, measured instead of asserted."""
    import statistics  # noqa: PLC0415

    print("excess/pair over 2,900-word windows, the body's own size")
    print(f"{'book':<14}{'windows':>9}{'min':>9}{'median':>9}{'max':>9}")
    lowest = []
    for name, lens in prose_sequences(30000):
        vals = [
            excess_per_pair([lens[i : i + 2900]], rng, draws=20)[0]
            for i in range(0, len(lens) - 2900, 2900)
        ]
        if not vals:
            continue
        lowest.append(min(vals))
        print(f"{name:<14}{len(vals):>9}{min(vals):>9.4f}"
              f"{statistics.median(vals):>9.4f}{max(vals):>9.4f}")
    print(f"\nlowest of all windows: {min(lowest):.4f}")
    print("body, matched size: 0.0037 +- 0.0022 -- six times below the floor.")


def intrapage(rng: random.Random) -> None:
    """Is the anomaly between pages or inside them?"""
    import re  # noqa: PLC0415

    from aldegonde import c3301  # noqa: PLC0415

    master = (ROOT / "data" / "liber-primus__transcription--master.txt").read_text().split("%")
    pages = []
    for n in range(15, 71):
        if n >= len(master) or not RUNE.search(master[n]):
            continue
        seq, cur = [], 0
        for c in master[n]:
            if RUNE.match(c):
                cur += 1
            elif c in "/\n":
                continue
            elif cur and c in c3301.WORD_BOUNDARY:
                seq.append(cur)
                cur = 0
        if cur:
            seq.append(cur)
        if len(seq) >= 10:
            pages.append(seq)
    e, se, _o, _m, n = excess_per_pair(pages, rng, draws=300)
    flat = [[x for s in pages for x in s]]
    e2, se2, _o, _m, n2 = excess_per_pair(flat, rng, draws=200)
    print(f"within a page only : {e:+.4f} +- {se:.4f} on {n:,} pairs, {len(pages)} pages")
    print(f"all transitions    : {e2:+.4f} +- {se2:.4f} on {n2:,} pairs")
    print(
        "\nDropping every cross-page transition does not recover the order, so the"
        "\nblocks are scrambled INSIDE pages and no page-level reordering explains it."
    )


def sort_control(rng: random.Random) -> None:
    """Sorting is the obvious compact permutation. It is the wrong shape entirely."""
    from runeglish_frequency import english_to_runeglish  # noqa: PLC0415

    text = (CACHE / "pg1033.txt").read_text(encoding="utf-8", errors="ignore")
    tokens = re.findall(r"[A-Za-z]+", text.upper())[:40000]

    def lengths(ws: list[str]) -> list[int]:
        out = [len(english_to_runeglish(w)) for w in ws]
        return [x for x in out if x]

    print(f"{'word order':<28}{'mean':>7}{'2-rune':>9}{'excess/pair':>14}")
    for label, ws in (
        ("original order", tokens),
        ("sorted alphabetically", sorted(tokens)),
        ("sorted by reversed word", sorted(tokens, key=lambda w: w[::-1])),
        ("shuffled", rng.sample(tokens, len(tokens))),
    ):
        ls = lengths(ws)
        e, se, _o, _m, _n = excess_per_pair([ls], rng, draws=25)
        print(f"{label:<28}{sum(ls) / len(ls):>7.2f}"
              f"{sum(1 for x in ls if x == 2) / len(ls):>9.3f}{e:>10.4f}+-{se:.4f}")
    body = [x for s in body_sequences() for x in s]
    print(f"{'body':<28}{sum(body) / len(body):>7.2f}"
          f"{sum(1 for x in body if x == 2) / len(body):>9.3f}{0.0039:>10.4f}+-0.0025")
    print(
        "\nSorting does not destroy order, it creates it: repeated words cluster into"
        "\nruns of equal length, and the excess jumps eighty-fold. The body matches the"
        "\nSHUFFLED row instead, which is the statement to carry forward -- whatever"
        "\nordered these blocks behaves like a random permutation."
    )


def type_control() -> None:
    """A list of distinct words is type-weighted. The body is not."""
    from runeglish_frequency import english_to_runeglish  # noqa: PLC0415

    text = "".join(
        (CACHE / f"pg{n}.txt").read_text(encoding="utf-8", errors="ignore")
        for n in ("1033", "131", "10")
    )
    tokens = re.findall(r"[A-Za-z]+", text.upper())
    token_lengths = [len(english_to_runeglish(w)) for w in tokens]
    type_lengths = [len(english_to_runeglish(w)) for w in sorted(set(tokens))]
    body = [x for s in body_sequences() for x in s]
    plain = [x for s in plaintext_sequences() for x in s]

    def hist(ls: list[int], cap: int = 12) -> tuple[list[float], int]:
        c = collections.Counter(min(x, cap) for x in ls if x > 0)
        n = sum(c.values())
        return [c[k] / n for k in range(1, cap + 1)], n

    hb, nb = hist(body)
    ht, _ = hist(token_lengths)
    hy, _ = hist(type_lengths)
    hp, _ = hist(plain)
    print(f"{'len':>4}{'body':>9}{'prose tokens':>14}{'prose TYPES':>13}{'LP plaintext':>14}")
    for k in range(12):
        print(f"{k + 1:>4}{hb[k]:>9.3f}{ht[k]:>14.3f}{hy[k]:>13.3f}{hp[k]:>14.3f}")
    print(f"\nmeans: body {sum(body) / len(body):.2f}  "
          f"tokens {sum(token_lengths) / len(token_lengths):.2f}  "
          f"types {sum(type_lengths) / len(type_lengths):.2f}  "
          f"LP plaintext {sum(plain) / len(plain):.2f}")

    def fit(h: list[float], n: int, m: list[float]) -> float:
        return sum(2 * n * o * math.log(o / e) for o, e in zip(h, m) if o > 0 < e) / n

    print("\nG2 per word, the body against:")
    print(f"  prose tokens  {fit(hb, nb, ht):.4f}")
    print(f"  prose TYPES   {fit(hb, nb, hy):.4f}")
    print(f"  LP plaintext  {fit(hb, nb, hp):.4f}")
    print(
        "\nA list of distinct words has mean 6.77 and a 0.5% two-rune share against the"
        "\nbody's 4.42 and 15.9%. The body's lengths are token-weighted: they look like"
        "\nrunning text, and carry none of running text's order."
    )


def perturb_control(rng: random.Random) -> None:
    """Nulls and padding, the other ways to lengthen words without reordering them."""
    prose = prose_sequences(40000)[1][1]
    body = [x for s in body_sequences() for x in s]

    def hist(ls: list[int], cap: int = 12) -> tuple[list[float], int]:
        c = collections.Counter(min(x, cap) for x in ls)
        return [c[k] / len(ls) for k in range(1, cap + 1)], len(ls)

    hb, _nb = hist(body)

    def fit(h: list[float], n: int, m: list[float]) -> float:
        return sum(2 * n * o * math.log(o / e) for o, e in zip(h, m) if o > 0 < e) / n

    print(
        f"body: mean {sum(body) / len(body):.2f} "
        f"2-rune {sum(1 for x in body if x == 2) / len(body):.3f} excess/pair 0.0039\n"
    )
    print(f"{'model':<32}{'mean':>7}{'2-rune':>9}{'excess/pair':>13}{'hist vs body':>14}")

    def show(ls: list[int], label: str) -> None:
        e = excess_per_pair([ls], rng, draws=30)[0]
        h, n = hist(ls)
        print(
            f"{label:<32}{sum(ls) / len(ls):>7.2f}"
            f"{sum(1 for x in ls if x == 2) / len(ls):>9.3f}{e:>13.4f}{fit(h, n, hb):>14.4f}"
        )

    show(prose, "prose, untouched")
    for r in (0.05, 0.10, 0.15, 0.25):
        show([L + sum(rng.random() < r for _ in range(L)) for L in prose],
             f"nulls inserted at rate {r}")
    for r in (0.5, 1.0):
        show([L + (rng.random() < r) + (r > 1) for L in prose], f"pad {r} runes per word")
    print(
        "\nThe rate that best matches the histogram, 0.10, still leaves 0.0237 of order"
        "\nwhere the body has 0.0039. Same failure as the merge family."
    )


def jackknife(rng: random.Random) -> None:
    """Is the plaintext reference driven by one page? No."""
    seqs = plaintext_sequences()
    full = excess_per_pair(seqs, rng, draws=300)
    print(f"all {len(seqs)} pages, {sum(len(s) for s in seqs)} words: "
          f"{full[0]:.4f} +- {full[1]:.4f}\n")
    vals = []
    for i in range(len(seqs)):
        e = excess_per_pair([s for j, s in enumerate(seqs) if j != i], rng, draws=150)[0]
        vals.append(e)
        print(f"  drop page {i:>2} ({len(seqs[i]):>3} words): {e:.4f}")
    m = sum(vals) / len(vals)
    sd = (sum((x - m) ** 2 for x in vals) / len(vals)) ** 0.5
    print(f"\njackknife: min {min(vals):.4f} max {max(vals):.4f} sd {sd:.4f}")
    print("No page drives the reference; every leave-one-out estimate stays far above")
    print("the body's 0.0039, and the jackknife spread is smaller than the quoted SE.")


def shape_control(rng: random.Random) -> None:
    """Is the block-length histogram memoryless, and how far is it from language?"""
    body = [x for s in body_sequences() for x in s]
    plain = [x for s in plaintext_sequences() for x in s]
    prose = [x for _n, l in prose_sequences() for x in l]

    def hist(ls: list[int], cap: int = 12) -> tuple[list[float], int]:
        c = collections.Counter(min(x, cap) for x in ls)
        return [c[k] / len(ls) for k in range(1, cap + 1)], len(ls)

    def fit(h: list[float], n: int, model: list[float]) -> float:
        return sum(2 * n * o * math.log(o / e) for o, e in zip(h, model) if o > 0 < e)

    print(f"{'len':>4}{'body':>9}{'LP plain':>10}{'prose':>9}{'geometric':>11}")
    hb, nb = hist(body)
    hp, npl = hist(plain)
    hr, nr = hist(prose)
    q = len(body) / sum(body)
    geo = [(1 - q) ** (k - 1) * q for k in range(1, 13)]
    geo = [x / sum(geo) for x in geo]
    for k in range(12):
        print(f"{k + 1:>4}{hb[k]:>9.3f}{hp[k]:>10.3f}{hr[k]:>9.3f}{geo[k]:>11.3f}")
    print("\nG2 per word against a geometric of matching mean:")
    for name, h, n, ls in (("body", hb, nb, body), ("LP plaintext", hp, npl, plain),
                           ("prose", hr, nr, prose)):
        qq = len(ls) / sum(ls)
        g = [(1 - qq) ** (k - 1) * qq for k in range(1, 13)]
        g = [x / sum(g) for x in g]
        print(f"  {name:<14}{fit(h, n, g) / n:>8.4f}")
    print("\nSo the body is no more memoryless than language is -- a simple block")
    print("process is out. But the shapes still differ, G2 per word:")
    print(f"  body vs LP plaintext {fit(hb, nb, hp) / nb:.4f}")
    print(f"  body vs prose        {fit(hb, nb, hr) / nb:.4f}")
    print(f"  LP plaintext vs prose{fit(hp, npl, hr) / npl:>8.4f}   <- the two references agree")


def merge_control(rng: random.Random) -> None:
    """Does merging adjacent words reproduce the body? Not on both axes at once."""
    books = prose_sequences(40000)
    if not books:
        print("no cached prose available for the merge control")
        return
    lens = books[1][1]
    body = [x for s in body_sequences() for x in s]
    print(
        f"body: mean {sum(body) / len(body):.2f}, "
        f"2-rune share {sum(1 for x in body if x == 2) / len(body):.3f}, "
        "excess/pair 0.0037\n"
    )
    print(f"{'merge p':>8}{'mean':>7}{'2-rune':>9}{'excess/pair':>13}")
    for p in (0.0, 0.04, 0.08, 0.12, 0.16):
        out, i = [], 0
        while i < len(lens):
            cur = lens[i]
            i += 1
            while i < len(lens) and rng.random() < p:
                cur += lens[i]
                i += 1
            out.append(cur)
        e, _se, _o, _m, _n = excess_per_pair([out], rng, draws=25)
        print(
            f"{p:>8.2f}{sum(out) / len(out):>7.2f}"
            f"{sum(1 for x in out if x == 2) / len(out):>9.3f}{e:>13.4f}"
        )
    print("\nmerging only SHORT words, which removes the alternation itself:")
    print(f"{'rule':<32}{'mean':>7}{'2-rune':>9}{'excess/pair':>13}")
    for cap, q in ((2, 0.3), (2, 0.5), (2, 0.7), (2, 0.9), (3, 0.3), (3, 0.5), (3, 0.7)):
        out, i = [], 0
        while i < len(lens):
            cur = lens[i]
            i += 1
            while i < len(lens) and cur <= cap and rng.random() < q:
                cur += lens[i]
                i += 1
            out.append(cur)
        e, se, _o, _m, _n = excess_per_pair([out], rng, draws=30)
        print(
            f"{f'merge length<={cap}, q={q}':<32}{sum(out) / len(out):>7.2f}"
            f"{sum(1 for x in out if x == 2) / len(out):>9.3f}{e:>9.4f}+-{se:.4f}"
        )
    print(
        "\nThe two observables demand different rules. q = 0.3 on words of length <= 2"
        "\nreproduces the body's mean (4.45 against 4.42) and its 2-rune share (0.162"
        "\nagainst 0.159) almost exactly, and still leaves 0.0199 of transition"
        "\nstructure where the body has 0.0039 +- 0.0025 -- a gap of 5.7 sigma. Reaching"
        "\nthe body's sequence needs q = 0.9, which drops the 2-rune share to 0.024."
        "\nNo rule in the family fits both."
    )


def main() -> None:
    rng = random.Random(3301)
    if "--merge" in sys.argv:
        merge_control(rng)
        return
    if "--shape" in sys.argv:
        shape_control(rng)
        return
    if "--tokenize" in sys.argv:
        tokenize_sweep(rng)
        return
    if "--perturb" in sys.argv:
        perturb_control(rng)
        return
    if "--jackknife" in sys.argv:
        jackknife(rng)
        return
    if "--types" in sys.argv:
        type_control()
        return
    if "--sort" in sys.argv:
        sort_control(rng)
        return
    if "--floor" in sys.argv:
        floor_probe(rng)
        return
    if "--intrapage" in sys.argv:
        intrapage(rng)
        return

    print(f"{'corpus':<26}{'words':>8}{'G2':>9}{'surrogate':>11}{'excess/pair':>14}")
    rows = {}
    for label, seqs in (
        ("LP solved plaintext", plaintext_sequences()),
        ("unsolved body", body_sequences()),
    ):
        e, se, obs, mu, _n = excess_per_pair(seqs, rng)
        rows[label] = (e, se)
        words = sum(len(s) for s in seqs)
        print(f"{label:<26}{words:>8,}{obs:>9.1f}{mu:>11.1f}{e:>9.4f} +-{se:.4f}")

    prose = prose_sequences()
    if prose:
        vals = []
        for name, lens in prose:
            e, _se, obs, mu, _n = excess_per_pair([lens], rng, draws=40)
            vals.append(e)
            print(f"{'  prose ' + name:<26}{len(lens):>8,}{obs:>9.1f}{mu:>11.1f}{e:>14.4f}")
        m = sum(vals) / len(vals)
        sd = (sum((x - m) ** 2 for x in vals) / len(vals)) ** 0.5
        rows["prose"] = (m, sd)
        print(f"{'prose, 6 books':<26}{'':>8}{'':>9}{'':>11}{m:>9.4f} +-{sd:.4f}")

    be, bse = rows["unsolved body"]
    print("\nthe body against each reference:")
    for ref in ("LP solved plaintext", "prose"):
        if ref not in rows:
            continue
        e, se = rows[ref]
        z = (e - be) / math.sqrt(se**2 + bse**2)
        print(f"  vs {ref:<22} {e:.4f} vs {be:.4f}   z = {z:+.2f}")
    print(
        "\nThe references' own uncertainty dominates, so these are 3-sigma statements,"
        "\nnot the 15 sigma a naive comparison against the body's surrogate would give."
    )


if __name__ == "__main__":
    main()
