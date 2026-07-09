#!/usr/bin/env python3
"""Battery 22: the two-layer decomposition, demonstrated and attacked.

Claim under test: the LP = (structureless keystream) + (two aware
rules). The doublet deficit and the lag-5 copies are made by the RULES;
the stream itself carries no interaction at distances 1 or 5. Two
complementary demonstrations:

A. EXCISION. Delete the ~103 copy-target glyphs of the paired events
   (the nulls-branch decorations) and re-measure the lag-5 channel on
   the residual 99.2% of the corpus. If the phenomenon lives in those
   glyphs, every lag-5 statistic must collapse to chance.

B. ANNIHILATOR SCAN. If instead the KEYSTREAM had built-in distance-1/
   distance-5 generation structure — any linear recurrence
   K[i] = a*K[i-j1] + b*K[i-j2] + c over GF(29), including the lagged
   Fibonacci taps {1,5} — then the matching ciphertext combination

       T[i] = C[i] - a*C[i-j1] - b*C[i-j2]
            = P[i] - a*P[i-j1] - b*P[i-j2] + c

   annihilates the key and exposes a plaintext combination, whose
   distribution is non-uniform. Scan ALL (a, b) in GF(29)^2 over the
   lag sets (1,5),(2,5),(3,5),(4,5),(1,2),(1,3),(1,4),(1,6): 6,728
   chi-square tests on the real corpus. Power is calibrated by running
   the identical scan on a simulated lagged-Fibonacci-keyed cipher over
   bag-of-words runeglish at the same length.

Usage: python experiments/lp_battery22.py
"""

from __future__ import annotations

import json

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"
CATALOG = "hypotheses/lag5-event-catalog.json"

LAG_SETS = [(1, 5), (2, 5), (3, 5), (4, 5), (1, 2), (1, 3), (1, 4), (1, 6)]


def load_clean() -> np.ndarray:
    with open(DATA) as f:
        raw = f.read()
    pages = [[R2I[ch] for ch in p if ch in R2I] for p in raw.split("%")]
    pages = [p for p in pages if p][:-2]
    return np.array([x for p in pages for x in p], dtype=np.int64)


# ------------------------------------------------------------- part A
def lag5_stats(c: np.ndarray) -> dict:
    m = c[:-5] == c[5:]
    return {"mono": int(m.sum()), "sites": len(m),
            "d1": int((m[:-1] & m[1:]).sum()),
            "d4": int((m[:-4] & m[4:]).sum())}


def part_a(c: np.ndarray) -> None:
    with open(CATALOG) as f:
        cat = json.load(f)
    targets: set[int] = set()
    for i in cat["d1_events"]:
        targets.update((i + 5, i + 6))
    for i in cat["d4_events"]:
        targets.update((i + 5, i + 9))
    keep = np.array([i not in targets for i in range(len(c))])
    resid = c[keep]
    before = lag5_stats(c)
    after = lag5_stats(resid)
    print("=== A. excision of the paired-event copy targets "
          f"({len(targets)} glyphs, {len(targets)/len(c):.2%}) ===")
    for label, s in (("full corpus", before), ("residual", after)):
        exp = s["sites"] / MOD
        zm = (s["mono"] - exp) / (exp * (1 - 1 / MOD)) ** 0.5
        ed = (s["sites"] - 1) / MOD ** 2
        zd1 = (s["d1"] - ed) / ed ** 0.5
        zd4 = (s["d4"] - ed) / ed ** 0.5
        print(f"  {label:>12}: mono {s['mono']:>4} (z={zm:+5.2f})  "
              f"d1 {s['d1']:>3} (z={zd1:+5.2f})  "
              f"d4 {s['d4']:>3} (z={zd4:+5.2f})")


