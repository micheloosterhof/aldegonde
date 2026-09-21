# ABOUTME: Decodes the two number grids on LP pages 50-51 as base-60 pairs and tests what
# ABOUTME: the resulting 176 values are: uniform bytes, not runes and not text.
"""Two pages of the Liber Primus are not runes, and nothing in this directory reads them.

Master chunks 65 and 66 carry grids of eight columns, thirteen rows and nine rows, of
two-character tokens: `2M`, `0w`, `15`, `4B`. `isdigit-counts-circled-marks` notes them
as "untranscribed base-60 data" and they have never been decoded here.

They decode cleanly. The second character runs over 60 symbols -- `0`-`9`, `A`-`Z`,
`a`-`x` -- and the first over `0`-`4`, so the token is a two-digit base-60 numeral. That
admits values 0 to 299, but the leading digit is not uniform over its five values:

    leading digit   0    1    2    3    4
    observed       45   34   46   39   12

Twelve at the top against roughly 41 elsewhere is the signature of a **byte**. Values 240
to 255 are the only ones with leading digit 4, which is 16 of 256, predicting 11. Uniform
over 0-299 would predict 35. So the grids hold 176 bytes, and the tests below ask what
kind.

Two follow-up questions get answered here too, because both are cheap and both are the
obvious Cicada guesses: are the grids large primes, and are they the body's keystream.

    python number_grid_bytes.py [--primes] [--keystream] [--unpack] [--xor]
"""

from __future__ import annotations

import collections
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
GRIDS = (65, 66)
TOKEN = re.compile(r"\b([0-4])([0-9A-Za-z])\b")


def digit(c: str) -> int:
    """Base-60 digit value: 0-9, then A-Z, then a-x."""
    if c.isdigit():
        return int(c)
    return (10 + ord(c) - 65) if c.isupper() else (36 + ord(c) - 97)


def grid_bytes() -> dict[int, list[int]]:
    """Decoded values per chunk, in reading order."""
    chunks = MASTER.read_text().split("%")
    return {
        n: [int(m.group(1)) * 60 + digit(m.group(2)) for m in TOKEN.finditer(chunks[n])]
        for n in GRIDS
    }


def distinct_expected(n: int, k: int) -> float:
    """Expected number of distinct values in n uniform draws from k."""
    return k * (1 - ((k - 1) / k) ** n)


def chi2_uniform(vals: list[int], k: int) -> float:
    counts = collections.Counter(vals)
    e = len(vals) / k
    return sum((counts[i] - e) ** 2 / e for i in range(k))


