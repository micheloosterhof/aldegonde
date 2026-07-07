#!/usr/bin/env python3
# ABOUTME: Simulates the opportunistic back-reference model: lag-5 echoes fire
# ABOUTME: only where the plaintext itself repeats, resolving the information
# ABOUTME: problem and matching the full LP fingerprint.
"""Opportunistic back-reference model for the lag-5 paired-match structure.

Information-theoretic motivation: a deterministic ciphertext copy carries no
information about the plaintext at the copied positions, so the verified
lag-5 copy events must be (a) inserted nulls, (b) key+plaintext coincidence,
or (c) back-references that fire only where the plaintext GENUINELY repeats
at lag 5 — the repetition is the information (LZ-style), or equivalently the
key is reused exactly where reuse is free.

Rates (Markov runeglish at corpus length):
- plaintext d1 opportunities (digraph repeats at lag 5): ~78 (observed
  events: 29 -> usage ~0.18-0.37 depending on accidental accounting)
- plaintext d4 opportunities (i/i+4 frame repeats): ~46 (observed 28)
- model (b) needs 18% key-pair reuse -> predicts mono kappa-5 ~ 1.14 vs
  observed 1.073 (~2 sigma strain); disfavored.

The simulation: OTP + 1/5-acceptance doublet avoidance + deliberate marking
of plaintext lag-5 repeats (u1 = 0.18 of digraph opportunities, u4 = 0.28 of
frame opportunities) by copying the ciphertext from 5 back. Accidental
echo patterns are left in (the decryptor tolerates ~0.5% corruption, or a
suppression variant gives the same statistics with higher usage rates).

Result: the FIRST mechanism to match the entire fingerprint —
doublets 0.666+/-0.046% (LP 0.664), triplets ~0, nIoC 1.000, mono kappa-5
1.101+/-0.029 (LP 1.073), d1 30.8+/-4.5 (LP 29), d2 19.6 (LP 15), d3 18.5
(LP 14), d4 33.0+/-2.9 (LP 28), T5z +5.9+/-1.1 (LP +4.7).

Corollaries if true: the 57 event positions yield 114 deterministic
plaintext constraints (P[i] = P[i-5] at marked spots) — free cribs; and the
section-4 concentration means section 4 has the most lag-5-repetitive
plaintext (chant-like text).
"""

import importlib.util
import random
import statistics

_spec = importlib.util.spec_from_file_location(
    "mf", "experiments/mechanism_fingerprint.py")
assert _spec is not None and _spec.loader is not None
mf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mf)

MOD = 29
i2r = mf.i2r
r2i = mf.r2i


def enc_backref(pt: str, u1: float = 0.18, u4: float = 0.28) -> str:
    """OTP + doublet avoidance + opportunistic lag-5 back-references."""
    p = [r2i(c) for c in pt]
    marks: set[int] = set()
    used: set[int] = set()
    for i in range(5, len(p) - 4):
        if i in used:
            continue
        if p[i] == p[i - 5] and p[i + 1] == p[i - 4] and random.random() < u1:
            marks.update((i, i + 1))
            used.update(range(i, i + 2))
            continue
        if p[i] == p[i - 5] and p[i + 4] == p[i - 1] and random.random() < u4:
            marks.update((i, i + 4))
            used.update(range(i, i + 5))
    out: list[str] = []
    for i in range(len(p)):
        if i in marks and len(out) >= 5:
            c = r2i(out[i - 5])
        else:
            c = (p[i] + random.randrange(MOD)) % MOD
            while out and i2r(c) == out[-1] and random.random() > 0.2:
                c = (p[i] + random.randrange(MOD)) % MOD
        out.append(i2r(c))
    return "".join(out)


def main() -> None:
    """Compare the back-reference model's fingerprint to the LP corpus."""
    text, _wlens = mf.load_corpus()
    gen = mf.build_markov()
    n = len(text)

    pt_d1 = []
    pt_d4 = []
    for _ in range(6):
        pt = gen(n)
        pt_d1.append(sum(1 for i in range(5, n - 1)
                         if pt[i] == pt[i - 5] and pt[i + 1] == pt[i - 4]))
        pt_d4.append(sum(1 for i in range(5, n - 4)
                         if pt[i] == pt[i - 5] and pt[i + 4] == pt[i - 1]))
    print(f"plaintext opportunities: d1 {statistics.mean(pt_d1):.0f}, "
          f"d4 {statistics.mean(pt_d4):.0f} (observed events: 29, 28)")

    obs = mf.fingerprint(text)
    fps = [mf.fingerprint(enc_backref(gen(n))) for _ in range(8)]
    avg = {k: statistics.mean(f[k] for f in fps) for k in fps[0]}
    sd = {k: statistics.stdev(f[k] for f in fps) for k in fps[0]}
    print("\nback-reference model (8 reps) vs observed LP:")
    for k in obs:
        print(f"  {k:9s}: sim {avg[k]:7.3f} +/- {sd[k]:5.3f}   LP {obs[k]:7.3f}")


if __name__ == "__main__":
    main()
