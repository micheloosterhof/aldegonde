# ABOUTME: Establishes the author's interrupter as an exact plaintext rule and turns it
# ABOUTME: into a point prediction for the body's rune-F rate, which the body refutes.
"""The interrupter is not a property of the ciphertext rune. It is a plaintext rule.

`interrupter-is-a-scribal-mark` records the puzzle from the ciphertext side: on page 1
only 6 of 14 ciphertext rune-F actually interrupt, so the trigger cannot be read off the
rune and skip positions have to be searched. That framing hides a rule that is exact.

From the plaintext side the rule has no exceptions at all. Across all five interrupted
pages in `solved_page_triples.json` -- chunks 1, 2, 12, 13 and 71, two different ciphers
between them -- the set of interrupt positions equals the set of positions where the
PLAINTEXT rune is F, with nothing left over on either side:

    every plaintext F is passed through literally, and nothing else is

So the interrupt rate is not a free parameter of the cipher. It is the plaintext's own F
frequency, and `lp-plaintext-register.md` measures that on the author's own words. That
turns `passthrough_interrupter_bound.py`'s inequality into an equality, which the body
can then fail.

    python interrupter_rule.py
"""

from __future__ import annotations

import collections
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from lp_corpus import load_clean  # noqa: E402
from lp_plaintext_register import corpus  # noqa: E402

M = 29
F = 0
TRIPLES = ROOT / "experiments" / "solved_page_triples.json"


def main() -> None:
    triples = json.loads(TRIPLES.read_text())
    print("the rule, checked on every interrupted page:")
    print(
        f"{'chunk':>7}{'cipher':>22}{'plaintext F':>13}{'interrupts':>12}{'equal':>7}"
    )
    for t in triples:
        if t["cipher"] == "monoalphabetic":
            continue
        fs = {i for i, v in enumerate(t["plaintext_runes"]) if v == F}
        skips = set(t["interrupts"])
        print(
            f"{t['page']:>7}{t['cipher']:>22}{len(fs):>13}{len(skips):>12}"
            f"{str(fs == skips):>7}"
        )

    plain = [r for w in corpus() for r in w]
    n = len(plain)
    q = collections.Counter(plain)[F] / n
    se = math.sqrt(q * (1 - q) / n)
    print(f"\nLP plaintext F frequency: {q:.4f} +- {se:.4f} over {n:,} runes")
    solved = sum(len(t["interrupts"]) for t in triples)
    runes = sum(t["runes"] for t in triples if t["cipher"] != "monoalphabetic")
    print(f"solved pages' own interrupt rate: {solved}/{runes} = {solved / runes:.4f}")

    body, _wid = load_clean()
    nb = len(body)
    obs = collections.Counter(body)[F] / nb
    bse = math.sqrt(obs * (1 - obs) / nb)
    pred = q + (1 - q) / M
    z = (obs - pred) / math.sqrt(bse**2 + se**2)
    print("\nif the body used this interrupter, its rune-F rate would be")
    print(f"  q + (1-q)/29 = {pred:.4f}")
    print(f"observed        {obs:.4f} +- {bse:.4f}   z = {z:+.2f}")
    print(f"\npredicted interrupts in the body: {q * nb:.0f}")
    allowed = ((obs + 1.645 * bse) - 1 / M) / (1 - 1 / M) * nb
    print(f"the unigram bound allows at most:  {allowed:.0f}")
    print(
        "\nConsequence for every alignment test. At 1.58% the expected run before the"
        f"\nfirst interrupt is {1 / q:.0f} runes; at the bound's {allowed / nb:.4f} it is"
        f" {nb / allowed:.0f}."
        "\nScope: this bounds only interrupters that EMIT a rune. A clock perturbation"
        "\nthat still enciphers leaves no unigram trace and is untouched."
    )


if __name__ == "__main__":
    main()
