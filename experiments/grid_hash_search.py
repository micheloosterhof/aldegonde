# ABOUTME: Tests whether any window of the number grids' 176 bytes is a digest of Liber
# ABOUTME: Primus content, which is the reading the AN END page itself points at.
"""The book says a page hashes to something. The grids are the only bytes in the book.

`number-grids-are-bytes.md` decodes master chunks 65 and 66 to 176 uniform bytes and
leaves one loose end: if those bytes are a digest, 176 is not a digest length, so a
digest would sit inside them as a window.

The motivation is not generic. The solved AN END page reads

    WITHIN THE DEEP WEB THERE EXISTS A PAGE THAT HASHES TO IT. IT IS THE DUTY OF
    EUERY PILGRIM TO SEEC OUT THIS PAGE

so the author states that a page of this book hashes to something. This checks whether
the something is written in the book.

Every window of every digest length is indexed, under four readings of the grid -- the
byte order matters here where it did not for the uniformity tests:

    row-major, column-major, each forwards and reversed

Against that index, digests of every plausible Liber Primus string: each master chunk's
runes (as Unicode text, as UTF-8, and as raw rune indices), each solved page's recovered
plaintext in both its English rendering and its rune indices, the whole body, and the
named strings the book uses as keys.

A hit is a 128-hex-digit coincidence and needs no significance test. A miss is reported
as the size of the search, since that is all a miss can be worth.

    python grid_hash_search.py
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from number_grid_bytes import grid_bytes  # noqa: E402

from aldegonde import c3301  # noqa: E402

MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
TRIPLES = ROOT / "experiments" / "solved_page_triples.json"
RUNE = re.compile(r"[ᚠ-᛿]")
ALGOS = ("md5", "sha1", "sha256", "sha512")
COLS = 8


def readings() -> dict[str, bytes]:
    """The four orders a reader could take the grid tokens in."""
    per = grid_bytes()
    out: dict[str, bytes] = {}
    for name, vals in (("65+66", per[65] + per[66]), ("66+65", per[66] + per[65])):
        rows = [vals[i : i + COLS] for i in range(0, len(vals), COLS)]
        colmajor = [r[c] for c in range(COLS) for r in rows if c < len(r)]
        out[f"{name} row-major"] = bytes(vals)
        out[f"{name} row-major reversed"] = bytes(vals[::-1])
        out[f"{name} column-major"] = bytes(colmajor)
        out[f"{name} column-major reversed"] = bytes(colmajor[::-1])
    return out


def windows(data: bytes) -> dict[bytes, int]:
    """Every window of every digest length, mapped to its offset."""
    out: dict[bytes, int] = {}
    for size in {hashlib.new(a).digest_size for a in ALGOS}:
        for i in range(len(data) - size + 1):
            out.setdefault(data[i : i + size], i)
    return out


def candidates() -> dict[str, bytes]:
    """Every plausible Liber Primus string, in every plausible encoding."""
    out: dict[str, bytes] = {}
    chunks = MASTER.read_text().split("%")
    idx = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
    body: list[int] = []
    for n, chunk in enumerate(chunks):
        runes = "".join(c for c in chunk if RUNE.match(c))
        if not runes:
            continue
        codes = bytes(idx[c] for c in runes)
        body += list(codes)
        out[f"chunk {n} runes utf8"] = runes.encode()
        out[f"chunk {n} runes indices"] = codes
        out[f"chunk {n} raw"] = chunk.encode()
    out["all runes utf8"] = "".join(
        c for chunk in chunks for c in chunk if RUNE.match(c)
    ).encode()
    out["all runes indices"] = bytes(body)
    out["master file"] = MASTER.read_bytes()

    for t in json.loads(TRIPLES.read_text()):
        tag = f"page {t['page']} plaintext"
        out[f"{tag} english"] = t["plaintext"].encode()
        out[f"{tag} indices"] = bytes(t["plaintext_runes"])
        out[f"{tag} runes utf8"] = "".join(
            c3301.CICADA_ALPHABET[r] for r in t["plaintext_runes"]
        ).encode()

    for s in (
        "3301",
        "CICADA",
        "CICADA 3301",
        "CICADA3301",
        "AN END",
        "ANEND",
        "PARABLE",
        "DIVINITY",
        "FIRFUMFERENFE",
        "AN INSTRUCTION",
        "A KOAN",
        "",
    ):
        out[f"literal {s!r}"] = s.encode()
    return out


def main() -> None:
    reads = readings()
    index: dict[bytes, tuple[str, int]] = {}
    for name, data in reads.items():
        for w, off in windows(data).items():
            index.setdefault(w, (name, off))

    cands = candidates()
    tested = 0
    for label, blob in cands.items():
        for algo in ALGOS:
            d = hashlib.new(algo, blob).digest()
            tested += 1
            if d in index:
                name, off = index[d]
                print(f"HIT: {algo} of {label} at {name} offset {off}")
                return

    print(f"grid readings indexed: {len(reads)}")
    print(f"distinct windows: {len(index):,} over digest sizes 16, 20, 32, 64")
    print(f"strings hashed: {len(cands)} x {len(ALGOS)} algorithms = {tested:,} digests")
    print("\nno window of the grids is a digest of any of them.")
    print(
        "\nThe search is not exhaustive and cannot be: a digest of a string this"
        "\nproject does not hold would not be found. What it rules out is the"
        "\nself-referential reading -- that the grids hash the book's own pages."
    )


if __name__ == "__main__":
    main()
