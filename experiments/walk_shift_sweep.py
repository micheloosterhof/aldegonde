# ABOUTME: Sweeps the length-clocked walk with a per-word plaintext shift over keys
# ABOUTME: built from one keyword: a grid step g, a conjugated-shift sigma, a dial start.
"""The walk with a per-word Caesar shift, over naturally built keys.

`within-word-relation-is-position-flat.md` (row C9) leaves the walk one repair: the
letter step conjugated by a per-word shift, which is a Caesar shift of the plaintext
by s_w before the walk. `walk_shift_verifier_check.py` shows the base_0-free verifier
still separates a true key with the preventer skipping the clock inside words.

The family is what one keyword builds, after `how-big-is-the-key-really.md`:

  K        a keyed alphabet from 3301's vocabulary (four construction rules)
  g        the 5x5 grid of K's first 25 (or last 25) runes with a column or a row
           rotated by one, the other four runes fixed: eight steps per K
  sigma    K-conjugated shifts K . (add d) . K^-1 for d = 1..28, plus K itself and its
           inverse as maps: thirty per K
  s_w      a_0 + w or a_0 - w, a_0 in 0..28

1,264 alphabets x 8 x 30 x 58 = 1.8e7 keys, scored on three 250-word windows that open
long sections, each with its own free base_0. A true key scores near +1.1 nats per
rune and wrong keys below +0.6 (`walk_shift_verifier_check.py`).

`--selftest` plants a key of exactly this family and must rank it first against the
family built from a few keywords; `--run` sweeps the priority vocabulary; `--show`
reads the body under the best candidates.
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from base_free_verifier import log_frequencies, powers  # noqa: E402
from quagmire_runner import conj_shift  # noqa: E402
from walk_shift_kernel import Windows, schedule_shifts, score_sigmas  # noqa: E402

from aldegonde.maths import permutation  # noqa: E402

M = 29
SPANS = [(0, 250), (806, 1056), (2181, 2431)]
OUT = ROOT / "experiments" / "walk_shift_candidates.jsonl"
KEEP = 40


def grid_steps(K):
    """Eight order-5 steps from K: rotate a column or a row of its 5x5 grid by one."""
    for which, grid in (("first25", K[:25]), ("last25", K[4:])):
        for axis in ("col", "row"):
            for sign in (+1, -1):
                g = list(range(M))
                for c in range(5):
                    line = (
                        [grid[r * 5 + c] for r in range(5)]
                        if axis == "col"
                        else grid[c * 5 : c * 5 + 5]
                    )
                    for t in range(5):
                        g[line[t]] = line[(t + sign) % 5]
                yield f"{which}-{axis}{'+' if sign > 0 else '-'}", g


def sigma_family(K):
    out = [conj_shift(K, d) for d in range(1, M)]
    out.append(list(K))
    out.append(permutation.inverse(list(K)))
    return np.array(out, dtype=np.int8)


def keyed_alphabets(words):
    from keyword_exhaustion import alphabets, kw_runes  # noqa: PLC0415

    for word in words:
        seq = kw_runes(word)
        if seq:
            for rule, K in alphabets(seq):
                yield f"{word} {rule}", list(K)


def sweep(words, body_words, logf, *, keep: int = KEEP, log_every: int = 100):
    """Best keys over the family built from `words`, scored on the body's windows."""
    windows_cache = {}
    best: list[tuple[float, str, str, int, int, int]] = []
    tested = 0
    start = time.time()
    for n, (kname, K) in enumerate(keyed_alphabets(words), 1):
        sigmas = sigma_family(K)
        for gname, g in grid_steps(K):
            perms = powers(g)
            for direction in (+1, -1):
                for a0 in range(M):
                    key = (a0, direction)
                    if key not in windows_cache:
                        windows_cache[key] = Windows(
                            [body_words[a:b] for a, b in SPANS],
                            schedule_shifts(SPANS, a0, direction),
                        )
                    scores = score_sigmas(perms, sigmas, windows_cache[key], logf)
                    tested += len(sigmas)
                    top = int(scores.argmax())
                    best.append((float(scores[top]), kname, gname, top, a0, direction))
                    best.sort(reverse=True)
                    del best[keep:]
        if n % log_every == 0:
            rate = tested / (time.time() - start)
            print(
                f"  {n} alphabets, {tested:,} keys, best {best[0][0]:+.4f} "
                f"({best[0][1]} {best[0][2]}), {rate:,.0f} keys/s",
                flush=True,
            )
    return best, tested


