# ABOUTME: Tests whether the within-word lag-k relation is one global g, by how lag-k
# ABOUTME: coincidence varies with word position; scores the walk against a per-word relation.
"""Is the within-word relation one global g?

The walk writes the alphabet at word position j as base_w o g^(j mod 5). Inside a word
the base cancels, and

    c_i == c_(i+k)  <=>  p_i == R_(i,k)(p_(i+k)),   R_(i,k) = A_i^-1 o A_(i+k)

Under one global g, R_(i,k) = g^k at every position of every word, so the lag-k
coincidence rate at word position i carries the plaintext's own position structure
(word-initial letters, long-word interiors) through a fixed relation. Under five
unrelated alphabets it depends on i mod 5. Under a relation that changes from word to
word it averages out, and the rate is the same at every position.

Statistic H: for lags 2, 3, 4, 6, 7 (lag 1 carries the preventer, lag 5 is the identity
in every model here), a chi2 of homogeneity of the coincidence rate across the five
classes of i mod 5, summed over lags; 20 df. H5 keeps only cells expecting 5 or more.

**Result (2026-10-19).** The body reads H = 15.1, H5 = 13.7: no position structure.
On 200 prose windows of the body's size:

    model                  mean H   min    P(H <= body)   P(H5 <= body)
    walk, random g           75.6   13.9      0.005          0.010
    walk, fitted g           97.9   36.6      0.000          0.000
    dodge walk               73.7   17.0      0.000          0.005
    five alphabets           90.3   20.2      0.000          0.000
    walk, 2-rune joined      70.8   17.8      0.000          0.005
    walk, blocks recut       19.5    7.6      0.210          0.490
    fresh g per word         19.7    6.5      0.260          0.450
    walk, clock skips q~0.2  44.4   10.7      0.020          0.035

`--start-end` classes pairs by start position {0, 1, 2+} and the second rune's distance
from the word end {0, 1, 2+} (40 df). Body H = 28.9. Every one-g model misses in all
200 draws (minima 43 to 131); fresh g per word P = 0.08, blocks re-cut P = 0.07.

`--fit`: one g CAN fit all 25 per-class body rates (misfit 3.6, below planted walks
and planted fresh-g corpora), so the walk is not excluded. It needs a g whose powers
are flat across English word positions, which about 1% of random order-5 g are and
the doublet-fitted g is not. On the 45 start-end cells (`--fit --start-end`) the best g
reaches 20.7, the same as on fresh-g corpora (22.2 +- 4.5): the fit absorbs noise.

`--evidence`: the Bayes factor for one g (uniform over order-5 g with five 5-cycles)
against a fresh such g per word. `--convergence` follows the body's value to 20 million
sampled g: -5.0 on start classes, flat from 200,000 on; about -10.5 on start-end
classes (-11.5 at 200,000, -10.3 to -10.8 from 10 million on). With each prose book
held out of the tables (`--holdout`), planted walks on the held-out books give medians
of +11 to +36 (+11 to +55 on start-end), and at most 1 of 80 reaches the body.

`--c0`: the filter behind C-0 ("g has five 5-cycles") reads the same top-1% profile
on fresh-g-per-word corpora ([0 0 7 19 34], [0 0 12 20 28]) as on the body
([0 0 4 20 36]), so it does not need one g. `--cipher-side`: g applied after the base
would leave a permutation-shaped excess in the ciphertext lag-k pair tables. Summed z
over lags 2-4 is +1.24 +- 0.96 for ten planted g, +0.09 +- 1.97 for a fresh g per
word, and -1.43 for the body: disfavoured, 0 of 10, not excluded.

Run with no arguments for the self-test, `--run` for the model table, `--fit` for the
joint fit, `--evidence` for the Bayes factor, `--convergence` for its limit, `--holdout`
for it with each prose book held out, `--c0` and `--cipher-side` for the two checks
above. `--start-end` switches `--run`, `--evidence`, `--convergence` and `--holdout`
to the start-end classes.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from doublet_dodge_walk import encipher as dodge_encipher  # noqa: E402
from fingerprint_battery import (  # noqa: E402
    M,
    distance_tables,
    fingerprint,
    fit_walk_key,
    lp_words,
    ppow,
    prose_corpora,
    rich_order5,
)

from aldegonde.maths import permutation  # noqa: E402

LAGS = (2, 3, 4, 6, 7)
CLASSES = 5  # the period: alphabets repeat every five runes inside a word


def start_class(i: int, k: int, length: int) -> int:
    """The pair's start position mod 5."""
    return i % CLASSES


