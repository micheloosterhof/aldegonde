# ABOUTME: Tests whether a keyword-derived mixed alphabet can satisfy the measured
# ABOUTME: constraints on sigma, which would collapse its key space or exclude the family.
"""The author's keys are English words. Could sigma be built from one?

Every key recovered from this book is a word: DIVINITY on pages 1 and 2, FIRFUMFERENFE on
12 and 13, and Atbash-plus-shift on the monoalphabetic pages
(`break_the_front_matter_pages.py`). The classical way to turn a word into a permutation
is a **mixed alphabet**: write the keyword with repeats removed, then the remaining
letters in order.

`key-local-channel-is-empty.md` gives sigma 103 bits with essentially none constrained
locally, and that is the larger half of the key. **If sigma is keyword-derived its space
is not 103 bits, it is the size of a vocabulary** -- a few thousand -- and a search becomes
trivial. So the question is worth asking directly rather than assuming a general
permutation.

Two measured constraints apply, both conditional and both stated as such by their files:

- **sigma is even** (`sigma-is-even.md`), if the DJU-BEI return is genuine: parity is a
  homomorphism, g is even because every cycle of an order-5 permutation is a 5-cycle, so
  the exponents drop out and an odd word gap forces sign(sigma) = +1;
- **order at least 1,536** (`sigma-cycle-type-narrowed.md`) under a per-block reset, which
  with evenness leaves the single cycle type (11, 7, 5, 4, 2).

A mixed alphabet's cycle type is fixed by its keyword, so this is a finite check.

## What either answer buys

If keyword alphabets routinely satisfy the constraints, sigma's search space collapses
from 103 bits to about eleven and the parked sweep changes character entirely. If they
systematically fail, the keyword family is excluded and sigma is a general permutation --
which is worth knowing before costing any search that assumes otherwise.

    python could_sigma_come_from_a_keyword.py
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from aldegonde import c3301  # noqa: E402

M = 29
ALPHA = c3301.CICADA_ALPHABET
ENGLISH = c3301.CICADA_ENGLISH_ALPHABET
IDX_ENG = {c: i for i, c in enumerate(ENGLISH)}
VOCAB = ROOT / "data" / "register_vocab.txt"
MIN_ORDER = 1536
TARGET_TYPE = (11, 7, 5, 4, 2)


def keywords() -> list[str]:
    out = []
    for line in VOCAB.read_text().splitlines():
        if line.startswith("#") or "\t" not in line:
            continue
        word = line.split("\t")[1].strip()
        if 3 <= len(word) <= 16:
            out.append(word)
    return sorted(set(out))


def mixed_alphabet(word: str) -> list[int] | None:
    """The classical construction: keyword without repeats, then the rest in order."""
    seen, order = set(), []
    for ch in word:
        i = IDX_ENG.get(ch)
        if i is None:
            return None
        if i not in seen:
            seen.add(i)
            order.append(i)
    order.extend(i for i in range(M) if i not in seen)
    return order


def cycle_type(perm) -> tuple[int, ...]:
    seen, out = set(), []
    for start in range(len(perm)):
        if start in seen:
            continue
        length, at = 0, start
        while at not in seen:
            seen.add(at)
            at = perm[at]
            length += 1
        out.append(length)
    return tuple(sorted(out, reverse=True))


def parity(perm) -> int:
    return 1 if sum(c - 1 for c in cycle_type(perm)) % 2 == 0 else -1


def order_of(kind) -> int:
    out = 1
    for c in kind:
        out = out * c // np.gcd(out, c)
    return int(out)


def main() -> None:
    words = keywords()
    perms = [(w, mixed_alphabet(w)) for w in words]
    perms = [(w, p) for w, p in perms if p]
    print(f"{len(perms)} keywords from the author's own vocabulary.\n")

    even = [(w, p) for w, p in perms if parity(p) == 1]
    long_order = [(w, p) for w, p in perms if order_of(cycle_type(p)) >= MIN_ORDER]
    both = [(w, p) for w, p in even if order_of(cycle_type(p)) >= MIN_ORDER]
    exact = [(w, p) for w, p in perms if cycle_type(p) == TARGET_TYPE]

    print(f"{'constraint':<46}{'keywords':>10}{'share':>9}")
    print(f"{'built at all':<46}{len(perms):>10}{1.0:>9.3f}")
    print(f"{'sigma is even':<46}{len(even):>10}{len(even) / len(perms):>9.3f}")
    print(
        f"{f'order >= {MIN_ORDER}':<46}{len(long_order):>10}"
        f"{len(long_order) / len(perms):>9.3f}"
    )
    print(f"{'both':<46}{len(both):>10}{len(both) / len(perms):>9.3f}")
    print(
        f"{f'cycle type exactly {TARGET_TYPE}':<46}{len(exact):>10}"
        f"{len(exact) / len(perms):>9.3f}"
    )

    print("\nWhat a random permutation of 29 would give, for scale:")
    rng = np.random.default_rng(3301)
    rand = [list(rng.permutation(M)) for _ in range(4000)]
    r_even = sum(1 for p in rand if parity(p) == 1)
    r_long = sum(1 for p in rand if order_of(cycle_type(p)) >= MIN_ORDER)
    print(f"  even {r_even / len(rand):.3f}   order >= {MIN_ORDER} {r_long / len(rand):.3f}")

    print("\nThe commonest cycle types a keyword produces:\n")
    for kind, n in Counter(cycle_type(p) for _, p in perms).most_common(6):
        print(f"  {str(kind):<34}{n:>5}   order {order_of(kind):,}")

    if both:
        print(f"\n{len(both)} keywords satisfy both constraints; the first few:")
        print("  " + ", ".join(w for w, _ in both[:10]))


if __name__ == "__main__":
    main()
