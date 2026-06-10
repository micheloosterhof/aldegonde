#!/usr/bin/env python3
# ABOUTME: Per-page attack battery for Liber Primus: affine, autokey, keywords,
# ABOUTME: and prime-1 keystream with interrupt-tolerant beam search.
"""Systematic cipher-breaking attempts on the Liber Primus unsolved section.

This script runs a battery of cryptanalytic attacks against every page of
``data/page0-58.txt``:

1. Baseline statistics: normalized IoC, doublet rate, columnar IoC by period.
2. Per-page monoalphabetic attacks: all 29 shifts, atbash, all 812 affine maps.
3. Per-page polyalphabetic attacks: Vigenere/Beaufort with known LP keywords,
   six autokey families (vigenere/beaufort/variant-beaufort, both index- and
   prime-value-based tabula recta) with all 29 primers.
4. Prime/totient keystream (key_n = nth prime - 1) with optional atbash, and
   a beam search over ᚠ-rune keystream interrupts (the scheme that solved the
   "AN END" page, which this script re-derives from scratch as validation).

Candidate plaintexts are ranked by runeglish trigram fitness, compared against
a random-runes reference and the solved "parable" page as plaintext reference.

Result: only the second-to-last page in the file flags - it is the already
solved "AN END" page, fully recovered from scratch by the interrupt-tolerant
beam search (validating the method). Pages 0-54 stay at random-level fitness
under every attack, including interrupt-tolerant keystreams that a plain
positional IOC subtraction test would miss. See
hypotheses/running-key-math-sequence.md.
"""

import itertools
import os
import random

from aldegonde import auto, c3301, pasc
from aldegonde.maths.primes import gen_primes_opt
from aldegonde.stats import ioc

ALPHABET = c3301.CICADA_ALPHABET
MOD = 29
FRUNE = ALPHABET[0]  # ᚠ, used as keystream interrupt on the solved pages


def runes_only(text: str) -> str:
    """Strip everything that is not a rune of the Cicada alphabet."""
    return "".join(x for x in text if x in ALPHABET)


def to_english(runes: str) -> str:
    """Transliterate runes to the Cicada english alphabet."""
    return "".join(c3301.CICADA_ENGLISH_ALPHABET[c3301.r2i(r)] for r in runes)


def nioc(text: str) -> float:
    """Normalized index of coincidence for the 29-rune alphabet."""
    return float(ioc(text)) * MOD


def doublet_rate(text: str) -> float:
    """Fraction of adjacent positions holding two identical runes."""
    if len(text) < 2:
        return 0.0
    return sum(1 for i in range(len(text) - 1) if text[i] == text[i + 1]) / (
        len(text) - 1
    )


def fitness(text: str) -> float:
    """Runeglish trigram score per rune (higher is more plaintext-like)."""
    return float(c3301.trigramscore(text)) / max(len(text), 1)


def load_pages(path: str) -> list[str]:
    """Load the LP transcription and return rune-only text per page."""
    with open(path) as f:
        raw = f.read()
    return [p for p in (runes_only(seg) for seg in raw.split("%")) if p]


def beam_decrypt_totient(
    ciphertext: str,
    keystream: list[int],
    sign: int = -1,
    beam: int = 60,
) -> tuple[str, float]:
    """Decrypt with a positional keystream allowing ᚠ-rune interrupts.

    At every ciphertext ᚠ the cipher may have emitted a literal plaintext F
    without consuming a key value. A beam search over these choices keeps the
    best partial decryptions by trigram fitness.

    Args:
        ciphertext: Rune string to decrypt
        keystream: Key value per consumed position (e.g. nth prime - 1)
        sign: -1 for plaintext = c - k, +1 for plaintext = c + k
        beam: Beam width

    Returns:
        Tuple of best plaintext and its fitness score
    """
    states: list[tuple[int, str]] = [(0, "")]
    for ch in ciphertext:
        c = c3301.r2i(ch)
        nxt: list[tuple[int, str]] = []
        for keyptr, pt in states:
            p = (c + sign * keystream[keyptr]) % MOD
            nxt.append((keyptr + 1, pt + c3301.i2r(p)))
            if ch == FRUNE:
                nxt.append((keyptr, pt + FRUNE))
        if len(nxt) > beam:
            nxt.sort(key=lambda s: c3301.trigramscore(s[1][-40:]), reverse=True)
            nxt = nxt[:beam]
        states = nxt
    best = max(states, key=lambda s: c3301.trigramscore(s[1]))
    return best[1], fitness(best[1])


def keyword_to_runes(word: str) -> str | None:
    """Convert an english keyword to runes via the Cicada english alphabet."""
    e2r: dict[str, str] = {}
    for i, e in enumerate(c3301.CICADA_ENGLISH_ALPHABET):
        e2r.setdefault(e, ALPHABET[i])
    out: list[str] = []
    i = 0
    while i < len(word):
        for ln in (3, 2, 1):
            if word[i : i + ln] in e2r:
                out.append(e2r[word[i : i + ln]])
                i += ln
                break
        else:
            return None
    return "".join(out)


