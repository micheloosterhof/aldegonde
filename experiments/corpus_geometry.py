# ABOUTME: Verifies which master pages each corpus file actually covers, and checks the
# ABOUTME: body's d-profile across a second split point for a change of g.
"""`page0-56.txt` is master pages 15-70, not pages 0-56. The name counts its own extent.

This cost a tick. Reading the name as "master pages 0 through 56" makes master pages
57-70 look like unused material worth ~20% more corpus; they are already in the file. The
only unsolved text outside it is master page 72, at 95 runes.

The mapping is verified here rather than asserted -- the file's rune sequence is compared
against every contiguous run of master pages until one matches exactly:

    page0-56.txt == master pages 15..70   (56 pages, 12,956 runes)

`hypotheses/README.md` described it as `page0-58.txt` "with the solved trailing pages
removed", which is true and hides that the fifteen solved *leading* pages are gone too,
and that 0-56 counts the file's own pages. Corrected there.

## Why the numbers in other experiments still hold

Experiments that walk the master use master indices throughout and are self-consistent;
`the_interrupter_tracks_the_cipher.py` takes the body as master pages 15 to the end, which
is 13,136 runes and right. Experiments that use `body_blocks()` read the file and get all
56 body pages. The trap is only in mixing the two, which is what happened here.

## A second split point for g

`does_g_change_mid_book.py` compares the body's halves and gets 7:1 for one g over a
change at the midpoint. Splitting instead at master page 57 -- where this tick wrongly
expected a new corpus to begin -- gives an independent second test:

    body pages 15-56    2,298 blocks
    body pages 57-70      630 blocks
    observed chi2 between their d-profiles   3.60 on 6 df, P = 0.73

    one g throughout            chi2  6.6 +- 3.5    P(<= observed) = 0.25
    g changes at the boundary   chi2 25.7 +- 14.8   P(<= observed) = 0.04

**About 6:1 for one g**, matching the midpoint result by a different cut. The changed arm
is heavily skewed for the reason that file records: two random permutations sometimes
give similar d-profiles, which caps this statistic's power wherever it is applied.

    python corpus_geometry.py
"""

from __future__ import annotations

import json
import math
import random
import re
import sys
from pathlib import Path

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from compact_state_models import N_RUNES, order5, prose_corpora  # noqa: E402
from lp_plaintext_register import MASTER, PLAIN_PAGES, TRIPLES  # noqa: E402

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
ANNOTATION = re.compile(r"^[\s0-9-]*$")
INDEX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
LAGS = range(1, 7)
TRIALS = 24
SPLIT = 57


def runes_of(text: str) -> list[str]:
    return RUNE.findall(
        "\n".join(
            line
            for line in text.replace("/", "\n").split("\n")
            if not ANNOTATION.match(line)
        )
    )


def locate(target: list[str], master: list[str]) -> tuple[int, int] | None:
    """The contiguous run of master pages whose runes equal `target` exactly."""
    per_page = [runes_of(page) for page in master]
    for lo in range(20):
        for hi in range(lo + 40, len(master) + 1):
            if [r for n in range(lo, hi) for r in per_page[n]] == target:
                return lo, hi - 1
    return None


def blocks_of(text: str) -> list[list[int]]:
    out, current = [], []
    for ch in runes_and_separators(text):
        if ch == "|":
            if current:
                out.append(current)
                current = []
        else:
            current.append(INDEX[ch])
    if current:
        out.append(current)
    return out


def runes_and_separators(text: str):
    cleaned = "\n".join(
        line
        for line in text.replace("/", "\n").split("\n")
        if not ANNOTATION.match(line)
    )
    for ch in cleaned:
        if RUNE.match(ch):
            yield ch
        elif ch == "\n" or ch in "%$&":
            continue
        elif ch in c3301.WORD_BOUNDARY:
            yield "|"


def profile(blocks):
    out = {}
    for k in LAGS:
        hits = total = 0
        for b in blocks:
            for i in range(len(b) - k):
                total += 1
                hits += b[i] == b[i + k]
        out[k] = (hits, total)
    return out


def chi_square(a, b) -> float:
    total = 0.0
    for k in LAGS:
        ha, ta = a[k]
        hb, tb = b[k]
        if not ta or not tb:
            continue
        ra, rb = ha / ta, hb / tb
        se = math.hypot(math.sqrt(ra * (1 - ra) / ta), math.sqrt(rb * (1 - rb) / tb))
        if se:
            total += ((rb - ra) / se) ** 2
    return total


