# ABOUTME: Aligns integer-sequence keystreams to the body with a Viterbi path that lets the
# ABOUTME: key skip or stall at any rune, so a doublet dodge that eats key cannot hide one.
"""A keystream test that survives any number of key slips.

`window_sequence_sweep.py` (row B5) slides 57-rune windows and allows at most 200
interrupts over the body, sized on the AN END page's one interrupt in 85 runes. A doublet
preventer that re-enciphers with the NEXT key element changes that arithmetic: a would-be
repeat arises once in 29 runes, so the key slips about 360 times, a 57-rune window is
slip-free one time in five, and the running index leaves the 200 allowance half way
through the body. A space that consumes a key element slips 2,927 times. Neither case was
tested.

Here the alignment is a path. For rune i the key index is base(i) + s, and s may stay,
rise by one (the key skipped an element) or fall by one (the key stalled, as it does on
the author's plaintext F). Each move costs a fixed penalty. The emission is the
log-likelihood ratio of the decrypted rune under the author's own plaintext unigrams
against uniform. The best path is found by dynamic programming for every generator, 29
alphabet offsets and three senses, in three layouts and three bases:

  runs on    one path over the whole body, any start term up to the slack
  sections   the key restarts at each section, one path per section
  pages      the key restarts at each page

  runes      base(i) = i: a rune consumes a key element
  spaces     base(i) = i + words before i: a space consumes one too
  ordinal    base(i) = word number + position in the word: every word starts one term
             after the previous word started

The null is matched to the generator. A path with a thousand free moves scores a
structured key differently from a random one whatever the text (prime(n)-1 reads about
150 nats above a random key on a SHUFFLED body), so each generator is scored on the body
and on surrogate bodies from `c3301.low_doublet_null`, which keep the rune counts and
the doublet rate and destroy the order. The surrogates keep the layout, the search and
the key; they destroy only the alignment between this text and this key.

The control plants prime(n)-1 on the author's words at the body's block lengths under a
dodge that skips a key element on every would-be repeat, with and without the spaces
eating key, and reads it back through the same search.

    python experiments/slip_tolerant_keystream.py [workers]
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
import sequence_key_sweep  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.stats import z_score  # noqa: E402

M = 29
SEED = 20261110
SLIP_PENALTY = math.log(36.0)  # one dodged would-be repeat per 36 runes
STALL_PENALTY = math.log(85.0)  # the AN END page's interrupt rate
SLACK = {"runs on": 900, "sections": 400, "pages": 150}
BASES = ("runes", "spaces", "ordinal")
SURROGATES = 12
SENSES = ("P = C - K", "P = K - C", "P = C + K")
CONSTANT_DIGITS = ("pi", "e", "golden ratio", "sqrt 2")


@njit(cache=True)
def best_paths(cipher, base, key, tab_minus, tab_plus, slack, slip_pen, stall_pen):
    """Best path score for each of the 87 (sense, offset) pairs.

    tab_minus[t] holds the 58 emissions of senses 0 and 1 for t = (c - k) mod 29, and
    tab_plus[t] the 29 of sense 2 for t = (c + k) mod 29."""
    n = cipher.shape[0]
    q_all = 3 * M
    prev = np.zeros((slack, q_all), dtype=np.float32)
    cur = np.empty((slack, q_all), dtype=np.float32)
    for i in range(n):
        c = cipher[i]
        b = base[i]
        for s in range(slack):
            k = key[b + s]
            tm = (c - k) % M
            tp = (c + k) % M
            for q in range(q_all):
                best = prev[s, q]
                if s > 0:
                    v = prev[s - 1, q] - slip_pen
                    if v > best:
                        best = v
                if s + 1 < slack:
                    v = prev[s + 1, q] - stall_pen
                    if v > best:
                        best = v
                if q < 2 * M:
                    cur[s, q] = best + tab_minus[tm, q]
                else:
                    cur[s, q] = best + tab_plus[tp, q - 2 * M]
        prev, cur = cur, prev
    out = np.empty(q_all, dtype=np.float64)
    for q in range(q_all):
        m = prev[0, q]
        for s in range(1, slack):
            if prev[s, q] > m:
                m = prev[s, q]
        out[q] = m
    return out


def emission_tables(llr: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    t = np.arange(M)
    minus = np.empty((M, 2 * M), dtype=np.float32)
    plus = np.empty((M, M), dtype=np.float32)
    for off in range(M):
        minus[:, off] = llr[(t - off) % M]  # P = C - K - off
        minus[:, M + off] = llr[(off - t) % M]  # P = K - C + off
        plus[:, off] = llr[(t + off) % M]  # P = C + K + off
    return minus, plus


def plaintext_llr() -> np.ndarray:
    """ln p(rune) - ln(1/29) on the author's solved pages, add-half smoothed."""
    counts = np.full(M, 0.5)
    for w in lp_plaintext_register.corpus():
        for r in w:
            counts[r] += 1
    return np.log(counts / counts.sum() * M)


