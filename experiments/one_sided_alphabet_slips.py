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

Each with the key added or subtracted; a free alphabet absorbs the reflection, so the two
signs cover the Beaufort senses too. The alphabet is searched by swaps; the objective is
the best slip-tolerant path score (forward slips only, any start term within the slack)
under the author's plaintext unigrams. With one side known, every rune of the alphabet
that is right pays on its own share of the positions, so the gain is linear in how much
of the alphabet is right and the search can climb.

The search is a wait, not a descent. On a planted key it sits at the noise level until
it falls into the true alphabet, after a number of steps that varies from seed to seed
(cooling from 12 to 0.6 over 250,000 steps solved half of the cipher-side plants, over
400,000 steps three quarters). So the search holds one temperature, hot enough to melt
the noise fits (a swap there costs 5 to 15 nats) and cold enough to keep the true
alphabet (a swap there costs about 60), and cools only at the end. The controls measure
how often one search of this length finds the planted alphabet, and the verdict is
refused unless the chance that every search of a cell misses a true key is small.

Two unknown alphabets (Quagmire III and IV) do NOT yield to this. A position pays only
when both of its lookups are right, the gain is quadratic, and a random start sees
nothing: four anneals of 800,000 steps on a planted Quagmire IV stayed at the noise
level (about -370 against a true +730). That cell is covered only for keyword alphabets
(`keyed_alphabet_slips.py`) and for keys that restart (`any_tableau_unit_heads.py`).

What the null keeps and destroys: the same search under the same generator on surrogate
bodies (`c3301.low_doublet_null`) keeps the rune counts, the doublet rate, the key and
the search's freedom, and destroys the order of the text. It has to be matched to the
generator. The first version of this script used random keys as the null and read the
key n on the plain side at -312 against -412 +- 11, +8.9 sigma; the same key on six
surrogate bodies reads -324 +- 26. A key that steps by one lets a fitted plaintext
alphabet reach some 80 nats higher on any text than a key with scattered residues does
(prime(n) on the same surrogates: -400 +- 7). The cause was not pursued.

The controls plant each side under prime(n)-1 with the key-skipping dodge on the
author's words at the body's block lengths. On the plain side the search ends above
the planted alphabet's own score with only some runes in their planted places: unigrams
cannot order plaintext runes of similar frequency, and do not need to.

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

from aldegonde import c3301  # noqa: E402

M = 29
SEED = 20261117
PREFIX = 2000
SLACK = 150
STEPS = {"cipher": 400_000, "plain": 150_000}
T_SEARCH = 8.0  # held while searching: melts the noise fits, keeps the true alphabet
T_END = 0.6
QUENCH = 0.15  # last share of the steps, cooling from T_SEARCH to T_END
SEEDS = 2  # searches of every cell of the body
CONTROL_SEEDS = 12  # searches of each planted control, to measure the success rate
NULL_SURROGATES = 4  # surrogate bodies per generator and side, one per base and sign
MISS_ALLOWED = 0.05  # chance that every search of a cell misses a true key
SIDES = ("cipher", "plain")
BASES = ("runes", "spaces")
SIGNS = ("K subtracted", "K added")


@njit(cache=True, fastmath=True)
def path_score(cipher, base, ke, rows, slack, slip_pen):
    """Best path score. ke[rows[c], j] is the emission of cipher rune c under key term j.

    The emissions are laid out along the key so that the inner loop reads three
    contiguous rows and vectorizes; a table lookup per cell is five times slower.
    """
    n = cipher.shape[0]
    dp = np.zeros((2, slack), dtype=np.float32)
    a = 0
    for i in range(n):
        prev = dp[a]
        cur = dp[1 - a]
        row = ke[rows[cipher[i]], base[i] : base[i] + slack]
        cur[0] = prev[0] + row[0]
        for s in range(1, slack):
            cur[s] = max(prev[s], prev[s - 1] - slip_pen) + row[s]
        a = 1 - a
    return dp[a].max()


@njit(cache=True)
def key_emissions(key, llr, perm, cipher_side):
    """The emission table along the key, and for the plain side its cells by residue.

    Cipher side: row v is the emission of a cipher rune standing at v, so the alphabet
    is the choice of row and the table never changes. Plain side: row c is cipher rune
    c, the cell holds the plaintext rune at residue C - K, and `order[starts[r] :
    starts[r + 1]]` are the cells at residue r, which a swap rewrites.
    """
    width = key.shape[0]
    ke = np.empty((M, width), dtype=np.float32)
    order = np.empty(M * width, dtype=np.int64)
    starts = np.zeros(M + 1, dtype=np.int64)
    if cipher_side:
        for v in range(M):
            for j in range(width):
                ke[v, j] = llr[(v - key[j]) % M]
        return ke, order, starts
    for c in range(M):
        for j in range(width):
            starts[(c - key[j]) % M + 1] += 1
    for r in range(M):
        starts[r + 1] += starts[r]
    fill = starts[:M].copy()
    for c in range(M):
        for j in range(width):
            r = (c - key[j]) % M
            order[fill[r]] = c * width + j
            fill[r] += 1
            ke[c, j] = llr[perm[r]]
    return ke, order, starts


