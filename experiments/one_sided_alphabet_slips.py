# ABOUTME: Recovers ONE arbitrary mixed alphabet under a number-sequence key with key slips,
# ABOUTME: by annealing the alphabet with the slip-tolerant alignment inside the loop.
"""An arbitrary alphabet on one side, a running key, and a key-skipping preventer.

`slip_tolerant_keystream.py` needs the standard rune order and
`any_tableau_keystream.py` a fixed alignment. Between them sits a mixed alphabet under a
key that runs on and slips. For ONE unknown alphabet that cell can be searched:

  cipher side   P = a[C] - K     a is an unknown arrangement of the cipher runes, the
                                 plaintext alphabet is standard (Quagmire II)
  plain side    P = b[C - K]     b is an unknown arrangement of the plaintext runes, the
                                 cipher alphabet is standard (Quagmire I)

Each with the key added or subtracted. The alphabet is annealed by swaps; the objective
is the best slip-tolerant path score (forward slips only, any start term within the
slack) under the author's plaintext unigrams. With one side known, every rune of the
alphabet that is right pays on its own share of the positions, so the gain is linear in
how much of the alphabet is right and the search can climb: on planted keys it recovers
the cipher-side alphabet exactly from random starts.

Two unknown alphabets (Quagmire III and IV) do NOT yield to this. A position pays only
when both of its lookups are right, the gain is quadratic, and a random start sees
nothing: four anneals of 800,000 steps on a planted Quagmire IV stayed at the noise
level (about -370 against a true +730). That cell is covered only for keyword alphabets
(`keyed_alphabet_slips.py`) and for keys that restart (`any_tableau_unit_heads.py`).

What the null keeps and destroys: the same anneal against uniformly random keys keeps
the body, the search and its freedom, and destroys the sequence; it gives the level an
anneal reaches by fitting noise. The controls plant each side under prime(n)-1 with the
key-skipping dodge on the author's words at the body's block lengths.

    python experiments/one_sided_alphabet_slips.py [workers]
"""

from __future__ import annotations

import math
import random
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from numba import njit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

import lp_corpus  # noqa: E402
import lp_plaintext_register  # noqa: E402
from keyed_alphabet_slips import flat_generators  # noqa: E402
from slip_tolerant_keystream import (  # noqa: E402
    SLIP_PENALTY,
    generators,
    plaintext_llr,
)

M = 29
SEED = 20261117
PREFIX = 2000
SLACK = 150
STEPS = {"cipher": 250_000, "plain": 120_000}
T_START, T_END = 12.0, 0.6
SEEDS = 2
NULL_KEYS = 6
SIDES = ("cipher", "plain")
BASES = ("runes", "spaces")
SIGNS = ("K subtracted", "K added")


@njit(cache=True)
def path_score(cipher, base, key, emit, slack, slip_pen):
    """Best path score; emit[c, k] is the emission of cipher rune c under key residue k."""
    n = cipher.shape[0]
    prev = np.zeros(slack)
    cur = np.empty(slack)
    for i in range(n):
        c = cipher[i]
        b = base[i]
        for s in range(slack):
            best = prev[s]
            if s > 0 and prev[s - 1] - slip_pen > best:
                best = prev[s - 1] - slip_pen
            cur[s] = best + emit[c, key[b + s]]
        prev, cur = cur, prev
    m = prev[0]
    for s in range(1, slack):
        if prev[s] > m:
            m = prev[s]
    return m


@njit(cache=True)
def emission(perm, llr, cipher_side):
    out = np.empty((M, M))
    for c in range(M):
        for k in range(M):
            if cipher_side:
                out[c, k] = llr[(perm[c] - k) % M]
            else:
                out[c, k] = llr[perm[(c - k) % M]]
    return out


@njit(cache=True)
def anneal(cipher, base, key, llr, cipher_side, slack, slip_pen, steps, t0, t1, seed):
    """Anneal one alphabet by swaps; returns the best score and its alphabet."""
    np.random.seed(seed)
    perm = np.random.permutation(M)
    cur = path_score(
        cipher, base, key, emission(perm, llr, cipher_side), slack, slip_pen
    )
    best = cur
    best_perm = perm.copy()
    for it in range(steps):
        temp = t0 * (t1 / t0) ** (it / steps)
        x = np.random.randint(M)
        y = np.random.randint(M)
        if x == y:
            continue
        perm[x], perm[y] = perm[y], perm[x]
        new = path_score(
            cipher, base, key, emission(perm, llr, cipher_side), slack, slip_pen
        )
        if new >= cur or np.random.random() < math.exp((new - cur) / temp):
            cur = new
            if cur > best:
                best = cur
                best_perm = perm.copy()
        else:
            perm[x], perm[y] = perm[y], perm[x]
    return best, best_perm


def base_of(word: np.ndarray, kind: str) -> np.ndarray:
    local = np.arange(len(word), dtype=np.int64)
    return local + (word - word[0]) if kind == "spaces" else local


