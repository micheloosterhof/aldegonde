---
type: observation
---
# Nothing Else in the Book Suppresses Adjacent Repeats

## Status

**Status**: confirmed. It turns the doublet deficit from a curiosity into a positive
constraint, measured against the author's own plaintext and his own ciphertexts rather
than against a theoretical 1/29.

## The question the deficit has never been asked

The body has 86 adjacent repeats where 447 are expected — a rate of 0.0066 against
1/29 = 0.0345, **81% suppression, z = −17.4**. `doublet-deficit-is-global.md` shows it is
uniform across word boundaries, so it constrains neither `g` nor `σ`.

But three quite different things could produce a low doublet rate, and only one is
interesting:

- **the language** — runeglish collapses TH, EA, NG and OE, so many of the doubled
  letters English is full of do not survive as doubled runes;
- **a weak cipher** — a monoalphabetic substitution maps a doublet to a doublet and
  inherits the plaintext rate exactly;
- **the cipher** — a rule that inspects its own output and refuses to repeat.

The book supplies all three as controls, in the author's own hand.

## The measurement

`experiments/doublets_in_the_authors_ciphers.py`

| text | runes | doublets | d1 rate | z | IoC | seam |
|---|---|---|---|---|---|---|
| chance | | | 0.0345 | 0.00 | 1.000 | 0.0345 |
| the author's plaintext | 1,963 | 47 | 0.0240 | −2.56 | 1.788 | 0.0309 |
| his monoalphabetic ciphertext | 962 | 19 | 0.0198 | −2.50 | 1.579 | 0.0236 |
| **his interrupted Vigenère** | 834 | 25 | **0.0300** | **−0.71** | 1.107 | 0.0284 |
| his prime running key | 85 | 2 | 0.0238 | −0.54 | 0.942 | 0.0417 |
| **the body** | 12,956 | 86 | **0.0066** | **−17.37** | 1.000 | **0.0079** |

**The Vigenère is the control that matters.** Its key changes between adjacent positions,
so a plaintext doublet stops being a ciphertext doublet and the rate returns to chance —
and it lands there, at z = −0.71. The language effect is real (−2.56 in the plaintext)
and it is an order of magnitude too small to matter.

The monoalphabetic pages behave exactly as they must, inheriting the plaintext rate.

**The body is unlike anything else in the book**, at both positions: 0.0066 inside a
block and 0.0079 at a block seam, against 0.0300 and 0.0284 for the author's own
keystream cipher.

## What it establishes

This is a positive constraint, which is rarer here than the negatives.

- The deficit is **not** the language: the language accounts for 0.0240, not 0.0066.
- It is **not** an artifact of any cipher the author is known to use: his own keystream
  cipher returns the rate to chance.
- So something in the body's cipher **inspects its own output and refuses to repeat.**
  That is the preventer family — `doublet-dodge-walk.md`, `probabilistic-preventer.md`,
  `substitution-preventer` — and this is the first evidence that the feature they model
  is a property of the cipher rather than a modelling convenience.

It also prices the strength: 81% suppression, not 100%. A rule that never repeats would
give zero doublets; 86 survive. Whatever the rule is, it fails about one time in five —
which is the quantity `substitution-preventer` fits with τ's fixed points and
`probabilistic-preventer` with φ.

## Falsification

- If a sixth solved page turns out to show a large doublet deficit in its ciphertext,
  the "no cipher of his does this" claim weakens. The Vigenère sample is 834 runes and
  its z of −0.71 has room for a real deficit of a few percent, not for one of 81%.
- If the body's plaintext register has a far lower doublet rate than the front matter's,
  the language explanation revives. It would have to be four times lower, against a
  measured 0.0240 that is itself only 1.4× below chance.
- The prime-running-key row is 85 runes and settles nothing on its own; it is listed for
  completeness.

## Scripts

- `experiments/doublets_in_the_authors_ciphers.py`

## Related

- `doublet-deficit-is-global.md` — that the deficit is uniform, which this complements
  with where it does *not* appear.
- `doublet-dodge-walk.md`, `substitution-preventer` — the mechanisms this justifies
  modelling at all.
- `the-body-passes-nothing-through.md` — the other place the body departs from the
  author's own conventions.
