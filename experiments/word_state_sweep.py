# ABOUTME: Broad sweep of word-level base-indexing schemes: any visible state
# ABOUTME: function x any modulus x both phase conventions, bucketed coincidence.
"""Everything so far indexed the per-word base by WORD COUNT (base_w = disk^w).
That is only one of many compact schemes, and not the most natural one for a
hand-operated device.

The general principle: if the alphabet is a function of some state S that a
solver can compute from visible data, then two runes sharing (S, phase) share
an alphabet, and their coincidence is the plaintext's (~0.060) rather than
1/29. So any candidate S can be tested by bucketing -- no key, no search.

Schemes swept here:

  w              disk turned once per word          (the baseline, done before)
  A              disk turned L_w times per word     <- letter-clocked disk
  A - w          disk turned (L_w - 1) times        <- the walk's own increment
  A + w          disk turned (L_w + 1) times
  L              base is the word's OWN length      (14 classes, no modulus)
  prevL          base is the previous word's length
  sent_idx       disk stepped once per sentence
  w_in_sent      position of the word within its sentence
  sec_idx        disk stepped once per section
  w_in_sec       position of the word within its section
  line_idx       disk stepped once per line
  w_in_line      position of the word within its line
  (w, A)         TWO disks, one per word and one per letter  <- 841 states

crossed with both phase conventions (reset per word / continuous) and every
modulus that leaves enough pairs.

Planted controls for a word-clocked and a letter-clocked disk, so the nulls
are worth something.
"""

from __future__ import annotations

import math
import random
import re
import sys
from pathlib import Path

import numpy as np

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

N = 29
CHANCE = 1.0 / N
RUNE = re.compile(r"[ᚠ-᛿]")
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
SENTENCE_MARKS = {"④", "⑬", "⑩", "③", "⑤", "."}


def load_rich() -> dict[str, np.ndarray]:
    """Per-rune geometry: word/line/sentence/section indices and positions."""
    text = (ROOT / "data" / "page0-56.txt").read_text()
    secs = [s for s in text.split("$") if RUNE.search(s)][:10]
    runes: list[int] = []
    wi: list[int] = []
    li: list[int] = []
    si: list[int] = []
    ci: list[int] = []
    w = ln = sent = 0
    for sec_no, s in enumerate(secs):
        started = False
        for ch in s:
            if RUNE.match(ch):
                runes.append(IDX[ch])
                wi.append(w)
                li.append(ln)
                si.append(sent)
                ci.append(sec_no)
                started = True
            elif ch == "\n" or ch == "/":
                ln += 1
            elif ch in c3301.WORD_BOUNDARY:
                if started:
                    w += 1
                    started = False
                if ch in SENTENCE_MARKS:
                    sent += 1
        if started:
            w += 1
        sent += 1
        ln += 1
    a = {k: np.asarray(v, dtype=np.int64) for k, v in
         (("rune", runes), ("w", wi), ("line", li), ("sent", si), ("sec", ci))}
    nw = int(a["w"][-1]) + 1
    lens = np.bincount(a["w"], minlength=nw)
    starts = np.concatenate([[0], np.cumsum(lens)[:-1]])
    a["j"] = np.arange(len(runes)) - starts[a["w"]]
    a["A"] = starts[a["w"]]
    a["i"] = np.arange(len(runes))
    a["L"] = lens[a["w"]]
    prev = np.concatenate([[0], lens[:-1]])
    a["prevL"] = prev[a["w"]]
    # word ordinal within sentence / section / line
    for key, src in (("w_in_sent", "sent"), ("w_in_sec", "sec"), ("w_in_line", "line")):
        first_w: dict[int, int] = {}
        vals = np.empty(nw, dtype=np.int64)
        srcw = np.zeros(nw, dtype=np.int64)
        for idx in range(len(runes)):
            srcw[a["w"][idx]] = a[src][idx]
        for ww in range(nw):
            g = int(srcw[ww])
            first_w.setdefault(g, ww)
            vals[ww] = ww - first_w[g]
        a[key] = vals[a["w"]]
    a["lens"] = lens
    return a