def start_end_class(i: int, k: int, length: int) -> int:
    """Start position {0, 1, 2+} by the second rune's distance from the end {0, 1, 2+}."""
    return 3 * min(i, 2) + min(length - 1 - (i + k), 2)


START = (start_class, CLASSES)
START_END = (start_end_class, 9)


def counts(words, classing=START) -> np.ndarray:
    """hits[a, c], pairs[a, c]: lag LAGS[a] coincidences by position class c."""
    classify, n = classing
    hits = np.zeros((len(LAGS), n))
    pairs = np.zeros((len(LAGS), n))
    for w in words:
        for a, k in enumerate(LAGS):
            for i in range(len(w) - k):
                c = classify(i, k, len(w))
                pairs[a, c] += 1
                hits[a, c] += w[i] == w[i + k]
    return np.stack([hits, pairs])


def heterogeneity(words, min_expected: float = 0.0, classing=START) -> float:
    """Homogeneity chi2 across position classes, over cells expecting > min_expected.

    The default keeps every cell with at least one pair. A small corpus leaves the
    long-word cells empty, and a cell expecting under one coincidence makes the chi2
    unstable, so `min_expected=5` gives a robust version on the populated cells.
    """
    hits, pairs = counts(words, classing)
    total = 0.0
    for a in range(len(LAGS)):
        p = hits[a].sum() / pairs[a].sum()
        e = pairs[a] * p
        keep = (pairs[a] > 0) & (e > min_expected)
        total += float(((hits[a][keep] - e[keep]) ** 2 / (e[keep] * (1 - p))).sum())
    return total


def per_word(plain, alphabets, rng):
    """c_j = base_w(A_(j mod 5)(p_j)) with a fresh base per word; it cancels inside."""
    out = []
    for w in plain:
        base = permutation.random_permutation(M, rng)
        out.append([base[alphabets[j % CLASSES][p]] for j, p in enumerate(w)])
    return out


def walk(g):
    gp = [ppow(g, k) for k in range(CLASSES)]
    return lambda plain, rng: per_word(plain, gp, rng)


def five_alphabets(plain, rng):
    alphabets = [permutation.random_permutation(M, rng) for _ in range(CLASSES)]
    return per_word(plain, alphabets, rng)


def self_test() -> None:
    rng = random.Random(7)
    plain = prose_corpora(2928, 1)[0]
    # under one g, the relation at lag 5 is the identity at every position, so the
    # lag-5 ciphertext coincidences are exactly the plaintext's
    g = rich_order5(rng)
    c = walk(g)(plain, rng)
    for wp, wc in zip(plain, c):
        for i in range(len(wp) - 5):
            assert (wp[i] == wp[i + 5]) == (wc[i] == wc[i + 5])
    # and under five alphabets the same holds, since A_(i+5) = A_i
    c = five_alphabets(plain, rng)
    for wp, wc in zip(plain, c):
        for i in range(len(wp) - 5):
            assert (wp[i] == wp[i + 5]) == (wc[i] == wc[i + 5])
    hits, pairs = counts([[1, 2, 1, 2, 1, 2, 1, 2]])
    assert hits[0, 0] == pairs[0, 0] == 2, "lag 2 from class 0: i = 0 and 5"
    # the vectorised sampler gives rich order-5 g, and its rates match the per-g ones
    batch = random_rich_batch(np.random.default_rng(0), 20)
    tables = class_tables([plain[:500]], START_END)
    for row, r in zip(batch, batch_rates(batch, tables)):
        g = [int(x) for x in row]
        assert permutation.cycle_type(g).count(5) == 5
        assert np.allclose(r, predicted(g, tables))
    print("self-test passed")


def recut(plain, lengths, rng):
    """The same rune stream cut into blocks of i.i.d. lengths drawn from `lengths`."""
    stream = [r for w in plain for r in w]
    out, i = [], 0
    while i < len(stream):
        n = rng.choice(lengths)
        out.append(stream[i : i + n])
        i += n
    return out


def joined(plain, rng, q: float = 0.40):
    """Each 2-rune word written together with the next word with probability q."""
    out, carry = [], []
    for w in plain:
        if carry:
            out.append(carry + w)
            carry = []
        elif len(w) == 2 and rng.random() < q:
            carry = list(w)
        else:
            out.append(list(w))
    if carry:
        out.append(carry)
    return out


