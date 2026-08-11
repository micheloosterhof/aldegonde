# ABOUTME: Three small open follow-ups: d5 hit-word clustering, the close-gap
# ABOUTME: prediction of the hold model, and the delta-1 nonzero-flatness recheck.
"""Follow-up checks left open in the observation files.

A. Hit-word clustering (within-word-d5-coincidence.md, Predictions): if a
   per-word key state drives the d5 echo, words sharing state should
   cluster — test pairs of hit words within a word-index window against a
   label permutation over words of the same length.
B. Close-gap prediction (doublet-spacing-poisson.md / stay-slot-hold.md):
   the hold model exposes 1/5 of plaintext doublets independently, so
   close ciphertext doublet pairs arise from close plaintext doublet pairs
   at ~(1/5)^2. Predicted count of gaps <= 5 from the author's register vs
   the observed zero.
C. Delta-1 nonzero flatness (cryptodiagnostics-page0-58.md): the nonzero
   first-difference distribution scored p = 0.026 pre-decontamination;
   recheck on the clean corpus.
"""

from __future__ import annotations

import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.stats import chisquare

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lp_corpus import load_clean
from solved_plaintext_running_key import recover_plaintext, solved_segments

M = 29


def main() -> None:
    rng = random.Random(3301)
    stream, wid = load_clean()
    n = len(stream)

    # word structure
    words: dict[int, list[int]] = {}
    for i, w in enumerate(wid):
        words.setdefault(w, []).append(stream[i])
    wlist = sorted(words)
    lengths = {w: len(words[w]) for w in wlist}

    # --- A. hit-word clustering ---
    hits = [
        w
        for w in wlist
        if any(words[w][j] == words[w][j + 5] for j in range(len(words[w]) - 5))
    ]
    print(f"A. hit words: {len(hits)} of {len(wlist)}")
    for window in (5, 10, 25):

        def close_pairs(hs, window=window):
            hs = sorted(hs)
            return sum(
                1
                for a in range(len(hs))
                for b in range(a + 1, len(hs))
                if hs[b] - hs[a] <= window
            )

        obs = close_pairs(hits)
        bylen: dict[int, list[int]] = {}
        for w in wlist:
            bylen.setdefault(lengths[w], []).append(w)
        null = []
        for _ in range(2000):
            fake = []
            need = Counter(lengths[w] for w in hits)
            for L, k in need.items():
                fake.extend(rng.sample(bylen[L], k))
            null.append(close_pairs(fake))
        mu, sd = float(np.mean(null)), float(np.std(null))
        print(
            f"   pairs within {window:>2} words: obs {obs} "
            f"vs null {mu:.1f} ± {sd:.1f} (z = {(obs - mu) / sd:+.2f})"
        )

    # --- B. close-gap prediction under the 1-in-5 hold ---
    plaintext = recover_plaintext(solved_segments())
    pd = [i for i in range(len(plaintext) - 1) if plaintext[i] == plaintext[i + 1]]
    close_pt = sum(
        1 for a in range(len(pd)) for b in range(a + 1, len(pd)) if pd[b] - pd[a] <= 5
    )
    scale = n / len(plaintext)
    pred = close_pt * scale * (1 / 5) ** 2
    dbl = [i for i in range(n - 1) if stream[i] == stream[i + 1]]
    close_ct = sum(
        1
        for a in range(len(dbl))
        for b in range(a + 1, len(dbl))
        if dbl[b] - dbl[a] <= 5
    )
    print(
        f"\nB. plaintext doublet pairs with gap <= 5 in the register: "
        f"{close_pt} per {len(plaintext)} runes"
    )
    print(
        f"   hold-model predicted close ciphertext doublet pairs: "
        f"{pred:.2f}; observed {close_ct} "
        f"(Poisson P(0) = {np.exp(-pred):.2f})"
    )

    # --- C. delta-1 nonzero flatness, clean corpus ---
    delta = [(stream[i + 1] - stream[i]) % M for i in range(n - 1)]
    counts = np.bincount(delta, minlength=M)
    nz = counts[1:]
    stat, p = chisquare(nz)
    print(
        f"\nC. delta-1 nonzero flatness (clean): chi2 = {stat:.1f} "
        f"(27 df), p = {p:.3f}; doublet bin (delta=0) = {counts[0]}"
    )


if __name__ == "__main__":
    main()
