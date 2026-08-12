---
type: observation
---
# No Known-Plaintext Foothold; Section 11 is the Only Plaintext Section

## Status

**Status**: confirmed (characterization) for the no-known-plaintext claim
itself, **qualified for partial cribs** — see the note below. The
"Consequences for the attack" section is conditional on the
length-clocked-walk model, which is plausible, not confirmed.

## Claim

The attack on sections 0-9 must be **blind (ciphertext-only)**. There is no
known-plaintext pair available inside `data/page0-58.txt`: the one readable
section, **section 11 (the Parable), is stored as unencrypted plaintext** — it
was never run through the 0-9 cipher, so it yields no plaintext↔ciphertext pair.

**Qualification (partial cribs).** The claim above holds for known-plaintext
*pairs* — no enciphered string whose plaintext is known. It is too strong as a
statement about plaintext constraint in general. The four apostrophes recovered
from the page scans (`contraction-cribs.md`) pin four words to small candidate
sets: the rune after each mark is `S`, `D` or `T`, and the two sites with a
two-rune stem cannot be `n't`. That is ≈ 28 bits of constraint at offsets 1107,
5136, 8513 and 10086. It is weaker than a known-plaintext pair — a candidate
set, not a known string — and `no-periodicity.md` stops the four sites from
chaining, so the attack on the bulk of the corpus remains blind. But the
corpus is not wholly without plaintext constraint.

## Evidence

- Section 11 transliterates directly (Gematria Primus rune→English):
  "PARABLE. LIKE THE INSTAR TUNNELING TO THE SURFACE. WE MUST SHED OUR OWN
  CIRCUMFERENCES. FIND THE DIVINITY WITHIN AND EMERGE." — 95 runes, clean English.
- Its IoC is **1.82** (rough, plaintext-like) versus ~1.0 for the encrypted
  sections 0-10 (sec 0 0.99, sec 8 1.00, sec 9 0.98, sec 10 0.94). So section 11
  is the *only* plaintext section; everything else is flat/enciphered.
- The Parable text yields no locatable crib inside 0-9: no test run
  (running-key slides, kappa scans) finds it, and an enciphered copy under
  the unknown cipher would be undetectable by those tests anyway — so it
  provides no foothold, which is weaker than proving it absent.

Useful by-product: section 11 confirms real LP plaintext IoC ≈ 1.8, matching the
runeglish-is-rougher-than-English fact and better than dictionary/prose proxies.

## Consequences for the attack

- **No algebraic known-plaintext recovery** of `(base_0, g, σ)`. The blind
  hillclimb is the only direct path, and it fights the diffusion barrier (three
  globally-coupled permutations, no fitness gradient until nearly solved).
  **The gradient problem has a partial answer**: score candidate keys on
  the 465 two-rune words instead of on n-gram fitness. In runeglish THE
  is exactly `ᚦᛖ`, and the 2-rune word class is dominated by eight
  function words (69% of tokens), so a correct key yields ~75-108 `ᚦᛖ`
  decryptions where chance gives 0.6, and the register log-likelihood
  over the whole class supplies the partial credit a pure count cannot.
  See the Predictions section of `length-clocked-walk.md`. This is a
  statistical crib rather than a known-plaintext foothold — it assumes
  only that the plaintext is ordinary English, not that any particular
  word sits at any particular place.
  **Both the 75-108 figure and the 465-word class need revising (August
  2026, `two-rune-deficit.md`).** The 2-rune deficit is z ≈ −10 on two
  independent references, so 75-108 over-estimates the STANDALONE count;
  and if the missing short words are attached to neighbours rather than
  absent, `ᚦᛖ` sits inside longer words that this class never inspects.
  Since the within-word phase is length-independent — `c₀ = base_w(p₀)`,
  `c₁ = base_w(g(p₁))` for any word — the class should be all 2,928
  word-initial digraphs, and word-final ones too if the attachment is to
  the previous word. That raises chance from 0.6 to ~3.5, which the
  correct-key count still dwarfs, and it cannot lose instances.
- **Tested on planted keys — the objective is a superb VERIFIER and a
  useless SEARCH GRADIENT** (July 2026,
  `experiments/two_rune_gradient.py`; simulated walk ciphertext over
  real English words in the LP length structure, known key):
  - Given `g` and `σ`, plain transposition hill-climbing recovers
    `base_0` **exactly, on the first restart** — the true key scores
    −1319 against −5366 for a random base (a gap of 4,047 nats, 8.7 per
    word), and all 79 planted THEs decrypt.
  - Searching `base_0` and `g` jointly **fails completely** (best −4901,
    `base_0` 0/29 correct), and all three jointly likewise.
  - The reason is measured directly: define score\*(g, σ) as the score
    after optimally fitting `base_0`. Then score\*(true) = −1296, while
    **σ off by a single transposition gives −4968 and a random key gives
    −4994** — one swap is already indistinguishable from noise. Same for
    a single conjugation of `g` (−4967).
  This quantifies the diffusion barrier exactly: `σ` and `g` enter the
  base chain once per word, so a one-swap error is applied ~2,900 times
  and every base past the first is destroyed. The landscape over
  `(g, σ)` is a delta function — flat everywhere, spiked only at the
  exact key.
