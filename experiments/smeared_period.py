# ABOUTME: Looks for a repeating key whose period has been smeared over a band of lags by
# ABOUTME: a preventer that skips key terms, by summing coincidences over lag bands.
"""A periodic key under a key-eating preventer has no single period to find.

`no-periodicity.md` and row B4 scan single lags. If a would-be repeat is dodged by
re-enciphering with the next key term, the key runs ahead of the text by one term per
36 runes, so two runes share a key term at lag P minus the skips between them. Over a
stretch of P runes that is P/36 skips with a Poisson spread: the coincidence peak at
lag P is spread over a band of lags below it, and each single lag keeps too little to
see once P passes about a hundred. The sum over the band keeps all of it.

The statistic is the coincidence count summed over a window of consecutive lags, as a z
against 1/29, maximised over the window's position for each of several widths. What the
null keeps and destroys: surrogate bodies from `c3301.low_doublet_null` keep the rune
counts and the doublet rate and destroy the order; the maximum over positions is taken
on each, so the scan over lags is priced. The widths are a second family, priced by
taking the smallest P over widths on the surrogates too.

The control plants a balanced random key of period P on the author's words at the
body's block lengths, with the dodge, and must find a band just below P.

    python experiments/smeared_period.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import lp_corpus  # noqa: E402
import lp_plaintext_register  # noqa: E402

from aldegonde import c3301  # noqa: E402

M = 29
SEED = 20261112
MAX_LAG = 6400
WIDTHS = (3, 5, 10, 20, 40, 80, 160)
SURROGATES = 400
CONTROL_PERIODS = (100, 300, 600, 1000, 2000)


def lag_hits(s: np.ndarray) -> np.ndarray:
    """Coincidences at every lag 0..MAX_LAG (lag 0 and 1 left at zero)."""
    out = np.zeros(MAX_LAG + 1)
    for lag in range(2, MAX_LAG + 1):
        out[lag] = (s[:-lag] == s[lag:]).sum()
    return out


def band_maxima(hits: np.ndarray, n: int) -> dict[int, tuple[float, int]]:
    """For each width, the best band z and its first lag."""
    pairs = n - np.arange(MAX_LAG + 1, dtype=float)
    pairs[:2] = 0
    ch, cp = np.cumsum(hits), np.cumsum(pairs)
    out = {}
    for w in WIDTHS:
        h = ch[w + 1 :] - ch[1:-w]  # lags a+1 .. a+w for a >= 1
        p = cp[w + 1 :] - cp[1:-w]
        z = (h - p / M) / np.sqrt(p / M * (1 - 1 / M))
        i = int(np.argmax(z))
        out[w] = (float(z[i]), i + 2)
    return out


def plant(lens, period: int, rng: random.Random) -> np.ndarray:
    """Vigenere under a random key of the given period with the key-skipping dodge."""
    key = [rng.randrange(M) for _ in range(period)]
    pools: dict[int, list[list[int]]] = {}
    for w in lp_plaintext_register.corpus():
        pools.setdefault(len(w), []).append(w)
    out: list[int] = []
    j, prev = 0, -1
    for L in lens:
        LL = L
        while LL not in pools:
            LL -= 1
        w = rng.choice(pools[LL])
        for r in (w * (L // len(w) + 1))[:L]:
            c = (r + key[j % period]) % M
            if c == prev:
                j += 1
                c = (r + key[j % period]) % M
            out.append(c)
            prev = c
            j += 1
    return np.array(out, dtype=np.int64)


def main() -> None:
    rng = random.Random(SEED)
    tok = lp_corpus.load_tokenized()
    body = np.array(tok.stream, dtype=np.int64)
    n = len(body)
    lens = [len(w) for w in tok.words()]

    null_model = c3301.low_doublet_null()
    null = {w: [] for w in WIDTHS}
    for _ in range(SURROGATES):
        sur = np.array(null_model(tok.stream, rng), dtype=np.int64)
        for w, (z, _) in band_maxima(lag_hits(sur), n).items():
            null[w].append(z)
    null = {w: np.array(v) for w, v in null.items()}

    def width_p(maxima) -> dict[int, float]:
        return {
            w: (int((null[w] >= maxima[w][0]).sum()) + 1) / (SURROGATES + 1)
            for w in WIDTHS
        }

    # the smallest per-width P on each surrogate, leaving that surrogate out of its own null
    null_min_p = []
    for k in range(SURROGATES):
        ps = []
        for w in WIDTHS:
            others = np.delete(null[w], k)
            ps.append((int((others >= null[w][k]).sum()) + 1) / SURROGATES)
        null_min_p.append(min(ps))
    null_min_p = np.array(null_min_p)

    print(
        f"control: a random key of period P under the key-skipping dodge, {n:,} runes"
    )
    print(f"  {'P':>6}{'best band':>22}{'width':>7}{'z':>8}{'P over lags':>13}")
    recovered = 0
    still = True
    for period in CONTROL_PERIODS:
        maxima = band_maxima(lag_hits(plant(lens, period, rng)), n)
        ps = width_p(maxima)
        w = min(WIDTHS, key=lambda x: (ps[x], -maxima[x][0]))
        z, first = maxima[w]
        skips = period / 36
        # a multiple of the period is a period: accept the band below any m * P
        in_band = any(
            m * (period - skips) - 6 * (m * skips) ** 0.5 - w <= first
            and first + w - 1 <= m * period
            for m in range(1, MAX_LAG // period + 1)
        )
        found = in_band and ps[w] <= 0.05
        still = still and found
        if still:
            recovered = period
        print(
            f"  {period:>6}{f'lags {first}..{first + w - 1}':>22}{w:>7}{z:>+8.2f}{ps[w]:>13.3f}"
            f"   {'found' if found else 'not found'}"
        )

    maxima = band_maxima(lag_hits(body), n)
    ps = width_p(maxima)
    print("\nthe body")
    print(f"  {'width':>6}{'best band':>22}{'z':>8}{'null max':>16}{'P over lags':>13}")
    for w in WIDTHS:
        z, first = maxima[w]
        print(
            f"  {w:>6}{f'lags {first}..{first + w - 1}':>22}{z:>+8.2f}"
            f"{f'{null[w].mean():.2f} +- {null[w].std(ddof=1):.2f}':>16}{ps[w]:>13.3f}"
        )
    best_p = min(ps.values())
    family = (int((null_min_p <= best_p).sum()) + 1) / (SURROGATES + 1)
    print(
        f"\nsmallest P over the {len(WIDTHS)} widths: {best_p:.3f}; a surrogate body does as "
        f"well {family:.2f} of the time"
    )
    if recovered == 0:
        print(
            "VERDICT: the control found no planted period; the negative means nothing."
        )
    elif family < 0.01:
        print("VERDICT: a band of lags stands out. Check its harmonics.")
    else:
        print(
            f"VERDICT: no band of lags holds a smeared period (family P {family:.2f}). A "
            f"repeating key under a key-skipping preventer is excluded up to period "
            f"{recovered}, the longest the control recovers."
        )


if __name__ == "__main__":
    main()
