# Liber Primus: Quagmire Cipher Variant Analysis

## Overview

This document analyzes various Quagmire cipher variants with autokey to determine which (if any) could produce the statistical properties observed in Liber Primus.

## Observed LP Properties

| Property | Value | Interpretation |
|----------|-------|----------------|
| IoC (normalized) | 0.9998 | Essentially random |
| Character frequency | Near-uniform | Chi-squared = 25.9 |
| Bigram distribution | Near-uniform (except doublets) | See below |
| Doublet frequency | 86 (vs ~450 expected) | Anomalously low |
| Repeats (4+ chars) | 142 | More than random expectation |

### Critical Bigram Observation

When grouping bigrams by `(pos[first] - pos[second]) mod 29`:
- **Doublets (diff=0)**: 86 occurrences
- **All other differences**: 404-510 occurrences (nearly uniform)

For a cipher where the same bigram always decrypts to the same plaintext letter at position 2, we'd expect non-uniform distribution matching English letter frequencies (~65:1 ratio). LP shows ~1.2:1 ratio.

---

## Cipher Variant Definitions

### Notation
- `P[i]` = plaintext character at position i
- `C[i]` = ciphertext character at position i
- `K[i]` = key character at position i
- `pos_p(x)` = position of x in plaintext alphabet
- `pos_c(x)` = position of x in cipher alphabet
- `n` = alphabet size (29 for runes)

---

## 1. Quagmire III Ciphertext Autokey (Original Hypothesis)

### Algorithm
```
Plaintext alphabet:  Standard (FUTHORCGWHNIJEOPXSTBEMLNGOEDAY AE Y IA EA)
Cipher alphabet:     Mixed (keyword-based permutation)
Key generation:      K[0] = primer, K[i] = C[i-1] for i > 0

Encryption (Beaufort): C[i] = cipher_alphabet[(pos_c(K[i]) - pos_p(P[i])) mod n]
Decryption:            P[i] = plain_alphabet[(pos_c(K[i]) - pos_c(C[i])) mod n]
```

### Bigram Property
For bigram C[i-1]C[i]:
```
P[i] = plain_alphabet[(pos_c(C[i-1]) - pos_c(C[i])) mod n]
```

**The plaintext at position i depends ONLY on the bigram, not on position.**

### Statistical Prediction
- Same bigram → same plaintext letter at position 2
- Bigram frequencies should mirror plaintext letter frequencies
- Expected: highly non-uniform bigram distribution

### Match with LP?
**NO** - LP has nearly uniform bigram distribution (except doublets)

---

## 2. Quagmire IV Ciphertext Autokey

### Algorithm
```
Plaintext alphabet:  Mixed (keyword 1)
Cipher alphabet:     Mixed (keyword 2, different from keyword 1)
Key generation:      K[0] = primer, K[i] = C[i-1] for i > 0

Encryption (Beaufort): C[i] = cipher_alphabet[(pos_c(K[i]) - pos_p(P[i])) mod n]
Decryption:            P[i] = plain_alphabet[(pos_c(K[i]) - pos_c(C[i])) mod n]
```

### Bigram Property
For bigram C[i-1]C[i]:
```
P[i] = plain_alphabet[(pos_c(C[i-1]) - pos_c(C[i])) mod n]
```

**Same as Quagmire III** - plaintext at position i depends only on the bigram.

### Statistical Prediction
- Same bigram → same plaintext letter at position 2
- Non-uniform bigram distribution expected

### Match with LP?
**NO** - Same problem as Quagmire III

---

## 3. Quagmire II Ciphertext Autokey

### Algorithm
```
Plaintext alphabet:  Mixed (keyword-based)
Cipher alphabet:     Standard
Key generation:      K[0] = primer, K[i] = C[i-1] for i > 0

Encryption (Beaufort): C[i] = standard[(pos_std(K[i]) - pos_p(P[i])) mod n]
Decryption:            P[i] = plain_alphabet[(pos_std(K[i]) - pos_std(C[i])) mod n]
```

### Bigram Property
For bigram C[i-1]C[i]:
```
P[i] = plain_alphabet[(pos_std(C[i-1]) - pos_std(C[i])) mod n]
```

**Still depends only on the bigram** - the difference is computed in standard alphabet positions.

### Statistical Prediction
- Same bigram → same plaintext letter at position 2
- Non-uniform bigram distribution expected

### Match with LP?
**NO** - Same fundamental problem

---

