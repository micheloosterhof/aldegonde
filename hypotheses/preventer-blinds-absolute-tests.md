---
type: observation
---
# Observation: A Preventer Blinds Absolute-Position Tests and Barely Touches Relative-Distance Ones

## Feature

The solved front matter gives ciphertext with known periods and known interrupt
positions, so the cost a clock perturbation imposes on each kind of test can be measured
rather than argued. It splits the project's tools cleanly in two.

**Absolute-position tests are destroyed.** The Friedman scan assigns every rune to a
coset by its index, so a single interrupt shifts everything after it into the wrong
coset. Only the prefix before the first interrupt is usable — on chunk 1 that is 48 of
251 runes, 19%:

| chunk | interrupts | period | avgioc as transcribed | phase restored | background |
|---|---|---|---|---|---|
| 1 | 6 | 8 | 0.0420 | **0.0640** | 0.0448 |
| 2 | 3 | 8 | 0.0440 | **0.0600** | 0.0392 |
| 12 | 2 | 13 | 0.0490 | **0.0630** | 0.0356 |

A period-8 Vigenère at a 2.4% interrupt rate is invisible; restoring the phase recovers
the full plaintext-level signal.

**Relative-distance tests survive.** Kappa counts coincidences at distance `d` directly,
and a pair is broken only if an interrupt falls *between* its two members — a fraction
`1 − (1−q)^d`, which at q = 2.4% is 11% at d = 5 and 18% at d = 8:

| chunk | interrupts | period | kappa z as transcribed | phase restored | cost |
|---|---|---|---|---|---|
| 1 | 6 | 8 | +2.33 | +2.43 | 0.10 |
| 2 | 3 | 8 | +1.77 | +2.51 | 0.74 |
| 12 | 2 | 13 | +1.37 | +2.54 | 1.16 |

Kappa loses between 0.1 and 1.2 sigma where Friedman loses everything.

## Status

**Status**: confirmed (measurement) on chunks 1, 2 and 12 of
`solved-page-testbed.md`, whose periods and interrupt positions are both known.

## The rule, and which results it touches

> A test that indexes runes by **absolute position** is destroyed by one interrupt. A
> test that indexes by **relative distance** degrades by `1 − (1−q)^d`.

- `no-periodicity.md` — Friedman coset scan: **blinded**. Its conclusion survives only
  because `flat-ioc.md`'s alphabet-count bound is phase-independent.
- `kappa-spectrum.md` — kappa by skip: **robust**, losing about a sigma at these rates.
- `within-word-d5-coincidence.md` — a relative-distance channel at d = 5: **robust**,
  attenuated ~11% at q = 2.4%. This is also why the d5 echo is the signal that survives
  in the body at all.
- `flat-ioc.md` — counts alphabets rather than locating them: **unaffected**. A
  perturbation changes which alphabet is used where, never how many exist.

The practical consequence is that a negative from an absolute-position test should not
be cited against any model in the preventer family, and `quagmire-dodge.md`'s own
history is the warning: its sweep failed because the scorer assumed clock = position.

## Related

- `solved-page-testbed.md` — the known-period, known-interrupt ciphertext used here.
- `no-periodicity.md` — the negative this qualifies.
- `key-local-channel-is-empty.md` — where the preventer reading is favoured.

## Where the 1.75% comes from, and why it is now an upper bound (September 2026)

The interrupt rates used here are calibrated on the author's own device, measured on the
solved front matter. `interrupter-is-a-plaintext-rule.md` shows that device is an exact
plaintext rule -- every plaintext F is passed through literally, nothing else is -- so
its rate is the plaintext's F frequency, 0.0158, and it EMITS a rune. That makes it
visible in the unigram table, and the body refutes it: the predicted rune-F rate is
0.0497 against an observed 0.0354, z = -4.43, or 205 predicted interrupts against at
most 47 allowed.

Two consequences, pulling opposite ways.

**For emitting interrupters the reach quoted here is four times too pessimistic.** The
body's 95% ceiling is q = 0.0037, so the expected clean run is 273 runes rather than the
57 this file's tables assume. Prefix-scored searches were conservative by that factor.

**For the family this file is actually about, nothing changes.** A preventer skips a key
step while still enciphering the rune, leaves no unigram trace, and is not bounded by
that measurement at all. The rates tabulated above remain the right ones to price a
preventer with; what is excluded is only the author's own pass-through device.

