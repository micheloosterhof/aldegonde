# Cipher Algorithm Analysis: Liber Primus (Unsolved Sections)

## Statistical Signature

| Property | Observed | Expected (random) | Significance |
|---|---|---|---|
| Alphabet size | 29 (all used) | — | Complete alphabet usage |
| Distribution | Nearly perfectly uniform | 1/29 = 3.45% each | chi² p=0.55 (indistinguishable from uniform) |
| Shannon entropy | 4.857 bits | max = 4.858 bits | 99.98% of maximum |
| IOC | 0.0345 | 1/29 = 0.0345 | Exactly random |
| Doublet rate | 0.68% | 3.45% (1/29) | **5.09x suppressed** |
| Doublet kappa skip=1 | 86 | 447 expected | **17.07σ below random** |
| Kappa skip≥2 | Normal | Normal | Only skip=1 is anomalous |
| Triplets | **0** | ~15 expected | Complete absence |
| Digraphic kappa skip=1 | **0** | 15.4 expected | No adjacent bigram repeats |
| Friedman test | No period detected | — | No polyalphabetic key length signal |
| Repeated 5-grams | 6 | 7 expected | Normal |
| Word boundaries | Match English words | — | Given constraint |
| Off-diagonal bigrams | chi² p=0.23 | — | **Uniform** — no structure beyond doublet suppression |
| Delta stream Δ≠0 | Perfectly uniform | — | All 28 non-zero deltas equally likely |
| Delta-of-delta doublets | 443 vs 453 expected | — | Normal — no second-order suppression |
| Doublet spacing | Mean 147.1, geometric distribution | — | **Doublets are independent random events** (p≈0.0068) |
| Single-letter words | 324 total, nearly uniform across all 29 runes | — | NOT concentrated — cipher scrambles word-initial |
| Conditional entropy H(C[i]|C[i-1]) | 4.786 bits | log₂(28) = 4.807 | Close to perfect no-doublet Markov |
| Mutual information I(C[i];C[i-1]) | 0.070 bits | — | Small — only the doublet suppression |
| Autocorrelation lag=1 | -0.030 | — | Slightly negative (consistent with doublet avoidance) |
| Autocorrelation lag≥2 | ~0 | — | No other lag anomalies |

---

## The Central Discovery: Autokey Identity

Under **any** ciphertext autokey (both Vigenere and Beaufort variants):

- **C[i] = C[i+1]** always implies **P[i+1] = index 0 (ᚠ/F)**
- This is a mathematical identity: the second element of every doublet, when decrypted via autokey, is always the additive identity element
- All 89/89 doublets produce this result — mathematical certainty, not statistical
- The 89 doublets are therefore not errors — they are positions where a specific plaintext rune appears

### The 1-Indexing Insight

Cicada 3301 uses **1-indexed** rune numbering throughout their materials. If the cipher also uses 1-indexing:

| Indexing | Identity element | Rune | Doublet means |
|---|---|---|---|
| 0-indexed (standard) | index 0 | ᚠ (F) | Plaintext F at 0.68% — too low for English F (~2.2%) |
| **1-indexed (Cicada)** | **index 29 ≡ 0 mod 29** | **ᛠ (EA)** | **Plaintext EA at 0.68% — plausible for rare digraph** |

Under 1-indexing, the autokey formula C[i] = P[i] + C[i-1] mod 29 treats rune values as 1–29 instead of 0–28. The identity element becomes 29 ≡ 0, which maps to the **last** rune EA (ᛠ) rather than the first rune F (ᚠ). This is equivalent to:

- Vigenere autokey with constant offset +1: C[i] = P[i] + C[i-1] + 1 mod 29
- Beaufort autokey with key = 28: C[i] = C[i-1] + 28 - P[i] mod 29

