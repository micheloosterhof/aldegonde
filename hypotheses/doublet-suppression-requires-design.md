---
type: observation
---
# Observation: Sub-Chance Doublets Force a Tuned Permutation Relation

## Feature

Michel asked for a mechanism explaining the low doublet rate (within AND across
words) and the d5 echo, **without** g/σ permutations. This note records why that
combination is not available: for any cipher that is invertible position by
position, a sub-chance doublet rate is *equivalent* to a rare-diagonal permutation
relation. The primitives can be rings, grids, arithmetic or keywords; the constraint
is the same.

## The argument

Let the cipher be invertible at each position, `c_j = f_j(p_j)` with each `f_j` a
bijection on the 29 runes. Define `R_j = f_j⁻¹ f_{j+1}`. Then

```
c_j = c_{j+1}   ⟺   f_j(p_j) = f_{j+1}(p_{j+1})   ⟺   p_j = R_j(p_{j+1})
```

so the doublet rate is the average over positions of `Σ_b P(R_j(b), b)` — the
**diagonal of a permutation** on the plaintext bigram table. Chance is 1/29 = 3.45%;
the corpus shows 0.63% within words and 0.79% across. Reaching that requires the
`R_j` to be rare-diagonal, i.e. designed against the digraph table.

`R_j` is a permutation by construction. So "no permutations" and "sub-chance
doublets" are incompatible **within this class**, whatever the mechanism looks like
from outside. Only the diagonals matter, and a device that produces them is
producing a tuned permutation whether or not it is described as one.

Note this also explains the boundary-blindness cheaply: the argument never mentions
word boundaries, so it applies identically at a seam with `R = σ`.

## It also fixes the operation order: g-inner, not g-outer

The `R_j` must be rare-diagonal *and the same across words*, which decides where
the letter-walk sits relative to the per-word base — the order is observable, not
a convention (`experiments/operation_order.py`). With the walk INSIDE the base,
`c = base_w(g^j(p))`, the base cancels in a coincidence and `R = g` is fixed, so
a designer tunes g's diagonal as low as wanted. With the walk OUTSIDE,
`c = g^j(base_w(p))`, the relation is `base_w(p_i) = g(base_w(p_{i+1}))`, i.e.
`R_w = base_w⁻¹ g base_w` — a conjugate of g that changes every word. Conjugating
by the fresh per-word base randomises the diagonal, so the doublet rate floors at
`P(pt doublet)·4/29 + P(non)·25/812 ≈ 0.033` regardless of g — five times the
observed 0.0063, and simulation confirms 0.0330 (theory 0.0331) against g-inner's
tunable-to-zero rate. The one escape, choosing every base to centralise g so the
conjugate stays low, collapses the base count into g's ~9×10⁶-element centralizer
and is excluded by `base-count-floor` / `sigma-power-step.md`. So the LP is
g-inner: the walk acts on the plaintext, then the per-word alphabet substitutes.

## What a genuinely new mechanism would have to break

Per-position bijectivity. The known ways, and their status:

| class | how it escapes | status |
|---|---|---|
| **Fractionation** (bifid etc.) | `c_j` mixes coordinates from several `p` | **excluded structurally** — an output doublet needs both coordinates to collide, and balanced marginals floor the product near 1/(rows×cols) ≈ chance. Annealed 5×6 grids reach 0.0237–0.0246 against 0.0063 (`bifid-fractionation.md`) |
| **Ciphertext feedback** (`f_{j+1}` depends on `c_j` alone) | adjacent positions coupled by construction | **excluded empirically** — each group sharing a previous rune would be enciphered by one fixed map, so grouped IoC must read ~1.78; measured within words 1.0227 / 0.9979 / 1.0060 at lags 1/2/5 |
| **Mixed feedback** (ciphertext *and* plaintext taps) | a plaintext tap convolves the grouped distribution flat again | **not excluded by the grouped-IoC test** (`dual-autokey-lag1-lag5.md` reaches 1.046 where the pure form gives 1.756) — but it does NOT escape this note: its doublet suppression requires a tuned labelling, which is a permutation, and over random labellings it sits at chance |
| **Homophonic** (one plaintext letter, several runes) | the encoder simply declines to repeat, so suppression is free | **excluded by alphabet size** — 29 runes in, 29 out leaves no spare symbols (`homophonic-substitution.md`) |
| **Digraphic** (unit is a rune pair) | doublets constrained inside a pair | **disfavoured** — flat parity at periods 2–6 |