def fresh_g(plain, rng):
    """A new order-5 step for every word, so no relation is shared between words."""
    out = []
    for w in plain:
        gp = [ppow(rich_order5(rng), k) for k in range(CLASSES)]
        out.append(per_word([w], gp, rng)[0])
    return out


def clock_skipped(plain, rng, size: int = 6):
    """The walk on joined words, its clock taking an extra step after `size` cipher runes.

    With six runes in the skip set the clock is perturbed at about 20% of steps, near
    the top of the range the d5 shortfall allows (`d5-bounds-the-clock-perturbation.md`).
    """
    from autokey_variants import encipher_clocked  # noqa: PLC0415

    skip = frozenset(rng.sample(range(M), size))
    base0 = permutation.random_permutation(M, rng)
    sigma = permutation.random_permutation(M, rng)
    return encipher_clocked(
        joined(plain, rng), base0, rich_order5(rng), sigma, skip, by_cipher=True
    )


def run(draws: int = 200, classing=START) -> None:
    body_words = lp_words()
    body = heterogeneity(body_words, classing=classing)
    body5 = heterogeneity(body_words, 5.0, classing)
    lengths = [len(w) for w in body_words]
    rng = random.Random(3301)
    lp = fingerprint(body_words)
    g_fit, sigma, _, _ = fit_walk_key(distance_tables(), lp, rng)
    corpora = prose_corpora(2928, draws)
    models = {
        "walk, random g": lambda plain, r: walk(rich_order5(r))(plain, r),
        "walk, fitted g": walk(g_fit),
        "dodge walk": lambda plain, r: dodge_encipher(
            plain, permutation.random_permutation(M, r), rich_order5(r), sigma
        ),
        "five alphabets": five_alphabets,
        "walk, 2-rune joined": lambda plain, r: walk(rich_order5(r))(
            joined(plain, r), r
        ),
        "walk, blocks recut": lambda plain, r: walk(rich_order5(r))(
            recut(plain, lengths, r), r
        ),
        "fresh g per word": fresh_g,
        "walk, clock skips": clock_skipped,
    }
    df = len(LAGS) * (classing[1] - 1)
    print(
        f"H = homogeneity chi2 over lags {LAGS} and {classing[1]} position classes"
        f" ({df} df)"
    )
    print(f"body H = {body:.1f}; on cells expecting 5 or more, H5 = {body5:.1f}\n")
    print(
        f"{'model':<22}{'mean H':>9}{'sd':>7}{'min':>7}{'P(<=body)':>11}"
        f"{'mean H5':>9}{'min':>7}{'P(<=body)':>11}"
    )
    for name, gen in models.items():
        ciphers = [gen(plain, rng) for plain in corpora]
        h = np.array([heterogeneity(c, classing=classing) for c in ciphers])
        h5 = np.array([heterogeneity(c, 5.0, classing) for c in ciphers])
        print(
            f"{name:<22}{h.mean():>9.1f}{h.std():>7.1f}{h.min():>7.1f}"
            f"{(h <= body).mean():>11.3f}{h5.mean():>9.1f}{h5.min():>7.1f}"
            f"{(h5 <= body5).mean():>11.3f}"
        )


def class_tables(corpora, classing=START) -> np.ndarray:
    """T[a, c, x, y]: plaintext pair table at lag LAGS[a] in position class c."""
    classify, n = classing
    t = np.zeros((len(LAGS), n, M, M))
    for words in corpora:
        for w in words:
            for a, k in enumerate(LAGS):
                for i in range(len(w) - k):
                    t[a, classify(i, k, len(w)), w[i], w[i + k]] += 1
    return t / np.maximum(t.sum(axis=(2, 3), keepdims=True), 1)


def predicted(g, tables) -> np.ndarray:
    """Coincidence rate per cell under one g: P(p_i == g^k(p_(i+k)))."""
    ys = np.arange(M)
    out = np.zeros(tables.shape[:2])
    for a, k in enumerate(LAGS):
        gk = np.array(ppow(g, k % CLASSES))
        out[a] = tables[a][:, gk, ys].sum(axis=1)
    return out


def misfit(g, hits, pairs, tables) -> float:
    r = predicted(g, tables)
    keep = pairs > 0
    e = pairs[keep] * r[keep]
    return float(((hits[keep] - e) ** 2 / (e * (1 - r[keep]))).sum())


