# ABOUTME: A base_0-free scorer that tracks the doublet preventer's clock skips, which
# ABOUTME: the sweep kernel cannot, by alternating an assignment solve with phase fitting.
"""Can a key search score a doublet-preventer key at all?

`dodge_scorer_check.py` showed that `walk_score_kernel.score_sigmas` cannot: a planted
key of the family scores 0.493 against 0.619 for the best of 2,000 wrong sigmas, below
random. The kernel undoes the letter step at position j with the alphabet for clock j,
and the preventer breaks `clock = position` by inserting steps.

**Why this looked impossible, and why it is not.** Detecting a fire needs the base, and
the base is the unknown the kernel leaves free. But the circularity is soluble. A fire
at j means the first emission hit `c_(j-1)` and the re-emission gave `c_j`:

    A_k(p_j) = base_w^-1(c_(j-1))   and   A_(k+d)(p_j) = base_w^-1(c_j)

Eliminating `p_j` gives `base_w^-1(c_j) = R(base_w^-1(c_(j-1)))` with
`R = A_(k+d) . A_k^-1`, a conjugated shift known from the key. Writing `v = base_0^-1(c)`
and folding the per-word step into `Q`, that is

    v_j = Q(v_(j-1))

a condition on the base_0-free coordinates alone. So fires are detectable GIVEN `v`, and
`v` is exactly what the assignment solves for. Chicken and egg, not a wall: alternate.

**Cost.** Separation switches on between 720 and 1,083 runes and is sharp, not
gradual, because the per-window phase is itself fitted and overfits short text. So the
first stage of a sweep is about 1,100 runes rather than the 100 a cheap bound would
want, and the saving is 1.66x rather than an order of magnitude.

**The loop.** Cut the stream into short windows. Inside a window assume no fire, so the
clock is the position plus an unknown phase in 0..4 — short windows are mostly
fire-free, at a rate of `(1-q)^L`. Then:

  1. seed the score matrix by summing every window over all five phases;
  2. solve the assignment for `v`;
  3. with `v` fixed, score each window at each phase and keep the best;
  4. rebuild the matrix from those phases and go back to 2.

Three passes is enough to converge. The question this script answers is whether the
result separates a planted key from wrong ones, which is the only thing that matters
before any of it is worth writing in C.

Run with no arguments.
"""

from __future__ import annotations

import random
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies  # noqa: E402
from doublet_phase_test import encipher  # noqa: E402
from ea_direction_test import PROSE_CACHE  # noqa: E402
from fingerprint_battery import M  # noqa: E402
from pure_quagmire_restart import matched_register, running, schedule  # noqa: E402
from quagmire_runner import load_clean, load_register  # noqa: E402

WINDOW = 18  # runes; (1-q)^18 is about half with q = 0.035
PASSES = 3
WRONG_KEYS = 60
SHARES = (0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0)


def letter_maps(K, offsets):
    """A_k as a lookup and its inverse, for each of the five clock phases."""
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    fwd = [[K[(pos[p] + S[k]) % M] for p in range(M)] for k in range(5)]
    inv = []
    for k in range(5):
        back = [0] * M
        for p, c in enumerate(fwd[k]):
            back[c] = p
        inv.append(back)
    return np.array(fwd, dtype=np.int64), np.array(inv, dtype=np.int64)


def word_shifts(n_words: int, startdials):
    """The odometer's (inner, outer) shift for each word."""
    a, b = startdials
    out = []
    for _ in range(n_words):
        out.append((a, b))
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return out


def plaintext_of(cipher_rune, phase, a, b, K, inv, pos_of):
    """p = A_phase^-1( (c - b) un-shifted by a ), all in K coordinates."""
    inner = (pos_of[(cipher_rune - b) % M] - a) % M
    return inv[phase][K[inner % M]]