@njit(cache=True)
def alphabet_score(cipher, base, key, llr, perm, cipher_side, slack, slip_pen):
    """Path score of one given alphabet."""
    ke, _, _ = key_emissions(key, llr, perm, cipher_side)
    rows = perm if cipher_side else np.arange(M)
    return path_score(cipher, base, ke, rows, slack, np.float32(slip_pen))


@njit(cache=True)
def anneal(
    cipher,
    base,
    key,
    llr,
    cipher_side,
    slack,
    slip_pen,
    steps,
    t_search,
    t_end,
    quench,
    seed,
):
    """Search one alphabet by swaps at t_search, cooling over the last `quench` share.

    Returns the best score and its alphabet."""
    np.random.seed(seed)
    perm = np.random.permutation(M)
    ke, order, starts = key_emissions(key, llr, perm, cipher_side)
    flat = ke.ravel()
    rows = perm if cipher_side else np.arange(M)
    pen = np.float32(slip_pen)
    cur = path_score(cipher, base, ke, rows, slack, pen)
    best = cur
    best_perm = perm.copy()
    hold = int(steps * (1.0 - quench))
    for it in range(steps):
        temp = t_search
        if it > hold:
            temp = t_search * (t_end / t_search) ** ((it - hold) / (steps - hold))
        x = np.random.randint(M)
        y = np.random.randint(M)
        if x == y:
            continue
        perm[x], perm[y] = perm[y], perm[x]
        if not cipher_side:
            for r in (x, y):
                v = llr[perm[r]]
                for t in range(starts[r], starts[r + 1]):
                    flat[order[t]] = v
        new = path_score(cipher, base, ke, rows, slack, pen)
        if new >= cur or np.random.random() < math.exp((new - cur) / temp):
            cur = new
            if cur > best:
                best = cur
                best_perm = perm.copy()
        else:
            perm[x], perm[y] = perm[y], perm[x]
            if not cipher_side:
                for r in (x, y):
                    v = llr[perm[r]]
                    for t in range(starts[r], starts[r + 1]):
                        flat[order[t]] = v
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
        T_SEARCH,
        T_END,
        QUENCH,
        seed,
    )
    return args, float(best), perm


def upper_tail(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2.0))


