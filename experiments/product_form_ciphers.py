#!/usr/bin/env python3
# ABOUTME: Simulates product-form/interpolation GF(29) autokeys and runs the joint
# ABOUTME: two-tap split test that closes the deterministic f(P,C[n-1],C[n-5]) class.
"""Test product-form / interpolation ciphers against the LP fingerprint.

Proposed mechanism family: deterministic algebra over GF(29) in which
zero factors created by plaintext repeats generate the lag-5 and
doublet structure "for free", e.g.

    F1:  C(n) = C(n-5)(P(n)-P(n-1)) + C(n-1)(P(n)-P(n-5))
    F2:  the subtraction variant  C(n-5)(..) - C(n-1)(..)
    F3:  with constants  a*C(n-5)(..) + b*C(n-1)(..) + g
    F4:  multiplicative  C(n-5)^(P(n)-P(n-1)) * C(n-1)^(P(n)-P(n-5))
         (over the multiplicative group; 0 mapped to 29 -> use exponents
         mod 28 on a generator representation)
    F5:  linear interpolation through (P(n-1),C(n-1)),(P(n-5),C(n-5))
         evaluated at P(n):
         C(n) = C(n-1) + (P(n)-P(n-1)) * (C(n-5)-C(n-1))
                          * inv(P(n-5)-P(n-1))
         -- the natural algebraic form that DOES yield literal copies:
         P(n)=P(n-5) => C(n)=C(n-5), P(n)=P(n-1) => C(n)=C(n-1).
         (fallback to fresh random when P(n-1)=P(n-5))

Each is run on bag-of-words runeglish plaintext (correct English word
frequencies) and fingerprinted on the statistics that define the LP:
unigram chi2, nIoC, doublet rate, triplet count, lag-5 mono rate,
d1/d4 pair counts, nonzero repeated lag-5 deltas at separations 1/4
(value-literality), and the cross-word vs in-word usage of plaintext
lag-5 repeats. LP targets in the header row.

Also runs the JOINT TWO-TAP SPLIT TEST on the real corpus: group C(n)
by the pair (C(n-1), C(n-5)) -- 841 groups. For ANY deterministic
C(n) = f(P(n), C(n-1), C(n-5)) with f injective in P(n), each group is
a substitution image of the plaintext, so the mean group nIoC must
approach plaintext IoC (~1.7). Random text gives ~1.0. This closes the
whole two-tap deterministic class in one number (the earlier split
tests conditioned on a single history symbol only).

Usage: python experiments/product_form_ciphers.py
"""

from __future__ import annotations

import numpy as np

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
DATA = "data/page0-58.txt"

INV = [0] + [pow(x, MOD - 2, MOD) for x in range(1, MOD)]


def transliterate(word: str) -> list[int] | None:
    w = word.upper()
    if not w.isalpha():
        return None
    for a, b in (("K", "C"), ("Q", "C"), ("V", "U"), ("Z", "S")):
        w = w.replace(a, b)
    digraphs = {
        "TH": 2,
        "EO": 12,
        "NG": 21,
        "OE": 22,
        "AE": 25,
        "IA": 27,
        "IO": 27,
        "EA": 28,
    }
    singles = {
        "F": 0,
        "U": 1,
        "O": 3,
        "R": 4,
        "C": 5,
        "G": 6,
        "W": 7,
        "H": 8,
        "N": 9,
        "I": 10,
        "J": 11,
        "P": 13,
        "X": 14,
        "S": 15,
        "T": 16,
        "B": 17,
        "E": 18,
        "M": 19,
        "L": 20,
        "D": 23,
        "A": 24,
        "Y": 26,
    }
    out: list[int] = []
    i = 0
    while i < len(w):
        if w[i : i + 2] in digraphs:
            out.append(digraphs[w[i : i + 2]])
            i += 2
        elif w[i] in singles:
            out.append(singles[w[i]])
            i += 1
        else:
            return None
    return out


def plaintext(n_runes: int, rng) -> tuple[list[int], list[int]]:
    from wordfreq import top_n_list, word_frequency

    lex, weights = [], []
    for eng in top_n_list("en", 30000):
        r = transliterate(eng)
        if r:
            lex.append(r)
            weights.append(word_frequency(eng, "en"))
    w = np.array(weights)
    w /= w.sum()
    p: list[int] = []
    word_of: list[int] = []
    wi = 0
    while len(p) < n_runes:
        word = lex[rng.choice(len(lex), p=w)]
        p.extend(word)
        word_of.extend([wi] * len(word))
        wi += 1
    return p, word_of


GEN = 2  # primitive root mod 29
LOG = {pow(GEN, e, MOD): e for e in range(MOD - 1)}


def encrypt(p: list[int], form: str, rng) -> list[int]:
    n = len(p)
    c = [int(rng.integers(MOD)) for _ in range(5)]
    for i in range(5, n):
        d1 = (p[i] - p[i - 1]) % MOD
        d5 = (p[i] - p[i - 5]) % MOD
        a, b = c[i - 5], c[i - 1]
        if form == "F1":
            v = (a * d1 + b * d5) % MOD
        elif form == "F2":
            v = (a * d1 - b * d5) % MOD
        elif form == "F3":
            v = (7 * a * d1 + 11 * b * d5 + 13) % MOD
        elif form == "F4":
            # multiplicative: work on nonzero residues via discrete log
            aa = a if a else 1
            bb = b if b else 1
            e = (LOG[aa] * d1 + LOG[bb] * d5) % (MOD - 1)
            v = pow(GEN, e, MOD)
        elif form == "F5":
            den = (p[i - 5] - p[i - 1]) % MOD
            if den == 0:
                v = int(rng.integers(MOD))
            else:
                v = (b + d1 * (a - b) * INV[den]) % MOD
        else:
            raise ValueError(form)
        c.append(v)
    return c


