# ABOUTME: Asks whether the walk's sigma-chain is observable at all, by comparing it to a
# ABOUTME: cipher that draws an independent base for every word and shares everything else.
"""Every sigma constraint in this directory assumes the chain exists. Can it be seen?

The length-clocked walk says consecutive bases are related:

    base_(w+1) = base_w o g^(a_w) o sigma

That chain is what carries `sigma-is-even.md`, `sigma-moves-almost-every-rune.md` and
`sigma-cycle-type-narrowed.md`. It is also what a 218-core-hour sweep would search.

But `base-pool-floor.md` shows the base is distinct for essentially every one of the
2,928 blocks, and a chain through 2,928 distinct permutations of A29 looks, pairwise,
like 2,928 independent draws. If no statistic separates the two, then sigma is not a
measurable object and every constraint on it is a property of the model rather than of
the corpus.

So build the null that differs in exactly one thing. Both ciphers:

  - step the letter alphabet by the same g of order 5, on the same continuous clock
  - hold the base fixed inside a word
  - change base at every separator

and differ only in HOW the base changes: composed with g^a o sigma, or redrawn at
random. Then run the full fingerprint battery on both, across keys, and measure

    separation = |mean_walk - mean_free| / pooled within-model sd

pooling the within-model spread over keys as well as corpora, because
`battery-cells-test-the-key.md` shows the key is the larger source for eleven cells.

Falsifiable: if any cell separates the two at more than about 1, the chain is visible
and the sigma programme has an observable to fit. If none does, it is not.

The answer is both. No MARGINAL cell separates them -- all nineteen agree, several of
them exactly, because a within-word statistic sees one uniformly random base either
way. But one CONDITIONAL statistic does, and the last section measures it: of the word
pairs that repeat, the fraction that extend to a repeated two-word phrase. A chain
carries a repeat forward, because equal bases at w and v give equal bases at w+1 and
v+1 whenever the clock phases agree, one time in five. Independent draws have to
coincide twice, one time in N. The ratio is the chain's signature.

    python chain_is_observable.py [--keys 12] [--draws 20]
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import recurrence_counts  # noqa: E402
from doublet_dodge_walk import order5_fixing  # noqa: E402
from fingerprint_battery import (  # noqa: E402
    M,
    compose,
    fingerprint,
    lp_words,
    ppow,
    prose_corpora,
)


def walk(g, sigma):
    """The chain: each base is the previous one composed with g^a o sigma."""

    def generate(plain, rng):
        gp = [ppow(g, k) for k in range(5)]
        base = rng.sample(range(M), M)
        out, clock = [], 0
        for word in plain:
            cw = []
            for p in word:
                cw.append(base[gp[clock % 5][p]])
                clock += 1
            out.append(cw)
            base = compose(base, compose(gp[(clock - 1) % 5], sigma))
        return out

    return generate


def free(g, sigma):
    """No chain: a fresh random base per word. Everything else is identical.

    `sigma` is accepted and ignored so the two generators share a signature.
    """

    def generate(plain, rng):
        gp = [ppow(g, k) for k in range(5)]
        out, clock = [], 0
        for word in plain:
            base = rng.sample(range(M), M)
            cw = []
            for p in word:
                cw.append(base[gp[clock % 5][p]])
                clock += 1
            out.append(cw)
        return out

    return generate


def cycling(period: int):
    """Positive control: a chain that returns to its start every `period` words.

    A negative result is only evidence if the test can see a chain when one is
    visible. This is the same cipher with the base pool deliberately closed, so the
    battery has base reuse to find.
    """

    def make(g, sigma):
        def generate(plain, rng):
            gp = [ppow(g, k) for k in range(5)]
            pool = [rng.sample(range(M), M) for _ in range(period)]
            out, clock = [], 0
            for w, word in enumerate(plain):
                base = pool[w % period]
                cw = []
                for p in word:
                    cw.append(base[gp[clock % 5][p]])
                    clock += 1
                out.append(cw)
            return out

        return generate

    return make


def collect(make, keys: int, draws: int, corpora) -> dict[str, np.ndarray]:
    """Per-key means and per-key within-spread for every cell."""
    rng = random.Random(4242)
    means: dict[str, list[float]] = {}
    spreads: dict[str, list[float]] = {}
    for _ in range(keys):
        g = order5_fixing(rng.sample(range(M), 4), rng)
        sigma = rng.sample(range(M), M)
        r = random.Random(3301)
        sims = [fingerprint(make(g, sigma)(p, r)) for p in corpora]
        for k in sims[0]:
            v = np.array([s[k] for s in sims], float)
            v = v[np.isfinite(v)]
            if len(v) < 2:
                continue
            means.setdefault(k, []).append(float(v.mean()))
            spreads.setdefault(k, []).append(float(v.std(ddof=1)))
    return {
        k: (np.array(means[k]), np.array(spreads[k]))
        for k in means
        if len(means[k]) >= 3
    }


def main() -> None:
    keys, draws = 12, 20
    for i, a in enumerate(sys.argv):
        if a == "--keys" and i + 1 < len(sys.argv):
            keys = int(sys.argv[i + 1])
        if a == "--draws" and i + 1 < len(sys.argv):
            draws = int(sys.argv[i + 1])

    lp = fingerprint(lp_words())
    corpora = list(prose_corpora(2928, draws))
    a = collect(walk, keys, draws, corpora)
    b = collect(free, keys, draws, corpora)

    print(f"{keys} keys x {draws} corpora per cipher. Separation pools the within-model")
    print("spread over corpora AND keys, since the key is the larger source for many cells.\n")
    print(f"{'cell':<16}{'corpus':>10}{'chain':>11}{'free':>11}{'spread':>10}{'sep':>8}")
    rows = []
    for k in sorted(a.keys() & b.keys()):
        ma, sa = a[k]
        mb, sb = b[k]
        # total within-model sd: corpora spread plus key spread, both models pooled
        var_a = float(np.mean(sa**2) + ma.var(ddof=1))
        var_b = float(np.mean(sb**2) + mb.var(ddof=1))
        pooled = float(np.sqrt((var_a + var_b) / 2))
        sep = abs(ma.mean() - mb.mean()) / pooled if pooled > 1e-12 else 0.0
        print(f"{k:<16}{lp[k]:>10.4f}{ma.mean():>11.4f}{mb.mean():>11.4f}"
              f"{pooled:>10.4f}{sep:>8.2f}")
        rows.append((k, sep))

    rows.sort(key=lambda r: -r[1])
    top = rows[0]
    print(f"\nlargest separation: {top[0]} at {top[1]:.2f}")
    strong = [k for k, s in rows if s > 1.0]
    print(f"cells separating the chain from independent bases at sep > 1.0: "
          f"{len(strong)} of {len(rows)}"
          + (f" -- {', '.join(strong)}" if strong else ""))
    if not strong:
        print(
            "\nNo MARGINAL cell distinguishes a chained base from an independently"
            "\nredrawn one. The conditional statistic at the end of this run does."
        )

    # The unpaired comparison above throws away most of its power: both ciphers share g,
    # and the key spread it pools into the denominator is largely g's. Pairing on g
    # removes it, so a difference of a few thousandths becomes visible.
    print("\nPaired on g, which both ciphers share. Only the base rule differs.\n")
    print(f"{'cell':<16}{'mean diff':>12}{'sd of diff':>12}{'t':>8}{'keys':>6}")
    paired = paired_differences(keys, draws, corpora)
    for k, d in sorted(paired.items(), key=lambda kv: -abs(kv[1].mean() / (kv[1].std(ddof=1) / np.sqrt(len(kv[1])) + 1e-30))):
        se = d.std(ddof=1) / np.sqrt(len(d))
        t = d.mean() / se if se > 1e-30 else 0.0
        if abs(t) < 1.5:
            continue
        print(f"{k:<16}{d.mean():>12.5f}{d.std(ddof=1):>12.5f}{t:>8.2f}{len(d):>6}")
    print("\nCells with |t| < 1.5 are omitted. A within-word cell must show t = 0 by"
          "\nconstruction: both ciphers hold one uniformly random base inside a word.")

    # Sensitivity: the same comparison against chains that DO revisit their states,
    # so a null result above can be read as blindness to chaining or as a real absence.
    print("\nPositive control: the free cipher against chains with a closed base pool.")
    print(f"{'pool':>8}{'identical':>12}{'returns':>10}{'ioc':>9}{'max sep':>9}  cell")
    fm = {k: v for k, v in b.items()}
    for period in (29, 100, 300, 1000, 2928):
        c = collect(cycling(period), max(4, keys // 3), draws, corpora)
        best, where = 0.0, "-"
        for k in c.keys() & fm.keys():
            mc, sc = c[k]
            mf, sf = fm[k]
            pooled = np.sqrt(
                (np.mean(sc**2) + mc.var(ddof=1) + np.mean(sf**2) + mf.var(ddof=1)) / 2
            )
            if pooled > 1e-12:
                sep = abs(mc.mean() - mf.mean()) / pooled
                if sep > best:
                    best, where = sep, k
        print(f"{period:>8}{c['identical'][0].mean():>12.1f}"
              f"{c['returns'][0].mean():>10.2f}{c['ioc'][0].mean():>9.4f}"
              f"{best:>9.2f}  {where}")
    print(
        "\nThe pool floor of `two-rune-depth-no-base-reuse.md` puts the corpus above the"
        "\nlargest row, so on the marginal counts the corpus sits where this test has no"
        "\npower."
    )

    extension_rate(keys, draws, corpora)


def extension_rate(keys: int, draws: int, corpora) -> None:
    """Of the word pairs that repeat, how many extend to a repeated phrase.

    This is where the chain shows. Equal bases at words w and v give equal bases at
    w+1 and v+1 whenever the clock phases agree, which is one time in five; under
    independent draws the second alphabet has to coincide by itself, one time in N.
    So the chain multiplies the extension rate by about N/5 while leaving the
    marginal counts alone, which is why nothing above saw it.
    """
    lp = recurrence_counts(lp_words())
    print("\nExtension rate: returns per identical pair, over keys and corpora.\n")
    print(f"{'pool':>7}{'rule':>10}{'identical':>11}{'returns':>9}{'rate':>10}{'1 in':>9}")
    rng = random.Random(505)
    for period in (300, 500):
        for chained in (True, False):
            tot_i = tot_r = 0
            for _ in range(max(4, keys // 2)):
                g = order5_fixing(rng.sample(range(M), 4), rng)
                r = random.Random(3301)
                for plain in corpora:
                    c = recurrence_counts(pool_cipher(g, period, chained)(plain, r))
                    tot_i += c["identical"]
                    tot_r += c["returns"]
            rate = tot_r / tot_i if tot_i else 0.0
            label = "chained" if chained else "free"
            inv = f"{1 / rate:,.0f}" if rate else f">{tot_i:,}"
            print(f"{period:>7}{label:>10}{tot_i:>11,}{tot_r:>9}{rate:>10.5f}{inv:>9}")
    rate = lp["returns"] / lp["identical"]
    print(f"{'corpus':>7}{'':>10}{lp['identical']:>11}{lp['returns']:>9}"
          f"{rate:>10.5f}{1 / rate:>9,.0f}")
    print(
        "\nThe corpus's single return is tens of times more likely under a chained base"
        "\nthan under independent per-word draws. It rests on one event, so it is weak"
        "\nevidence -- but it is evidence, and it is the only channel that carries any."
    )


def pool_cipher(g, period: int, chained: bool):
    """A pool of `period` alphabets, walked in order or sampled independently."""

    def generate(plain, rng):
        gp = [ppow(g, k) for k in range(5)]
        pool = [rng.sample(range(M), M) for _ in range(period)]
        idx = (
            [w % period for w in range(len(plain))]
            if chained
            else [rng.randrange(period) for _ in plain]
        )
        out, clock = [], 0
        for w, word in enumerate(plain):
            base = pool[idx[w]]
            cw = []
            for p in word:
                cw.append(base[gp[clock % 5][p]])
                clock += 1
            out.append(cw)
        return out

    return generate


def paired_differences(keys: int, draws: int, corpora) -> dict[str, np.ndarray]:
    """chain minus free, cell by cell, with g and the corpora held identical."""
    rng = random.Random(4242)
    diffs: dict[str, list[float]] = {}
    for _ in range(keys):
        g = order5_fixing(rng.sample(range(M), 4), rng)
        sigma = rng.sample(range(M), M)
        ra, rb = random.Random(3301), random.Random(3301)
        sa = [fingerprint(walk(g, sigma)(p, ra)) for p in corpora]
        sb = [fingerprint(free(g, sigma)(p, rb)) for p in corpora]
        for k in sa[0]:
            va = np.array([s[k] for s in sa], float)
            vb = np.array([s[k] for s in sb], float)
            m = np.isfinite(va) & np.isfinite(vb)
            if m.sum() < 2:
                continue
            diffs.setdefault(k, []).append(float(va[m].mean() - vb[m].mean()))
    return {k: np.array(v) for k, v in diffs.items() if len(v) >= 3}


if __name__ == "__main__":
    main()
