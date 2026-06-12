# Liber Primus lag-5 repeat investigation

Analysis of `data/page0-58.txt` (the runic Liber Primus corpus), prompted by
the suspicion of a lag-5 repeat structure. Reproduce everything with
`python examples/lp_lag5_analysis.py`.

## Corpus structure

The file holds 58 pages separated by `%` (lines end in `/`, words are
separated by `-` and `.`). The tail is the known, solved material:

* **Page 57** is plain runeglish, no encryption: *"PARABLE. LIKE THE INSTAR,
  TUNNELING TO THE SURFACE..."*
* **Page 56** decrypts with `plain = cipher - (prime_i - 1) mod 29`, no
  interruptors: *"AN END. WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES
  TO ... IT IS THE DUTY O[F EVE]RY PILGRIM TO SEEK OUT THIS PAGE."* The
  transcription contains one extra rune around index 60; resyncing the prime
  stream by −1 recovers the rest of the sentence cleanly.
* **Pages 0–55** are the unsolved body: 12,956 runes, 2,928 words
  (2,744 unique — no repeated word of 5+ runes anywhere, confirming the
  cipher is polyalphabetic across word repetitions).

All statistics below are computed page-wise (no comparison crosses a page
boundary) on pages 0–55.

## The two real anomalies

### 1. The lag-1 doublet deficit (z = −17.3)

`P(c[i+1] = c[i])` is 0.0067 versus 0.0345 expected — the famous LP doublet
deficit, and it is *surgically precise*: the histogram of lag-1 deltas
`(c[i+1] − c[i]) mod 29` is statistically uniform on deltas 1–28 and only
delta 0 is suppressed. The ciphertext behaves like a random walk with
i.i.d. uniform **nonzero** increments. The residual doublet rate (86 in
12,901, ≈ 0.0067) is in the range of a plaintext-rare-event leaking through
(compare: rune-level doublets in runeglish plaintext are themselves rare
since TH/NG/EO/etc. are single runes).

### 2. The lag-5 digraph repeat excess

Digraphic kappa (pattern `XY···XY`, the two digraphs exactly 5 apart) at
lag 5: **28 observed**. Against the naive baseline (15.0 expected) that is
z = +3.35, the highest of all 60 lags tested (next best: lag 29 at +2.34).
Against a doublet-adjusted baseline (16.8 expected, factoring kappa as
`P(rune match) × P(delta match)`) the Poisson p-value is **0.0078** — still
uniquely low among lags 1–20 (next best: lag 18 at 0.118).

Supporting wisps, none independently significant:

* monographic kappa at lag 5 is the (joint) highest of lags 2–17 (+1.25 z);
* the single trigraphic lag-5 repeat (1 observed vs 0.52 expected);
* the only repeated 6-gram in the entire corpus, `DJUBEI`
  (`ᚢᛄᚢᛒᛖᛁ`-context, pages 27 → 55), sits at distance 6395 = 5 × 1279,
  i.e. ≡ 0 mod 5.

**Honest significance assessment:** with ~60 lags examined, the corrected
probability of seeing one lag this strong by chance is roughly 0.3–0.5. The
lag-5 excess is the strongest repeat signal in the corpus and worth chasing,
but it is *not* proof of period-5 structure on its own.

## What the lag-5 signal is NOT

Every conventional period-5 mechanism was tested and excluded:

| Hypothesis | Test | Result |
|---|---|---|
| Period-5 repeating key (Vigenère/Beaufort/Quagmire) | coset IOC, periods 2–10 | flat (≈1.000 all cosets) |
| Ciphertext autokey, primer length 5 | IOC of `c[i+5] ± c[i]` streams | flat (≈1.000) — would be ~1.8 if true |
| Period-5 key over the delta domain | delta-stream coset IOC + delta kappa | flat; lag 20 (+2.31) tops, not 5 |
| Keystream reuse across pages (incl. shift 5) | cross-page coincidence, shifts 0–10 | flat (max pair z within order-statistic expectation) |
| Word-keyed / word-aligned mechanism | word-boundary offsets of the 28 lag-5 repeats | no alignment (21/28 at unrelated offsets); word-length autocorrelation flat |
| Plain transposition of runeglish | unigram IOC | 0.9999 — transposition would preserve plaintext IOC ≈ 1.8 |

The repeats are also spread over 22 different pages (max 3 on one page), so
no single section drives the signal, and their positions are uniform mod 5
(no absolute-position alignment).

## Interpretation

The combined fingerprint — flat unigram IOC, *only* delta 0 suppressed,
flat cosets in every domain, no autokey signature, no keystream reuse, yet
a residual local lag-5 digraph correlation — is consistent with a keystream
that is effectively non-repeating globally but has weak *local* lag-5
autocorrelation. A 5-element key schedule applied with irregular
interruptors/resets would look exactly like this: interruptors destroy all
global coset/periodic statistics while leaving a small probability that
positions 5 apart still share key alignment. Quantitatively, the digraph
excess implies key alignment at distance 5 roughly 7–15% of the time
(consistent between the monographic and digraphic estimates).

The doublet deficit additionally implies the keystream's own lag-1 deltas
avoid the negated plaintext deltas almost perfectly — most simply explained
if the cipher's increment can never be zero (a 28-valued increment domain),
e.g. a scheme that enciphers into rune *differences* rather than runes.
A candidate family matching both anomalies: ciphertext built as a running
sum of nonzero increments, where the increment generator has a 5-element
schedule with interruptors. None of the obvious concrete instances
(primes-1 per page, totient stream, simple chained sums — all tested) fit,
so the LP remains unbroken here; but the lag-5 hypothesis is *supported*,
localized (it lives in adjacent-pair correlations, not in any global period),
and bounded (≤ ~15% residual alignment).

## Suggested next steps

* Brute-force 29^5 5-element increment schedules against single pages under
  an interruptor model, scoring with the runeglish n-gram tables in
  `src/aldegonde/data/ngrams/runeglish/`.
* Treat the 28 lag-5 repeat sites (listed by the script) as cribs: under an
  interruptor model these are the positions where key alignment most likely
  survived, so plaintext there should repeat at distance 5
  (`THE·xx·THE`-style patterns).
* Examine `DJUBEI` (pages 27/55, distance 5 × 1279; 1279 is prime) for a
  shared key-schedule phase between those two pages.
