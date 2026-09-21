---
type: observation
---
# Eleven of the Seventeen Repeated Words Are Chance, and the One Repeated Phrase Is Not

## Status

**Status**: confirmed. It retracts the pool inversion in `base_pool_thermometer.py`
and the tension that inversion put into the specification, and it replaces yesterday's
simulation-based chain argument with a stronger one that needs no simulation.

## The count that was read wrong

`base_pool_thermometer.py` inverted the corpus's 17 repeated words into a base pool of
357, against the 2,928 that `two-rune-depth-no-base-reuse.md` prefers, and the
disagreement went into `what-any-solution-must-satisfy.md` as an open tension.

The inversion never subtracted the rate at which a random rune stream produces
repeated three-rune words, and at three runes that rate is most of the count.

`experiments/word_repeat_accounting.py`, 400 shuffles of the corpus's own runes inside
its own word shapes — nothing about the cipher survives, word lengths and rune
frequencies do:

| count | chance floor | corpus | excess |
|---|---|---|---|
| identical | 11.06 ± 3.38 | 17 | **+5.94 (z = +1.76)** |
| long | 0.21 ± 0.47 | 0 | −0.21 |
| returns | **0.00 ± 0.00** | 1 | **+1.00** |

**Eleven of the seventeen repeats are chance.** The excess is 5.9 ± 3.4, under 2σ, so
`identical` is a weak estimator and a lower bound on the pool at best.

**The phrase repeat is not chance at any level.** Zero in 400 rune shuffles.

## The register the earlier estimates missed

Inverting a count into a pool needs the plaintext repeat supply, which every earlier
estimate took from prose. The LP's own plaintext is available
(`lp_plaintext_register.py`, 486 words) and is far more formulaic. Scaling to 2,928
words uses growth exponents measured on prose rather than an assumed square, because a
longer corpus also has more distinct types:

| register | repeated word pairs | repeated phrase pairs |
|---|---|---|
| prose | 14,981 | 662 |
| **LP's own** | **18,804** | **3,977** |

exponents 1.88 and 1.77. **The LP's plaintext repeats whole phrases about seven times
as often as prose does.** Word repeats differ by only 1.3×, so this is specifically a
phrase-level property of the register — and the phrase count is the one that carries
the chain.

## The inversion, and which model survives it

The two models differ in one thing: what a repeated *phrase* costs.

- **chain** — `base_w = base_v` makes `base_(w+1) = base_(v+1)` whenever the clock
  phases agree, so a phrase repeat costs one pool draw and one phase in five:
  `returns = phrases / (5N)`.
- **free** — the second alphabet must coincide on its own, so it costs two independent
  draws: `returns = phrases / N²`.

A model is consistent when both counts give the same pool.

| register | from `identical` | `returns`: chain | `returns`: free |
|---|---|---|---|
| prose | 2,456 | 132 [36, 5,231] | 26 [13, 162] |
| **LP's own** | **3,083** | **795 [216, 31,442]** | **63 [33, 396]** |

Intervals are the exact Poisson 95% range for a single observed count.

**On the LP's own register the chain is consistent and the free model is not.** The
chain's interval contains the pool that `identical` implies; the free model's excludes
it by a factor of eight. The free model has to buy the phrase repeat twice, and there
is not enough corpus to pay for it.

## The same conclusion without any register at all

The argument above depends on a 486-word plaintext sample scaled by a factor of six. A
second test needs none of that.

Shuffle the **order** of the corpus's own ciphertext words. Every word survives intact,
so all seventeen repeats are held fixed; only adjacency is destroyed.

    20,000 shuffles:  returns mean 0.0001,  P(at least one) = 0.00005

**Given exactly the repeated words the corpus has, two of them landing adjacent in the
same order happens once in twenty thousand times.** No register, no simulated cipher,
no key, no choice of null family — the corpus is its own control.

## What this changes

- The pool tension is gone. `identical` implies 3,083 with a 95% lower bound near
  1,500, which is what one base per block looks like. The 357 in
  `base_pool_thermometer.py` is withdrawn.
- Yesterday's chain evidence was a factor of 30 from simulated prose. This replaces it
  with a corpus-internal 1-in-20,000 and a consistency argument the free model fails
  by a factor of eight.
- `identical` should not be quoted as a battery cell again without its floor. Most of
  it is three-rune coincidence.
- `long` is exactly what chance gives (0 against 0.21), so it carries nothing either
  way, which is worth knowing before anyone fits to it.

## Two things the 17 pairs do not give

Both were tried and both are underpowered, which is worth recording so they are not
tried again.

**Span parity does not pin σ.** `sign(Π g^a σ) = sign(σ)^L`, since `g` has odd order and
is therefore even. So under an odd σ only even-span pairs can be genuine base returns,
and the ~6 genuine ones would pile up at even spans. Observed: 10 even, 7 odd, against a
random-pair baseline of 8.51 ± 2.07 — z = +0.72. The two hypotheses differ by about 3
pairs and the spread is 2.07, so 17 pairs cannot separate them. (The DJU-BEI span is
1449, odd, which is the single-event route by which `sigma-is-even.md` already gets
there.)

**There is no chain period.** If the walk returned to its start every P blocks, the
genuine returns would share P as a divisor. Scanning P from 2 to 1464, the best divides
10 of the 17 spans — and a surrogate scan over random pairs reaches 8.76 ± 1.83, giving
P = 0.34. Nothing. The spans are 42, 100, 178, 254, 276, 411, 904, 998, 1114, 1227,
1252, 1449, 1449, 1474, 1973, 1983, 2009.

Worth noting for its own sake: **all 17 repeated words are 3 runes long.** Not one
4-rune repeat exists, which is why `long` is 0 and why the whole channel sits in the
chance-dominated class.

## Falsification

- The chance floor is a property of the shuffle. If the corpus's rune frequencies are
  mis-transcribed the floor moves; recomputing it from the master transcription must
  reproduce 11.1 ± 3.4.
- The word-order shuffle assumes the 2,928 blocks are exchangeable. If block order
  carries structure — which `block-lengths-are-detached.md` says it does not — the
  1-in-20,000 is optimistic. A block-length-stratified shuffle must give the same
  answer.
- If the LP's phrase repeat supply is an artifact of the 486-word sample, the chain's
  consistency goes with it. The test is to recompute the supply from any newly solved
  page and check the 3,977 holds.

## Scripts

- `experiments/word_repeat_accounting.py`

## Related

- `the-chain-shows-only-in-extension.md` — the simulation-based version of this
  argument, which this supersedes on evidence while confirming on direction.
- `base_pool_thermometer.py` — the inversion corrected here.
- `two-rune-depth-no-base-reuse.md` — the pool floor now agreed with rather than
  contradicted.
- `dju-bei-stands-alone.md` — "no shorter companions" now has a number: the shorter
  companions that exist are eleven-seventeenths chance.
