# ABOUTME: Hill-climbs a 29-rune substitution on the LP transcription pages whose IoC says
# ABOUTME: they are monoalphabetic, to recover real (ciphertext, key, plaintext) triples.
"""Which of the enciphered pages are monoalphabetic, and can their keys be recovered?

`solved-page-testbed.md` records nine enciphered ASCII-convention pages that resist
shifts, Atbash, keyword Vigenere and prime/totient running keys. The index of
coincidence says why the search was aimed wrongly for most of them: IoC is invariant
under any monoalphabetic substitution, and normalised to 29 symbols it splits the
pages in two.

    plaintext pages           1.52 - 1.96
    pages 0, 4, 5, 6, 7       1.63 - 2.06   <- monoalphabetic, same range as plaintext
    pages 1, 2, 12, 13        1.07 - 1.28   <- flatter, so polyalphabetic
    the unsolved corpus       1.000         <- perfectly flat

Five of the nine are simple substitutions on a general keyed alphabet, which shifts
and Atbash cannot reach but hill-climbing can. This recovers them, giving genuine
(ciphertext, key, plaintext) triples rather than another simulation.

The climb is plain steepest-ascent over transpositions of a 29-symbol key, scored by
runeglish quadgrams, with random restarts. `--control` first plants a random key on a
page of real LP plaintext and recovers it, so a failure on the real pages cannot be
blamed on the solver.

    python solved_page_masc.py [--restarts 60] [--control]
"""

from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

from aldegonde import c3301
from aldegonde.stats import ioc

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
M = 29
ALPHABET = c3301.CICADA_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHABET)}
PLAIN_LEVEL = -6.0
MONO_IOC = 1.45  # normalised IoC above this is plaintext-like, so monoalphabetic


def pages() -> list[tuple[int, list[int]]]:
    out = []
    for n, page in enumerate(MASTER.read_text().split("%")):
        if "." not in page:
            continue
        runes = [IDX[c] for c in page if RUNE.match(c)]
        if runes:
            out.append((n, runes))
    return out


def score(runes: list[int]) -> float:
    return c3301.quadgramscore("".join(ALPHABET[r] for r in runes)) / max(1, len(runes))


def apply_key(runes: list[int], key: list[int]) -> list[int]:
    return [key[r] for r in runes]


def climb(runes: list[int], rng: random.Random, restarts: int):
    """Steepest ascent over transpositions, best of `restarts` random starts."""
    best_key, best = None, float("-inf")
    for _ in range(restarts):
        key = list(range(M))
        rng.shuffle(key)
        current = score(apply_key(runes, key))
        improved = True
        while improved:
            improved = False
            for a in range(M):
                for b in range(a + 1, M):
                    key[a], key[b] = key[b], key[a]
                    s = score(apply_key(runes, key))
                    if s > current:
                        current, improved = s, True
                    else:
                        key[a], key[b] = key[b], key[a]
        if current > best:
            best_key, best = list(key), current
    return best, best_key


def english(runes: list[int], limit: int = 70) -> str:
    return "".join(c3301.CICADA_ENGLISH_ALPHABET[r] for r in runes[:limit])


def main() -> None:
    restarts = 60
    for i, a in enumerate(sys.argv):
        if a == "--restarts" and i + 1 < len(sys.argv):
            restarts = int(sys.argv[i + 1])
    rng = random.Random(3301)
    allp = pages()

    if "--control" in sys.argv:
        plain = [(n, r) for n, r in allp if score(r) > PLAIN_LEVEL]
        n, runes = plain[1]
        key = list(range(M))
        rng.shuffle(key)
        ct = apply_key(runes, key)
        got, _k = climb(ct, rng, restarts)
        print(
            f"control: page {n} plaintext {score(runes):+.2f}, "
            f"enciphered {score(ct):+.2f}, recovered {got:+.2f}"
        )
        print(f"  {english(apply_key(ct, _inverse(_k)))}\n")

    triples: list[dict] = []
    print(f"{'page':>5}{'runes':>7}{'IoC':>7}{'kind':>8}{'best':>8}   plaintext head")
    for n, runes in allp:
        v = ioc(runes) * M
        if score(runes) > PLAIN_LEVEL:
            print(
                f"{n:>5}{len(runes):>7}{v:>7.2f}{'PLAIN':>8}{score(runes):>8.2f}   {english(runes, 44)}"
            )
            continue
        if v < MONO_IOC:
            print(
                f"{n:>5}{len(runes):>7}{v:>7.2f}{'poly':>8}{'-':>8}   (flat IoC: not monoalphabetic, skipped)"
            )
            continue
        best, key = climb(runes, rng, restarts)
        hit = " <- HIT" if best > PLAIN_LEVEL else ""
        print(
            f"{n:>5}{len(runes):>7}{v:>7.2f}{'mono':>8}{best:>8.2f}   {english(apply_key(runes, key), 44)}{hit}"
        )
        if best > PLAIN_LEVEL:
            triples.append(
                {
                    "page": n,
                    "runes": len(runes),
                    "ioc": round(v, 3),
                    "score": round(best, 3),
                    "key": key,
                    "plaintext": english(apply_key(runes, key), 10**6),
                }
            )
    _write(triples)


def _write(triples: list[dict]) -> None:
    """Persist the recovered triples so other experiments can validate against them."""
    out = ROOT / "experiments" / "solved_page_triples.json"
    out.write_text(json.dumps(triples, indent=1, ensure_ascii=False))
    print(
        f"\n{len(triples)} (ciphertext, key, plaintext) triples written to {out.name}"
    )


def _inverse(key: list[int]) -> list[int]:
    inv = [0] * M
    for i, k in enumerate(key):
        inv[k] = i
    return inv


if __name__ == "__main__":
    main()
