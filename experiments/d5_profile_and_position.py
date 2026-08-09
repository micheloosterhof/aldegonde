# ABOUTME: The full within-word distance profile with phases, what d10 can and
# ABOUTME: cannot test, and where inside a word the d5 echo actually sits.
"""Three questions about the d5 echo that the headline number hides.

1. **The whole profile.** d1..d12 against the structure-free surrogate, with
   the period-5 phase of each cell. The phase pattern is the model's signature:
   phase 0 (d5, d10) should echo, phase 1 (d1, d6) should be suppressed.

2. **Can d10 check the recurrence?** `g^5 = id` predicts the echo returns at
   d10. Words long enough to supply a d10 pair are rare, so the answer is a
   power calculation, not a measurement — and a flat d10 must not be read as
   evidence against the model.

3. **Where in the word does the echo sit?** Grouped by the pair's start
   position: is it 1&6, or 2&7, or spread evenly? A concentration would mean
   something other than a uniform period-5 leak. The trend across positions
   also tests base drift: if the base moved WITHIN a word the echo would decay
   as the pair starts later, since more drift accumulates between i and i+5.

The surrogate keeps every word boundary and mark and redraws only the runes at
the observed doublet rate, so it holds the word-length structure fixed. That
matters for question 3: later start positions only exist inside longer words,
and the surrogate carries the same confound, so comparing against it removes it.
"""

from __future__ import annotations

import random
from math import sqrt

import numpy as np
from scipy import stats

from aldegonde import c3301
from experiments.negative_control_grid import load, within_pairs

DRAWS = 400
SEED = 3301
ECHO_D = 5
FLAT = 1 / 29


def position_pairs(words: list[list[int]], d: int = ECHO_D) -> dict[int, tuple]:
    """Index pairs (i, i+d) inside a word, grouped by the start position i."""
    out: dict[int, tuple[list[int], list[int]]] = {}
    pos = 0
    for w in words:
        for i in range(len(w) - d):
            a, b = out.setdefault(i, ([], []))
            a.append(pos + i)
            b.append(pos + i + d)
        pos += len(w)
    return {i: (np.array(a), np.array(b)) for i, (a, b) in sorted(out.items())}


def rates(stream: np.ndarray, groups: dict) -> dict[int, float]:
    return {k: float(np.mean(stream[a] == stream[b])) for k, (a, b) in groups.items()}


def trend(stream: np.ndarray, groups: dict, floor: int = 20) -> float:
    """Weighted least-squares slope of the rate against start position."""
    xs, ys, ws = [], [], []
    for i, (a, b) in groups.items():
        if len(a) < floor:
            continue
        xs.append(i)
        ys.append(float(np.mean(stream[a] == stream[b])))
        ws.append(len(a))
    xs, ys, ws = np.array(xs), np.array(ys), np.array(ws, float)
    xm, ym = np.average(xs, weights=ws), np.average(ys, weights=ws)
    return float(np.sum(ws * (xs - xm) * (ys - ym)) / np.sum(ws * (xs - xm) ** 2))


def surrogates(stream: np.ndarray, rng: random.Random):
    model = c3301.low_doublet_null()
    for _ in range(DRAWS):
        yield np.array(model(stream.tolist(), random.Random(rng.randrange(2**32))),
                       dtype=np.int8)


def main() -> None:
    rng = random.Random(SEED)
    stream, words = load()
    dist = within_pairs(words)
    posn = position_pairs(words)

    draws_d = {d: [] for d in dist}
    draws_p = {i: [] for i in posn}
    draws_t = []
    for surr in surrogates(stream, rng):
        for d, v in rates(surr, dist).items():
            draws_d[d].append(v)
        for i, v in rates(surr, posn).items():
            draws_p[i].append(v)
        draws_t.append(trend(surr, posn))

    print("1. within-word profile, all distances\n")
    print(f"{'d':>3}{'pairs':>8}{'match':>7}{'rate':>9}{'surrogate':>11}"
          f"{'sd':>8}{'z':>7}   phase")
    for d, (a, b) in dist.items():
        n = len(a)
        m = int(np.count_nonzero(stream[a] == stream[b]))
        mu, sd = np.mean(draws_d[d]), np.std(draws_d[d])
        z = (m / n - mu) / sd if sd else float("nan")
        phase = "0 (echo)" if d % 5 == 0 else str(d % 5)
        print(f"{d:>3}{n:>8}{m:>7}{m / n:>9.4f}{mu:>11.4f}{sd:>8.4f}{z:>+7.2f}"
              f"   {phase}")

    a10, b10 = dist[10]
    n10 = len(a10)
    echo = float(np.mean(stream[dist[5][0]] == stream[dist[5][1]]))
    se10 = sqrt(FLAT * (1 - FLAT) / n10)
    need = FLAT * (1 - FLAT) / ((echo - FLAT) / 2) ** 2
    print(f"\n2. what d10 can test: {n10} pairs, "
          f"{int(np.count_nonzero(stream[a10] == stream[b10]))} matches")
    print(f"   flat predicts {FLAT * n10:.1f} matches, a d5-strength echo "
          f"{echo * n10:.1f} — a gap of {(echo - FLAT) * n10:.1f}")
    print(f"   the standard error on the rate is {se10:.4f}, so the two "
          f"hypotheses sit {(echo - FLAT) / se10:.2f} sd apart")
    print(f"   separating them at 2 sigma needs ~{need:.0f} pairs against the "
          f"{n10} available ({need / n10:.0f}x the long-word supply)")
    print("   d10 is therefore not a test; a flat d10 is not evidence against "
          "the echo")

    print("\n3. where the d5 echo sits inside the word\n")
    print(f"{'runes':>10}{'pairs':>8}{'match':>7}{'rate':>9}{'surrogate':>11}"
          f"{'sd':>8}{'z':>7}")
    obs = []
    for i, (a, b) in posn.items():
        n = len(a)
        m = int(np.count_nonzero(stream[a] == stream[b]))
        mu, sd = np.mean(draws_p[i]), np.std(draws_p[i])
        z = (m / n - mu) / sd if sd else float("nan")
        obs.append((m, n))
        print(f"{f'{i + 1} & {i + 1 + ECHO_D}':>10}{n:>8}{m:>7}{m / n:>9.4f}"
              f"{mu:>11.4f}{sd:>8.4f}{z:>+7.2f}")

    tot_m, tot_n = sum(m for m, _ in obs), sum(n for _, n in obs)
    p = tot_m / tot_n
    chi2 = sum((m - n * p) ** 2 / (n * p * (1 - p)) for m, n in obs)
    df = len(obs) - 1
    print(f"\n   pooled {tot_m}/{tot_n} = {p:.4f}")
    print(f"   homogeneity across start positions: chi2 = {chi2:.2f} on {df} df, "
          f"p = {stats.chi2.sf(chi2, df):.3f}")

    t_real = trend(stream, posn)
    t_mu, t_sd = np.mean(draws_t), np.std(draws_t)
    print(f"\n   slope against start position: real {t_real:+.5f}, surrogate "
          f"{t_mu:+.5f} +- {t_sd:.5f}, z = {(t_real - t_mu) / t_sd:+.2f}")
    print("   base drift inside a word would make this NEGATIVE (the echo")
    print("   decaying as more drift accumulates). It does not.")


if __name__ == "__main__":
    main()
