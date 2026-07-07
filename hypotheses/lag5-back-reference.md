# Hypothesis: Lag-5 Events are Opportunistic Plaintext Back-References

## Claim

The image-verified lag-5 copy events (`lag5-digraph-structure.md`) are not
produced by the cipher's per-rune mechanics. They are deliberate
back-references: the encoder, upon reaching a place where the PLAINTEXT
repeats itself at distance 5 (a digraph repeat, or a first/last-of-5 frame
repeat), sometimes encodes that repetition by copying the ciphertext from 5
positions back instead of encrypting normally.

## Status

**Status**: unresolved (unfalsifiable from ciphertext statistics alone —
see the degrees-of-freedom audit below)

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
  predicting mono kappa-5 ~ 1.14 vs observed 1.073 (~2 sigma strain);
  disfavored but the (a)-nulls variant is statistically indistinguishable
  from (c) and remains open.
- The motive for marking is unclear: key economy saves only ~114 key runes
  (~1%); alternatives are a designed breadcrumb or an LZ-flavored encoding
  aesthetic. The constant 5 is a designer choice here, separate from the
  doublet machinery's 5 (see `cotiling_test.py`).
- Post-hoc: the model was constructed to explain the anomaly. Its
  independent support is the rate feasibility, the information-theoretic
  necessity of its shape, and the full-fingerprint fit.

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

Unresolved, and honestly: a consistent re-description rather than a tested
mechanism. Its simulation "match" spends three fitted parameters on the
three independent fingerprint numbers (see the audit above), and its
distinguishing claims are unobservable without a decryption. What survives
scrutiny: the information-theoretic trichotomy for deterministic copies is
sound, the coincidence branch is rate-disfavored, and the opportunity-rate
feasibility check passed (it could have failed: had runeglish offered
fewer than 29 digraph-repeat opportunities, the model would be dead). The
model earns no status beyond that until it makes a ciphertext-observable
prediction that was not used in its construction — or until a key search
conditioned on its P[i] = P[i-5] constraints produces readable text, which
would be the only real confirmation.
