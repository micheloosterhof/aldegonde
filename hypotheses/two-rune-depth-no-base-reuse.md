---
type: observation
---
# Two-Rune Words Show No Depth: the Base Essentially Never Repeats

## Status

**Status**: confirmed (characterization). Enumeration-free and independent of
`g`; excludes any base schedule with fewer than ~300 effective states.

## Claim

A 2-rune word encrypts to `( base_w(p0), base_w(g(p1)) )`. Two such words agree
at a position exactly when their bases agree at the corresponding point, so
whether the **two positions agree together** is decided by how often bases
coincide. Measured over the 465 two-rune words of the clean corpus, they do
not: agreement at position 0 carries **no** information about agreement at
position 1.

That excludes shift-like schedules directly, without enumerating keys and
without assuming anything about `g`.

## Why this discriminates

Agreement at a position means `base_w(x) = base_v(x)`, i.e. `x` is a fixed
point of `h = base_v^-1 base_w`. The fixed-point structure of the group the
base differences live in decides everything:

- **Shift-like schedules** (Vigenère, Quagmire, any conjugated shift
  `K s_k K^-1`): `h` is fixed-point-free unless the two shifts are equal. So
  two words with the same plaintext agree at **both** positions or **neither**.
  With ~29 shifts, ~1/29 of same-plaintext pairs collide completely.
- **A rich walk** (~2,928 distinct bases, DJU-BEI the single observed state
  return): distinct bases behave like unrelated permutations and the two
  positions agree independently at ~1/29 each. No excess.

`g` only selects *which* point the second position tests, never the structure,
so the test is `g`-free. It does require the base to be constant within a word,
which is established (`d5-partial-alphabet-leak.md`: the echo is flat over
position, so the base is word-locked).

## What was measured

`experiments/two_rune_depth.py`, clean corpus: 465 two-rune words, 107,880 pairs.

| | rate | count |
|---|---|---|
| agree at position 0 | 0.03447 | 3719 |
| agree at position 1 | 0.03373 | 3639 |
| agree at BOTH, observed | 0.00104 | **112** |
| agree at BOTH, if independent | 0.00116 | 125.4 |

Against a null reshuffling the second runes across words (preserving both
marginals exactly, 20,000 draws): **z = −1.24, p = 0.91**. There is no excess;
if anything a slight deficit.

The conditional statement is the direct answer: **P(position 1 agrees |
position 0 agrees) = 0.0301** against an unconditional 0.0337. Knowing the
first rune matched tells you nothing about the second.

Position 0 agrees at 0.03447 against 1/29 = 0.03448 — flat to four figures.

## The exclusion

The argument needs no estimate of how many 2-rune words are THE. Any repeated
2-rune plaintext collides fully when the shifts match, and the class is
function-word dominated: the top-8 cover 69% of register tokens (README
constraint 3). Given eight words summing to 0.69, `sum p^2` is minimised when
they are equal, so the same-plaintext pair rate is **at least 0.0595** — a
rigorous lower bound, ≥ 6,420 of the 107,880 pairs.

With 29 shifts, ≥ 221 of those must collide at both positions, predicting
≥ 347 double agreements against the **112 observed** — excluded at **22 sigma**.

Inverted into a constraint: at most ~22 pairs can share a base at 2 sigma, so
the same-plaintext collision rate is below 3.4e-3 against the 0.034 a 29-shift
schedule requires. **The base must take at least ~300 effective values.** A
29-state shift schedule is a factor of ten short.

## Relation to what was already known

This agrees with `mixed-alphabet-vigenere.md` (keyword-Quagmire excluded by
313M-key enumeration) and with the "no small key exists" diagonal-floor
argument, but it reaches the conclusion from a different statistic and along a
much shorter path:

- **Enumeration-free** — no key search, one census of 465 words.
- **Register-light** — it needs only that 2-rune words are function-word
  dominated, which is near-universal in English, not the Pride & Prejudice
  diagonal bands whose representativeness is the enumeration's one open
  scope caveat.
- **`g`-free** — unaffected by the order-5 question entirely.

It does not exclude the walk; ~2,928 distinct bases sit comfortably inside the
bound. Its force is against every small-state schedule at once.

## Scripts

- `experiments/two_rune_depth.py`

## Related

- `mixed-alphabet-vigenere.md` — the keyword-Quagmire enumeration this
  corroborates from outside.
- `collision-hunt-single-constraint.md` — the repeat census, which starts at
  length 3 and so never examined the 2-rune class.
- `length-clocked-walk.md` — the model whose word-locked base the argument
  assumes.

## Verdict

The 2-rune words carry no depth. Position-0 agreement predicts nothing about
position 1, where a shared-base schedule would force the two together. Any
scheme whose base takes fewer than ~300 effective values is excluded at 22
sigma, without enumerating a single key.
