---
type: hypothesis
---
# Hypothesis: The Order-5 Step is a Fractional-Linear Map on 30 Points

## Claim

The letter step `g` is a fractional-linear (Möbius) map `x → (ax+b)/(cx+d)` acting on
the projective line over F₂₉ — the 29 residues plus a point at infinity, 30 in all —
and the space step σ is another. Michel's question (September 2026): the project has
addition and multiplication; is exponentiation available, and does it reach order 5?

It does not, and this family is the only algebraic one that does.

## Status

**Status**: disproved (September 2026). The algebra is correct and the family is the
smallest complete candidate set the project has had, 1,792 keys. It fails because an
order-5 Möbius map cannot avoid emitting the extra point, and every way of writing
that point contradicts the transcription.

## Mechanism

No operation on 29 symbols has order 5, exponentiation included
(`experiments/order5_algebraic_routes.py`):

| operation | achievable orders | why |
|---|---|---|
| power maps `x^k` | 1, 2, 3, 6 | acts as multiplication by k in Z/28, so the order divides \|(Z/28)*\| = 12 |
| affine `ax + b` | 1, 2, 4, 7, 14, 28, 29 | orders divide 28 or equal 29 |

5 divides neither 12 nor 28. This completes the exclusion in `length-clocked-walk.md`,
which covered shifts, multiplication and affine maps but not powers.

On the projective line the maps form PGL(2,29) of order 29·28·30 = 24,360, and element
orders divide 28, divide 30, or equal 29. **5 divides 30**, so order-5 elements exist:
exactly **1,624**, every one of cycle type **5⁶**, and **none fixes the extra point**.
So an algebraic order-5 step forces a 30-symbol alphabet and a fixed-point-free step,
where the walk's 29-symbol `g` has cycle type 5⁵1⁴ with four fixed points.

## Evidence for

**Both diagonals are reachable, which no arithmetic family on 29 symbols managed.**
`sigma-power-step.md` excludes affine σ because it floors at 0.0122 against an observed
seam of 0.0079, and inverse maps `a/x+b` at 0.0162. Measured on prose over 30 points
(`experiments/mobius_walk.py`):

| | reachable minimum | observed |
|---|---|---|
| order-5 Möbius `g`, within-word doublet | 0.0040 | 0.0063 |
| Möbius σ, seam | 0.0076 | 0.0079 |

Keeping only maps whose diagonal lands inside the observed 95% interval leaves **28
letter steps and 64 space steps**, a complete family of **1,792 keys** — against ~10⁴⁸
for freely designed permutations.

**A fixed-point-free step suits the low doublet rate.** A fixed point `x` of `g` makes
the doublet condition fire on plaintext doubles of `x`. With cycle type 5⁵1⁴ the four
fixed points must all sit on runes that almost never double; with 5⁶ the low rate needs
no such coincidence. `period5-doublet-linkage.md` reaches the same point from the other
side, recording that `g` has low-frequency fixed points.

## Evidence against — the extra point cannot be hidden

**It must be emitted.** For the output never to be the extra point, the g-orbit of
`base_w⁻¹(∞)` — five points — would have to be disjoint from the plaintext alphabet.
The plaintext alphabet is 29 of the 30 points, so its complement is one point and
cannot hold an orbit of five. The emission rate is `(1/5)·Σ freq` over that orbit,
minimised over the free choice of base. Across all 1,624 order-5 maps it ranges from
0.00091 to 0.0285; **across the 28 inside the doublet band the minimum is 134.6
emissions** in the corpus, median 257.3, and none is under 100.

So the family predicts that 135 to 359 of the transcribed word boundaries are cipher
output rather than spaces. Three ways to write that point, all excluded:

1. **As its own symbol.** It would occupy 1/30 = 3.33% of the stream. The cluster
   marks occupy 1.29% and the word separators 18.6%, and no combination gives 1/30.
2. **As a word separator.** Then an emission at a word's first or last rune puts two
   separators in a row. At 22.6% of positions being word-initial, the weakest candidate
   predicts **26 to 70 empty words**. The clean corpus contains **zero**: of its 238
   adjacent separator pairs, 235 have transcription annotation between them and 3 have
   only a line wrap. At the most favourable candidate that is p ≈ 5×10⁻¹².
3. **Skipped, not written.** Not uniquely decodable. The forbidden rune at phase j is
   emitted under phase j+1, which is exactly what `g(p)` produces at phase j, so the
   two plaintexts are indistinguishable. A collision was found for **200 of 200**
   random bases.

