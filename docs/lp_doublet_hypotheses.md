# Liber Primus Doublet Suppression Analysis

## Observed Properties

1. **29-symbol alphabet** (Gematria Primus / Elder Futhark)
2. **Near-random statistics** (flat distribution, IoC ≈ 1/29 ≈ 0.0345)
3. **Doublets suppressed 5-6×** (expected ~3.45%, observed ~0.6%)
4. **Zero triplets** in the corpus
5. **KRAKUP analysis**: highly nonhomogeneous (score ~0.4-0.5), suggesting mixed material or changing periods

## Hypotheses

### Hypothesis 1: Simple Ciphertext Autokey (RULED OUT)

**Mechanism**: Beaufort or Vigenère ciphertext autokey with standard tableau.

```
C₀ = K₀ - P₀  (primer)
Cᵢ = Cᵢ₋₁ - Pᵢ  (Beaufort)
```

**Doublet condition**: Cᵢ = Cᵢ₋₁ ⟺ Pᵢ = 0

**Why it fails**:
- Trying all 29 single-rune primers produces no recognizable plaintext
- The decrypted text remains random with high IoC
- If this were the cipher, at least one primer should reveal patterns

**Status**: RULED OUT for simple case, but see Hypothesis 1b.

---

### Hypothesis 1b: Custom Alphabet Autokey (Quagmire-style)

**Mechanism**: Autokey cipher using a keyed/scrambled tableau instead of standard Vigenère/Beaufort tableau.

```
C₀ = T[K₀][P₀]  (keyed tableau T, primer K₀)
Cᵢ = T[Cᵢ₋₁][Pᵢ]  (ciphertext autokey with custom tableau)
```

**Doublet condition analysis**:

In a standard tableau, row k has identity at column 0: T[k][0] = k for all k.

In a scrambled tableau:
- Each row is a permutation of 0-28
- For row k, the identity element (where T[k][p] = k) varies
- Let I(k) = the identity element for row k

Doublet Cᵢ = Cᵢ₋₁ occurs when Pᵢ = I(Cᵢ₋₁)

**Key insight**: If the tableau is constructed such that all identity elements are the SAME value (say, all rows have identity at column 7), then:
- Doublet rate = frequency of symbol 7 in plaintext
- If that symbol is rare in plaintext → doublets are rare

**Properties of custom alphabet autokey ciphertext**:
1. IoC remains near random (autokey destroys patterns)
2. Doublet rate depends on tableau structure and plaintext distribution
3. Without the keyword, the tableau is unknown → 29! possible permutations per row
4. Standard attacks (trying 29 primers) fail because the tableau is wrong
5. Frequency analysis fails because autokey + scrambling destroys patterns

**Why this is promising**:
- Explains why trying 29 primers doesn't work (wrong tableau)
- Explains doublet suppression (if tableau has consistent identity structure)
- Explains near-random statistics (autokey property)
- Matches known Cicada use of Beaufort + keywords

**Open question**: What tableau structure would give consistent identity elements while remaining a valid Latin square?

---

### Hypothesis 2: Plaintext Autokey / Running Key (EQUIVALENT TO 1)

**Mechanism**: Running key where key is the plaintext shifted by some offset.

This is mathematically equivalent to plaintext autokey:
```
Cᵢ = Pᵢ - Pᵢ₋ₙ (mod 29)
```

For n=1, this is first-difference encoding.

**Doublet condition**: Pᵢ - Pᵢ₋ₙ = Pᵢ₊₁ - Pᵢ₊₁₋ₙ

**Status**: Subsumed by Hypothesis 1/1b analysis.

---

### Hypothesis 3: Progressive Counter Element (TESTED, INCONCLUSIVE)

**Mechanism**:
```
Cᵢ = Pᵢ + Kᵢ + i·c (mod 29)
```

Where c is a constant increment (tried c=1).

**Doublet condition**:
```
Pᵢ + Kᵢ + i·c = Pᵢ₊₁ + Kᵢ₊₁ + (i+1)·c
Pᵢ - Pᵢ₊₁ + Kᵢ - Kᵢ₊₁ = c
```

**Status**: Tested with c=1, no patterns emerged. Could test c=2..28.

---

### Hypothesis 4: Explicit Anti-Doublet Rule (RULED OUT)

**Mechanism**: "If next ciphertext would repeat, add 1"

**Status**: RULED OUT - inelegant and would create detectable statistical anomalies.

---

### Hypothesis 5: Monoalphabetic Layer on Autokey

