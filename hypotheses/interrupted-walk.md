---
type: hypothesis
---
# Hypothesis: The Walk with 3301's Own Interrupter

## Claim

The length-clocked walk, with the letter clock skipping an extra step whenever the
plaintext rune falls in a marked set — the device 3301 uses on its own solved AN END
page, where the keystream interrupts at ᚠ.

```
c_j = base_w( g^(k_j)( p_j ) ),    k_(j+1) = k_j + 1 + [ p_j ∈ S ]
```

Proposed September 2026, on the reasoning that the walk's one falsifiable cell
over-predicts — model d5 0.056–0.059 against the corpus's 0.0492 — and that φ5, the
distance-5 leak fraction, has sat at 0.64–0.85 for a year, "consistent with full leak
but below it" (`d5-partial-alphabet-leak.md`). Both suggest something occasionally
breaks the period-5 alignment, and an interrupter is exactly that, in the author's own
documented idiom.

## Status

**Status**: disproved (September 2026). It is decodable and it is in style, but it
cannot deliver the d5 reduction it was proposed for, and it destroys the doublet
suppression on the way. Both failures have the same cause and generalise — see the
bound at the end, which is the useful part.

## Mechanism

The clock still advances once per rune and the alphabet still has period 5; an
interrupt costs one extra step. Decryption is unambiguous for the reason 3301's own
page is: the decoder recovers `p_j` and only then knows whether to skip, so no
lookahead is needed (`experiments/interrupted_walk.py` asserts the round trip).

## Evidence against

**1. The d5 rate barely moves, and cannot be driven down.** The proposal predicted
φ5 = (1 − s)⁵ with s the interrupt rate. That is wrong. With `n` interrupts between a
pair the relation is `g^n`, and **g⁵ = id**, so the rate CYCLES rather than decaying:
five interrupts return it to the identity and the full plaintext rate. Measured on a
fitted key:

| marked runes | interrupt rate | d5 | drop |
|---|---|---|---|
| 0 | 0.0000 | 0.0727 | — |
| 8 | 0.0230 | 0.0683 | 6.2% |
| 13 | 0.1188 | 0.0708 | 2.7% |
| 15 | 0.1664 | 0.0693 | 4.8% |

About 5%, where the corpus needs roughly 30%.

**2. It destroys the doublet suppression.** At an interrupt the adjacent relation
becomes `g²` rather than `g`, and `g²`'s diagonal is at chance — the corpus itself
says so, d2w = 0.0347. Scored on the held-out battery
(`experiments/fingerprint_battery.py`) with the interrupt rate fitted to the corpus's
d5, the model reads **d1w 0.0137 against 0.0063** and d6w 0.0384 against 0.0245, and
four free cells miss (doublet position, doublet minimum gap, identical words, the
repeat) where the plain walk misses one.

## The bound this leaves, which is the useful result

The second failure is not special to interrupters. **Any** mechanism that perturbs the
relation between ADJACENT positions injects chance-rate coincidences into d1, and the
observed doublet rate is too tight to absorb much. Requiring d1 to stay inside its
Wilson top of 0.0080:

| `g`'s achievable diagonal | maximum perturbation rate |
|---|---|
| 0.0000 (the floor) | 23% |
| 0.0040 (a realistically tuned `g`) | **13%** |
| 0.0063 (the observed rate itself) | 6% |

So any proposal of the form "the walk, but something occasionally happens" — an
interrupter, a skipped step, a re-draw, a hold, a phase slip — is capped at roughly
**10–15% of positions**, and at that rate it cannot move any other cell far either.
The doublet suppression is the corpus's tightest constraint and it forbids occasional
perturbation almost as firmly as it forbids none.

That also explains why this family looked attractive and is not: the cells it was
meant to fix (φ5, the d5 over-prediction) are soft and register-dependent, while the
cell it breaks is the hardest number in the corpus.

## Predictions

- Any surviving perturbation mechanism must perturb something OTHER than the adjacent
  relation — the base, the word boundary, the plaintext — or must keep `g²`'s diagonal
  low as well as `g`'s, which costs a second tuned relation and buys nothing measured.

## Scripts

- `experiments/interrupted_walk.py` — the cipher, the round-trip self-test, the
  measured d5 response and the battery score.

## Related

- `length-clocked-walk.md` — the model this perturbs; its d5 over-prediction is the
  motivation, and its register caveat is why that motivation is weak.
- `d5-partial-alphabet-leak.md` — φ5, which this cannot explain after all.
- `doublet-suppression-requires-design.md` — the constraint that kills it.
- `stay-slot-hold.md` — an earlier hold mechanism, disproved on the doublet position
  profile; this is the same family failing on the doublet rate instead.

## Verdict

Disproved. Worth keeping for the bound: the doublet rate caps any occasional-perturbation
mechanism at ~10–15% of positions, which is too little to reshape any other cell. The
proposal was aimed at the walk's softest, most register-dependent miss and was stopped
by its hardest number.
