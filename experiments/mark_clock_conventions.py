# ABOUTME: Which visible marks advance the cipher's word clock? Audits the
# ABOUTME: apostrophe/quote/sentence conventions and their effect on the gaps.
"""Michel's question: is the apostrophe a word breaker, and does the LP's own
algorithm treat it as one?

Two separate questions.

WHAT WE COUNT is checkable. c3301.WORD_BOUNDARY contains the separators, the
sentence marks, the section markers and the double quote -- but NOT the
apostrophe. So under the repo's tokenizer a word flows across an apostrophe.
This script verifies that is actually what happens, and that the quote never
splits a word either (it turns out every quote is adjacent to a mark on one
side, so it can never fall strictly inside a word).

WHAT THE LP COUNTS is not decidable from four apostrophes -- no statistic
built on four events has power. But the CONSEQUENCES are exactly computable,
and one of them matters: the DJU-BEI word gap, which the autonomous-machine
divisibility argument in rotor-machine-compact-state.md rests on. Two of the
four apostrophes fall between the two occurrences, so the gap moves if they
clock.

This script prices every plausible convention rather than assuming one.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from aldegonde import c3301

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from rotor_period_closure import divisors, factorise  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ALPHABET = c3301.CICADA_ALPHABET
IDX = {r: i for i, r in enumerate(ALPHABET)}

APOSTROPHE = "'"
QUOTE = '"'
SENTENCE = {"④", "⑬", "⑩", "③", "⑤"}
DIGITS = set("0123456789")
# NB: use this, not str.isdigit() -- '①' and friends are isdigit()==True,
# which is the trap recorded in isdigit-counts-circled-marks.md.
ASCII_DIGIT = re.compile(r"[0-9]")


def sections(text: str) -> list[str]:
    return [s for s in text.split("$") if RUNE.search(s)][:10]


def tokenize(
    text: str, breakers: set[str], digit_mode: str = "break"
) -> tuple[list[int], list[int], int]:
    """Rune stream + word id + extra clock steps.

    digit_mode:
      "break"       digits act as word separators (the repo default)
      "transparent" digits are ignored entirely, words flow across them
      "token"       digits are transparent, but each digit RUN costs one
                    extra clock step (a numeral is a plaintext word that
                    happens to carry no runes)
    """
    stream: list[int] = []
    word_id: list[int] = []
    w = 0
    extra = 0
    for s in sections(text):
        started = False
        in_digits = False
        for ch in s:
            is_digit = bool(ASCII_DIGIT.match(ch))
            if is_digit and digit_mode != "break":
                if not in_digits:
                    in_digits = True
                    if digit_mode == "token":
                        extra += 1
                continue
            in_digits = False
            if RUNE.match(ch):
                stream.append(IDX[ch])
                word_id.append(w)
                started = True
            elif ch in breakers:
                if started:
                    w += 1
                    started = False
        if started:
            w += 1
    return stream, word_id, extra


def djubei(stream: list[int], word_id: list[int]) -> tuple[int, int, int, int]:
    from collections import defaultdict

    seen: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for i in range(len(stream) - 5):
        if i > 0 and word_id[i - 1] == word_id[i]:
            continue
        seen[tuple(stream[i : i + 6])].append(i)
    rep = {g: p for g, p in seen.items() if len(p) > 1}
    assert len(rep) == 1, f"expected one word-initial 6-gram repeat, got {len(rep)}"
    pos = next(iter(rep.values()))
    a, b = pos[0], pos[1]
    return a, b, b - a, word_id[b] - word_id[a]


def digit_runs_between(text: str, breakers: set[str], a: int, b: int) -> int:
    """Digit runs falling between rune offsets a and b (extra clock steps)."""
    secs = "$".join(sections(text))
    runes = 0
    n = 0
    in_digits = False
    for ch in secs:
        if RUNE.match(ch):
            runes += 1
            in_digits = False
        elif ASCII_DIGIT.match(ch):
            if not in_digits and a < runes < b:
                n += 1
            in_digits = True
        else:
            in_digits = False
    return n


def main() -> None:
    text = (ROOT / "data" / "page0-56.txt").read_text()
    base = set(c3301.WORD_BOUNDARY)

    print("--- what the repo counts ---")
    print(f"  apostrophe {APOSTROPHE!r} in WORD_BOUNDARY? {APOSTROPHE in base}")
    print(f"  quote      {QUOTE!r} in WORD_BOUNDARY? {QUOTE in base}")

    # Where do the marks actually sit?
    inner_ap = inner_q = 0
    for m in re.finditer(re.escape(APOSTROPHE), text):
        i = m.start()
        if RUNE.match(text[i - 1]) and RUNE.match(text[i + 1]):
            inner_ap += 1
    for m in re.finditer(re.escape(QUOTE), text):
        i = m.start()
        if RUNE.match(text[i - 1]) and RUNE.match(text[i + 1]):
            inner_q += 1
    n_ap = text.count(APOSTROPHE)
    n_q = text.count(QUOTE)
    print(f"  apostrophes rune-flanked on BOTH sides: {inner_ap}/{n_ap}  (strictly mid-word)")
    print(f"  quotes      rune-flanked on BOTH sides: {inner_q}/{n_q}  (never mid-word)")
    print(
        "  => the quote is in WORD_BOUNDARY but can never split a word, because it\n"
        "     always sits next to a mark. Counting it changes nothing."
    )

    # Where are the ASCII digits, and what work are they doing?
    print("\n--- the ASCII digits ---")
    secs = "$".join(sections(text))
    runes_seen = 0
    adjacent = []
    for i, ch in enumerate(secs):
        if RUNE.match(ch):
            runes_seen += 1
        elif ASCII_DIGIT.match(ch):
            nxt = secs[i + 1] if i + 1 < len(secs) else ""
            if RUNE.match(nxt or " "):
                adjacent.append((runes_seen, ch))
    total = sum(1 for ch in secs if ASCII_DIGIT.match(ch))
    print(f"  {total} ASCII digits in sections 0-9; {len(adjacent)} immediately precede a rune")
    print(f"  those are the line-initial headers: {[c for _, c in adjacent]}")
    print(f"  at rune offsets {[r for r, _ in adjacent]} (DJU-BEI spans 6555..12950)")

    # Does a header digit ever land strictly inside a word?
    split = 0
    for br_default, br_transparent in [(base, base - DIGITS)]:
        _, wid_a, _ = tokenize(text, br_default, "break")
        _, wid_b, _ = tokenize(text, br_transparent, "transparent")
        split = (wid_a[-1] + 1) - (wid_b[-1] + 1)
    print(f"  words created by digits acting as separators: {split}")

    print("\n--- word counts and the DJU-BEI gaps, per convention ---")
    conventions = [
        ("repo default", base, "break"),
        ("apostrophe also breaks", base | {APOSTROPHE}, "break"),
        ("quote does NOT break", base - {QUOTE}, "break"),
        ("sentence marks do NOT break", base - SENTENCE, "break"),
        ("digits transparent", base - DIGITS, "transparent"),
        ("digits are word tokens", base - DIGITS, "token"),
        ("digits tokens + apostrophe breaks", (base | {APOSTROPHE}) - DIGITS, "token"),
    ]
    rows = []
    for name, br, dm in conventions:
        stream, wid, extra = tokenize(text, br, dm)
        a, b, rgap, wgap = djubei(stream, wid)
        # extra clock steps that fall between the two occurrences
        if dm == "token":
            wgap += digit_runs_between(text, br, a, b)
        rows.append((name, len(stream), wid[-1] + 1 + extra, rgap, wgap))
        print(
            f"  {name:<36} runes {len(stream)}  words {wid[-1] + 1 + extra:>5}  "
            f"rune gap {rgap}  word gap {wgap}"
        )

    # Self-check: the repo default must reproduce the published figures.
    d = rows[0]
    assert (d[1], d[2], d[3], d[4]) == (12956, 2928, 6395, 1449), d
    print("  self-check: repo default = 12956 / 2928 / 6395 / 1449  OK")

    print("\n--- consequence for the autonomous-machine divisibility argument ---")
    print("  (an autonomous machine returns to a state iff its period divides the gap)")
    seen_gaps = set()
    for _name, _, _, rgap, wgap in rows:
        for label, gap in (("rune", rgap), ("word", wgap)):
            if (label, gap) in seen_gaps:
                continue
            seen_gaps.add((label, gap))
            dv = divisors(gap)
            usable = [x for x in dv if 1 < x <= 60]
            print(
                f"  {label} gap {gap:>5} = {factorise(gap)}  "
                f"divisors {dv if len(dv) <= 12 else str(dv[:12]) + '...'}"
            )
            print(f"      usable small periods: {usable or 'NONE'}   29 divides? {gap % 29 == 0}")


if __name__ == "__main__":
    main()