def fingerprint(c: list[int], p: list[int], word_of: list[int]) -> dict:
    ca = np.array(c)
    n = len(ca)
    uni = np.bincount(ca, minlength=MOD)
    chi = float(((uni - n / MOD) ** 2 / (n / MOD)).sum())
    _, counts = np.unique(ca, return_counts=True)
    nioc = float((counts * (counts - 1)).sum() / (n * (n - 1)) * MOD)
    dbl = float((ca[1:] == ca[:-1]).mean())
    tri = int(((ca[2:] == ca[1:-1]) & (ca[1:-1] == ca[:-2])).sum())
    m = ca[:-5] == ca[5:]
    mono = float(m.mean())
    d1p = int((m[:-1] & m[1:]).sum())
    d4p = int((m[:-4] & m[4:]).sum())
    delta = (ca[5:] - ca[:-5]) % MOD
    eq1 = delta[:-1] == delta[1:]
    nz1 = int((eq1 & (delta[:-1] != 0)).sum())
    # usage of plaintext lag-5 repeats -> ciphertext copies, in/cross word
    pa = np.array(p[:n])
    prep = pa[:-5] == pa[5:]
    wa = np.array(word_of[:n])
    inw = wa[:-5] == wa[5:]
    use_in = float(m[prep & inw].mean()) if (prep & inw).any() else 0.0
    use_x = float(m[prep & ~inw].mean()) if (prep & ~inw).any() else 0.0
    return {
        "uni_chi2": chi,
        "nIoC": nioc,
        "dbl%": 100 * dbl,
        "triplets": tri,
        "mono5%": 100 * mono,
        "d1": d1p,
        "d4": d4p,
        "nz_rep_sep1": nz1,
        "use_in%": 100 * use_in,
        "use_x%": 100 * use_x,
    }


def joint_split_test() -> None:
    """Mean group nIoC of C(n) | (C(n-1), C(n-5)) on the REAL corpus."""
    with open(DATA) as f:
        raw = f.read()
    pages = [[R2I[ch] for ch in pg if ch in R2I] for pg in raw.split("%")]
    pages = [pg for pg in pages if pg][:-2]
    c = [x for pg in pages for x in pg]
    groups: dict[tuple[int, int], list[int]] = {}
    for i in range(5, len(c)):
        groups.setdefault((c[i - 1], c[i - 5]), []).append(c[i])
    iocs = []
    weights = []
    for g in groups.values():
        k = len(g)
        if k < 5:
            continue
        cnt = np.bincount(np.array(g), minlength=MOD)
        iocs.append(float((cnt * (cnt - 1)).sum() / (k * (k - 1)) * MOD))
        weights.append(k)
    mean = float(np.average(iocs, weights=weights))
    print(
        f"\nJOINT TWO-TAP SPLIT TEST on the real LP: mean nIoC of "
        f"C(n) | (C(n-1), C(n-5)) over {len(iocs)} groups (>=5 members) "
        f"= {mean:.3f}"
    )
    print(
        "  any deterministic C(n)=f(P(n),C(n-1),C(n-5)) injective in "
        "P(n) forces ~1.7 (plaintext IoC); random forces ~1.0"
    )


def main() -> None:
    rng = np.random.default_rng(20260707)
    n_runes = 260_000
    p, word_of = plaintext(n_runes, rng)

    lp = {
        "uni_chi2": 25.9,
        "nIoC": 1.000,
        "dbl%": 0.664,
        "triplets": 0,
        "mono5%": 3.70,
        "d1": "29/13k",
        "d4": "28/13k",
        "nz_rep_sep1": "chance",
        "use_in%": "~25 (marks)",
        "use_x%": "~10 (marks)",
    }
    print(
        f"{'form':>5} {'uni_chi2':>9} {'nIoC':>6} {'dbl%':>6} "
        f"{'tripl':>6} {'mono5%':>7} {'d1':>6} {'d4':>6} "
        f"{'nzrep1':>7} {'use_in%':>8} {'use_x%':>7}"
    )
    print(
        f"{'LP':>5} {lp['uni_chi2']:>9} {lp['nIoC']:>6} {lp['dbl%']:>6} "
        f"{lp['triplets']:>6} {lp['mono5%']:>7} {lp['d1']:>6} "
        f"{lp['d4']:>6} {lp['nz_rep_sep1']:>7} {lp['use_in%']:>8} "
        f"{lp['use_x%']:>7}"
    )
    for form in ("F1", "F2", "F3", "F4", "F5"):
        c = encrypt(p, form, rng)
        fp = fingerprint(c, p, word_of)
        # scale d1/d4/nz counts to per-13k for comparability
        scale = 12956 / n_runes
        print(
            f"{form:>5} {fp['uni_chi2']:>9.0f} {fp['nIoC']:>6.3f} "
            f"{fp['dbl%']:>6.2f} {fp['triplets']:>6} "
            f"{fp['mono5%']:>7.2f} {fp['d1'] * scale:>6.1f} "
            f"{fp['d4'] * scale:>6.1f} {fp['nz_rep_sep1'] * scale:>7.1f} "
            f"{fp['use_in%']:>8.1f} {fp['use_x%']:>7.1f}"
        )
    print(
        "\n(nzrep1 = nonzero repeated lag-5 deltas at separation 1 per "
        "13k runes; LP is at chance ~430 with zero-value pairs at 29. "
        "use_in/use_x = fraction of plaintext lag-5 repeats that became "
        "ciphertext copies, in-word / cross-word.)"
    )

    joint_split_test()


if __name__ == "__main__":
    main()
