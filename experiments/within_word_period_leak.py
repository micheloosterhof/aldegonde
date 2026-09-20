# ABOUTME: Decomposes the LP within-word same-rune curve into a doublet-avoidance
# ABOUTME: baseline plus a period-5 leak, and maps the period-5 duty cycle per section.
"""Within-word repeated-rune analysis of the Liber Primus.

The within-word same-rune rate at distance d, for the ciphertext, factors as

    R_ct(d) = pi(d) * R_pt(d) + (1 - pi(d)) * B(d)

  * B(d)     -- the doublet-avoidance baseline: the rate under a null that keeps
                the exact rune frequencies AND the observed adjacent-doublet rate
                but destroys all positional structure (c3301.low_doublet_null).
                B(1) ~ 0, B(d>=2) ~ chance.
  * R_pt(d)  -- the plaintext same-rune rate (runeglish); on-alphabet pairs pass
                a substitution bijectively, so plaintext equality survives.
  * pi(d)    -- fraction of distance-d within-word pairs sharing a key element.
                For cyclic period-5, pi(d)=1 iff d = 0 mod 5, else 0; interruptors
                pull pi(5) below 1.

The ciphertext shows B(d) everywhere except a lone bump at d=5, whose excess over
B measures the period-5 leak. This script prints the decomposition, estimates the
period-5 duty cycle pi(5) globally and per unsolved section, and writes two figures.

Usage: python experiments/within_word_period_leak.py
"""

from __future__ import annotations

import random
import sys

sys.path.insert(0, "src")

from plaintext_control_corpus import (
    candidate_decodes,
    load_quadgram_scorer,
    parse_sections,
)

from aldegonde import c3301
from aldegonde.analysis.coincidence import within_word_match_rate

MOD = 29
SKIPS = list(range(1, 7))
DECODE_ACCEPT = -5.5  # quadgram score above which a section reads as plaintext
# The ciphertext under analysis is the unsolved corpus, pages 0-56; the master
# (which folds in the solved intro pages) is read only for the plaintext reference.
CIPHERTEXT = "data/page0-56.txt"
MASTER = "data/liber-primus__transcription--master.txt"
RUNE_S = c3301.CICADA_ALPHABET.index("ᛋ")  # the rune that dominates the d=5 leak
SEED = 20260901
FIG_DIR = "experiments"

# The 13-dot glyph is the real on-page section mark; the project's editorial
# `$`/`%`/`&` dividers over-segment into title-sized fragments. Split on `⑬`
# and merge fragments up to a body-sized minimum so a title joins its section.
SECTION_MARK = "⑬"
MIN_SECTION_RUNES = 150
R2I = {rune: index for index, rune in enumerate(c3301.CICADA_ALPHABET)}
_WORD_END = (
    set(c3301.MARK_CHARS + "&%$" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS)
    - {SECTION_MARK}
)


def chance_rate(words: list[list[int]]) -> float:
    """Sum of p_i^2: the same-rune rate expected from rune frequencies alone."""
    freq = [0] * MOD
    for w in words:
        for r in w:
            freq[r] += 1
    tot = sum(freq)
    return sum((f / tot) ** 2 for f in freq) if tot else 0.0


def doublet_null_band(words: list[list[int]], permutations: int, rng: random.Random):
    """Per-skip within-word rate under the frequency+doublet-preserving null.

    Draws surrogate streams that keep the exact rune frequencies and the
    observed adjacent-doublet rate but randomize everything else, recuts each
    into the original word lengths, and measures the within-word same-rune rate.
    Returns (mean, lo2.5, hi97.5) per skip -- the baseline B(d) with its spread.
    """
    stream = [r for w in words for r in w]
    lengths = [len(w) for w in words]
    null = c3301.low_doublet_null()
    per_skip: dict[int, list[float]] = {k: [] for k in SKIPS}
    for _ in range(permutations):
        surrogate = list(null(stream, rng))
        recut, pos = [], 0
        for length in lengths:
            recut.append(surrogate[pos : pos + length])
            pos += length
        for k in SKIPS:
            per_skip[k].append(within_word_match_rate(recut, k).rate)
    mean, lo, hi = [], [], []
    for k in SKIPS:
        vals = sorted(per_skip[k])
        mean.append(sum(vals) / len(vals))
        lo.append(vals[int(0.025 * len(vals))])
        hi.append(vals[int(0.975 * len(vals))])
    return mean, lo, hi


