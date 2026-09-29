# ABOUTME: Shows the five monoalphabetic front-matter pages are Atbash and Atbash-plus-3,
# ABOUTME: correcting the claim that their keys are out of reach of shifts and Atbash.
"""The five monoalphabetic pages are Atbash. The testbed says they cannot be.

**This file re-derives a solved result.** `hypotheses/solved-page-testbed.md` already
records pages 0, 4, 5, 6 and 7 as monoalphabetic, already recovers their plaintext, and
already stores the keys in `experiments/solved_page_triples.json`. Running an affine sweep
over them was duplicated work and is kept only for what it found on the way.

That file explains the keys as "simple substitutions on a general keyed alphabet -- which
shifts and Atbash cannot reach, and which is why the earlier family missed them."

**That is wrong.** An affine sweep over `x -> a*x + b`, 812 keys, recovers all five at
7.6 to 8.4 sigma above a random-key null:

| page | runes | best affine key | equivalently | score/rune |
|---|---|---|---|---|
| 0 | 184 | a=28, b=28 | **plain Atbash** | -4.23 |
| 4 | 209 | a=28, b=2 | Atbash then shift 3 | -4.05 |
| 5 | 210 | a=28, b=2 | Atbash then shift 3 | -4.09 |
| 6 | 218 | a=28, b=2 | Atbash then shift 3 | -4.19 |
| 7 | 141 | a=28, b=2 | Atbash then shift 3 | -4.20 |

a = 28 is -1 mod 29, so `x -> 28x + b` is a reflection: `x -> (28 + k) - x` with k = b - 28.
Atbash is exactly k = 0. **Page 0 is plain Atbash and the other four are Atbash followed
by a shift of three** -- a 29-key family, not a general keyed alphabet.

The scores land in the -4.05 to -4.23 band that the author's six plaintext pages set
(-4.39 for the pooled plaintext, -6.64 for the same text shuffled), so these are the same
decryptions the testbed reports, reached by a much smaller family.

## Why it matters

The testbed uses "shifts and Atbash cannot reach these" to explain why an earlier search
missed them. That explanation cannot be right, so whatever the earlier search did wrong is
still unexplained -- a narrower family than claimed, a bug, or the interrupter handling.
Worth knowing before trusting that search's negative results elsewhere.

Note also that the affine sweep here handles no interrupter at all and still lands in the
plaintext band, so the interrupts on these five pages are few enough not to matter for
identification.

## The four that do not break

Pages 1, 2, 12 and 13 reach only -7.2 to -8.1 per rune at 3.4 to 4.1 sigma, nowhere near
the plaintext band. Their IoC of 1.07-1.28 says polyalphabetic with a short period, which
the testbed already names as the open target.

    python break_the_front_matter_pages.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
ALPHA = c3301.CICADA_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHA)}
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
PAGES = (4, 6, 0, 5, 7, 13, 1, 2, 12)
PLAIN_PAGES = (3, 8, 9, 10, 11, 14)
N = 29


def runes_of(page: int) -> list[int]:
    chunks = MASTER.read_text().split("%")
    return [IDX[c] for c in chunks[page] if RUNE.match(c)]


def score(v) -> float:
    return c3301.quadgramscore("".join(ALPHA[x] for x in v))


def readable(v) -> str:
    return "".join(ENGLISH[x] for x in v)


def best_affine(v):
    """Highest-scoring x -> a*x + b over all invertible a, plus the reversed text."""
    out = []
    for text, tag in ((v, ""), (v[::-1], " reversed")):
        for a in range(1, N):
            if np.gcd(a, N) != 1:
                continue
            for b in range(N):
                cand = [(a * x + b) % N for x in text]
                out.append((score(cand), f"a={a} b={b}{tag}", cand))
    out.sort(key=lambda r: -r[0])
    return out


def main() -> None:
    plain = [x for p in PLAIN_PAGES for x in runes_of(p)]
    print(f"Calibration on the author's own plaintext ({len(plain)} runes):")
    print(
        f"  quadgram score per rune, true plaintext : {score(plain) / len(plain):+.3f}"
    )
    scrambled = list(plain)
    rng = np.random.default_rng(3301)
    rng.shuffle(scrambled)
    print(
        f"  the same text shuffled                  : {score(scrambled) / len(scrambled):+.3f}\n"
    )

    print("Best affine key per page, scored per rune against a random-key null.\n")
    print(
        f"{'page':>5}{'runes':>7}{'best key':>18}{'score/rune':>12}{'null':>18}{'z':>8}"
    )
    for page in PAGES:
        v = runes_of(page)
        ranked = best_affine(v)
        top, key, cand = ranked[0]
        rest = np.array([s / len(v) for s, _, _ in ranked[1:]])
        z = (top / len(v) - rest.mean()) / rest.std(ddof=1)
        print(
            f"{page:>5}{len(v):>7}{key:>18}{top / len(v):>12.3f}"
            f"{f'{rest.mean():+.3f} +- {rest.std(ddof=1):.3f}':>18}{z:>8.2f}"
        )

    print("\nThe two highest-scoring readings, first 60 runes each:\n")
    scored = []
    for page in PAGES:
        v = runes_of(page)
        top, key, cand = best_affine(v)[0]
        scored.append((top / len(v), page, key, cand))
    for s, page, key, cand in sorted(scored, reverse=True)[:2]:
        print(f"  page {page}, {key}, {s:+.3f}/rune")
        print(f"    {readable(cand)[:60]}")


if __name__ == "__main__":
    main()
