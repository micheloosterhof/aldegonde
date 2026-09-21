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
