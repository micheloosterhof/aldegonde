---
type: hypothesis
---
# Hypothesis: The Space Step σ is a Power of g

## Claim

In the length-clocked walk (`length-clocked-walk.md`) the two key
permutations are related: σ = g^k for some k — σ = g, g², g³, g⁻¹ (= g⁴),
or the identity. The key would then be a single permutation `g` plus an
exponent, roughly halving the key material.

## Status

**Status**: disproved (all five powers, on three independent grounds;
near-powers excluded too — see Evidence against)

## Mechanism

If σ ∈ ⟨g⟩ (cyclic, order 5), every per-word base is base₀ ∘ g^m: the
cipher collapses to **five alphabets**, scheduled aperiodically by the
word lengths. For σ = g specifically, the boundary factor
g^((L−1) mod 5) ∘ g completes each word to a full cycle and the alphabet
depends only on absolute position mod 5 — a strict period-5
polyalphabetic.

## Evidence for

- Parsimony: one permutation instead of two.
- The boundary step already contains a power of g (g^((L−1) mod 5)), so a
  designer folding σ into ⟨g⟩ is not far-fetched.

## Evidence against

1. **The identity census (kills every k).** With five reachable bases,
   ~1/5 of repeated plaintext words recur under a colliding base and
   encrypt **identically**. Simulated on an LP-sized register corpus
   (2,928 words, `experiments/sigma_power_kill.py`):

   | σ | identity pairs | unigram nIoC | Friedman-5 |
   |---|---|---|---|
   | g⁰ (id) | 2,659 | 1.174 | 1.174 |
   | g | 2,567 | 1.173 | **1.768** |
   | g² | 2,561 | 1.174 | 1.175 |
   | g³ | 2,492 | 1.174 | 1.174 |
   | g⁴ (= g⁻¹) | 2,599 | 1.175 | 1.178 |
   | g² ∘ (one transposition) | **876** | 1.165 | 1.166 |
   | random mixed | 16 | 0.999 | 0.998 |
   | **LP observed** | **17 (chance 10.7 ± 3.3)** | **1.000** | **~1.00** |

   Every power predicts thousands of identical cipher-word pairs
   (`word-transform-census.md`: at chance) and a visibly non-flat unigram
   distribution (a mixture of five permuted English distributions; a
   designed "flattening quintet" could fix the unigrams but not the
   census). Two orders of magnitude, each column.
2. **Near-powers die too.** One transposition away from g² still leaves
   ~900 identity pairs — the base orbit grows too slowly. σ is not merely
   outside ⟨g⟩; it must scramble the coset walk fast enough to visit
   hundreds of bases (see the bound below).
3. **σ = g is separately dead by periodicity**: strict period 5 in
   absolute position (simulated Friedman-5 = 1.77 vs LP ~1.00; the kappa
   spectrum and Friedman scans exclude any period).
4. **The DJU-BEI state return forbids the powers arithmetically**
   (conditional on the full-return reading — the ciphertext itself only
   forces 6-point agreement). The return over the 1,449-word interval
   requires 4946·[g] + 1449·[σ] ≡ 0 in the abelianization; substituting
   σ = g^k gives 1 + 4k ≡ 0 (mod 5), i.e. **k = 1** — the one power
   already excluded by periodicity. The state return and σ ∈ ⟨g⟩ are
   jointly inconsistent.

## What σ must satisfy (the surviving constraints)

- **Seam algebra — σ isolated exactly.** In the walk, the length factor
  cancels at the boundary: a cross-word doublet occurs **iff
  p_last = σ(p_first)**, independent of g and of the word length. The
  seam doublet rate (0.0079) is therefore σ's diagonal measured against
  the CROSS-word bigram distribution (last-letters × first-letters) — σ
  is rare-diagonal tuned on a different table than g, and the 23 observed
  seam doublets are 23 pure σ-diagonal events. The predicted
  length-independence is verified: the diagonal rate is flat across
  (L−1) mod 5 classes, and the full seam channel carries no other
  structure (`seam-channel-clean.md`).
