---
type: observation
---
# Observation: Coincidence Is the *Only* Base-Invariant Statistic, So the Local Channel's 13 Bits Are All There Are

## Feature

Several results in this directory are empirical findings that turn out to be forced.
`bigram-ioc.md` measures that off-diagonal within-word bigrams are uniform;
`key-local-channel-is-empty.md` finds no constraint beyond the coincidence rates. Both
follow from a two-line group-theoretic argument, given one condition that this file
also tests.

**The argument.** Under a per-word base `β`, a within-word pair `(a, b)` of ciphertext
runes is `(β(u), β(v))` for the underlying pair `(u, v)`. Since `β` is unknown and
changes every word, any usable statistic of that pair must be invariant under the whole
base family. If the family acts **2-transitively** on the 29 runes — as the full
symmetric group does, and as the affine group AGL(1,29) does — then ordered pairs of
*distinct* runes form a single orbit, and the equal pairs form the other. There are
exactly two orbits, so

> the only base-invariant statistic of a within-word pair is **whether the two runes
> are equal**.

The within-word coincidence rates are therefore not merely the best local signal found
so far; they are the complete local signal. Off-diagonal uniformity is a theorem, not
an observation.

**The condition is testable, and it holds.** The argument needs 2-transitivity. A base
family of pure *shifts* is not 2-transitive — it preserves differences, so `b − a` would
be invariant and would carry plaintext structure worth far more than 13 bits. Measuring
the within-word difference distribution in the body:

| d | pairs | chi² on all differences | chi² excluding the zero cell (27 df) | verdict |
|---|---|---|---|---|
| 1 | 10,028 | 274.8 | **34.3** | uniform |
| 2 | 7,199 | 21.4 | 21.4 | uniform |
| 3 | 4,835 | 27.4 | 26.5 | uniform |
| 4 | 3,197 | 31.7 | 27.8 | uniform |
| 5 | 2,073 | 38.9 | 25.8 | uniform |

Every distance is uniform once the zero cell is removed (5% critical value 40.1). The
d=1 raw value of 274.8 is entirely the doublet suppression — that is, entirely the
coincidence channel already counted. **So the base does not preserve differences, the
2-transitivity condition is satisfied, and the theorem applies.**

## Status

**Status**: confirmed — the orbit argument is elementary (S₂₉ is 2-transitive, so
ordered distinct pairs form one orbit), and its condition is verified by the difference
test above.

## What it closes

- **The local channel is exactly 13 bits on g** (`key-local-channel-is-empty.md`), and
  that is a ceiling, not a current best. No cleverer within-word statistic exists.
- **Off-diagonal bigram uniformity needs no explanation.** It cannot be otherwise.
- **σ's absence of local constraint is structural.** A statistic that cannot see past
  the base cannot constrain what the base does between words.

## The one channel the argument leaves open, and why it is empty

Triples have more orbits than pairs — the equality *pattern* of `(a,b,c)` is invariant
and is strictly more than the three pairwise equalities — so a joint coincidence
statistic could in principle add bits. It does not, for want of data. Counting joint
matches in the body:

| shape (a,b) | triples | both match | expected if independent |
|---|---|---|---|
| (1,2) | 7,199 | 0 | 1.53 |
| (1,5) | 2,073 | 0 | 0.49 |
| (2,4) | 3,197 | 5 | 4.18 |
| (5,6) | 1,267 | 0 | 1.61 |
| (5,10) | 88 | 0 | 0.11 |

**Five joint-match events in total.** The standard error on a count of `k` is `√k`, so
at these counts even a two-fold effect is about one sigma. The channel exists and is
empty.

## Scope

The theorem is about **within-word** pairs, where one base applies to both runes. It
says nothing about cross-word pairs, which involve two different bases and are the
subject of `seam-channel-clean.md`. It also assumes the base family is 2-transitive;
the difference test establishes only that the family does not preserve differences,
which excludes shifts and any other regular family but does not by itself prove full
2-transitivity.

## Related

- `key-local-channel-is-empty.md` — the 13-bit figure this bounds as a ceiling.
- `bigram-ioc.md` — the uniformity this derives.
- `zero-triplets.md` — the (1,2) row above.

## The 2-transitivity condition, sharpened (September 2026)

The difference test above rules out a base family of pure shifts. It does not rule out
the other proper subgroups of AGL(1,29): a base x -> m*x + c with m drawn from a
multiplicative subgroup H of order k is transitive but 2-transitive only when k = 28,
and its invariant is the coset H*(b - a), not the difference itself. Spread over 27
degrees of freedom, such a signal is diluted by up to 27x.

`base-family-is-2-transitive.md` runs the concentrated test at every subgroup order
k in {1, 2, 4, 7, 14, 28}, both for the difference and for the ratio, at lags 1 to 5,
against a surrogate null. Nothing exceeds z = +2.5 in 60 tests. Planted controls put
H_2, H_4 and H_7 one to two orders of magnitude above what the body shows.

H_14 is the one family the scan cannot see, because the invariant it exposes is the
quadratic-residue class of g^j(p_j) - g^i(p_i) rather than of p_j - p_i, and a
non-affine g scrambles those classes. The conclusion of this file is unaffected: that
extra bit is not a plaintext statistic unless g is affine, and the only affine maps of
order 5 on F_29 are translations, which the difference test above already excludes.

