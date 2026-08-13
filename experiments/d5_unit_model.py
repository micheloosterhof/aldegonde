# ABOUTME: Tests whether the LP's visible units are words or merged word groups,
# ABOUTME: using d5 -- the walk's only key-free, parameter-free plaintext channel.
"""Which unit model does the parameter-free d5 cell prefer?

Under the length-clocked walk a within-word ciphertext repeat at distance d means
`p_j = g^(d mod 5)(p_{j+d})`, so the observed rate is the `g^(d mod 5)` diagonal on
the distance-d plaintext pair table. At d = 5 the relation is `g^0` = identity: the
cell reads plaintext equality directly and NO choice of key can move it. It is the
walk's single parameter-free prediction, and its value is set entirely by how the
plaintext reference is built.

Every reference in this repo builds it from isolated dictionary words drawn to the
LP's length histogram -- which assumes each visible unit is one word. That is the
register hypothesis of `two-rune-deficit.md`, baked into the reference rather than
tested. The rival hypothesis in the same file says the units are merged word groups.

Both models can be forced to the SAME length histogram, so the histogram cannot
separate them (that file's finding). This script asked whether d5 can, since it
needs no key.

**It cannot, and the reason is worth recording.** Merging pulls the plaintext d5
rate two ways that very nearly cancel: across-boundary pairs draw on frequent
letters and so repeat MORE (0.0564 -> 0.0597 as absorption goes 0 -> 1), while the
straddling pairs lose the shared base and go flat. Net prediction 0.0538 for MERGE
against 0.0540 for REGISTER -- a gap of 0.0002 against an LP error of 0.0048. The
two unit models are observationally identical in this cell.

Models compared, all matched to the LP length histogram:
  REGISTER  isolated dictionary words at LP lengths (the current reference)
  MERGE     running prose with a fraction of short words absorbed into a neighbour
  BLIND     running prose with all boundaries erased, re-cut to LP lengths

Reported for each: the resulting length histogram, and the within-unit repeat rate
at d = 1..6. Only d5 is a parameter-free comparison against the LP; the others are
reported because a wrong unit model mis-specifies the P_d tables that every g-filter
in the repo is scored against.

The raw plaintext rates below are NOT the ciphertext prediction under merging --
straddling pairs go flat. `d5_straddle_prediction.py` does that properly.
"""

from __future__ import annotations

import random
import re
from collections import Counter
from pathlib import Path

from aldegonde import c3301
from experiments.runeglish_frequency import english_to_runeglish
from experiments.walk_verifier import load_words

M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
SEED = 3301
PROSE = "/var/folders/8r/93r5lmp93hx0w451_fv2p3rr0000gn/T/pg1342.txt"
DICT = "/usr/share/dict/web2"
DMAX = 6
SCALE = 30

# LP within-word counts, matches / pairs, from the clean corpus.
LP_COUNTS = {
    1: (63, 10028),
    2: (110, 3170),
    3: (98, 2649),
    4: (131, 3197),
    5: (102, 2073),
    6: (31, 1267),
}


def to_runes(word: str) -> list[int]:
    return [IDX[c] for c in english_to_runeglish(word.upper()) if c in IDX]


def prose_words() -> list[list[int]]:
    """Running prose in order, as rune-index words."""
    raw = Path(PROSE).read_text(errors="ignore")
    body = raw[raw.find("It is a truth universally") :]
    out = []
    for w in re.findall(r"[A-Za-z]+", body):
        r = to_runes(w)
        if r:
            out.append(r)
    return out


def dict_words() -> dict[int, list[list[int]]]:
    by_len: dict[int, list[list[int]]] = {}
    with open(DICT) as f:
        for line in f:
            w = line.strip()
            if w.isalpha():
                r = to_runes(w)
                if 1 <= len(r) <= 14:
                    by_len.setdefault(len(r), []).append(r)
    return by_len


def profile(units: list[list[int]]) -> dict[int, float]:
    """Within-unit plaintext repeat rate at each distance."""
    out = {}
    for d in range(1, DMAX + 1):
        hits = tot = 0
        for u in units:
            for i in range(len(u) - d):
                tot += 1
                hits += u[i] == u[i + d]
        out[d] = hits / tot if tot else 0.0
    return out


def hist(units: list[list[int]]) -> tuple[float, float]:
    """2-rune share and mean length."""
    c = Counter(len(u) for u in units)
    n = len(units)
    return 100 * c[2] / n, sum(len(u) for u in units) / n