- **σ cannot be an arithmetic map (July 2026,
  `experiments/sigma_algebraic_floor.py`).** The seam relation makes the
  observed cross-word doublet rate 0.0079 *literally* σ's diagonal on the
  word-final × word-initial plaintext table — a different table from g's
  adjacent bigrams, so g's affine exclusion does not carry over and had
  to be computed separately. Minimum achievable diagonal by family
  (register prose, LP length mix):

  | family | min diagonal | vs observed 0.0079 |
  |---|---|---|
  | additive `x+b` | 0.0207 | 2.6x too high |
  | Beaufort `b−x` | 0.0211 | 2.7x too high |
  | multiplicative `a·x` | 0.0122 | 1.5x too high |
  | affine `a·x+b` | 0.0122 | 1.5x too high |
  | inverse `a/x+b` | 0.0162 | 2.1x too high |
  | unconstrained permutation | 0.0048 | reachable |
  | random permutation | 0.0343 (mean) | — |

  Every arithmetic family floors out above the observation while a
  general mixed permutation clears it comfortably. The margins
  (1.5-2.7x) are far beyond plausible register variation. σ is a
  non-arithmetic mixed permutation, and — like g — a *mildly* rare one:
  0.0079 sits 1.6x above the 0.0048 assignment-problem floor, not at it.
- **Group-size floor.** The census bounds the number of visited bases:
  excess identity pairs ≲ 13 (2σ) against ~8,000 register-implied
  repeated pairs gives **N ≳ 600** distinct bases, so |⟨g, σ⟩| is at
  least in the hundreds.
- **σ does NOT normalise ⟨g⟩ — so the walk has no closed form**
  (July 2026). This is the question "what does the base look like four
  words in?". In general it is the raw alternating word
  `base_0 g^{a₀} σ g^{a₁} σ g^{a₂} σ g^{a₃} σ` with no simplification.
  It *would* telescope if σ normalised ⟨g⟩ (σgσ⁻¹ = g^r), because every
  σ could then be pushed past the g's, giving the clean closed form

      base_w = base_0 ∘ g^(Σᵢ aᵢ rⁱ mod 5) ∘ σ^w

  — a polynomial in `r` evaluated on the public word-length sequence,
  times a power of σ. But that form caps the state at the pair
  (exponent mod 5, w mod ord σ), i.e. at most **5·ord(σ)** distinct
  bases, and the maximum order of a normalising σ on 29 points is
  **100** (the commuting case: a 5-cycle of g's blocks with nonzero
  shift-sum gives order 25 on the 25 moved runes, times a 4-cycle on the
  4 fixed runes, lcm = 100; the genuinely twisted cases r = 2,3,4 cap at
  60). That allows at most 500 bases against the ~600 the census
  requires — so normalising σ, including the commuting case, is
  excluded. (At the census bound's own ~2σ strength, and inheriting its
  register assumption.) This supersedes the earlier note here that
  commuting σ was unconstrained: the centralizer is indeed large
  (~9×10⁶ elements) but its *element orders* are not, and that is what
  the base count depends on.

  Consequence: the base sequence is a genuine non-abelian alternating
  product with no algebraic shortcut — which is precisely why it cannot
  be summarised by a small state, and why a one-transposition error in σ
  propagates catastrophically down the chain
  (`no-known-plaintext-foothold.md`, constraint 3 in `README.md`).
- **Abelianization link** (conditional, as above): [g] = −1449·[σ], with
  the parity necessary-condition σ even (`walk_verifier.py`).
- **Not excluded**: σ of order 5, σ a conjugate h∘g∘h⁻¹, larger
  compositions g^k∘τ with τ moving enough points to break the small
  orbit.

## Predictions

- Any candidate key pair (g, σ) must show a σ-diagonal rate ≈ 0.0079 on
  the cross-word bigram table and satisfy the abelianization parity —
  both are cheap pre-filters for key enumeration
  (`experiments/enumerate_keys.py`).
- If a decryption is ever obtained, the 23 seam doublets directly read
  out 23 values of σ (p_last = σ(p_first) at each).

## Scripts

- `experiments/sigma_power_kill.py` — the simulation table above.

## Related

- `length-clocked-walk.md` — the model whose σ this constrains; its
  "outside ⟨g⟩" assertion is here made quantitative.
- `word-transform-census.md` — the identity-pair census the kill rests on.
- `repeated-phrase-dju-bei.md` — the state return behind the
  abelianization constraint.
- `g-from-5x5-grid.md` — construction proposals for g; the same grid idea
  could apply to σ, now knowing σ ∉ ⟨g⟩.

## Verdict

Disproved for every power and for small perturbations of a power: the
five-alphabet collapse predicts thousands of identical cipher words and
non-flat unigrams, the LP shows neither, and the DJU-BEI arithmetic
independently forbids k ≠ 1 while periodicity kills k = 1. σ is a second,
genuinely independent mixed permutation — but not a free one: it carries
its own tuned rare diagonal on the cross-word bigram table, a parity
condition, the abelianization link to g, and a floor of hundreds on the
group the pair generates.
