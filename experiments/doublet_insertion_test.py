#!/usr/bin/env python3
"""Doublets: insertion (chaff) vs occupying-event (marker-class) test.

If doublets are inserted dittographs (removable chaff over a strictly
doublet-free cipher stream), each insertion inflates its host word by one
rune: doublet-containing words should average ~1 rune longer than the
length-weighted baseline. If doublets are events occupying a plaintext
position (a rare plaintext rune/bigram, or the keystream hitting the
forbidden zero step), word lengths are unchanged.
"""

import math

import numpy as np

from anomaly_scan import parse


def main() -> None:
    stream, seps, words, lines, pages, sections = parse()
    nplain = len(sections[-1])
    n = len(stream) - nplain
    C = stream[:-nplain]
    total = 0
    cw = []
    for w in words:
        if total + len(w) <= n:
            cw.append(w)
        total += len(w)
    lens = [len(w) for w in cw]
    rune_word = []
    for i, L in enumerate(lens):
        rune_word.extend([i] * L)

    dwords = set()
    cross = 0
    for i in range(n - 1):
        if C[i] == C[i + 1]:
            if rune_word[i] == rune_word[i + 1]:
                dwords.add(rune_word[i])
            else:
                cross += 1
    dl = np.array([lens[i] for i in dwords], float)
    print(f"within-word doublets in {len(dwords)} words; cross-word: {cross}")

    La = np.array(lens, float)
    p_len = La / La.sum()  # host word chosen proportional to its length
    obs = dl.mean()
    se = dl.std() / math.sqrt(len(dl))
    mean_marker = float((La * p_len).sum())
    mean_ins = mean_marker + 1.0
    print(f"observed doublet-word mean length: {obs:.2f} (se {se:.2f})")
    print(f"occupying-event prediction: {mean_marker:.2f} -> "
          f"z={(obs - mean_marker) / se:+.2f}")
    print(f"insertion prediction:       {mean_ins:.2f} -> "
          f"z={(obs - mean_ins) / se:+.2f}")

    rng = np.random.default_rng(4)
    for model, shift in (("occupying-event", 0.0), ("insertion", 1.0)):
        mm = []
        for _ in range(4000):
            pick = rng.choice(len(La), size=len(dl), replace=False, p=p_len)
            mm.append(La[pick].mean() + shift)
        mm = np.array(mm)
        p = (np.sum(np.abs(mm - mm.mean()) >= abs(obs - mm.mean())) + 1) / (len(mm) + 1)
        print(f"{model}: MC {mm.mean():.2f}±{mm.std():.2f}, two-sided p={p:.4f}")


if __name__ == "__main__":
    main()
