## Index

Files are tagged `type:` in frontmatter. Observations are measured features
(each with an `experiments/` script reproducing its significance); hypotheses are
proposed mechanisms scored against them.

### Observations (34)

| File | Feature | Status |
|---|---|---|
| [aligned-kappa-no-reset.md](aligned-kappa-no-reset.md) | No Shared Keystream Reset at Page or Section Boundaries | confirmed (characterization) |
| [bigram-ioc.md](bigram-ioc.md) | Off-Diagonal Bigrams are Uniform | confirmed (characterization) |
| [collision-hunt-single-constraint.md](collision-hunt-single-constraint.md) | The Ciphertext Yields One Cross-Word Constraint (DJU-BEI); the Wiring is Starved | confirmed (characterization) for the repeat census itself |
| [cross-product-sum-flat.md](cross-product-sum-flat.md) | Bauer's Cross-Product Sum Finds Nothing (Flat Unigrams Make It Blind) | confirmed (characterization), negative at every window 29-2000; sections homogeneous (chi2 p=0.90) |
| [cryptodiagnostics-page0-58.md](cryptodiagnostics-page0-58.md) | Full Cryptodiagnostic Battery on page0-58.txt (2026-06) | confirmed (characterization) |
| [d5-partial-alphabet-leak.md](d5-partial-alphabet-leak.md) | The d5 Echo is a Same-Alphabet Leak (order-5 g confirmed; phi5 still open) | partial (Aug 2026): d3/d4 controls fall far short of plaintext (z −5.9, −3.7; phi3 = 0.13 +- 0.14 is 6.4 sigma below full leak, phi4 = 0.37 +- 0.20 is marginally above chance) while d5 reads plaintext, so one-alphabet-per-word is REFUTED and g has order exactly 5; phi5 itself remains underpowered at 0.64–0.71, convention-dependent |
| [doublet-spacing-poisson.md](doublet-spacing-poisson.md) | Doublet Spacing is Poisson, Not Mathematical | confirmed (characterization) |
| [doublet-suppression.md](doublet-suppression.md) | Doublet Suppression (5.2x, boundary-blind) | confirmed (characterization) |
| [entropy-incompressible.md](entropy-incompressible.md) | Near-Maximal Entropy, Zero Compressible Redundancy | confirmed (characterization) |
| [flat-ioc.md](flat-ioc.md) | Flat Unigram Distribution (IoC = 1/29) | confirmed (characterization) |
| [kappa-spectrum.md](kappa-spectrum.md) | Kappa Anomalous Only at Skip 1 | confirmed (characterization) |
| [key-local-channel-is-empty.md](key-local-channel-is-empty.md) | The Only Key-Local Channel is Empty (why no filter or gradient exists) | confirmed (characterization); isomorph patterns reduce to six per-distance scalars (p=0.36) worth ~4 bits about g, so all information is key-global -- four extraction attempts measured, all consistent |
| [lag11-cross-word-deficit.md](lag11-cross-word-deficit.md) | Distance-11 Coincidence Deficit (Cross-Word, mod-5 Phase) | retired (scan noise; word-length-periodicity mechanism refuted by test F) |
| [lag5-digraph-structure.md](lag5-digraph-structure.md) | Lag-5 Paired-Match Structure | confirmed (characterization) |
| [line-initial-bias.md](line-initial-bias.md) | Line-Initial Rune Bias (layout artifact) | confirmed (characterization) |
| [long-word-structure.md](long-word-structure.md) | Long Words Carry No Structure Beyond the d5 Echo | confirmed (characterization) |
| [mark-glyph-inventory.md](mark-glyph-inventory.md) | The Transcription Collapses Four Mark Glyphs into Two Characters | confirmed (characterization); 1/3/4/10/13-dot glyphs map onto '-' and '.'; the dropped line-initial marks are now RECOVERED (38 in page0-56.txt) |
| [negative-control-battery.md](negative-control-battery.md) | Negative-Control Battery: Which Measurements Survive a Structureless Corpus | confirmed (characterization); family-blind, only the d5 echo survives (p=0.020); lag-5 pairing, seam diagonal and d6 do not |
| [no-known-plaintext-foothold.md](no-known-plaintext-foothold.md) | No Known-Plaintext Foothold; Section 11 is the Only Plaintext Section | confirmed (characterization) for the no-known-plaintext claim |
| [no-periodicity.md](no-periodicity.md) | No Periodic Key (Friedman flat at every period) | confirmed (characterization) |
| [quote-span-boundaries.md](quote-span-boundaries.md) | Quoted Spans Align to the '.' Marks (the Marks Are Not Inert) | confirmed (characterization) for the alignment (p=1.5e-7, layout-robust); what the marks delimit stays open |
| [no-running-key-depth.md](no-running-key-depth.md) | No Running-Key Depth at Any Lag | confirmed (characterization) |
| [pairwise-dependence.md](pairwise-dependence.md) | No Pairwise Dependence Except Lag 1 | confirmed (characterization) |
| [repeated-phrase-dju-bei.md](repeated-phrase-dju-bei.md) | The Repeated Phrase ᛞᛄᚢ-ᛒᛖᛁ (Key-State Recurrence) | confirmed (characterization) |
| [rune-s-lag5-echo.md](rune-s-lag5-echo.md) | The Lag-5 Echo is Carried by the Rune S | confirmed (characterization; p=2.4e-6 vs identity-preserving nulls, expected-level under the walk) |
| [seam-channel-clean.md](seam-channel-clean.md) | The Seam Channel is Clean (Suppressed Diagonal Only) | confirmed (characterization) |
| [transcription-verification.md](transcription-verification.md) | Transcription verification worksheet | confirmed (characterization) |
| [two-rune-deficit.md](two-rune-deficit.md) | The 2-Rune Word Deficit (one bucket, z ≈ −10) | confirmed (characterization) for the deficit, on two independent references with the transliteration convention calibrated; MECHANISM OPEN and not identifiable from word lengths |
| [two-rune-depth-no-base-reuse.md](two-rune-depth-no-base-reuse.md) | Short Words Show No Depth: the Base Essentially Never Repeats | confirmed (characterization); a 29-state schedule excluded at 10^-124 on 3-rune words, enumeration-free and g-free |
| [within-word-d5-coincidence.md](within-word-d5-coincidence.md) | Within-Word Distance-5 Coincidence Excess | plausible (verified anomaly; mechanism unknown) |
| [word-length-keystream-and-boundaries.md](word-length-keystream-and-boundaries.md) | Word-Length Keystream & Boundary Authenticity | confirmed (characterization) for the keystream disproof and the '.'-semantics; transcription omission now CLOSED so the clock is sound; the short-word deficit is split out to two-rune-deficit.md |
| [word-position-pairs.md](word-position-pairs.md) | Within-Word Position Pairs Carry Distance-Only Structure | confirmed (characterization) |
| [word-transform-census.md](word-transform-census.md) | Word-Level Transform Census (Per-Word Keyed Ciphers Excluded) | confirmed (characterization) |
| [zero-triplets.md](zero-triplets.md) | Zero Triplets | confirmed (characterization) |