## 4. Quagmire I Ciphertext Autokey

### Algorithm
```
Plaintext alphabet:  Standard
Cipher alphabet:     Mixed (keyword-based)
Key generation:      K[0] = primer, K[i] = C[i-1] for i > 0

Encryption (Beaufort): C[i] = cipher_alphabet[(pos_c(K[i]) - pos_std(P[i])) mod n]
Decryption:            P[i] = standard[(pos_c(K[i]) - pos_c(C[i])) mod n]
```

### Bigram Property
For bigram C[i-1]C[i]:
```
P[i] = standard[(pos_c(C[i-1]) - pos_c(C[i])) mod n]
```

**Still depends only on the bigram.**

### Statistical Prediction
- Same bigram → same plaintext letter at position 2
- Non-uniform bigram distribution expected

### Match with LP?
**NO** - Same fundamental problem

---

## 5. MASC followed by Autokey (Substitution then Autokey)

### Algorithm
```
Step 1 - MASC:     M[i] = substitute(P[i])  using fixed substitution table
Step 2 - Autokey:  C[i] = (M[i] + K[i]) mod n, where K[i] = C[i-1]

Combined:          C[i] = (substitute(P[i]) + C[i-1]) mod n
```

### Bigram Property
For bigram C[i-1]C[i]:
```
C[i] = (M[i] + C[i-1]) mod n
M[i] = (C[i] - C[i-1]) mod n
P[i] = inverse_substitute(M[i])
```

**The INTERMEDIATE value M[i] depends only on the bigram.**
Since MASC is a fixed bijection, **P[i] also depends only on the bigram.**

### Statistical Prediction
- Same bigram → same plaintext letter at position 2
- Non-uniform bigram distribution expected

### Match with LP?
**NO** - Same fundamental problem

---

## 6. Autokey followed by MASC (Autokey then Substitution)

### Algorithm
```
Step 1 - Autokey:  A[i] = (P[i] + K[i]) mod n, where K[i] = A[i-1] or P[i-1]
Step 2 - MASC:     C[i] = substitute(A[i])

For ciphertext autokey on the INNER layer:
     A[i] = (P[i] + A[i-1]) mod n
     C[i] = substitute(A[i])
```

### Bigram Property
For bigram C[i-1]C[i]:
```
A[i-1] = inverse_substitute(C[i-1])
A[i] = inverse_substitute(C[i])
P[i] = (A[i] - A[i-1]) mod n
```

**P[i] depends on inverse_substitute(C[i-1]) and inverse_substitute(C[i]).**
Since the substitution is fixed, **P[i] still depends only on the bigram C[i-1]C[i].**

### Statistical Prediction
- Same bigram → same plaintext letter at position 2
- Non-uniform bigram distribution expected

### Match with LP?
**NO** - Same fundamental problem

---

## PLAINTEXT AUTOKEY VARIANTS

All the above used ciphertext autokey (K[i] = C[i-1]). Now we analyze plaintext autokey variants where K[i] = P[i-1].

**Key Insight for All Plaintext Autokey:**
- K[i] = P[i-1] (previous plaintext character)
- To decrypt C[i], we need P[i-1]
- To get P[i-1], we need to have decrypted C[i-1] using P[i-2]
- This creates a CHAIN dependency from position 0

**Critical Difference from Ciphertext Autokey:**
- For CT autokey: P[i] = f(C[i-1], C[i]) - depends only on CT bigram
- For PT autokey: P[i] = f(P[i-1], C[i]) - depends on decrypted chain + C[i]

**Same CT bigram at different positions will generally decrypt to DIFFERENT plaintext!**

---

## 7. Quagmire I Plaintext Autokey

### Algorithm
```
Plaintext alphabet:  Standard
Cipher alphabet:     Mixed (keyword-based)
Key generation:      K[0] = primer, K[i] = P[i-1] for i > 0

Encryption (Beaufort): C[i] = cipher_alphabet[(pos_c(K[i]) - pos_std(P[i])) mod n]
                      C[i] = cipher_alphabet[(pos_c(P[i-1]) - pos_std(P[i])) mod n]

Decryption:            P[i] = standard[(pos_c(P[i-1]) - pos_c(C[i])) mod n]
```

### Bigram Property
For bigram C[i-1]C[i] at position i:
```
P[i] = standard[(pos_c(P[i-1]) - pos_c(C[i])) mod n]
```
P[i] depends on P[i-1], which depends on the entire decryption chain from start.

