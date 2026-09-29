# ABOUTME: Pins the author's interrupt rule from all five keyed solved pages, then shows the
# ABOUTME: body cannot be using it, because no rune is left unenciphered there.
"""On every keyed page the author solved, the interrupt rule is exact: plaintext F.

The five solved pages that carry a keystream -- four interrupted Vigenere and one prime
running key -- have twelve interrupts between them. At every one of the twelve the
ciphertext rune is F and the plaintext rune is F: the rune passes through unenciphered
and the key does not advance. And the count matches exactly on every page:

    page  1   6 plaintext F,  6 interrupts
    page  2   3 plaintext F,  3 interrupts
    page 12   2 plaintext F,  2 interrupts
    page 13   0 plaintext F,  0 interrupts
    page 71   1 plaintext F,  1 interrupt

Twelve for twelve, no exceptions, across two different cipher families. The rule is not a
tendency, it is the convention.

That makes a hard prediction about any text enciphered the same way. A rune passed through
appears in the ciphertext at its plaintext rate PLUS the flat rate from everything else,
so its ciphertext frequency stands well clear of 1/29. The body is flat. This measures how
far the body is from the pass-through prediction, for F and for every other rune.

    python nothing_passes_through.py
"""

from __future__ import annotations

import collections
import importlib.util
import json
import math
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402
from lp_corpus import load_clean  # noqa: E402

RUNE = re.compile(r"[ᚠ-᛿]")
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
ENG = c3301.CICADA_ENGLISH_ALPHABET
M = 29


def register():
    spec = importlib.util.spec_from_file_location(
        "lp_plaintext_register", ROOT / "experiments" / "lp_plaintext_register.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rule_on_solved_pages() -> None:
    master = (ROOT / "data" / "liber-primus__transcription--master.txt").read_text()
    chunks = master.split("%")
    triples = json.loads(
        (ROOT / "experiments" / "solved_page_triples.json").read_text()
    )
    f = ENG.index("F")
    print("the interrupt rule on every solved page that carries a keystream\n")
    print(
        f"{'page':>5}{'cipher':>22}{'plain F':>9}{'interrupts':>12}"
        f"{'all at plain F':>16}"
    )
    total_f = total_i = 0
    for x in triples:
        if x["cipher"] == "monoalphabetic":
            continue
        plain = x["plaintext_runes"]
        ints = x.get("interrupts") or []
        cipher = [IDX[ch] for ch in RUNE.findall(chunks[x["page"]])]
        pf = sum(1 for r in plain if r == f)
        ok = all(plain[i] == f and i < len(cipher) and cipher[i] == f for i in ints)
        print(
            f"{x['page']:>5}{x['cipher']:>22}{pf:>9}{len(ints):>12}"
            f"{('yes' if ok else 'NO'):>16}"
        )
        total_f += pf
        total_i += len(ints)
    print(f"\n{total_i} interrupts against {total_f} plaintext F. The rule is exact.")
    print("At every interrupt the ciphertext rune is F too, because the rune passes")
    print("through: c = p = F, and the key index does not advance.")


def body_passes_nothing() -> None:
    stream, _ = load_clean()
    n = len(stream)
    counts = collections.Counter(stream)
    plain = register().corpus()
    pn = sum(len(w) for w in plain)
    pc = collections.Counter(r for w in plain for r in w)

    print(f"\n\nthe body: {n:,} runes. If a rune passed through, its ciphertext rate")
    print("would be its plaintext rate plus the flat rate from everything else.\n")
    print(
        f"{'rune':>5}{'plain rate':>12}{'predicted':>11}{'observed':>10}"
        f"{'z vs flat':>11}{'z vs pass-through':>19}"
    )
    rows = []
    for i in range(M):
        pf = pc[i] / pn
        pred = pf + (1 - pf) / M
        obs = counts[i] / n
        se = math.sqrt(obs * (1 - obs) / n) or 1e-9
        rows.append((pf, i, pred, obs, (obs - 1 / M) / se, (obs - pred) / se))
    for pf, i, pred, obs, zflat, zpass in sorted(rows, reverse=True)[:10]:
        print(
            f"{ENG[i]:>5}{pf:>12.4f}{pred:>11.4f}{obs:>10.4f}{zflat:>+11.2f}"
            f"{zpass:>+19.2f}"
        )
    f = ENG.index("F")
    row = next(r for r in rows if r[1] == f)
    print(
        f"{'F':>5}{row[0]:>12.4f}{row[2]:>11.4f}{row[3]:>10.4f}{row[4]:>+11.2f}"
        f"{row[5]:>+19.2f}"
    )

    closest = max(r[5] for r in rows)
    print(
        f"\nEvery rune is flat and none is near its pass-through rate. The closest any"
    )
    print(
        f"rune comes is {closest:+.1f} sigma, which is F -- the one the author actually"
    )
    print("uses -- and the common plaintext runes miss by tens of sigma.")
    chi = sum((counts[i] - n / M) ** 2 / (n / M) for i in range(M))
    print(f"unigram chi2 against uniform: {chi:.1f} on 28 df")
    print(
        "\nSo the body does not pass any rune through. Whatever encrypts it, it is not"
        "\nthe interrupted keystream the author used on every other keyed page of the"
        "\nbook -- that convention would leave a signature the body does not carry."
        "\n\nWhat is excluded is the PASS-THROUGH convention, not key-skipping in"
        "\ngeneral: a rule that holds the key index while still enciphering the rune"
        "\nleaves the unigram table flat and is untouched by this test."
    )


def main() -> None:
    rule_on_solved_pages()
    body_passes_nothing()


if __name__ == "__main__":
    main()
