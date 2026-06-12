# Hypothesis: Autokey Outer Layer + Unknown Inner Layer

## Claim

The cipher has (at least) two layers: an outer ciphertext autokey
(Beaufort/Vigenere) and an inner transformation. The delta text
D[i] = (C[i-1] - C[i]) mod 29 is the output of the inner layer, not
the plaintext directly.

## Status

**Status**: unresolved

## Mechanism

Layer 1 (inner, unknown): M[i] = transform(P[i])
Layer 2 (outer, autokey): C[i] = C[i-1] - M[i] mod 29

The delta text D[i] = (C[i-1] - C[i]) mod 29 recovers M (the inner
layer's output). M has specific properties that constrain the inner
layer.

## Evidence for

- **Normal doublets/triplets in delta**: The delta text has 443 doublets (vs
  453 expected) and 16 triplets — perfectly normal. The autokey layer is what
  creates the doublet suppression in the ciphertext.
- **F suppression in delta**: Delta value 0 (= EA under 1-based indexing)
  occurs at 0.68% instead of 3.45%. This is the "shadow" of the ciphertext's
  doublet suppression: C[i]=C[i-1] iff delta=0.
- **28-symbol effective alphabet**: The delta text excluding value 0 has IOC =
  0.03576, matching 1/28 = 0.03571 perfectly. The inner layer output avoids
  the identity value.

## Evidence against

- **Bigram structure is only from F suppression**: The delta bigram chi-sq
  (1433 vs 840) is entirely explained by the rarity of value 0. Non-zero
  bigrams are perfectly uniform (chi-sq 766 vs 783 expected). No hidden
  bigram structure beyond the F/EA suppression.
- **Delta text is random over 28 symbols**: IOC 0.03576 = 1/28 exactly.
  Repeat counts match 28-symbol random text. No word-boundary effects.
- The split test on the delta text (group by delta[i-1]) gives random IOC.
  So the inner layer is not another autokey.
- A monoalphabetic inner layer is ruled out (would preserve IOC at
  English-like levels, not flatten to 1/28).

## Predictions

The inner layer maps 29 English runeglish plaintext runes to 28 non-zero
values (avoiding F/index 0). This inner layer must:
1. Flatten the English letter frequencies to near-uniform
2. Map 29 symbols to 28 (lossy, or the missing symbol is very rare)
3. Preserve word boundaries

Possible inner layer mechanisms:
- A homophonic-like encoding that redistributes letter frequencies
- A compression that eliminates one symbol
- A non-linear substitution that happens to flatten frequencies

## Scripts

- `experiments/jstream_battery.py` — full test battery on the 28-symbol
  inner stream J[t] = (C[i] - C[i-1] - 1) mod 28 (the delta text's live
  values), June 2026. Tests BOTH interrupter alignments: doublet steps
  deleted (EA-as-ditto reading: the marked rare rune consumes plaintext but
  no key, so deleting doublets re-aligns a periodic inner key) and doublet
  steps as gaps (the marked rune consumes key). Results, all flat:
  - kappa at every shift, both alignments: max |z| ~3.8 of 6,475 shifts,
    below the expected extreme for that many trials
  - Friedman column IoC, periods 2-120, compressed stream: top 1.0155
    (~1.7 sigma). Column IoC is permutation-invariant, so this excludes a
    periodic inner key for ANY mixed alphabet, in both alignments
  - CRT projections mod 2/4/7/14 (28 = 4 x 7): marginals and kappa flat
    (a mod-14 marginal blip at p=0.006 is noise projection: no step-size
    wheel-distance trend, r=0.08 p=0.68, and no clockwise vs
    counterclockwise asymmetry, p=0.12)
  - linear functionals (J[t+d] + a*J[t] + b) mod 28, d <= 20: none
  - pairwise contingency J[t] vs J[t+d], d <= 50: none (flatness at d=1
    argues against an inner layer g(P[i], P[i-1]) with generic mixing)
  - DFT, all multipliers x all real frequencies: white
  - J grouped by position-in-word: flat (no word-keyed inner layer)
  - repeated J n-grams: at chance except the DJU-BEI repeat

## Additional constraint (June 2026)

Any cipher of the form **C[i] = f(C[i-1], P[i])** with f(c, .) a
permutation for each c — which includes this model with a memoryless inner
layer, for EVERY alphabet family — is excluded analytically: given
C[i-1] = c, the next-symbol distribution would be a permuted mixture of
English conditional letter distributions (strongly non-uniform), but the
observed bigram rows are uniform off the diagonal. The inner layer
therefore needs at least one more symbol of hidden context beyond
(C[i-1], P[i]), and by the DJU-BEI depth (`repeated-phrase-dju-bei.md`)
that context must be SHORT and plaintext-driven so the state can recur.

## Related

- `ciphertext-autokey.md` — Single-layer autokey is disproved
- `substitution-plus-autokey.md` — Substitution before autokey doesn't flatten
  IOC (preserves it). The inner layer here must be something that DOES flatten.

## Simulation exclusion of bounded-context inner layers (June 2026)

`experiments/inner_layer_sim.py` generates runeglish-like plaintext from
the repo's trigram/quadgram tables, encrypts with C[i] = C[i-1] - M[i]
where M[i] = g(P[i], ..., P[i-k]) for random tables g, and measures the
same J statistics observed on the real cipher:

| inner layer | J marginal chi2 (obs 41.7) | J d=1 contingency (obs 684.2) |
|-------------|---------------------------:|------------------------------:|
| memoryless g(P) | 27,164 ± 6,947 | 6,563 ± 836 |
| lag-1 g(P,P') | 2,276 ± 522 | 6,601 ± 410 |
| lag-2 g(3 runes) | 356 ± 82 | 1,749 ± 117 |
| lag-3 g(4 runes) | 89 ± 25 | 1,067 ± 59 |
| lag-4 g(5 runes) | 42 ± 9 | 832 ± 45 |
| lag-5 g(6 runes) | 31 ± 9 | 766 ± 41 |

(null reference: marginal dof 27, contingency dof 729; lag-4/lag-5 use a
hash-realized generic table; the hash lag-4 run reproduces the explicit
29^5-array run exactly.)

Generic bounded-context tables are excluded through **5 runes of context**
(lag-4: simulated d=1 contingency 838 ± 49 over 40 samples vs 684.2
observed, z = -3.1, with 0/40 samples reaching the observed value — the
simulated minimum was 730; the marginal statistic stops discriminating at
this size, matching the observed 41.7 exactly). **6 runes of context is
disfavored at ~2 sigma** (766 ± 41 vs 684) but cannot be excluded; 7+
runes is statistically invisible to this test. The d=1 excess decays
~3.3x per added context rune. All exclusions are lower bounds: real
plaintext has longer-range structure than the order-3 simulator, which
would only make a real bounded-context cipher more detectable. The
observed 684.2 in fact sits below even the null mean (729, p=0.88) — the
real stream is flat into the null's low tail. Caveat: a *designed*
(balanced) table rather than a random one could suppress these
statistics, but flattening the d=1 joint alone imposes ~729 simultaneous
design constraints; pushing all measured statistics to chance requires g
to approach a strong pseudo-random function of its context.

## Verdict

Unresolved, but boxed in hard. The inner 28-symbol stream is flat against
every periodicity, recurrence, CRT, functional, positional, and
bounded-context test. What survives:

1. **Uniform keystream + rare-rune ditto**: J[t] = img(P[t]) + K[t] with
   K effectively uniform-iid (true pad or strong PRNG), plus the doublet
   rule marking a rare plaintext event. This fits every observed statistic;
   under it the DJU-BEI depth is a ~0.5% coincidence and the only
   recoverable plaintext information is the 89 marked positions and the
   word lengths.
2. **A designed, balanced inner table — or a generic one with >= 6 runes
   of context** (6 runes itself mildly disfavored at ~2 sigma) — enough to
   defeat the simulation bounds — whose state recurred once to produce the
   DJU-BEI depth, which this variant explains better than chance.

The DJU-BEI repeat is the main evidence discriminating (2) over (1).