## The one structural gap

**Homophonic remains the only class** where the suppression would cost nothing rather
than being designed, and it fails only on alphabet size.

A mixed-feedback candidate (`dual-autokey-lag1-lag5.md`) appeared to escape this
conclusion and does not. Its apparent structural suppression — 2.28% against a 3.45%
chance — was one labelling's fluctuation: over 200 random labellings the mechanism
gives 3.41% ± 0.76, i.e. chance. Its suppression comes from tuning the labelling, and
a labelling is a 29-permutation. The conclusion of this note is unaffected. It would revive if the ciphertext
alphabet were larger than the plaintext alphabet — which is what
`thirty-symbol-disk.md` (unresolved) posits, treating the `.` mark as a 30th symbol.

The obvious version of that is already refuted. If a mark were inserted to break a
would-be doublet, the runes flanking a mark would be EQUAL by construction, so the
across-mark rate would be near 1. Measured: **0.786%**, i.e. suppressed like
everything else. Any surviving variant must therefore break doublets without leaving
equal runes on either side of the inserted symbol.

## What is NOT claimed

That no new mechanism exists. The argument is exact only for per-position-bijective
ciphers; outside that class it is a table of four known escapes with their statuses,
not a proof of exhaustiveness. A fifth escape not listed here would not contradict
anything measured.

Nor does any of this address the **d5 echo**, which is a separate requirement: the
transformation at positions `j` and `j+5` must coincide, so something must have
period 5 regardless of how the doublet question resolves.

## Scripts

- `experiments/sigma_local_budget.py` — the seam relations, including the across-mark
  rate quoted above.
- `experiments/information_budget.py` — the grouped-IoC and delta-stream measurements
  that exclude feedback.

## Related

- `bifid-fractionation.md`, `homophonic-substitution.md`, `thirty-symbol-disk.md`,
  `stream-cipher-no-repeat.md` — the four escape classes.
- `doublet-suppression.md` — the measurement being explained.
- `length-clocked-walk.md` — the model that pays the design cost this note describes.

## Demonstrated on the author's own ciphertext, not only in simulation (September 2026)

The argument above is made from first principles and checked against simulated
ciphers. `solved-page-testbed.md` now supplies the missing empirical leg: real LP
ciphertext whose cipher is known, from the same author and the same book.

| corpus | words | d1 rate | × chance | z vs chance |
|---|---|---|---|---|
| plaintext, 6 pages | 231 | 0.0247 | 0.72 | −1.49 |
| monoalphabetic ciphertext, 5 pages | 255 | 0.0184 | 0.53 | −2.35 |
| **interrupted Vigenère ciphertext, 4 pages** | 212 | **0.0305** | **0.89** | −0.54 |
| the unsolved body | 2,928 | 0.0063 | 0.18 | −15.48 |

The three known groups behave exactly as the theory requires, which is what makes the
fourth row mean something:

