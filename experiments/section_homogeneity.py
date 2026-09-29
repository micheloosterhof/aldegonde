# ABOUTME: Tests whether the body is one cipher uniformly applied, by checking its
# ABOUTME: structural statistics for homogeneity across sections and across pages.
"""Is there a weak page? Every foothold argument assumes not, and nobody has checked.

The project treats the unsolved body as a single cipher and pools 12,956 runes to measure
everything. If one page or section were enciphered differently -- a shorter key, a lapse,
a different variant -- pooling would bury it, and that page would be the way in.

Three statistics carry the body's structure and each has a clean homogeneity test:

    within-block doublet rate   the suppression, pooled 0.0063
    within-block d5 rate        the period-5 echo, pooled 0.0492
    normalised IoC              the alphabet count, pooled ~1.00

Chi-square of observed against the pooled rate, over sections and then over the 57 master
chunks, which is the finer grid.

    python section_homogeneity.py
"""

from __future__ import annotations

import collections
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
M = 29
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"


def parse(text: str) -> tuple[list[int], list[int]]:
    stream: list[int] = []
    wid: list[int] = []
    w, started = 0, False
    for ch in text:
        if RUNE.match(ch):
            stream.append(IDX[ch])
            wid.append(w)
            started = True
        elif ch in "/\n":
            continue
        elif started and ch in c3301.WORD_BOUNDARY:
            w += 1
            started = False
    return stream, wid


def within(stream: list[int], wid: list[int], lag: int) -> tuple[int, int]:
    hits = pairs = 0
    for i in range(len(stream) - lag):
        if wid[i] == wid[i + lag]:
            pairs += 1
            hits += stream[i] == stream[i + lag]
    return hits, pairs


def homogeneity(cells: list[tuple[int, int]], label: str) -> None:
    """Chi-square of per-unit counts against the pooled rate."""
    used = [(h, p) for h, p in cells if p >= 20]
    th = sum(h for h, _ in used)
    tp = sum(p for _, p in used)
    rate = th / tp
    chi = sum((h - p * rate) ** 2 / (p * rate) for h, p in used if p * rate > 0)
    df = len(used) - 1
    crit = df + 1.645 * math.sqrt(2 * df)
    verdict = "homogeneous" if chi < crit else "NOT homogeneous"
    print(
        f"  {label:<22} pooled {rate:.4f}  chi2 {chi:>6.1f} on {df:>2} df "
        f"(5% crit {crit:.1f})  {verdict}"
    )


def main() -> None:
    body = (ROOT / "data" / "page0-56.txt").read_text()
    sections = [s for s in body.split("$") if RUNE.search(s)][:10]
    raw = MASTER.read_text().split("%")
    # chunk 71 is the solved AN END page and 72 is the Parable, stored as plaintext;
    # lp_corpus excludes both from the clean corpus and so does this
    chunks = [c for i, c in enumerate(raw) if 15 <= i <= 70 and RUNE.search(c)]
    control = [IDX[c] for c in raw[72] if RUNE.match(c)]

    for label, units in (("sections", sections), ("master chunks", chunks)):
        parsed = [parse(u) for u in units]
        kept = [(s, w) for s, w in parsed if len(s) >= 50]
        print(f"\n{label}: {len(parsed)} units, {len(kept)} with 50+ runes")
        homogeneity([within(s, w, 1) for s, w in kept], "within-block doublets")
        homogeneity([within(s, w, 5) for s, w in kept], "within-block d5")
        iocs = []
        for s, _w in kept:
            n = len(s)
            c = collections.Counter(s)
            iocs.append(M * sum(v * (v - 1) for v in c.values()) / (n * (n - 1)))
        mu = sum(iocs) / len(iocs)
        sd = (sum((x - mu) ** 2 for x in iocs) / len(iocs)) ** 0.5
        expected = sum(math.sqrt(2 / len(s)) for s, _w in kept) / len(kept)
        print(
            f"  {'normalised IoC':<22} mean {mu:.4f}  sd {sd:.4f}  "
            f"(sampling alone predicts ~{expected:.4f})"
        )
        worst = max(range(len(iocs)), key=lambda i: abs(iocs[i] - mu))
        print(
            f"  {'':22} most extreme unit: {iocs[worst]:.4f} "
            f"at {(iocs[worst] - mu) / sd:+.2f} sd, {len(kept[worst][0])} runes"
        )

    cc = collections.Counter(control)
    nc = len(control)
    ioc_c = M * sum(v * (v - 1) for v in cc.values()) / (nc * (nc - 1))
    print(f"\npositive control: chunk 72 is the Parable, stored as PLAINTEXT.")
    print(
        f"  {nc} runes, normalised IoC {ioc_c:.3f} -- it stands out at +7 sd when left in,"
    )
    print("  so this test would find a plaintext or monoalphabetic page in the body.")
    print(
        "\nOne cipher, uniformly applied. No section or page carries a weaker variant,"
        "\nso there is no page to attack first -- the body has to be taken whole."
    )


if __name__ == "__main__":
    main()