def duty_cycle(r_ct: float, b: float, r_pt: float) -> float:
    """pi = (R_ct - B) / (R_pt - B): fraction of d=5 pairs that stay on-period."""
    return (r_ct - b) / (r_pt - b) if r_pt != b else float("nan")


def period5_excess(section: list[list[int]]) -> float:
    """Skip-5 same-rune rate minus the section's own off-period baseline.

    The baseline is the mean rate over skips 2, 3, 4, 6 -- the distances a
    period-5 cipher scrambles. A period-5 leak lifts skip 5 above that baseline;
    a solved (monoalphabetic) section sits high at every skip, so its excess is
    near zero; a flat section sits at chance everywhere. Excess isolates the
    period-5-specific structure from both.
    """
    rate = [within_word_match_rate(section, k).rate for k in (2, 3, 4, 5, 6)]
    baseline = (rate[0] + rate[1] + rate[2] + rate[4]) / 4
    return rate[3] - baseline


def dot_sections() -> list[list[list[int]]]:
    """The master split into big sections on the 13-dot mark, titles merged.

    Fragments between `⑬` marks that fall below MIN_SECTION_RUNES are titles;
    each is merged forward into the next fragment until a section reaches the
    minimum, so the result is body-sized sections with no title-sized slivers.
    """
    with open(CIPHERTEXT) as handle:
        text = handle.read()
    fragments: list[list[list[int]]] = [[]]
    word: list[int] = []
    for ch in text:
        if ch in R2I:
            word.append(R2I[ch])
        elif ch == SECTION_MARK:
            if word:
                fragments[-1].append(word)
                word = []
            fragments.append([])
        elif ch in _WORD_END and word:
            fragments[-1].append(word)
            word = []
    if word:
        fragments[-1].append(word)

    sections: list[list[list[int]]] = []
    current: list[list[int]] = []
    for fragment in (f for f in fragments if f):
        current.extend(fragment)
        if sum(len(w) for w in current) >= MIN_SECTION_RUNES:
            sections.append(current)
            current = []
    if current:
        if sections:
            sections[-1].extend(current)
        else:
            sections.append(current)
    return sections


def plaintext_reference() -> list[list[int]]:
    """Runeglish plaintext words from the master's solved sections.

    The analyzed ciphertext (pages 0-56) is all unsolved, so the plaintext
    baseline R_pt comes from the solved LP pages in the master: sections that
    decode under a single shift/atbash transform, kept as their decoded words.
    Register-matched reference, not part of the page-0-56 corpus.
    """
    score = load_quadgram_scorer()
    pt_words: list[list[int]] = []
    for sec in parse_sections(MASTER):
        best_words, best_score = sec, -99.0
        for _name, words in candidate_decodes(sec):
            s = score([c for w in words for c in w])
            if s > best_score:
                best_words, best_score = words, s
        if best_score > DECODE_ACCEPT:
            pt_words.extend(best_words)
    return pt_words


def main() -> None:
    rng = random.Random(SEED)
    sections = dot_sections()
    ct_words = [w for sec in sections for w in sec]
    pt_words = plaintext_reference()
    print(f"ciphertext (pages 0-56): {len(sections)} 13-dot sections, "
          f"{sum(len(w) for w in ct_words)} runes; "
          f"plaintext reference: {sum(len(w) for w in pt_words)} runes")

    ct_rate = [within_word_match_rate(ct_words, k).rate for k in SKIPS]
    pt_rate = [within_word_match_rate(pt_words, k).rate for k in SKIPS]
    b_mean, b_lo, b_hi = doublet_null_band(ct_words, permutations=400, rng=rng)
    q2_ct, p2_pt = chance_rate(ct_words), chance_rate(pt_words)

    print(f"\nchance rate Sum(freq^2): ct={q2_ct:.4f}  pt={p2_pt:.4f}  uniform={1/MOD:.4f}")
    print("\nskip | R_ct   | B (null)  [95% band]     | R_ct/B | R_pt")
    for i, k in enumerate(SKIPS):
        print(f"  {k}  | {ct_rate[i]:.4f} | {b_mean[i]:.4f} "
              f"[{b_lo[i]:.4f},{b_hi[i]:.4f}] |  {ct_rate[i]/b_mean[i]:.2f}  | {pt_rate[i]:.4f}")

    pi5 = duty_cycle(ct_rate[4], b_mean[4], p2_pt)
    print(f"\nglobal period-5 duty cycle pi(5) = "
          f"({ct_rate[4]:.4f}-{b_mean[4]:.4f})/({p2_pt:.4f}-{b_mean[4]:.4f}) = {pi5:.2f}")

    _figure_decomposition(ct_rate, pt_rate, b_mean, b_lo, b_hi, q2_ct, p2_pt)
    _per_section_leak(sections, rng)
    _rune_s_by_section(sections)