**Mechanism**: Two-layer encryption:
1. First layer: Autokey (produces few doublets due to plaintext property)
2. Second layer: Monoalphabetic substitution (MASC)

```
C = MASC(Autokey(P, primer), substitution_key)
```

**Why this works**:
- MASC preserves doublet relationships perfectly (if A→X, then AA→XX)
- Autokey creates few doublets if some plaintext symbol is rare
- MASC scrambles everything else, making frequency analysis fail
- Combined: random-looking output with suppressed doublets

**Properties**:
- Doublet rate = frequency of identity element in autokey output
- MASC adds 29! complexity on top of autokey
- Explains why standard attacks fail

---

### Hypothesis 6: Polygraphic Element (Digraphic Cipher)

**Mechanism**: What if the cipher operates on pairs?

A Playfair-like or Hill-like cipher on rune pairs:
- Input: digraphs (pairs of runes)
- Output: digraphs
- If the cipher maps (A,A) to rare outputs, or has structure that avoids adjacent identical symbols

**Properties of Playfair that suppress doublets**:
- Playfair explicitly handles doubles by inserting nulls
- Could a similar mechanism be at play?

**Status**: Worth investigating if the text length is even and digraph analysis shows structure.

---

### Hypothesis 7: Interrupted Key with Phase Shifts

**KRAKUP analysis** shows:
- Homogeneity score ~0.4-0.5 (highly nonhomogeneous)
- Multiple stable regions with different dominant periods
- Phase slips detected at specific positions
- Period changes throughout the text

This suggests the cipher might:
1. Change key/method at certain points
2. Have interruptions or resets
3. Be a mix of different sections with different encryption

**Implication**: The doublet suppression might be a property of the OVERALL construction, not a single cipher.

---

## Key Questions to Investigate

1. **Custom tableau structure**: What Quagmire-style tableau would have all identity elements at the same column? Is this possible while maintaining invertibility?

2. **MASC + Autokey testing**: Can we detect if there's a MASC layer by analyzing digraph patterns or other second-order statistics?

3. **Segment-by-segment analysis**: Do different LP segments have different doublet rates? This would support the nonhomogeneous hypothesis.

4. **Known plaintexts**: In solved LP pages, what is the frequency of the identity element? Does it match the observed doublet rate?

5. **Digraphic patterns**: Even with suppressed doublets, are there patterns in the digraph distribution that could reveal structure?

---

---

## CRITICAL FINDING: Runeglish Frequencies Match Doublet Rate!

**CORRECTION**: I initially confused CIPHERTEXT frequencies with PLAINTEXT frequencies.

- **CIPHERTEXT** has flat frequencies (3.05% - 3.75%) - this is EXPECTED from autokey
- **PLAINTEXT** (Runeglish from English) has very different frequencies!

Actual LP ciphertext statistics:
- Total runes: 13,136
- Doublets: 89 (0.678%)
- Suppression: 5.09x
- Triplets: 0

**Runeglish frequencies from English text (2M+ characters):**
```
ᛟ (OE   ):  0.08%  <-- extremely rare
ᛄ (J    ):  0.15%  <-- very rare
ᛇ (EO   ):  0.18%  <-- very rare
ᚫ (AE   ):  0.18%  <-- very rare
ᛉ (X    ):  0.32%  <-- very rare
ᛠ (EA   ):  0.45%  <-- rare
ᚦ (TH   ):  0.56%  <-- CLOSE TO 0.68%!
ᛝ (NG   ):  0.60%  <-- MATCHES 0.68%! ✓
ᚹ (W    ):  0.64%  <-- MATCHES 0.68%! ✓
ᚠ (F    ):  1.11%
ᛡ (IA/IO):  1.41%
...
ᛖ (E    ):  9.94%  <-- most common
```

**The doublet rate of 0.68% matches NG (0.60%) or W (0.64%) almost exactly!**

---

## CONFIRMED: Simple Quagmire Autokey IS Consistent

For ciphertext autokey: `doublet_rate = frequency(identity_char_in_PLAINTEXT)`

If the Quagmire keyword starts with:
- **ᛝ (NG)**: plaintext frequency 0.60% → expect ~0.60% doublets ✓
- **ᚹ (W)**: plaintext frequency 0.64% → expect ~0.64% doublets ✓
- **ᚦ (TH)**: plaintext frequency 0.56% → expect ~0.56% doublets ✓

The observed 0.68% is within statistical noise of these values!