EA appears in runeglish in words like "each", "ear", "eat", "earth", "east" — typically as the first rune. A frequency of 0.68% is plausible for this rare digraph-rune. The self-referential property (key = 28 = EA's index in 0-based) is thematically consistent with Cicada's style.

---

## Ruled Out

The following cipher classes are **eliminated** by the evidence:

### Simple Monoalphabetic Substitution
**Eliminated by**: Single-letter words are distributed uniformly across all 29 runes (not concentrated on 2 values for "a"/"I"). A monoalphabetic cipher would preserve the concentration of single-letter words on a few rune values.

### Periodic Polyalphabetic (Vigenere with Fixed Key)
**Eliminated by**: Friedman test detects no period. Any periodic key would produce a detectable IOC spike at the key length.

### Pure Transposition
**Eliminated by**: Only skip=1 kappa is anomalous. A transposition would affect kappa at multiple skip values corresponding to the transposition's column width. Also, word boundaries are preserved and match English word lengths.

### Block Cipher / SPN
**Eliminated by**: Word boundaries are preserved with no block structure. Block ciphers operate on fixed-size blocks and would not respect word boundaries.

### Homophonic Substitution (alone)
**Eliminated by**: 29-symbol input maps to 29-symbol output with all symbols used equally. No room for homophones in a same-size alphabet.

### Second-Order Difference Cipher
**Eliminated by**: Delta-of-delta stream has normal doublet count (443 vs 453 expected). A second-order difference cipher would show anomalies in the second difference stream.

### Encoding-Only Explanation
**Eliminated by**: Runeglish encoding alone cannot explain 5.09x doublet suppression. Even accounting for digraph compression (TH→ᚦ, NG→ᛝ), the natural English doublet rate in runeglish is at most ~2x reduced, not 5x. A cipher mechanism is required.

### Explicit Doublet Avoidance (Post-Processing)
**Eliminated by**: Doublet spacings follow a geometric distribution — doublets are independent random events with p≈0.0068. A post-processing rule that "fixes" doublets would produce a different spacing distribution (minimum spacing would be anomalous). The 89 doublets are natural occurrences, not residual errors.

---

## Hypotheses

### Tier 1: Ciphertext Autokey (Strong Evidence)

**Hypothesis 1: Ciphertext Autokey with 1-Indexed Arithmetic**

The primary hypothesis. A Beaufort or Vigenere ciphertext autokey cipher using Cicada's 1-indexed rune numbering (values 1–29 instead of 0–28).

**Mechanism**: C[i] = f(P[i], C[i-1]) where f uses 1-indexed modular arithmetic. Under this model:
- Doublets occur if and only if the plaintext rune at position i+1 is EA (ᛠ, the identity under 1-indexing)
- The flat distribution arises naturally from autokey feedback
- The absence of Friedman period signal is expected (autokey has no fixed period)
- Single-letter words are scrambled because each word's first rune depends on the preceding ciphertext

**Specific variants** (mathematically equivalent under 1-indexing):
- Beaufort autokey with key = 28: C[i] = C[i-1] - P[i] + 28 mod 29
- Vigenere autokey with offset +1: C[i] = P[i] + C[i-1] + 1 mod 29
- Standard autokey in 1-indexed arithmetic: C[i] = P[i]₁ + C[i-1]₁ mod 29, where subscript ₁ denotes 1-based values

**Evidence for**:
- All 89 doublets decrypt to the identity element — mathematical certainty
- EA frequency of 0.68% is plausible for a rare runeglish digraph
- Cicada has used Beaufort autokey in solved LP sections
- Cicada uses 1-indexing throughout their materials
- Key = 28 = EA's own index creates Cicada-style self-reference
- Flat distribution, no period, scrambled single-letter words all consistent

**Evidence against**:
- Simple autokey decryption hasn't cracked the text (likely needs additional layers or unknown primer)
- 0.68% seems low even for EA unless the plaintext has unusual word choices

**Prediction**: Decrypt with Beaufort autokey key=28, check if the resulting text has English-like statistics. Every position where a doublet occurs should correspond to EA in the plaintext.

---

**Hypothesis 2: Prime-Value Tabula Recta Autokey**

An autokey cipher where the tabula recta is constructed using Cicada's prime-rune associations (each rune maps to a prime number). The codebase includes `valueTR()` which builds exactly this kind of TR.

**Mechanism**: C[i] = TR[C[i-1]][P[i]] where TR[k][p] = (prime(k) + prime(p)) mod 29 or similar prime-based arithmetic.

**Key difference from Hypothesis 1**: The identity element under prime-value arithmetic is different from standard additive arithmetic. The "doublet-causing" plaintext rune depends on the specific prime mapping, and could naturally be EA if the prime structure works out.

**Evidence for**:
- Cicada explicitly associates primes with runes (Gematria Primus)
- The `valueTR()` function exists in the codebase, suggesting this is a known construction
- Prime arithmetic mod 29 is well-behaved (29 is prime, so GF(29) is a field)

**Prediction**: Compute the identity element of the prime-value TR and check if it corresponds to EA or another rare rune.

---

### Tier 2: Autokey Variants

**Hypothesis 3: Multi-Layer Autokey**

Two or more autokey passes with different tabula rectae. The first pass suppresses doublets; the second pass makes simple autokey decryption fail.

**Why it matters**: If simple autokey decryption of the unsolved sections hasn't worked, a second layer would explain why while preserving the statistical signature (doublet suppression compounds across layers).

**Evidence**: The squared doublet suppression from double autokey would push the rate from ~3.45% to ~0.12% per layer — but the observed 0.68% suggests either a single layer with a rare identity rune, or two layers where the identity rune is moderately common (~1.8% per layer). The single-layer-with-rare-identity model (Hypothesis 1) is more parsimonious.

---

**Hypothesis 4: Autokey with Keyword Interleaving**

A periodic keyword K is added on top of the autokey: C[i] = P[i] + C[i-1] + K[i mod L] mod 29.

**Effect**: The "identity rune" (the one causing doublets) cycles through L different values depending on position mod L. The doublet rate is the average frequency of L different runes in the plaintext.

**Evidence for**: Would explain why simple autokey decryption fails (unknown keyword). Friedman test wouldn't detect the period because the autokey feedback dominates the periodic component.

**Evidence against**: Adds complexity without strong motivation from the evidence.

---

**Hypothesis 5: Word-Boundary-Reset Autokey**

An autokey that resets its state (primer) at word boundaries. Since word boundaries are preserved, each word starts fresh with a new primer value.

**Evidence for**: Cross-boundary doublets are extra-suppressed (27 observed vs ~116 expected for random). This could indicate different autokey behavior at boundaries — either a reset or a different primer selection rule that avoids producing the same output as the previous word's last rune.

**Evidence against**: Within-word doublets (62) and cross-boundary doublets (27) are both suppressed relative to random, just at slightly different rates. This could also be explained by word-boundary runes having different frequency characteristics in English.

---

### Tier 3: Non-Autokey Alternatives

**Hypothesis 6: First-Difference Cipher**

C[i] = P[i+1] - P[i] mod 29. A doublet requires P[i+2] - P[i+1] = P[i+1] - P[i] — three values in arithmetic progression — which is rarer than random.

**Evidence for**: Elegant mechanism that naturally flattens distributions and suppresses doublets. The running total (cumulative sum) interpretation means decryption is P[i] = sum(C[0..i]) mod 29 plus a constant.

**Evidence against**: Doesn't explain the specific autokey algebraic identity (all doublets → index 0). A difference cipher would produce doublets when three consecutive plaintext values are in arithmetic progression, not when a specific rune appears. The evidence more strongly supports the autokey model.

---

**Hypothesis 7: Additive Stream Cipher with No-Repeat Keystream**

C[i] = P[i] + K[i] mod 29, where the keystream K is generated by a process that guarantees K[i] ≠ K[i+1] (e.g., LFSR over GF(29), or de Bruijn sequence).

**Evidence for**: Produces flat output with suppressed doublets. An LFSR over GF(29) with a primitive polynomial generates maximum-length sequences where consecutive values are never equal.

**Evidence against**: The suppression would be partial (doublets suppressed but not to 0.68% — the rate depends on plaintext statistics interacting with the keystream constraint). Doesn't produce the clean "all doublets → identity element" property seen under autokey.

---

**Hypothesis 8: Markov Chain with Near-Zero Diagonal**

The cipher output follows a first-order Markov chain where P(C[i]=x | C[i-1]=x) ≈ 0.0068/0.0345 ≈ 0.20 and P(C[i]=y | C[i-1]=x) ≈ 1/28.2 for y≠x.

**Note**: This is a **descriptive model**, not a mechanism. It perfectly describes the observed statistics (conditional entropy 4.786 bits ≈ log₂(28), uniform off-diagonal) but doesn't specify how the cipher achieves this. Both autokey and stream cipher mechanisms can produce this Markov structure.

---

### Tier 4: Worth Investigating (Weaker Evidence)

**Hypothesis 9: Affine Autokey**

C[i] = a·P[i] + b·C[i-1] mod 29, where a and b are constants. The multiplicative component (a) adds non-linearity beyond standard additive autokey, potentially making cryptanalysis harder while preserving doublet suppression.

**Identity element**: C[i]=C[i+1] requires a·P[i+1] + b·C[i] = a·P[i+1+1] + b·C[i+1], which simplifies to a·(P[i+1] - P[i+2]) = 0. Since 29 is prime and a≠0, this requires P[i+1] = P[i+2] — a plaintext doublet. The doublet suppression would then reflect the English plaintext doublet rate in runeglish, which is plausible at ~0.68%.

---

**Hypothesis 10: Playfair/Seriated Playfair Variant**

A Playfair-type cipher adapted to 29 symbols. Standard Playfair never produces a doublet within its output bigrams. Cross-bigram doublets would be reduced but not zero, potentially matching the ~0.68% rate.

**Evidence against**: Playfair produces structured bigram statistics that should be detectable. The observed off-diagonal bigrams are perfectly uniform (chi² p=0.23), which is inconsistent with Playfair's characteristic patterns.

---

**Hypothesis 11: Substitution + Autokey Layering**

First apply a monoalphabetic substitution (to scramble letter frequencies), then apply ciphertext autokey. Decryption requires knowing both the substitution key and the autokey primer.

**Why it matters**: This explains why simple autokey decryption hasn't worked — the substitution layer must be removed first. The autokey layer produces the doublet suppression; the substitution layer prevents frequency analysis of the autokey output.

---

**Hypothesis 12: Autokey with Gematria Primus Arithmetic**

C[i] = (prime(P[i]) + prime(C[i-1])) mod 29, where prime() maps each rune to its Cicada-assigned prime value. This is non-linear and uses Cicada's own mathematical framework.

**Difference from Hypothesis 2**: Here the primes are used in the autokey formula directly, not to construct a tabula recta. The identity element depends on which prime value maps to 0 mod 29 when combined with the previous ciphertext's prime.

---

## Crib-Based Attack Vectors

Regardless of which hypothesis is correct, the following cribs constrain the solution:

1. **Doublet positions**: All 89 doublets identify positions where the "identity rune" appears in plaintext (under autokey models). If the identity rune is EA, these are positions where "ea" appears in the English plaintext.

2. **Single-letter words**: 324 single-letter words uniformly distributed across all 29 runes. Under autokey, each decrypts based on the preceding ciphertext. If the plaintext is English, these should concentrate on "a" and "I" after decryption with the correct parameters.

3. **ABA-pattern words**: 32 three-rune words have pattern ABA (first and third rune identical). In English, 3-letter ABA words include "did", "mom", "pop", "nun". These constrain the autokey parameters.

4. **Repeated 6-gram**: ᛞᛄᚢᛒᛖᛁ appears at positions 6555 and 12950. Under autokey, identical ciphertext sequences at different positions imply specific plaintext relationships.

5. **Cross-boundary doublets**: The 27 cross-boundary doublets reveal positions where a word ends and the next word begins with the same ciphertext rune. Under autokey, these constrain the plaintext relationship across word boundaries.

---

## Experimental Priorities

1. **Test Hypothesis 1 directly**: Decrypt all text with Beaufort autokey (key=28) and Vigenere autokey (offset +1). Check resulting text for:
   - English-like IOC (~0.0667 for 26 letters after rune-to-English mapping)
   - Concentration of single-letter words on "a" and "I"
   - Recognizable English word fragments

2. **Compute prime-value TR identity** (Hypothesis 2): Use `valueTR()` to build the prime-based tabula recta and determine which plaintext rune produces the identity (doublet) under autokey with that TR.

3. **Test multi-layer autokey** (Hypothesis 3): Try decrypting with autokey twice using different TR variants (Vigenere then Beaufort, etc.).

4. **Crib drag on single-letter words** (all hypotheses): For each autokey parameter set, check if the 324 single-letter words decrypt to predominantly "a"/"I".

5. **Per-segment analysis**: The per-segment doublet rates vary (0.52% to 1.08%). Test if different autokey primers or offsets per segment improve decryption results.
