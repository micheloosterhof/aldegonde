# ABOUTME: Tests integer-sequence keystreams under ANY tableau: is the cipher rune
# ABOUTME: statistically dependent on the aligned key residue, whatever the alphabets are?
"""A keystream test that needs no alphabet.

Rows B3 and B5 exclude integer-sequence keystreams "over the standard rune order", and
say so: a mixed alphabet inside the loop does not linearise under subtraction. This test
drops the alphabet altogether. If the cipher is C = T(P, K) for any fixed table T whose
row is chosen by the key residue (Vigenere, Beaufort, the four Quagmires with any keyed
alphabets, any Latin square, any 29 unrelated alphabets), then at the right alignment
the cipher rune and the key residue are dependent: the runes enciphered under one
residue are a monoalphabetic sample of plaintext. So the 29 x 29 contingency table of
(cipher rune, key residue) fails a chi-square test of independence, by about
n x (I_p - 1), near 10,000 on 784 degrees of freedom for the body, where I_p is the
plaintext's normalised index of coincidence. No alphabet enters.

Three key labels, each over every generator, three bases and three layouts
(`slip_tolerant_keystream`), and every start term up to STARTS:

  K               the residue itself:              C = T(P, K)
  C[-1] + K       with ciphertext feedback:        C = T(P, C_prev + K)
  C[-1] - K                                        C = T(P, C_prev - K)

The alignment is fixed, so this covers a cipher with no preventer, a tuned relation, and
a preventer that inserts a null (the null consumes a key term like any rune). A
preventer that skips a key term breaks the alignment every 36 runes and is the business
of `slip_tolerant_keystream.py`, which needs the standard rune order.

What the null keeps and destroys: the z of a cell is its chi-square against its own
degrees of freedom; the family is priced by the same scan on surrogate bodies from
`c3301.low_doublet_null`, which keep rune counts and the doublet rate and destroy the
order. The control plants a Quagmire IV (two random alphabets) under prime(n)-1 on the
author's words at the body's block lengths, starting 123 terms in.

    python experiments/any_tableau_keystream.py
"""

from __future__ import annotations

import random
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import lp_corpus  # noqa: E402
import lp_plaintext_register  # noqa: E402
from slip_tolerant_keystream import BASES, base_index, generators, units  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.maths import permutation  # noqa: E402

M = 29
SEED = 20261111
STARTS = 2000
SURROGATES = 5
LABELS = ("K", "C[-1] + K", "C[-1] - K")
PLANT_START = 123


def independence_z(cipher: np.ndarray, label: np.ndarray) -> float:
    """Chi-square of independence of (cipher rune, label), as a z on its own df."""
    table = np.bincount(cipher * M + label, minlength=M * M).reshape(M, M).astype(float)
    rows = table.sum(axis=1)
    cols = table.sum(axis=0)
    keep_r, keep_c = rows > 0, cols > 0
    table = table[keep_r][:, keep_c]
    expected = np.outer(rows[keep_r], cols[keep_c]) / table.sum()
    chi = ((table - expected) ** 2 / expected).sum()
    df = (keep_r.sum() - 1) * (keep_c.sum() - 1)
    return float((chi - df) / np.sqrt(2 * df)) if df > 0 else 0.0


def scan(cipher, bases, prevs, gens, starts=STARTS):
    """Best z over starts for every (generator, layout, base, label).

    bases[layout, kind] is the key index of every rune before the start term is added;
    prevs[layout] is the previous cipher rune inside the unit, or -1 at a unit start."""
    out = {}
    for (layout, kind), base in bases.items():
        prev = prevs[layout]
        inner = prev >= 0
        c_in, p_in = cipher[inner], prev[inner]
        for g, key in gens.items():
            best = dict.fromkeys(LABELS, (-1000000000.0, 0))
            for start in range(starts):
                k = key[base + start]
                z = independence_z(cipher, k)
                if z > best["K"][0]:
                    best["K"] = (z, start)
                ki = k[inner]
                z = independence_z(c_in, (p_in + ki) % M)
                if z > best["C[-1] + K"][0]:
                    best["C[-1] + K"] = (z, start)
                z = independence_z(c_in, (p_in - ki) % M)
                if z > best["C[-1] - K"][0]:
                    best["C[-1] - K"] = (z, start)
            for lab in LABELS:
                out[g, layout, kind, lab] = best[lab]
    return out


def structure(tok):
    """Key index before the start term, and the previous rune, for every layout."""
    word = np.array(tok.word, dtype=np.int64)
    n = len(word)
    bases, prevs = {}, {}
    for layout, unit_list in units(tok).items():
        first = np.zeros(n, dtype=bool)
        for idx in unit_list:
            first[idx[0]] = True
        prevs[layout] = first
        for kind in BASES:
            base = np.empty(n, dtype=np.int64)
            for idx in unit_list:
                base[idx] = base_index(word, idx, kind)
            bases[layout, kind] = base
    return bases, prevs


