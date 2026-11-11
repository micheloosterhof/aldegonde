# ABOUTME: Sweeps keyword-mixed alphabets through the slip-tolerant keystream alignment:
# ABOUTME: a Quagmire under a number-sequence key with a key-skipping preventer.
"""The cell left by the two keystream tests, for keyword alphabets.

`slip_tolerant_keystream.py` survives any key slips but needs the standard rune order;
`any_tableau_keystream.py` survives any alphabets but needs a fixed alignment. A
key-skipping preventer with a mixed alphabet under a key that runs on is neither. For
an arbitrary alphabet that needs a joint search; for a KEYWORD alphabet it is a sweep,
because the alphabet is one of a short list and each one is a single alignment.

Alphabets: the four constructions of `keyword_exhaustion.alphabets` over 3301's own
vocabulary (`quagmire_ungated_sweep.priority_vocabulary`). Three placements:

  plain    the plaintext alphabet is keyed, the cipher alphabet standard (Quagmire I)
  cipher   the cipher alphabet is keyed (Quagmire II)
  both     the same keyed alphabet on both sides (Quagmire III)

Generators: those of `slip_tolerant_keystream.generators` whose residues can give the
body's flat rune counts at all. The cipher's rune distribution is the plaintext's
convolved with the key's, in whatever order the alphabets impose, so a key with uneven
residues leaves uneven counts; the filter prints what each would leave. Generators that
differ by a constant are one class under the 29 offsets and are run once.

The alignment is `slip_tolerant_keystream.best_paths` on the first PREFIX runes, with
29 offsets, three senses, and two bases (a rune eats a key term; a space eats one too).

The null is the sweep itself: all but at most one alphabet is wrong, so each (generator,
placement, base) cell has a thousand wrong keys of its own, and a true key is an outlier
against them. The best alphabet of the best cell is still the best of some 140,000 tries,
so the opening alone cannot name a key: the top cells are re-scored on the WHOLE body
against surrogate bodies, where a true key keeps gaining 0.4 nats a rune and a lucky fit
of the opening does not. The control plants a Quagmire III under prime(n)-1 with the
key-skipping dodge, the keyword drawn from the same vocabulary, and must be the sweep's
top outlier.

    python experiments/keyed_alphabet_slips.py [workers]
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
from keyword_exhaustion import alphabets, kw_runes  # noqa: E402
from quagmire_ungated_sweep import priority_vocabulary  # noqa: E402
from slip_tolerant_keystream import (  # noqa: E402
    SLIP_PENALTY,
    STALL_PENALTY,
    best_paths,
    emission_tables,
    generators,
    plaintext_llr,
)

from aldegonde import c3301  # noqa: E402

M = 29
SEED = 20261116
PREFIX = 2000
SLACK = 160
FLAT_EXCESS = (
    28.0  # predicted chi-square excess a generator may leave in the rune counts
)
PLACEMENTS = ("plain", "cipher", "both")
BASES = ("runes", "spaces")
CONTROL_SAMPLE = 200  # wrong alphabets the control is scored on beside its planted one
EXTENSION_CELLS = 5  # top cells of the opening re-scored on the whole body
EXTENSION_SURROGATES = 30
EXTENSION_HIT = 10.0  # z on the whole body a true key clears many times over
WHOLE_SLACK = 900


def flat_generators(
    gens, llr, n
) -> tuple[dict[str, np.ndarray], list[tuple[str, float]]]:
    """Generators whose residues can leave flat rune counts, one per offset class."""
    p = np.exp(llr) / M
    shown, kept, seen = [], {}, set()
    for name, key in gens.items():
        kd = np.bincount(key[:n], minlength=M) / n
        q = np.array([sum(p[(c - j) % M] * kd[j] for j in range(M)) for c in range(M)])
        excess = float(n * M * ((q - 1 / M) ** 2).sum())
        shown.append((name, excess))
        if excess > FLAT_EXCESS:
            continue
        head = key[:200]
        klass = tuple(((head - head[0]) % M).tolist())
        if klass in seen:
            continue
        seen.add(klass)
        kept[name] = key
    return kept, shown


def keyed_alphabets() -> list[tuple[str, tuple[int, ...]]]:
    out, seen = [], set()
    for word in priority_vocabulary():
        seq = kw_runes(word)
        if not seq:
            continue
        for rule, alphabet in alphabets(seq):
            t = tuple(alphabet)
            if t not in seen:
                seen.add(t)
                out.append((f"{word}, {rule}", t))
    return out


def arrange(cipher: np.ndarray, llr: np.ndarray, alphabet, placement: str):
    """The cipher stream and emission tables for one alphabet in one placement."""
    kappa = np.array(alphabet)
    pos = np.empty(M, dtype=np.int64)
    pos[kappa] = np.arange(M)
    c = pos[cipher] if placement in ("cipher", "both") else cipher
    table = llr[kappa] if placement in ("plain", "both") else llr
    return c, emission_tables(table)


def base_of(word: np.ndarray, kind: str) -> np.ndarray:
    local = np.arange(len(word), dtype=np.int64)
    return local + (word - word[0]) if kind == "spaces" else local


_W: dict = {}


def _init(texts, word, llr, gens, control_set) -> None:
    _W.update(texts=texts, word=word, llr=llr, gens=gens, control_set=control_set)


def _task(args):
    """One alphabet: best (sense, offset) score for every text, generator, placement, base."""
    name, alphabet = args
    w = _W
    out = {}
    for label, text in w["texts"].items():
        if label == "control" and name not in w["control_set"]:
            continue
        for placement in PLACEMENTS:
            c, tabs = arrange(text, w["llr"], alphabet, placement)
            for kind in BASES:
                base = base_of(w["word"], kind)
                for g, key in w["gens"].items():
                    out[label, g, placement, kind] = float(
                        best_paths(
                            c,
                            base,
                            key,
                            tabs[0],
                            tabs[1],
                            SLACK,
                            SLIP_PENALTY,
                            STALL_PENALTY,
                        ).max()
                    )
    return name, out


def plant(lens, key, alphabet, rng) -> np.ndarray:
    """Quagmire III under the key with the key-skipping dodge."""
    kappa = list(alphabet)
    pos = [0] * M
    for i, r in enumerate(kappa):
        pos[r] = i
    pools: dict[int, list[list[int]]] = {}
    for w in lp_plaintext_register.corpus():
        pools.setdefault(len(w), []).append(w)
    out: list[int] = []
    j, prev = 0, -1
    for L in lens:
        LL = L
        while LL not in pools:
            LL -= 1
        src = rng.choice(pools[LL])
        for r in (src * (L // len(src) + 1))[:L]:
            c = kappa[(pos[r] + int(key[j])) % M]
            if c == prev:
                j += 1
                c = kappa[(pos[r] + int(key[j])) % M]
            out.append(c)
            prev = c
            j += 1
    return np.array(out, dtype=np.int64)


def main() -> None:
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    rng = random.Random(SEED)
    tok = lp_corpus.load_tokenized()
    cipher = np.array(tok.stream, dtype=np.int64)[:PREFIX]
    word = np.array(tok.word, dtype=np.int64)[:PREFIX]
    lens = [len(w) for w in tok.words()]
    llr = plaintext_llr()
    need = PREFIX + int(word[-1]) + SLACK + 10
    full, shown = flat_generators(
        generators(len(tok.stream) + len(lens) + 910), llr, len(tok.stream)
    )
    gens = {k: v[:need] for k, v in full.items()}
    print(
        "rune-count chi-square excess each generator would leave on the body (it has none):"
    )
    for name, excess in shown:
        mark = "" if excess <= FLAT_EXCESS else "   excluded by the flat counts"
        print(f"  {name:<30}{excess:>9.1f}{mark}")
    alph = keyed_alphabets()
    print(
        f"\n{len(alph)} keyed alphabets x {len(PLACEMENTS)} placements x {len(BASES)} bases x "
        f"{len(gens)} generator classes on the first {PREFIX} runes, slack {SLACK}\n"
    )

    plant_name, plant_alphabet = alph[rng.randrange(len(alph))]
    planted = plant(lens, full["prime(n)"], plant_alphabet, rng)[:PREFIX]
    texts = {"body": cipher, "control": planted}

    scores: dict[tuple, list[float]] = {}
    names: list[str] = []
    # the control is scored on its planted alphabet and CONTROL_SAMPLE others
    others = [name for name, _ in alph if name != plant_name]
    control_set = {plant_name, *rng.sample(others, CONTROL_SAMPLE)}
    cell_names: dict[tuple, list[str]] = {}
    args = (texts, word, llr, gens, control_set)
    with Pool(nproc, initializer=_init, initargs=args) as pool:
        for name, out in pool.imap(_task, alph, chunksize=8):
            names.append(name)
            for cell, v in out.items():
                scores.setdefault(cell, []).append(v)
                cell_names.setdefault(cell, []).append(name)

    def outliers(label: str):
        rows = []
        for cell, vals in scores.items():
            if cell[0] != label:
                continue
            v = np.array(vals)
            med = np.median(v)
            mad = 1.4826 * np.median(np.abs(v - med))
            i = int(v.argmax())
            rows.append(
                (
                    (v[i] - med) / mad,
                    cell_names[cell][i],
                    cell[1:],
                    float(v[i]),
                    float(med),
                    float(mad),
                )
            )
        rows.sort(reverse=True)
        return rows

    ctrl = outliers("control")
    z, name, cell, top, med, mad = ctrl[0]
    control_ok = name == plant_name and z > 20
    print(
        f"control (planted: {plant_name}, both, prime(n)): top outlier {name}, "
        f"{cell[1]}, {cell[0]}, base {cell[2]}: {top:.0f} against {med:.0f} +- {mad:.0f}, "
        f"robust z {z:+.1f}"
    )
    body = outliers("body")
    print("\nthe body, best alphabet of each cell, top cells by robust z:")
    for z, name, cell, top, med, mad in body[:6]:
        print(
            f"  {z:+6.2f}  {name:<28}{cell[1]:<8}{cell[0]:<30}{cell[2]:<8}"
            f"{top:.0f} against {med:.0f} +- {mad:.0f}"
        )
    zs = np.array([r[0] for r in body])
    print(
        f"\n{len(body)} cells of {len(names)} alphabets each: best alphabet's robust z "
        f"mean {zs.mean():+.2f}, sd {zs.std(ddof=1):.2f}, max {zs.max():+.2f}; the "
        f"control's planted key reads {ctrl[0][0]:+.1f}"
    )

    # A cell's best alphabet is the best of a thousand, and the top cell the best of
    # all of them, so the prefix alone cannot name a key. A true key keeps paying on
    # the rest of the body; noise does not. Re-score the top cells on the whole body
    # against surrogate bodies.
    whole = np.array(tok.stream, dtype=np.int64)
    whole_word = np.array(tok.word, dtype=np.int64)
    null_model = c3301.low_doublet_null()
    surrogates = [
        np.array(null_model(tok.stream, rng), dtype=np.int64)
        for _ in range(EXTENSION_SURROGATES)
    ]
    lookup = dict(alph)
    print("\nthe top cells re-scored on the whole body against surrogate bodies:")
    extension = []
    for _z, name, cell, _top, _med, _mad in body[:EXTENSION_CELLS]:
        g, placement, kind = cell
        vals = []
        for text in (whole, *surrogates):
            c, tabs = arrange(text, llr, lookup[name], placement)
            vals.append(
                float(
                    best_paths(
                        c,
                        base_of(whole_word, kind),
                        full[g],
                        tabs[0],
                        tabs[1],
                        WHOLE_SLACK,
                        SLIP_PENALTY,
                        STALL_PENALTY,
                    ).max()
                )
            )
        sur = np.array(vals[1:])
        ze = (vals[0] - sur.mean()) / sur.std(ddof=1)
        extension.append(ze)
        print(
            f"  {name:<28}{placement:<8}{g:<30}{kind:<8}{vals[0]:.0f} against "
            f"{sur.mean():.0f} +- {sur.std(ddof=1):.0f}, z {ze:+.2f}"
        )
    if not control_ok:
        print(
            "VERDICT: the control's planted key was not the top outlier; the negative "
            "means nothing."
        )
    elif max(extension) > EXTENSION_HIT:
        print(
            "VERDICT: a top cell keeps paying on the whole body. Decrypt along its path."
        )
    else:
        print(
            "VERDICT: no keyword alphabet from 3301's vocabulary, in any of three "
            "placements, aligns the body with a number-sequence key under key skips and "
            f"stalls: the opening's best cells do not extend (best z {max(extension):+.2f} "
            f"on the whole body, where the control's key would read in the hundreds)."
        )


if __name__ == "__main__":
    main()
