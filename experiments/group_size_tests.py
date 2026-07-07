#!/usr/bin/env python3
# ABOUTME: Tests group-size mixtures, reset rules, marker-rune boundary
# ABOUTME: triggers, and Hill-5-with-rejection against the doublet fingerprint.
"""Group-size variants, reset rules, marker runes, and Hill-with-rejection.

Results:
1. Marker runes: the runes before/at/after doublets are corpus-typical
   (chi2 24/27/33, df 28). No visible rune class triggers boundaries.
2. Gap-process Monte Carlo vs observed (86 doublets, min gap 6, zero gaps
   <=5, flat mod 5): fixed-5 groups are catastrophically excluded (mod-5
   lattice); {5,6} free-running fits everything with no extra parameters
   (81.6+/-8.9 doublets, P(no gaps<=5)=23%); {4,5,6} needs the 5-position
   dead time to explain zero small gaps; {4,5} is strained (98.5 doublets,
   p~3% for no small gaps). Reset-at-doublet is statistically
   indistinguishable from free-running; protecting the entire first
   boundary after a doublet predicts min gap >= 8, contradicting the
   observed 6 - the dead time is positional (~5 positions), not
   boundary-counted.
3. Hill 5x5 over GF(29) with internal-doublet rejection reproduces the
   doublet rate (0.69%), zero triplets, and flat IoC - but fixed-aligned
   blocks put every doublet at position 4 mod 5, a lattice LP does not
   have. Any block cipher of this shape needs drifting alignment.
   Plain Hill (no rejection) has no doublet suppression at all: for fixed
   adjacent-row difference r, P(r.P = 0) = 1/29 regardless of the matrix.
"""

import importlib.util
import random
import statistics
from collections import Counter

from aldegonde import c3301

AB = c3301.CICADA_ALPHABET
N = 29
r2i = c3301.r2i

with open("data/page0-58.txt") as f:
    raw = f.read()
parts = raw.split("%")
keep = [i for i, p in enumerate(parts) if any(c in AB for c in p)][:-2]
text = "".join(x for i in keep for x in parts[i] if x in AB)
n = len(text)
dpos = [i for i in range(n - 1) if text[i] == text[i + 1]]
gaps_obs = [b - a for a, b in zip(dpos, dpos[1:])]

# ---- 1. categorical marker-rune tests ----
print("=== 1. do specific runes flank doublets? (chi2 vs corpus, df=28) ===")
corpus_freq = Counter(text)
def cat_test(positions: list[int], name: str) -> None:
    vals = Counter(text[p] for p in positions if 0 <= p < n)
    tot = sum(vals.values())
    chi2 = 0.0
    for r in AB:
        e = tot * corpus_freq[r] / n
        chi2 += (vals.get(r, 0) - e) ** 2 / e
    print(f"  {name}: chi2={chi2:.1f} (28 df; >41 is p<0.05)")

cat_test([i - 1 for i in dpos], "rune BEFORE doublet")
cat_test(list(dpos), "doubled rune itself")
cat_test([i + 2 for i in dpos], "rune AFTER doublet")

# ---- 2. gap-process Monte Carlo for group-size variants ----
print("\n=== 2. doublet gap process under group-size variants ===")
print(f"observed: {len(dpos)} doublets, min gap {min(gaps_obs)}, "
      f"gaps<=5: {sum(1 for g in gaps_obs if g <= 5)}, "
      f"gaps mod5 {sorted(Counter(g % 5 for g in gaps_obs).items())}")

