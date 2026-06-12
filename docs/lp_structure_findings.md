# Structural analysis of the unsolved Liber Primus (data/page0-58.txt)

Analysis of the rune ciphertext in `data/page0-58.txt`, assuming English
plaintext written in runes (runeglish) and genuine word boundaries
(`-` = word break, `/` = line break within word stream, `%` = page break,
`.` = sentence break).

Corpus after parsing: 57 pages, 13,136 runes, 3,367 words. Pages 55 and 56
of the file are the two *known* pages — page 55 decrypts with
`c − totient(prime_n)` to "AN END WITHIN THE DEEP WEB THERE EXISTS A PAGE
THAT HASHES TO IT …" and page 56 is the unencrypted Parable
(nIoC 1.82). Both were re-derived from scratch by the test battery, which
validates the pipeline. All conclusions below are for the **clean unsolved
corpus: pages 0–54, 12,956 runes**.

All IoC values are normalized (×29): 1.0 = uniform random,
≈ 1.78 = runeglish plaintext.

## 1. The ciphertext is flat in every channel except one

| Test | Result |
|---|---|
| Unigram distribution | chi² 25.9 (28 df) — uniform |
| Global nIoC | 0.9999 |
| Periodic IoC, periods 2–80 | all ≈ 1.00, no period |
| Kappa autocorrelation, lags 2–6000 | flat; nothing survives multiple-test correction |
| Digram IoC at distances 2–20 | ≈ 1.00 |
| `(c[i+d] − c[i]) mod 29` distribution, d = 2–40 | uniform |
| IoC by position-in-word (incl. first/last letters, per word length) | uniform |
| Sentence-initial, line-initial, page-aligned, word-aligned coincidence | uniform |
| Same-length word pairs, consecutive words/pages aligned | uniform |
| Repeated whole ciphertext words | zero of length ≥ 4 in 3,367 words; lengths 1–3 at chance level |
| Repeated n-grams (Kasiski) | at chance level (1 six-gram pair vs 0.14 expected; n.s.) |
| Per-page and per-`$`-segment IoC | homogeneous, all ≈ 1.0 |
| Index/prime/totient/π/e/Fibonacci/squares/2^i/3^i keystreams, ± , corpus-wide and restarted per page | nothing |
| Prefix attack (first 15/25 runes of every page vs those keystreams, LL-scored) | nothing |
| Drift-tolerant Viterbi attack (keystream + plaintext-dependent skips) | nothing (solved page 55 lights up; pages 0–54 do not) |
| Running key with the book itself (page j vs page j−1) | nothing |
| Word gematria-prime sums mod 28/29/30/59 vs Monte-Carlo null | nothing |
| Within-word isomorph shape census vs shuffled null | only doublet-containing shapes deviate (see §2) |

The word-length distribution (mean 3.90) and its small negative lag-1/lag-2
autocorrelation are consistent with genuine English-in-runes word
boundaries, i.e. the word lengths look like real language even though the
runes look like noise.

## 2. The single robust anomaly: doublet suppression

`P(c[i+1] = c[i])` = 86/12,955 = **0.66 %** against 3.45 % expected
(**z = −17.4**). Properties, each established directly:

- **Uniform over rune identity**: every one of the 29 runes is suppressed
  (per-rune z between −1.9 and −4.0, no outliers).
- **Uniform over the corpus**: all 8 corpus chunks and essentially all
  pages show the deficit; no trend.
- **Boundary-transparent**: the same suppression holds within words
  (0.63 %), across word breaks (0.84 %), across line breaks and across
  sentence breaks. A 2×28 homogeneity test of the lag-1 difference
  distribution within-word vs cross-word gives chi² 28.5 (27 df): the
  cipher state passes through word boundaries untouched — no space
  symbol, no key advance at breaks.
- **Memory length exactly 1**: lag-2 coincidence is perfectly normal
  (z = −0.3), ABA patterns are normal, and the doublet gap distribution is
  geometric. Only the immediately preceding glyph matters.
- **Otherwise uniform transition matrix**: a 29×29 independence test gives
  chi² 796.6 on 784 df (z = +0.3); the digram IoC excess (1.0254) is fully
  predicted by the diagonal deficit alone (1.0229). Off the diagonal the
  residual structure is chi² 41.4 on 27 df — noise.

