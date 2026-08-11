# ABOUTME: Comprehensive battery on the long words (>= 5 runes) of the clean
# ABOUTME: corpus — the only words that exercise g^3, g^4 and the g^5=id echo —
# ABOUTME: scored throughout against doublet-aware surrogates.
"""Long words (>= 5 runes): what do they carry?

1,124 words (38% of the corpus) reach length 5; 806 reach length 6 and
so can hold a distance-5 pair. Under the length-clocked walk a word's
rune at position j is base_w(g^(j mod 5)(p_j)), so long words are where
the model's internals are visible:

  A. census and doublet rate by length class (suppression must be
     length-independent).
  B. within-word distance profile d1..d10 restricted to long words.
  C. PHASE-CLASS TEST — the walk's sharpest within-word prediction:
     positions sharing j mod 5 share an alphabet, so ALL same-phase
     pairs (distance 5, 10, ...) should leak plaintext coincidence while
     different-phase pairs sit at chance. Aggregating over distances is
     more powerful than any single distance cell.
  D. internal repeat structure: repeated runes, repeated bigrams and
     trigrams inside a single word.
  E. cross-word collisions among long words: shared 2/3/4-rune prefixes
     and suffixes, and the longest common substring census — a
     base-collision would show here far more sharply than in short words.
  F. positional rune uniformity (first/second/.../last).

Null throughout: aldegonde.stats.nulls.doublet_shuffle at the observed
rate, re-segmented into the real word-length structure.
"""

from __future__ import annotations

import math
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT / "src"))

from aldegonde.stats.nulls import doublet_shuffle  # noqa: E402, I001
from lp_corpus import load_clean  # noqa: E402

MINLEN = 5
TRIALS = 400


def segment(stream, lens):
    out, pos = [], 0
    for L in lens:
        out.append(tuple(stream[pos : pos + L]))
        pos += L
    return out