def build(cipher_words, K, offsets, startdials, logf, phases=None):
    """Score matrix over (ciphertext rune, candidate base_0 image).

    `phases` gives the clock phase at the start of each window; None seeds by summing
    all five, which is the uninformed first pass.
    """
    _fwd, inv = letter_maps(K, offsets)
    pos_of = [0] * M
    for i, r in enumerate(K):
        pos_of[r] = i
    shifts = word_shifts(len(cipher_words), startdials)

    flat, owner = [], []
    for w, word in enumerate(cipher_words):
        flat.extend(word)
        owner.extend([w] * len(word))

    mat = np.zeros((M, M))
    n_windows = (len(flat) + WINDOW - 1) // WINDOW
    for m in range(n_windows):
        lo = m * WINDOW
        hi = min(lo + WINDOW, len(flat))
        options = range(5) if phases is None else (phases[m],)
        for phase in options:
            for i in range(lo, hi):
                a, b = shifts[owner[i]]
                k = (phase + i - lo) % 5
                # for each candidate image y of this ciphertext rune, the plaintext it
                # implies under this phase
                for y in range(M):
                    inner = (pos_of[(y - b) % M] - a) % M
                    mat[flat[i], y] += logf[inv[k][K[inner]]]
    return mat, flat, owner, shifts, inv, pos_of, n_windows


def assign(mat):
    """Greedy one-to-one choice, as base_free_verifier does."""
    left = mat.copy()
    total = 0.0
    out = np.empty(M, dtype=np.int64)
    for _ in range(M):
        c, y = divmod(int(left.argmax()), M)
        total += left[c, y]
        out[c] = y
        left[c, :] = -np.inf
        left[:, y] = -np.inf
    return total, out


def refit_phases(flat, owner, shifts, inv, K, pos_of, logf, v, n_windows):
    """With base_0 fixed, pick each window's phase by its own unigram score."""
    chosen = []
    for m in range(n_windows):
        lo = m * WINDOW
        hi = min(lo + WINDOW, len(flat))
        best, arg = -np.inf, 0
        for phase in range(5):
            total = 0.0
            for i in range(lo, hi):
                a, b = shifts[owner[i]]
                inner = (pos_of[(int(v[flat[i]]) - b) % M] - a) % M
                total += logf[inv[(phase + i - lo) % 5][K[inner]]]
            if total > best:
                best, arg = total, phase
        chosen.append(arg)
    return chosen


def score(cipher_words, K, offsets, startdials, logf) -> float:
    """Nats per rune, after alternating the assignment with the window phases."""
    phases = None
    total = 0.0
    n_runes = sum(len(w) for w in cipher_words)
    for _ in range(PASSES):
        mat, flat, owner, shifts, inv, pos_of, n_windows = build(
            cipher_words, K, offsets, startdials, logf, phases
        )
        if phases is None:
            mat /= 5.0  # the seed summed five phases per position
        total, v = assign(mat)
        phases = refit_phases(flat, owner, shifts, inv, K, pos_of, logf, v, n_windows)
    return total / n_runes


def prefix(cipher_words, runes: int):
    """The first `runes` runes of the ciphertext, cut at a word boundary."""
    out, total = [], 0
    for word in cipher_words:
        if total >= runes:
            break
        out.append(word)
        total += len(word)
    return out


