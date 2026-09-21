# ABOUTME: Tests the body's block-length distribution against the author's own word lengths,
# ABOUTME: finding a hole at length two that no register shift or merge rule reproduces.
"""The blocks are said to have "the marginal of running text". Whose running text?

`what-any-solution-must-satisfy.md` row E1 records that the block lengths carry no
language ORDER, measured against the author's own plaintext. It says nothing about the
marginal, which has only ever been compared to prose by eye.

This compares it properly, against three references:

    LP plaintext   486 words from the eleven solved pages, the author's own register
    prose          Pride and Prejudice in runeglish, the surrogate used everywhere else
    tilted         either of the above reweighted by exp(lambda * length), a one-parameter
                   register shift toward longer or shorter words

A register difference between the front matter and the body is entirely plausible, so
the tilt is the fair null: it lets the body be wordier without letting it be shaped
differently. If a tilt fits, there is nothing to explain.

It does not fit, and the misfit is one length.

    python block_length_shape.py
"""

from __future__ import annotations

import collections
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import lp_words, prose_corpora  # noqa: E402

CAP = 12


def register():
    spec = importlib.util.spec_from_file_location(
        "lp_plaintext_register", ROOT / "experiments" / "lp_plaintext_register.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def histogram(words) -> tuple[np.ndarray, int]:
    c = collections.Counter(min(len(w), CAP) for w in words)
    return np.array([c[k] for k in range(1, CAP + 1)], float), sum(c.values())


def tilt_fit(base: np.ndarray, obs: np.ndarray) -> tuple[float, float, np.ndarray]:
    """Best exp(lambda*L) reweighting of `base`, by chi2 against `obs`."""
    lengths = np.arange(1, CAP + 1)
    p = base / base.sum()
    n = obs.sum()
    best = (float("inf"), 0.0)
    for lam in np.linspace(-0.5, 0.5, 1001):
        q = p * np.exp(lam * lengths)
        q /= q.sum()
        e = q * n
        chi = float((((obs - e) ** 2) / np.maximum(e, 1e-9)).sum())
        if chi < best[0]:
            best = (chi, float(lam))
    chi, lam = best
    q = p * np.exp(lam * lengths)
    q /= q.sum()
    e = q * n
    return lam, chi, (obs - e) / np.sqrt(np.maximum(e, 1e-9))


def merged(words, absorb_len: int, q: float, rng) -> list:
    """Join each word of `absorb_len` runes to the next with probability q."""
    out, carry = [], []
    for w in words:
        if carry:
            out.append(carry + list(w))
            carry = []
        elif len(w) == absorb_len and rng.random() < q:
            carry = list(w)
        else:
            out.append(list(w))
    if carry:
        out.append(carry)
    return out


def page_spread(mod) -> tuple[float, float, int]:
    """Fraction of 2-rune words per solved page, so register variation is priced."""
    pages = mod.MASTER.read_text().split("%")
    fracs, sizes = [], []
    for n in mod.PLAIN_PAGES:
        w = mod.words_of(pages[n])
        if w:
            fracs.append(sum(1 for x in w if len(x) == 2) / len(w))
            sizes.append(len(w))
    for t in json.loads(mod.TRIPLES.read_text()):
        if t["cipher"] == "monoalphabetic":
            w = mod.words_of(pages[t["page"]], t["key"])
            if w:
                fracs.append(sum(1 for x in w if len(x) == 2) / len(w))
                sizes.append(len(w))
    f = np.array(fracs)
    s = np.array(sizes, float)
    return float((f * s).sum() / s.sum()), float(f.std(ddof=1) / np.sqrt(len(f))), len(f)


def main() -> None:
    import random

    mod = register()
    body, n_body = histogram(lp_words())
    plain, n_plain = histogram(mod.corpus())
    prose = np.zeros(CAP)
    n_prose = 0
    for p in prose_corpora(2928, 10):
        h, n = histogram(p)
        prose += h
        n_prose += n

    print(f"body {n_body:,} blocks, LP plaintext {n_plain} words, "
          f"prose {n_prose:,} words\n")
    print(f"{'len':>4}{'LP plain':>10}{'prose':>9}{'body':>9}")
    for i in range(CAP):
        print(f"{i + 1:>4}{plain[i] / n_plain:>10.4f}{prose[i] / n_prose:>9.4f}"
              f"{body[i] / n_body:>9.4f}")
    mean = lambda h, n: sum((i + 1) * h[i] for i in range(CAP)) / n  # noqa: E731
    print(f"{'mean':>4}{mean(plain, n_plain):>10.3f}{mean(prose, n_prose):>9.3f}"
          f"{mean(body, n_body):>9.3f}")

    print("\nbest one-parameter register tilt, exp(lambda * length):")
    for name, base in (("LP plaintext", plain), ("prose", prose)):
        lam, chi, res = tilt_fit(base, body)
        print(f"  {name:<13} lambda {lam:+.3f}  chi2 {chi:>6.1f} on {CAP - 2} df")
        print("    residual by length: " + " ".join(f"{r:+5.1f}" for r in res))
    print("\nNeither fits, and in both the largest residual is at length 2, with length")
    print("1 and length 3 on the other side of the prediction.")

    pooled, se, npages = page_spread(mod)
    frac2 = body[1] / n_body
    print(f"\nfraction of 2-rune units: LP plaintext {pooled:.3f} (between-page se "
          f"{se:.4f} over {npages} pages), body {frac2:.3f}")
    print(f"  z against the between-page spread: {(frac2 - pooled) / se:+.2f}")
    print("  The between-page spread is the right denominator: it prices the register")
    print("  difference between one solved page and another, which is what the body")
    print("  might also be.")

    print("\nWhich length has to be absorbed? One parameter, fitted:")
    rng = random.Random(31)
    words = mod.corpus()
    print(f"{'absorbed':>9}{'best q':>8}{'chi2':>9}{'len-2 resid':>13}")
    for absorb in (1, 2, 3):
        best = (float("inf"), 0.0, None)
        for q in np.linspace(0.05, 1.0, 20):
            h = np.zeros(CAP)
            n = 0
            for _ in range(40):
                mh, mn = histogram(merged(words, absorb, float(q), rng))
                h += mh
                n += mn
            e = h / n * n_body
            chi = float((((body - e) ** 2) / np.maximum(e, 1e-9)).sum())
            if chi < best[0]:
                best = (chi, float(q), (body - e) / np.sqrt(np.maximum(e, 1e-9)))
        chi, q, res = best
        print(f"{absorb:>9}{q:>8.2f}{chi:>9.1f}{res[1]:>13.1f}")
    print("\nOnly length 2. So absorbing 2-rune units is the shape of the marginal.")
    joint_scan()


def joint_scan() -> None:
    """Fit the merge rate twice: on the length marginal, and on the serial order.

    Merging removes exactly the transitions that carry the serial signal -- a short
    function word followed by a longer content word -- so it moves both statistics.
    If one rate satisfies both, the body is the author's words with the short ones
    absorbed. If the two fits disagree, absorption is only part of the story.
    """
    import random  # noqa: PLC0415

    from word_length_sequence import (  # noqa: PLC0415
        excess_per_pair,
        plaintext_sequences,
    )

    body_h, n_body = histogram(lp_words())
    plain_seqs = plaintext_sequences()

    def merge_seq(seq, q, rng):
        out, carry = [], 0
        for length in seq:
            if carry:
                out.append(carry + length)
                carry = 0
            elif length == 2 and rng.random() < q:
                carry = 2
            else:
                out.append(length)
        if carry:
            out.append(carry)
        return out

    print("\nThe same rate, fitted on the marginal and on the serial order:\n")
    print(f"{'q':>6}{'marginal chi2':>15}{'frac len 2':>12}{'excess G2 per pair':>22}")
    for q in (0.0, 0.15, 0.30, 0.35, 0.50, 0.70, 1.0):
        hs = np.zeros(CAP)
        ex = []
        for t in range(12):
            r = random.Random(200 + t)
            m = [merge_seq(s, q, r) for s in plain_seqs]
            for s in m:
                c = collections.Counter(min(x, CAP) for x in s)
                hs += np.array([c[k] for k in range(1, CAP + 1)], float)
            ex.append(excess_per_pair(m, r, 120)[0])
        e = hs / hs.sum() * n_body
        chi = float((((body_h - e) ** 2) / np.maximum(e, 1e-9)).sum())
        v = np.array(ex)
        print(f"{q:>6.2f}{chi:>15.1f}{hs[1] / hs.sum():>12.4f}"
              f"{f'{v.mean():.4f} +- {v.std():.4f}':>22}")
    print(f"{'body':>6}{'-':>15}{body_h[1] / n_body:>12.4f}"
          f"{'0.0040 +- 0.0025':>22}")
    print(
        "\nThe two fits disagree. The marginal picks q = 0.35, and at that rate the"
        "\nlength sequence still carries 0.023 of excess against the body's 0.004,"
        "\nabout three sigma. Pushing q to 1.0 gets the sequence to 0.0096, still two"
        "\nsigma high, and destroys the marginal completely."
        "\n\nSo absorbing short units accounts for the hole at length 2 and not for the"
        "\nmissing serial order. They are two effects, not one."
    )
    author_never_splits()
    hole_is_uniform()


def author_never_splits() -> None:
    """Could the body simply spell digraphs differently?

    Seven of the 29 runes stand for two English letters, TH among them, and THE is
    the commonest 2-rune word. If the body wrote T+H instead of the single rune, mass
    would move from length 2 to length 3 -- which is the shape of the deficit. The
    hypothesis is worth a number and then a check against the author's own practice.
    """
    from aldegonde import c3301  # noqa: PLC0415

    eng = c3301.CICADA_ENGLISH_ALPHABET
    plain = register().corpus()
    body, n_body = histogram(lp_words())
    print("\nCould the body spell digraphs differently?\n")
    for label, extra in (
        ("as transcribed", ()),
        ("TH written as two runes", ("TH",)),
        ("TH, EA, NG as two runes", ("TH", "EA", "NG")),
    ):
        lens = [len(w) + sum(1 for r in w if eng[r] in extra) for w in plain]
        c = collections.Counter(min(x, CAP) for x in lens)
        h = np.array([c[k] for k in range(1, CAP + 1)], float)
        e = h / h.sum() * n_body
        chi = float((((body - e) ** 2) / np.maximum(e, 1e-9)).sum())
        res2 = (body[1] - e[1]) / np.sqrt(max(e[1], 1e-9))
        print(f"  {label:<26} chi2 {chi:>7.1f}   length-2 residual {res2:+.1f}")
    print("\n  Splitting TH halves the misfit. But the author never does it:")
    pairs = {"TH": ("T", "H"), "EA": ("E", "A"), "NG": ("N", "G"),
             "IA": ("I", "A"), "AE": ("A", "E")}
    for dg, (a, b) in pairs.items():
        one = sum(1 for w in plain for r in w if eng[r] == dg)
        two = sum(1 for w in plain for i in range(len(w) - 1)
                  if eng[w[i]] == a and eng[w[i + 1]] == b)
        print(f"    {dg}: {one} as one rune, {two} as two")
    print("  125 digraph tokens in the solved plaintext, not one written apart.")


def hole_is_uniform() -> None:
    """Content varies between sections; a scribal or cipher rule does not.

    If the deficit is register it should move with the text. If it is a process it
    should not.
    """
    import re  # noqa: PLC0415

    from aldegonde import c3301  # noqa: PLC0415

    rune = re.compile(r"[\u16a0-\u16ff]")
    text = (ROOT / "data" / "page0-56.txt").read_text()
    rows = []
    for k, chunk in enumerate(x for x in text.split("$") if rune.search(x)):
        seq, cur = [], 0
        for ch in chunk:
            if rune.match(ch):
                cur += 1
            elif ch in "/\n":
                continue
            elif cur and ch in c3301.WORD_BOUNDARY:
                seq.append(cur)
                cur = 0
        if cur:
            seq.append(cur)
        if len(seq) >= 40:
            rows.append((k, len(seq), sum(1 for x in seq if x == 2) / len(seq)))
    print(f"\nIs the hole uniform across the body? {len(rows)} sections of 40+ blocks.\n")
    print(f"{'section':>8}{'blocks':>8}{'frac len 2':>12}")
    for k, n, f in rows:
        print(f"{k:>8}{n:>8}{f:>12.3f}")
    f = np.array([r[2] for r in rows])
    n = np.array([r[1] for r in rows], float)
    pooled = float((f * n).sum() / n.sum())
    chi = float((((f - pooled) ** 2) * n / (pooled * (1 - pooled))).sum())
    print(f"\npooled {pooled:.4f} over {int(n.sum()):,} blocks; homogeneity chi2 "
          f"{chi:.1f} on {len(rows) - 1} df")
    print(f"observed sd across sections {f.std(ddof=1):.4f}, binomial expectation "
          f"{np.sqrt(pooled * (1 - pooled) * (1 / n).mean()):.4f}")
    print(f"highest section {f.max():.3f}; the author's own plaintext is 0.239; "
          f"sections reaching it: {(f >= 0.239).sum()}")
    print(
        "\nThe body is homogeneous and no section comes near the author's rate. Content"
        "\nvaries from section to section and this does not, which is what a process"
        "\nlooks like and not what a register looks like."
    )


if __name__ == "__main__":
    main()
