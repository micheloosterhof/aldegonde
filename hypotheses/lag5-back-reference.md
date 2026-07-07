# Hypothesis: Lag-5 Events are Opportunistic Plaintext Back-References

## Claim

The image-verified lag-5 copy events (`lag5-digraph-structure.md`) are not
produced by the cipher's per-rune mechanics. They are deliberate
back-references: the encoder, upon reaching a place where the PLAINTEXT
repeats itself at distance 5 (a digraph repeat, or a first/last-of-5 frame
repeat), sometimes encodes that repetition by copying the ciphertext from 5
positions back instead of encrypting normally.

## Status

**Status**: plausible (upgraded July 2026: two out-of-construction
ciphertext predictions of copy semantics held while the additive
alternatives failed the same tests — see below; the internal split
nulls / back-references / stutters remains untestable from ciphertext
statistics alone, see the degrees-of-freedom audit)

## Mechanism

Information theory forces this shape: a deterministic ciphertext copy
carries zero fresh information, so the plaintext at copied positions must
come from somewhere. The candidates:

- (a) the copied runes are NULLS (inserted padding the decryptor skips);
- (b) the key repeated AND the plaintext repeated by coincidence;
- (c) the copy fires only where the plaintext genuinely repeats at lag 5 —
  the repetition IS the information (LZ-style back-reference), equivalently
  the key is reused exactly where reuse costs nothing.

Decryption under (c): the receiver decrypts normally; on recognizing the
echo pattern (paired lag-5 ciphertext repeat) they emit the plaintext from
5 back. Accidental echo patterns (~15 of each type expected by chance)
either cause ~0.5% tolerable corruption, or are suppressed by the encoder
(the same output-watching machinery as doublet avoidance), with identical
observable statistics at higher marking rates.

## Degrees-of-freedom audit (read before the evidence)

The "full-fingerprint match" below is weaker than it looks. The model has
three fitted parameters (doublet acceptance probability, u1, u4) and the
fingerprint contains effectively three independent numbers (doublet rate,
d1, d4). Everything else follows automatically: nIoC = 1.000 and flat
split tests come free with ANY OTP-based construction; ~0 triplets follows
from doublet avoidance; mono kappa-5 and T5z are arithmetic consequences
of the d1/d4 counts; d2/d3 are at chance in model and data alike. Three
knobs fitting three numbers is a re-parameterization of the observations,
not a confirmed mechanism.

The model's distinguishing claims — plaintext repeats at the event
positions, section 4 is repetitive text — are unobservable without a
decryption. It therefore forbids nothing measurable from the ciphertext,
and it cannot currently be distinguished from the nulls variant (a) or
from author-side copy-paste artifacts during page composition. Its honest
content is: (i) the information-theoretic trichotomy (nulls /
key+plaintext coincidence / plaintext-repeat marking) is exhaustive for
deterministic copies, and coincidence is disfavored by the mono kappa-5
rate check; (ii) IF assumed, it supplies conditional constraints
(P[i] = P[i-5] at events) usable to prune key searches — conclusions from
such searches are conditional on this unverified assumption.

## Out-of-construction predictions that held (July 2026)

Two ciphertext-observable consequences of copy semantics — neither used
when the model was built — were tested and held, while the additive
alternatives failed the same tests:

1. **Value-literality**: copies predict that only exact glyph equality is
   special. Repeated *nonzero* lag-5 deltas at separations 1/4 are at
   chance (z = +0.21 / -0.14) while zero-value pairs stand at
   z = +3.3 / +3.1 (`experiments/delta5_generalization.py`). Any additive
   drift mechanism would elevate all delta values equally.
2. **No plaintext-difference leak**: copies predict the within-word d=5
   delta histogram is flat off zero; key sharing predicts the plaintext
   difference distribution leaks at f ~= 0.55. The histogram is flat off
   zero; pinned key-sharing is rejected at z = +3.6 and the one-parameter
   copy model wins by 6.4 nats (`within-word-key-sharing.md`, disproved).

New constraint the model must absorb: **the copy rule is word-scoped.**
Plaintext lag-5 repeats occur at ~6.1% both within and across words (the
rate is just the runeglish IoC — measured on Cicada's own solved sections
and a frequency-weighted lexicon), yet cross-word ciphertext pairs match
at exactly 1/29. Under branch (c) the encoder only marks repeats whose
endpoints share a word (natural for a human working word-by-word); under
branch (a) the null-insertion rule respects word units. Purely positional
copy semantics blind to words is now excluded.

## Evidence for

- **Feasible rates**: Markov runeglish has ~78 d1 opportunities and ~46 d4
  opportunities per corpus length; observed events are 29 and 28 — usage
  fractions 0.18-0.37 and 0.28-0.62 depending on accidental accounting.