def measure(words):
    """All battery statistics for one word list."""
    lw = [w for w in words if len(w) >= MINLEN]
    st: dict[str, float] = {}

    # B. distance profile
    m: Counter = Counter()
    s: Counter = Counter()
    for w in lw:
        L = len(w)
        for j in range(L):
            for d in range(1, min(11, L - j)):
                s[d] += 1
                m[d] += w[j] == w[j + d]
    for d in range(1, 11):
        st[f"d{d}"] = m[d] / s[d] if s[d] else float("nan")

    # C. phase-class aggregate (distance divisible by 5 vs not), d >= 2
    same = same_n = diff = diff_n = 0
    for w in lw:
        L = len(w)
        for j in range(L):
            for k in range(j + 2, L):
                if (k - j) % 5 == 0:
                    same_n += 1
                    same += w[j] == w[k]
                else:
                    diff_n += 1
                    diff += w[j] == w[k]
    st["phase_same"] = same / same_n if same_n else float("nan")
    st["phase_diff"] = diff / diff_n if diff_n else float("nan")
    st["phase_gap"] = st["phase_same"] - st["phase_diff"]

    # D. internal repeats
    rep_rune = sum(len(w) - len(set(w)) for w in lw)
    bigr = trigr = 0
    for w in lw:
        bs = [w[i : i + 2] for i in range(len(w) - 1)]
        ts = [w[i : i + 3] for i in range(len(w) - 2)]
        bigr += len(bs) - len(set(bs))
        trigr += len(ts) - len(set(ts))
    st["rep_rune"] = rep_rune
    st["rep_bigram"] = bigr
    st["rep_trigram"] = trigr

    # E. cross-word collisions among long words
    for k in (2, 3, 4):
        pre = Counter(w[:k] for w in lw)
        suf = Counter(w[-k:] for w in lw)
        st[f"pre{k}"] = sum(v * (v - 1) // 2 for v in pre.values())
        st[f"suf{k}"] = sum(v * (v - 1) // 2 for v in suf.values())
    # shared internal substrings of length 4 and 5 across different words
    for k in (4, 5):
        seen: Counter = Counter()
        for _i, w in enumerate(lw):
            for j in range(len(w) - k + 1):
                seen[w[j : j + k]] += 1
        st[f"sub{k}"] = sum(v * (v - 1) // 2 for v in seen.values())
    return st


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    d: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        d.setdefault(w, []).append(stream[i])
    words = [tuple(d[k]) for k in sorted(d)]
    lens = [len(w) for w in words]
    lw = [w for w in words if len(w) >= MINLEN]

    print(
        f"A. census: {len(lw)} words of length >= {MINLEN} "
        f"({len(lw) / len(words) * 100:.1f}% of {len(words)}), "
        f"{sum(len(w) for w in lw)} runes"
    )
    hist = Counter(len(w) for w in lw)
    print("   lengths: " + "  ".join(f"{L}:{hist[L]}" for L in sorted(hist)))
    print("   doublet rate by length class (suppression must be flat):")
    for lo, hi, label in ((1, 4, "1-4"), (5, 7, "5-7"), (8, 20, "8+")):
        sel = [w for w in words if lo <= len(w) <= hi]
        adj = sum(len(w) - 1 for w in sel)
        dbl = sum(1 for w in sel for i in range(len(w) - 1) if w[i] == w[i + 1])
        se = math.sqrt(dbl) if dbl else 1
        print(
            f"     len {label:>3}: {dbl:>3}/{adj:>5} = {dbl / adj:.4f} ± {se / adj:.4f}"
        )

    obs = measure(words)
    rate = sum(1 for i in range(len(stream) - 1) if stream[i] == stream[i + 1]) / (
        len(stream) - 1
    )
    model = doublet_shuffle(rate)
    null: dict[str, list[float]] = {k: [] for k in obs}
    for _ in range(TRIALS):
        surr = measure(segment(list(model(stream, rng)), lens))
        for k, v in surr.items():
            null[k].append(v)

    def line(key, label, fmt="{:.4f}"):
        arr = np.array(null[key])
        mu, sd = arr.mean(), arr.std()
        z = (obs[key] - mu) / sd if sd else float("nan")
        p = float((arr >= obs[key]).mean())
        print(
            f"   {label:<34} obs {fmt.format(obs[key]):>8}  "
            f"null {fmt.format(mu):>8} ± {fmt.format(sd):>7}  "
            f"z {z:+5.2f}  p(hi) {p:.3f}"
        )

    print(f"\nB. within-word distance profile (long words only, {TRIALS} surrogates):")
    for dd in range(1, 11):
        line(f"d{dd}", f"d = {dd}")

    print("\nC. phase-class test (the walk's sharpest within-word prediction):")
    line("phase_same", "same phase (d = 5, 10)")
    line("phase_diff", "different phase (all other d >= 2)")
    line("phase_gap", "gap (same - different)")

    print("\nD. internal repeat structure:")
    line("rep_rune", "repeated runes within a word", "{:.0f}")
    line("rep_bigram", "repeated bigrams within a word", "{:.0f}")
    line("rep_trigram", "repeated trigrams within a word", "{:.0f}")

    print("\nE. cross-word collisions among long words:")
    for k in (2, 3, 4):
        line(f"pre{k}", f"shared {k}-rune prefixes (pairs)", "{:.0f}")
        line(f"suf{k}", f"shared {k}-rune suffixes (pairs)", "{:.0f}")
    for k in (4, 5):
        line(f"sub{k}", f"shared {k}-rune substrings (pairs)", "{:.0f}")

    print("\nF. positional rune uniformity (long words):")
    for pos, label in (
        (0, "first"),
        (1, "second"),
        (2, "third"),
        (-1, "last"),
        (-2, "second-to-last"),
    ):
        c = Counter(w[pos] for w in lw)
        e = len(lw) / 29
        chi = sum((c[r] - e) ** 2 / e for r in range(29))
        print(
            f"   {label:<16} chi2 {chi:6.1f} (28 df, p "
            f"{'<0.05' if chi > 41.3 else '>0.05'})"
        )


if __name__ == "__main__":
    main()