def pooled(codes: np.ndarray, keys: np.ndarray) -> tuple[int, int]:
    keys = keys - keys.min()
    nb = int(keys.max()) + 1
    counts = np.bincount(keys * N + codes, minlength=nb * N)
    sizes = np.bincount(keys, minlength=nb)
    return int((counts * (counts - 1) // 2).sum()), int((sizes * (sizes - 1) // 2).sum())


def z(h: int, t: int, p: float = CHANCE) -> float:
    return (h - t * p) / math.sqrt(t * p * (1 - p)) if t else float("nan")


def state_functions(a: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    return {
        "w": a["w"],
        "A": a["A"],
        "A-w": a["A"] - a["w"],
        "A+w": a["A"] + a["w"],
        "L": a["L"],
        "prevL": a["prevL"],
        "sent_idx": a["sent"],
        "w_in_sent": a["w_in_sent"],
        "sec_idx": a["sec"],
        "w_in_sec": a["w_in_sec"],
        "line_idx": a["line"],
        "w_in_line": a["w_in_line"],
    }


def sweep(
    a: dict[str, np.ndarray],
    codes: np.ndarray,
    min_pairs: int = 3000,
    qs: tuple[int, ...] = (5,),
):
    """qs = candidate letter-step ORDERS. q=1 means no letter step at all."""
    out = []
    for sname, sv in state_functions(a).items():
        span = int(sv.max()) + 1
        mods = [m for m in range(2, 61) if m <= span] or [span]
        if sname in ("L", "prevL"):
            mods = [span]  # use the raw class, not a modulus
        for q in qs:
            phases = {"reset": a["j"] % q, "cont": a["i"] % q}
            for m in mods:
                for pname, pv in phases.items():
                    if q == 1 and pname == "cont":
                        continue  # identical to reset when q == 1
                    keys = (sv % m) * q + pv
                    h, t = pooled(codes, keys)
                    if t < min_pairs:
                        continue
                    label = sname if q == 5 else f"{sname}|q={q}"
                    out.append((z(h, t), label, m, pname, h, t))
    # the two-disk machine: state = (w mod 29, A mod 29) -> 841 classes
    for pname, pv in {"reset": a["j"] % 5, "cont": a["i"] % 5}.items():
        keys = ((a["w"] % 29) * 29 + (a["A"] % 29)) * 5 + pv
        h, t = pooled(codes, keys)
        if t >= 1000:
            out.append((z(h, t), "(w,A) two-disk", 841, pname, h, t))
    out.sort(reverse=True)
    return out


def leak_bound(nioc: float) -> float:
    """Fraction of pairs that could be sharing an alphabet, given nIoC."""
    return max(0.0, (nioc - 1.0) / (1.74 - 1.0))


def plant(a: dict[str, np.ndarray], state: np.ndarray, mod: int, rng: random.Random):
    pts = list(range(N))
    rng.shuffle(pts)
    g = list(range(N))
    for c in range(5):
        cyc = pts[5 * c : 5 * c + 5]
        for t in range(5):
            g[cyc[t]] = cyc[(t + 1) % 5]
    gp = [list(range(N))]
    for _ in range(4):
        gp.append([g[x] for x in gp[-1]])
    order = list(range(N))
    rng.shuffle(order)
    disk = list(range(N))
    for t in range(N):
        disk[order[t]] = order[(t + 1) % N]
    dp = [list(range(N))]
    for _ in range(mod - 1):
        dp.append([disk[x] for x in dp[-1]])
    wts = np.array([1.0 / (1 + k) ** 1.6 for k in range(N)])
    wts /= wts.sum()
    pool = np.random.default_rng(5)
    pt = pool.choice(N, size=len(a["rune"]), p=wts)
    st = state % mod
    ph = a["j"] % 5
    return np.array([dp[st[k] % len(dp)][gp[ph[k]][pt[k]]] for k in range(len(pt))])


def main() -> None:
    a = load_rich()
    print(f"corpus: {len(a['rune'])} runes, {int(a['w'][-1]) + 1} words, "
          f"{int(a['sec'][-1]) + 1} sections, {int(a['sent'][-1]) + 1} sentences, "
          f"{int(a['line'][-1]) + 1} lines")
    print("chance nIoC 1.000; a shared alphabet ~1.74\n")

    print("POSITIVE CONTROLS")
    for label, st, m in (("word-clocked disk (w mod 29)", a["w"], 29),
                         ("letter-clocked disk (A mod 29)", a["A"], 29)):
        planted = plant(a, st, m, random.Random(3301))
        res = sweep(a, planted)
        zz, sn, mm, pn, h, t = res[0]
        print(f"  planted {label:<32} top hit: {sn} mod {mm} [{pn}]  "
              f"nIoC {h / t * N:.2f}  z={zz:+.0f}")
    print("  -> the sweep recovers both planted machines\n")

    res = sweep(a, a["rune"])
    print(f"THE LP: {len(res)} (state, modulus, phase) cells")
    print("  strongest 12:")
    for zz, sn, m, pn, h, t in res[:12]:
        print(f"    {sn:<16} mod {m:>3} [{pn:<5}] nIoC {h / t * N:.3f}  z={zz:+5.2f}  ({t} pairs)")
    print("  weakest 3:")
    for zz, sn, m, pn, h, t in res[-3:]:
        print(f"    {sn:<16} mod {m:>3} [{pn:<5}] nIoC {h / t * N:.3f}  z={zz:+5.2f}")
    mx = max(abs(r[0]) for r in res)
    print(f"\n  scan max |z| {mx:.2f}; noise expects ~{math.sqrt(2 * math.log(len(res))):.2f}")

    print("\n  the named schemes, best modulus each:")
    best: dict[str, tuple] = {}
    for zz, sn, m, pn, h, t in res:
        if sn not in best:
            best[sn] = (zz, m, pn, h, t)
    for sn, (zz, m, pn, h, t) in sorted(best.items(), key=lambda kv: -kv[1][0]):
        print(f"    {sn:<16} best mod {m:>3} [{pn:<5}] nIoC {h / t * N:.3f}  z={zz:+5.2f}")

    # Effect size is the real argument, not significance: a genuine shared
    # alphabet gives nIoC ~1.74 by construction, so bound how much sharing
    # the best cell could possibly represent.
    top = res[0]
    nioc = top[4] / top[5] * N
    print(
        f"\n  EFFECT SIZE: the best cell reaches nIoC {nioc:.3f}. A real state "
        f"variable\n  gives 1.74 by construction, so at most "
        f"{leak_bound(nioc) * 100:.1f}% of its pairs could be sharing an\n"
        f"  alphabet -- it cannot be a base-indexing scheme at any significance."
    )

    # --- relax the period-5 premise ----------------------------------------
    print("\n--- letter-step order q relaxed (q=1 means NO letter step) ---")
    res2 = sweep(a, a["rune"], qs=(1, 2, 3, 4, 5, 6, 7, 8))
    print(f"  {len(res2)} cells swept")
    for zz, sn, m, pn, h, t in res2[:8]:
        print(f"    {sn:<20} mod {m:>3} [{pn:<5}] nIoC {h / t * N:.3f}  z={zz:+5.2f}")
    mx2 = max(abs(r[0]) for r in res2)
    print(f"  scan max |z| {mx2:.2f}; noise expects "
          f"~{math.sqrt(2 * math.log(len(res2))):.2f}")
    q1 = [r for r in res2 if "|q=1" in r[1]]
    if q1:
        zz, sn, m, pn, h, t = q1[0]
        print(f"  best PURE word-state cell (no letter step at all): {sn} mod {m} "
              f"nIoC {h / t * N:.3f}  z={zz:+.2f}")


if __name__ == "__main__":
    main()
