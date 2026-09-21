---
type: hypothesis
---
# Hypothesis: The Doublet Avoidance Is What Breaks the Distance-5 Echo

## Claim

Michel's proposal (September 2026). One rule does both jobs: when the emission would
repeat the previous rune, the letter clock skips an extra step. That suppresses
doublets, and because the skip moves the phase it also breaks the period-5 alignment —
so the corpus's partial distance-5 leak and its missing doublets are the same event
seen twice, with no tuned permutation diagonal anywhere.

```
c_j = base_w( g^(k_j)( p_j ) )
k_(j+1) = k_j + 1, and one step more whenever the emission would have repeated
```

## Status

**Status**: unresolved, and the most economical proposal this directory has had. Two
verdicts recorded here have since been retracted. The doublet POSITION disproof rested
on one arbitrarily drawn key and the statistic is strongly key-dependent for both this
model and the walk. The decodability objection was never measured: the collision is
real but costs 0-6 runes in 12,388, and a beam search holding the key recovers the
corpus exactly for half the keys tried. What stands against it is three cells it has
not yet been shown to reach.

## Mechanism, and what falls out of it

Inside a word the base is constant, so a would-be doublet is `g(p_j) = p_(j−1)`. After
the extra step the emission repeats only if `g²(p_j) = p_(j−1)`. Combining the two, a
doublet **survives** exactly when

```
g(p_j) = p_j = p_(j−1)
```

a plaintext double sitting on a fixed point of `g`. Three consequences, none tuned:

- **The suppression is structural.** With `g` and σ drawn at random — no diagonal
  fitted at all — the model gives d1w **0.0009** against chance 0.0345. The rate is
  (plaintext doubles) × (fixed points) = 0.0263 × 4/29 = 0.0036, and choosing *which*
  four runes `g` fixes moves it between 0.0000 and 0.0174, which brackets the observed
  0.0063. That is ~14 bits of key where the walk spends ~100 on a tuned 29-permutation.
- **The seam comes along.** The same rule fires across a word boundary, so the seam
  rate tracks the within-word rate by construction. `length-clocked-walk.md` states
  that the walk does *not* predict their observed equality (z = −0.92); this does.
- **Much of the distance profile comes free.** Scored on the held-out battery with only
  the four fixed points chosen, d2w, d4w, d5w and the cross-word d5x land — cells the
  walk has to fit. d3w lands for some fixed-point choices and not others (0.0595 against
  0.0370 for the key that best fits the doublet rate and position), so it belongs with
  the open cells below rather than here.

Verified in `experiments/doublet_dodge_walk.py`: every surviving doublet in a simulated
corpus is a plaintext double on a fixed point of `g`, zero exceptions.

## Evidence against

**1. It is not uniquely decodable — but the collision costs a few runes, not the
message.** A skip emits `base(g^(k+1)(p_(j−1)))`, which is exactly what the unskipped
clock emits for a repeated plaintext rune. So `x x` and `x g⁻¹(x)` produce identical
ciphertext and a decoder holding the whole key cannot separate them;
`experiments/doublet_dodge_walk.py` exhibits a concrete collision. That much stands.

What was never measured is how often it happens or what it costs, and
`experiments/quagmire_dodge_decode.py` now measures both. The decoder knows `c_(j−1)`
from the ciphertext, so it can test both hypotheses:

```
N (no skip):  p = A_k^-1(base^-1(c_j)),     consistent iff c_j != c_(j-1)
D (skip):     p = A_(k+1)^-1(base^-1(c_j)), consistent iff base(A_k(p)) == c_(j-1)
```

Three things follow, measured over four keys on a 12,388-rune corpus.

- **An observed doublet is never ambiguous.** N requires `c_j != c_(j−1)`, so a doublet
  in the ciphertext forces D. Doublets announce themselves.
- **Ambiguity is one shift diagonal**, 4.5%–6.5% of positions against 3.4% for a flat
  one, since D needs `u_j = u_(j−1) + s_(k+1)` in K coordinates.
- **Nine rivals in ten strand themselves.** A skip only ever ADDS a step, so a wrong
  branch holds a permanent clock offset and reads every later rune through the wrong
  alphabet. 524–738 rivals per key never rejoin the true path; 33–63 do, by deferring
  the skip to the next position instead of dropping it, and those cost a few runes.

A beam search over the branches, scored by a plaintext rune trigram model, recovers
12,382–12,388 of 12,388 runes, **exactly for two keys of the four**. Widening the beam
eightfold changes the output not at all, and the trigram model scores the wrong reading
HIGHER than the truth, so the residual is the language model rather than the cipher:
FORGOTTEN decodes as FORGBTTEN.

So unique decodability fails and practical decodability holds. The reader needs the key
and the context, which is one more than a deterministic cipher asks and far less than
"cannot be undone". 3301's own interrupter conditions on an already-decoded plaintext
rune and so avoids the ambiguity entirely; this family pays a handful of runes instead.
That is a weaker objection than this file previously recorded, and it no longer blocks
the family.

**2. Three cells are not yet reached.** With `g`'s fixed points chosen on the doublet
rate and position together, and the rest of `g` and σ drawn at random, the held-out
battery leaves d3w at 0.0595 against 0.0370 (p = 0.000), d6w at 0.0420 against 0.0245,
and the seam at 0.0030 against 0.0079 — over-suppressed with this key, where a different
key over-shoots it. Twelve free cells do land, including flat unigrams, entropy,
off-diagonal bigram uniformity, the kappa maximum, the clock, d2w, d4w, d5w, d5x and
the doublet minimum gap.

