# The Cipher: A Length-Clocked Progressive Substitution (g per letter, σ per space)

## Claim

The unsolved Liber Primus ciphertext (sections 0-9 of `data/page0-58.txt`) is a
**progressive polyalphabetic substitution with a small fixed key**, not a
per-word one-time pad. The alphabet advances by a fixed **order-5 mixed
permutation `g`** on every letter, and by a second fixed **mixed permutation
`σ`** at every word boundary. Per word `w`, at within-word position `j`:

```
c[j] = base_w( g^(j mod 5)( p[j] ) )
base_{w+1} = base_w ∘ g^((L_w − 1) mod 5) ∘ σ      (L_w = length of word w)
```

The sequence of per-word bases is generated **deterministically** from the key
`(base_0, g, σ)` and the **public word-length sequence** — the word lengths are
visible in the ciphertext, so they are not secret. Total key: two mixed
29-permutations (one of order 5), **fixed, ~200 bits, not growing with the
text.** This is the load-bearing correction to the earlier `free base →
unbreakable` reading: the base is a keyed generator, so the cipher is breakable
in principle.

## Status

**Status**: plausible (comprehensive statistical fit; NOT confirmed by
decryption)

The model reproduces every hard observable and survives an exhaustive battery
of null tests (below). It has **not** been verified by producing plaintext —
the two mixed permutations have not been recovered. Confidence is high on the
*shape* (period-5 mixed substitution + per-word mixed step, small fixed key),
lower on details flagged under "open".

## Mechanism

