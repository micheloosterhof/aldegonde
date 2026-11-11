# ABOUTME: Any-tableau keystream test on the HEADS of pages, sections and lines, where a
# ABOUTME: key that restarts per unit is still aligned before a key-skipping preventer slips.
"""A restarting key under a key-skipping preventer, under any tableau.

`any_tableau_keystream.py` needs a fixed alignment and `slip_tolerant_keystream.py`
needs the rune order. The cell between them, a key-skipping preventer WITH mixed
alphabets, is reachable without either when the key restarts at a unit: a would-be
repeat arises once in 29 runes, so the first few dozen runes of every unit are still
aligned with the first few dozen key terms, and there are many units. The table of
(cipher rune, key residue) over those heads alone is dependent under any tableau.

Units: pages (55), sections (10) and lines (the key restarts at each line, whole lines
kept: a line is short enough to be mostly aligned). Heads of 20, 36 and 60 runes for
pages and sections. The same 34 generators, three bases and start terms to 300.

The first two runes of every written line are left out of every table: their
distribution is set by glyph width (`line-initial-bias.md`), and a key whose early terms
label those positions apart reads that typesetting as dependence (the first run of this
script found "n!" and "prime gap" on lines that way, at +7.3 and +6.1).

What the null keeps and destroys: surrogate bodies from `c3301.low_doublet_null` keep
rune counts and the doublet rate and destroy the order; the best cell of the whole scan
is taken on each.

The control plants a Quagmire IV (two random alphabets) under prime(n)-1 restarting at
every page, with the key-skipping dodge, on the author's words at the body's block
lengths. It must be found on the page heads, and the script prints what the same key
reads over whole pages at a fixed alignment, which is the cell this test adds.

    python experiments/any_tableau_unit_heads.py
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
from any_tableau_keystream import independence_z  # noqa: E402
from slip_tolerant_keystream import BASES, base_index, generators  # noqa: E402

from aldegonde import c3301  # noqa: E402
from aldegonde.maths import permutation  # noqa: E402

M = 29
SEED = 20261115
STARTS = 300
HEADS = (20, 36, 60)
SURROGATES = 8
LINE_SKIP = 2  # runes at the start of each written line left out of every table


def cases(tok) -> dict[tuple[str, str], tuple[np.ndarray, np.ndarray]]:
    """(layout, base) -> (key index before the start term, mask of runes used)."""
    word = np.array(tok.word, dtype=np.int64)
    n = len(word)
    labels = {
        "pages": np.array(tok.page),
        "sections": np.array(tok.section),
        "lines": np.array(tok.line),
    }
    # the first runes of a written line are set by glyph width (`line-initial-bias.md`):
    # chi-square 81.6 on 28 df at the first rune, 44.9 at the second. Any key whose
    # early terms label those positions apart reads that as dependence, so they are
    # left out of every table.
    line_position = np.empty(n, dtype=np.int64)
    for u in np.unique(labels["lines"]):
        idx = np.flatnonzero(labels["lines"] == u)
        line_position[idx] = np.arange(len(idx))
    usable = line_position >= LINE_SKIP
    out = {}
    for unit, label in labels.items():
        unit_list = [np.flatnonzero(label == u) for u in np.unique(label)]
        position = np.empty(n, dtype=np.int64)
        for idx in unit_list:
            position[idx] = np.arange(len(idx))
        for kind in BASES:
            base = np.empty(n, dtype=np.int64)
            for idx in unit_list:
                base[idx] = base_index(word, idx, kind)
            if unit == "lines":
                out[unit, kind] = (base, usable)
            else:
                for h in HEADS:
                    out[f"{unit}, first {h}", kind] = (base, (position < h) & usable)
                out[f"{unit}, whole", kind] = (base, usable)
    return out


def scan(text: np.ndarray, case_map, gens, starts: int = STARTS) -> dict:
    out = {}
    for (layout, kind), (base, mask) in case_map.items():
        c = text[mask]
        b = base[mask]
        for g, key in gens.items():
            best = (-1e9, 0)
            for start in range(starts):
                z = independence_z(c, key[b + start])
                if z > best[0]:
                    best = (z, start)
            out[g, layout, kind] = best
    return out


def plant(tok, key, rng) -> np.ndarray:
    """Quagmire IV under a key that restarts at every page, with the key-skipping dodge."""
    a = permutation.random_permutation(M, rng)
    b = permutation.random_permutation(M, rng)
    pools: dict[int, list[list[int]]] = {}
    for w in lp_plaintext_register.corpus():
        pools.setdefault(len(w), []).append(w)
    page = tok.page
    out: list[int] = []
    j, prev, i = 0, -1, 0
    for w in tok.words():
        L = len(w)
        LL = L
        while LL not in pools:
            LL -= 1
        src = rng.choice(pools[LL])
        for r in (src * (L // len(src) + 1))[:L]:
            if i and page[i] != page[i - 1]:
                j = 0
            c = a[(b[r] + int(key[j])) % M]
            if c == prev:
                j += 1
                c = a[(b[r] + int(key[j])) % M]
            out.append(c)
            prev = c
            j += 1
            i += 1
    return np.array(out, dtype=np.int64)


_W: dict = {}


def _init(case_map, gens) -> None:
    _W.update(case_map=case_map, gens=gens)


def _run(text):
    return scan(text, _W["case_map"], _W["gens"])


def main() -> None:
    rng = random.Random(SEED)
    tok = lp_corpus.load_tokenized()
    cipher = np.array(tok.stream, dtype=np.int64)
    n = len(cipher)
    gens = generators(n + len(tok.words()) + STARTS + 10)
    case_map = cases(tok)
    print(
        f"body: {n:,} runes; {len(gens)} generators x {len(case_map)} cases, each the "
        f"best of {STARTS} start terms\n"
    )

    planted = plant(tok, gens["prime(n)-1"], rng)
    ctrl = scan(planted, case_map, {"prime(n)-1": gens["prime(n)-1"]})
    print("control: Quagmire IV, prime(n)-1 restarting per page, key-skipping dodge")
    heads_ok = False
    for layout in (*(f"pages, first {h}" for h in HEADS), "pages, whole"):
        z, start = ctrl["prime(n)-1", layout, "runes"]
        heads_ok = heads_ok or (layout != "pages, whole" and z > 8 and start == 0)
        print(f"  {layout:<18} z {z:+7.2f} at start {start}")
    print()

    null_model = c3301.low_doublet_null()
    texts = [cipher] + [
        np.array(null_model(tok.stream, rng), dtype=np.int64) for _ in range(SURROGATES)
    ]
    with Pool(4, initializer=_init, initargs=(case_map, gens)) as pool:
        results = pool.map(_run, texts)
    body = results[0]
    vals = np.array([v[0] for v in body.values()])
    null_max = np.array([max(v[0] for v in r.values()) for r in results[1:]])
    print("the body, best cells:")
    for (g, layout, kind), (z, start) in sorted(body.items(), key=lambda kv: -kv[1][0])[
        :6
    ]:
        print(f"  {z:+6.2f}  {g:<30}{layout:<20}{kind:<8} start {start}")
    beaten = int((null_max >= vals.max()).sum())
    print(
        f"\nbody: best {vals.max():+.2f} of {len(vals)} cells; surrogate bodies: best "
        f"{null_max.mean():+.2f} +- {null_max.std(ddof=1):.2f} "
        f"({null_max.min():+.2f} to {null_max.max():+.2f})"
    )
    if not heads_ok:
        print(
            "VERDICT: the control was not found on the page heads; the negative means nothing."
        )
    elif vals.max() > null_max.max() + 3 * null_max.std(ddof=1):
        print(
            "VERDICT: a cell stands clear of the surrogates. Solve its alphabets on the heads."
        )
    else:
        print(
            f"VERDICT: no generator restarting at a page, section or line selects the "
            f"body's alphabet under any tableau, key-skipping preventer included: the "
            f"body's best cell is reached by {beaten} of {SURROGATES} surrogate bodies."
        )


if __name__ == "__main__":
    main()