def main() -> None:
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    rng = random.Random(SEED)
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

    texts = {"body": cipher}
    truth, truth_score = {}, {}
    for side in SIDES:
        name = f"control, {side}"
        texts[name], truth[side] = plant(lens, full["prime(n)"], rng, side, PREFIX)
        truth_score[side] = float(
            alphabet_score(
                texts[name],
                base_of(word, "runes"),
                keys["prime(n)"],
                llr,
                truth[side],
                side == "cipher",
                SLACK,
                SLIP_PENALTY,
            )
        )
    null_model = c3301.low_doublet_null()
    cells = [(kind, sign) for sign in SIGNS for kind in BASES]

    tasks = []
    for side in SIDES:
        for seed in range(CONTROL_SEEDS):
            tasks.append(
                (f"control, {side}", "prime(n)", side, "runes", "K subtracted", seed)
            )
        for g in full:
            for kind in BASES:
                for sign in SIGNS:
                    for seed in range(SEEDS):
                        tasks.append(("body", g, side, kind, sign, seed))
    for gi, g in enumerate(full):
        for i in range(NULL_SURROGATES):
            name = f"surrogate {gi}.{i}"
            texts[name] = np.array(null_model(tok.stream, rng), dtype=np.int64)[:PREFIX]
            kind, sign = cells[i % len(cells)]
            for side in SIDES:
                tasks.append((name, g, side, kind, sign, i))
    on_body = sum(t[0] == "body" for t in tasks)
    print(
        f"first {PREFIX} runes, slack {SLACK}; {len(full)} generator classes x "
        f"{len(BASES)} bases x {len(SIGNS)} signs x {len(SIDES)} sides x {SEEDS} seeds = "
        f"{on_body} searches of the body, "
        f"{len(full) * NULL_SURROGATES * len(SIDES)} of surrogate bodies, "
        f"{CONTROL_SEEDS * len(SIDES)} of the controls\n"
    )

    results = []
    with Pool(nproc, initializer=_init, initargs=(texts, word, llr, keys)) as pool:
        for r in pool.imap_unordered(_task, tasks, chunksize=1):
            results.append(r)

    null: dict[tuple[str, str], list[float]] = {}
    for a, s, _ in results:
        if a[0].startswith("surrogate"):
            null.setdefault((a[2], a[1]), []).append(s)
    spread = {
        side: math.sqrt(
            float(
                np.mean(
                    [np.var(v, ddof=1) for (sd, _), v in null.items() if sd == side]
                )
            )
        )
        for side in SIDES
    }
    level = {
        side: float(np.mean([np.mean(v) for (sd, _), v in null.items() if sd == side]))
        for side in SIDES
    }
    # a search has found a key when it is nearer the planted alphabet's score than the
    # surrogates' level
    solved_above = {side: (truth_score[side] + level[side]) / 2 for side in SIDES}

    miss = {}
    for side in SIDES:
        ctrl = [(s, p) for a, s, p in results if a[0] == f"control, {side}"]
        solved = sum(s > solved_above[side] for s, _ in ctrl)
        agree = max(int((p == truth[side]).sum()) for _, p in ctrl)
        # Laplace's rule, so that a clean sweep of the controls is not read as certainty
        miss[side] = (1 - (solved + 1) / (len(ctrl) + 2)) ** SEEDS
        lo = min(s for s, _ in ctrl)
        hi = max(s for s, _ in ctrl)
        print(
            f"{side} side: the planted alphabet scores {truth_score[side]:.0f}; found in "
            f"{solved} of {len(ctrl)} searches (scores {lo:.0f} to {hi:.0f}, best "
            f"alphabet {agree}/29 exact); surrogate bodies {level[side]:.0f}, sd "
            f"{spread[side]:.0f} within a generator; chance that {SEEDS} searches both "
            f"miss a true key at most {miss[side]:.3f}"
        )
    print()

    rows = []
    for a, s, _ in results:
        if a[0] != "body":
            continue
        ref = null[a[2], a[1]]
        z = (s - np.mean(ref)) / (spread[a[2]] * math.sqrt(1 + 1 / len(ref)))
        rows.append((float(z), s, float(np.mean(ref)), a))
    rows.sort(key=lambda r: -r[0])
    print("the body, best searches (z against the same generator on surrogate bodies):")
    for z, s, ref, a in rows[:6]:
        print(
            f"  {z:+6.2f}  {s:6.0f} against {ref:6.0f}  {a[1]:<30}{a[2]:<8}{a[3]:<8}{a[4]}"
        )
    print("\nthe body, highest raw scores:")
    for z, s, ref, a in sorted(rows, key=lambda r: -r[1])[:4]:
        print(
            f"  {z:+6.2f}  {s:6.0f} against {ref:6.0f}  {a[1]:<30}{a[2]:<8}{a[3]:<8}{a[4]}"
        )
    zs = np.array([r[0] for r in rows])
    family = 1 - (1 - upper_tail(float(zs.max()))) ** len(zs)
    found = [r for r in rows if r[1] > solved_above[r[3][2]]]
    best = {side: max(r[1] for r in rows if r[3][2] == side) for side in SIDES}
    print(
        f"\n{len(rows)} searches of the body: z mean {zs.mean():+.2f}, sd {zs.std():.2f}, "
        f"max {zs.max():+.2f} (family P {family:.2f}); best scores "
        + ", ".join(
            f"{best[side]:.0f} on the {side} side where a planted key reads "
            f"{truth_score[side]:.0f}"
            for side in SIDES
        )
    )
    if max(miss.values()) > MISS_ALLOWED:
        print(
            f"VERDICT: a true key could be missed with chance {max(miss.values()):.2f}; "
            f"a negative here is not safe."
        )
    elif found:
        z, s, _, a = max(found, key=lambda r: r[1])
        print(
            f"VERDICT: {len(found)} searches reach a planted key's level; the best is "
            f"{a[1]}, {a[2]} side, {a[3]}, {a[4]} at {s:.0f}. Decrypt along its path."
        )
    elif family < 0.01:
        z, s, ref, a = rows[0]
        print(
            f"VERDICT: no search reaches a planted key's level, but {a[1]} ({a[2]} side, "
            f"{a[3]}, {a[4]}) stands {z:+.1f} above its own surrogates. Extend it to the "
            f"whole body."
        )
    else:
        print(
            f"VERDICT: no number-sequence key with one arbitrary mixed alphabet, on "
            f"either side, aligns the body's opening under key slips: every search "
            f"stays at the level of the same key on surrogate bodies, and a true key "
            f"would be missed with chance at most {max(miss.values()):.3f}."
        )


if __name__ == "__main__":
    main()
