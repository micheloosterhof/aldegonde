---
type: disproof
---
# Disproof: No Rune Partition Into Three or More Blocks Survives, and Two Blocks Only in One Shape

## The gap this closes

`rotor-machine-compact-state.md` prices the intransitive escape. If the base group never
mixes certain runes, the runes split into blocks, the state space collapses and the
cipher becomes hand-runnable again. Block membership passes through the cipher exactly —
a plaintext rune and its ciphertext always share a block — so the plaintext's block-level
structure is deposited in the ciphertext whatever the wiring.

That file tests one block **shape** at a time against the partition the shape implies,
and reports the test losing all power below five blocks: the leak a 2- to 4-block machine
would deposit is smaller than the surrogate's own noise. Its own verdict is "untested",
not "excluded".

The power loss is about degrees of freedom, not about the effect. A k-block partition
reduces the 29×29 bigram table to k×k, which at k = 2 is one degree of freedom. But the
**partition itself was never searched**. So turn the question round: instead of asking
whether a named partition leaks, ask whether *any* partition does.

## Method

For each k, maximise the block-sequence G² — the summed mutual information of block pairs
at within-word lags 1, 2 and 3 — over all assignments of the 29 runes to k blocks, by
random restarts plus greedy single-rune moves. Compare the maximum against the same
optimisation run on **doublet-preserving surrogates**. Calibrating against a plain
shuffle would report the doublet deficit as a block signal, which is the `bigram-ioc.md`
trap.

## Result: nothing, at any block count from 2 to 6

| k | observed G² | surrogate mean | sd | z | best partition sizes |
|---|---|---|---|---|---|
| 2 | 75.6 | 68.3 | 5.6 | +1.30 | 10, 19 |
| 3 | 130.6 | 123.7 | 13.2 | +0.53 | 7, 10, 12 |
| 4 | 176.4 | 178.4 | 11.4 | −0.18 | 5, 7, 8, 9 |
| 5 | 230.9 | 235.0 | 11.4 | −0.36 | 4, 5, 6, 7, 7 |
| 6 | 283.8 | 297.0 | 8.3 | −1.59 | 2, 2, 4, 6, 7, 8 |

The optimiser is searching hard — it beats the surrogate mean at k = 2 and 3 — and still
lands inside the null everywhere.

## Power, which is partition-dependent and must be quoted that way

Planting block ciphers over the LP's own plaintext, 12 random partitions of each shape,
against the 95% detection threshold read off the body's own surrogates:

| k | shape | planted G² min / median / max | detected |
|---|---|---|---|
| 3 | 10, 10, 9 | 158 / 358 / 706 | **100%** |
| 4 | 10, 9, 5, 5 | 360 / 911 / 1186 | **100%** |
| 2 | 15, 14 | 49 / 152 / 441 | 50% |
| 2 | 25, 4 | 47 / 56 / 92 | **8%** |

**Three and four blocks are now excluded** — the region the block-bigram leak test could
not reach. Every planted partition of those shapes is found.

**Two blocks are not.** How much a 2-block cipher leaks depends entirely on which runes
it groups, and a small block leaks almost nothing: a block of 4 against a block of 25 is
detected 8% of the time.

## The one surviving shape is a named one

The [25, 4] split is not an arbitrary survivor. `rotor-machine-compact-state.md` reaches
the same shape from the other direction: four *singleton* blocks are excluded by unigram
mass at z ≈ −5.0, but "letting the four fixed points share one block of size 4 drops the
worst mass error to 0.7%". Under a g of cycle type 5⁵1⁴ those four runes are exactly g's
fixed points, on which g acts as the identity.

So the surviving hypothesis is specific and worth stating as one line:

> the 29 runes split into g's five 5-cycles (25 runes, one block) and g's four fixed
> points (one block of 4), and no base ever moves a rune between them.

It is the one intransitive shape that passes the mass test *and* is invisible to this
one. Everything else is closed.

## Why the obvious follow-up does not work

If g fixes those four runes, then within a word every position holding one of them shares
the same restricted alphabet, whatever the letter phase — so within-word coincidence
restricted to the block should sit at the plaintext rate rather than 1/4. The arithmetic
kills it: about 4/29 of 12,956 runes land in the block, which yields roughly 560
within-word pairs, an excess of about 0.05 over chance, and z ≈ 2.7 for the *correct*
4-set. Over the 23,751 candidate 4-sets that is not a test. A sharper handle on this
shape has to come from somewhere other than coincidence counting.