def compose(p, q):
    return [p[q[i]] for i in range(len(p))]


def power(p, k):
    out = list(range(len(p)))
    for _ in range(k):
        out = compose(p, out)
    return out


def encipher(plain, seed, change_at=None):
    rng = random.Random(seed)
    g = order5(rng)
    powers = [power(g, k) for k in range(5)]
    sigma = rng.sample(range(N_RUNES), N_RUNES)
    base = rng.sample(range(N_RUNES), N_RUNES)
    out, clock, previous = [], 0, None
    for w, word in enumerate(plain):
        if change_at is not None and w == change_at:
            g = order5(rng)
            powers = [power(g, k) for k in range(5)]
        emitted = []
        for p in word:
            c = base[powers[clock % 5][p]]
            if c == previous and rng.random() < 0.90:
                clock += 1
                c = base[powers[clock % 5][p]]
            emitted.append(c)
            previous = c
            clock += 1
        out.append(emitted)
        base = compose(base, compose(powers[(clock - 1) % 5], sigma))
    return out


def main() -> None:
    master = MASTER.read_text().split("%")
    body_file = (ROOT / "data" / "page0-56.txt").read_text()
    found = locate(runes_of(body_file), master)
    print("Which master pages does each corpus file cover?\n")
    if found:
        lo, hi = found
        print(
            f"  data/page0-56.txt == master pages {lo}..{hi}   "
            f"({hi - lo + 1} pages, {len(runes_of(body_file)):,} runes)"
        )
    else:
        print("  data/page0-56.txt matches no contiguous run of master pages")
    total = sum(len(runes_of(p)) for p in master)
    solved = set(PLAIN_PAGES) | {t["page"] for t in json.loads(TRIPLES.read_text())}
    outside = [
        n
        for n in range(len(master))
        if n not in solved
        and not (found and found[0] <= n <= found[1])
        and len(runes_of(master[n]))
    ]
    print(f"  the master holds {total:,} runes over {len(master)} pages")
    print(
        f"  unsolved pages outside the body file: {outside} "
        f"({sum(len(runes_of(master[n])) for n in outside)} runes)"
    )
    print(
        "\n  So there is no unused body material: the name counts the file's own pages."
    )

    before = [
        b for n in range(15, SPLIT) if n not in solved for b in blocks_of(master[n])
    ]
    after = [
        b for n in range(SPLIT, 71) if n not in solved for b in blocks_of(master[n])
    ]
    observed = chi_square(profile(before), profile(after))
    print(f"\nA second split point for g, at master page {SPLIT}.\n")
    print(f"  body pages 15-{SPLIT - 1}   {len(before):>5} blocks")
    print(f"  body pages {SPLIT}-70      {len(after):>5} blocks")
    print(
        f"  observed chi2 {observed:.2f} on {len(list(LAGS))} df, "
        f"P = {1 - stats.chi2.cdf(observed, len(list(LAGS))):.3f}\n"
    )
    plain = prose_corpora(len(before) + len(after), 1)[0]
    print(f"{'arm':<32}{'chi2':>22}{'P(<= observed)':>17}")
    ratios = {}
    for label, change in (
        ("one g throughout", None),
        ("g changes at the boundary", len(before)),
    ):
        values = np.array(
            [
                chi_square(profile(c[: len(before)]), profile(c[len(before) :]))
                for c in (encipher(plain, 300 + s, change) for s in range(TRIALS))
            ]
        )
        p = float((values <= observed).mean())
        ratios[label] = max(p, 1 / TRIALS)
        print(
            f"{label:<32}{f'{values.mean():.1f} +- {values.std(ddof=1):.1f}':>22}{p:>17.2f}"
        )
    print(
        f"\n  likelihood ratio, one g over a change here: "
        f"{ratios['one g throughout'] / ratios['g changes at the boundary']:.0f} to 1"
    )
    print(
        "  which matches the midpoint result in does_g_change_mid_book.py by a"
        "\n  different cut. The changed arm is skewed for the reason that file gives:"
        "\n  two random permutations sometimes give similar d-profiles."
    )


if __name__ == "__main__":
    main()
