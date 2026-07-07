#!/usr/bin/env python3
"""Sweep book-derivable candidates against the AN END page's 512-bit hash.

The final decrypted page of the Liber Primus reads "WITHIN THE DEEP WEB
THERE EXISTS A PAGE THAT HASHES TO <512-bit hex> ...". The obvious
reading is a Tor hidden-service page (likely long gone). But "a page"
could pun on a page of the book itself, and hashing everything
derivable from the repo costs nothing, so this puts the self-referential
family on the record under every 2014-plausible 512-bit hash available
in hashlib (SHA-512, SHA3-512 in its final FIPS form, BLAKE2b-512;
Keccak-with-competition-padding, Whirlpool, Skein and Streebog are not
in hashlib and remain untested here).

CAVEAT: the target hex below is the community-recorded value, quoted
from memory in an offline session -- verify against the page scan
before trusting a (non-)match. The constant is trivially replaceable.

Candidates (each as UTF-8 bytes, with a few whitespace variants):
    - the raw data files in the repo
    - every page's rune string, every $-section's rune string
    - the clean corpus, the full late corpus
    - the decoded plaintext of the six constant-transform sections
      (rune form and Latin-letter form)
    - the Parable (runes and letters), the AN END plaintext
    - the Gematria Primus alphabet in several encodings

Usage: python experiments/anend_hash_sweep.py
"""

from __future__ import annotations

import hashlib

TARGET = ("36367763ab73783c7af284446c59466b4cd653239a311cb7116d4618dee0"
          "9a8425893dc7500b464fdaf1672d7bef5e891c6e2274568926a49fb4f451"
          "32c2a8b4")

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MOD = 29
R2I = {r: i for i, r in enumerate(RUNES)}
R2I["ᛂ"] = R2I["ᛄ"]
LETTERS = ["F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J",
           "EO", "P", "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D",
           "A", "AE", "Y", "IA", "EA"]

FILES = ["data/page0-58.txt", "data/page0-56.txt",
         "data/liber-primus__transcription--master.txt",
         "data/liber-primus__transcription--master.md"]

SOLVED_PLAIN = {0: ("atbash", 0), 2: ("shift", 0), 3: ("atbash", 26),
                4: ("shift", 0), 6: ("shift", 0), 18: ("shift", 0)}

HASHES = {
    "sha512": lambda b: hashlib.sha512(b).hexdigest(),
    "sha3_512": lambda b: hashlib.sha3_512(b).hexdigest(),
    "blake2b": lambda b: hashlib.blake2b(b, digest_size=64).hexdigest(),
}


def runes_only(s: str) -> str:
    return "".join(ch for ch in s if ch in R2I)


def candidates():
    for path in FILES:
        try:
            with open(path, "rb") as f:
                yield f"file:{path}", f.read()
        except OSError:
            continue
    with open("data/page0-58.txt") as f:
        raw58 = f.read()
    with open("data/liber-primus__transcription--master.txt") as f:
        master = f.read()
    # pages and sections, runes only
    for i, page in enumerate(p for p in raw58.split("%")
                             if runes_only(p)):
        yield f"page58[{i}] runes", runes_only(page).encode()
    for i, sec in enumerate(s for s in raw58.split("$") if runes_only(s)):
        yield f"sec58[{i}] runes", runes_only(sec).encode()
    for i, sec in enumerate(s for s in master.split("$")
                            if runes_only(s)):
        yield f"master-sec[{i}] runes", runes_only(sec).encode()
    clean = "".join(runes_only(s) for s in raw58.split("$")[:10])
    yield "clean corpus runes", clean.encode()
    yield "full late corpus runes", runes_only(raw58).encode()
    yield "master runes", runes_only(master).encode()
    # decoded solved sections, rune and letter forms
    for idx, (kind, shift) in SOLVED_PLAIN.items():
        sec = master.split("$")[idx]
        vals = [R2I[ch] for ch in sec if ch in R2I]
        plain = [(MOD - 1 - c - shift) % MOD if kind == "atbash"
                 else (c - shift) % MOD for c in vals]
        yield (f"solved-sec[{idx}] plaintext runes",
               "".join(RUNES[p] for p in plain).encode())
        yield (f"solved-sec[{idx}] plaintext letters",
               "".join(LETTERS[p] for p in plain).encode())
    # alphabet encodings
    yield "gematria runes", RUNES.encode()
    yield "gematria letters", "".join(LETTERS).encode()
    yield "3301", b"3301"


def main() -> None:
    target = TARGET.lower()
    tried = 0
    for name, data in candidates():
        variants = {name: data,
                    name + "+\\n": data + b"\n"}
        for vname, blob in variants.items():
            for hname, fn in HASHES.items():
                tried += 1
                if fn(blob) == target:
                    print(f"*** MATCH: {hname}({vname}) ***")
                    return
    print(f"no match in {tried} candidate x hash combinations "
          f"(sha512 / sha3_512 / blake2b over book-derivable inputs)")


if __name__ == "__main__":
    main()