**Per-segment doublet rates vary:**
```
Segments 0-4: 0.52-0.55% (6.3-6.6x suppression) ← more suppressed
Segments 5-9: 0.60-1.08% (3.2-5.8x suppression) ← less suppressed
```

This variation could indicate:
1. Different keywords per segment (different identity characters)
2. Different plaintext content (more/fewer NG/W/TH occurrences)
3. Or different encryption methods entirely

**All 29 runes appear as doublets** (1-7 occurrences each), which IS consistent with autokey (the doublet symbol depends on previous ciphertext, not on the identity character).

---

## Primary Hypothesis: Quagmire III Autokey with Rare Digraph Identity

The cipher is likely:
1. **Quagmire III** (keyed Beaufort) with **ciphertext autokey**
2. **Keyword starts with NG, W, or TH** (or letter that maps to position 0)
3. This makes the identity character one with ~0.6% frequency in Runeglish

Why this explains everything:
- ✓ Flat ciphertext distribution (autokey property)
- ✓ Suppressed doublets (rare identity character)
- ✓ Zero triplets (probability ≈ 0.006² ≈ 0.004%)
- ✓ No pattern in single-key decryption (wrong tableau without keyword)
- ✓ Matches known Cicada use of Beaufort + keywords

---

## Alternative Hypotheses (Lower Probability)

---

## Experimental Confirmation

Ran `experiments/custom_autokey_analysis.py` on 10,000 characters of English-like text:

```
Keyword: DIVINITY  → Identity: D (4.3% in text) → Doublet rate: 4.3%  (0.9x suppression)
Keyword: FIRFUMFER → Identity: F (2.4% in text) → Doublet rate: 2.4%  (1.6x suppression)
Keyword: PRIMUS    → Identity: P (1.9% in text) → Doublet rate: 1.9%  (2.0x suppression)
Keyword: A         → Identity: A (8.6% in text) → Doublet rate: 8.6%  (0.4x suppression)
```

**KEY FINDING**: In Quagmire III ciphertext autokey:
- **Doublet rate = frequency of identity character in plaintext**
- Identity character = first letter of mixed alphabet = first letter of keyword
- Ciphertext IoC is ALWAYS near-random (~1/n) regardless of keyword

---

## Implications for Liber Primus

For LP with 5-6x doublet suppression:
- Expected random doublet rate: 1/29 ≈ 3.45%
- Observed doublet rate: ~0.6%
- Therefore: **identity character appears ~0.6% of the time in plaintext**

This is VERY rare. In a uniform 29-symbol distribution, each symbol would be ~3.45%.

**Possible explanations**:

### A. Keyword starts with a rare character
If the keyword starts with a rune that maps to a letter rare in the plaintext (like Q, X, Z in English), we'd see suppression. But 5-6x is extreme—even Z at 0.07% wouldn't quite work.

### B. Plaintext avoids the identity character
The plaintext (before encryption) might have been preprocessed to avoid a specific character. This could be:
- A stylistic choice (avoid certain words/letters)
- A deliberate obfuscation layer
- A property of an intermediate encoding

### C. MASC layer on top of autokey
```
Plaintext → Autokey encrypt → MASC → Ciphertext
```
- The MASC scrambles the alphabet but preserves doublet relationships
- Combined with autokey: explains random statistics + doublet suppression
- Adds 29! complexity to the MASC layer alone
- Standard attacks (29 primers) fail because MASC is unknown

### D. Multiple keywords/segments
KRAKUP shows nonhomogeneous material. Different sections might use:
- Different keywords (different identity characters)
- Different primers
- Different cipher modes entirely

The average effect could produce the observed 0.6% doublet rate if the identities vary but all are moderately rare.

---

## Critical Insight

**To achieve 5-6x doublet suppression in ciphertext autokey:**

The identity character (first letter of keyword in mixed alphabet) must appear at ~1/6 of its expected random frequency in the plaintext.

For a 29-symbol alphabet:
- Expected: 3.45%
- Observed: 0.6%
- Ratio: 5.75x

This is a VERY strong constraint on either:
1. The keyword choice (must start with something rare)
2. The plaintext content (must avoid that character)
3. An additional layer (MASC, encoding, etc.)

---

## Next Steps

1. ~~Implement custom alphabet autokey encryption/decryption~~ DONE
2. Analyze doublet rates per segment
3. Compare with solved LP pages
4. Search for tableau structures with consistent identity elements
5. Test MASC + autokey hypothesis
6. **NEW**: Calculate which Gematria Primus character at ~0.6% frequency would explain doublet rate
7. **NEW**: Test if solved pages show this same identity character pattern
