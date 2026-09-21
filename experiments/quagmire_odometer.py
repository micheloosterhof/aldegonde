# ABOUTME: A Quagmire whose per-word step is two shift dials on an odometer carry, with
# ABOUTME: a continuous clock and a doublet preventer -- no general permutation anywhere.
"""The cipher `pure-quagmire-word-restart.md` points at.

That file disproved the fixed per-word restart on the seam and measured what the rest of
Michel's proposal needs. This builds it.

    c_j = ( K[ (pos_K(p_j) + a_w + S[clock mod 5]) mod 29 ] + b_w ) mod 29

Every operation is a shift. `a_w` shifts inside the keyed alphabet, `b_w` outside it,
and the two do not commute, so the per-word step ranges over 29 x 29 = 841 permutations
rather than the 29 a single shift would give. They are driven as an ODOMETER: `a`
advances every word, `b` advances only when `a` wraps. That matters -- two dials each
advancing at a fixed rate stay on a line and deliver 29 states between them, which is
what a naive two-dial version measured.

Two properties are inherited rather than chosen:

  * **the clock runs on through the word break.** A fixed restart puts every boundary on
    one clock phase, so the preventer fails at all of them or none, and the seam comes
    out 0 or several times the within-word rate. The corpus has them nearly equal, which
    needs the boundaries spread over all five phases.
  * **the schedule holds exactly one zero offset.** That is the only way the preventer
    can fail, and it forces the doublet rate to (1/5) x a diagonal.

Nothing here is fitted. K, the schedule and the dials' starting values are drawn at
random, so every cell of the battery is a free prediction.

Run with no arguments for the self-test, `--fit` for the battery score, `--matched` to
re-score the length-sensitive cells on a register carrying the LP's own word lengths.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from ea_direction_test import PROSE_CACHE  # noqa: E402
from fingerprint_battery import (  # noqa: E402
    M,
    compare,
    cross_word_d5,
    fingerprint,
    lp_words,
)
from pure_quagmire_restart import matched_register, running, schedule  # noqa: E402
from quagmire_runner import load_clean, load_register  # noqa: E402

FITTED: set[str] = set()  # nothing is chosen against the corpus


def encipher(plain, K, offsets, start, *, carry=True, restart=None):
    """Two shift dials on a carry, a continuous clock, and the doublet preventer.

    `carry` False advances both dials every word instead, which collapses them onto a
    line and is the failure the hypothesis file records. `restart` fixes the clock at
    that phase for every word instead of letting it run, which is the disproved variant.
    """
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    S = running(offsets)
    a, b = start
    out = []
    previous = None
    clock = 0
    for word in plain:
        if restart is not None:
            clock = restart
        cipher_word = []
        for p in word:
            c = (K[(pos[p] + a + S[clock % 5]) % M] + b) % M
            if c == previous:
                clock += 1
                c = (K[(pos[p] + a + S[clock % 5]) % M] + b) % M
            cipher_word.append(c)
            previous = c
            clock += 1
        out.append(cipher_word)
        a = (a + 1) % M
        b = (b + 1) % M if not carry or a == 0 else b
    return out


def generator(K, offsets, start, **kw):
    def generate(plain, _rng):
        return encipher(plain, K, offsets, start, **kw)

    return generate


def draw(rng):
    return rng.sample(range(M), M), schedule(rng), (rng.randrange(M), rng.randrange(M))


def states(K, offsets, start, **kw) -> int:
    """Distinct per-word permutations the dials actually visit over 2,928 words."""
    pos = [0] * M
    for i, r in enumerate(K):
        pos[r] = i
    del offsets, kw
    a, b = start
    seen = set()
    for _ in range(2928):
        seen.add((a, b))
        a = (a + 1) % M
        if a == 0:
            b = (b + 1) % M
    return len(seen)


def self_test() -> None:
    rng = random.Random(3301)
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    pools, _t, _f = load_register(PROSE_CACHE)
    lp = fingerprint(lp_words())
    K, offsets, start = draw(rng)

    n = states(K, offsets, start)
    print(f"schedule {offsets} (one zero offset)")
    print(f"per-word states visited in 2,928 words: {n} of 29 x 29 = {M * M}")
    assert n > 800, "the carry must decorrelate the dials, or they stay on a line"

    plain = matched_register(rng, lens, pools)
    got = fingerprint(encipher(plain, K, offsets, start))
    flat = fingerprint(encipher(plain, K, offsets, start, carry=False))
    print(
        f"\n{'variant':<34}{'nIoC':>9}{'identical':>11}{'d1w':>9}"
        f"{'seam':>9}{'seam/d1w':>10}"
    )
    print(
        f"{'the corpus':<34}{lp['ioc']:>9.4f}{lp['identical']:>11.0f}"
        f"{lp['d1w']:>9.4f}{lp['seam']:>9.4f}"
        f"{lp['seam'] / lp['d1w']:>10.2f}"
    )
    for label, cells in (("odometer carry", got), ("both dials every word", flat)):
        print(
            f"{label:<34}{cells['ioc']:>9.4f}{cells['identical']:>11.0f}"
            f"{cells['d1w']:>9.4f}{cells['seam']:>9.4f}"
            f"{cells['seam'] / cells['d1w'] if cells['d1w'] else float('nan'):>10.2f}"
        )
    assert got["identical"] < flat["identical"] / 3, (
        "the carry must cut identical words well below the lockstep version"
    )

    # the continuous clock is what lets the seam match the within-word rate
    ratios = []
    for _ in range(12):
        Kx, offx, startx = draw(rng)
        cells = fingerprint(
            encipher(
                matched_register(rng, lens, pools),
                Kx,
                offx,
                startx,
                restart=rng.randrange(5),
            )
        )
        ratios.append(cells["seam"] / cells["d1w"] if cells["d1w"] else float("nan"))
    print(
        f"\nsame key with a FIXED restart, seam/d1w over 12 draws: "
        f"{' '.join(f'{r:.1f}' for r in ratios)}"
    )
    print("the corpus reads 1.25; a restart cannot produce it, a running clock can")
    print("\nself-test passed")


def matched() -> None:
    """Re-score the length-sensitive cells on a register with the LP's word lengths.

    `fingerprint_battery.compare` draws consecutive prose, which carries prose word
    lengths. `identical` counts only words of MIN_WORD runes or more and the distance
    cells only count pairs inside a word, so the register moves them.
    """
    rng = random.Random(3301)
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    pools, _t, _f = load_register(PROSE_CACHE)
    lp = fingerprint(lp_words())

    rows = []
    for _ in range(40):
        K, offsets, start = draw(rng)
        rows.append(
            fingerprint(encipher(matched_register(rng, lens, pools), K, offsets, start))
        )
    print("register matched to the LP's word lengths, 40 draws\n")
    print(f"{'cell':<16}{'LP':>10}{'model':>11}{'spread':>10}{'tail':>8}   tag")
    for key in lp:
        values = np.array([r[key] for r in rows])
        below = float((values <= lp[key]).mean())
        tail = 2 * min(below, 1 - below + 1.0 / len(values))
        if values.std() < 1e-12 and abs(values.mean() - lp[key]) < 1e-9:
            tail = 1.0
        flag = "  <== miss" if tail <= 0.05 else ""
        print(
            f"{key:<16}{lp[key]:>10.4f}{values.mean():>11.4f}{values.std():>10.4f}"
            f"{tail:>8.3f}   FREE{flag}"
        )


TARGETS = {"d1w": 0.003, "d6w": 0.006, "d2w": 0.003, "d3w": 0.003, "d5x": 0.002}


def fit_profile(rng, lens, pools, cells, tries=900):
    """Hill-climb K and the schedule onto `cells` of the distance profile.

    Under a period-5 schedule 6 = 1 mod 5, so the distance-6 relation is a shift like
    the distance-1 one and the alphabet can tune it. Fitting d1w and d6w alone pushes
    d2w and d5x out, so this takes the set to fit as an argument: whether the whole
    profile can be satisfied at once decides if that was a local optimum or a real
    tension between the diagonals.
    """
    lp = fingerprint(lp_words())
    plain = [matched_register(rng, lens, pools) for _ in range(3)]

    def rate(words, distance):
        hits = pairs = 0
        for w in words:
            for j in range(len(w) - distance):
                pairs += 1
                hits += w[j] == w[j + distance]
        return hits / pairs

    def cost(K, offsets, start):
        # only the requested cells are scored, so skip the rest of the battery: a full
        # fingerprint runs a 39-skip kappa scan this search has no use for
        runs = [encipher(p, K, offsets, start) for p in plain]
        total = 0.0
        for cell in cells:
            if cell == "d5x":
                got = float(np.mean([cross_word_d5(r) for r in runs]))
            else:
                got = float(np.mean([rate(r, int(cell[1])) for r in runs]))
            total += abs(got - lp[cell]) / TARGETS[cell]
        return total

    K, offsets, start = draw(rng)
    best = cost(K, offsets, start)
    for _ in range(tries):
        cand_K, cand_off = list(K), list(offsets)
        if rng.random() < 0.75:
            i, j = rng.randrange(M), rng.randrange(M)
            cand_K[i], cand_K[j] = cand_K[j], cand_K[i]
        else:
            cand_off = schedule(rng)
        score = cost(cand_K, cand_off, start)
        if score < best:
            best, K, offsets = score, cand_K, cand_off
    return K, offsets, start, best


def fitted_run() -> None:
    """Fit d1w and d6w only, then score every other cell as a free prediction."""
    rng = random.Random(3301)
    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    lens = [counts[k] for k in sorted(counts)]
    pools, _t, _f = load_register(PROSE_CACHE)
    lp = fingerprint(lp_words())

    cells = (
        {"d1w", "d6w"} if "--two" in sys.argv else {"d1w", "d6w", "d2w", "d3w", "d5x"}
    )
    K, offsets, start, score = fit_profile(rng, lens, pools, cells)
    print(f"fitting {sorted(cells)}")
    print(f"schedule {offsets}, residual {score:.2f}\n")
    rows = [
        fingerprint(encipher(matched_register(rng, lens, pools), K, offsets, start))
        for _ in range(40)
    ]
    tuned = cells
    print(f"{'cell':<16}{'LP':>10}{'model':>11}{'spread':>10}{'tail':>8}   tag")
    misses = []
    for key in lp:
        values = np.array([r[key] for r in rows])
        below = float((values <= lp[key]).mean())
        tail = 2 * min(below, 1 - below + 1.0 / len(values))
        if values.std() < 1e-12 and abs(values.mean() - lp[key]) < 1e-9:
            tail = 1.0
        tag = "fitted" if key in tuned else "FREE"
        # a FITTED cell that still misses is the more serious result, so flag it too:
        # it means the search could not reach the corpus even while aiming at it
        flag = ""
        if tail <= 0.05:
            flag = "  <== miss" if tag == "FREE" else "  <== MISSED WHILE FITTED"
            misses.append(f"{key} ({tag})")
        print(
            f"{key:<16}{lp[key]:>10.4f}{values.mean():>11.4f}{values.std():>10.4f}"
            f"{tail:>8.3f}   {tag}{flag}"
        )
    print(
        f"\n{len(lp) - len(tuned)} free cells, {len(tuned)} fitted; "
        f"misses: {', '.join(misses) if misses else 'none'}"
    )
    print(
        f"the walk fits six cells and leaves 13 free with one miss; this fits "
        f"{len(tuned)}\nand leaves {len(lp) - len(tuned)}, with no general "
        f"permutation in the key."
    )


def main() -> None:
    if "--fit-d6" in sys.argv:
        fitted_run()
    elif "--matched" in sys.argv:
        matched()
    elif "--fit" in sys.argv:
        rng = random.Random(3301)
        K, offsets, start = draw(rng)
        print(f"schedule {offsets}; K, schedule and dials all drawn at random\n")
        compare(generator(K, offsets, start), 60, FITTED, "Quagmire on an odometer")
    else:
        self_test()


if __name__ == "__main__":
    main()
