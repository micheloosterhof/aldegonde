---
type: hypothesis
---
# Hypothesis: A Word-Delimited Quagmire with a Doublet-Dodge Rule

## Claim

Michel's proposal (September 2026). The letter step is an ordinary Quagmire schedule —
alphabets `A_k = K ∘ (add S_k)`, so the relation between adjacent positions is a pure
shift in K coordinates — and the doublet suppression is a separate rule on top: when
the emission would repeat the previous rune, advance the clock one step and re-emit.
The base advances per word, which is the word-delimited part.

## Status

**Status**: unresolved, and now the best-fitting mechanism in this directory. With one
alphabet and one schedule fitted to the distance profile it matches every measured cell
except the DJU-BEI repeat, across independent fits, with the seam landing unfitted. It
derives the factor 1/5 in the observed doublet rate from the schedule length, where
other files here record that factor without a mechanism. It also identifies a class of
key that every sweep in this directory excluded by construction.

The decodability objection it inherited from `doublet-dodge-walk.md` is now measured
and withdrawn as a blocker: the collision costs 0-6 runes in 12,388.

What blocks it instead is that the sweep's scorer cannot see the model at all. A
planted key of this family scores BELOW two thousand random wrong sigmas under
`walk_score_kernel`, so the search recorded below as "never done" cannot be done until
that is fixed. `d6w` and `d1w` also miss for unfitted keys.

## Mechanism

The dodge re-emits with `A_(k+1)` in place of `A_k`, so it fails exactly when

```
A_(k+1)(p) = A_k(p)   ⟺   s_(k+1) = 0
```

which does not involve the plaintext at all — it is a property of the schedule. So a
five-step schedule holding exactly one **zero offset** admits doublets at one clock
phase and forbids them at the other four:

```
P(doublet) = P(next step is zero) × P(would-be doublet)
           = 1/5 × (a shift diagonal)
```

Verified directly (`experiments/quagmire_dodge.py`): with one zero offset, 92 of 377
would-be doublets survive (24%, predicted 20%); with **no** zero offset the doublet
rate is **0.00000 over eight keys** — the dodge then never fails, and the corpus's
doublets could not exist at all.

`README.md` records that the observed rate fits (1/5)×(1/29) with no free parameters
(z = −0.36), and no file here supplies a mechanism for the 1/5. It follows from the
schedule length. The second factor is a shift diagonal, which is not parameter-free: it
varies with the key and averages about 1/29. So the mechanism determines the 1/5 and
leaves the second factor to the key.

## The schedule space these sweeps searched

`quagmire_runner.g_candidates` masks its candidate schedules with

```python
nz = r != 0
NZ = nz[:, None, None, None] & nz[None, :, None, None] & ... & (IDX0 != 0)
```

requiring all five offsets to be non-zero. Under a no-dodge model a zero offset means
two identical adjacent alphabets and a doublet rate at the plaintext level, so the mask
is correct for the walk. This model requires the opposite: exactly one zero offset.

The 3.1×10⁸-key enumeration (`mixed-alphabet-vigenere.md`), the ungated 7.0×10⁸ re-run
and the 4.2×10⁸ priority sweep therefore all searched only the zero-free half of the
schedule space. None of them could have returned a key of this form.

## Evidence for

Scored on the held-out battery with **only the word step fitted** (chosen against the
seam); the alphabets and the schedule are drawn at random. Best key of 60 draws:

| | LP | model | tail |
|---|---|---|---|
| d1w | 0.0063 | 0.0066 | 0.700 |
| d2w–d5w, d5x | — | — | 0.13–0.83 |
| unigram IoC | 0.9999 | 0.9999 | 1.000 |
| triplets | 0 | 0 | exact |
| kappa max z | 2.908 | 2.899 | 1.000 |
| doublet position | 0.553 | 0.473 | 0.200 |
| doublet min gap | 6 | 4.88 | 0.300 |

17 of 18 free cells, one fitted. For comparison the walk fits six and leaves 13 free.

## Evidence against

**Robustness, measured over ten independently drawn keys:**

| misses of 18 free cells | keys |
|---|---|
| 2 | 1 |
| 3 | 3 |
| 4 | 3 |
| 5 | 3 |

Median 4. The single-key table above is the best of the draws, not the model's typical
performance. Two cells miss systematically:

- **`d6w` misses for all ten keys.** The corpus reads 0.0245, below chance; a Quagmire
  shift relation at distance 6 gives chance. Suppressing it needs a tuned relation that the
  shift structure may not supply, which is the limit `sigma_algebraic_floor.py` found
  for arithmetic families.
- **`returns`** — the DJU-BEI repeat, which no model here produces.

**`d1w` misses for four keys in ten**, because the second factor in the rate is a
key-dependent shift diagonal rather than a constant.

