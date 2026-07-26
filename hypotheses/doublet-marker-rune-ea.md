---
type: hypothesis
---
# Hypothesis: The Doublet Marker Rune is EA

## Claim

**IF** each ciphertext doublet (`C[i] == C[i+1]`) marks a position where one
fixed plaintext rune occurs, **THEN** that rune is **EA (ᛠ)** — the least-refuted
candidate, with F, NG, and IO excluded. The premise itself is unproven.

## Status

**Status**: disproved (positional-profile test, July 2026 — even granting
the marker premise, EA and every frequency-band candidate fail; see below)

The load-bearing premise — that doublets mark a single fixed plaintext rune at
all — was never established, and is undercut: the mechanism that would naturally
imply it (ciphertext autokey) is disproved (see Evidence against). EA was the
project's starting assumption, not a finding. The July 2026 direction test
(`experiments/ea_direction_test.py`) settles the conditional claim negatively:
in word-bounded runeglish prose EA is 90% medial / 8% initial / 2% final, while
BOTH doublet runes sit on the all-rune positional baseline (p = 0.16 / 0.54
vs baseline; chi2 = 225-275, p < 1e-48 vs the EA profile). NG (74% final)
and IO (100% medial) fail the same way. No rune in the 0.4-1.0% frequency
band has a baseline-flat profile, so the single-fixed-rune marker class is
refuted on position alone — and the observed flatness is exactly what a
content-uncorrelated KEY event predicts.

## Mechanism

This is not a cipher mechanism — it is a constraint on the plaintext that holds
for any cipher in which doublets mark a single fixed rune. That class includes
ciphertext autokey (where `C[i]=C[i+1]` forces the **2nd** rune to the additive
identity) and its reverse-direction and inner-layer variants. The marker rune
can be the **1st or 2nd** rune of the doublet depending on keystream direction;
the frequency argument below does not distinguish the two, only the rune.

Two filters narrow the candidate *given the premise*. Neither is positive
evidence for the premise; both only test which rune survives if the premise is
granted.

## Consistency checks (conditional on the premise)

**Frequency filter.** The doublet rate is 0.664% (86 / 12,956 clean; the
pre-decontamination figures below used 89 / 13,136 = 0.678%). If each doublet
marks one fixed plaintext rune, that rune's runeglish frequency must match.
From `src/aldegonde/data/ngrams/runeglish/unigrams.txt`, only three runes fall
in the 0.4-1.0% band:

| rune | name | runeglish freq | predicted doublet rate |
|------|------|----------------|------------------------|
| ᛠ | EA | 0.587% | 0.59% (matches 0.68%) |
| ᛝ | NG | 0.826% | 0.83% |
| ᛡ | IA/IO | 0.961% | 0.96% |

F (ᚠ) = 2.566% predicts a 2.57% doublet rate — **refuted** (3.8x too many). This
kills the naive 0-indexed identity (F=0) and every common rune.

**Word-initial filter.** The marker rune demonstrably appears at the start of a
word: 23 times as the 2nd rune of a doublet (the cross-word doublets), 12 times
as the 1st rune (clean corpus). Either count is fatal to candidates that cannot
begin a word:

- **NG** never starts an English/runeglish word. Predicts ~0 word-initial.
  Refuted.
- **IO** appears word-initially only in rare cases (ion, iota); in runeglish it
  is overwhelmingly the medial "-ION" cluster. Predicts ~0 word-initial.
  Refuted.
- **EA** starts each, ear, early, earth, east, eat... and also goes medial
  (great, dream) and final (sea, idea). Survives.

EA is the unique intersection of both filters — but only the closest of a band,
and the frequency match is loose (15% off, against a generic corpus). NG is fine
on frequency alone and is excluded only by the premise-dependent word-initial
argument.

**Positional neutrality — first read as consistent, later fatal.** The 2nd
rune's word-position distribution (start 23 / middle 44 / end 19, clean
corpus) is statistically indistinguishable from the all-rune baseline
(21.8 / 55.6 / 21.8%): chi-square 1.25, p ≈ 0.54. This was originally read
as "a positionally-flexible digraph like EA fits" — but flexible is not the
same as baseline-flat: measured on word-bounded prose, EA's actual profile
is 90% medial, and the July 2026 profile test below turns this observation
into the refutation.

**Suppression is uniform across word boundaries.** 63 within-word doublets, 23
cross-word (22 across `-`, 1 across `.`, none across segment/page/number-page
gaps; clean corpus). Cross-word count 23 vs 19.4 expected from opportunity —
not suppressed.
This points to a continuous running mechanism that ignores word spacing, and
argues against word-boundary-reset autokey (see `word-boundary-reset-autokey.md`).

## Evidence against

- The frequency match is to a generic runeglish corpus, not the LP plaintext;
  observed 0.68% vs EA's 0.59% is a 0.09-point excess (about 12 doublets). Within
  text-to-text variation, but not exact.
- Pure ciphertext autokey — the most natural mechanism that produces a fixed
  identity rune — is itself disproved by the preceding-rune split test
  (`beaufort-autokey-ea.md`, `ciphertext-autokey.md`). So the EA-marker
  constraint must be carried by a different mechanism (e.g. autokey plus an
  inner layer), not plain autokey.

## The positional-profile test (July 2026) — the conditional claim fails

The direction test proposed under Predictions was run once the
word-bounded runeglish prose corpus existed
(`experiments/ea_direction_test.py`, Gutenberg #1342, 127k word tokens,
537k runes, token-weighted, same digraph rules as the d5 full-leak
reference; EA frequency there 0.611%, confirming the band):

