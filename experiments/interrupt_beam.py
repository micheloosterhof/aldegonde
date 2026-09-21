# ABOUTME: Beam-searches the keystream skip positions of the interrupted Vigenere pages,
# ABOUTME: recovering full plaintext and then reporting which rune sits at each skip.
"""Find the interrupts instead of guessing them.

Page 1 decrypts under plain Vigenere with the key DIVINITY for its first 49 runes --
"WELCOME WELCOME PILGRIM TO THE GREAT JOURNEY TOWARD THE END" -- and then loses sync.
That is an interrupted keystream: at some positions the key does not advance. Guessing
which rune triggers the interrupt (`interrupt_cipher.py`) recovers different stretches
for different guesses and none of them cleanly, because the trigger is a property of
the text the scribe marked, not a rune this project can name in advance.

So search the skip positions directly. At each ciphertext rune the keystream either
advances or holds; a beam over those binary choices, scored by runeglish trigrams on
the plaintext produced so far, recovers the whole page without any assumption about
what causes a hold. Once the positions are known, the rule can simply be read off:
print the ciphertext and plaintext rune at every recovered skip and see what they
share.

Two conventions are searched, because "consumes no key" is ambiguous:

    hold   the rune is decrypted with the key letter already in hand, key stays put
    drop   the rune is a null, emitted nowhere, key stays put

    python interrupt_beam.py [--beam 400] [--key DIVINITY] [--page 1]
"""

from __future__ import annotations

import sys
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from interrupt_cipher import key_runes, page_runes, score  # noqa: E402

M = 29
ALPHABET = c3301.CICADA_ALPHABET
ENG = c3301.CICADA_ENGLISH_ALPHABET
TRI = c3301.trigrams
FLOOR = -9.0


def tri_score(a: int, b: int, c: int) -> float:
    import math  # noqa: PLC0415

    v = TRI.get(ALPHABET[a] + ALPHABET[b] + ALPHABET[c])
    return math.log(v) if v else FLOOR


def beam_search(cipher: list[int], key: list[int], width: int, mode: str):
    """Best (score, plaintext, skip positions) over keystream hold/advance choices."""
    klen = len(key)
    # state: (score, key index, last two plaintext runes, output, skips)
    start = (0.0, 0, (0, 0), [], [])
    beam = [start]
    for i, c in enumerate(cipher):
        nxt = []
        for sc, j, tail, out, skips in beam:
            # normal: consume a key letter
            p = (c - key[j % klen]) % M
            s = sc + (tri_score(tail[0], tail[1], p) if out else 0.0)
            nxt.append((s, j + 1, (tail[1], p), [*out, p], skips))
            # interrupt: the key does not advance
            if mode == "hold":
                q = (c - key[(j - 1) % klen]) % M if j else p
                s2 = sc + (tri_score(tail[0], tail[1], q) if out else 0.0)
                nxt.append((s2, j, (tail[1], q), [*out, q], [*skips, i]))
            else:  # drop
                nxt.append((sc, j, tail, out, [*skips, i]))
        nxt.sort(key=lambda t: -t[0])
        beam = nxt[:width]
    return max(beam, key=lambda t: t[0])


def main() -> None:
    width, keyword, page = 400, "DIVINITY", 1
    for i, a in enumerate(sys.argv):
        if a == "--beam" and i + 1 < len(sys.argv):
            width = int(sys.argv[i + 1])
        if a == "--key" and i + 1 < len(sys.argv):
            keyword = sys.argv[i + 1]
        if a == "--page" and i + 1 < len(sys.argv):
            page = int(sys.argv[i + 1])

    cipher = page_runes(page)
    key = key_runes(keyword)
    print(f"page {page}, {len(cipher)} runes, key {keyword} = {key}\n")

    for mode in ("hold", "drop"):
        _s, _j, _t, out, skips = beam_search(cipher, key, width, mode)
        txt = "".join(ENG[x] for x in out)
        print(f"[{mode}] {len(skips)} skips, quadgram {score(out):+.2f}")
        print(f"   {txt[:150]}")
        if len(txt) > 150:
            print(f"   {txt[150:300]}")
        if skips:
            runes = [ALPHABET[cipher[i]] for i in skips]
            eng = [ENG[cipher[i]] for i in skips]
            print(f"   skip positions: {skips[:18]}")
            print(f"   ciphertext rune at each skip: {' '.join(eng[:18])}")
            from collections import Counter  # noqa: PLC0415

            top = Counter(runes).most_common(4)
            print(f"   commonest: {top}")
        print()


if __name__ == "__main__":
    main()