**Not uniquely decodable, at a price of 0–6 runes.** Inherited from
`doublet-dodge-walk.md`: an output-conditioned skip emits exactly what the unskipped
clock emits for a repeated plaintext rune, so two plaintexts collide. Measured in
`experiments/quagmire_dodge_decode.py`, the collision lands on 4.5–6.5% of positions,
nine rivals in ten strand themselves on a permanent clock offset, and a beam search
holding the key recovers 12,382–12,388 of 12,388 runes — exactly, for two keys of four.
It is a real defect of the cipher and not a reason to drop the family.

## Can the schedule reach d6?

Yes. Under a period-5 schedule
6 ≡ 1 mod 5, so the distance-6 relation is the same shift as the distance-1 relation
evaluated on the distance-6 plaintext table. The zero offset makes one of the five
phases the identity, so that phase reads the plaintext distance-6 rate of 0.0672; for
the mean to reach the corpus's 0.0245 the other four shift diagonals must average
0.0138 against chance 0.0345. Hill-climbing the alphabet reaches **0.0083**, so d6 is
reachable with room to spare.

Fitting one alphabet and one schedule jointly to d1, d2, d3, d4 and d6 lands all five
within 2%, and simulation confirms the analytic prediction. Across five independent
joint fits, scored on 60 prose corpora with σ drawn at random:

| fit | free cells missing of 14 |
|---|---|
| 0 | 2 — `returns`, `identical` |
| 1 | 2 — `returns`, `identical` |
| 2 | 1 — `returns` |

So the earlier "median 4 misses" figure was a property of the unfitted model, not of
the family. With the schedule and alphabet fitted to the distance profile the model
matches everything except the DJU-BEI repeat, and `identical` in two fits of three.
The seam is NOT fitted here — σ was random — and it lands anyway.

That makes this comparable to the length-clocked walk, which fits six cells and leaves
13 free with one miss, while this fits five and leaves 14 with one or two. The
difference is that d1 comes from the schedule's zero offset rather than from a tuned
29-permutation diagonal.

## The d5 leak, predicted rather than fitted

Michel's original question was whether the doublet rule is what breaks the distance-5
repeat. It is, in the right direction and by the right amount, though not by enough to
decide anything.

Under the walk `g⁵ = id`, so two positions five apart inside a word share the alphabet
and the base and coincide exactly when the plaintext does. `period5-is-confirmed.md`
records the observed leak as PARTIAL and the full-versus-partial question as undecided.
The dodge supplies the attenuation and fixes its size from the doublet rate alone:

```
q  = 5 x d1 = 0.0314            the skip fires at q, fails only at the zero phase
d5 = (1-q)^5 x plaintext_d5 + (1-(1-q)^5)/29        a skip in between kills the echo
```

| | predicted d5 | observed − predicted |
|---|---|---|
| length-clocked walk (`g⁵ = id`) | 0.05205 | −0.41 SE |
| the same with the dodge | 0.04946 | **−0.04 SE** |

The predictions sit 0.37 SE apart, so d5 does not separate the two models — the same
verdict `period5-is-confirmed.md` reached by another route. What is new is that the
dodge DERIVES the partial leak where the walk has to accept it.

The register decides these numbers. On raw prose the plaintext lag-5 rate reads 0.0596
and both models look badly off (−2.2 and −1.4 SE); length-matched to the LP it reads
0.0521 and both are fine. d5 pairs come only from words of six runes or more, and prose
has more of those than the LP, so the unmatched figure measures the wrong words.

## What the zero-offset sweep would cost

Priced before running, in `experiments/zero_offset_census.py`.

The old d1 band constrains the SUM of five phase contributions, and that is what cut
the schedule space to about one per alphabet. Under this model the doublet rate comes
from one phase, so d1 pins a single offset and the cut collapses:

```
d1 = (1/5) x diagonal(-offsets[(z-1) % 5]),  offsets[z] = 0
```

d4 and d6 restore joint constraints of the old shape. Because the five offsets sum to
zero the distance-4 shift at phase k is `+offsets[k]`, and because 6 = 1 mod 5 the
distance-6 shift is `offsets[k+1]` — different functions of the same five offsets, so
they constrain independently. Both bands must be widened first: over d steps the dodge
inserts an extra step with probability q each time, and any insertion sends the relation
to a different shift, which reads as chance.

| filter | pairs | keys | core-hours |
|---|---|---|---|
| existing sweep: no zero, five-phase d1 | 8.4e5 | 3.10e8 | 2 |
| dodge: one zero, d1 pins one offset | 3.9e10 | 1.44e13 | 88,781 |
| dodge, plus the d4 and d6 sums | 8.1e9 | 2.99e12 | 18,454 |
| the same on 3301's own vocabulary | 1.3e7 | 4.92e9 | **30** |

Keys are (alphabet, schedule) pairs times the 369 sigma disks in the seam band, at the
45,000 keys/s/core of `walk_score_kernel.c`. The first row reproduces the 3.1e8 of the
recorded enumeration, which is the calibration check on the filter model.

