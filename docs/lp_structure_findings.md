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

## 5. Mechanism kill-table (simulated fingerprints)

Every candidate mechanism was simulated on Markov-1 runeglish plaintext at
the corpus length and fingerprinted on the same seven statistics measured
on the LP. The target row is the LP itself. A mechanism is viable only if
it matches **all** columns, the decisive one being the doublet rate.

| mechanism | nIoC | uni-χ² | dbl % | off-χ² | digIoC | lag2 z | maxPeriod |
|---|---|---|---|---|---|---|---|
| **LP unsolved corpus (target)** | 1.000 | 26 | **0.66** | 41 | 1.026 | −0.3 | 1.009 |
| plaintext itself | 1.759 | 9860 | 3.27 | 1544 | 4.92 | +19.7 | 1.765 |
| OTP (control) | 0.999 | 20 | 3.70 | 27 | 1.003 | +0.5 | 1.008 |
| no-repeat-key OTP (k[i]≠k[i−1]) | 1.001 | 36 | 3.55 | 35 | 0.998 | −1.2 | 1.009 |
| running key (Vigenère) | 1.048 | 650 | 3.69 | 47 | 1.109 | +1.1 | 1.053 |
| running key (quagmire s(p)+t(k)) | 1.016 | 231 | 3.44 | 42 | 1.040 | −0.5 | 1.022 |
| running key (Beaufort) | 1.051 | 686 | 3.62 | 32 | 1.116 | +1.7 | 1.057 |
| plaintext autokey L=1/3/7 | 1.05–1.11 | 646–1493 | 3.5–6.6 | 48–496 | 1.13–1.48 | +0.8…+3.2 | 1.05–1.12 |
| key autokey (k += p) | 1.000 | 24 | 2.68 | 9757 | 1.752 | −7.1 | 1.005 |
| c = p + c_prev + random k | 1.000 | 31 | 3.45 | 28 | 1.001 | +0.2 | 1.005 |
| ciphertext autokey (mixed TR) | 1.000 | 31 | 4.02 | 455 | 1.762 | −0.8 | 1.012 |
| progressive quagmire perm(p)+i | 0.999 | 21 | 3.98 | 1144 | 1.084 | −0.5 | 1.752 |
| Gromark (chain-addition digits) | 1.124 | 1635 | 3.74 | 95 | 1.272 | +3.1 | 1.188 |
| Hill 2×2 | 1.032 | 439 | 3.73 | 285 | 2.013 | −0.2 | 1.075 |
| Chaocipher-29 | 1.000 | 22 | 3.53 | 26 | 1.004 | −1.4 | 1.005 |
| **S1 skip-key-on-collision** | 1.000 | 24 | 0.20 | 46 | 1.031 | +0.3 | 1.005 |
| **S2 stream + reroll, 19 % lapse** | 1.000 | 25 | **0.70** | 35 | 1.021 | −0.2 | 1.006 |
| S3 two-stream choice | 1.000 | 22 | 0.07 | 22 | 1.033 | +0.9 | 1.003 |
| **post-encryption deletion 81 %** | 1.000 | 31 | **0.59** | 36 | 1.023 | +1.3 | 1.007 |

Reading the table:

- Anything with **digIoC ≫ 1.03 or off-χ² ≫ 50** is dead: ciphertext
  autokey, plaintext autokey, key-autokey, Hill, progressive quagmire,
  running keys. These all leak adjacent-pair structure the LP does not have.
- Anything with **uni-χ² in the hundreds/thousands or nIoC > 1.02** is
  dead: running keys, Gromark, autokey — they leave a unigram bias.
- Everything with a clean fingerprint (OTP, no-repeat-key OTP, Chaocipher,
  c=p+c_prev+random) still has a **~3.5 % doublet rate** and is therefore
  excluded by the one statistic the LP fails by 5×.
- **Only three mechanisms reproduce the sub-1 % doublet rate**, and of
  those only two hit the *exact* 0.66 % naturally rather than driving it to
  ~0: a strong stream with a **probabilistic anti-doublet lapse (~19–25 %)**
  and **post-encryption deletion of ~81 % of doublets**. S1/S3 (strict
  skip) over-suppress to near zero, so whatever rule is in play is
  *deliberately inconsistent* — consistent with a human carver applying it
  by hand, or with the rule only firing under a secondary condition.

## 6. The difference-domain reframing (the strongest remaining lead)

