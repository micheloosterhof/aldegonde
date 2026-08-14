# ABOUTME: Key-free test of whether the per-word base step lies in <g>, which would
# ABOUTME: collapse the book to 5 alphabets and make sigma disappear as an unknown.
"""Is the base step a power of g -- or driven by the ciphertext?

The walk steps the base once per word:

    base_{w+1} = base_w . g^((L_w - 1) mod 5) . sigma

sigma is the expensive half of the key: 97.9 bits, no construction, and no local
statistic constrains it (`key-local-channel-is-empty.md`). Two ways it could stop
being a free permutation, both of which make it computable from what we already
have:

  (A) sigma = g^t for some t in 0..4. Then the base only ever moves by powers of
      g, so base_w = base_0 . g^(s_w) and the ENTIRE BOOK uses just 5 alphabets.

  (B) sigma = h^(c_last), the step driven by the last ciphertext rune of the word
      -- Michel's ciphertext-autokey idea moved from the value channel to the
      alphabet channel, where it does not convolve. With h in <g> this is again
      5 alphabets, but with a schedule the ciphertext itself dictates.

Both make an identical, KEY-FREE prediction. If the alphabet at a position depends
only on a class index computable from word lengths and observed ciphertext, then
any two positions in the SAME class are enciphered by the same alphabet, and their
coincidence rate is the plaintext's -- IoC ~1.6 -- rather than flat 1.00. Base_0
never enters, because IoC is invariant under a permutation of the alphabet.

Under the walk with a general sigma, every class definition based on position
gives IoC 1.00, because base_w wanders freely from word to word. So this cleanly
separates the hypotheses, and a hit would collapse the key from ~178 bits to ~83.

It would also explain boundary-blindness for free: the seam diagonal would be a
g-power diagonal like d1, so one tuning suppresses both, instead of g and sigma
having to be independently tuned low -- which the current model needs and does not
explain.
"""

from __future__ import annotations

from collections import Counter

from experiments.walk_verifier import load_words

M = 29


def class_ioc(
    classes: list[int], runes: list[int], nclass: int = 5
) -> tuple[float, int]:
    """Pooled coincidence IoC within classes: sum n(n-1) over runes / over totals."""
    tab = [Counter() for _ in range(nclass)]
    for c, r in zip(classes, runes):
        tab[c][r] += 1
    num = den = 0
    for t in tab:
        n = sum(t.values())
        num += sum(v * (v - 1) for v in t.values())
        den += n * (n - 1)
    return (M * num / den if den else 0.0), den


def main() -> None:
    words = load_words()
    runes = [r for w in words for r in w]
    n = len(runes)
    print(f"corpus: {n} runes, {len(words)} words")
    print("flat = 1.00; runeglish plaintext ~1.6-1.7\n")

    # u_w = cumulative (L-1) mod 5, the part of the schedule the lengths already fix
    u = []
    acc = 0
    for w in words:
        u.append(acc % 5)
        acc += len(w) - 1

    print("(A) sigma = g^t -- 5 alphabets, schedule fixed by word lengths")
    print(f"{'t':>4}{'within-class IoC':>20}{'pairs':>14}")
    best = []
    for t in range(5):
        cls = []
        for wi, w in enumerate(words):
            base = (u[wi] + t * wi) % 5
            cls += [(base + j) % 5 for j in range(len(w))]
        ioc, pairs = class_ioc(cls, runes)
        best.append((ioc, f"A t={t}"))
        print(f"{t:>4}{ioc:>20.4f}{pairs:>14}")

    print("\n(B) sigma = h^(c_last) -- step driven by the last ciphertext rune")
    print(f"{'map of c_last':>22}{'within-class IoC':>20}")
    maps = {
        "c mod 5": lambda r: r % 5,
        "c // 5 mod 5": lambda r: (r // 5) % 5,
        "-(c) mod 5": lambda r: (-r) % 5,
        "2c mod 5": lambda r: (2 * r) % 5,
    }
    for name, f in maps.items():
        cls = []
        acc2 = 0
        for w in words:
            cls += [(acc2 + j) % 5 for j in range(len(w))]
            acc2 = (acc2 + (len(w) - 1) + f(w[-1])) % 5
        ioc, _ = class_ioc(cls, runes)
        best.append((ioc, f"B {name}"))
        print(f"{name:>22}{ioc:>20.4f}")

    # Controls: the same statistic on schedules that cannot be right.
    print("\ncontrols -- schedules that must give 1.00 if the test is calibrated")
    cls = [j % 5 for w in words for j in range(len(w))]
    ioc, _ = class_ioc(cls, runes)
    print(f"{'phase only (ignores sigma)':>34}{ioc:>12.4f}")
    cls = [i % 5 for i in range(n)]
    ioc, _ = class_ioc(cls, runes)
    print(f"{'absolute position mod 5':>34}{ioc:>12.4f}")
    cls = [0] * n
    ioc, _ = class_ioc(cls, runes, nclass=1)
    print(f"{'no classes (whole corpus IoC)':>34}{ioc:>12.4f}")

    top = max(best)
    print(f"\nbest hypothesis: {top[1]} at IoC {top[0]:.4f}")
    print("A real hit needs ~1.6. Anything near 1.00-1.10 means the base does NOT")
    print("move within <g>, so sigma stays a free permutation and the 5-alphabet")
    print("collapse is refuted.")


if __name__ == "__main__":
    main()