# ------------------------------------------------------------- part B
def annihilator_scan(c: np.ndarray, label: str,
                     report_threshold: float) -> float:
    n = len(c)
    worst = 0.0
    worst_id = None
    n_tests = 0
    for j1, j2 in LAG_SETS:
        x0 = c[j2:]
        x1 = c[j2 - j1:n - j1]
        x2 = c[: n - j2]
        m = len(x0)
        exp = m / MOD
        for a in range(1, MOD):
            t_base = (x0 - a * x1) % MOD
            for b in range(1, MOD):
                t = (t_base - b * x2) % MOD
                counts = np.bincount(t, minlength=MOD)
                chi = float(((counts - exp) ** 2 / exp).sum())
                n_tests += 1
                if chi > worst:
                    worst, worst_id = chi, (j1, j2, a, b)
    print(f"  {label}: {n_tests} combos, max chi2 = {worst:.1f} at "
          f"lags {worst_id[:2]} coeffs (a={worst_id[2]}, b={worst_id[3]}) "
          f"[threshold ~{report_threshold:.0f}]")
    return worst


def simulate_lagged_fib(n: int, rng) -> np.ndarray:
    """Cipher with K[i] = K[i-1] + K[i-5] mod 29 over runeglish."""
    from wordfreq import top_n_list, word_frequency

    def transliterate(word: str):
        w = word.upper()
        if not w.isalpha():
            return None
        for x, y in (("K", "C"), ("Q", "C"), ("V", "U"), ("Z", "S")):
            w = w.replace(x, y)
        digraphs = {"TH": 2, "EO": 12, "NG": 21, "OE": 22, "AE": 25,
                    "IA": 27, "IO": 27, "EA": 28}
        singles = {"F": 0, "U": 1, "O": 3, "R": 4, "C": 5, "G": 6,
                   "W": 7, "H": 8, "N": 9, "I": 10, "J": 11, "P": 13,
                   "X": 14, "S": 15, "T": 16, "B": 17, "E": 18, "M": 19,
                   "L": 20, "D": 23, "A": 24, "Y": 26}
        out = []
        i = 0
        while i < len(w):
            if w[i:i + 2] in digraphs:
                out.append(digraphs[w[i:i + 2]])
                i += 2
            elif w[i] in singles:
                out.append(singles[w[i]])
                i += 1
            else:
                return None
        return out

    lex, wts = [], []
    for eng in top_n_list("en", 30000):
        r = transliterate(eng)
        if r:
            lex.append(r)
            wts.append(word_frequency(eng, "en"))
    wts = np.array(wts)
    wts /= wts.sum()
    p: list[int] = []
    while len(p) < n:
        p.extend(lex[rng.choice(len(lex), p=wts)])
    p = np.array(p[:n], dtype=np.int64)
    k = np.empty(n, dtype=np.int64)
    k[:5] = rng.integers(0, MOD, 5)
    for i in range(5, n):
        k[i] = (k[i - 1] + k[i - 5]) % MOD
    return (p + k) % MOD


def main() -> None:
    c = load_clean()
    part_a(c)

    print("\n=== B. linear annihilator scan "
          "(kills any low-order linear-recurrence keystream) ===")
    # threshold: max of ~6728 chi2(28) draws
    from scipy.stats import chi2 as chi2_dist
    thresh = chi2_dist.isf(1 / 6728, 28)
    annihilator_scan(c, "LP corpus", thresh)

    rng = np.random.default_rng(20260707)
    sim = simulate_lagged_fib(len(c), rng)
    print("  power calibration (simulated K[i]=K[i-1]+K[i-5] cipher, "
          "same length):")
    annihilator_scan(sim, "lagged-fib sim", thresh)
    # the specific annihilating combo for the simulated recurrence:
    t = (sim[5:] - sim[4:-1] - sim[:-5]) % MOD
    counts = np.bincount(t, minlength=MOD)
    exp = len(t) / MOD
    chi = float(((counts - exp) ** 2 / exp).sum())
    print(f"  sim's true annihilator (lags (1,5), a=1, b=1): "
          f"chi2 = {chi:.1f}")


if __name__ == "__main__":
    main()