def plant(lens, key, rng, side: str, count: int):
    """One mixed alphabet on the given side under the key, with the key-skipping dodge.

    Returns the cipher stream and the alphabet the anneal should find."""
    arrangement = list(range(M))
    rng.shuffle(arrangement)
    pools: dict[int, list[list[int]]] = {}
    for w in lp_plaintext_register.corpus():
        pools.setdefault(len(w), []).append(w)

    def encipher(r: int, k: int) -> int:
        if side == "cipher":
            return arrangement[(r + k) % M]  # C = A[P + K]
        return (arrangement[r] + k) % M  # C = B[P] + K

    out: list[int] = []
    j, prev = 7, -1
    for L in lens:
        LL = L
        while LL not in pools:
            LL -= 1
        src = rng.choice(pools[LL])
        for r in (src * (L // len(src) + 1))[:L]:
            c = encipher(r, int(key[j]))
            if c == prev:
                j += 1
                c = encipher(r, int(key[j]))
            out.append(c)
            prev = c
            j += 1
            if len(out) == count:
                inverse = np.empty(M, dtype=np.int64)
                inverse[np.array(arrangement)] = np.arange(M)
                return np.array(out, dtype=np.int64), inverse
    msg = "text too short"
    raise RuntimeError(msg)


_W: dict = {}


def _init(texts, word, llr, keys) -> None:
    _W.update(texts=texts, word=word, llr=llr, keys=keys)


def _task(args):
    text, key_name, side, kind, sign, seed = args
    w = _W
    key = w["keys"][key_name]
    if sign == "K added":
        key = (-key) % M
    best, perm = anneal(
        w["texts"][text],
        base_of(w["word"], kind),
        key,
        w["llr"],
        side == "cipher",
        SLACK,
        SLIP_PENALTY,
        STEPS[side],
        T_START,
        T_END,
        seed,
    )
    return args, float(best), perm


def main() -> None:
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    rng = random.Random(SEED)
    nrng = np.random.default_rng(SEED)
    tok = lp_corpus.load_tokenized()
    cipher = np.array(tok.stream, dtype=np.int64)[:PREFIX]
    word = np.array(tok.word, dtype=np.int64)[:PREFIX]
    lens = [len(w) for w in tok.words()]
    llr = plaintext_llr()
    full, _ = flat_generators(
        generators(len(tok.stream) + len(lens) + 910), llr, len(tok.stream)
    )
    need = PREFIX + int(word[-1]) + SLACK + 10
    keys = {k: v[:need].copy() for k, v in full.items()}
    for i in range(NULL_KEYS):
        keys[f"random key {i}"] = nrng.integers(0, M, need)

    texts = {"body": cipher}
    truth = {}
    for side in SIDES:
        texts[f"control, {side}"], truth[side] = plant(
            lens, full["prime(n)"], rng, side, PREFIX
        )

    tasks = []
    for side in SIDES:
        for seed in range(SEEDS):
            tasks.append(
                (f"control, {side}", "prime(n)", side, "runes", "K subtracted", seed)
            )
        for i in range(NULL_KEYS):
            tasks.append(("body", f"random key {i}", side, "runes", "K subtracted", i))
        for g in full:
            for kind in BASES:
                for sign in SIGNS:
                    for seed in range(SEEDS):
                        tasks.append(("body", g, side, kind, sign, seed))
    print(
        f"first {PREFIX} runes, slack {SLACK}; {len(full)} generator classes x "
        f"{len(BASES)} bases x {len(SIGNS)} signs x {len(SIDES)} sides x {SEEDS} seeds; "
        f"{len(tasks)} anneals\n"
    )

    results = []
    with Pool(nproc, initializer=_init, initargs=(texts, word, llr, keys)) as pool:
        for r in pool.imap_unordered(_task, tasks):
            results.append(r)

    control_ok = True
    null: dict[str, np.ndarray] = {}
    for side in SIDES:
        ctrl = [(s, p) for a, s, p in results if a[0] == f"control, {side}"]
        null[side] = np.array(
            [s for a, s, _ in results if a[1].startswith("random key") and a[2] == side]
        )
        solved = sum(
            s > null[side].max() + 10 * null[side].std(ddof=1) for s, _ in ctrl
        )
        agree = max(int((p == truth[side]).sum()) for _, p in ctrl)
        control_ok = control_ok and solved == len(ctrl)
        print(
            f"{side} side: planted key solved in {solved} of {len(ctrl)} anneals, scores "
            f"{', '.join(f'{s:.0f}' for s, _ in ctrl)}, best alphabet {agree}/29 exact; "
            f"random keys on the body {null[side].mean():.0f} +- {null[side].std(ddof=1):.0f}"
        )
    print()
    rows = []
    for a, s, _ in results:
        if a[0] != "body" or a[1].startswith("random key"):
            continue
        z = (s - null[a[2]].mean()) / null[a[2]].std(ddof=1)
        rows.append((z, s, a))
    rows.sort(reverse=True)
    print("the body, best anneals (z against the random-key anneals of the same side):")
    for z, s, a in rows[:6]:
        print(f"  {z:+6.2f}  {s:8.0f}  {a[1]:<30}{a[2]:<8}{a[3]:<8}{a[4]}")
    zs = np.array([r[0] for r in rows])
    ctrl_z = min(
        (s - null[a[2]].mean()) / null[a[2]].std(ddof=1)
        for a, s, _ in results
        if a[0].startswith("control")
    )
    print(
        f"\n{len(rows)} anneals on the body: z mean {zs.mean():+.2f}, max {zs.max():+.2f}; "
        f"the weakest control anneal reads {ctrl_z:+.0f}"
    )
    if not control_ok:
        print("VERDICT: a control anneal failed; a negative here is not safe.")
    elif zs.max() > 10:
        print(
            "VERDICT: an anneal stands far above the noise level. Decrypt along its path."
        )
    else:
        print(
            "VERDICT: no number-sequence key with one arbitrary mixed alphabet, on "
            "either side, aligns the body's opening under key slips."
        )


if __name__ == "__main__":
    main()