### Hypotheses (45)

| File | Mechanism | Status |
|---|---|---|
| [accumulator-autokey.md](accumulator-autokey.md) | Accumulator Autokey (Running Ciphertext Sum) | disproved |
| [affine-autokey.md](affine-autokey.md) | Affine Autokey | disproved |
| [autokey-plus-substitution.md](autokey-plus-substitution.md) | Autokey Outer Layer + Unknown Inner Layer | unresolved |
| [autokey-with-keyword.md](autokey-with-keyword.md) | Autokey with Keyword Interleaving | disproved |
| [beaufort-autokey-ea.md](beaufort-autokey-ea.md) | Beaufort Ciphertext Autokey with 1-Based Indexing (EA Identity) | disproved |
| [bifid-fractionation.md](bifid-fractionation.md) | Bifid or Trifid Fractionation Cipher | disproved |
| [block-cipher.md](block-cipher.md) | Block Cipher / Substitution-Permutation Network | disproved (boundary-blind fixed blocks; five-block edge variant tracked separately) |
| [ciphertext-autokey.md](ciphertext-autokey.md) | Ciphertext Autokey Cipher | disproved |
| [contraction-cribs.md](contraction-cribs.md) | The Apostrophes Mark English Contractions (Four Plaintext Cribs) | plausible (punctuation is genuine: 14 quotes nest into 7 spans, p~1.2e-4 pre-registered; which contraction sits at each of the 4 sites rests on n=4, p=0.028) |
| [doublet-marker-rune-ea.md](doublet-marker-rune-ea.md) | The Doublet Marker Rune is EA | disproved (positional-profile test kills the whole fixed-rune marker band; flat split favors a key event) |
| [encoding-only.md](encoding-only.md) | Runeglish Encoding Alone Explains the Statistics | disproved |
| [explicit-doublet-avoidance.md](explicit-doublet-avoidance.md) | Explicit Doublet Avoidance (Post-Processing) | disproved (deterministic fixes; stochastic re-draw = `stream-cipher-no-repeat.md`) |
| [first-difference.md](first-difference.md) | First-Difference Cipher | disproved |
| [five-block-boundary.md](five-block-boundary.md) | Five-Block Cipher with Edge Effects | unresolved |
| [g-from-5x5-grid.md](g-from-5x5-grid.md) | Constructing the Order-5 Step `g` from a 5×5 Grid | unresolved (construction proposal; arrangement unknown and unverified) |
| [gematria-primus-arithmetic.md](gematria-primus-arithmetic.md) | Autokey with Gematria Primus Arithmetic | disproved |
| [hill-cipher-per-word.md](hill-cipher-per-word.md) | Hill Cipher per Word | disproved (fixed matrices by census; varying matrices by the doublet hyperplane argument) |
| [homophonic-substitution.md](homophonic-substitution.md) | Homophonic Substitution | disproved |
| [lag5-back-reference.md](lag5-back-reference.md) | Lag-5 Events are Opportunistic Plaintext Back-References | unresolved (unfalsifiable from ciphertext statistics alone) |
| [length-clocked-walk.md](length-clocked-walk.md) | The Cipher: A Length-Clocked Progressive Substitution (g per letter, σ per space) | plausible (comprehensive statistical fit; NOT confirmed by decryption) |
| [magic-square-grid-key.md](magic-square-grid-key.md) | `g` From the Book's Own 5×5 Magic Square (constant 3301) | no advantage shown (Aug 2026, corrected): 0 of 190,008 survive the seven distance cuts, against 1.4 expected by chance (3 of 400,000 random order-5 g pass) -- the cuts admit only a TUNED g, so no construction family can pass; the earlier "1 vs 2.4 expected" used tables that were not length-matched |
| [mixed-alphabet-vigenere.md](mixed-alphabet-vigenere.md) | The Period-5 Step is a Mixed-Alphabet (Quagmire) Vigenere | disproved for the keyword family (register caveat) — the full ~3.1e8-key enumeration ran (DJU-BEI 6-point return + 2-rune verifier) and NO keyword key decrypts; not excluded for freely-designed alphabets or an out-of-band register |
| [mixed-cycle-progression.md](mixed-cycle-progression.md) | The Letter Step g Has Mixed Cycle Lengths | unresolved (pure return ladders disproved by monotonicity; census selection below calibration resolution; open cells: d6 suppressed −2.3σ/p=0.016, d4 lean +1.85σ, split ~2.7σ) |
| [monoalphabetic-substitution.md](monoalphabetic-substitution.md) | Monoalphabetic Substitution | disproved |
| [multi-layer-autokey.md](multi-layer-autokey.md) | Multi-Layer Autokey | disproved |
| [page-reset-keystream.md](page-reset-keystream.md) | Shared Positional Keystream Resetting at Page/Section Boundaries | disproved |
| [per-word-related-alphabets.md](per-word-related-alphabets.md) | Per-Word Related-Alphabet Cipher (5 Alphabets, Bigram-Dodging Step) | plausible — superseded by `length-clocked-walk.md` |
| [periodic-polyalphabetic.md](periodic-polyalphabetic.md) | Periodic Polyalphabetic Cipher (Vigenere with Fixed Key) | disproved |
| [plaintext-autokey.md](plaintext-autokey.md) | Plaintext Autokey Cipher | disproved |
| [playfair-variant.md](playfair-variant.md) | Playfair / Seriated Playfair Variant | disproved |
| [position-within-word.md](position-within-word.md) | Position-Within-Word Dependent Cipher | disproved (additive variants; the mixed-alphabet member is the live walk model) |
| [prime-value-autokey.md](prime-value-autokey.md) | Prime-Value Tabula Recta Autokey | disproved |
| [product-form-autokey.md](product-form-autokey.md) | Product-Form / Interpolation Autokey over GF(29) | disproved |
| [running-key-math-sequence.md](running-key-math-sequence.md) | Running Key from Mathematical Sequence | disproved |
| [running-key-text.md](running-key-text.md) | Running Key from Another Text | disproved |
| [second-order-difference.md](second-order-difference.md) | Second-Order Difference Cipher | disproved |
| [sigma-power-step.md](sigma-power-step.md) | The Space Step σ is a Power of g | disproved (all powers and near-powers; census collapse + DJU-BEI arithmetic + periodicity) |
| [stay-slot-hold.md](stay-slot-hold.md) | The Doublet Suppression is Inherent: the 1-in-5 Hold, not a Tuned Diagonal | disproved (doublets are positionally flat, not plaintext-double-shaped; the rate match was a coincidence) |
| [stream-cipher-no-repeat.md](stream-cipher-no-repeat.md) | Additive Stream Cipher with Ciphertext-Doublet Avoidance | unresolved (reformulated; keystream-only variant disproved) |
| [substitution-plus-autokey.md](substitution-plus-autokey.md) | Monoalphabetic Substitution + Autokey Layering | disproved |
| [thirty-symbol-disk.md](thirty-symbol-disk.md) | The '.' Mark is the 30th Character of a 30/29 Cipher Disk | unresolved |
| [transposition.md](transposition.md) | Transposition Cipher | disproved |
| [within-word-key-sharing.md](within-word-key-sharing.md) | Within-Word Distance-5 Key Sharing (Per-Word 5-Periodic Key) | disproved |
| [word-boundary-reset-autokey.md](word-boundary-reset-autokey.md) | Word-Boundary-Reset Autokey | disproved |
| [word-level-autokey.md](word-level-autokey.md) | Word-Level Autokey | disproved |
