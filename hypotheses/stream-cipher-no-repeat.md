---
type: hypothesis
---
# Hypothesis: Additive Stream Cipher with Ciphertext-Doublet Avoidance

## Claim

The ciphertext is produced by adding a keystream to the plaintext,
C[i] = P[i] + K[i] mod 29, where the encryption process partially avoids
emitting C[i] == C[i-1] (re-keying or nudging when a doublet would occur).

Earlier formulation — "the KEYSTREAM has no repeats, K[i] != K[i+1]" — is
**mathematically incapable of producing the observed doublet suppression**
and has been corrected (see below).

## Status

**Status**: unresolved (reformulated; keystream-only variant disproved)

## Mechanism

A ciphertext doublet requires dP[i] = -dK[i] (mod 29). Forbidding dK = 0
only blocks the channel where a plaintext doublet passes through unchanged;
all 28 nonzero dK values remain available to cancel nonzero plaintext
deltas, giving a doublet rate of about (1 - 3.2%)/28 = 3.46% — i.e. no
suppression at all. Verified by simulation
(`experiments/mechanism_fingerprint.py`): a K[i] != K[i+1] keystream yields
3.4-3.5% ciphertext doublets vs the observed 0.66%.

To suppress ciphertext doublets the encryptor must look at what it is
emitting: when P[i] + K[i] would equal C[i-1], it re-draws or modifies the
key with high probability. Equivalently, the key selection is
plaintext-aware. This is a structural requirement for ANY additive-stream
explanation of the corpus, not just this hypothesis.

The avoidance parameter is now pinned (`experiments/unit5_telex_tests.py`):
the doublet rate fits P(doublet) = (1/5) x (1/29) with NO free parameters
(86 observed vs 89.3 predicted, z = -0.36). The acceptance probability is
exactly 1/5 — a suspiciously clean design constant, and the second
independent appearance of the number 5 in the fingerprint (after the lag-5
paired-match structure). The 1/5 is realized memorylessly: doublet positions
are uniform mod 5, gaps have no mod-5 lattice, and word-position rates show
no period-5 comb — so it is a per-event probability, not a positional
"units of 5" grid (consistent with the confirmed Poisson spacing). Soft
hint: the minimum observed doublet gap is 6 where Poisson expects ~2.8 gaps
of 5 or less (p ~= 0.06). On avoidance, the replacement output is drawn
uniformly: the missing doublet mass redistributes across Hamming distances
(canonical 5-bit encoding) in proportion to chance, ruling out a
single-bit-flip nudge.

## Evidence for

- Simulated output-avoidance stream (80% re-key on would-be doublet) matches
  the base fingerprint: doublet rate ~0.70% (observed 0.66%), ~0 triplets
  (observed 0), nIoC 1.000 (observed 1.000), flat kappa at all skips.
- Flat distribution and the absence of any split-test signal are automatic
  for OTP-like keystreams.

## Evidence against

- Does not explain the lag-5 paired-match structure
  (`lag5-digraph-structure.md`): simulated avoidance streams show no d=1/d=4
  excess. Lag-5-tapped lagged-Fibonacci keystreams (taps {1,5}, {4,5}, with
  and without avoidance) also fail to produce it.
- The lag-5 matches are word-boundary-aware — both the paired and the
  isolated matches sit inside words above the boundary-permutation null
  (`experiments/lag5_word_boundary.py`, p = 0.014 / 0.018). A purely
  positional stream has no access to word structure, so whatever produces
  the lag-5 behavior sees the boundaries; this favors word-scoped state
  (the length-clocked walk family) over position-driven keystreams.
- A truly random keystream would make the cipher unsolvable, which
  contradicts Cicada's stated intent that the Liber Primus can be read;
  the keystream must be a derivable PRNG, and no candidate construction has
  been identified.

## Predictions

- Doublet positions should look content-independent and Poisson — consistent
  with `doublet-spacing-poisson.md` (confirmed).
- The ~86 surviving doublets are the ~20% acceptance leak; under re-key-once
  semantics the rate would be (1/29)^2 = 0.12%, too low, so the avoidance is
  probabilistic or rule-based rather than absolute.
- If the PRNG is identified, subtracting trial keystreams must account for
  re-key events, so naive positional subtraction will fail even with the
  right generator (same loophole as the AN END interrupts).
- The word-aligned repeated 6-gram (`repeated-phrase-dju-bei.md`) is hard to
  reconcile with a position-driven keystream: if the keystream states at the
  two locations were equal they would stay synchronized past the 7 runes
  (LFSR-style states evolve deterministically), but the match dies
  immediately. Under any keystream-only model the event is chance (p < 1e-3).

## Scripts

- `experiments/mechanism_fingerprint.py` — disproves the keystream-only
  variant, validates the output-avoidance fingerprint.

## Related

- `explicit-doublet-avoidance.md` — absolute avoidance, disproved (doublets
  exist); this hypothesis is the probabilistic version.
- `lag5-digraph-structure.md` — the structure any surviving variant must
  also explain.
- `running-key-math-sequence.md`, `running-key-text.md` — fixed keystreams
  without feedback, both disproved.

## Verdict

The original keystream-constraint formulation is disproved by direct
calculation and simulation. The corrected formulation — additive stream with
probabilistic ciphertext-doublet avoidance — was the first mechanism family
tested that matches the base fingerprint (flatness, doublet rate,
triplets); the five-block machinery, the back-reference model, and the
length-clocked-walk family have since matched it too (see
`five-block-boundary.md`, `lag5-back-reference.md`,
`length-clocked-walk.md`). It does not explain the lag-5 paired-match
structure, is disfavored by that structure's word-boundary-awareness
(a positional stream cannot see word boundaries), and offers no specific
keystream construction to attack.