- **Full-fingerprint simulation match** (`experiments/backref_model.py`) —
  the FIRST mechanism in the program to fit everything simultaneously:
  doublets 0.666+/-0.046% (LP 0.664), triplets ~0 (LP 0), nIoC 1.000
  (LP 1.000), mono kappa-5 1.101+/-0.029 (LP 1.073), d1 30.8+/-4.5 (LP 29),
  d2 19.6+/-7.6 (LP 15), d3 18.5+/-4.0 (LP 14), d4 33.0+/-2.9 (LP 28),
  T5z +5.9+/-1.1 (LP +4.7). All within ~1.1 sigma; no other tested
  mechanism produces the selective d1/d4 shape at all.
- **Explains the inexplicable selectivity**: separations 1 and 4 are not a
  mechanical resonance but a design choice of two escape codes (digraph,
  frame). d2/d3/d5 stay at chance because nothing marks them.
- **Explains every negative result**: events ignore word/sentence/page
  boundaries and the doublet grid (plaintext repetition does not care);
  no algebraic relation inside events (the copies are literal); the
  mono lag-5 excess lives entirely inside pairs.
- **Explains the section-4 concentration as content**: more lag-5
  plaintext repetition there — repetitive, chant-like text. A testable
  content inference.

## Evidence against

- Model (b) — pure coincidence via key reuse — needs ~18% key-pair reuse,
  predicting mono kappa-5 ~ 1.14 vs observed 1.073 (~2 sigma strain); as
  of July 2026 it is additionally excluded by the delta-histogram test
  (key reuse leaks the plaintext difference distribution; rejected at
  z = +3.6, see `within-word-key-sharing.md`). The (a)-nulls variant
  remains statistically indistinguishable from (c).
- The motive for marking is unclear: key economy saves only ~114 key runes
  (~1%); alternatives are a designed breadcrumb or an LZ-flavored encoding
  aesthetic. The constant 5 is a designer choice here, separate from the
  doublet machinery's 5 (see `cotiling_test.py`).
- Post-hoc: the model was constructed to explain the anomaly. Its
  independent support is the rate feasibility, the information-theoretic
  necessity of its shape, and the full-fingerprint fit.

## Word-scoped simulation and copy budget (July 2026)

`experiments/word_scoped_copy_simulator.py` layers literal copies on the
established base process (doublet-suppressed uniform stream cut into the
REAL word-length sequence): single / digraph / frame copies with separate
word-internal and boundary-crossing rates. Five rates are calibrated by
moment matching (d1, d4, paired-within, isolated-within, mono total);
twelve further statistics are emergent, and all agree with the LP within
Monte Carlo noise (|z| <= 1.8 across the full table, including the
paired/isolated x within/across decomposition, separations 2-8, the
off-zero delta histogram, doublets and triplets). The calibrated copy
budget is small and specific:

    ~8  in-word digraph copies   (the XY···XY words)
    ~4  cross-word digraph copies
    ~12 frame copies             (the d4 events; span 10, mostly cross-word)
    ~15 in-word single copies
    ==> ~39 events, ~66 copied glyphs in 12,956 runes (~0.5%)

Two honest residuals: the LP's isolated-across count is mildly below the
model (z = -1.4, noise-compatible), and the model does not produce the
within-word d=6 deficit hint (LP 31 vs model 42.9 ± 6.6; see
`within-word-d5-coincidence.md`) — if that deficit is real it is beyond
copy semantics. Degrees-of-freedom caveat: five calibrated rates is five;
the test content lives in the twelve emergent statistics.

The complete event coordinates (479 matches classified paired/isolated x
within/across, the 29 d1 and 28 d4 events, the 86 doublets) are frozen in
`hypotheses/lag5-event-catalog.json`
(`experiments/lag5_event_catalog.py`) for direct consumption by key
searches: under branch (c) each event supplies P[i] = P[i-5]; under
branch (a) the copied glyph is skipped and consumes no key symbol.

## Shape census: what is marked, what plaintext offers, and what is absent
## (July 2026)

`experiments/copy_shape_census.py` measures every composite lag-5 match
shape in the LP against (i) chance and (ii) its plaintext availability
(frequency-weighted runeglish lexicon, per within-word window):

| shape | LP in-word | chance | plaintext offers | reading |
|---|---|---|---|---|
| digram `XY···XY` (sep 1) | 9 | 1.5 | 6.9 | marked at ~100% of opportunities (excess 7.5 vs available 5.4; Poisson-compatible) |
| gapped `X·Y··X·Y` (sep 2) | 2 | 0.9 | 3.0 | UNMARKED (stream level 15 vs chance 15.4) |
| gapped `X··Y·X··Y` (sep 3) | 1 | 0.4 | 1.8 | UNMARKED (stream level 14 vs 15.4) |
| frame `X···Y X···Y` (sep 4) | 1 | 0.2 | 0.6 | marked, but lives cross-word (28 events; span 10 rarely fits a word) |
| trigram `XYZ··XYZ` | 1 | 0.03 | 0.7 | exactly the ~1.3 predicted by digram usage x availability (the page-50 SDNG event) |
| tetragram / double-digram `XY·AB XY·AB` | 0 | ~0 | ~0.000 | absent exactly where English offers nothing |