So the sweep is not affordable over the dictionary and is cheap over the priority
vocabulary — 316 words from the register, the solved pages and the puzzle. That is the
version to run, and it is a narrower bet: it assumes the designer used one of their own
words.

## The sweep cannot be run with the scorer it has

Pricing the sweep assumed its scorer would recognise the key. It does not, and
`experiments/dodge_scorer_check.py` shows so with the sweep's own positive control.

`walk_score_kernel.score_sigmas` undoes the letter step at position j with the alphabet
for clock `j`, because in every model it was written for the clock IS the position. A
skip inserts a step, so from the first skip onward every remaining rune is decoded
through the wrong alphabet, and the base step compounds the error at the next word
boundary. Skips land on 4-6% of positions, about forty per 200-word window.

One planted key — DIUINITY wheel, PILGRIM disk, schedule [3, 7, 0, 11, 8], dodge
doublet rate 0.00648 against the corpus's 0.0063 — enciphered both ways:

| ciphertext | planted key | best of 2000 wrong | gap |
|---|---|---|---|
| no dodge (the sweep's own control) | 1.217 | 0.582 | +0.635 |
| with the dodge | 0.493 | 0.619 | **−0.126** |

The true key scores below two thousand random wrong sigmas.

So no sweep in this project could have found a key of this family, for two independent
reasons: `g_candidates`'s `nz` mask excludes the schedule, and the scorer cannot see the
model. The first was already recorded here; the second was not, and it is the one that
matters, because it would have turned a 30-core-hour run into a false negative of the
same shape as the DJU-BEI gate.

## What to do next

1. **Write a dodge-aware scorer.** This now gates everything else. The decoder in
   `quagmire_dodge_decode.py` tracks the clock correctly, but it needs base₀ and runs at
   Python speed. The sweep's kernel needs the same branch test with base₀ left free,
   which means an assignment problem per surviving clock path rather than one per key.
   A beam of 2–4 would hold the true path at 95% of positions; the cost is unestimated
   and is the real work.
2. **Then run the zero-offset sweep on the priority vocabulary.** 4.9e9 keys, 30
   core-hours with the scorer above, using the census's one-zero generator and its
   d1/d4/d6 bands in place of the `nz` mask and the five-phase band.
3. ~~Find whether any Quagmire can suppress d6.~~ Answered above: yes.
4. ~~Find a decodable trigger, or accept the family is a generative account only.~~
   Answered in `doublet-dodge-walk.md`: the family decodes with the key plus context,
   at a cost of 0–6 runes in 12,388. What remains is that the decode is not
   deterministic, which is a property of the cipher and not an obstacle to testing it.

## Scripts

- `experiments/quagmire_dodge.py` — the cipher, the zero-offset self-test, the
  zero-doublet control and the battery score.
- `experiments/quagmire_dodge_decode.py` — the decoder, the ambiguity rate, whether a
  rival reading rejoins the true path, and the beam-search recovery. Runs on both this
  model and the walk of `doublet-dodge-walk.md`, which is the same code with
  `alpha[k] = g^k`.
- `experiments/zero_offset_census.py` — what the zero-offset sweep would cost, over the
  dictionary and over 3301's own vocabulary.
- `experiments/dodge_scorer_check.py` — the sweep's own positive control run against
  dodge ciphertext, which is where the planted key scores below random.
- `experiments/dodge_d5_attenuation.py` — the no-free-parameter d5 prediction below.

## Related

- `doublet-dodge-walk.md` — the dodge rule on a general walk; this replaces its tuned
  `g` with a Quagmire schedule and gains the 1/5.
- `mixed-alphabet-vigenere.md` — the sweeps whose offset mask excludes this model.
- `stream-cipher-no-repeat.md` — where the (1/5)×(1/29) fit is recorded as having no
  free parameters and no mechanism.
- `length-clocked-walk.md` — the incumbent, which fits six cells to this one's one.

## Verdict

Unresolved. It is the first mechanism here to derive the 1/5 in the doublet rate rather
than fit it, and it shows that every keyword sweep in this project searched half the
schedule space.

Two of the three things recorded against it are now settled. `d6w` is reachable:
hill-climbing the alphabet gets 0.0083 where 0.0138 is required. Decodability costs 0-6
runes in 12,388 and no longer blocks the family.

The third is new and is now the binding constraint. The sweep's scorer assumes the
clock is the position, which the dodge violates, so a planted key of this family scores
below random. The search this file has been pointing at for two revisions cannot be run
until the scorer tracks the skips.

It also answers the question Michel asked first — whether the doublet rule is what
breaks the distance-5 repeat. It is: the attenuation (1-q)^5 = 0.8525 follows from the
doublet rate alone and lands d5 at -0.04 SE where the unattenuated walk gives -0.41.
The two are 0.37 SE apart, so this is a lean and not a discriminator.
