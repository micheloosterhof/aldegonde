---
type: hypothesis
---
# Hypothesis: The Preventer Is a Plaintext Null

## Claim

When the next ciphertext rune would repeat the one just written, the encipherer inserts
a **null plaintext symbol** and enciphers it like any other rune, then continues. The
null is one of the runes the author never writes (J, EO, OE, AE: five occurrences in the
2,882-rune register). Decryption is "drop every null".

## Status

**Status**: unresolved. Proposed 2026-10-24 in review of the relation catalogue
(`no-natural-relation-suppresses-doublets.md`); no prior entry in this directory. It is
observationally close to the dodge and differs from it in one measurable channel, the
block lengths.

## Mechanism

Any carrier that changes alphabet every letter (the walk, a Quagmire schedule, an
odometer). At position j+1 the encipherer computes c and compares it with c_j. If equal,
it emits the current alphabet's image of the null instead, advances the clock, and
enciphers p_{j+1} at the next position. The null's image is uniform under a mixed base, so
it repeats c_j with probability 1/29; the rule then applies again at the following
position.

## Evidence for

What the ledger (`what-any-solution-must-satisfy.md`) asks of a preventer, the null
gives without a parameter:

| row | requirement | the null |
|---|---|---|
| D3 | the deficit belongs to the emitted stream, not the schedule | inspects the output |
| D5 | rune-blind | the null's image is uniform |
| D11 | strictly adjacent, memory of one rune | compares with c_j only |
| D9 | φ ≈ 0.90, [0.80, 1.00] at 2σ | φ = 1 − 1/29 = 0.966 |
| D10 | clock perturbation q ∈ [0.003, 0.262] | q ≈ 1/29 ≈ 0.034 |
| `stay-slot-hold.md` | surviving doublets positionally flat | the survivors are the null's own collisions, placed wherever would-be repeats fall |
| zero triplets | | a surviving doublet is followed by a fresh would-be repeat with probability 1/29, nulled again: about 0.1 triplets expected |
| boundary-blind | the seam is suppressed too | a null can open a word |

It also uses a fact no other reading uses: the author's alphabet has four runes his
plaintext does not, which is what a null symbol needs.

## Evidence against

- The blocks grow. Would-be repeats occur at about 1/29 of positions, so the body would
  carry roughly 450 nulls and its blocks would average about 0.15 runes more than the
  plaintext words. The body's blocks do average 4.42 against the author's 4.01, but
  `short-units-are-written-joined.md` already spends that surplus on joining 2-rune
  units at q ≈ 0.40 with P = 0.79. The two effects compete for one surplus.
- Nothing distinguishes a null from a dodge in any within-word coincidence statistic:
  both advance the clock once per would-be repeat and both emit a uniform rune there.

## Predictions

1. Block lengths are the plaintext lengths plus a Binomial(L, 1/29) number of nulls,
   with no free parameter. Re-run the joining fit of `short-units-are-written-joined.md`
   with that inflation applied first; the fitted join rate should fall and the fit
   should hold. If P drops below about 0.05 the null is out.
2. Under a dodge the number of runes equals the number of plaintext letters; under a
   null it exceeds it by about 450. Any decryption candidate can be checked for this.
3. A null that opens a word makes that block one rune longer at the seam rate 0.0079 ×
   2,927 ≈ 23 words; too few to see in the marginal, so prediction 1 carries the test.

## Scripts

- `experiments/natural_relations_doublet_rate.py` — the φ bound for homophones and the
  null, and the register's unused runes.
- To write: the inflated joining fit, as a flag on `short_units_are_written_joined`'s
  script or a sibling.

## Related

- `explicit-doublet-avoidance.md` — deterministic post-processing fixes, excluded; the
  null is applied at emission time and emits a uniform rune, so those tests do not reach
  it.
- `stream-cipher-no-repeat.md`, `doublet-dodge-walk.md`, `quagmire-dodge.md` — the
  dodge readings this one differs from only in the length channel.
- `doublet-marker-rune-ea.md` — the fixed-rune marker, excluded on the positional
  profile; the null predicts the flat profile that test found.

## Verdict

Open. One parameter-free prediction, in the block lengths, decides it against the dodge.
