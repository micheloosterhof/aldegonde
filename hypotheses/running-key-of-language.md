---
type: disproof
---
# Disproof: The Keystream Is Not Made of Language

## Hypothesis

The body is enciphered against a running key drawn from a text — a book, another
section of the LP, scripture — used once and never repeated. `no-running-key-depth.md`
excludes every *repeating* key by finding no depth, and states its own gap explicitly:
a non-repeating key as long as the text leaves no depth to find. It closes that gap
only for keys that are "statistically uniform". A book used once is not uniform.

## The test

Write an additive keystream as c = p + k mod 29 with k independent of p. In Fourier
coordinates, with P^(j) = Σ_x P(x)·ω^(jx) and ω = exp(2πi/29),

    C^(j) = P^(j)·K^(j)        so        IoC_c = 1 + Σ_(j≠0) |P^(j)|² |K^(j)|²

normalising uniform to 1. Multiplying by n gives the unigram chi², which is what
`flat-ioc.md` already reports for the body.

Every term is a **product**. The keystream can only flatten the ciphertext at a
frequency where the plaintext has mass by being flat there itself. No alignment, no
phase, no period: the statistic is a frequency table.

## Result

The LP's own plaintext (`lp-plaintext-register.md`, 1,963 runes) has chi² 1,574 on
28 df, with its mass concentrated at six frequencies:

| j | 4 | 25 | 19 | 10 | 2 | 27 |
|---|---|---|---|---|---|---|
| \|P^(j)\|² | 0.114 | 0.114 | 0.080 | 0.080 | 0.078 | 0.078 |

A key with the same spectrum predicts a ciphertext chi² of **743**. The body's is
**26.4**, against a null of 28 ± 7.5. The prediction is out by a factor of 28, about
90 σ.

| | chi² on 28 df |
|---|---|
| predicted, text key | 743 |
| simulated, text plaintext + text key | 1,043 |
| simulated, text plaintext + uniform key | 26.6 |
| **observed body** | **26.4** |

The simulated text-on-text control overshoots the independence prediction (1,043 vs
743) because the two streams are the same corpus at an offset and so are not quite
independent. Both are two orders of magnitude from what the body shows.

## Per-frequency cap on *any* additive keystream

The same identity, inverted, caps the keystream at every frequency (95% one-sided):

| j | \|P^(j)\|² | \|K^(j)\|² ≤ |
|---|---|---|
| 4, 25 | 0.1140 | 0.0020 |
| 19, 10 | 0.0801 | 0.0021 |
| 2, 27 | 0.0781 | 0.0027 |
| 14, 15 | 0.0325 | 0.0058 |

The cap binds only where the plaintext has mass; at frequencies the plaintext ignores,
the keystream is unconstrained. That is the honest shape of the result — it is not a
general flatness requirement, it is a requirement to avoid the plaintext's six
frequencies.

## What passes, and a second finding

The author's own arithmetic keystream, prime(n) − 1 mod 29, has chi² 465 — far from
uniform, because residue 0 is nearly absent among primes. But a missing residue spreads
its mass evenly across all 28 frequencies, so |K^(4)|² = 0.00130 against a cap of
0.00195. **It passes, with 33% headroom.** Arithmetic keystreams are flat in the way
that matters here; language ones are not.

Enciphering LP plaintext with that prime keystream gives chi² **43.4**, against the
body's 26.4 — the body is *flatter* than the author's own prime keystream would leave
it. At 2.3 σ that is suggestive, not decisive, and it is recorded as a weak count
against `prime-value-autokey.md` rather than a disproof.

## Scope

- **Additive keystreams only.** A per-position permutation drawn from a 2-transitive
  family is covered by the orbit theorem in `local-channel-is-exactly-coincidence.md`,
  not by this.
- **Interrupters do not blind it.** `preventer-blinds-absolute-tests.md` shows the
  author uses a device that destroys absolute-position tests. This is not one: an
  interrupt changes which key letter lands where, not which letters the key is made of.
  A pass-through interrupt adds plaintext non-uniformity and sharpens the bound.
- **The plaintext register could differ**, since the spectrum is measured on the front
  matter. To rescue a text key, the body's plaintext would need chi² near 297 on 28 df
  — a fifth of the author's own per-rune non-uniformity. That is not a register
  difference; nothing written in a language is that flat.

## Consequences

- Closes the case `no-running-key-depth.md` left open, so the running-key family is now
  excluded whether or not the key repeats.
- Any surviving additive keystream must be arithmetic, algorithmic or random — not
  copied from a text.
- Weak count against `prime-value-autokey.md` (2.3 σ).

## Scripts

- `experiments/keystream_spectrum_bound.py`

## Related

- `no-running-key-depth.md` — the depth argument whose stated gap this closes.
- `flat-ioc.md` — the 26.4 the bound is built on.
- `lp-plaintext-register.md` — the plaintext spectrum.
- `stream-cipher-no-repeat.md` — what still survives: a flat, non-repeating keystream.
