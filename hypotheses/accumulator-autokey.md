# Hypothesis: Accumulator Autokey (Running Ciphertext Sum)

## Claim

The key at each position is the running cumulative sum of all prior
ciphertext runes, not just the immediately preceding rune.

## Status

**Status**: disproved

## Mechanism

S[i] = (S[i-1] + C[i-1]) mod 29 (running sum of all prior ciphertext)
C[i] = (S[i] - P[i]) mod 29 (Beaufort-style)
Decrypt: P[i] = (S[i] - C[i]) mod 29

S is fully determined from the ciphertext and the primer S[0].

## Evidence for

- The running sum is a many-to-one function of the ciphertext history: many
  different ciphertext histories produce the same sum. This makes the split
  test fail — grouping by C[i-1] doesn't fix S[i], because S depends on the
  entire prior history.
- No Friedman period (aperiodic state evolution)
- Flat distribution from Beaufort-like operation

## Evidence against

- We tested `beaufort_mult_running_ct` in the model tester (with the running
  sum as a multiplicative factor) and got random IOC. But that used the sum
  as a MULTIPLIER, not as the key itself. The pure additive version needs
  testing.
- **Wait**: S[i] = (S[i-1] + C[i-1]) mod 29, so S[i] = (S[0] + sum(C[0..i-1])) mod 29.
  P[i] = (S[i] - C[i]) mod 29 = (S[0] + sum(C[0..i-1]) - C[i]) mod 29.
  For fixed S[0], this is a deterministic function of the ciphertext. Grouping
  by C[i-1]: S[i] = S[i-1] + C[i-1], so S[i] varies with S[i-1]. BUT S[i-1]
  depends on the full history. Different positions with the same C[i-1] have
  different S[i-1], so different S[i]. The mapping P[i] = S[i] - C[i] varies
  per position → IOC within each C[i-1] group is washed out. ✓ Survives split.

## Predictions

Decryption is deterministic given the primer S[0] (29 values to try).
If correct, one of the 29 primers should produce English-like IOC.

## Test result (July 2026)

`experiments/accumulator_autokey_test.py` decrypts every clean section
(0-9) with all 29 primers in both the Beaufort form (P = S - C) and the
Vigenere form (P = C - S). The primer only shifts the recovered plaintext
by a constant, so IOC is primer-invariant; the two forms are negations of
each other and give identical IOC. Max per-section normalized IOC: 1.032
(random ~1.0, English runeglish ~1.6-1.8). No primer produces anything
but random text.

Independently, the mechanism cannot produce the doublet suppression:
C[i] = C[i-1] iff P[i] - P[i-1] = C[i-1] mod 29, which for near-uniform
ciphertext holds with probability ~1/29 regardless of the plaintext — a
~3.45% doublet rate, not the observed 0.66%. The running sum is output
feedback, but without an avoidance rule feedback alone does not suppress
doublets.

## Scripts

- `experiments/accumulator_autokey_test.py` — exhaustive primer test.

## Verdict

Disproved. Exhaustive decryption over all 29 primers yields random IOC in
every section, and the mechanism has no way to produce the observed
doublet suppression.