def register_units(rng: random.Random, lp_hist: Counter) -> list[list[int]]:
    """Isolated dictionary words drawn to the LP histogram -- the current reference."""
    by_len = dict_words()
    out: list[list[int]] = []
    for length, count in lp_hist.items():
        pool = by_len.get(length, [])
        if pool:
            out += [pool[rng.randrange(len(pool))] for _ in range(count * SCALE)]
    rng.shuffle(out)
    return out


def merge_units(
    words: list[list[int]], q: float, rng: random.Random
) -> list[list[int]]:
    """Absorb a fraction q of short words into the preceding unit."""
    out: list[list[int]] = []
    for w in words:
        if out and len(w) <= 2 and rng.random() < q:
            out[-1] = out[-1] + w
        else:
            out.append(list(w))
    return out


def blind_units(
    words: list[list[int]], lp_hist: Counter, rng: random.Random
) -> list[list[int]]:
    """Erase every boundary, re-cut to the LP length histogram."""
    stream = [r for w in words for r in w]
    lengths = [ln for ln, c in lp_hist.items() for _ in range(c)]
    out, i = [], 0
    while i < len(stream) - 14:
        ln = lengths[rng.randrange(len(lengths))]
        out.append(stream[i : i + ln])
        i += ln
    return out


def tuned_q(words: list[list[int]], target: float, rng_seed: int) -> float:
    """Absorption rate that reproduces the LP's 2-rune share."""
    lo, hi = 0.0, 1.0
    for _ in range(24):
        mid = (lo + hi) / 2
        share, _ = hist(merge_units(words, mid, random.Random(rng_seed)))
        if share > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def main() -> None:
    rng = random.Random(SEED)
    lp = load_words()
    lp_hist = Counter(len(w) for w in lp)
    lp_share, lp_mean = hist(lp)
    lp_prof = {d: k / n for d, (k, n) in LP_COUNTS.items()}
    lp_se = {
        d: (lp_prof[d] * (1 - lp_prof[d]) / n) ** 0.5 for d, (_, n) in LP_COUNTS.items()
    }

    print(f"LP: {len(lp)} units, 2-rune {lp_share:.1f}%, mean {lp_mean:.3f}")
    print(
        f"    d5 = 102/2073 = {lp_prof[5]:.4f} +- {lp_se[5]:.4f}"
        "  (key-free: g^0 = identity)\n"
    )

    words = prose_words()
    print(f"prose: {len(words)} running words\n")

    q = tuned_q(words, lp_share, SEED)
    print(f"absorption rate reproducing the LP 2-rune share: q = {q:.3f}\n")

    models = {
        "REGISTER": register_units(rng, lp_hist),
        "MERGE": merge_units(words, q, random.Random(SEED)),
        "BLIND": blind_units(words, lp_hist, random.Random(SEED)),
    }

    print(
        f"{'model':>10}{'2-rune':>9}{'mean':>7}   "
        + "".join(f"{'d' + str(d):>8}" for d in range(1, DMAX + 1))
    )
    print(
        f"{'LP':>10}{lp_share:>8.1f}%{lp_mean:>7.2f}   "
        + "".join(f"{lp_prof[d]:>8.4f}" for d in range(1, DMAX + 1))
    )
    profs = {}
    for name, units in models.items():
        share, mean = hist(units)
        p = profile(units)
        profs[name] = p
        print(
            f"{name:>10}{share:>8.1f}%{mean:>7.2f}   "
            + "".join(f"{p[d]:>8.4f}" for d in range(1, DMAX + 1))
        )

    print("\nd5 is the only cell no key can move. Each model's d5 IS its prediction.")
    print(f"{'model':>10}{'predicts d5':>14}{'LP observed':>14}{'z':>9}")
    for name, p in profs.items():
        z = (lp_prof[5] - p[5]) / lp_se[5]
        print(f"{name:>10}{p[5]:>14.4f}{lp_prof[5]:>14.4f}{z:>9.2f}")

    print("\nThe d5 comparison carries only the LP's binomial error; the reference")
    print("rests on >1e5 pairs. A model is preferred if its d5 lands inside +-2.")

    # Merging is a one-parameter family; report the sensitivity rather than one q.
    print(f"\nsensitivity of MERGE d5 to the absorption rate (q tuned to {q:.3f}):")
    for qq in (0.0, 0.2, q, 0.6, 0.8, 1.0):
        u = merge_units(words, qq, random.Random(SEED))
        share, _ = hist(u)
        p5 = profile(u)[5]
        z = (lp_prof[5] - p5) / lp_se[5]
        tag = "  <- tuned to the 2-rune share" if abs(qq - q) < 1e-9 else ""
        print(
            f"   q = {qq:.3f}  2-rune {share:5.1f}%   d5 {p5:.4f}   z = {z:+.2f}{tag}"
        )


if __name__ == "__main__":
    main()