**Same bigram at different positions → generally different P[i]**

### Statistical Prediction
- Ciphertext bigram distribution NOT tied to single PT letter frequency
- Bigrams could be more uniformly distributed
- IoC: Ciphertext encodes P[i-1] - P[i] differences; English differences are more uniform than letters but not random

### Match with LP?
**PARTIAL** - Could explain uniform bigrams. IoC analysis needed.

---

## 8. Quagmire II Plaintext Autokey

### Algorithm
```
Plaintext alphabet:  Mixed (keyword-based)
Cipher alphabet:     Standard
Key generation:      K[0] = primer, K[i] = P[i-1] for i > 0

Encryption (Beaufort): C[i] = standard[(pos_std(K[i]) - pos_p(P[i])) mod n]
                      C[i] = standard[(pos_std(P[i-1]) - pos_p(P[i])) mod n]

Decryption:            P[i] = plain_alphabet[(pos_std(P[i-1]) - pos_std(C[i])) mod n]
```

### Bigram Property
```
P[i] = plain_alphabet[(pos_std(P[i-1]) - pos_std(C[i])) mod n]
```

P[i] depends on P[i-1] (chain dependency).

**Same bigram at different positions → generally different P[i]**

### Statistical Prediction
- Uniform bigrams possible
- IoC depends on plaintext difference distribution

### Match with LP?
**PARTIAL** - Could explain uniform bigrams.

---

## 9. Quagmire III Plaintext Autokey

### Algorithm
```
Plaintext alphabet:  Standard
Cipher alphabet:     Mixed (same keyword, shifted)
Key generation:      K[0] = primer, K[i] = P[i-1] for i > 0

Encryption (Beaufort): C[i] = cipher_alphabet[(pos_c(P[i-1]) - pos_std(P[i])) mod n]

Decryption:            P[i] = standard[(pos_c(P[i-1]) - pos_c(C[i])) mod n]
```

### Bigram Property
```
P[i] = standard[(pos_c(P[i-1]) - pos_c(C[i])) mod n]
```

Chain dependency on P[i-1].

**Same bigram at different positions → generally different P[i]**

### Statistical Prediction
- Uniform bigrams possible
- The encryption C[i] depends on pos_c(P[i-1]) - pos_std(P[i])
- This is a "mixed" difference between cipher and standard alphabet positions

### Match with LP?
**PARTIAL** - Could explain uniform bigrams.

---

## 10. Quagmire IV Plaintext Autokey

### Algorithm
```
Plaintext alphabet:  Mixed (keyword 1)
Cipher alphabet:     Mixed (keyword 2)
Key generation:      K[0] = primer, K[i] = P[i-1] for i > 0

Encryption (Beaufort): C[i] = cipher_alphabet[(pos_c(P[i-1]) - pos_p(P[i])) mod n]

Decryption:            P[i] = plain_alphabet[(pos_c(P[i-1]) - pos_c(C[i])) mod n]
```

### Bigram Property
Chain dependency through P[i-1].

**Same bigram at different positions → generally different P[i]**

### Statistical Prediction
- Uniform bigrams possible
- Two independent mixed alphabets add complexity

### Match with LP?
**PARTIAL** - Could explain uniform bigrams.

---

## 11. MASC followed by Plaintext Autokey

### Algorithm
```
Step 1 - MASC:     M[i] = substitute(P[i])
Step 2 - PT Autokey: C[i] = (M[i] + M[i-1]) mod n  [where key = previous substituted value]

Combined: C[i] = (substitute(P[i]) + substitute(P[i-1])) mod n
```

### Bigram Property
For bigram C[i-1]C[i]:
```
C[i] = (M[i] + M[i-1]) mod n
C[i-1] = (M[i-1] + M[i-2]) mod n

To find M[i], we need M[i-1], which requires the chain.
```

**Chain dependency through M values.**

### Statistical Prediction
- Uniform bigrams possible
- MASC preserves frequency, then autokey spreads it

### Match with LP?
**PARTIAL** - Could explain uniform bigrams.

---

## 12. Plaintext Autokey followed by MASC

### Algorithm
```
Step 1 - PT Autokey: A[i] = (P[i] + P[i-1]) mod n
Step 2 - MASC:       C[i] = substitute(A[i])

Combined: C[i] = substitute((P[i] + P[i-1]) mod n)
```

### Bigram Property
```
A[i] = inverse_substitute(C[i])
P[i] = (A[i] - P[i-1]) mod n
```