Because the only structure is exactly the suppressed diagonal, the cipher
is equivalent to a **first-difference stream**: define
`d[i] = (c[i] − c[i−1]) mod 29`. Then the LP is `d` uniform over {1..28}
with the value 0 suppressed. So the *real* message channel is `d`, and the
86 doublets are the 86 surviving `d = 0` events.

Attacking `d` directly (`lp_battery12.py`):

- The **nonzero-d stream is uniform over its 28 values** (base-28
  nIoC 1.0011; χ² 41.4 on 27 df — a single ~p=0.04 result among dozens of
  tests, i.e. noise).
- **No periodicity** in `d` at any period 2–60, and **no short-key
  Vigenère** on `d` (per-column χ² never significant, periods 2–29).
- **No keystream correlation** in `d`: primes, totient, index, Fibonacci,
  π, primes-mod-29, both signs — best nIoC 1.002.

So the plaintext is OTP-grade *even in the difference domain*. This is the
sharpest statement of the problem: there is no additive layer to peel in
either the value domain or the difference domain.

## 7. Provenance of the doublets: residue, not plaintext

Tested against Cicada's *own* solved plaintext (the plain/mono `$`-segments
of the master transcription, 2,058 runes, `lp_battery10.py`):

- Cicada plaintext doubles at **2.33 %**, concentrated on specific runes
  (ᛚ ᛏ ᛋ dominate, matching English ll/tt/ss), **62 % interior / 38 %
  cross-word / 0 % word-initial**.
- The LP's 86 doublets are **uniform over all 29 runes** and their
  position mix (17 % first-pair / 52 % interior / 30 % cross-word) is
  statistically identical to the by-opportunity null (χ² 1.95, 2 df).

The LP doublets therefore do **not** look like surviving plaintext doubles
(which would be rune-biased and word-structured) — they look like the
random residue of a stream process whose anti-doublet rule occasionally
lapsed. This **excludes the monoalphabetic / doubling-preserving family**
(any cipher where a plaintext double shows as a cipher double): such a
cipher would inherit Cicada's 2.33 %, rune-biased, word-structured profile,
not a flat 0.66 %.

Also killed in battery 10/12: **fractionation / tomographic** ciphers (no
2-periodic bigram structure; even/odd-aligned bigram IoC both ≈ 1.03) and
**digraphic (Playfair-type)** ciphers (no excess of repeated even-aligned
bigrams; even-aligned doublets present at 37, whereas Playfair forbids
them). Triplets in the corpus: **0** (vs 15 expected uniform), consistent
with a memory-1 anti-doublet rule and inconsistent with any independent
stream.

## 8. Updated verdict and where to point compute

Ranked surviving hypotheses, all of the same shape — *strong stream +
weak, plaintext-dependent anti-doublet perturbation*:

1. **Disk/keystream that re-steps on collision** (Wheatstone- or
   Alberti-style: "if the next output equals the last, advance one more
   step"), applied ~80 % of the time. Makes key alignment drift by the
   running count of collisions — defeats subtraction unless the base stream
   *and* every collision point are reconstructed jointly.
2. **OTP-grade stream + manual no-doubles touch-up** during carving.
3. **Post-encryption deletion** of ~81 % of doubled glyphs (changes the
   length relationship to plaintext; the other two preserve length).

Concrete next experiments worth the compute:

- **Joint stream+drift search restricted to the 49 short pages** (< 130
  runes, e.g. pages 22, 32, 49, 54): few collisions, so a brute force over
  a small key space *with* collision-resteps is tractable where the full
  pages are not.
- **Test the resteps-on-collision model against the known streams with the
  drift counter keyed to observed doublets** rather than a free HMM: at
  each doublet, bump the key index by +1 (or by 29) and re-score with
  unigram+bigram runeglish fitness. This is a deterministic variant of the
  Viterbi attack and is cheap to run for primes/totient/index/π.
- **Cross-page key reuse**: align all 55 pages at index 0 and test whether
  a single per-position key (mod the per-page collision drift) raises the
  pooled column IoC. Negative so far on raw alignment, but not yet tested
  with collision-drift compensation.

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
python lp_battery10.py    # Cicada plaintext doubling profile; keystream dbl rates
python lp_battery11.py    # mechanism kill-table (20 simulated mechanisms)
python lp_battery12.py    # difference-domain attack; fractionation/Playfair kills
```