Two independent "clocks", forced to be independent (see "single permutation
refuted"):

- **`g` — the letter step.** Order 5 (`g⁵ = id`), a rich mixed permutation
  (~five 5-cycles + fixed points), tuned **rare-diagonal**: `g(y)` is a rune
  that rarely precedes `y` in plaintext, so the within-word doublet
  (`c[i]=c[i-1] ⟺ p[i-1]=g(p[i])`) is held to 0.0063. `g⁵=id` makes positions
  5 apart share the alphabet → the d5 echo. Non-arithmetic: GF(29)* has order
  28 and 5∤28, so no shift/multiply/affine map has order 5.
  **The tuned diagonal can be removed** — reformulate as advance-4/hold-1
  (`g4⁴=id`), where the hold exposes 1/5 of plaintext doublets, so the doublet
  rate = plaintext-doublet/5 is *inherent*, and the whole d1-d5 profile falls
  out of one minimized advance. See `stay-slot-hold.md`.
- **`σ` — the space step.** A second mixed permutation **outside ⟨g⟩** (not a
  power of `g`), tuned rare-diagonal so the seam doublet is suppressed to
  0.0079. Being outside ⟨g⟩ is what breaks the walk out of the 5-alphabet
  cyclic cage and gives flat unigrams + aperiodicity.

The `g^((L−1) mod 5)` factor in the transition completes the period-5 cycle at
the boundary, so the letter-clock effectively runs continuously across the
space; that is why doublet suppression is boundary-blind. Note the
period-5-vs-continuous framing is a **reparametrization** (fold `g^(word_start
mod 5)` into the base), so "does the phase reset per word?" is not observable.

## Evidence for

Clean corpus: sections 0-9, 12,956 runes, words tokenized on `- . & %`; `/` and
newlines are line wraps (words flow across them).

- **Flat unigrams (IoC 1.00).** The non-abelian walk ⟨g,σ⟩ visits many
  alphabets → uniform marginal.
- **Doublet suppression, boundary-blind.** Within-word 0.0063, seam 0.0079 (not
  significantly different, z=+0.87). Plaintext d1 is itself flat (real prose
  IoC ~1.0), so the ~5× suppression is entirely cipher-induced — the g/σ
  rare-diagonals. It is sub-maximal (an order-5 g could reach ~0), i.e. a
  "mildly rare" wiring.
- **Period-5 confirmed twice.** d5 echo (elevated coincidence, IoC 1.43,
  +3.7σ above flat) AND d6 suppression (the phase-1 image of d1: `g⁶ = g¹`
  under period 5; permutation null p=0.016). d6 pins the period at exactly 5,
  independent of the fragile d10 (2/88 pairs).
- **Empty d2/d3/d4 (~chance).** `g²/g³/g⁴` diagonals sit at chance.
- **No periodicity.** No Kasiski, no periodic-IoC (periods ≤600), no period in
  absolute rune position (k≤40) or word index (k≤49, incl divisors of 1449).
  Consistent: the walk is clocked by aperiodic word lengths.
- **Not a rotor machine.** A physical wheel stepping 1/letter reuses its
  alphabet at the wheel period, but absolute-position coincidence at d=29 is
  flat (IoC 1.01) and d=20–45 averages 1.00 — no wheel-period echo. And period-5
  is impossible for a 29-symbol wheel (period is 29 for any step, 29 prime), so
  the d5 echo needs a *designed* order-5 permutation, not a rotation. Plus the
  phase resets at word boundaries, which continuous machine stepping cannot do.
  Enigma/Hebern out; Hagelin/Lorenz are additive (killed by the algebra battery).
  The model is rotor-*structured* (order-5 letter rotor + per-space rotor) but
  not a historical machine — a pencil-and-paper progressive substitution.
- **No algebraic structure anywhere.** Delta, sum, ratio, product, and all 28
  affine multipliers — within-word AND across the seam — are null beyond the
  coincidence. So `g` and `σ` are general mixed permutations, not
  affine/multiplicative/Beaufort. (Two scan "hits", d6-m27 and d5-per-word,
  survived permutation nulls but failed split-half → overfit, not signal.)
- **Single permutation refuted.** Doublet suppression needs a *rich* order-5
  `g` (~25 runes moving); flatness needs a *large-order* generator; one
  permutation on 29 runes can't be both. Forces two independent generators.
- **Base re-key is thorough.** No cross-word d5 echo at any (first-word-length,
  distance) cell; first letters of adjacent words are independent; the word
  boundary is a hard cut of the alphabet.
- **DJU-BEI (`ᛞᛄᚢ·ᛒᛖᛁ`).** A 6-rune, two-word (3+3) refrain that *closes*
  section 9 and recurs mid-section-6. Same ciphertext ⟹ `base_1477 =
  base_2926` — a state return of the deterministic walk. Both words length 3,
  so the step (`g²σ`) matched and the bases stayed synced across both words —
  which a random per-word key could not produce. Yields a key constraint:
  `Σ(L−1)=4946 ≡ 1 (mod 5)` over the interval, so `[g] = −1449·[σ]` in the
  abelianization of ⟨g,σ⟩.

## Evidence against / open

- **Partial-vs-full d5 leak is underpowered.** IoC 1.43 vs full-leak ~1.60;
  point estimate 72% same-alphabet, but the bootstrap CI [1.15,1.72] contains
  full leak. Position decomposition (`within_word_position_decomposition.py`)
  shows the echo is **flat over absolute position** (no intra-word drift), so
  the partial leak is *not* drift — the base is word-locked and the partiality
  is uniform (σ knocking the leak down by a constant factor). See
  `d5-partial-alphabet-leak.md`.
- **Order-5-g vs stay-slot: not separable by the ciphertext.** Direct simulation
  on real runeglish words (`mechanism_discriminator.py`) shows *both* reproduce
  the d5 echo and d1≠d6, and the d1..d6 fit winner flips with the g-tuning seed.
  (d1≠d6 does NOT favour stay-slot — an earlier note claimed pure order-5-g
  forces d1=d6; wrong, since the g-diagonal acts on distance-6 skip-grams at d6,
  not adjacent bigrams.) Stable leans only: stay-slot gives d1=plaintext-doublet/5
  parameter-free; order-5-g brackets d6 better. What's real beyond period-5 is the
  **damped rising shoulder** — LP's d2→d5 tracks a half-damped copy of the
  plaintext's own within-word profile with extra phase-1 suppression, i.e. a
  partial plaintext leak under the period-5 envelope. See
  `d5-partial-alphabet-leak.md`.
- **Continuous-vs-per-section walk: weak.** Page-seam doublets 0/47 favour
  "continuous" ~3.4:1; DJU-BEI's differing section-offsets argue against
  per-section reset. But only 9 section boundaries — not provable.
- **`σ`: one or a small keyed set?** Seam suppression proves the space step is
  a rare-diagonal permutation (not a random re-key) but does not prove there is
  only *one* `σ`. A small keyed family fits equally; the fully-deterministic
  single-`σ` version is the simplest, not the confirmed, form.
- **Not confirmed by decryption.** All of the above is statistical shape.

## Predictions

- The key `(base_0, g, σ)` is small and fixed; decryption is a deterministic
  function of it and the observable word lengths. A **contiguous crib** of a
  few words would pin `g` and `σ` and then propagate to the whole corpus —
  unlike a free-base model, where a crib dies at its own word.
- Any candidate key must satisfy the DJU-BEI abelianization constraint above.
- A single guessed word (e.g. DJU-BEI = a [3,3] phrase such as "OUR OWN") is
  **not** verifiable — 6 runes under two unknown bases + g is underdetermined.

## Scripts

- `experiments/phase_absorbing_walk.py` — the model: `base_{w+1} = base_w ∘
  g^((len−1) mod5) ∘ σ`, hits the full battery.
- `experiments/final_orbit_walk.py` — rate-targeted variant.
- `experiments/within_word_phase_profile.py` — d1-d10 permutation null (d5
  echo p=0.001, d6 suppression p=0.016).
- `experiments/d5_partial_leak.py` — the partial-leak measurement and its
  underpowered CI.
- `experiments/stay_slot_cipher.py` — plaintext generator, cipher batteries,
  permutation tooling.

## Related

- `per-word-related-alphabets.md` — the predecessor model; this note supersedes
  its "free per-word base" pessimism with the length-clocked deterministic walk.
- `d5-partial-alphabet-leak.md`, `within-word-d5-coincidence.md`,
  `rune-s-lag5-echo.md` — the d5/d6 structure.
- `repeated-phrase-dju-bei.md`, `cryptodiagnostics-page0-58.md` — DJU-BEI and
  the full diagnostic battery.

## Verdict

The mechanism is characterized: a **length-clocked progressive substitution** —
step `g` (order-5 mixed) per letter, step `σ` (mixed, outside ⟨g⟩) per space,
base = the running product clocked by the public word lengths. Both steps are
non-arithmetic mixed permutations, which would be a first for Cicada and
explains why value-based attacks fail. The key is **small and fixed**, so the
cipher is breakable in principle — but the barrier is recovering two mixed
29-permutations, against which every statistical and algebraic shortcut is
null. The realistic paths to plaintext are a length-clocked hillclimb on
`(base_0, g, σ)` or a contiguous crib; a short guessed phrase alone cannot
verify. Everything here is statistical shape, not a confirmed decryption.