| | start | middle | end |
|---|---|---|---|
| EA profile (prose) | 7.9% | 90.0% | 2.0% |
| NG profile (prose) | 0.0% | 26.2% | 73.8% |
| IO profile (prose) | 0.0% | 100.0% | 0.0% |
| LP 1st rune of doublet (86) | 12 | 51 | 23 |
| LP 2nd rune of doublet (86) | 23 | 44 | 19 |
| all-rune baseline | 21.8% | 55.6% | 21.8% |

Both doublet-rune splits match the all-rune baseline (chi2 = 3.6 / 1.25,
p = 0.16 / 0.54) and reject the EA profile at chi2 = 275 / 225
(p < 1e-48). Under the marker premise, the marked rune's word positions
ARE the plaintext rune's word positions — so a 90%-medial rune cannot
produce a baseline-flat split with 19-23 word-final doublets where EA
predicts ~2. NG and IO fail identically in other directions. No rune in
the frequency band is baseline-flat, so this refutes the entire
single-fixed-rune marker class, not merely EA, and it decides the
original question by dissolving it: neither direction matches because no
rune matches. What the flat split DOES fit is a trigger uncorrelated
with plaintext content — a rare key event.

## Scripts

- `experiments/doublet_word_position.py` — word-position analysis plus the
  frequency and word-initial filters. Reproduces every number above.
- `experiments/ea_direction_test.py` — the positional-profile test
  (prose EA/NG/IO profiles vs the doublet-rune splits).

## Related

- `beaufort-autokey-ea.md` — EA identity under ciphertext autokey (disproved as
  a full mechanism; the mechanism-independent EA constraint falls too — the
  positional-profile test here refutes the whole marker class).
- `ciphertext-autokey.md` — general ciphertext autokey, same disproof.
- `autokey-plus-substitution.md` — a mechanism that could have carried the
  EA marker; the marker class it would carry is refuted here.
- `position-within-word.md`, `word-boundary-reset-autokey.md` — word-structure
  hypotheses tested here.

## Insertion (chaff/null) alternative — tested, disfavored (June 2026)

The strongest premise-free alternative to any marker reading: the true
cipher stream NEVER repeats a rune (strict GF(29)* closure) and the
doublets are deliberately inserted dittographs — removable chaff with the
receiver rule "collapse any doublet". This fits the Poisson positions,
uniform doubled-rune identities, and structureless context just as well
as a marker does.

Discriminator: an INSERTION inflates its host word by one rune; a marker
(an event occupying a plaintext position) does not. Observed mean length
of the 62 words containing the 63 within-word doublets: **5.97 +- 0.32**
(clean corpus).

- occupying-event (marker-class) prediction: 5.63 -> z = +1.1, p = 0.29
- insertion prediction: 6.63 -> z = -2.1, **p = 0.037**

The insertion/chaff model is disfavored at ~2 sigma; the doublets behave
like events that occupy plaintext positions
(`experiments/doublet_insertion_test.py`).

## Ciphertext-conditioned triggers — tested, excluded (June 2026)

Generalizing further: could the trigger involve a CIPHERTEXT condition —
a pair of ciphertext runes, or one ciphertext rune plus one plaintext
rune (`experiments/doublet_context_test.py`)?

- **Mixed trigger P[i+1] = g(C[i]) with bijective g**: excluded by rate
  alone (predicts 1/29 = 3.45% vs observed 0.675%).
- **Trigger forcing the doubled value into a subset** (e.g. doublet fires
  only when C[i] = x and the incoming plaintext is some common letter):
  excluded by the uniform doubled-rune identities (chi2 p=0.50, spread
  over 28 of 29 values).
- **Trigger conditioned on nearby ciphertext runes**: identity
  distributions of C[i-2], C[i-1], C[i+2], C[i+3] at the 86 doublets are
  all uniform (p = 0.30-0.72; detects condition sets up to ~15 runes).
- **Trigger = small set of ciphertext pairs**: pair-collision counts
  among the doublet contexts at all tested offset combinations are at
  chance (3-5 collisions vs 4.6 expected; a 6-pair trigger set would
  give ~600).

What survives is exactly the class with NO small ciphertext-visible
condition: a rare plaintext event (rune or bigram), a context-dependent
marker g(C) whose range is rare letters with a LARGE ciphertext domain
(observationally identical to the plain marker), or a rare key event.
From the ciphertext alone these remain indistinguishable.

## Verdict

Disproved. The July 2026 positional-profile test refutes the conditional
claim on its own terms: granting the marker premise, the marked rune's
word-position split must follow that rune's plaintext profile, and both
doublet-rune splits instead follow the all-rune baseline — incompatible
with EA (90% medial, p < 1e-48) and with every other rune in the
0.4-1.0% frequency band (NG 74% final, IO 100% medial). The frequency
filter's survivors all die on position.

What survives is the interpretation the flat split actually predicts:
(b) a rare KEY event (e.g. the keystream step hitting a forbidden value
~0.7% of the time), or a rare plaintext-BIGRAM class only if its mixture
happens to be positionally baseline — a much narrower remnant than
before. The companion doublet-pair profile test
(`experiments/doublet_position_profile.py`) closes one more cell of the
same grid: plaintext DOUBLE LETTERS specifically are excluded (they are
start-forbidden and end-heavy; the doublets are flat), which also
disproves the stay-slot hold reading (`stay-slot-hold.md`). The earlier narrowing stands: deliberate chaff/dittograph
insertion is disfavored at ~2 sigma (June 2026 insertion test), and no
small ciphertext-visible condition exists. Doublet spacing is
content-driven Poisson (`doublet-spacing-poisson.md`), consistent with a
key-event trigger.
