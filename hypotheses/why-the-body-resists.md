---
type: observation
---
# Observation: The Information Is There and the Local Channel Cannot Reach It — 13 Bits Against 170

## Feature

Four results established separately this September compose into one statement about why
the unsolved body resists, and the statement is quantitative.

**The key is small and the ciphertext over-determines it.** A length-clocked walk key is
`g` (an order-5 permutation, 80 bits at cycle type 5⁵1⁴), `σ` (103 bits) and `base₀`
(103 bits) — **285 bits**. With plaintext redundancy measured on the author's own
runeglish, 12,956 runes can pin about 19,700 bits, so the key is over-determined **69
times over** (`unicity-distance.md`). There is exactly one consistent answer and it is
not hiding.

**But only one statistic survives the unknown base.** Under a per-word base `β`, a
within-word ciphertext pair is `(β(u), β(v))`, and a 2-transitive base family has
exactly two orbits on ordered pairs — equal and unequal. So the *only* base-invariant
statistic of a pair is **whether the two runes are equal**
(`local-channel-is-exactly-coincidence.md`). Off-diagonal bigram uniformity is a
theorem, not an observation, and the condition is verified: within-word differences are
uniform at every distance once the zero cell is removed.

**That statistic is worth 13 bits.** Measured against the author's own plaintext
bigrams, the within-word coincidence rates at distances 1 to 4 admit 1 in 7,700 random
order-5 permutations — **13.0 bits**, of which d1 alone supplies 7.0
(`key-local-channel-is-empty.md`). Distance 5 supplies none: since `g⁵ = id`, every
order-5 `g` predicts the same rate there, so the corpus's most-studied anomaly carries
zero information about *which* `g` it is.

**And a preventer attenuates even that.** A clock perturbation at rate `q` breaks a
distance-`d` pair with probability `1 − (1−q)^d`, and destroys absolute-position tests
outright (`preventer-blinds-absolute-tests.md`). The boundary-blindness of the doublet
suppression favours a preventer by 13 to 34 bits over tuned relations, and under that
reading the d1 channel's 7 bits are produced by the mechanism rather than by `g`.

## The arithmetic

| | bits |
|---|---|
| `g` search space | 80 |
| `σ` search space | 103 |
| local information about `g` | **13** |
| local information about `σ` | **0** |
| shortfall on `g` | 67 |
| shortfall on `σ` | 103 |

## Status

**Status**: confirmed — each component is measured or proved in the file cited, and the
composition is arithmetic.

## What follows

- **The answer exists uniquely.** Unicity settles that; "flat everywhere, spiked only at
  the exact key" (`no-known-plaintext-foothold.md`) describes the search surface, not
  the existence of a solution.
- **Local statistics cannot find it, and this is a ceiling rather than a current best.**
  The orbit theorem says no cleverer within-word statistic exists, so the 13 bits will
  not improve with more analysis of the same kind.
- **More ciphertext would not help either**, because there is none: the master's 15,933
  runes are the front matter's 2,797 plus page0-58's 13,136, of which the solved AN END
  page and the Parable make up the 180 beyond the clean 12,956.
- **So progress requires information from outside the local channel** — a crib, a
  structural insight about how `g` and `σ` are *constructed* rather than what they do,
  or a search that exploits the 69-fold over-determination directly. The rubricated
  titles supply 52 words where cribbing `g` needs about 300
  (`rubrication-crib-candidates.md`), which is the size of the remaining gap.

## Related

- `unicity-distance.md`, `local-channel-is-exactly-coincidence.md`,
  `key-local-channel-is-empty.md`, `preventer-blinds-absolute-tests.md` — the four
  components.

## There is no weak stretch to seed a search from

`experiments/is_there_an_unsuppressed_stretch.py`

This file argues a key search has nothing to climb. The obvious hope against that is a
**local lapse** — one page where the encipherer forgot the preventer, leaving a stretch
with a weaker mechanism and a foothold. Every previous test of the suppression asks
whether it holds on average, which a lapse would survive: one unsuppressed page moves the
pooled rate by less than a tenth of its own standard error.

A sliding window over all 12,955 adjacent pairs, scored against a surrogate null that
shuffles the doublet flags:

| window | expected at 0.0066 | expected at chance | observed max | null max | P |
|---|---|---|---|---|---|
| 200 | 1.3 | 6.9 | 5 | 5.5 ± 0.8 | 0.920 |
| 500 | 3.3 | 17.2 | 8 | 8.7 ± 1.2 | 0.863 |
| 1000 | 6.6 | 34.5 | 15 | 13.0 ± 1.5 | 0.150 |

**No lapse anywhere.** And the scan could see one: a 500-pair stretch without the
preventer would hold 17.2 doublets against a null maximum of 8.7 ± 1.2 — **seven sigma**.
The shortest complete lapse it resolves is about 200 pairs, roughly a page of runes.

So the preventer was applied without a gap across the whole body. That closes the foothold
this file's argument predicts should not exist, by direct measurement rather than by
inference.

**Limits:** a lapse shorter than ~200 pairs would pass unseen, and the scan tests for
absence of the mechanism, not for a locally lower φ.