def selftest() -> None:
    from pure_quagmire_restart import matched_register  # noqa: PLC0415
    from quagmire_runner import PROSE_CACHE, load_register  # noqa: PLC0415

    rng = random.Random(3301)
    pools, _t, _f = load_register(PROSE_CACHE)
    lens = _lens()
    plain = matched_register(rng, lens, pools)
    words = ["DIVINITY", "WITHIN", "CIRCUMFERENCE", "PARABLE", "WISDOM", "PILGRIM"]
    alphabets = list(keyed_alphabets(words))
    kname, K = alphabets[7]
    gname, g = list(grid_steps(K))[5]
    sigma = [int(x) for x in sigma_family(K)[11]]
    a0, direction = 19, -1
    ct = encipher_dir(plain, rng.sample(range(M), M), g, sigma, a0, direction)
    print(
        f"planted: {kname}, g {gname}, sigma index 11, a0 {a0}, direction {direction}"
    )
    logf = log_frequencies()
    best, tested = sweep(words, ct, logf, keep=10, log_every=10**9)
    print(f"{tested:,} keys tested; top five:")
    for row in best[:5]:
        print(
            f"  {row[0]:+.4f}  {row[1]:<26} {row[2]:<16} sigma {row[3]:>2} a0 {row[4]:>2} dir {row[5]:+d}"
        )
    top = best[0]
    assert (top[1], top[2], top[3], top[4], top[5]) == (
        kname,
        gname,
        11,
        a0,
        direction,
    ), "the planted key does not rank first"
    assert top[0] > best[1][0] + 0.2 or best[1][1:3] == (kname, gname), (
        "no margin over the runner-up"
    )
    print("self-test passed")


def encipher_dir(plain, base0, g, sigma, a0, direction):
    gp = [permutation.power(g, k) for k in range(5)]
    base = list(base0)
    out, previous = [], None
    for w, word in enumerate(plain):
        s = (a0 + direction * w) % M
        cw, clock = [], 0
        for p in word:
            c = base[gp[clock % 5][(p + s) % M]]
            if c == previous:
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


def _lens() -> list[int]:
    from lp_corpus import load_clean  # noqa: PLC0415

    _stream, wid = load_clean()
    counts: dict[int, int] = {}
    for w in wid:
        counts[w] = counts.get(w, 0) + 1
    return [counts[k] for k in sorted(counts)]


def run() -> None:
    from quagmire_schedule_census import lp_words  # noqa: PLC0415
    from quagmire_ungated_sweep import priority_vocabulary  # noqa: PLC0415

    words = priority_vocabulary()
    body = lp_words()
    logf = log_frequencies()
    print(f"{len(words)} priority words; scoring on windows {SPANS}")
    best, tested = sweep(words, body, logf)
    print(f"\nDONE: {tested:,} keys")
    with OUT.open("w") as fout:
        for score, kname, gname, sidx, a0, direction in best:
            print(
                f"  {score:+.4f}  {kname:<28} {gname:<16} sigma {sidx:>2} a0 {a0:>2} dir {direction:+d}"
            )
            fout.write(
                json.dumps(
                    {
                        "score": score,
                        "alphabet": kname,
                        "g": gname,
                        "sigma": sidx,
                        "a0": a0,
                        "dir": direction,
                    }
                )
                + "\n"
            )
    print(f"written to {OUT}; a true key scores near +1.1, wrong keys below +0.6")


def main() -> None:
    if "--selftest" in sys.argv:
        selftest()
    elif "--run" in sys.argv:
        run()
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