def base_index(word: np.ndarray, idx: np.ndarray, kind: str) -> np.ndarray:
    """Key index of each rune of one unit before any slip."""
    local = np.arange(len(idx), dtype=np.int64)
    if kind == "runes":
        return local
    w = word[idx] - word[idx[0]]
    if kind == "spaces":
        return local + w
    start = np.zeros(len(idx), dtype=np.int64)  # ordinal: word number + position
    for i in range(1, len(idx)):
        start[i] = 0 if w[i] != w[i - 1] else start[i - 1] + 1
    return w + start


def units(tok) -> dict[str, list[np.ndarray]]:
    n = len(tok.stream)
    section = np.array(tok.section)
    page = np.array(tok.page)
    return {
        "runs on": [np.arange(n)],
        "sections": [np.flatnonzero(section == s) for s in np.unique(section)],
        "pages": [np.flatnonzero(page == p) for p in np.unique(page)],
    }


def score(cipher, word, unit_list, key, tabs, slack, kind) -> np.ndarray:
    """Summed best-path scores over the units, for the 87 (sense, offset) pairs."""
    total = np.zeros(3 * M)
    for idx in unit_list:
        total += best_paths(
            cipher[idx],
            base_index(word, idx, kind),
            key,
            tabs[0],
            tabs[1],
            slack,
            SLIP_PENALTY,
            STALL_PENALTY,
        )
    return total


def constant_digits(name: str, count: int) -> np.ndarray:
    """The first `count` base-29 digits of the fractional part of a constant."""
    import mpmath

    mpmath.mp.prec = int(count * math.log2(M)) + 64
    value = {
        "pi": mpmath.pi,
        "e": mpmath.e,
        "golden ratio": mpmath.phi,
        "sqrt 2": mpmath.sqrt(2),
    }[name]
    frac = int(mpmath.floor((value - mpmath.floor(value)) * mpmath.mpf(M) ** count))
    digits = []
    for _ in range(count):
        frac, d = divmod(frac, M)
        digits.append(d)
    return np.array(digits[::-1], dtype=np.int64)


