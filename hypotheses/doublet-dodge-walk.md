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

**Status**: disproved (September 2026), on the doublet POSITION profile and on unique
decodability. It is nonetheless the most economical proposal this directory has had —
it gets six cells for free that the walk has to fit — and the two failures are sharp
and specific.

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
- **The distance profile comes free.** Scored on the held-out battery with only the
  four fixed points chosen, **d2w, d3w, d4w and d5w all land** (tails 0.20, 0.13, 0.93,
  0.57) — cells the walk has to fit.

Verified in `experiments/doublet_dodge_walk.py`: every surviving doublet in a simulated
corpus is a plaintext double on a fixed point of `g`, zero exceptions.

## Evidence against

**1. The doublet position profile, at z = −5.2.** If the survivors are plaintext
doubles then they inherit English's positional habit, which is strongly end-heavy. The
model puts the mean doublet position at **0.833**; the corpus reads **0.553**. This is
the same measurement that disproved `stay-slot-hold.md`, for the same reason: any
mechanism making ciphertext doublets *be* plaintext doubles predicts a positional
signature the corpus does not carry. Note the corpus sits between this model's 0.833
and the plain walk's 0.40, so neither pure mechanism matches.

**2. It is not uniquely decodable.** A skip emits `base(g^(k+1)(p_(j−1)))`, which is
exactly what the unskipped clock emits for a repeated plaintext rune. So `x x` and
`x g⁻¹(x)` produce identical ciphertext, and a decoder holding the whole key cannot
separate them — the script exhibits a concrete collision. The condition is on the
OUTPUT, and an output-conditioned skip cannot be undone; 3301's own interrupter avoids
this by conditioning on an already-decoded plaintext rune.

**3. d6 still needs a tuned `g`.** With `g` untuned, d6w comes out at chance, 0.0444
against the corpus's 0.0245 (p = 0.000). The d6 suppression is `diag(g)` on the
distance-6 table and this mechanism does not touch it, so the economy is smaller than
it first looks: one tuned relation is still required, just not for d1.

**4. The seam is suppressed but not enough**, 0.0142 against 0.0079 (p = 0.000).

## What it does get that the walk does not

It produces the DJU-BEI-style repeat in a first version with a small base set — but
that version failed IoC and identical-word counts outright, and once the base steps
properly (`g^a ∘ σ`, giving full base diversity) the repeat disappears again, exactly
as for the walk. So it does not rescue that cell either.

## Predictions, if it is to be rescued

- A decodable variant must condition the skip on something already decoded. Conditioning
  on `p_(j−1)` alone is `interrupted-walk.md`, which is disproved.
- A mixture — some doublets from a tuned diagonal, some surviving plaintext doubles —
  would sit between 0.40 and 0.833 on the position profile and could reach the observed
  0.553. That is a free parameter and it is untested.

## Scripts

- `experiments/doublet_dodge_walk.py` — the cipher, the algebraic self-test (every
  survivor is a plaintext double on a fixed point), the decoding collision, and the
  battery score.

## Related

- `stay-slot-hold.md` — disproved by the same positional test; this is a different
  route to the same prediction.
- `interrupted-walk.md` — the decodable but disproved sibling, where the skip is
  triggered by a marked plaintext rune instead.
- `length-clocked-walk.md` — the model this replaces the tuning of; its seam/within-word
  equality is unexplained there and automatic here.
- `doublet-suppression-requires-design.md` — the escape list this adds a member to.

## Verdict

Disproved, and the best-value idea in this directory. It buys the doublet suppression,
the seam equality and the whole d2–d5 profile with ~14 bits and no tuned diagonal,
where the walk spends ~100 bits fitting them. It dies on the doublet position profile
at z = −5.2 and on unique decodability, and it still needs a tuned `g` for d6.

The positional result is the durable one: the corpus's doublets sit at 0.553, between
a tuned-diagonal mechanism (0.40) and a plaintext-double mechanism (0.833), and no pure
version of either reaches it.
