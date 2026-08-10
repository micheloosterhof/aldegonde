#!/usr/bin/env python3
# ABOUTME: The within-word lag-5 coincidence excess in the clean Liber Primus is
# ABOUTME: carried disproportionately by one rune, S (Sigel); this reproduces it.
"""Which runes carry the within-word distance-5 coincidence excess?

The within-word d=5 coincidence (within-word-d5-coincidence.md) is 102 matches
vs a ~76 null (+26 excess). This asks whether that excess is rune-agnostic or
concentrated. It is concentrated: the rune S (Sigel) echoes at distance 5
eleven times against a null of ~1.7 -- p ~ 2e-4, Bonferroni-clean across 29
runes -- and alone accounts for roughly a third of the whole excess. The
effect is specific to distance 5 (d=1..4,6 are normal) and to within-word
pairs (cross-word S at d=5 is at chance).

Null: each word's exact rune multiset and length are held fixed and only the
arrangement is randomized. For a word of length L holding k copies of rune r,
the expected number of r-r pairs at distance d is (L-d)*k*(k-1)/(L*(L-1)) --
exact, so no simulation is needed for the mean; the p-value is the Poisson
upper tail at that mean (rare-event approximation, matched by a within-word
shuffle to two decimals).

Corpus and tokenization as in within_word_d5.py (clean sections 0-9).
"""

from __future__ import annotations

from collections import Counter

from scipy.stats import poisson

from aldegonde import c3301

M = 29
R2I = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
RUNES = set(R2I)
WORD_BOUNDARIES = set(c3301.MARK_CHARS + "&%" + c3301.NUMERAL_CHARS)
EN = c3301.CICADA_ENGLISH_ALPHABET
S = EN.index("S")


def parse_clean_words(path: str = "data/page0-58.txt") -> list[list[int]]:
    """Flat word list (clean sections 0-9), each word a list of rune indices."""
    with open(path) as f:
        text = f.read()
    sec: list[list[list[int]]] = [[]]
    cur: list[int] = []
    for ch in text:
        if ch in RUNES:
            cur.append(R2I[ch])
        elif ch == "$":
            if cur:
                sec[-1].append(cur)
                cur = []
            sec.append([])
        elif ch in WORD_BOUNDARIES and cur:
            sec[-1].append(cur)
            cur = []
    if cur:
        sec[-1].append(cur)
    return [w for s in [x for x in sec if x][:10] for w in s]


def null_mean(words: list[list[int]], rune: int, d: int) -> float:
    """Expected within-word d-pairs of `rune` under random per-word arrangement."""
    total = 0.0
    for w in words:
        length = len(w)
        if length <= d:
            continue
        k = w.count(rune)
        if k >= 2:
            total += (length - d) * k * (k - 1) / (length * (length - 1))
    return total


def observed(words: list[list[int]], rune: int, d: int) -> int:
    """Observed within-word d-pairs of `rune`."""
    return sum(1 for w in words for i in range(len(w) - d) if w[i] == w[i + d] == rune)


def observed_any(words: list[list[int]], d: int) -> tuple[int, float]:
    """Observed and null-mean within-word d-pairs of any rune."""
    obs = sum(1 for w in words for i in range(len(w) - d) if w[i] == w[i + d])
    exp = sum(null_mean(words, r, d) for r in range(M))
    return obs, exp


def main() -> None:
    words = parse_clean_words()

    print("S echo within words, by distance (obs vs random-arrangement null):")
    print("  d   obs  null   Poisson p(>=obs)")
    for d in range(1, 9):
        obs = observed(words, S, d)
        exp = null_mean(words, S, d)
        p = float(poisson.sf(obs - 1, exp))
        flag = "  <<<" if p < 0.006 else ""
        print(f"  {d}   {obs:3d}  {exp:4.2f}  {p:.4f}{flag}")

    print("\nEvery rune at d=5 (Bonferroni threshold p < 0.05/29 = 0.0017):")
    print("  rune  obs  null   Poisson p")
    rows = []
    for r in range(M):
        obs = observed(words, r, 5)
        exp = null_mean(words, r, 5)
        p = float(poisson.sf(obs - 1, exp)) if obs else 1.0
        rows.append((obs, exp, p, r))
    for obs, exp, p, r in sorted(rows, reverse=True)[:8]:
        flag = "  <<<" if p < 0.0017 else ("  <" if p < 0.05 else "")
        print(f"  {EN[r]:>3}   {obs:3d}  {exp:4.2f}  {p:.4f}{flag}")

    tot_obs, tot_exp = observed_any(words, 5)
    s_obs, s_exp = observed(words, S, 5), null_mean(words, S, 5)
    print(
        f"\ntotal within-word d=5 excess: {tot_obs} - {tot_exp:.1f} = "
        f"{tot_obs - tot_exp:.1f}"
    )
    print(
        f"S share of the excess: ({s_obs} - {s_exp:.1f}) / "
        f"({tot_obs} - {tot_exp:.1f}) = {(s_obs - s_exp) / (tot_obs - tot_exp):.0%}"
    )

    # within vs cross-word at d=5
    stream = [x for w in words for x in w]
    wid: list[int] = []
    for wi, w in enumerate(words):
        wid += [wi] * len(w)
    fS = Counter(stream)[S] / len(stream)
    win = sum(
        1
        for i in range(len(stream) - 5)
        if wid[i] == wid[i + 5] and stream[i] == stream[i + 5] == S
    )
    cro = sum(
        1
        for i in range(len(stream) - 5)
        if wid[i] != wid[i + 5] and stream[i] == stream[i + 5] == S
    )
    cp = sum(1 for i in range(len(stream) - 5) if wid[i] != wid[i + 5])
    print(
        f"\nd=5 S echo: within-word {win} (null {s_exp:.1f}) | "
        f"cross-word {cro} (chance {cp * fS * fS:.1f})"
    )

    print("\nthe S-echo words:")
    for w in words:
        hits = [k for k in range(len(w) - 5) if w[k] == w[k + 5] == S]
        if hits:
            runes = "".join(c3301.CICADA_ALPHABET[x] for x in w)
            eng = "·".join(EN[x] for x in w)
            print(f"  {runes}   {eng}   S@{hits}")


if __name__ == "__main__":
    main()
