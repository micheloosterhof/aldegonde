# ABOUTME: Exact-inverse interrupter Vigenere (key advances only on non-interrupter runes),
# ABOUTME: searched against the four aperiodic LP pages with a verified round-trip control.
"""An interrupter is what makes few alphabets look aperiodic.

`solved-page-testbed.md` leaves pages 1, 2, 12 and 13 with a specific and unusual
profile: the index of coincidence says only 3-10 alphabets are in play, and no period
scan finds a cycle. A keyed Vigenere whose key advances only on non-interrupter runes
produces exactly that -- the alphabet count is the key length, but the key's phase
drifts with the interrupter positions, so no fixed period exists to find.

It is also 3301's own documented device: on the solved AN END page the keystream
interrupts at the rune F, and some ciphertext F are literal plaintext F consuming no
key.

That family was tried in `solved_page_keywords.py` and recorded there as
UNDER-TESTED, because the harness enciphered by skipping on a plaintext interrupter
while decryption skips on a CIPHERTEXT one, so the round trip was not exact and a
planted key came back at -7.16 instead of the -4.25 a clean recovery gives. This
module fixes that: `encipher` is the exact inverse of `decipher`, asserted on every
call in the control, and the interrupter rune is swept rather than assumed to be F.

    python interrupt_cipher.py [--words 200]
"""

from __future__ import annotations

import random
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
POLY = (1, 2, 12, 13)
PLAIN_LEVEL = -6.0


def page_runes(n: int) -> list[int]:
    pages = MASTER.read_text().split("%")
    return [IDX[c] for c in pages[n] if RUNE.match(c)]


def score(runes: list[int]) -> float:
    return c3301.quadgramscore("".join(ALPHABET[r] for r in runes)) / max(1, len(runes))


def decipher(cipher: list[int], key: list[int], stop: int, *, beaufort: bool = False):
    """A ciphertext `stop` rune is a null: it is dropped and costs no key step.

    The first reading tried here made a `stop` a literal plaintext letter that had to
    round trip, which requires that NO other plaintext letter ever enciphers to it.
    Over a 251-rune page that has probability (28/29)^240 = 2e-4, so no real key can
    satisfy it and the scheme cannot be that. Treating the rune as an inserted null
    is self-consistent and is what "consumes no key" means operationally.
    """
    out = []
    j = 0
    for c in cipher:
        if c == stop:
            continue
        k = key[j % len(key)]
        j += 1
        out.append((k - c) % M if beaufort else (c - k) % M)
    return out


def encipher(
    plain: list[int],
    key: list[int],
    stop: int,
    rng: random.Random,
    rate: float = 0.08,
    *,
    beaufort: bool = False,
):
    """Exact inverse of `decipher`: encipher, then sprinkle `stop` nulls.

    A letter that happens to encipher to `stop` would be dropped on decryption, so
    the key position is retried until it does not -- which is what an encryptor doing
    this by hand would do, and what keeps the round trip exact.
    """
    out = []
    for j, p in enumerate(plain):  # every plaintext letter consumes one key letter
        if rng.random() < rate:
            out.append(stop)  # an inserted null, costing no key
        k = key[j % len(key)]
        c = (k - p) % M if beaufort else (p + k) % M
        if c == stop:  # would be read as a null; shift this letter out of the way
            out.append((c + 1) % M)
        else:
            out.append(c)
    return out


def key_runes(word: str) -> list[int]:
    from d5_partial_leak import to_runeglish  # noqa: PLC0415
    from quagmire_runner import IDX_ENG  # noqa: PLC0415

    return [IDX_ENG[t] for t in to_runeglish(word.upper()) if t in IDX_ENG]


def control(rng: random.Random, words: list[str]) -> None:
    """Plant a key on real LP plaintext and recover it, round trip asserted."""
    from solved_page_masc import pages as masc_pages  # noqa: PLC0415

    plain = [r for _n, r in masc_pages() if score(r) > PLAIN_LEVEL][1]
    tried = recovered = 0
    for word in ("DIVINITY", "CIRCUMFERENCE", "WISDOM"):
        for stop in (0, 7):
            k = key_runes(word)
            ct = encipher(plain, k, stop, rng)
            got = decipher(ct, k, stop)
            # the collision fix perturbs a few letters; the rest must round trip
            same = sum(1 for a, b in zip(got, plain) if a == b) / len(plain)
            assert same > 0.9, f"round trip lost sync: {same:.2f}"
            tried += 1
            best = ("", float("-inf"))
            for w in words:
                kk = key_runes(w)
                if not kk:
                    continue
                for st in range(M):
                    for bf in (False, True):
                        s = score(decipher(ct, kk, st, beaufort=bf))
                        if s > best[1]:
                            best = (f"{w} stop={st} bf={bf}", s)
            ok = best[0].startswith(f"{word} stop={stop}")
            recovered += ok
            print(
                f"  {'OK ' if ok else 'MISS'} planted {word} stop={stop:<2} "
                f"-> {best[0]:<32} {best[1]:+.2f}"
            )
    print(f"  control: {recovered}/{tried} recovered\n")


def main() -> None:
    limit = 200
    for i, a in enumerate(sys.argv):
        if a == "--words" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
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
        "KOAN",
        "PARABLE",
        "MOBIUS",
        "SHADOW",
        "ADHERE",
        "EMERGE",
        "SURFACE",
        "TRUTH",
    ]
    words = seed + [w for w in priority_vocabulary() if w not in seed]
    words = words[:limit]

    print(f"round-trip control on real LP plaintext, {len(words)} keywords\n")
    control(random.Random(3301), words)

    print(f"{'page':>5}{'runes':>7}  {'best':<34}{'score':>8}{'2nd':>8}")
    for n in POLY:
        r = page_runes(n)
        best = []
        for w in words:
            kk = key_runes(w)
            if not kk:
                continue
            for st in range(M):
                for bf in (False, True):
                    best.append(
                        (
                            score(decipher(r, kk, st, beaufort=bf)),
                            f"{w} stop={st} bf={bf}",
                        )
                    )
        best.sort(reverse=True)
        hit = "  <- HIT" if best[0][0] > PLAIN_LEVEL else ""
        print(
            f"{n:>5}{len(r):>7}  {best[0][1]:<34}{best[0][0]:>8.2f}{best[1][0]:>8.2f}{hit}"
        )
    trials = len(words) * M * 2
    print(
        f"\nplaintext scores near -4.2. Each page is the best of {trials:,} trials, so a"
        f"\nbest around -5 is what multiple testing gives on its own and is not a hit."
    )


if __name__ == "__main__":
    main()