def page_attack_battery(
    page: str,
    keystream: list[int],
) -> list[tuple[float, str, str]]:
    """Run all single-page attacks and return scored candidates."""
    idx = [c3301.r2i(r) for r in page]
    atbash = [28 - c for c in idx]
    candidates: list[tuple[float, str, str]] = []

    def consider(name: str, text: str) -> None:
        candidates.append((fitness(text), name, text))

    # all affine decrypt maps (includes all shifts and atbash variants)
    for a in range(1, MOD):
        for b in range(MOD):
            consider(
                f"affine-{a}-{b}",
                "".join(c3301.i2r((a * c + b) % MOD) for c in idx),
            )

    # prime/totient keystream, with and without atbash
    for nm, base in [("", idx), ("atbash-", atbash)]:
        for sg, sgnm in [(-1, "minus"), (1, "plus")]:
            consider(
                f"{nm}{sgnm}-totient",
                "".join(
                    c3301.i2r((c + sg * k) % MOD) for c, k in zip(base, keystream)
                ),
            )

    # totient keystream with ᚠ interrupts (the "AN END" scheme)
    for sg in (-1, 1):
        pt, sc = beam_decrypt_totient(page, keystream, sign=sg)
        candidates.append((sc, f"totient-interrupted-{sg:+d}", pt))

    # autokey families with every primer
    trs = [
        ("vig", pasc.vigenere_tr(ALPHABET)),
        ("bof", pasc.beaufort_tr(ALPHABET)),
        ("vbf", pasc.variantbeaufort_tr(ALPHABET)),
        ("vvig", c3301.valueTR("vigenere")),
        ("vbof", c3301.valueTR("beaufort")),
        ("vvbf", c3301.valueTR("variantbeaufort")),
    ]
    for trname, tr in trs:
        for primer in ALPHABET:
            consider(
                f"ct-autokey-{trname}-{c3301.r2i(primer)}",
                "".join(auto.ciphertext_autokey_decrypt(page, primer=primer, tr=tr)),
            )
            consider(
                f"pt-autokey-{trname}-{c3301.r2i(primer)}",
                "".join(auto.plaintext_autokey_decrypt(page, primer=primer, tr=tr)),
            )

    # known LP keywords
    keywords = [
        "DIVINITY",
        "FIRFUMFERENFE",
        "CIRCUMFERENCE",
        "WELCOME",
        "WISDOM",
        "PILGRIM",
        "KOAN",
        "INSTAR",
        "CICADA",
    ]
    for kw in keywords:
        rk = keyword_to_runes(kw)
        if not rk:
            continue
        for trname, tr in trs[:3]:
            consider(
                f"{trname}-{kw}",
                "".join(pasc.pasc_decrypt(page, keyword=rk, tr=tr)),
            )

    candidates.sort(reverse=True)
    return candidates


def main() -> None:
    """Run the full attack battery against every page."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, "..", "data", "page0-58.txt")
    pages = load_pages(data_file)

    parable = pages[-1]  # final page is known plaintext
    unsolved = "".join(pages[:-1])

    rnd = "".join(random.choice(ALPHABET) for _ in range(5000))
    random_ref = fitness(rnd)
    plain_ref = fitness(parable)
    # short pages can cherry-pick noise from 800+ affine maps, so demand a
    # score much closer to real plaintext than to random
    threshold = random_ref + 0.55 * (plain_ref - random_ref)

    print(f"pages: {len(pages)}, unsolved runes: {len(unsolved)}")
    print(f"plaintext reference (parable): fitness={plain_ref:.3f} "
          f"nIoC={nioc(parable):.3f} doublets={doublet_rate(parable):.4f}")
    print(f"random reference: fitness={random_ref:.3f} nIoC={nioc(rnd):.3f} "
          f"doublets={doublet_rate(rnd):.4f}")
    print(f"unsolved corpus: nIoC={nioc(unsolved):.3f} "
          f"doublets={doublet_rate(unsolved):.4f}")
    print(f"hit threshold: fitness > {threshold:.3f}\n")

    print("columnar nIoC by period (top 5):")
    periods = []
    for period in range(1, 41):
        cols = ["".join(unsolved[i::period]) for i in range(period)]
        periods.append((sum(nioc(c) for c in cols) / period, period))
    for avg, period in sorted(periods, reverse=True)[:5]:
        print(f"  period {period:2d}: {avg:.4f}")
    print()

    maxlen = max(len(p) for p in pages) + 1
    keystream = [p - 1 for p in itertools.islice(gen_primes_opt(), maxlen)]

    for pi, page in enumerate(pages[:-1]):
        best = page_attack_battery(page, keystream)[0]
        score, name, text = best
        hit = score > threshold
        print(f"page {pi:2d} len={len(page):3d} best={name} fitness={score:.3f}"
              + ("  <<< HIT" if hit else ""))
        if hit:
            print(f"   {to_english(text)}")


if __name__ == "__main__":
    main()