- **Monoalphabetic preserves coincidence**, so it inherits the plaintext's own mild
  suppression (0.53× against the plaintext's 0.72×, consistent within noise).
- **Polyalphabetic decorrelates**, so it returns the rate to chance: 0.89×, z = −0.54.
  This is the "baseline is 1.0 whatever the plaintext does" step that the argument
  elsewhere in this directory assumes; here it is measured on the author's own work
  rather than assumed.
- **The body is nowhere near either.** At 0.0063 it sits 4.9× below 3301's own
  polyalphabetic output, a difference of z = −3.49 (19/622 against 63/10028).

So the body's doublet suppression is not something polyalphabetic encipherment
produces on its own — the author's own polyalphabetic pages demonstrate that it does
not. A mechanism is required, which is this file's claim, now with a non-simulated
control behind it.

**Limits.** The front-matter groups are small (622 within-word pairs for the Vigenère
row) and their register is didactic where the body's is not. The comparison is
directional and 3.5 sigma, not decisive on its own; its value is that every step is
measured on real material from the same source.

## How much design, in bits (September 2026)

The argument above says a tuned permutation relation is required. With the author's own
plaintext available the requirement can be priced.

Under the walk the alphabet at within-word position j is `base_w ∘ g^j`, so the
relation between adjacent positions is `A_(j+1)⁻¹ ∘ A_j = g⁻¹`, constant in both the
word and the position. A ciphertext doublet means `p_(j+1) = g⁻¹(p_j)`: the plaintext
pair lies on the **graph** of `g⁻¹`. So the within-word doublet rate is exactly

    Σ_x P(p_j = x, p_(j+1) = g⁻¹(x))

the plaintext bigram mass `g⁻¹` selects. `experiments/doublet_constrains_g.py`
validates this on planted walks before using it — predicted and observed agree to five
decimals on every trial — because an earlier attempt at this argument used *fixed
points* rather than the graph and was wrong (`key-local-channel-is-empty.md`).

Against the author's own within-word bigrams, over 200,000 random order-5 permutations:

| | |
|---|---|
| body's within-word doublet rate | 0.00628 (0.182× chance) |
| mean mass selected by a random order-5 g | 0.0331 (= 1/29) |
| standard deviation | 0.0143 |
| **fraction of g selecting ≤ the body's rate** | **0.0046, or 1 in 215** |

**So the doublet suppression alone constrains g by about 7.8 bits.** That is real
design — 99.5% of order-5 steps are excluded — but it is modest, not the astronomical
tuning the phrase "requires design" might suggest. It is also consistent with
`key-local-channel-is-empty.md`'s independent figure of 16.0 bits of local constraint
on g from distances 1 through 7, of which this is the d1 share.

**Direction of the caveat matters.** The bigram table is 1,477 pairs over 841 cells, so
it is sparse and a random g often selects empty cells. That makes low sums *easier* to
reach by chance, so 1-in-215 is an upper bound on the fraction and 7.8 bits is a lower
bound on the constraint.

## A discriminator that does not exist, and why (September 2026)

Two mechanisms are on the books for the suppression: an explicit rule that fires on
equality, and a tuned letter step whose graph sits on low-mass plaintext pairs. They look
as though they should differ **per rune** — a rule that fires on equality is
value-independent and should suppress every rune equally, while a tuned diagonal has 29
different entries and should not.

Measured, the body's suppression is uniform: pooled factor 0.1925, homogeneity χ² **27.8
on 28 df** against a 5% critical value of 41.3. That looks like evidence for the rule.

**It is not, and the reason is structural.** Under the walk, adjacent positions carry
`base ∘ g^j` and `base ∘ g^(j+1)`, so a ciphertext doublet at value x requires
`g^j(p_i) = g^(j+1)(p_{i+1})`, i.e. `p_i = g(p_{i+1})`. The plaintext condition is about
g — but the ciphertext *value* it lands on is `base(g^j(p_i))`, and base changes every
block while j runs over five phases. The value is randomised before anyone sees it.

Planted walks confirm it. Four walks with **no doublet rule at all** give homogeneity χ²
of 23.1, 11.8, 28.8 and 28.9 — the body's 27.8 sits in the middle of them. The statistic
has no power, and the apparent evidence for the rule is nothing.

Recorded so it is not tried again. Any per-rune statistic of the ciphertext is blind to g
for the same reason: the base absorbs the value.

**The control does reproduce this file's own result from a new direction.** Those same
four walks, carrying a per-block base and a letter step of order 5 and nothing else, give
suppression factors of **0.74 to 1.40** where the body gives **0.19**. A walk does not
suppress doublets. Something in the mechanism does.