def fit_g(
    words, tables, rng, restarts: int = 3, rounds: int = 6000, classing=START
) -> float:
    """The smallest misfit over order-5 g, by conjugating with transpositions."""
    hits, pairs = counts(words, classing)
    best = float("inf")
    for _ in range(restarts):
        g = rich_order5(rng)
        cost = misfit(g, hits, pairs, tables)
        for _ in range(rounds):
            x, y = rng.sample(range(M), 2)
            t = list(range(M))
            t[x], t[y] = y, x
            cand = [t[g[t[z]]] for z in range(M)]
            c = misfit(cand, hits, pairs, tables)
            if c < cost:
                g, cost = cand, c
        best = min(best, cost)
    return best


def joint_fit(planted: int = 20, classing=START) -> None:
    """Can one g fit all 25 per-class body rates? Calibrated on planted walks."""
    rng = random.Random(5)
    corpora = prose_corpora(2928, 200)
    reference = [joined(c, rng) for c in corpora[:150]]
    tables = class_tables(reference, classing)
    body = fit_g(lp_words(), tables, rng, classing=classing)
    walks, fresh = [], []
    for plain in corpora[150 : 150 + planted]:
        words = joined(plain, rng)
        cipher = walk(rich_order5(rng))(words, rng)
        walks.append(fit_g(cipher, tables, rng, classing=classing))
        fresh.append(fit_g(fresh_g(words, rng), tables, rng, classing=classing))
    walks, fresh = np.array(walks), np.array(fresh)
    cells = len(LAGS) * classing[1]
    print(
        f"best one-g misfit over the {cells} per-class cells (prose tables, joined)\n"
    )
    print(f"  body                       {body:6.1f}")
    print(
        f"  planted walk, one g        {walks.mean():6.1f} +- {walks.std():.1f}"
        f"   P(>= body) {(walks >= body).mean():.2f}"
    )
    print(
        f"  planted fresh g per word   {fresh.mean():6.1f} +- {fresh.std():.1f}"
        f"   P(>= body) {(fresh >= body).mean():.2f}"
    )


def random_rich_batch(rng: np.random.Generator, size: int) -> np.ndarray:
    """`size` order-5 permutations with five 5-cycles, uniformly, as rows."""
    points = np.argsort(rng.random((size, M)), axis=1)[:, :25].reshape(size, 5, 5)
    g = np.tile(np.arange(M), (size, 1))
    rows = np.arange(size)[:, None, None]
    g[rows, points] = np.roll(points, -1, axis=2)
    return g


def batch_rates(g: np.ndarray, tables: np.ndarray) -> np.ndarray:
    """rates[b, a, c] for a batch of g, as `predicted` gives for one."""
    size = len(g)
    rows = np.arange(size)[:, None]
    powers = [np.tile(np.arange(M), (size, 1))]
    for _ in range(CLASSES - 1):
        powers.append(g[rows, powers[-1]])
    ys = np.arange(M)
    out = np.zeros((size,) + tables.shape[:2])
    for a, k in enumerate(LAGS):
        gk = powers[k % CLASSES]
        # tables[a][c, gk[b, y], y] summed over y
        out[:, a, :] = tables[a][:, gk, ys].sum(axis=2).T
    return out


def converged_log_evidence(
    words, tables, classing, total: int, chunk: int = 50000, seed: int = 1
) -> list[tuple[int, float]]:
    """The log evidence ratio as the number of sampled g grows, in chunks.

    Returns (samples so far, estimate) after each chunk, so convergence can be read.
    """
    rng = np.random.default_rng(seed)
    hits, pairs = counts(words, classing)
    keep = pairs > 0
    h, n = hits[keep], pairs[keep]
    log_sum, rate_sum, done, trace = -np.inf, np.zeros(int(keep.sum())), 0, []
    while done < total:
        r = batch_rates(random_rich_batch(rng, chunk), tables)[:, keep]
        ll = (h * np.log(r) + (n - h) * np.log1p(-r)).sum(axis=1)
        log_sum = np.logaddexp(log_sum, np.logaddexp.reduce(ll))
        rate_sum += r.sum(axis=0)
        done += chunk
        mean = rate_sum / done
        ll_fresh = float((h * np.log(mean) + (n - h) * np.log1p(-mean)).sum())
        trace.append((done, float(log_sum - np.log(done) - ll_fresh)))
    return trace