Three structural conclusions:

1. **The copy unit is a contiguous chunk.** Plaintext offers gapped
   repeats at rates comparable to contiguous ones, but only contiguous
   digrams (and singles) are marked. Per-position repeat marking
   (mark every i with P[i] = P[i-5] independently) is excluded — it
   would light up separations 2 and 3 pro-rata. This answers "why
   separations {1,4} and not {2,3}".
2. **Pairs-not-triplets is pure availability.** English offers trigram
   repeats at 0.18x the digram rate; the LP ratio is 1:9 = 0.11, and the
   single observed trigram matches the 1.3 predicted. Nothing is missing.
3. **The frame is a true bracket.** The three interior positions of the
   28 d4 events match at exactly chance (3 vs 2.9): the frame marks the
   5-window's edges only — either a second escape code ("this 5-frame
   repeats") or brackets around a unit; it is NOT a fully copied 5-gram.
   5 of 28 d4 events share a match with a d1 event (the page-50 cluster
   family).

Usage fractions under branch (c): in-word digrams ~100% (every in-word
plaintext digram repeat got marked), in-word singles ~55%, frames ~30%.
The digram overshoot (9 observed vs 6.9 available, i.e. nominal usage
1.4) is within Poisson noise of 100% but is the one number that would,
with more data, discriminate stutters/nulls (no opportunity ceiling)
from plaintext-repeat marking (hard ceiling at availability).

**Parity/phase (same script):** d1 events, d4 events, and all 479
matches are flat mod 2 AND mod 5 measured from all four origins (text,
section, page, word start) against the opportunity distribution (all
p >= 0.11). There is no digraph-pair encryption grid and no positional
frame — complementing the earlier fractionation/Playfair exclusions at
the event level.

## The nulls-branch key search (battery 19, negative)

If branch (a) is true AND the underlying keystream is simple, all earlier
keystream sweeps missed it, because a null consumes no key symbol and the
sweeps assumed one-key-per-rune alignment. `experiments/lp_battery19.py`
closes this: decryption with catalog-driven deletion (skip the copy
targets of the 29 d1 + 28 d4 events, or of all 479 matches; key advances
only on real glyphs), 13 streams (primes, totient, index, triangular,
Fibonacci, Lucas, pi, e, 2^i, squares, cubes, prime gaps, cycled
gematria values) x both signs, corpus-wide, per-page restart and
per-$-section restart, plus the full battery-14-style per-page offset
brute force (offsets 0..24999, 33M trials) in both deletion modes.
Result: nothing — per-page restart max z = +3.98 (threshold ~4.5),
per-section max +2.88 (threshold ~4.2); offset-search max in deletion
modes +4.53 (noise ceiling ~5.5 for the family; the global max +5.53 is
the known page-42 battery-14 noise hit, reproduced in the no-deletion
mode, which cross-validates the reimplementation). So EITHER the copies
are not nulls, OR the base keystream is not any of the standard
sequences at any per-page offset — the nulls branch survives only in
combination with a strong (OTP-grade) base stream, which it already
required for every other statistic.

## Predictions

- **114 free cribs**: at each verified event, the plaintext satisfies
  P[i] = P[i-5] (and partner). Any future decryption attempt must honor
  these deterministic constraints; conversely they prune key searches.
- Section 4's plaintext is the most lag-5-repetitive in the book.
- If the encoder suppresses accidental echoes, accidental-looking events
  are absent: ALL observed events decode as genuine plaintext repeats.
- No other lag should ever show this structure (designer chose 5): already
  consistent with the lag spectrum.

## Scripts

- `experiments/backref_model.py` — rates and full-fingerprint simulation.

## Related

- `lag5-digraph-structure.md` — the structure being explained.
- `transcription-verification.md` — the events are in Cicada's ink.
- `five-block-boundary.md` — the doublet machinery, now decoupled.
- `stream-cipher-no-repeat.md` — the avoidance layer this composes with.

## Verdict

Plausible — upgraded from unresolved. The original audit demanded "a
ciphertext-observable prediction that was not used in its construction";
July 2026 delivered two (value-literality of the pairing; a flat-off-zero
within-word delta histogram), both held, while the additive readings of
the same data (local key drift, within-word key sharing, coincidence via
key reuse) were rejected at 3.1-3.6 sigma by the identical tests. The
copy-semantics *family* is now the only surviving explanation of the
lag-5 phenomenon, with one new constraint: the rule is word-scoped
(cross-word plaintext repeats are never marked). What has NOT advanced:
the internal trichotomy — nulls (a) vs plaintext-repeat back-references
(c) vs author-side stutters — is still indistinguishable from ciphertext
statistics, and confirmation still requires a key search conditioned on
the P[i] = P[i-5] constraints producing readable text.
