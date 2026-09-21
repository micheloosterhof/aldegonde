# ABOUTME: Sweeps deterministic integer sequences as additive keystreams, scoring the
# ABOUTME: decrypted PREFIX so a downstream interrupter cannot hide a correct generator.
"""The old sequence sweep could not have found the author's own keystream.

`running-key-math-sequence.md` reports eight sequences tried in both senses at all 29
offsets, every combination indistinguishable from random. Three things were missing.

**Interrupt tolerance.** The score was the index of coincidence of the whole decrypted
text. The author interrupts his keystream (`interrupter-is-a-scribal-mark`), and after
the first interrupt every later rune is decrypted against the wrong key letter. On the
solved AN END page one interrupt at position 56 ruins the remaining 29 runes. Scoring a
PREFIX fixes this: only the stretch before the first interrupt has to be right.

**Sequence phase.** The sweep varied the alphabet offset but always started the sequence
at its first term. A keystream that begins at prime number 40 was never tried.

**A scorer with enough power.** The cheap score is the unigram chi2 of the decrypted
prefix, which is invariant to the alphabet offset and to the Beaufort reflection and so
covers 58 variants at once. On the real AN END page it works: the true generator scores
92.1 against a best false of 72.4 and ranks first of 4,800. Runeglish trigrams separate
the same case far more widely -- +14.25 against +10.99 -- at the cost of having to try
all 29 offsets and both senses explicitly. The scan ranks on trigrams; chi2 remains a
sound 58x cheaper prefilter.

Scope. This tests ADDITIVE keystreams over the standard rune order, which is what the
author uses on the solved pages. A mixed alphabet in the loop does not linearize under
subtraction and is untouched.

    python sequence_key_sweep.py [--control] [--prefix 57] [--starts 200]
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

M = 29
TERMS = 4000


def _sieve(n: int) -> np.ndarray:
    flag = np.ones(n + 1, dtype=bool)
    flag[:2] = False
    for i in range(2, int(n**0.5) + 1):
        if flag[i]:
            flag[i * i :: i] = False
    return np.flatnonzero(flag)


def generators() -> dict[str, np.ndarray]:
    """Deterministic integer sequences, as residues mod 29."""
    n = np.arange(1, TERMS + 1, dtype=np.int64)
    pr = _sieve(200000)[:TERMS]
    seqs: dict[str, np.ndarray] = {
        "n": n,
        "n^2": n * n,
        "n^3": n**3 % M,
        "triangular": n * (n + 1) // 2,
        "prime(n)": pr,
        "prime(n)-1": pr - 1,
        "prime(n)+1": pr + 1,
        "prime index in GP": np.arange(TERMS) % M,
        "prime gap": np.diff(_sieve(200000)[: TERMS + 1]),
        "2^n": np.array([pow(2, int(i), M) for i in n]),
        "3^n": np.array([pow(3, int(i), M) for i in n]),
        "n!": np.array([1] * TERMS),
        "central binomial": np.array([1] * TERMS),
    }
    fact = 1
    f = []
    for i in range(1, TERMS + 1):
        fact = fact * i % M
        f.append(fact)
    seqs["n!"] = np.array(f)
    a, b, fib, luc = 0, 1, [], []
    x, y = 2, 1
    for _ in range(TERMS):
        fib.append(a)
        luc.append(x)
        a, b = b, (a + b) % M
        x, y = y, (x + y) % M
    seqs["fibonacci"] = np.array(fib)
    seqs["lucas"] = np.array(luc)
    p, q, r = 1, 1, 1
    pad = []
    for _ in range(TERMS):
        pad.append(p)
        p, q, r = q, r, (p + q) % M
    seqs["padovan"] = np.array(pad)
    u, v = 0, 1
    pell = []
    for _ in range(TERMS):
        pell.append(u)
        u, v = v, (2 * v + u) % M
    seqs["pell"] = np.array(pell)
    cat, c = [], 1
    for i in range(TERMS):
        cat.append(c % M)
        c = c * 2 * (2 * i + 1) // (i + 2)
        if i > 40:
            break
    seqs.pop("central binomial")
    # multiplicative functions
    spf = np.arange(TERMS + 1)
    for i in range(2, int(TERMS**0.5) + 1):
        if spf[i] == i:
            for j in range(i * i, TERMS + 1, i):
                if spf[j] == j:
                    spf[j] = i
    tot, dvc, dvs, mob = [], [], [], []
    for i in range(1, TERMS + 1):
        x, t, d, s, sq = i, 1, 1, 1, False
        nf = 0
        while x > 1:
            p0, e = spf[x], 0
            while x % p0 == 0:
                x //= p0
                e += 1
            t *= (p0 - 1) * p0 ** (e - 1)
            d *= e + 1
            s *= (p0 ** (e + 1) - 1) // (p0 - 1)
            nf += 1
            sq = sq or e > 1
        tot.append(t)
        dvc.append(d)
        dvs.append(s)
        mob.append(0 if sq else (-1) ** nf)
    seqs["totient"] = np.array(tot)
    seqs["divisor count"] = np.array(dvc)
    seqs["divisor sum"] = np.array(dvs)
    seqs["moebius"] = np.array(mob)
    seqs["thue-morse"] = np.array([bin(i).count("1") % 2 for i in range(TERMS)])
    seqs["digit sum base 10"] = np.array([sum(int(d) for d in str(i)) for i in n])
    seqs["3301*n"] = 3301 * n
    seqs["n-th rune value"] = np.array([_sieve(200)[i % M] for i in range(TERMS)])
    return {k: (v.astype(np.int64) % M) for k, v in seqs.items()}


TRI: np.ndarray | None = None


def trigram_table() -> np.ndarray:
    """log P(trigram) over the 29 runes, floored for unseen trigrams."""
    global TRI  # noqa: PLW0603
    if TRI is None:
        from aldegonde import c3301  # noqa: PLC0415

        t = np.full(M**3, -9.0)
        alph = c3301.CICADA_ALPHABET
        pos = {r: i for i, r in enumerate(alph)}
        for gram, v in c3301.trigrams.items():
            if len(gram) == 3 and all(c in pos for c in gram):
                t[pos[gram[0]] * 841 + pos[gram[1]] * 29 + pos[gram[2]]] = np.log(v)
        TRI = t
    return TRI


def best_variant(cipher: np.ndarray, key: np.ndarray) -> tuple[float, str, int]:
    """Best runeglish trigram score over 29 alphabet offsets and both senses.

    Vigenere reads p = c - k, Beaufort reads p = k - c; adding an offset to the key
    shifts the result. Neither is visible to a unigram statistic, so both must be
    scored explicitly.
    """
    t = trigram_table()
    d = (cipher - key) % M
    offs = np.arange(M)[:, None]
    variants = np.concatenate([(d + offs) % M, (-d + offs) % M])
    idx = variants[:, :-2] * 841 + variants[:, 1:-1] * 29 + variants[:, 2:]
    scores = t[idx].mean(axis=1)
    j = int(scores.argmax())
    return float(scores[j]), ("vigenere" if j < M else "beaufort"), j % M


def sweep(cipher: np.ndarray, starts: int) -> list[tuple[float, str, int, str, int]]:
    """(score, generator, sequence start, sense, alphabet offset), best first."""
    rows = []
    for name, seq in generators().items():
        for s in range(starts):
            k = seq[s : s + cipher.size]
            if k.size < cipher.size:
                break
            sc, sense, off = best_variant(cipher, k)
            rows.append((sc, name, s, sense, off))
    rows.sort(reverse=True)
    return rows


def main() -> None:
    prefix, starts = 57, 200
    for i, a in enumerate(sys.argv):
        if a == "--prefix" and i + 1 < len(sys.argv):
            prefix = int(sys.argv[i + 1])
        if a == "--starts" and i + 1 < len(sys.argv):
            starts = int(sys.argv[i + 1])

    if "--control" in sys.argv:
        import json  # noqa: PLC0415

        t = json.loads((ROOT / "experiments" / "solved_page_triples.json").read_text())
        page = next(x for x in t if x["cipher"] == "prime running key")
        import re  # noqa: PLC0415

        from aldegonde import c3301  # noqa: PLC0415

        master = (ROOT / "data" / "liber-primus__transcription--master.txt").read_text()
        idx = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
        chunk = master.split("%")[page["page"]]
        runes = [idx[c] for c in chunk if re.match(r"[ᚠ-᛿]", c)]
        cut = page["interrupts"][0]
        cipher = np.array(runes[:cut], dtype=np.int64)
        print(f"POSITIVE CONTROL: AN END, {cipher.size} runes before the first interrupt")
        rows = sweep(cipher, starts)
        for c, name, st, sense, off in rows[:6]:
            print(f"  {c:>+7.3f}  {name:<22} start {st:<4} {sense} offset {off}")
        rank = next(i for i, r in enumerate(rows) if r[1] == "prime(n)-1" and r[2] == 0)
        hit = rows[rank]
        print(f"\n  prime(n)-1 at start 0: score {hit[0]:+.3f}, {hit[3]} offset {hit[4]},"
              f" rank {rank + 1} of {len(rows):,}")
        return

    stream, wid = load_clean()
    print(f"generators: {len(generators())}, starts 0..{starts - 1}, prefix {prefix}\n")
    # word-aligned prefixes: every word start is a candidate keystream origin
    origins = [0]
    for i in range(1, len(stream)):
        if wid[i] != wid[i - 1]:
            origins.append(i)
    best: list[tuple[float, str, int, str, int, int]] = []
    step = max(1, len(origins) // 400)
    for o in origins[::step]:
        cipher = np.array(stream[o : o + prefix], dtype=np.int64)
        if cipher.size < prefix:
            break
        for c, name, st, sense, off in sweep(cipher, starts)[:3]:
            best.append((c, name, st, sense, off, o))
    best.sort(reverse=True)
    print(f"{'score':>8}{'generator':>24}{'start':>7}{'sense':>10}{'off':>5}{'origin':>8}")
    for c, name, st, sense, off, o in best[:12]:
        print(f"{c:>+8.3f}{name:>24}{st:>7}{sense:>10}{off:>5}{o:>8}")


if __name__ == "__main__":
    main()