def previous(cipher: np.ndarray, first: np.ndarray) -> np.ndarray:
    prev = np.empty(len(cipher), dtype=np.int64)
    prev[1:] = cipher[:-1]
    prev[first] = -1
    prev[0] = -1
    return prev


def plant(lens, key, rng) -> np.ndarray:
    """Quagmire IV under the key: C = A[(B[P] + K) mod 29], two random alphabets."""
    a = permutation.random_permutation(M, rng)
    b = permutation.random_permutation(M, rng)
    pools: dict[int, list[list[int]]] = {}
    for w in lp_plaintext_register.corpus():
        pools.setdefault(len(w), []).append(w)
    out, j = [], PLANT_START
    for L in lens:
        LL = L
        while LL not in pools:
            LL -= 1
        w = rng.choice(pools[LL])
        for r in (w * (L // len(w) + 1))[:L]:
            out.append(a[(b[r] + int(key[j])) % M])
            j += 1
    return np.array(out, dtype=np.int64)


_W: dict = {}


def _init(bases, firsts, gens) -> None:
    _W.update(bases=bases, firsts=firsts, gens=gens)


def _run(text):
    prevs = {layout: previous(text, _W["firsts"][layout]) for layout in _W["firsts"]}
    return scan(text, _W["bases"], prevs, _W["gens"])


def main() -> None:
    rng = random.Random(SEED)
    tok = lp_corpus.load_tokenized()
    cipher = np.array(tok.stream, dtype=np.int64)
    n = len(cipher)
    lens = [len(w) for w in tok.words()]
    gens = generators(n + len(lens) + STARTS + 10)
    bases, firsts = structure(tok)
    cells = len(gens) * len(bases) * len(LABELS)
    print(
        f"body: {n:,} runes; {len(gens)} generators x {len(bases)} layout-base cases x "
        f"{len(LABELS)} labels = {cells} cells, each the best of {STARTS} start terms\n"
    )

    # control
    planted = plant(lens, gens["prime(n)-1"], rng)
    one = {k: v for k, v in bases.items() if k == ("runs on", "runes")}
    res = scan(
        planted,
        one,
        {"runs on": previous(planted, firsts["runs on"])},
        {"prime(n)-1": gens["prime(n)-1"], "totient": gens["totient"]},
        starts=300,
    )
    z_true, start_true = res["prime(n)-1", "runs on", "runes", "K"]
    z_wrong = res["totient", "runs on", "runes", "K"][0]
    control_ok = z_true > 20 and start_true == PLANT_START
    print(
        f"control: Quagmire IV with two random alphabets under prime(n)-1 from term "
        f"{PLANT_START}: z {z_true:+.1f} at start {start_true}; the wrong generator's "
        f"best of 300 starts {z_wrong:+.2f}\n"
    )

    null_model = c3301.low_doublet_null()
    texts = [cipher] + [
        np.array(null_model(tok.stream, rng), dtype=np.int64) for _ in range(SURROGATES)
    ]
    with Pool(
        min(4, len(texts)), initializer=_init, initargs=(bases, firsts, gens)
    ) as pool:
        results = pool.map(_run, texts)
    body = results[0]
    null_max = []
    null_all = []
    for sur in results[1:]:
        vals = [v[0] for v in sur.values()]
        null_max.append(max(vals))
        null_all.extend(vals)
    null_max_arr = np.array(null_max)
    vals = np.array([v[0] for v in body.values()])
    top = sorted(body.items(), key=lambda kv: -kv[1][0])[:6]
    print("the body, best cells (z of the best start):")
    for (g, layout, kind, lab), (z, start) in top:
        print(f"  {z:+6.2f}  {g:<30}{layout:<9}{kind:<8}{lab:<10} start {start}")
    print(
        f"\nbody: best {vals.max():+.2f}, cells mean {vals.mean():+.2f} sd {vals.std():.2f}"
    )
    print(
        f"surrogate bodies: best {null_max_arr.mean():+.2f} +- {null_max_arr.std(ddof=1):.2f} "
        f"over {SURROGATES} (range {null_max_arr.min():+.2f} to {null_max_arr.max():+.2f}), "
        f"cells mean {np.mean(null_all):+.2f} sd {np.std(null_all):.2f}"
    )
    beaten = int((null_max_arr >= vals.max()).sum())
    if not control_ok:
        print("VERDICT: the control failed; the negative means nothing.")
    elif vals.max() > null_max_arr.max() + 3 * null_max_arr.std(ddof=1):
        print("VERDICT: a cell stands clear of the surrogates. Solve its alphabets.")
    else:
        print(
            f"VERDICT: no generator selects the body's alphabet at any start term to "
            f"{STARTS}, under any tableau, with or without one rune of ciphertext "
            f"feedback: the body's best cell is reached by {beaten} of {SURROGATES} "
            f"surrogate bodies, and a true key reads z {z_true:+.0f}."
        )


if __name__ == "__main__":
    main()