def rejection_curve(cipher, K, offsets, startdials, logf, rng) -> None:
    """How little text is enough to throw a wrong key away.

    The full-length score is what a sweep would use on survivors. What decides its cost
    is the cheap first look: if a short prefix already puts every wrong key below the
    planted one, the sweep only pays full price for the few that pass.
    """
    full = sum(len(w) for w in cipher)
    print(
        f"\n{'prefix':>8}{'runes':>8}{'planted':>10}{'best wrong':>12}"
        f"{'gap':>8}{'z':>8}   separates"
    )
    for share in SHARES:
        part = prefix(cipher, max(60, int(full * share)))
        runes = sum(len(w) for w in part)
        true = score(part, K, offsets, startdials, logf)
        vals = np.array(
            [
                score(
                    part,
                    rng.sample(range(M), M),
                    schedule(rng),
                    (rng.randrange(M), rng.randrange(M)),
                    logf,
                )
                for _ in range(WRONG_KEYS)
            ]
        )
        gap = true - vals.max()
        print(
            f"{share:>8.0%}{runes:>8}{true:>10.3f}{vals.max():>12.3f}"
            f"{gap:>8.3f}{(true - vals.mean()) / vals.std():>8.1f}"
            f"   {'yes' if gap > 0 else 'NO'}"
        )
    print(
        "\nRejection switches on sharply between 40% and 60%, not gradually. Below that"
        "\nthe per-window phase -- a FITTED parameter, one of five per window -- flatters"
        "\na wrong key as much as the true one, and it pays off only once the base_0"
        "\nassignment is well determined. So the useful first stage is about 1,100 runes,"
        "\nnot the 100 a really cheap bound would want."
        "\n"
        "\nTwo stages, then: score every key at 60% and keep what clears the wrong-key"
        "\nmean by 3 SD, which the planted key beats by 5.5; full-score the survivors."
        "\nThat costs about 0.6 of the full score per key rather than 1.0."
    )


def main() -> None:
    rng = random.Random(3301)
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)][:400]  # a 400-word slice, for speed
    pools, _t, _f = load_register(PROSE_CACHE)
    logf = log_frequencies()

    K = rng.sample(range(M), M)
    offsets = schedule(rng)
    startdials = (rng.randrange(M), rng.randrange(M))
    plain = matched_register(rng, lens, pools)

    for variant in ("advance",) if "--curve" in sys.argv else ("advance", "hold"):
        cipher = encipher(plain, K, offsets, startdials, 0, variant)
        runes = sum(len(w) for w in cipher)
        print(
            f"\n=== preventer: {variant} === {len(cipher)} words, {runes} runes, "
            f"window {WINDOW}, {PASSES} passes"
        )
        t0 = time.time()
        true = score(cipher, K, offsets, startdials, logf)
        per_key = time.time() - t0
        print(f"planted key {true:+.3f} nats/rune   ({per_key:.2f}s in Python)")

        # wrong keys of three kinds, hardest last
        beaten = []
        for label, maker in (
            (
                "wrong alphabet only",
                lambda: (rng.sample(range(M), M), offsets, startdials),
            ),
            ("wrong schedule only", lambda: (K, schedule(rng), startdials)),
            (
                "everything wrong",
                lambda: (
                    rng.sample(range(M), M),
                    schedule(rng),
                    (rng.randrange(M), rng.randrange(M)),
                ),
            ),
        ):
            vals = np.array([score(cipher, *maker(), logf) for _ in range(WRONG_KEYS)])
            found = true > vals.max()
            beaten.append((label, found))
            print(
                f"   {label:<22} mean {vals.mean():+.3f}  best {vals.max():+.3f}  "
                f"gap {true - vals.max():+.3f}  z {(true - vals.mean()) / vals.std():+.1f}"
                f"   {'FOUND' if found else 'MISSED'}"
            )
        missed = [label for label, found in beaten if not found]
        assert not missed, (
            f"{variant}: the planted key must top every category, missed {missed}"
        )

    # cost projection: the old kernel does 45,000 keys/s/core on three 200-word
    # windows, about 1.2e8 rune-scores/s. This does 5 phases in the seed pass, then
    # PASSES builds and refits, so roughly 8-10x the work per rune.
    python_rate = runes / per_key
    print(f"\ncost: {per_key:.2f}s per key in Python, {python_rate:,.0f} rune-scores/s")
    for speedup in (100, 200):
        rate = python_rate * speedup / runes
        print(
            f"   at {speedup}x for a C port: {rate:,.0f} keys/s/core, so the "
            f"4.9e9-key priority sweep\n      takes {4.9e9 / rate / 3600:,.0f} core-hours"
        )
    print(
        "   against 30 core-hours for the old kernel, which cannot score this family"
        "\n   at all. A cheap first-pass bound cuts it further, as skip_below does:"
    )
    rejection_curve(cipher, K, offsets, startdials, logf, rng)


if __name__ == "__main__":
    main()