def generators(need: int) -> dict[str, np.ndarray]:
    """The 24 sequences of `sequence_key_sweep`, and a second set that sweep lacks."""
    sequence_key_sweep.TERMS = need
    gens = {k: v for k, v in sequence_key_sweep.generators().items() if len(v) >= need}
    limit = 4_000_000
    flag = np.ones(limit + 1, dtype=bool)
    flag[:2] = False
    for i in range(2, int(limit**0.5) + 1):
        if flag[i]:
            flag[i * i :: i] = False
    primes = np.flatnonzero(flag)
    p = primes[:need]
    n = np.arange(1, need + 1, dtype=np.int64)
    tot = sequence_key_sweep.generators()["totient"]
    spf_count = np.zeros(
        limit // 40 + 1, dtype=np.int64
    )  # prime factors with multiplicity
    for q in primes[primes <= limit // 40]:
        pk = int(q)
        while pk <= limit // 40:
            spf_count[pk::pk] += 1
            pk *= int(q)
    gens.update(
        {
            "prime(prime(n))": primes[p - 1] % M,
            "prime(n)^2": p * p % M,
            "n * prime(n)": n * p % M,
            "sum of primes": np.cumsum(p % M) % M,
            "sum of totients": np.cumsum(tot[:need]) % M,
            "semiprime(n)": np.flatnonzero(spf_count == 2)[:need] % M,
            "twin prime, lower": p[:-1][np.diff(p) == 2] % M,
        }
    )
    for name in CONSTANT_DIGITS:
        gens[f"{name}, base-29 digits"] = constant_digits(name, need)
    return {k: v.astype(np.int64) for k, v in gens.items() if len(v) >= need}


def plant(lens, key, rng, *, spaces: bool) -> np.ndarray:
    """The author's words at the body's block lengths under key + dodge: a would-be
    repeat is re-enciphered once with the next key element."""
    pools: dict[int, list[list[int]]] = {}
    for w in lp_plaintext_register.corpus():
        pools.setdefault(len(w), []).append(w)
    out: list[int] = []
    j, prev = 0, -1
    for L in lens:
        LL = L
        while LL not in pools:
            LL -= 1
        w = rng.choice(pools[LL])
        w = (w * (L // len(w) + 1))[:L]
        for r in w:
            c = (r + int(key[j])) % M
            if c == prev:
                j += 1
                c = (r + int(key[j])) % M
            out.append(c)
            prev = c
            j += 1
        if spaces:
            j += 1
    return np.array(out, dtype=np.int64)


_W: dict = {}


def _init(texts, word, unit_map, tabs) -> None:
    _W.update(texts=texts, word=word, units=unit_map, tabs=tabs)


def _task(args):
    """One generator in one case: the body's best score and the surrogates'."""
    name, key, layout, kind = args
    w = _W
    out = []
    best_q = 0
    for t, text in enumerate(w["texts"]):
        sc = score(
            text, w["word"], w["units"][layout], key, w["tabs"], SLACK[layout], kind
        )
        out.append(float(sc.max()))
        if t == 0:
            best_q = int(sc.argmax())
    return name, layout, kind, out, best_q


def main() -> None:
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    rng = random.Random(SEED)
    tok = lp_corpus.load_tokenized()
    cipher = np.array(tok.stream, dtype=np.int64)
    word = np.array(tok.word, dtype=np.int64)
    n = len(cipher)
    lens = [len(w) for w in tok.words()]
    llr = plaintext_llr()
    tabs = emission_tables(llr)
    unit_map = units(tok)
    need = n + len(lens) + max(SLACK.values()) + 10
    gens = generators(need)
    gain = float((np.exp(llr) / M * llr).sum())
    print(
        f"body: {n:,} runes; {len(gens)} generators of {need:,} terms; a true key gains "
        f"{gain:.3f} nats per rune before slip penalties"
    )

    null_model = c3301.low_doublet_null()
    texts = [cipher] + [
        np.array(null_model(tok.stream, rng), dtype=np.int64) for _ in range(SURROGATES)
    ]

    # control: prime(n)-1 planted with the dodge, read back, against the same key on the
    # surrogate bodies
    key = gens["prime(n)-1"]
    print(
        "\ncontrol: prime(n)-1 planted on the author's words at the body's block lengths"
    )
    print(f"  {'base':<9}{'planted':>9}{'same key, surrogate bodies':>30}{'z':>9}")
    control_ok = True
    for kind in ("runes", "spaces"):
        planted = plant(lens, key, rng, spaces=kind == "spaces")
        s = score(
            planted, word, unit_map["runs on"], key, tabs, SLACK["runs on"], kind
        ).max()
        sur = np.array(
            [
                score(
                    t, word, unit_map["runs on"], key, tabs, SLACK["runs on"], kind
                ).max()
                for t in texts[1:]
            ]
        )
        z = z_score(float(s), float(sur.mean()), float(sur.std(ddof=1)))
        control_ok = control_ok and z > 20
        print(
            f"  {kind:<9}{s:>9.0f}{f'{sur.mean():.0f} +- {sur.std(ddof=1):.0f}':>30}{z:>+9.1f}"
        )

    cases = [(layout, kind) for layout in unit_map for kind in BASES]
    tasks = [(g, k, layout, kind) for g, k in gens.items() for layout, kind in cases]
    results: dict[tuple[str, str, str], tuple[float, int]] = {}
    with Pool(nproc, initializer=_init, initargs=(texts, word, unit_map, tabs)) as pool:
        for name, layout, kind, out, best_q in pool.imap_unordered(_task, tasks):
            sur = np.array(out[1:])
            results[name, layout, kind] = (
                z_score(out[0], float(sur.mean()), float(sur.std(ddof=1))),
                best_q,
            )

    print(
        f"\nthe body: z of the best (sense, offset) against the same key on "
        f"{SURROGATES} surrogate bodies"
    )
    header = f"  {'generator':<30}"
    for layout, kind in cases:
        header += f"{layout[:4] + '/' + kind[:3]:>9}"
    print(header)
    zs = []
    best = (-1e9, "", "", "", 0)
    for g in gens:
        row = f"  {g:<30}"
        for layout, kind in cases:
            z, q = results[g, layout, kind]
            zs.append(z)
            row += f"{z:>+9.2f}"
            if z > best[0]:
                best = (z, g, layout, kind, q)
        print(row)

    def t_tail(z: float) -> float:
        """One-sided tail of a z against SURROGATES draws: Student t with the predictive
        factor, integrated numerically."""
        df = SURROGATES - 1
        t = z / math.sqrt(1 + 1 / SURROGATES)
        grid = np.linspace(t, t + 400.0, 400001)
        norm = math.gamma((df + 1) / 2) / (math.sqrt(df * math.pi) * math.gamma(df / 2))
        dens = norm * (1 + grid * grid / df) ** (-(df + 1) / 2)
        return float(dens.sum() * (grid[1] - grid[0]))

    p_single = t_tail(best[0])
    p_family = 1 - (1 - p_single) ** len(zs)
    zs_arr = np.array(zs)
    sense, off = divmod(best[4], M)
    print(
        f"\n{len(zs)} cells: z mean {zs_arr.mean():+.2f}, sd {zs_arr.std(ddof=1):.2f}. "
        f"Best: {best[1]}, {best[2]}, base {best[3]}, {SENSES[sense]}, offset {off}: "
        f"z {best[0]:+.2f}, single P {p_single:.4f} (Student t, {SURROGATES - 1} df), "
        f"family P {p_family:.3f}"
    )
    if not control_ok:
        print("VERDICT: the control failed; the negative below means nothing.")
    elif p_family < 0.01:
        print("VERDICT: a generator aligns with the body. Decrypt along its path.")
    else:
        print(
            f"VERDICT: none of the {len(gens)} generators aligns with the body under any "
            f"pattern of key skips and stalls within the slack "
            f"({', '.join(f'{k} {v}' for k, v in SLACK.items())})."
        )


if __name__ == "__main__":
    main()