Whether the three can be reached is open and cheap to test: the mechanism fixes only
which four runes `g` holds still, leaving its five 5-cycles and the whole of σ free —
roughly the same key material the walk spends — so there is ample freedom left to fit
d3, d6 and the seam.

**Tried, September 2026** (`experiments/dodge_three_cells.py`). Holding the fixed points
at this file's own best choice {4, 8, 18, 19} and redrawing the five 5-cycles, σ and the
initial base 150 times:

| cell | corpus | model median | min | max | within 2 SE |
|---|---|---|---|---|---|
| d1w | 0.0063 | 0.0051 | — | — | **150/150** |
| d3w | 0.0370 | 0.0565 | **0.0428** | 0.0722 | **0/150** |
| d6w | 0.0245 | 0.0403 | 0.0292 | 0.0680 | 24/150 |
| seam | 0.0079 | 0.0038 | 0.0000 | 0.0188 | 128/150 |
| doublet_pos | 0.5532 | 0.5638 | — | — | **150/150** |

**d3w never lands.** Its minimum over 150 draws is 0.0428, above the corpus's own 2 SE
ceiling of 0.0422 — the model systematically over-produces distance-3 coincidence, and no
choice of the free parameters brings it down. The seam lands easily and d6w lands 16% of
the time; all three together, **0 of 150**.

d1w and the doublet position are constant across every draw, exactly as the mechanism
requires: they are set by the fixed points alone. So the freedom this file counted on is
real but is the wrong freedom — it moves d3w over a range that does not include the
target.

What remains open is narrower: whether one of the *other* admissible fixed-point choices
— the file counts 21 of 220 that land the doublet rate and position together — shifts
d3w's whole range downward. That is the test to run next, and it is no longer the
open-ended one this paragraph used to describe.

**A harness trap worth recording.** The first run of this test fed `lp_words()` in as
plaintext. That function returns the LP **ciphertext**; the plaintext surrogate is
`prose_corpora()`, and neither name says so. With the ciphertext as input the doublets are
already suppressed to 0.0063, the model cannot produce them at all — d1w reads 0.0008 —
and the three cells appear to land 54% of the time. Every figure above uses prose.

## The retracted disproof, and why it was wrong

The first pass reported the doublet position at 0.833 against the corpus's 0.553,
z = −5.2, and called the hypothesis dead by the same test that disproved
`stay-slot-hold.md`. Re-measured across ten keys per model:

| model | doublet position over 10 keys |
|---|---|
| length-clocked walk | 0.368 – 0.600, median 0.470 |
| this model | 0.295 – 0.780, median 0.612 |
| **corpus** | **0.553** |

**Both models bracket the corpus.** The statistic is set by WHICH runes take part in
doublets — for this model, exactly the four `g` holds still — so it is a free parameter
of the same 14-bit choice that sets the rate, not an independent prediction. Searching
220 random choices of those four runes, **21 (10%) land the doublet rate and the
position together**; the best, fixing runes {4, 8, 18, 19}, gives 0.0053 and 0.570
against the corpus's 0.0063 and 0.553.

The error was reporting a single fitted key as if it were the model, the same mistake
recorded for the walk's own held-out run in `length-clocked-walk.md`.

## What it does not get either

It produces the DJU-BEI-style repeat in a first version with a small base set — but
that version failed IoC and identical-word counts outright, and once the base steps
properly (`g^a ∘ σ`, giving full base diversity) the repeat disappears again, exactly
as for the walk. So it does not rescue that cell either.

## What to do next

- ~~Decodability is the real obstacle.~~ Measured above: the family decodes with the key
  plus context, at a cost of 0–6 runes in 12,388. It is no longer the blocking
  objection, and the search for a decodable trigger is no longer needed to keep the
  family alive.
- **Fit the rest of `g`.** Only the four fixed points are used; the five 5-cycles and
  all of σ are free, which is about the key material the walk spends on its diagonals.
  Fitting them to d3w, d6w and the seam is a small search and would settle whether the
  model reaches the whole profile.

## Scripts

- `experiments/doublet_dodge_walk.py` — the cipher, the algebraic self-test (every
  survivor is a plaintext double on a fixed point), the decoding collision, and the
  battery score.

## Related

- `stay-slot-hold.md` — reaches the same "doublets are plaintext doubles" prediction by
  a different route. Its positional disproof and the one retracted here rest on the same
  statistic, which this file shows to be key-dependent, so that file is flagged for
  re-checking across keys.
- `interrupted-walk.md` — the decodable but disproved sibling, where the skip is
  triggered by a marked plaintext rune instead.
- `length-clocked-walk.md` — the model this replaces the tuning of; its seam/within-word
  equality is unexplained there and automatic here.
- `doublet-suppression-requires-design.md` — the escape list this adds a member to.

## Verdict

Unresolved, and the best-value proposal here. It buys the doublet suppression, the
seam/within-word equality and much of the distance profile with ~14 bits and no tuned
diagonal, where the walk spends ~100 bits fitting them. The positional disproof is
withdrawn: both models bracket the corpus on that statistic and 10% of this model's
fixed-point choices hit the rate and the position at once.

The decodability objection is now withdrawn as a blocker too. It is true that distinct
plaintexts share a ciphertext, and false that this prevents reading the message: a beam
search holding the key recovers 12,382–12,388 runes of 12,388, exactly for half the
keys tried. The cipher costs its reader a handful of letters and the need to read in
context.

What stands against it is three cells (d3w, d6w, seam) not yet shown to be reachable
with the key material it leaves free. That is concrete, testable and untried.