def convergence(total: int = 20_000_000, classing=START) -> None:
    rng = random.Random(31)
    tables = class_tables([joined(c, rng) for c in prose_corpora(2928, 150)], classing)
    trace = converged_log_evidence(lp_words(), tables, classing, total)
    print("body log evidence, one g against a fresh g per word, by samples of g\n")
    for done, value in trace:
        if done in (200_000, 2_000_000) or done % 5_000_000 == 0:
            print(f"  {done:>11,}  {value:+7.2f}")


def log_evidence_ratio(words, rates: np.ndarray, classing=START) -> float:
    """log P(cells | one g, g from the prior) - log P(cells | a fresh g per word).

    `rates[s]` holds the per-class rates of the s-th sampled g. One g averages the
    binomial likelihood over the sample; a fresh g per word gives every pair the
    sample's mean rate, since each word draws its own g.
    """
    hits, pairs = counts(words, classing)
    keep = pairs > 0
    h, n = hits[keep], pairs[keep]
    r = rates[:, keep]
    ll = (h * np.log(r) + (n - h) * np.log1p(-r)).sum(axis=1)
    mean = r.mean(axis=0)
    ll_fresh = float((h * np.log(mean) + (n - h) * np.log1p(-mean)).sum())
    top = ll.max()
    return float(top + np.log(np.exp(ll - top).mean()) - ll_fresh)


def evidence(samples: int = 20000, planted: int = 20, classing=START) -> None:
    rng = random.Random(9)
    corpora = prose_corpora(2928, 200)
    tables = class_tables([joined(c, rng) for c in corpora[:150]], classing)
    rates = np.array([predicted(rich_order5(rng), tables) for _ in range(samples)])
    body = log_evidence_ratio(lp_words(), rates, classing)
    walks, fresh = [], []
    for plain in corpora[150 : 150 + planted]:
        words = joined(plain, rng)
        cipher = walk(rich_order5(rng))(words, rng)
        walks.append(log_evidence_ratio(cipher, rates, classing))
        fresh.append(log_evidence_ratio(fresh_g(words, rng), rates, classing))
    walks, fresh = np.array(walks), np.array(fresh)
    hits, pairs = counts(lp_words(), classing)
    mean = rates.mean(axis=0)
    print("pooled body rate per lag against a fresh g per word (prose tables)\n")
    for a, k in enumerate(LAGS):
        n = pairs[a].sum()
        expect = float((mean[a] * pairs[a]).sum())
        z = (hits[a].sum() - expect) / np.sqrt(expect)
        print(
            f"  lag {k}: body {hits[a].sum() / n:.4f} ({int(hits[a].sum())} of {int(n)}),"
            f" fresh g predicts {expect / n:.4f}, z {z:+.2f}"
        )
    print()
    print(f"log evidence, one g against a fresh g per word ({samples} sampled g)\n")
    print(f"  body                        {body:+7.2f}")
    print(
        f"  planted walk, one g         {np.median(walks):+7.2f} median"
        f"   range [{walks.min():+.2f}, {walks.max():+.2f}]"
    )
    print(
        f"  planted fresh g per word    {np.median(fresh):+7.2f} median"
        f"   range [{fresh.min():+.2f}, {fresh.max():+.2f}]"
    )


def holdout(samples: int = 20000, planted: int = 8, classing=START) -> None:
    """The Bayes factor with each prose book held out of the tables and planted from.

    Planted plaintext then differs from the tables in register, as the body's does.
    """
    from compact_state_models import _prose_books  # noqa: PLC0415

    rng = random.Random(21)
    books = _prose_books()

    def windows(book):
        return [
            [list(w) for w in book[i : i + 2928]]
            for i in range(0, len(book) - 2927, 2928)
        ]

    body = lp_words()
    below = total = 0
    print(
        f"{'held out':>9}{'walk median':>13}{'walk min':>10}{'fresh median':>14}{'body':>8}"
    )
    for hold in range(len(books)):
        rest = [w for i, b in enumerate(books) if i != hold for w in windows(b)]
        tables = class_tables([joined(c, rng) for c in rest[:150]], classing)
        rates = np.array([predicted(rich_order5(rng), tables) for _ in range(samples)])
        plants = windows(books[hold])[:planted]
        wv = [
            log_evidence_ratio(
                walk(rich_order5(rng))(joined(x, rng), rng), rates, classing
            )
            for x in plants
        ]
        fv = [
            log_evidence_ratio(fresh_g(joined(x, rng), rng), rates, classing)
            for x in plants
        ]
        b = log_evidence_ratio(body, rates, classing)
        below += sum(1 for v in wv if v <= b)
        total += len(wv)
        print(
            f"{hold:>9}{np.median(wv):>+13.2f}{min(wv):>+10.2f}{np.median(fv):>+14.2f}"
            f"{b:>+8.2f}"
        )
    print(f"\nplanted walks at or below the body: {below} of {total}")


