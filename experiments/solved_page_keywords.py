# ABOUTME: Cracks the still-enciphered ASCII-convention LP pages with keyed Vigenere,
# ABOUTME: building real (ciphertext, key, plaintext) triples to validate this project against.
"""Real LP ciphertext with a recovered key, instead of another simulation.

`solved_page_testbed.py` showed that six of the fifteen ASCII-convention pages are
plaintext in the transcription and nine are still enciphered, and that the
shift/Atbash family does not crack those nine. The LP's front matter is known to use
keyed ciphers, so the obvious next family is Vigenere over the 29 runes with a keyword
drawn from the puzzle's own vocabulary.

Why bother with pages other people have already solved: every positive control in this
project is built by enciphering prose with a planted key, which cannot catch a
tokenization bug, a register mismatch, or a scorer that is blind to real LP text,
because the same code made the ciphertext. A cracked page gives a genuine triple --
the author's ciphertext, the author's key, the author's plaintext -- and anything that
claims to score or search LP-like text should survive being pointed at it.

Four families, each keyed by one word:

    vigenere              p = c - k
    beaufort              p = k - c
    atbash then vigenere  atbash applied before the shift
    vigenere then atbash  atbash applied after

A hit is a page whose best key beats the runner-up by a clear margin AND scores near
the plaintext pages' own level (about -4.2 nats per rune), which those six pages fix.

    python solved_page_keywords.py [--words N]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
RUNE = re.compile(r"[ᚠ-᛿]")
M = 29
ALPHABET = c3301.CICADA_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHABET)}
PLAIN_LEVEL = -6.0  # the six plaintext pages sit near -4.2; ciphertext near -9
F_RUNE = 0  # the interrupter on the solved AN END page


def pages() -> list[tuple[int, list[int], bool]]:
    """(page number, rune indices, is_plaintext) for the ASCII-convention pages."""
    out = []
    for n, page in enumerate(MASTER.read_text().split("%")):
        if "." not in page:
            continue
        runes = [IDX[c] for c in page if RUNE.match(c)]
        if not runes:
            continue
        out.append((n, runes, score(runes) > PLAIN_LEVEL))
    return out


def score(runes: list[int]) -> float:
    return c3301.quadgramscore("".join(ALPHABET[r] for r in runes)) / max(1, len(runes))


def key_runes(word: str) -> list[int]:
    """Keyword as rune indices, WITHOUT de-duplication -- this is a key stream."""
    from d5_partial_leak import to_runeglish  # noqa: PLC0415
    from quagmire_runner import IDX_ENG  # noqa: PLC0415

    return [IDX_ENG[t] for t in to_runeglish(word.upper()) if t in IDX_ENG]


def decrypt(
    runes: list[int], key: list[int], family: str, *, interrupt: bool = False
) -> list[int]:
    """Decrypt under one family. With `interrupt`, a ciphertext F consumes no key.

    That is 3301's own convention on the solved AN END page: some ciphertext F runes
    are literal plaintext F and the keystream does not advance past them.
    """
    out = []
    j = 0
    for c in runes:
        if interrupt and c == F_RUNE:
            out.append(F_RUNE)
            continue
        k = key[j % len(key)]
        j += 1
        x = c
        if family.startswith("atbash then"):
            x = (M - 1 - x) % M
        p = (k - x) % M if "beaufort" in family else (x - k) % M
        if family.endswith("then atbash"):
            p = (M - 1 - p) % M
        out.append(p)
    return out


FAMILIES = ("vigenere", "beaufort", "atbash then vigenere", "vigenere then atbash")


def running_keys(n: int) -> list[tuple[str, list[int]]]:
    """The keystreams 3301 used on the solved pages: primes, and Euler's totient."""
    from aldegonde.maths import primes as prime_list  # noqa: PLC0415

    ps = prime_list(40_000)[: n + 10]
    out = [
        ("primes-1", [(p - 1) % M for p in ps]),
        ("primes", [p % M for p in ps]),
    ]
    tot = []
    for i in range(1, n + 10):
        c = sum(1 for k in range(1, i + 1) if _gcd(i, k) == 1)
        tot.append(c % M)
    out.append(("totient", tot))
    return out


def _gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def vocabulary(limit: int) -> list[str]:
    from quagmire_ungated_sweep import priority_vocabulary  # noqa: PLC0415

    seed = [
        "DIVINITY",
        "CIRCUMFERENCE",
        "FIRFUMFERENFE",
        "INSTAR",
        "TUNNELING",
        "WELCOME",
        "WISDOM",
        "PILGRIM",
        "PRIMES",
        "TOTIENT",
        "CICADA",
        "LIBER",
        "PRIMUS",
        "KOAN",
        "PARABLE",
        "MOBIUS",
        "SHADOW",
        "ADHERE",
        "EMERGE",
        "SURFACE",
        "TRUTH",
        "SACRED",
        "INSTRUCTION",
        "WARNING",
        "AMASS",
        "PRIMALITY",
        "CONSUMPTION",
        "PRESERVATION",
        "BEHAVIOR",
    ]
    rest = [w for w in priority_vocabulary() if w not in seed]
    return (seed + rest)[:limit]


def main() -> None:
    limit = 400
    for i, a in enumerate(sys.argv):
        if a == "--words" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])

    allp = pages()
    plain = [n for n, _r, p in allp if p]
    cipher = [(n, r) for n, r, p in allp if not p]
    words = vocabulary(limit)
    keys = [(w, key_runes(w)) for w in words]
    keys = [(w, k) for w, k in keys if k]
    print(f"plaintext pages {plain}")
    print(
        f"{len(cipher)} enciphered pages, {len(keys)} keywords, {len(FAMILIES)} families\n"
    )

    print(f"{'page':>5}{'runes':>7}  {'best':<38}{'score':>8}{'2nd':>8}{'gap':>7}")
    for n, runes in cipher:
        best = []
        pool = keys + running_keys(len(runes))
        for w, k in pool:
            for fam in FAMILIES:
                for intr in (False, True):
                    tag = f"{w} [{fam}{'+F' if intr else ''}]"
                    best.append((score(decrypt(runes, k, fam, interrupt=intr)), tag))
        best.sort(reverse=True)
        gap = best[0][0] - best[1][0]
        flag = "  <- HIT" if best[0][0] > PLAIN_LEVEL else ""
        print(
            f"{n:>5}{len(runes):>7}  {best[0][1]:<38}{best[0][0]:>8.2f}"
            f"{best[1][0]:>8.2f}{gap:>7.2f}{flag}"
        )
        if best[0][0] > PLAIN_LEVEL:
            w, fam = best[0][1].split(" [")
            fam = fam[:-1]
            intr = fam.endswith("+F")
            k = dict(keys + running_keys(len(runes)))[w]
            txt = "".join(
                ALPHABET[x]
                for x in decrypt(runes, k, fam.removesuffix("+F"), interrupt=intr)[:60]
            )
            print("        ", end="")
            c3301.print_english(txt)
    print(
        f"\nplaintext pages score near {score(pages()[3][1]):.2f}; a real hit must reach that."
    )


if __name__ == "__main__":
    main()