Model that fits everything: **c[i+1] is uniform over the 28 runes other
than c[i]; the no-repeat rule lapses (or is overridden) ~19 % of the
candidate times, leaving 86 doublets.**

## 3. What this excludes (the strongest result)

For any additive cipher `c = p + k (mod 29)` whose keystream is generated
independently of the plaintext — periodic Vigenère/Beaufort, running key,
Gronsfeld, any PRNG or mathematical stream, *regardless of key length* —

```
P(c[i+1]=c[i]) = Σ_d P(Δp = −d)·P(Δk = d)  ≥  min_d P(Δp = d) ≈ 1.7 %
```

using the runeglish lag-1 difference distribution (whose smallest bin is
≈ 1.7 %, and which is ≈ 3.2 % at d = 0). The observed 0.66 % is **half the
theoretical floor**. Hence:

1. **No plaintext-independent additive keystream can produce this
   ciphertext** (assuming English/runeglish plaintext) — the entire class
   the community keeps sweeping is mathematically excluded by one
   statistic, before any key search.
2. General mixed-alphabet polyalphabetics (quagmires) with independent key
   could in principle dip lower only by exploiting rare English bigrams,
   but that would imprint structure on specific off-diagonal transition
   cells. The observed suppression is exactly diagonal and otherwise
   perfectly uniform — a rule about the *ciphertext glyphs*, not about
   plaintext bigrams.
3. Ciphertext autokey with any fixed tabula recta is excluded separately:
   it forces digram-IoC(distance 1) ≈ plaintext IoC (≈ 1.78); observed
   1.0254.
4. Simulated always-advancing disk machines (Wheatstone-style, geared
   variants) do *not* reproduce the deficit; simulated OTP-with-rejection
   reproduces it exactly except it yields 0 doublets instead of 86.
5. Since lag-1 structure survives in reading order, **there is no
   post-encryption transposition**: the carving order is the encryption
   order.
6. No keystream re-alignment anywhere: no repeated cipher word of length
   ≥ 4, n-gram repeats at chance, autocorrelation flat to lag 6000 —
   the effective keystream never repeats within the 12,956 runes.

## 4. Interpretation and attack surface

The cipher behaves like a one-time / strong-PRNG stream **plus a
deliberate anti-repetition step applied at encryption time** (e.g. "if the
output glyph equals the previous one, advance the key/disk one extra step"
or "choose the alternative output"), applied with ~80 % consistency — the
inconsistency itself looks human. Such a rule makes the key alignment
drift in a plaintext-dependent way, which would defeat keystream
subtraction even if the underlying stream were guessable (tested here with
a drift-tolerant Viterbi decoder for the known Cicada streams — negative).

What information remains exploitable:

- **The 86 doublet positions** are the only plaintext-correlated marks in
  the corpus. Under "skip-on-collision" mechanics each doublet marks a
  position where the rule lapsed or was inapplicable; under
  full-revolution mechanics they mark plaintext doubled runes. Any future
  candidate scheme can be tested first against the doublet statistic
  (0.66 %, diagonal-only, memory-1, boundary-transparent) — it instantly
  falsifies most proposals at zero search cost.
- Word boundaries are real but cryptographically inert: attacks should
  treat the rune stream as continuous.
- All 55 pages are statistically identical: one scheme, one continuous or
  per-page-unique keying; solving any page likely solves all.

## Reproduction

```
python lp_structure.py    # parsing + baseline
python lp_battery1.py     # lags, periods, difference streams
python lp_battery2.py     # lag-1 anatomy
python lp_battery3.py     # word/sentence/line/page anchored tests
python lp_battery4.py     # doublet anatomy vs runeglish reference
python lp_battery5.py     # keystream sweep, feedback models, gematria
python lp_battery6.py     # Monte-Carlo nulls, transition independence, repeats
python lp_battery7.py     # long repeats, solved-page confirmation, clean corpus
python lp_battery8.py     # boundary homogeneity + mechanism simulations
python lp_battery9.py     # prefix attack + Viterbi drift attack
```
