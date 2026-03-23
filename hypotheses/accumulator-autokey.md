# Hypothesis: Accumulator Autokey (Running Ciphertext Sum)

## Claim

The key at each position is the running cumulative sum of all prior
ciphertext runes, not just the immediately preceding rune.

## Status

**Status**: unresolved

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

## Scripts

Should be trivial to test — 29 primers, cumulative sum, compute IOC.

## Verdict

Unresolved. This is a simple model that survives the split test because
the running sum introduces position-dependent state. Needs testing.
