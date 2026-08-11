# ABOUTME: Within-word coincidence profile d1-d10 with a word-length permutation
# ABOUTME: null, showing the period-5 phase structure (echo at d5, suppression at d1/d6).
"""The within-word coincidence profile is organized by phase (d mod 5), not
raw distance. Under a period-5 substitution c[j]=base(g^(j mod 5)(p[j])):

  d mod 5 = 0 (d=5,10): same phase -> plaintext coincidence leaks (echo)
  d mod 5 = 1 (d=1,6):  g^1 diagonal -> doublet suppression, BELOW flat
  d mod 5 = 2,3,4:      g^2/3/4 diagonals -> intermediate

The null keeps the published rune stream byte-for-byte intact and only
shuffles each section's word-length sequence before re-cutting into words --
isolating whether the real word boundaries know where the coincidences are.

Result (clean corpus, sections 0-9, 10000 permutations):
  d5 excess p=0.0010 (the echo), d6 deficit p=0.0155 (the suppression
  recurring 5 later). Past d6 the samples collapse (d7=713 pairs down to
  d10=88), so d7-d10 are noise.
"""

from __future__ import annotations

import random

from aldegonde import c3301

BOUNDARY_CHARS = frozenset(
    c3301.MARK_CHARS + "&%" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS
)

ALPH = c3301.CICADA_ALPHABET
RUNES = set(ALPH)
R2I = {r: i for i, r in enumerate(ALPH)}
CLEAN = 12956  # sections 0-9
DMAX = 10
NPERM = 10000
SEED = 3301


def load_sections() -> list[tuple[list[int], list[int]]]:
    """Per section: (rune stream in order, word-length sequence). Words flow
    across line wraps; sections split on `$`; capped at the clean corpus."""
    with open("data/page0-58.txt") as f:
        text = f.read()
    sections: list[tuple[list[int], list[int]]] = []
    sr: list[int] = []
    sl: list[int] = []
    cur = total = 0
    for ch in text:
        if total >= CLEAN:
            break
        if ch in RUNES:
            sr.append(R2I[ch])
            cur += 1
            total += 1
        elif ch in BOUNDARY_CHARS:
            if cur:
                sl.append(cur)
                cur = 0
        elif ch in "/\n":
            pass
        elif ch == "$":
            if cur:
                sl.append(cur)
                cur = 0
            if sr:
                sections.append((sr, sl))
            sr, sl = [], []
    if cur:
        sl.append(cur)
    if sr:
        sections.append((sr, sl))
    return sections


def cut(runes: list[int], lengths: list[int]) -> list[list[int]]:
    out = []
    p = 0
    for length in lengths:
        out.append(runes[p : p + length])
        p += length
    return out


def counts(secs: list[tuple[list[int], list[int]]]) -> list[int]:
    c = [0] * (DMAX + 1)
    for runes, lengths in secs:
        for w in cut(runes, lengths):
            for d in range(1, DMAX + 1):
                for i in range(len(w) - d):
                    c[d] += w[i] == w[i + d]
    return c


def main() -> None:
    sections = load_sections()
    obs = counts(sections)
    rng = random.Random(SEED)
    null: list[list[int]] = [[] for _ in range(DMAX + 1)]
    for _ in range(NPERM):
        secs = []
        for r, l in sections:
            ll = l[:]
            rng.shuffle(ll)
            secs.append((r, ll))
        c = counts(secs)
        for d in range(1, DMAX + 1):
            null[d].append(c[d])
    print(" d | obs | null mean +/- sd | z     | p       | phase")
    for d in range(1, DMAX + 1):
        nd = null[d]
        mu = sum(nd) / NPERM
        sd = (sum((x - mu) ** 2 for x in nd) / NPERM) ** 0.5
        z = (obs[d] - mu) / sd if sd else 0.0
        p_ge = sum(x >= obs[d] for x in nd) / NPERM
        p_le = sum(x <= obs[d] for x in nd) / NPERM
        p = min(p_ge, p_le)
        tail = "excess" if obs[d] > mu else "deficit"
        print(
            f"{d:2d} | {obs[d]:3d} | {mu:5.1f} +/- {sd:4.1f} | {z:+.2f} | "
            f"{p:.4f} | {d % 5} ({tail})"
        )


if __name__ == "__main__":
    main()