Requires P[i-1] - chain dependency.

**Same bigram at different positions → generally different P[i]**

### Statistical Prediction
- The autokey output A[i] = P[i] + P[i-1] depends on plaintext bigrams
- MASC scrambles but preserves frequency
- Ciphertext bigram distribution depends on plaintext bigram sums

### Match with LP?
**PARTIAL** - Could explain uniform bigrams. Needs further analysis.

---

## Plaintext Autokey IoC Analysis

For plaintext autokey variants, the ciphertext character depends on:
- Beaufort: C ∝ P[i-1] - P[i] (difference of consecutive PT letters)
- Vigenere: C ∝ P[i-1] + P[i] (sum of consecutive PT letters)

**Distribution of P[i-1] ± P[i] for English:**

In English text:
- Individual letters: highly non-uniform (E≈13%, X≈0.2%)
- Letter DIFFERENCES: more uniform but not random
- Letter SUMS: more uniform but not random

The resulting ciphertext IoC should be:
- Lower than plaintext IoC (more uniform)
- But likely still above 1.0 (not perfectly random)

**LP has IoC ≈ 1.0 (essentially random)** - this suggests:
- Either plaintext autokey with very specific plaintext
- Or a different cipher entirely
- Or additional processing (transposition, multiple stages)

---

## 13. Running Key Cipher

### Algorithm
```
Key is a long text (book, etc.), not derived from plaintext or ciphertext
C[i] = (P[i] + K[i]) mod n, where K[i] comes from key text
```

### Bigram Property
```
P[i] = (C[i] - K[i]) mod n
```

The plaintext depends on both ciphertext AND the running key position.
**Same bigram at different positions → different plaintext.**

### Statistical Prediction
- Uniform-looking ciphertext (IoC ≈ 1.0) ✓
- Uniform bigram distribution ✓
- No special doublet behavior (unless key has structure)

### Match with LP?
**PARTIAL** - Matches uniform distribution, but doesn't explain doublet anomaly

---

## Summary Table

### Ciphertext Autokey Variants (K[i] = C[i-1])

| Cipher Variant | Same Bigram → Same PT? | Bigram Uniform? | Matches LP? |
|---------------|------------------------|-----------------|-------------|
| Quagmire I CT autokey | Yes | No (expect non-uniform) | **NO** |
| Quagmire II CT autokey | Yes | No | **NO** |
| Quagmire III CT autokey | Yes | No | **NO** |
| Quagmire IV CT autokey | Yes | No | **NO** |
| MASC → CT Autokey | Yes | No | **NO** |
| CT Autokey → MASC | Yes | No | **NO** |

### Plaintext Autokey Variants (K[i] = P[i-1])

| Cipher Variant | Same Bigram → Same PT? | Bigram Uniform? | IoC ≈ 1.0? | Matches LP? |
|---------------|------------------------|-----------------|------------|-------------|
| Quagmire I PT autokey | No (chain) | Possibly | Unlikely | **PARTIAL** |
| Quagmire II PT autokey | No (chain) | Possibly | Unlikely | **PARTIAL** |
| Quagmire III PT autokey | No (chain) | Possibly | Unlikely | **PARTIAL** |
| Quagmire IV PT autokey | No (chain) | Possibly | Unlikely | **PARTIAL** |
| MASC → PT Autokey | No (chain) | Possibly | Unlikely | **PARTIAL** |
| PT Autokey → MASC | No (chain) | Possibly | Unlikely | **PARTIAL** |

### Other Ciphers

| Cipher Variant | Same Bigram → Same PT? | Bigram Uniform? | IoC ≈ 1.0? | Matches LP? |
|---------------|------------------------|-----------------|------------|-------------|
| Running Key | No (position-dependent) | Yes | Yes | **PARTIAL** |

---

## Key Insight

**Any cipher where the same ciphertext bigram always produces the same plaintext letter at position 2 will show non-uniform bigram distribution when encrypting English text.**

This rules out:
- All Quagmire variants with ciphertext autokey
- MASC combined with autokey (in either order)

Ciphers that could produce uniform bigrams:
- Plaintext autokey variants
- Running key cipher
- Polyalphabetic ciphers with long period
- More complex constructions

---

## The Doublet Anomaly

### Quantitative Analysis

LP shows 86 doublets vs 446 expected (for uniform distribution):
- **Suppression factor: 5.2x**
- Chi-squared: 290.4 (extremely significant)
- Every single rune shows fewer doublets than expected
- ᛒ (B) has ZERO doublets out of 445 occurrences

