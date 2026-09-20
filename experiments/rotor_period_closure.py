# ABOUTME: Can a regularly-stepping rotor machine produce the DJU-BEI state
# ABOUTME: return? Its period must divide the gap; this enumerates what fits.
"""Rotor machines have bounded state, which is the property that makes them
computable by hand -- and it is also a hard constraint.

A machine whose wheels advance on a fixed schedule returns to an earlier
state exactly when the elapsed step count is a multiple of the machine
period (the lcm of the wheel sizes, for odometer stepping). The LP
contains one exact state return: DJU-BEI, whose two occurrences sit a
known distance apart. So the machine period must DIVIDE that distance.

That is a divisibility test with no free parameters and no register
assumptions. This script measures the gap from the corpus itself (rather
than trusting the documented figure), factorises it under both the
letter-clocked and word-clocked readings, and reports which wheel sizes
survive.

Self-tests: the located gap must reproduce the documented 6395 runes /
1449 words, and both occurrences must be word-initial 3+3.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402

N = 29


def factorise(n: int) -> dict[int, int]:
    f: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def divisors(n: int) -> list[int]:
    out = [1]
    for p, e in factorise(n).items():
        out = [d * p**k for d in out for k in range(e + 1)]
    return sorted(out)


def find_repeat(stream: list[int], word_id: list[int], gram: list[int]) -> list[int]:
    """Positions where `gram` occurs starting at a word boundary."""
    hits = []
    L = len(gram)
    for i in range(len(stream) - L + 1):
        if stream[i : i + L] != gram:
            continue
        if i > 0 and word_id[i - 1] == word_id[i]:
            continue  # not word-initial
        hits.append(i)
    return hits


def main() -> None:
    stream, word_id = load_clean()
    print(f"corpus: {len(stream)} runes, {word_id[-1] + 1} words")

    # DJU-BEI = the runes at the first documented occurrence; located from the
    # corpus rather than hardcoded, so the gap is measured not assumed.
    from collections import defaultdict

    seen: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for i in range(len(stream) - 5):
        if i > 0 and word_id[i - 1] == word_id[i]:
            continue
        seen[tuple(stream[i : i + 6])].append(i)
    repeats = {g: p for g, p in seen.items() if len(p) > 1}
    assert len(repeats) == 1, f"expected one word-initial 6-gram repeat, got {len(repeats)}"
    gram, pos = next(iter(repeats.items()))
    a, b = pos[0], pos[1]
    rune_gap = b - a
    word_gap = word_id[b] - word_id[a]

    print(f"\nDJU-BEI at rune {a} and {b}")
    print(f"  word indices {word_id[a]} -> {word_id[b]}")
    print(f"  rune gap  {rune_gap} = {factorise(rune_gap)}")
    print(f"  word gap  {word_gap} = {factorise(word_gap)}")

    # Self-tests against the documented figures.
    assert rune_gap == 6395, rune_gap
    assert word_gap == 1449, word_gap
    # both occurrences are 3+3 words
    for p in (a, b):
        assert word_id[p] == word_id[p + 2] and word_id[p + 3] == word_id[p + 5]
        assert word_id[p] != word_id[p + 3]
    print("  self-test: 6395 runes / 1449 words, both word-initial 3+3  OK")

    for label, gap in (("letter-clocked", rune_gap), ("word-clocked", word_gap)):
        divs = divisors(gap)
        print(f"\n--- {label}: period must divide {gap} ---")
        print(f"  divisors: {divs}")
        small = [d for d in divs if 1 < d <= 60]
        print(f"  usable wheel periods (2..60): {small if small else 'NONE'}")
        print(f"  is 29 a divisor? {'yes' if gap % N == 0 else 'NO'}")

    # Odometer machines built from 29-position wheels: period 29^k.
    print("\n--- odometer of k wheels of 29 positions ---")
    for k in range(1, 5):
        per = N**k
        print(
            f"  k={k}: period {per:>8}  "
            f"6395 mod {per} = {rune_gap % per:>5}  "
            f"1449 mod {per} = {word_gap % per:>5}"
        )

    # The divisors are few enough to test directly. If the alphabet sequence
    # has period p, two positions p apart share an alphabet, so they coincide
    # at the PLAINTEXT rate rather than at 1/29 -- and that holds whatever the
    # alphabets are, so it needs no key and no register model beyond the
    # plaintext IoC.
    print("\n--- direct test of each surviving period ---")
    print("    a shared alphabet gives coincidence ~0.060 (runeglish IoC 1.75/29)")
    print("    chance is 1/29 = 0.0345\n")
    letter_lags = [d for d in divisors(rune_gap) if 1 < d < len(stream)]
    print("  letter-clocked (absolute position):")
    for p in letter_lags:
        hits, tot = lag_coincidence(stream, p)
        print(f"    period {p:>5}: {hits:>5}/{tot:<6} = {hits / tot:.4f}  {zfmt(hits, tot)}")

    print("\n  word-clocked (same within-word phase, words p apart):")
    for p in divisors(word_gap):
        if p == 1 or p > 500:
            continue
        hits, tot = word_period_coincidence(stream, word_id, p)
        if tot < 200:
            continue
        print(f"    period {p:>5}: {hits:>5}/{tot:<6} = {hits / tot:.4f}  {zfmt(hits, tot)}")

    full_lag_scan(stream)
    full_word_period_scan(stream, word_id)


def full_word_period_scan(stream: list[int], word_id: list[int]) -> None:
    """Machines whose per-word state is periodic in WORD index.

    This is the class the repo's own two-wheel device belongs to: a
    5-position letter wheel stepping per rune plus a 29-position mixed disk
    turned once per word. Such a machine reuses its whole alphabet set every
    `period` words, so words p apart share a base and coincide at the same
    within-word position at the plaintext rate.

    Scanning every period covers every such device at once, whatever the
    disk wiring.
    """
    words: dict[int, list[int]] = {}
    for i, w in enumerate(word_id):
        words.setdefault(w, []).append(stream[i])
    nw = max(words) + 1

    best = (0.0, 0, 0, 0)
    rows = []
    for p in range(1, nw // 2):
        hits = tot = 0
        for w in range(nw - p):
            a, b = words[w], words[w + p]
            for j in range(min(len(a), len(b))):
                tot += 1
                hits += a[j] == b[j]
        if tot < 1000:
            continue
        rate = hits / tot
        rows.append((p, rate, hits, tot))
        if rate > best[0]:
            best = (rate, p, hits, tot)

    print(f"\n--- every word period 1..{nw // 2} (covers word-clocked devices) ---")
    rate, p, hits, tot = best
    print(f"  max over all periods: period {p}, rate {rate:.4f} ({hits}/{tot})")
    print(f"    -> {zfmt(hits, tot)}")
    reach = [r[0] for r in rows if r[1] >= 0.055]
    print(f"  periods reaching 0.055: {reach or 'NONE'}")
    for target, label in ((29, "one 29-disk"), (145, "5-wheel x 29-disk"), (841, "two disks")):
        for pp, rr, hh, tt in rows:
            if pp == target:
                print(f"  period {target:>4} ({label}): {rr:.4f}  {zfmt(hh, tt)}")


def full_lag_scan(stream: list[int]) -> None:
    """Any autonomous machine of period p reuses its alphabet at lag p.

    That is not a rotor-specific claim: for ANY deterministic machine whose
    state advances without reading the text, the state sequence is eventually
    periodic, and two positions p apart share an alphabet exactly. Sharing a
    bijection makes C[i]==C[i+p] iff P[i]==P[i+p], so the coincidence rate at
    that lag is the plaintext's own (~0.060), not 1/29.

    So scanning every lag tests every autonomous machine at once.
    """
    import numpy as np

    a = np.array(stream, dtype=np.int8)
    n = len(a)
    max_lag = n // 2
    rates = np.empty(max_lag + 1)
    rates[0] = np.nan
    for p in range(1, max_lag + 1):
        rates[p] = float(np.count_nonzero(a[:-p] == a[p:])) / (n - p)

    lags = np.arange(max_lag + 1)
    best = int(np.nanargmax(rates))
    tot = n - best
    print(f"\n--- every lag 1..{max_lag} (covers every autonomous period) ---")
    print(f"  chance 1/29 = {1 / N:.4f}   shared-alphabet ~0.0600")
    print(f"  max coincidence over all lags: lag {best}, rate {rates[best]:.4f}")
    print(f"    -> {zfmt(int(rates[best] * tot), tot)}")
    hits = lags[1:][rates[1:] >= 0.055]
    print(f"  lags reaching 0.055 (a weak shared-alphabet bar): {list(hits) or 'NONE'}")
    for p in (5, 29, 841, 1279, 6395):
        if p <= max_lag:
            t = n - p
            print(
                f"  lag {p:>5}: {rates[p]:.4f}  {zfmt(int(round(rates[p] * t)), t)}"
                f"   <- {'single rotor' if p == 29 else 'two rotors' if p == 841 else ''}"
            )


def lag_coincidence(stream: list[int], lag: int) -> tuple[int, int]:
    tot = len(stream) - lag
    hits = sum(1 for i in range(tot) if stream[i] == stream[i + lag])
    return hits, tot


def word_period_coincidence(
    stream: list[int], word_id: list[int], period: int
) -> tuple[int, int]:
    """Coincidence between words `period` apart at equal within-word position."""
    words: dict[int, list[int]] = {}
    for i, w in enumerate(word_id):
        words.setdefault(w, []).append(stream[i])
    hits = tot = 0
    nw = max(words) + 1
    for w in range(nw - period):
        a, b = words[w], words[w + period]
        for j in range(min(len(a), len(b))):
            tot += 1
            hits += a[j] == b[j]
    return hits, tot


def zfmt(hits: int, tot: int) -> str:
    """z of the observed rate against chance, and against a shared-alphabet leak."""
    import math

    p0 = 1.0 / N
    z0 = (hits - tot * p0) / math.sqrt(tot * p0 * (1 - p0))
    p1 = 0.060  # runeglish plaintext coincidence, the shared-alphabet prediction
    z1 = (hits - tot * p1) / math.sqrt(tot * p1 * (1 - p1))
    return f"z(chance)={z0:+5.2f}  z(shared-alphabet)={z1:+7.2f}"


if __name__ == "__main__":
    main()