def simulate(lengths: list[int], probs: list[float], *, reset: bool,
             protect_first: bool, reps: int = 400) -> None:
    tot_d, tot_min, tot_le5, mod5 = [], [], [], Counter()
    for _ in range(reps):
        pos = 0
        doublets = []
        next_boundary = pos + random.choices(lengths, weights=probs)[0]
        protected = False
        while pos < n - 1:
            if next_boundary == pos + 1:
                # boundary adjacency: doublet occurs w.p. 1/29 unless protected
                if not protected and random.random() < 1 / N:
                    doublets.append(pos)
                    if reset:
                        next_boundary = pos + 1 + random.choices(
                            lengths, weights=probs)[0]
                        protected = protect_first
                        pos += 1
                        continue
                protected = False
                next_boundary = pos + 1 + random.choices(lengths, weights=probs)[0]
            pos += 1
        g = [b - a for a, b in zip(doublets, doublets[1:])]
        tot_d.append(len(doublets))
        if g:
            tot_min.append(min(g))
            tot_le5.append(sum(1 for x in g if x <= 5))
            mod5.update(x % 5 for x in g)
    m5 = [mod5[k] for k in range(5)]
    m5n = sum(m5)
    chi5 = sum((c - m5n / 5) ** 2 / (m5n / 5) for c in m5) if m5n else 0
    print(f"  doublets {statistics.mean(tot_d):6.1f}+/-{statistics.stdev(tot_d):4.1f} "
          f"min-gap {statistics.mean(tot_min):4.1f} "
          f"gaps<=5 {statistics.mean(tot_le5):4.2f} "
          f"mod5-chi2/rep {chi5 / len(tot_d) / 4:.2f}")

for name, L, P, rs, pf in [
    ("{4,5,6} free          ", [4, 5, 6], [.15, .7, .15], False, False),
    ("{4,5,6} reset@doublet ", [4, 5, 6], [.15, .7, .15], True, False),
    ("{4,5,6} reset+protect ", [4, 5, 6], [.15, .7, .15], True, True),
    ("{5,6}   free          ", [5, 6], [.5, .5], False, False),
    ("{4,5}   free          ", [4, 5], [.5, .5], False, False),
    ("fixed 5 reset@doublet ", [5], [1.0], True, False),
    ("fixed 5 free (lattice)", [5], [1.0], False, False),
]:
    print(f"{name}", end="")
    simulate(L, P, reset=rs, protect_first=pf)

# ---- 3. Hill-5 with internal-doublet rejection ----
print("\n=== 3. Hill 5x5 over GF(29) with internal-doublet rejection ===")

spec = importlib.util.spec_from_file_location(
    "mf", "experiments/mechanism_fingerprint.py")
mf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mf)

def rand_invertible() -> list[list[int]]:
    while True:
        M = [[random.randrange(N) for _ in range(5)] for _ in range(5)]
        # check invertibility via Gaussian elimination mod 29
        A = [row[:] for row in M]
        ok = True
        for col in range(5):
            piv = next((r for r in range(col, 5) if A[r][col] % N), None)
            if piv is None:
                ok = False
                break
            A[col], A[piv] = A[piv], A[col]
            inv = pow(A[col][col], N - 2, N)
            for r in range(col + 1, 5):
                f = (A[r][col] * inv) % N
                for c in range(col, 5):
                    A[r][c] = (A[r][c] - f * A[col][c]) % N
        if ok:
            return M

def enc_hill_reject(pt: str, wl: list[int]) -> str:
    M = rand_invertible()
    v = [1 + random.randrange(N - 1) for _ in range(5)]
    out: list[str] = []
    for b in range(0, len(pt) - 4, 5):
        block = [r2i(c) for c in pt[b:b + 5]]
        t = 0
        while True:
            cb = [(sum(M[r][c] * block[c] for c in range(5)) + t * v[r]) % N
                  for r in range(5)]
            if all(cb[j] != cb[j + 1] for j in range(4)):
                break
            t += 1
        out.extend(mf.i2r(x) for x in cb)
    rem = len(pt) % 5
    if rem:
        out.extend(pt[len(pt) - rem:])
    return "".join(out)

textc, wlens = mf.load_corpus()
gen = mf.build_markov()
fps = [mf.fingerprint(enc_hill_reject(gen(len(textc)), wlens)) for _ in range(3)]
avg = {k: statistics.mean(f[k] for f in fps) for k in fps[0]}
print("  " + " ".join(f"{k}={v:.3f}" for k, v in avg.items()))
# doublet position lattice check
s = enc_hill_reject(gen(len(textc)), wlens)
dp = [i for i in range(len(s) - 1) if s[i] == s[i + 1]]
print(f"  doublet positions mod 5: {sorted(Counter(i % 5 for i in dp).items())}"
      f"   <- fixed-aligned blocks leave a lattice; LP has none")
