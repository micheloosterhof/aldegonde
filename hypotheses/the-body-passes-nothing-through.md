---
type: observation
---
# The Interrupt Rule Is Exactly "Plaintext F", and the Body Does Not Use It

## Status

**Status**: confirmed, both halves. The rule is now pinned over all five keyed solved
pages rather than one, and the body's exclusion is a unigram argument, so no alignment
or phase is involved.

## Half one: the rule is exact

The book has five solved pages carrying a keystream — four interrupted Vigenère and one
prime running key. Between them they have twelve interrupts.

| page | cipher | plaintext F | interrupts | every interrupt at a plaintext F |
|---|---|---|---|---|
| 1 | interrupted Vigenère | 6 | 6 | yes |
| 2 | interrupted Vigenère | 3 | 3 | yes |
| 12 | interrupted Vigenère | 2 | 2 | yes |
| 13 | interrupted Vigenère | 0 | 0 | yes |
| 71 | prime running key | 1 | 1 | yes |

**Twelve interrupts against twelve plaintext F, no exceptions, across two cipher
families.** At every one the ciphertext rune is F as well, because the rune passes
through unenciphered and the key index does not advance: `c = p = F`.

Page 13 is the useful negative: no plaintext F, no interrupts.

This is stronger than `interrupter-is-a-plaintext-rule.md` records, which establishes it
on one page. It is the author's convention, not a tendency.

## Half two: the body cannot be doing this

A rune that passes through appears in the ciphertext at its plaintext rate *plus* the
flat rate contributed by everything else, so its frequency stands clear of 1/29 by a wide
margin. The body's unigram table is flat — χ² 26.4 on 28 df.

| rune | plaintext rate | predicted if passed through | observed | z vs flat | z vs pass-through |
|---|---|---|---|---|---|
| E | 0.1263 | 0.1565 | 0.0339 | −0.38 | **−77.1** |
| O | 0.0968 | 0.1279 | 0.0354 | +0.53 | −57.1 |
| A | 0.0734 | 0.1053 | 0.0372 | +1.64 | −41.0 |
| R | 0.0688 | 0.1009 | 0.0327 | −1.12 | −43.6 |
| **F** | **0.0149** | **0.0489** | **0.0354** | **+0.53** | **−8.3** |

**F — the rune the author actually uses — misses its pass-through rate by 8.3 sigma**,
and it is the closest of all 29. The common plaintext runes miss by tens.

## What this excludes, and what it does not

**Excluded**: the body being enciphered with the author's own interrupt convention, on
any keystream whatever. The test is a frequency table, so no alignment, phase or period
is involved, and the interrupter that blinds every alignment test cannot blind it
(`spectral-bounds-dodge-interrupters`).

**Not excluded**: key-skipping in general. A rule that holds the key index while still
enciphering the rune leaves the unigram table flat and is untouched here. Nor are nulls
that are themselves enciphered.

So the body differs from every other keyed page in the book in a specific, checkable way.
Each solved page escalates the cipher — monoalphabetic, then interrupted Vigenère, then a
prime running key — and each keeps the same interrupt convention. The body drops it.

## Consequences

- Any attack on the body that assumes ciphertext F marks a skip is misconceived. The
  prefix-scoring in `sequence_key_sweep.py` and `window_sequence_sweep.py` is
  conservative rather than wrong — it tolerates interrupts it now appears there are none
  of — but nothing should be *fitted* to an F-interrupt model.
- It strengthens the case that the body's cipher is bijective at every position, which is
  what the walk family assumes and what a null- or skip-bearing cipher would not be.
- `interrupter-is-a-scribal-mark` should be read carefully: from the *ciphertext* side
  only some F are interrupts (6 of 14 on page 1), because the rest are coincidental
  encipherments to F. From the *plaintext* side the rule is complete. Both are true and
  the attacker only gets the ciphertext side.

## Falsification

- If a sixth keyed page is solved and its interrupts are not exactly its plaintext F, the
  rule is a tendency and half one weakens. Twelve for twelve is a small sample of pages,
  though not of interrupts.
- If the body's plaintext register is very unlike the front matter's — F rate far below
  0.0149 — the predicted pass-through rate drops. It would have to fall below about
  0.002, an eighth of the author's own rate, for the −8.3 sigma to close.
- The prediction assumes a passed-through rune is otherwise enciphered flat. That is what
  the body's χ² 26.4 on 28 df says it is.

## Register note

The plaintext rates above are from the sixteen-page register
(`lp_plaintext_register.corpus()`, 723 words and 2,882 runes). On the eleven-page
register this file originally used, F read 0.0158 and the miss was −8.9 sigma. Every
other row moves by a similar tenth and none of them changes sign.

## Scripts

- `experiments/nothing_passes_through.py`

## Related

- `interrupter-is-a-plaintext-rule.md` — the one-page version of half one.
- `interrupter-is-a-scribal-mark` — the ciphertext-side statement, consistent with this.
- `no-integer-keystream-anywhere.md` — the sweep whose interrupt tolerance this shows is
  belt and braces.
