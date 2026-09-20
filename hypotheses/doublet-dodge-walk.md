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

**Status**: unresolved, and the most economical proposal this directory has had. A
first pass here called it disproved on the doublet POSITION profile; **that verdict is
retracted** — it rested on one arbitrarily drawn key, and the statistic is strongly
key-dependent for both this model and the walk. What stands against it is unique
decodability, and three cells it has not yet been shown to reach.

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

**1. It is not uniquely decodable.** A skip emits `base(g^(k+1)(p_(j−1)))`, which is
exactly what the unskipped clock emits for a repeated plaintext rune. So `x x` and
`x g⁻¹(x)` produce identical ciphertext, and a decoder holding the whole key cannot
separate them — `experiments/doublet_dodge_walk.py` exhibits a concrete collision. The
condition is on the OUTPUT, and an output-conditioned skip cannot be undone; 3301's own
interrupter avoids this by conditioning on an already-decoded plaintext rune. This is
the substantive objection.

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
d3, d6 and the seam. Nobody has tried.

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

- **Decodability is the real obstacle.** A decodable variant must condition the skip on
  something already decoded. Conditioning on `p_(j−1)` alone is `interrupted-walk.md`,
  which is disproved. Conditioning on the previous CIPHERTEXT pair — "skip if the last
  two emissions were equal" — is decodable and reacts to doublets instead of preventing
  them, so it would need the suppression from somewhere else; untested.
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

What actually stands against it is unique decodability — an output-conditioned skip
cannot be undone — and three cells (d3w, d6w, seam) not yet shown to be reachable with
the key material it leaves free. Both are concrete and testable, and neither has been
tried.
