# ABOUTME: Re-enciphers every recovered plaintext with its recorded key and asserts the
# ABOUTME: result is the LP's actual ciphertext, so the testbed cannot rot unnoticed.
"""The testbed is only worth something if it round-trips.

`solved_page_triples.json` holds nine (ciphertext, key, plaintext) triples recovered
from the LP's front matter -- five monoalphabetic pages and four interrupted Vigenere
pages. Six results in this directory now lean on them, so the claim that each key
really produces the author's ciphertext should be checked rather than assumed.

This re-enciphers each recorded plaintext under its recorded key and compares the
result to the transcription, rune for rune. It is not a scoring test: it either
reproduces the ciphertext exactly or it does not.

The plaintext is stored as rune INDICES, not as its English rendering. The rendering
is lossy -- TH, EA, NG, OE and the rest are single runes written with multi-letter
names -- so parsing it back is ambiguous, and a first version of this check failed
eight of nine triples for that reason alone while the triples themselves were sound.

All four Vigenere pages share one convention, which the check also pins: a ciphertext
F at an interrupt position is a literal plaintext F and consumes no key letter. Page 2
was briefly recorded with a skip on a D, which this convention rejects; the correct
skip is the F two positions later.

    python verify_triples.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
TRIPLES = ROOT / "experiments" / "solved_page_triples.json"
RUNE = re.compile(r"[ᚠ-᛿]")
M = 29
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
ENG = c3301.CICADA_ENGLISH_ALPHABET
F_RUNE = 0


def ciphertext(page: int) -> list[int]:
    chunk = MASTER.read_text().split("%")[page]
    return [IDX[c] for c in chunk if RUNE.match(c)]


def encipher(plain: list[int], triple: dict) -> list[int]:
    """Re-encipher under the recorded key, reproducing the interrupt convention."""
    if triple["cipher"] == "monoalphabetic":
        inverse = [0] * M
        for i, k in enumerate(triple["key"]):
            inverse[k] = i
        return [inverse[p] for p in plain]
    key = triple["key"]
    off = triple["key_offset"]
    rot = key[off:] + key[:off]
    skips = set(triple["interrupts"])
    out, j = [], 0
    for i, p in enumerate(plain):
        if i in skips:
            out.append(F_RUNE)
            continue
        out.append((p + rot[j % len(rot)]) % M)
        j += 1
    return out


def main() -> None:
    triples = json.loads(TRIPLES.read_text())
    print(f"{len(triples)} triples\n")
    print(
        f"{'page':>5}{'cipher':>24}{'keyword':>16}{'runes':>7}{'intr':>6}  round trip"
    )
    failures = 0
    for t in triples:
        ct = ciphertext(t["page"])
        plain = t["plaintext_runes"]
        got = encipher(plain, t)
        ok = got == ct
        failures += not ok
        print(
            f"{t['page']:>5}{t['cipher']:>24}{t.get('keyword', '-'):>16}"
            f"{t['runes']:>7}{len(t['interrupts']):>6}  {'OK' if ok else 'FAILED'}"
        )
    print(
        f"\n{len(triples) - failures}/{len(triples)} reproduce the ciphertext exactly"
    )
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