- **The prefix escape was tested and does not rescue it.** Errors
  saturate with distance along the chain, so a *short prefix* should
  retain signal the full corpus destroys — and it does, measurably: with
  `base_0` and `g` known, trigram fitness on the first 160 words puts a
  one-transposition-wrong `σ` several sd above random, where the
  full-corpus objective puts it at 0.8 sd. **The basin width depends on
  the prefix length, and that is exactly what kills the idea** — basin
  and statistical power move in opposite directions with K, and they
  never overlap. With `base_0` and `g` handed over for free:

  | K words | runes | signal a 1-swap σ retains | hill-climb from random |
  |---|---|---|---|
  | 5 | 23 | 100% | — |
  | 10 | 49 | 94% | score −3.86 vs true −3.38, **1/29 correct** |
  | 15 | 75 | 84% | — |
  | 20 | 95 | 58% | −4.76 vs −3.77, **1/29** |
  | 40 | 177 | 42% | −5.67 vs −3.62, **0/29** |
  | 160 | 729 | 14% | 1/29 |

  At short prefixes the basin is genuinely wide, but the objective is
  **degenerate**: 49 runes cannot pin a 29-permutation, so the climb
  finds a σ that renders plausible runeglish and is nowhere near the
  key. At long prefixes the objective discriminates but the basin has
  collapsed and the climb never leaves the flat. Nothing in between
  works either — at K = 20 the basin is already halved and the climb
  still returns 1/29.

  **Practical warning**: the short-prefix failures score *close to the
  true key* (−3.86 against −3.38 at K = 10) while being essentially
  100% wrong. A prefix-based attack will manufacture convincing false
  positives, and anyone running one should verify on the full corpus,
  where those candidates collapse to −6.83 against the true −3.56. **Consequence for the attack architecture**: no
  hill-climb, annealing or evolutionary search over `(g, σ)` can work,
  with this or any comparable objective. `base_0` is effectively free
  (a 29!-fold reduction, solved by the objective in seconds), so the
  entire difficulty is concentrated in `(g, σ)`, which must come from
  **enumeration over structurally constrained candidates** — making the
  filter stack (`sigma-power-step.md`, `g-from-5x5-grid.md`) and the
  small-key construction problem the whole game.

**The search space, and the one route left.** With `base_0` free, the
space is `(g, σ)`: order-5 permutations number 9.84e23, of which ~0.1%
carry a diagonal in the required band → ~1e21 candidate `g`; `σ` ranges
over 29! = 8.8e30, of which ~1.6e-4 sit in the cross-word diagonal band
→ ~1.4e27. The joint space is **~1e48**, so blind enumeration is as
hopeless as local search. That leaves one route, and it follows from
constraint 1 instead of fighting it: both wheels need diagonals the
arithmetic families cannot reach (two exhaustive demonstrations —
plain Vigenere shifts and the arithmetic σ families; the keyword
families are NOT excluded, and in fact supply the one enumerable
candidate set, `mixed-alphabet-vigenere.md`). A designer wiring a
permutation against digraph statistics uses a **procedure**: process
the runes in some canonical order assigning each its rarest available
partner, take the assignment-problem optimum on a published bigram
table, route grid columns through rare digraphs, and so on. The
permutations number ~1e48; the plausible *procedures* number in the
dozens — and one procedure family is already enumerated, the keyword
Quagmire pairs (~10⁶ alphabet pairs before schedules). The enumerable
object is the construction rule, not the key — the one search the
evidence has actually made smaller, and where the next attack should
go.
- The deterministic-walk structure is the exploitable weakness instead: DJU-BEI
  gave one state-return constraint (`base_1477 = base_2926`; the
  once-quoted abelianization corollary `[g] = −1449[σ]` is vacuous for
  real ⟨g,σ⟩ — `repeated-phrase-dju-bei.md`);
  a systematic hunt for repeated ciphertext structures could add more equations
  on `(g, σ)` — a collision/constraint attack that uses the determinism the
  hillclimb ignores.

## Related

- `length-clocked-walk.md` — the candidate model and its key (plausible,
  not confirmed).
- `repeated-phrase-dju-bei.md` — the one known state-return constraint.
- `experiments/length_clocked_cipher.py` — encrypt/decrypt + round-trip.
