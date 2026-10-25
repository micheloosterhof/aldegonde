---
type: hypothesis
---
# Hypothesis: The Body Is the Composition of Every Device the Solved Pages Teach

## Claim

The solved pages are a syllabus. Each introduces one component: a mixed (Atbash-like)
alphabet on page 0; a keyword Vigenère with a key-skip interrupter on the Vigenère pages;
a running numeric key from the primes on page 71, with the totient variants nearby. The
body is their product: a **mixed alphabet** through which a **5-rune keyword restarting
at every word** and a **running numeric key from the prime or totient family** are added,
with the author's **key-skip** generalised from "at plaintext F" to "when the output would
repeat". Every piece is one the author has shown he uses.

## Status

**Status**: unresolved. Proposed 2026-10-25. The numeric-key component sits in a gap two
files leave explicitly: `running-key-math-sequence.md` ("this linearizes only ADDITIVE
keystreams over the standard rune order. A mixed alphabet in the loop does not") and
`no-integer-keystream-anywhere.md` ("A mixed alphabet inside the loop does not linearise
under subtraction and is untouched"). `docs/lp_structure_findings.md` fingerprinted a
Quagmire running key once as a generic model; no numeric sequence was ever searched
through a mixed alphabet.

## Mechanism

With `K` a mixed alphabet, `W` a 5-rune keyword, and `π`, `τ` numeric streams reduced
mod 29:

    c_j = K( p_j + W[j mod 5] + π_w + τ_j )        skip a step when c_j == c_{j-1}

- `W[j mod 5]` restarting at each separator gives the within-word lag-5 echo anchored to
  the separators (D1, D2) and chance at lags 1–4.
- `π_w` per word and `τ_j` per letter supply the alphabets. A1 needs at least 949:
  one 29-valued stream and five phases give 145 and are excluded by the flat IoC, so the
  model needs two independent streams, 29 × 29 × 5 = 4,205.
- The skip is the dodge, which the author already operated by hand as the interrupter;
  here it is output-triggered rather than plaintext-triggered (B6 excludes the
  pass-through form, not a skip that still enciphers the rune).
- `K` makes every ledger row that excluded "additive over the standard order" silent.

## Evidence for

- The author demonstrably used each component: mixed alphabet, keyword, interrupter,
  prime running key, totient arithmetic.
- The body's additive-keystream exclusions (B1 to B5) all state the standard-order scope.
- The 5-rune keyword is the one carrier of the lag-5 echo that needs no permutation of
  order 5 to be constructed.

## Evidence against

- The seam and within-word doublet rates still need the skip; nothing here suppresses
  repeats on its own (`no-natural-relation-suppresses-doublets.md`).
- The quagmire family's standing miss, d6w on 31 coincidences (`quagmire-odometer.md`),
  may carry over, since the within-word relation is again a schedule of shifts through
  one mixed alphabet.
- Two numeric streams is one more than the author used on any solved page.

## Predictions

1. For the true `K`, `W`, `π`, `τ` and origin, the stream `K⁻¹(c_j) − W − π − τ` has the
   register's nIoC of about 1.78 after undoing the skips; for every wrong sequence it is
   flat. This is a Quagmire-with-running-numeric-key solver: hill-climb `K` on IoC with
   the 24 sequences × origins × offsets of `sequence_key_sweep.py` as the numeric part.
   Plant a key first; the climb must recover it.
2. The DJU-BEI return (words 1477 and 2926, three runes each, identical with their
   successors) requires `π_1477 ≡ π_2926` and `π_1478 ≡ π_2927` mod 29 for the per-word
   stream, which filters origins before any climb.

## Scripts

- To write: the solver above, on `sequence_key_sweep.py`'s generators and
  `quagmire_runner.py`'s skip model.

## Related

- `running-key-math-sequence.md`, `no-integer-keystream-anywhere.md` — the scope gap.
- `mixed-alphabet-vigenere.md`, `quagmire-dodge.md`, `quagmire-odometer.md` — the
  keyword-and-skip half, already studied.
- `the-body-passes-nothing-through.md` — why the skip must encipher the rune.

## Verdict

Open. One solver, with a planted control, decides it.
