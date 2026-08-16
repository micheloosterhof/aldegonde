# ABOUTME: Builds data/register_vocab.txt -- the Cicada 3301 register vocabulary for
# ABOUTME: cribbing: each word with its source and its runeglish transcoding.
"""Assemble the authentic Cicada register into one reusable file.

Sources, kept and labelled:
  * lp-solved     -- words of the recovered solved Liber Primus pages
  * cicada2014    -- solved English from ~/src/cicada-2014/stage11 (AN END, the
                     Parable, the enlightenment message)
  * cicada2012-13 -- the canonical 2012/2013 solved messages
  * lore          -- curated 3301 vocabulary not otherwise captured

Runeglish (Gematria Primus) sources are kept as-is and transliterated to English;
English sources are transcoded to runeglish with the shared digraph rules. The
crib-relevant column is the runeglish; the English and source are for the reader.
Output columns (tab-separated): runeglish  english  sources
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402, I001
from crib_phrase_search import plaintext_phrases  # noqa: E402
from runeglish_frequency import english_to_runeglish  # noqa: E402

ALPHA = c3301.CICADA_ALPHABET
ENG = c3301.CICADA_ENGLISH_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHA)}
OUT = ROOT / "data" / "register_vocab.txt"
CICADA2014 = Path.home() / "src" / "cicada-2014" / "stage11"
WORD = re.compile(r"[A-Za-z]{2,}")

LORE = ["DIVINITY", "WITHIN", "INSTAR", "EMERGE", "EMERGENCE", "CIRCUMFERENCE", "CIRCUMFERENCES", "SURFACE", "TUNNELING", "PARABLE", "WISDOM", "SACRED", "PRIMES", "PRIME", "TOTIENT", "FUNCTION", "PILGRIM", "PILGRIMS", "PILGRIMAGE", "WELCOME", "WARNING", "JOURNEY", "DECEPTION", "ILLUSION", "REALITY", "UNIVERSE", "HOLOGRAM", "CONSUMPTION", "PRESERVATION", "ADHERENCE", "ENLIGHTENMENT", "CONSCIOUSNESS", "KNOWLEDGE", "MOBIUS", "MOEBIUS", "INSTRUCTION", "COMMAND", "ENCRYPTED", "ENCRYPT", "DECRYPT", "SHADOWS", "PRESERVE", "DISCOVER", "BEHOLD", "SEEKER", "MASTER", "STUDENT", "CICADA", "ANALOG", "DIGITAL", "MEANING", "TRUTH", "PATIENCE", "SACRIFICE", "MAGIC", "SQUARE", "KOAN", "AMASS", "PRODUCE", "SHED", "INTUS", "FORM", "VOID", "BEING", "WAY", "END", "BOOK", "PATH", "MOURNFUL", "BUFFERS", "SHADOW", "MIND", "BODY", "SOUL", "FORTITUDE", "FAITH", "FREEDOM"]


# Canonical solved Cicada messages, 2012-2013 (the earlier rounds' register).
CICADA_MESSAGES = """
Hello. We are looking for highly intelligent individuals. To find them, we have
devised a test. There is a message hidden in the image. Find it, and it will lead
you on the road to finding us. We look forward to meeting the few who will make it
all the way through. Good luck.
Hello again. We are looking for highly intelligent individuals. We have hidden a
message in this image. It is not that easy to find. Good luck.
Congratulations. You have proven yourself worthy. We are watching.
We have now found the individuals we sought. Thus, our month long journey ends.
"""


def load_register() -> dict[int, list[tuple[tuple[int, ...], str]]]:
    """Read data/register_vocab.txt -> length -> [(runeglish index tuple, english)]."""
    out: dict[int, list[tuple[tuple[int, ...], str]]] = defaultdict(list)
    for line in OUT.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        rg, eng = line.split("\t")[:2]
        t = tuple(IDX[c] for c in rg if c in IDX)
        if t:
            out[len(t)].append((t, eng))
    return out


VOWELS = set("AEIOU")


def plausible(word: str) -> bool:
    """Reject obvious junk (hash / base64 / .onion fragments) while keeping real
    words and runeglish spellings: needs a vowel and any Q must be QU. The heavy
    lifting is done by stripping PGP armour and hash lines in words_from_prose;
    this is only a backstop (a strict consonant-run rule wrongly drops INSTRUCTION,
    CRYPT, etc.)."""
    w = word.upper()
    if not (set(w) & VOWELS):
        return False
    return not ("Q" in w and "QU" not in w)


def words_from_prose(path: Path) -> list[str]:
    """English words from a solved-text file, skipping PGP armour and hash lines."""
    out: list[str] = []
    for line in path.read_text().splitlines():
        if "BEGIN PGP SIGNATURE" in line:
            break
        if line.startswith(("-----", "Hash:", "Version:")) or ".onion" in line:
            continue
        if re.search(r"[0-9a-fA-F]{8,}", line):  # a hash line
            continue
        out += [t for t in WORD.findall(line) if plausible(t)]
    return out


def runeglish(word_english: str) -> str:
    return "".join(c for c in english_to_runeglish(word_english.upper()) if c in IDX)


def english_of(runes: str) -> str:
    return "".join(ENG[IDX[r]] for r in runes if r in IDX)


def main() -> None:
    # runeglish -> (english, set of sources)
    vocab: dict[str, tuple[str, set[str]]] = {}

    def add_runes(runes: str, source: str) -> None:
        runes = "".join(r for r in runes if r in IDX)
        if len(runes) < 2:
            return
        eng = english_of(runes)
        if not plausible(eng):
            return
        _eng, srcs = vocab.get(runes, (eng, set()))
        srcs.add(source)
        vocab[runes] = (eng, srcs)

    def add_english(word: str, source: str) -> None:
        rg = runeglish(word)
        if len(rg) < 2:
            return
        eng, srcs = vocab.get(rg, (word.upper(), set()))
        srcs.add(source)
        vocab[rg] = (eng, srcs)

    # LP plaintext words (runeglish) from the RECOVERED solved pages only. The
    # "plaintext" tail of page0-58 mixes in the still-enciphered section 10, so it
    # is skipped; the plaintext Parable/AN END come in cleanly via cicada2014.
    for label, words in plaintext_phrases():
        if "plaintext" in label:
            continue
        for w in words:
            add_runes("".join(ALPHA[i] for i in w), "lp-solved")

    # cicada-2014 solved English prose (PGP armour and hash lines stripped)
    for name in ("56.decoded", "57.decoded", "message.txt.asc"):
        p = CICADA2014 / name
        if p.exists():
            for tok in words_from_prose(p):
                add_english(tok, "cicada2014")

    for tok in WORD.findall(CICADA_MESSAGES):
        if plausible(tok):
            add_english(tok, "cicada2012-13")

    for term in LORE:
        add_english(term, "lore")

    lines = [
        f"{rg}\t{eng}\t{','.join(sorted(srcs))}"
        for rg, (eng, srcs) in sorted(vocab.items(), key=lambda kv: kv[1][0])
    ]
    header = (
        "# Cicada 3301 register vocabulary for cribbing.\n"
        "# Built by experiments/build_register_vocab.py.\n"
        "# columns (tab-separated): runeglish  english  sources\n"
    )
    OUT.write_text(header + "\n".join(lines) + "\n")
    by_src: dict[str, int] = defaultdict(int)
    for _rg, (_eng, srcs) in vocab.items():
        for s in srcs:
            by_src[s] += 1
    print(f"wrote {len(vocab)} distinct register words to {OUT.relative_to(ROOT)}")
    for s, n in sorted(by_src.items()):
        print(f"  {s:<12} {n}")


if __name__ == "__main__":
    main()
