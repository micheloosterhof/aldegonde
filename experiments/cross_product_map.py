# ABOUTME: Bauer's cross-product sum between pairs of LP windows, as a heatmap
# ABOUTME: beside a shuffled null, and swept across window sizes.
"""Do two stretches of the ciphertext follow the same distribution?

Bauer's cross-product sum (Decrypted Secrets) tests exactly that. For two
samples with alphabet counts n_i and m_i it is

    chi(X, Y) = sum_i n_i * m_i

Normalised by |X|*|Y| it estimates sum_i p_i * q_i: if both samples come from
the same distribution it estimates sum_i p_i^2, and if they come from unrelated
distributions it estimates the inner product of two different vectors, which is
smaller. It is the cross-text analogue of the index of coincidence, and the
classical use is deciding whether two ciphertext stretches share an alphabet.

Here it is evaluated for every pair of windows, x and y being the two window
offsets, normalised so 1.0 is the uniform expectation (1/29 unscaled).

Reading the map needs two warnings:

  * The bright diagonal is window overlap. Windows closer together than the
    window length share runes, and a window against itself gives sum_i n_i^2.
    All statistics below use non-overlapping pairs only.
  * The off-diagonal blob texture is also overlap. Neighbouring windows share
    almost all their runes, so the field is smoothed over the window length,
    and smoothed noise looks like structure. Shuffled text produces the same
    texture, which is why the null is rendered beside it.

The calibrated statistic is the spread: localised alphabet structure would make
chi vary more between window pairs than shuffling the same corpus does. The
shuffled null has identical window geometry and identical unigram counts, so it
isolates exactly that.

Usage:
    python3 experiments/cross_product_map.py                  # map + stats
    python3 experiments/cross_product_map.py --sweep           # window sweep
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from lp_corpus import load_clean  # noqa: E402

N_RUNES = 29
SEED = 3301
NULL_DRAWS = 20
GRID_WINDOWS = 700
SWEEP_WINDOWS = [29, 58, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000]


def window_counts(stream: np.ndarray, window: int, stride: int) -> tuple[np.ndarray, np.ndarray]:
    """Per-rune counts of each window, shape (n_windows, 29), plus offsets."""
    onehot = np.zeros((len(stream) + 1, N_RUNES), dtype=np.int32)
    onehot[np.arange(1, len(stream) + 1), stream] = 1
    prefix = np.cumsum(onehot, axis=0)
    starts = np.arange(0, len(stream) - window + 1, stride)
    return prefix[starts + window] - prefix[starts], starts


def cross_product(counts: np.ndarray, window: int) -> np.ndarray:
    """Normalised cross-product sum matrix; 1.0 is the uniform expectation."""
    c = counts.astype(np.float64)
    return (c @ c.T) / (window * window) * N_RUNES


def make_null(kind: str):
    """Surrogate generator. 'shuffle' randomises freely; 'doublet' also holds
    the observed doublet rate, so known doublet suppression is not read as
    signal (`c3301.low_doublet_null`)."""
    if kind == "shuffle":
        def draw(stream: np.ndarray, rng: np.random.Generator) -> np.ndarray:
            out = stream.copy()
            rng.shuffle(out)
            return out
        return draw

    from aldegonde import c3301

    model = c3301.low_doublet_null()

    def draw(stream: np.ndarray, rng: np.random.Generator) -> np.ndarray:
        seed = int(rng.integers(0, 2**32))
        return np.array(model(stream.tolist(), random.Random(seed)), dtype=np.int64)

    return draw


def analyse(
    stream: np.ndarray, window: int, stride: int, rng: np.random.Generator,
    null_kind: str = "shuffle",
) -> dict:
    """Observed and null cross-product spread at one window size."""
    counts, starts = window_counts(stream, window, stride)
    chi = cross_product(counts, window)
    apart = np.abs(starts[:, None] - starts[None, :]) >= window
    obs = chi[apart]

    draw = make_null(null_kind)
    null_sds, null_all = [], None
    for _ in range(NULL_DRAWS):
        ncounts, _ = window_counts(draw(stream, rng), window, stride)
        nchi = cross_product(ncounts, window)
        null_sds.append(nchi[apart].std())
        if null_all is None:
            null_all = nchi
    null_sds = np.array(null_sds)
    return {
        "window": window,
        "stride": stride,
        "n_windows": len(starts),
        "n_pairs": int(apart.sum()),
        "obs_sd": obs.std(),
        "null_sd": null_sds.mean(),
        "null_sd_sd": null_sds.std(),
        "ratio": obs.std() / null_sds.mean(),
        "z": (obs.std() - null_sds.mean()) / null_sds.std(),
        "chi": chi,
        "null_chi": null_all,
        "starts": starts,
        "apart": apart,
    }


def section_of(starts: np.ndarray, window: int) -> np.ndarray:
    """Section index of each window centre, from the $-split of the corpus."""
    import re

    text = (ROOT.parent / "data" / "page0-58.txt").read_text()
    rune = re.compile(r"[ᚠ-᛿]")
    bounds, n = [], 0
    for part in text.split("$")[:10]:
        n += len(rune.findall(part))
        bounds.append(n)
    return np.searchsorted(np.array(bounds), starts + window // 2)


def section_homogeneity(stream: np.ndarray, rng: np.random.Generator) -> None:
    """Do the ten sections share one rune distribution?

    A window-pair contrast (within-section chi minus cross-section chi) is the
    tempting statistic but a bad one here: the sections run from 9 to 3008
    runes, so any null built by permuting the partition is unreliable and large
    windows straddle several sections at once. The contingency test asks the
    question directly, with honest degrees of freedom and no windows involved.
    """
    from scipy import stats

    labels = section_of_positions(stream)
    n_sections = int(labels.max()) + 1
    print(f"section sizes: {[int(v) for v in np.bincount(labels)]}")

    def table(data: np.ndarray) -> np.ndarray:
        out = np.zeros((n_sections, N_RUNES))
        for r in range(N_RUNES):
            out[:, r] = np.bincount(labels[data == r], minlength=n_sections)
        return out

    chi2, p, dof, _ = stats.chi2_contingency(table(stream))
    print("\nchi-square homogeneity of rune frequencies across sections")
    print(f"   chi2 = {chi2:.1f}, dof = {dof}, p = {p:.4f}")
    for kind in ("shuffle", "doublet"):
        draw = make_null(kind)
        vals = np.array(
            [stats.chi2_contingency(table(draw(stream, rng)))[0] for _ in range(300)]
        )
        beat = int((vals >= chi2).sum())
        print(f"   {kind} null: chi2 mean {vals.mean():.1f} sd {vals.std():.1f}"
              f" -> permutation p = {(beat + 1) / 301:.4f}")


def section_of_positions(stream: np.ndarray) -> np.ndarray:
    """Section index of every rune position."""
    import re

    text = (ROOT.parent / "data" / "page0-58.txt").read_text()
    rune = re.compile(r"[ᚠ-᛿]")
    bounds, n = [], 0
    for part in text.split("$")[:10]:
        n += len(rune.findall(part))
        bounds.append(n)
    return np.searchsorted(np.array(bounds), np.arange(len(stream)), side="right")


def render(res: dict, out: str) -> None:
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    chi, null, starts, window = res["chi"], res["null_chi"], res["starts"], res["window"]
    lo = min(chi.min(), null.min())
    hi = max(np.percentile(chi, 99.9), np.percentile(null, 99.9))
    extent = [starts[0], starts[-1] + window, starts[-1] + window, starts[0]]
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)
    for ax, data, name in ((axes[0], chi, "Liber Primus"), (axes[1], null, "shuffled null")):
        im = ax.imshow(
            data, cmap="viridis", extent=extent, vmin=lo, vmax=hi, interpolation="nearest"
        )
        ax.set_title(name, fontsize=11)
        ax.set_xlabel("window offset (runes)")
    axes[0].set_ylabel("window offset (runes)")
    fig.suptitle(
        f"Bauer cross-product sum, {window}-rune windows, stride {res['stride']}\n"
        "bright diagonal = window overlap; blob texture = the same overlap smoothing noise",
        fontsize=11,
    )
    fig.colorbar(im, ax=axes, label="normalised cross-product sum (1.0 = uniform)")
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"\nwrote {out}")


def render_grid(results: list[dict], out: str) -> None:
    """One column per window size, data above its own null."""
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, len(results), figsize=(3.1 * len(results), 6.6))
    for col, res in enumerate(results):
        chi, null, starts, window = res["chi"], res["null_chi"], res["starts"], res["window"]
        lo = min(np.percentile(chi, 0.1), np.percentile(null, 0.1))
        hi = max(np.percentile(chi, 99.9), np.percentile(null, 99.9))
        extent = [starts[0], starts[-1] + window, starts[-1] + window, starts[0]]
        for row, data in ((0, chi), (1, null)):
            ax = axes[row, col]
            ax.imshow(data, cmap="viridis", extent=extent, vmin=lo, vmax=hi,
                      interpolation="nearest")
            ax.set_xticks([])
            ax.set_yticks([])
            if row == 0:
                ax.set_title(f"window {window}\nratio {res['ratio']:.3f}", fontsize=10)
        axes[0, col].set_xlabel("")
    axes[0, 0].set_ylabel("Liber Primus", fontsize=11)
    axes[1, 0].set_ylabel("its own null", fontsize=11)
    fig.suptitle(
        "Bauer cross-product sum across window sizes, each above its doublet-matched null\n"
        "colour scale is per column; no window size separates the data from its null",
        fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(out, dpi=140, bbox_inches="tight")
    print(f"\nwrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=300)
    ap.add_argument("--stride", type=int, default=0, help="default window//30")
    ap.add_argument("--out", default="cross_product_map.png")
    ap.add_argument("--sweep", action="store_true")
    ap.add_argument("--null", choices=["shuffle", "doublet"], default="shuffle")
    ap.add_argument("--grid", action="store_true", help="maps at several window sizes")
    args = ap.parse_args()

    stream = np.array(load_clean()[0], dtype=np.int64)
    rng = np.random.default_rng(SEED)
    print(f"clean corpus: {len(stream)} runes, {NULL_DRAWS} draws of the "
          f"{args.null} null per point\n")

    if args.sweep:
        print("cross-product spread against a shuffled null, by window size")
        print("(spread above the null is what localised alphabet structure looks like)\n")
        print(f"{'window':>7}{'wins':>6}{'pairs':>9}{'obs sd':>10}{'null sd':>10}"
              f"{'ratio':>8}{'z':>7}")
        for window in SWEEP_WINDOWS:
            stride = max(1, window // 4)
            res = analyse(stream, window, stride, rng, args.null)
            print(f"{window:>7}{res['n_windows']:>6}{res['n_pairs']:>9}"
                  f"{res['obs_sd']:>10.5f}{res['null_sd']:>10.5f}"
                  f"{res['ratio']:>8.4f}{res['z']:>+7.2f}")
        print()
        section_homogeneity(stream, rng)
        return

    if args.grid:
        results = []
        for window in (58, 150, 500, 1500):
            # cap the window count so every panel is the same resolution and the
            # matrices stay small; stride 1 at window 58 would be 12899^2
            stride = max(1, (len(stream) - window) // GRID_WINDOWS)
            res = analyse(stream, window, stride, rng, args.null)
            print(f"window {window:>5}: ratio {res['ratio']:.4f}, z {res['z']:+.2f}")
            results.append(res)
        render_grid(results, args.out)
        return

    stride = args.stride or max(1, args.window // 30)
    res = analyse(stream, args.window, stride, rng, args.null)
    print(f"window {args.window}, stride {stride}: {res['n_windows']} windows, "
          f"{res['n_pairs']} non-overlapping pairs")
    print(f"   observed sd {res['obs_sd']:.5f}")
    print(f"   null sd     {res['null_sd']:.5f} +- {res['null_sd_sd']:.5f} "
          f"({NULL_DRAWS} draws)")
    print(f"   spread ratio {res['ratio']:.4f}, z = {res['z']:+.2f}")

    print()
    section_homogeneity(stream, rng)
    render(res, args.out)


if __name__ == "__main__":
    main()