def _figure_decomposition(ct_rate, pt_rate, b_mean, b_lo, b_hi, q2_ct, p2_pt):
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 5.6))
    axA.fill_between(SKIPS, b_lo, b_hi, color="steelblue", alpha=0.18,
                     label="doublet-avoidance null (95%)")
    axA.plot(SKIPS, b_mean, color="steelblue", ls=":", lw=2, label="null mean B(d)")
    axA.plot(SKIPS, ct_rate, color="tab:blue", marker="o", lw=2.2, label="ciphertext")
    axA.plot(SKIPS, pt_rate, color="tab:orange", marker="s", label="plaintext (solved)")
    axA.axhline(1 / MOD, color="black", ls="--", lw=1, label=f"uniform {1/MOD:.4f}")
    axA.axhline(q2_ct, color="tab:blue", ls="-.", lw=1, label=f"random ct Σq²={q2_ct:.4f}")
    axA.axhline(p2_pt, color="tab:orange", ls="-.", lw=1, label=f"random pt Σp²={p2_pt:.4f}")
    axA.axvspan(4.6, 5.4, color="gold", alpha=0.15)
    axA.set(xlabel="skip", ylabel="within-word same-rune rate",
            title="Raw rates + true random rate per corpus")
    axA.legend(fontsize=7.5)
    axA.grid(alpha=0.3)

    axB.axhline(1.0, color="black", ls="--", lw=1, label="own random rate = 1.0")
    axB.fill_between(SKIPS, [x / q2_ct for x in b_lo], [x / q2_ct for x in b_hi],
                     color="steelblue", alpha=0.18)
    axB.plot(SKIPS, [x / q2_ct for x in ct_rate], color="tab:blue", marker="o", lw=2.2,
             label="ciphertext / Σq²")
    axB.plot(SKIPS, [x / p2_pt for x in pt_rate], color="tab:orange", marker="s",
             label="plaintext / Σp²")
    axB.axvspan(4.6, 5.4, color="gold", alpha=0.15)
    axB.set(xlabel="skip", ylabel="rate / own random rate",
            title="Normalized: positional structure only")
    axB.legend(fontsize=7.5)
    axB.grid(alpha=0.3)
    fig.suptitle("LP within-word repeated-rune: doublet avoidance + a lone period-5 leak")
    fig.tight_layout()
    path = f"{FIG_DIR}/within_word_period_leak.png"
    fig.savefig(path, dpi=130)
    print(f"wrote {path}")


def _per_section_leak(sections, rng, bootstrap=300):
    """Map the period-5 excess across the 13-dot big sections, with bootstrap CIs.

    Reports, per section: the off-period baseline (mean skip-2/3/4/6 rate), the
    skip-5 rate, and the excess of one over the other. A high baseline flags a
    solved monoalphabetic section (the intro), where every skip is lifted; a
    positive excess on a chance-level baseline is a period-5 ciphertext leak.
    """
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    uniform = 1 / MOD
    print("\nper-section period-5 excess (13-dot big sections):")
    print("  sec  runes | d1/U  base/U  d5/U | excess/U  [68% CI]  | flag")
    rows = []
    for idx, sec in enumerate(sections):
        runes = sum(len(w) for w in sec)
        d1 = within_word_match_rate(sec, 1).rate / uniform
        base = sum(within_word_match_rate(sec, k).rate for k in (2, 3, 4, 6)) / 4
        d5 = within_word_match_rate(sec, 5).rate
        excess = (d5 - base) / uniform
        boot = []
        for _ in range(bootstrap):
            sample = [sec[rng.randrange(len(sec))] for _ in range(len(sec))]
            boot.append(period5_excess(sample) / uniform)
        boot.sort()
        lo, hi = boot[int(0.16 * len(boot))], boot[int(0.84 * len(boot))]
        # A lifted d1 and a lifted off-period baseline mark a solved MASC section.
        flag = "MASC/solved" if d1 > 0.5 and base / uniform > 1.2 else "cipher"
        rows.append((idx, runes, d1, base / uniform, d5 / uniform, excess, lo, hi, flag))
    for idx, runes, d1, base, d5, excess, lo, hi, flag in rows:
        print(f"  s{idx:<2} {runes:>5} | {d1:4.2f}  {base:5.2f}  {d5:4.2f} |"
              f"  {excess:+5.2f}  [{lo:+4.2f},{hi:+4.2f}]  | {flag}")

    fig, ax = plt.subplots(figsize=(10, 4.8))
    xs = range(len(rows))
    excesses = [r[5] for r in rows]
    err = [[r[5] - r[6] for r in rows], [r[7] - r[5] for r in rows]]
    colors = ["tab:orange" if r[8].startswith("MASC") else "tab:blue" for r in rows]
    ax.bar(xs, excesses, color=colors, alpha=0.85)
    ax.errorbar(xs, excesses, yerr=err, fmt="none", ecolor="black", capsize=3, lw=1)
    ax.axhline(0, color="gray", lw=1)
    ax.set_xticks(list(xs))
    ax.set_xticklabels([f"s{r[0]}\n{r[1]}r" for r in rows], fontsize=8)
    ax.set(ylabel="skip-5 excess over off-period baseline (/uniform)",
           title="Period-5 leak per 13-dot section (orange = solved/MASC intro; "
                 "68% word-bootstrap CI)")
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    path = f"{FIG_DIR}/within_word_period_leak_per_section.png"
    fig.savefig(path, dpi=130)
    print(f"wrote {path}")