**And the word lengths point the other way.** Spurious breaks split words into short
fragments, but the corpus already holds far fewer 2-rune words than English (15.9%
against 23.7%, z ≈ −10, `two-rune-deficit.md`). Removing the fragments to recover the
true words would push that share lower and deepen the sharpest anomaly in the corpus.

## The escape is closed from both sides

The emission count could be survivable if `g`'s infinity-orbit held only the rarest
runes: the four rarest occur about 30 times between them in 12,956 runes, so such a
map would emit roughly a dozen times and leave about three empty words, which the
test above could not see. That requires one map to be good at two things at once, and
none is. Over all 1,624 order-5 maps:

| doublet diagonal at most | maps | fewest emissions any of them allows |
|---|---|---|
| 0.0063 (the observed rate) | 1 | 335.9 |
| 0.0121 (top of the 95% interval) | 28 | 134.6 |
| 0.0200 | 227 | 62.2 |
| 0.0500 | 1,431 | 11.8 |

| emissions at most | maps | lowest doublet diagonal any of them allows |
|---|---|---|
| 30 | 8 | 0.0250 |
| 60 | 8 | 0.0250 |
| 135 | 172 | 0.0078 |

The two requirements are mildly anticorrelated (r = −0.19) and cannot be met
together. A map quiet enough to hide — 30 emissions or fewer, so about six empty
words — carries a doublet diagonal of at least 0.0250, which predicts **251 within-word
doublets against the 63 observed, z = −11.9**. A map matching the doublet rate emits at
least 135 times and leaves empty words that do not exist. There is no middle: at the
observed 0.0063 the best available map emits 336 times.

## A caveat on the empty-word test

It assumes a scribe writing two separators in a row would record both, and the
transcription would keep them. If doubled separators collapse to one in the writing,
the test is silent and only the word-length argument stands. The re-transcription
distinguishes five mark glyphs carefully (`mark-glyph-inventory.md`), which makes a
silently dropped doubling less likely, but it is not ruled out.

## The enumeration, and why it decides nothing on its own

All 1,792 keys were scored with the base₀-free verifier at 30 points
(`experiments/mobius_walk.py --run`). Best 1.000, where a planted key of the family
reaches 1.765 and wrong keys reach 1.019. Nothing decrypts.

**That run is not the refutation, and must not be cited as one.** It clocks the walk
with the word lengths as transcribed, while every candidate says 5–12% of those
boundaries are cipher output. A sweep on a wrong clock cannot find a key it contains —
the same flaw as the DJU-BEI gate (`dju-bei-gate-validity.md`). The refutation is the
emission argument above, which needs no key search.

## Predictions

- Any surviving 30-point construction must keep the extra point out of the output.
  That requires a plaintext alphabet of at most 25 symbols, since the orbit takes 5 of
  the 30, which runeglish's 29 runes exceed.
- If a doubled separator ever turns up in a re-transcription, point 2 above reopens.

## Scripts

- `experiments/order5_algebraic_routes.py` — the order census for every operation, the
  PGL(2,29) enumeration, the emission rates and the skip-rule collision.
- `experiments/mobius_walk.py` — the candidate bands, the 1,792-key enumeration and the
  30-point verifier self-test.
- `experiments/walk_score_kernel.c` — compiles for either alphabet size.

## Related

- `length-clocked-walk.md` — its "why no construction for `g` can help" argument, which
  this extends: the conjugacy argument covers 29 points, and 30 points is where the
  algebra actually lives.
- `thirty-symbol-disk.md` — the other 30-symbol proposal, reached from the marks rather
  than from the group.
- `sigma-power-step.md` — the arithmetic σ floors this family clears.
- `two-rune-deficit.md` — the word-length anomaly this family deepens.

## Verdict

Disproved, and worth keeping for the algebra. The period the corpus shows cannot come
from any operation on 29 symbols, and the one family that supplies it needs a 30th
point that the transcription has nowhere to put: written as a symbol it is too rare,
written as a separator it would leave empty words that do not occur, and skipped it is
not decodable. The quiet-map escape closes the other way, at z = −11.9 on the doublet
count. So the order-5 step is a designed permutation rather than an algebraic map,
which is the walk's reading, unless the plaintext alphabet holds at most 25 symbols —
and runeglish has 29.
