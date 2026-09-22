# ABOUTME: Shows the passthrough interrupter follows the cipher type rather than the
# ABOUTME: production phase, removing it from the list of conventions changing at page 15.
"""The interrupter is not a fourth convention changing at page 15.

`one-production-break-at-page-fifteen.md` lists the interrupter as the obvious candidate
for a fourth observable switching at the break, and says locating its change point "needs
a key-free proxy that does not yet exist". **Both halves of that are wrong**, and this
file corrects them.

The proxy exists and `interrupter_rule.py` already uses it. The rule is exact: every
interrupt position is a plaintext F passed through literally, and nothing else is, on all
five interrupted pages. So a passed-through F appears in the ciphertext *as* rune F, and
the **rune-F rate** is a key-free observable.

And the convention does not change at page 15, because it never belonged to a phase:

| page | cipher | interrupts | phase |
|---|---|---|---|
| 0, 4, 5, 6, 7 | monoalphabetic | **0** | before the break |
| 1, 2, 12, 13 | interrupted vigenere | 6, 3, 2, 0 | before the break |
| 3, 8-11, 14 | plaintext | none to have | before the break |
| **71** | **prime running key** | **1** | **after the break** |

A monoalphabetic cipher has no keystream to interrupt, so the convention *cannot* appear
on those pages, and it does not. It appears on every polyalphabetic page the author
solved -- including page 71, which sits after the production break. There is no change
point to find because the interrupter tracks the cipher, not the scribe.

## What the body's failure does mean

The body still fails the test, and that is a statement about its cipher:

    the author's plaintext F rate     0.0149 +- 0.0023   (2,882 runes)
    predicted with passthrough        0.0489
    the body's rune-F rate            0.0354 +- 0.0016   z = -4.87
    predicted without passthrough     0.0345             z = +0.61

The body sits exactly where no passthrough puts it. So whatever the body's cipher does,
it does not emit plaintext runes literally -- which is a constraint on the mechanism and
carries nothing about who wrote the page or when.

`interrupter_rule.py` states the scope this leaves: the bound applies only to interrupters
that **emit a rune**. A clock perturbation that still enciphers leaves no unigram trace,
and the body's preventer is exactly that, so it is untouched.

## The page-15 list, corrected

Three observables change at the break, not four: the joining rate, the mark rate and the
line measure. The 13-dot is a fourth difference but cannot be scanned -- it simply does
not occur before page 15 -- and the interrupter is not a difference of that kind at all.

    python the_interrupter_tracks_the_cipher.py
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_plaintext_register import MASTER, PLAIN_PAGES, TRIPLES  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ANNOTATION = re.compile(r"^[\s0-9-]*$")
RUNE_F = c3301.CICADA_ALPHABET[0]
BREAK = 15


def runes_of(page: str) -> list[str]:
    text = "\n".join(
        line
        for line in page.replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    return RUNE.findall(text)


def main() -> None:
    pages = MASTER.read_text().split("%")
    triples = {t["page"]: t for t in json.loads(TRIPLES.read_text())}

    print("Every solved page, by cipher and by which side of the break it sits on.\n")
    print(
        f"{'page':>5}  {'cipher':<22}{'runes':>7}{'interrupts':>12}"
        f"{'rune F':>8}{'phase':>16}"
    )
    by_cipher = {}
    for n in sorted(set(PLAIN_PAGES) | set(triples)):
        runes = runes_of(pages[n])
        if len(runes) < 60:
            continue
        cipher = "plaintext" if n in PLAIN_PAGES else triples[n]["cipher"]
        interrupts = len(triples[n]["interrupts"]) if n in triples else None
        f = sum(1 for x in runes if x == RUNE_F)
        phase = "before the break" if n < BREAK else "AFTER the break"
        print(
            f"{n:>5}  {cipher:<22}{len(runes):>7}"
            f"{('n/a' if interrupts is None else interrupts):>12}{f:>8}{phase:>16}"
        )
        if interrupts is not None:
            got = by_cipher.setdefault(cipher, [0, 0])
            got[0] += interrupts
            got[1] += 1

    print("\nInterrupts by cipher, which is what they track.\n")
    print(f"{'cipher':<24}{'pages':>7}{'interrupts':>12}")
    for cipher, (total, count) in sorted(by_cipher.items()):
        print(f"{cipher:<24}{count:>7}{total:>12}")
    print("\nA monoalphabetic cipher has no keystream to interrupt, so the convention")
    print("cannot appear there. It appears on every polyalphabetic page, on both sides")
    print("of the break, so there is no change point to find.")

    plaintext = [x for n in PLAIN_PAGES for x in runes_of(pages[n])]
    solved_plain = plaintext + [
        c3301.CICADA_ALPHABET[i] for t in triples.values() for i in t["plaintext_runes"]
    ]
    q = sum(1 for x in solved_plain if x == RUNE_F) / len(solved_plain)
    q_se = math.sqrt(q * (1 - q) / len(solved_plain))
    body = [x for n in range(BREAK, len(pages)) for x in runes_of(pages[n])]
    observed = sum(1 for x in body if x == RUNE_F) / len(body)
    se = math.sqrt(observed * (1 - observed) / len(body))

    print("\nWhat the body's failure constrains: the cipher, not the phase.\n")
    print(
        f"  the author's plaintext F rate   {q:.4f} +- {q_se:.4f}   "
        f"({len(solved_plain):,} runes)"
    )
    print(
        f"  the body's rune-F rate          {observed:.4f} +- {se:.4f}   "
        f"({len(body):,} runes)"
    )
    for label, predicted, predicted_se in (
        ("with passthrough", q + (1 - q) / 29, q_se * (1 - 1 / 29)),
        ("without passthrough", 1 / 29, 0.0),
    ):
        z = (observed - predicted) / math.hypot(se, predicted_se)
        print(f"  predicted {label:<22}{predicted:.4f}   z = {z:+.2f}")

    print(
        "\nThe body sits where no passthrough puts it, so its cipher does not emit"
        "\nplaintext runes literally. The bound reaches only interrupters that EMIT a"
        "\nrune; a clock perturbation that still enciphers leaves no unigram trace, and"
        "\nthe body's preventer is exactly that."
    )


if __name__ == "__main__":
    main()