### Distribution Statistics

| Metric | Observed | Expected (random) |
|--------|----------|-------------------|
| Total doublets | 86 | 446 |
| Mean gap between doublets | 150.8 | 28.8 |
| Min gap | 6 | ~1 |
| Max gap | 712 | ~100 |

### Spatial Distribution

Doublets are distributed across all sections of the text, not clustered:
- Section with fewest doublets: 3 (positions 2590-3885)
- Section with most doublets: 13 (positions 5180-6475 and 7770-9065)
- No obvious pattern or clustering

### Possible Explanations

The low doublet count is unexplained by:
- Random text (would have ~450 doublets)
- Running key cipher (no special doublet behavior)
- Most standard ciphers

Potential explanations:
1. **Intentional avoidance** - author manually eliminated doublets
2. **Cipher with doublet property** - cipher specifically suppresses doublets
3. **Transposition component** - shuffling breaks up consecutive pairs
4. **Underlying plaintext property** - source text avoids doublets
5. **Constrained encoding** - encoding rules prevent doublets

### Cipher Implications

For Quagmire ciphertext autokey:
- Doublet CC decrypts to: P = alphabet position 0 (for Beaufort mode)
- 86 doublets → 86 positions decrypt to position 0 rune
- Expected if this is English: position 0 would need to be ~0.6% of text
- This is roughly consistent with a rare digraph rune (EA, IA, OE, AE)

For plaintext autokey:
- Doublet behavior depends on the plaintext sequence
- Low doublets could indicate plaintext avoids patterns where P[i-1] encrypts P[i] to same value

---

## NEW HYPOTHESIS: Autokey with Multiplication

### Cipher Formula

```
C[i] = C[i-1] - P[i] * M[i]  mod 29
M[i] = (i % 28) + 1
```

This is **Beaufort ciphertext autokey with position-based multiplication**.

### Decryption

```
P[i] = (C[i-1] - C[i]) * M[i]^(-1)  mod 29
```

Where M[i]^(-1) is the modular multiplicative inverse of M[i] mod 29.

### Why This Works

1. **IoC ≈ 1.0**: The multiplication by varying M[i] scrambles frequencies
2. **Uniform bigrams**: Same CT bigram at different positions decrypts differently
   - P[i] = (C[i-1] - C[i]) * M[i]^(-1)
   - Different positions have different M[i], so different P[i]
3. **Doublet suppression**: For doublet C[i] = C[i+1]:
   - C[i-1] - P[i]*M[i] = C[i] - P[i+1]*M[i+1]
   - Simplifies to: P[i+1] * M[i+1] ≡ 0 mod 29
   - Since M[i+1] ≠ 0: **Doublet ⟺ P[i+1] = 0**

### Statistics Comparison

| Property | This Cipher | LP Observed |
|----------|-------------|-------------|
| IoC | 0.9996 | 0.9999 |
| Bigram ratio | 1.28 | 1.26 |
| Doublet condition | P[i+1] = 0 | ~0.66% rate |

### Required Alphabet

For 86 doublets in 12956 chars (0.66% rate):
- Position 0 must be a character appearing ~0.66% in English
- Candidates: EA (~0.5%), or a mixed keyword that puts a ~0.66% char first

### Multiplier Variants Tested

| Multiplier M[i] | Ratio | IoC | Invertible |
|----------------|-------|-----|------------|
| (i % 28) + 1 | 1.28 | 0.9996 | Yes |
| 2^i mod 29 | 1.08 | 1.0040 | Yes |
| (CT[i-1] % 28) + 1 | 3.30 | 1.0658 | Yes |
| (PT[i-1] % 28) + 1 | 8.33 | 0.9981 | Yes |

The position-based `(i % 28) + 1` matches LP best.

---

## Recommendations for Further Analysis

1. **Test this cipher on LP** - try decrypting with various mixed alphabets
2. **Analyze trigrams and longer n-grams** - may reveal additional structure
3. **Consider multi-stage encryption** - combinations not analyzed here
4. **Search for the keyword** - that produces a ~0.66% char at position 0

---

## Files

- `quagmire_repeat_attack.py` - Hill climber for Q3 ciphertext autokey
- `quagmire_az_hillclimber.py` - A-Z alphabet test version
- `quagmire_az_analysis.py` - Statistical analysis tools

## Date

Analysis performed: December 2024