def c0_check() -> None:
    """Does C-0's five-cycle reading need one g? Run its filter on a fresh-g corpus."""
    import d_profile_constrains_g as d  # noqa: PLC0415

    prose = list(prose_corpora(2928, 60))
    mats, tot = d.lag_tables(prose)
    pool = d.make_pool(6000, 5)
    cyc = np.array([d.cycles(g) for g in pool])
    rng = random.Random(77)

    def top(words):
        meas = d.measure(words)
        scores = np.array([d.chi2(h, meas, mats, tot) for h in pool])
        return np.bincount(cyc[scores <= np.percentile(scores, 1)], minlength=6)[1:]

    for n in range(2):
        cipher = [w for c in prose[2 * n : 2 * n + 2] for w in fresh_g(c, rng)]
        print(
            f"fresh g per word, corpus {n + 1}: top-1% five-cycle counts {top(cipher)}"
        )
    print(f"body:                         top-1% five-cycle counts {top(lp_words())}")


def permutation_excess(words, rng, lags=(2, 3, 4), shuffles: int = 20) -> float:
    """Summed z over lags of the best one-permutation mass in the lag-k pair table.

    Each lag's null shuffles the second coordinate of its own pairs, which keeps both
    marginals and removes any pairing.
    """
    from scipy.optimize import linear_sum_assignment  # noqa: PLC0415

    def mass(a, b):
        t = np.zeros((M, M))
        np.add.at(t, (a, b), 1)
        r, c = linear_sum_assignment(-t)
        return t[r, c].sum() / t.sum()

    total = 0.0
    for k in lags:
        a, b = zip(*[(w[i], w[i + k]) for w in words for i in range(len(w) - k)])
        a, b = np.array(a), np.array(b)
        null = [mass(a, rng.permutation(b)) for _ in range(shuffles)]
        total += (mass(a, b) - np.mean(null)) / np.std(null)
    return float(total)


def cipher_side_check(planted: int = 10) -> None:
    """g applied after the base, c_j = g^j(base_w(p_j)), would make the relation vary
    per word too, but it puts every plaintext repeat at lag k on the graph of g^k in
    the ciphertext pair table, a permutation-shaped excess the body would show.
    """
    rng = np.random.default_rng(3)
    prng = random.Random(3)
    body = permutation_excess(lp_words(), rng)
    planted_z, fresh_z = [], []
    for plain in prose_corpora(2928, planted):
        gp = [ppow(rich_order5(prng), j) for j in range(CLASSES)]
        cs = []
        for w in plain:
            base = permutation.random_permutation(M, prng)
            cs.append([gp[j % CLASSES][base[p]] for j, p in enumerate(w)])
        planted_z.append(permutation_excess(cs, rng))
        fresh_z.append(permutation_excess(fresh_g(plain, prng), rng))
    planted_z, fresh_z = np.array(planted_z), np.array(fresh_z)
    print("summed z of the best one-permutation mass, lags 2, 3, 4\n")
    print(f"  body                  {body:+6.2f}")
    print(
        f"  cipher-side g         {planted_z.mean():+6.2f} +- {planted_z.std():.2f}"
        f"   P(<= body) {(planted_z <= body).mean():.2f}"
    )
    print(
        f"  fresh g per word      {fresh_z.mean():+6.2f} +- {fresh_z.std():.2f}"
        f"   P(<= body) {(fresh_z <= body).mean():.2f}"
    )


if __name__ == "__main__":
    classing = START_END if "--start-end" in sys.argv else START
    if "--convergence" in sys.argv:
        convergence(classing=classing)
    elif "--holdout" in sys.argv:
        holdout(classing=classing)
    elif "--c0" in sys.argv:
        c0_check()
    elif "--cipher-side" in sys.argv:
        cipher_side_check()
    elif "--evidence" in sys.argv:
        evidence(classing=classing)
    elif "--fit" in sys.argv:
        joint_fit(classing=classing)
    elif "--run" in sys.argv:
        run(classing=classing)
    else:
        self_test()