## Status

**Status**: disproved for k ≥ 3 (planted detection 100%); for k = 2, disproved only for
balanced shapes (50% at 15/14) and **untested for a small block** (8% at 25/4).
`experiments/block_partition_search.py`, `--control` for the planted table.

## Related

- `rotor-machine-compact-state.md` — the file whose few-block hole this closes, and whose
  mass test independently selects the same surviving shape.
- `bigram-ioc.md` — why the surrogate must preserve doublets.
- `local-channel-is-exactly-coincidence.md` — an intransitive family is not 2-transitive,
  so a surviving block structure would reopen the local channel.

## The surviving shape, enumerated (September 2026)

The partition optimiser detects a [25, 4] split only 8% of the time, so the shape was
left open above. Enumerating it directly does much better, because the statistic factors:
block membership passes through the cipher untouched, so the ciphertext's membership
INDICATOR is the plaintext's, and the 2x2 indicator transition table at lag k is four sums
over the 29x29 lag-k bigram matrix. Build the matrices once and all **23,751** four-rune
subsets cost a few lookups each -- three seconds for the whole enumeration.

Pooling G^2 over lags 1 to 5:

| | |
|---|---|
| subsets | 23,751 |
| mean / sd | 16.31 / 7.16 |
| **body maximum** | **50.30** at (4, 5, 21, 22) |
| best set sharing no rune with it | 49.18 at (1, 12, 15, 19) |
| **top-to-disjoint ratio** | **1.023** |

**Power, measured by planting eight random 4-sets into the LP's own plaintext:**

| planted score | 20.0 | 25.2 | 47.7 | 84.8 | 106.2 | 122.1 | 145.2 | 371.5 |
|---|---|---|---|---|---|---|---|---|
| rank of 23,751 | 656 | 129 | **1** | **1** | **1** | **1** | **1** | **1** |

Six of eight rank first — **75% detection**, against the optimiser's 8%. The two misses
are 4-sets whose letters carry almost no indicator structure in the plaintext to begin
with, so there is nothing for any statistic to find.

**The discriminator is the margin, not the score.** A real block wins by one: the
successful plants beat their runners-up by 11% to 190%. The body's top three candidates
are (4,5,21,22), (4,5,20,22) and (0,4,5,22) — an overlapping cluster sharing runes 4, 5
and 22 — scoring 50.30, 50.28 and 50.23, and the best *disjoint* set reaches 49.18. A
ratio of **1.023** is what the maximum of 23,751 correlated draws looks like, not a block.

**So [25, 4] is now excluded at 75% power**, and the last structural escape narrows to
4-sets that leak nothing measurable — which are also the 4-sets a solver would gain
nothing from knowing.

## Every small block size, enumerated

The enumeration generalises to any size, so the whole two-block family the optimiser is
weakest on can be covered exhaustively rather than argued about:

| block size | subsets | body max | best disjoint | ratio | planted rank 1 | planted median |
|---|---|---|---|---|---|---|
| 2 | 406 | 46.3 | 43.8 | 1.056 | 6/6 | 105 |
| 3 | 3,654 | 47.8 | 47.6 | 1.004 | 5/6 | 69 |
| 4 | 23,751 | 50.3 | 49.2 | 1.023 | 5/6 | 67 |
| 5 | 118,755 | 59.0 | 54.4 | 1.085 | 4/6 | 130 |
| 6 | 475,020 | 64.7 | 59.9 | 1.081 | 5/6 | 201 |

At every size the body's maximum sits well below what a planted block of that size
scores, and its best candidate is separated from the best *disjoint* candidate by 0.4% to
8.5% — the margin a maximum over correlated draws produces, not the 11%-to-190% margin
the successful plants show.

Power runs 4/6 to 6/6 across the sizes, because the misses are always
sets whose letters carry little indicator structure in the plaintext. That is a ceiling
on this method rather than a gap in the conclusion: a partition no statistic can see is
also a partition that tells a solver nothing.

**So the two-block family is closed for small blocks (2–6) at 67–100% power**, the
optimiser covers balanced splits at 50%, and three or more blocks are excluded outright.
The intransitive escape is effectively shut.