def _d5_same_rune(section: list[list[int]]) -> tuple[int, int, int, float, float]:
    """(pairs, matches, S-S matches, expected matches, expected S-S) at skip 5."""
    freq = [0] * MOD
    pairs = matches = ss = 0
    for w in section:
        for r in w:
            freq[r] += 1
        for i in range(len(w) - 5):
            pairs += 1
            if w[i] == w[i + 5]:
                matches += 1
                if w[i] == RUNE_S:
                    ss += 1
    tot = sum(freq)
    p2 = sum((f / tot) ** 2 for f in freq) if tot else 0.0
    ps = freq[RUNE_S] / tot if tot else 0.0
    return pairs, matches, ss, pairs * p2, pairs * ps * ps


def _rune_s_by_section(sections):
    """Split each section's skip-5 same-rune excess into the S-S part and the rest.

    A period-5 cipher preserves every rune's within-word repeat at distance 5,
    so the excess should spread across runes. Rune S is over-represented; this
    shows whether that concentrates in particular sections.
    """
    import matplotlib as mpl

    mpl.use("Agg")
    import matplotlib.pyplot as plt

    print(f"\nskip-5 excess split by rune S ({c3301.CICADA_ALPHABET[RUNE_S]}):")
    print("  sec  runes | d5match(exp) | S-S(exp) | excess  S-part  S-frac")
    rows = []
    for idx, sec in enumerate(sections):
        pairs, matches, ss, exp_all, exp_ss = _d5_same_rune(sec)
        exc_all = matches - exp_all
        exc_ss = ss - exp_ss
        frac = exc_ss / exc_all if exc_all > 0 else float("nan")
        runes = sum(len(w) for w in sec)
        rows.append((idx, runes, matches, exp_all, ss, exp_ss, exc_all, exc_ss, frac))
        print(f"  s{idx:<2} {runes:>5} | {matches:>3}({exp_all:5.1f})   |"
              f" {ss:>2}({exp_ss:4.1f}) | {exc_all:+5.1f}  {exc_ss:+5.1f}  {frac:.2f}")

    fig, ax = plt.subplots(figsize=(10, 4.8))
    xs = list(range(len(rows)))
    s_part = [r[7] for r in rows]
    rest = [r[6] - r[7] for r in rows]
    ax.bar(xs, s_part, color="tab:red", label="rune S (Sigel)")
    ax.bar(xs, rest, bottom=s_part, color="tab:blue", label="all other runes")
    ax.axhline(0, color="gray", lw=1)
    ax.set_xticks(xs)
    ax.set_xticklabels([f"s{r[0]}\n{r[1]}r" for r in rows], fontsize=8)
    ax.set(ylabel="skip-5 same-rune excess (pairs over chance)",
           title="Who carries the period-5 leak per section: rune S vs the rest")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    path = f"{FIG_DIR}/within_word_period_leak_rune_s.png"
    fig.savefig(path, dpi=130)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
