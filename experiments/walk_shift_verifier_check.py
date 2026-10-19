# ABOUTME: Can the base_0-free walk verifier score a walk key whose plaintext is Caesar-
# ABOUTME: shifted per word and whose preventer skips the clock inside the word?
"""Does the walk verifier survive a per-word plaintext shift and a within-word dodge?

`within-word-relation-is-position-flat.md` leaves the length-clocked walk one way to
fit: conjugate its letter step by a per-word Caesar shift, which is the same as
shifting the plaintext by s_w before the walk,

    c_j = base_w( g^(k_j)( p_j + s_w ) ),   s_w = a_0 + w  (mod 29)

with the clock k re-anchored at each separator (row D1) and the doublet preventer
advancing it by one inside the word when an emission would repeat the previous rune.
The chain is the walk's: base_{w+1} = base_w o g^((L-1) mod 5) o sigma.

`base_free_verifier.score_key` assumes k_j = j and no shift. Here it gets the shift
(one more table index) and keeps assuming k_j = j, so every word in which the
preventer fired reads wrongly from the fire onward. About one word in seven carries a
fire. The question is whether a true key still separates from wrong ones, which
decides whether the compiled kernel needs windowed phase fitting or just the shift.

Run with no arguments.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import (  # noqa: E402
    assign,
    conjugate_swap,
    inverse,
    log_frequencies,
    powers,
    swap_two,
)
from fingerprint_battery import rich_order5  # noqa: E402
from pure_quagmire_restart import matched_register  # noqa: E402
from quagmire_runner import PROSE_CACHE, load_register  # noqa: E402

from aldegonde.maths import permutation  # noqa: E402

M = 29


def encipher(plain, base0, g, sigma, a0, *, dodge: bool = True):
    gp = [permutation.power(g, k) for k in range(5)]
    base = list(base0)
    out, previous = [], None
    for w, word in enumerate(plain):
        s = (a0 + w) % M
        cw, clock = [], 0
        for p in word:
            c = base[gp[clock % 5][(p + s) % M]]
            if dodge and c == previous:
                clock += 1
                c = base[gp[clock % 5][(p + s) % M]]
            cw.append(c)
            previous = c
            clock += 1
        out.append(cw)
        base = permutation.compose(
            base, permutation.compose(gp[(len(word) - 1) % 5], sigma)
        )
    return out


def score_key(ct_words, g, sigma, a0, logf, n_words=None):
    """`base_free_verifier.score_key` with the per-word shift folded into the table."""
    letter_perms = powers(g)
    sig = np.asarray(sigma)
    # by_phase[j][s][u] = log f( g_j^-1(u) - s )
    by_phase = np.empty((5, M, M))
    for j, perm in enumerate(letter_perms):
        inv = inverse(np.asarray(perm))
        for s in range(M):
            by_phase[j, s] = logf[(inv - s) % M]
    step_inv = [inverse(np.asarray(p)[sig]) for p in letter_perms]
    table = np.zeros((M, M))
    m_inv = np.arange(M)
    words = ct_words[:n_words]
    for w, word in enumerate(words):
        s = (a0 + w) % M
        for j, c in enumerate(word):
            table[c] += by_phase[j % 5, s][m_inv]
        m_inv = step_inv[(len(word) - 1) % 5][m_inv]
    runes = sum(len(w) for w in words)
    total, _u = assign(table)
    return (total - runes * logf.mean()) / runes


def main() -> None:
    rng = random.Random(3301)
    pools, _t, _f = load_register(PROSE_CACHE)
    from lp_corpus import load_clean  # noqa: PLC0415

    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    plain = matched_register(rng, lens, pools)
    logf = log_frequencies()
    g = rich_order5(rng)
    sigma = rng.sample(range(M), M)
    base0 = rng.sample(range(M), M)
    a0 = rng.randrange(M)

    for dodge in (False, True):
        ct = encipher(plain, base0, g, sigma, a0, dodge=dodge)
        fires = sum(1 for w in ct for i in range(1, len(w)) if w[i] == w[i - 1])
        print(
            f"\n{'with' if dodge else 'without'} the preventer (surviving doublets {fires})"
        )
        print(
            f"{'words':>6}{'true':>8}{'swap sigma':>13}{'conj g':>10}{'a0+1':>8}{'random':>9}"
        )
        for n in (200, 400, 800):
            true = score_key(ct, g, sigma, a0, logf, n)
            wrong = {
                "swap": [
                    score_key(ct, g, swap_two(sigma, rng), a0, logf, n)
                    for _ in range(20)
                ],
                "conj": [
                    score_key(ct, conjugate_swap(g, rng), sigma, a0, logf, n)
                    for _ in range(20)
                ],
                "a0": [score_key(ct, g, sigma, (a0 + 1) % M, logf, n)],
                "rand": [
                    score_key(
                        ct,
                        rich_order5(rng),
                        rng.sample(range(M), M),
                        rng.randrange(M),
                        logf,
                        n,
                    )
                    for _ in range(20)
                ],
            }
            cells = "".join(
                f"{max(v):>{wdt}.3f}" for v, wdt in zip(wrong.values(), (13, 10, 8, 9))
            )
            print(f"{n:>6}{true:>8.3f}{cells}   (max of each)")
        ceiling = max(max(v) for v in wrong.values())
        print(
            f"  true key {'separates' if true > ceiling + 0.2 else 'does NOT separate'} at 800 words"
        )


if __name__ == "__main__":
    main()