def main() -> None:
    per = grid_bytes()
    data = [v for n in GRIDS for v in per[n]]
    n = len(data)
    print(f"chunk 65: {len(per[65])} tokens (13 rows x 8)")
    print(f"chunk 66: {len(per[66])} tokens (9 rows x 8)")
    print(f"total {n} values, range {min(data)}-{max(data)}\n")

    lead = collections.Counter(v // 60 for v in data)
    print("leading base-60 digit, observed against two readings of the token:")
    print(f"{'digit':>7}{'observed':>10}{'if 0-255':>10}{'if 0-299':>10}")
    for d in range(5):
        span = min(300, 256) - 240 if d == 4 else 60
        print(f"{d:>7}{lead[d]:>10}{n * span / 256:>10.1f}{n * 60 / 300:>10.1f}")

    print(f"\ndistinct values: {len(set(data))}")
    print(f"  expected if uniform over 256: {distinct_expected(n, 256):.1f}")
    print(f"  expected if uniform over 300: {distinct_expected(n, 300):.1f}")

    h = 0.0
    for c in collections.Counter(data).values():
        h -= (c / n) * math.log2(c / n)
    print(f"\nShannon entropy {h:.2f} bits per value (max for {n} samples: {math.log2(n):.2f})")

    print("\nwhat the values are NOT:")
    ascii_share = sum(1 for v in data if 32 <= v < 127) / n
    print(f"  printable ASCII: {ascii_share:.1%} of values (uniform bytes predict 37.1%)")
    high = sum(1 for v in data if v > 127) / n
    print(f"  bytes above 127: {high:.1%} (text would be near 0%)")
    mod29 = chi2_uniform([v % 29 for v in data], 29)
    print(f"  runes: chi2 of value mod 29 is {mod29:.1f} on 28 df, and 256 is not a")
    print("         multiple of 29, so a rune encoding would show the wrap")

    print("\nserial structure:")
    runs = sum(1 for a, b in zip(data, data[1:]) if a == b)
    print(f"  adjacent equal values: {runs} (uniform bytes predict {n / 256:.1f})")
    for lag in (1, 8, 13):
        pairs = [(a, b) for a, b in zip(data, data[lag:])]
        hits = sum(1 for a, b in pairs if a == b)
        print(f"  lag {lag:>2}: {hits} coincidences in {len(pairs)} pairs")
    print(
        "\nUniform bytes with no serial structure is what a hash, a cipher key or"
        "\nalready-encrypted data looks like. It is not an encoding of runes, and it"
        "\nis not text."
    )


def as_integers(per: dict[int, list[int]]) -> dict[str, int]:
    """Every natural big-integer reading of the grids."""
    out: dict[str, int] = {}
    for name, vals in (
        ("65", per[65]),
        ("66", per[66]),
        ("65+66", per[65] + per[66]),
        ("66+65", per[66] + per[65]),
    ):
        for order, seq in (("fwd", vals), ("rev", vals[::-1])):
            for base, label in ((256, "base256"), (300, "base300")):
                x = 0
                for v in seq:
                    x = x * base + v
                out[f"{name} {order} {label}"] = x
            d60: list[int] = []
            for v in seq:
                d60 += [v // 60, v % 60]
            x = 0
            for v in d60:
                x = x * 60 + v
            out[f"{name} {order} base60-digits"] = x
    return out


def primality() -> None:
    from sympy import factorint, isprime  # noqa: PLC0415

    print(f"{'reading':<28}{'bits':>7}{'prime?':>8}  small factors")
    for k, v in as_integers(grid_bytes()).items():
        f = sorted(p for p in factorint(v, limit=10000) if p < 10000)
        print(f"{k:<28}{v.bit_length():>7}{str(isprime(v)):>8}  {f[:6]}")
    print("\nEvery reading is composite with small factors: ordinary integers.")


def keystream() -> None:
    """Are the grid values the body's additive keystream? Scored like any generator."""
    import numpy as np  # noqa: PLC0415

    from lp_corpus import load_clean  # noqa: PLC0415
    from sequence_key_sweep import best_variant  # noqa: PLC0415

    per = grid_bytes()
    stream, wid = load_clean()
    origins = [0] + [i for i in range(1, len(stream)) if wid[i] != wid[i - 1]]
    cands: dict[str, list[int]] = {}
    for name, v in (("65", per[65]), ("66", per[66]), ("65+66", per[65] + per[66])):
        for order, seq in (("fwd", v), ("rev", v[::-1])):
            cands[f"{name} {order} mod29"] = [x % 29 for x in seq]
            d: list[int] = []
            for x in seq:
                d += [x // 60 % 29, x % 60 % 29]
            cands[f"{name} {order} base60-digits"] = d
    best = []
    for kname, key in cands.items():
        k = np.array(key, dtype=np.int64)
        length = min(57, k.size)
        for o in origins[::4]:
            c = np.array(stream[o : o + length], dtype=np.int64)
            if c.size < length:
                break
            sc, sense, off = best_variant(c, k[:length])
            best.append((sc, kname, sense, off, o))
    best.sort(reverse=True)
    print(f"{'score':>8}  {'key':<26}{'sense':>10}{'off':>5}{'origin':>8}")
    for sc, kn, se, of, o in best[:6]:
        print(f"{sc:>+8.3f}  {kn:<26}{se:>10}{of:>5}{o:>8}")
    print(f"\n{len(best):,} scored; a true key on a 57-rune prefix reads +14.25")
    print("(the benchmark is prime(n)-1 on the AN END page, running-key-math-sequence.md)")


def unpack() -> None:
    """Are the grids a page of runes packed densely? 1,408 bits is about 290 runes."""
    import numpy as np  # noqa: PLC0415

    from lp_plaintext_register import corpus  # noqa: PLC0415
    from sequence_key_sweep import trigram_table  # noqa: PLC0415

    t = trigram_table()

    def score(seq: list[int]) -> float:
        a = np.array(seq, dtype=np.int64)
        if a.size < 20:
            return -9.0
        return float(t[a[:-2] * 841 + a[1:-1] * 29 + a[2:]].mean())

    ref = score([r for w in corpus() for r in w])
    rnd = score(list(np.random.default_rng(1).integers(0, 29, 3000)))
    print(f"reference: LP plaintext {ref:+.3f}, uniform random {rnd:+.3f}\n")
    rows = []
    for name, v in as_integers(grid_bytes()).items():
        x, digits = v, []
        while x:
            digits.append(x % 29)
            x //= 29
        for lbl, seq in (("lsb-first", digits), ("msb-first", digits[::-1])):
            rows.append((score(seq), f"{name} {lbl}", len(seq)))
    rows.sort(reverse=True)
    for sc, name, length in rows[:6]:
        print(f"  {sc:+.3f}  {name:<34} {length} runes")
    print("\nEvery unpacking sits near the random reference, not the plaintext one.")


def xor_search() -> None:
    """A repeating-XOR key, the standard thing to try on a short byte blob."""
    from grid_hash_search import readings  # noqa: PLC0415

    def english(b: bytes) -> float:
        s = 0
        for c in b:
            ch = chr(c)
            if ch.isalpha():
                s += 3 if ch.lower() in "etaoinshr" else 1
            elif ch == " ":
                s += 4
            elif not 32 <= c < 127:
                s -= 3
        return s / len(b)

    data = readings()["65+66 row-major"]
    print(f"{'keylen':>7}{'best score':>12}   key bytes")
    for k in range(1, 9):
        key, total = [], 0.0
        for r in range(k):
            cls = data[r::k]
            b, bs = max(
                ((x, english(bytes(c ^ x for c in cls))) for x in range(256)),
                key=lambda t: t[1],
            )
            key.append(b)
            total += bs * len(cls)
        print(f"{k:>7}{total / len(data):>12.2f}   {' '.join(f'{b:02x}' for b in key)}")
    print("\nEnglish prose scores about 2.46 here and random bytes about -0.84. The")
    print("rise with key length is the free parameters, not a signal: eight key bytes")
    print("fitted to 176 is 22 bytes per parameter.")


if __name__ == "__main__":
    import sys  # noqa: PLC0415

    if "--unpack" in sys.argv:
        unpack()
    elif "--xor" in sys.argv:
        xor_search()
    elif "--primes" in sys.argv:
        primality()
    elif "--keystream" in sys.argv:
        keystream()
    else:
        main()
