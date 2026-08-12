# ABOUTME: Fits the 2-rune deficit as lost word separators and shows random loss
# ABOUTME: cannot produce it, while selective loss at 2-rune words fully can.
"""What kind of separator loss produces a deficit at length 2 and nowhere else?

`word-length-keystream-and-boundaries.md` establishes the deficit and rules out
line-break merging (which closes about a quarter of it). This asks the next
question: if separators are missing, WHICH ones?

Two models, both one-parameter, both fitted against the register- and
convention-matched solved pages rather than generic English:

  H1  random loss     a separator vanishes with probability q, regardless of the
                      lengths on either side -- the shape a transcriber's
                      oversights would take
  H2  selective loss  only separators bounding a 2-rune word vanish, so the short
                      word is absorbed into its neighbour

H1 is refuted, though not by chi-square -- base noise makes that test permissive
enough to tolerate it (106 against a no-loss 207). It fails because it cannot hit
the observed mean and the observed 2-rune share together. Tuned to the mean
(q = 0.09, mean 4.38 against 4.43) it leaves the 2-rune share at 21.8% against
15.9%; tuned to chi-square (q = 0.15) it overshoots the mean to 4.61 and still
sits at 20.5%. Removing separators without regard to length takes words of every
length in proportion, so it moves the mean while leaving the shape alone. The
loss is not inattention -- it is selective.

H2 is adequate and hits both targets at once: q = 0.39 gives mean 4.416 against
4.425 and 2-rune 14.9% against 15.9%, with chi-square down from 207 to 26 on
12 df. The residue is not a misfit -- the solved base is itself only ~700 words,
and resampling it from its own words gives chi-square a median of 70 with a 90%
range of 25 to 120, so 94% of draws that ASSUME the model come out worse than the
fitted value.

Direction is a weak preference, not a finding: absorbing into the previous word
scores 26 against 40 for the next, and both sit below the bootstrap median, so
the histogram alone does not settle which side the short word attaches to.

Two readings, and they differ in consequence. If the separators are absent from
the MANUSCRIPT (a scribal habit of attaching short function words), the composer
clocked the cipher on the text as written, the visible word lengths are the right
clock, and only cribbing on word identity suffers. If they are absent from the
TRANSCRIPTION, the clock every key search has used is wrong: the walk's base is
a running product over (L_w - 1) mod 5, so one missing separator corrupts every
base after it. ~300 omissions spread through 2,928 words puts the first one
within the opening handful, i.e. essentially the whole corpus is mis-clocked, and
no enumeration could have succeeded whatever the key.

`boundary_verification.py` favours the second reading, which is the actionable
one: of its 21 clean transcription/scan disagreements, 19 have the IMAGE carrying
MORE separators and none the transcription, and 113 of 604 lines do not verify.
"""

from __future__ import annotations

import random
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from walk_verifier import load_words  # noqa: E402

from aldegonde import c3301  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "liber-primus__transcription--master.txt"
SOLVED_LINES = 187
IDX = {r: i for i, r in enumerate(c3301.CICADA_ALPHABET)}
MAXLEN = 13


def rune_word_lengths(text: str) -> list[int]:
    out: list[int] = []
    cur = 0
    for ch in text:
        if ch in IDX:
            cur += 1
        elif ch in c3301.WORD_BOUNDARY and cur:
            out.append(cur)
            cur = 0
    if cur:
        out.append(cur)
    return out


def sample(base: list[int], runes: int, rng: random.Random) -> list[int]:
    """Draw words from `base` until the rune budget is spent."""
    out: list[int] = []
    total = 0
    while total < runes:
        length = rng.choice(base)
        out.append(length)
        total += length
    return out


def lose_random(words: list[int], q: float, rng: random.Random) -> list[int]:
    """H1: every separator is equally likely to go missing."""
    out: list[int] = []
    i = 0
    while i < len(words):
        if i + 1 < len(words) and rng.random() < q:
            out.append(words[i] + words[i + 1])
            i += 2
        else:
            out.append(words[i])
            i += 1
    return out


def lose_at_short(
    words: list[int], q: float, rng: random.Random, *, into_prev: bool
) -> list[int]:
    """H2: only 2-rune words are absorbed, into the previous or the next word."""
    out: list[int] = []
    i = 0
    while i < len(words):
        short = words[i] == 2 and rng.random() < q
        if short and into_prev and out:
            out[-1] += 2
            i += 1
        elif short and not into_prev and i + 1 < len(words):
            out.append(2 + words[i + 1])
            i += 2
        else:
            out.append(words[i])
            i += 1
    return out


def chi_square(model: list[int], observed: Counter[int], n: int) -> tuple[float, int]:
    counts = Counter(model)
    total = sum(counts.values())
    stat = 0.0
    cells = 0
    for length in range(1, MAXLEN):
        expected = counts[length] / total * n
        if expected > 5:
            stat += (observed[length] - expected) ** 2 / expected
            cells += 1
    return stat, cells


def main() -> None:
    rng = random.Random(23)
    solved = rune_word_lengths("\n".join(MASTER.read_text().split("\n")[:SOLVED_LINES]))
    unsolved = [len(w) for w in load_words()]
    runes = sum(unsolved)
    n = len(unsolved)
    observed = Counter(unsolved)
    print(f"unsolved {n:,} words / {runes:,} runes, mean {runes / n:.3f}")
    print(f"solved base {len(solved):,} words, mean {sum(solved) / len(solved):.3f}\n")

    reps = 8

    def fit(fn) -> tuple[float, float, list[int]]:
        best: tuple[float, float, list[int]] | None = None
        for step in range(0, 60, 3):
            q = step / 100
            model: list[int] = []
            for _ in range(reps):
                model += fn(sample(solved, runes, rng), q)
            stat, _ = chi_square(model, observed, n)
            if best is None or stat < best[0]:
                best = (stat, q, model)
        assert best is not None
        return best

    def describe(label: str, result: tuple[float, float, list[int]]) -> None:
        model = result[2]
        counts = Counter(model)
        total = sum(counts.values())
        mean = sum(model) / total
        two = 100 * counts[2] / total
        print(
            f"{label:<26} q={result[1]:.2f}  chi2 {result[0]:>5.0f}"
            f"   mean {mean:.3f}   2-rune {two:.1f}%"
        )

    plain = []
    for _ in range(reps):
        plain += sample(solved, runes, rng)
    stat, cells = chi_square(plain, observed, n)
    print(
        f"{'observed (target)':<26} {'':6}  {'':10}   mean {runes / n:.3f}"
        f"   2-rune {100 * observed[2] / n:.1f}%"
    )
    print(
        f"{'no loss at all':<26} {'':6}  chi2 {stat:>5.0f}"
        f"   mean {sum(plain) / len(plain):.3f}"
        f"   2-rune {100 * Counter(plain)[2] / len(plain):.1f}%   ({cells} df)"
    )

    h1 = fit(lambda w, q: lose_random(w, q, rng))
    describe("H1 random loss", h1)
    h2n = fit(lambda w, q: lose_at_short(w, q, rng, into_prev=False))
    describe("H2 absorbed into next", h2n)
    h2p = fit(lambda w, q: lose_at_short(w, q, rng, into_prev=True))
    describe("H2 absorbed into prev", h2p)

    # H1's real failure is not chi-square, which base noise makes permissive, but
    # that it cannot hit the mean and the 2-rune share at once.
    print("\nH1 tuned to the observed MEAN instead of to chi-square:")
    for q in (0.03, 0.06, 0.09):
        model = []
        for _ in range(reps):
            model += lose_random(sample(solved, runes, rng), q, rng)
        counts = Counter(model)
        total = sum(counts.values())
        print(
            f"  q={q:.2f}  mean {sum(model) / total:.3f}"
            f"   2-rune {100 * counts[2] / total:.1f}%"
        )
    print("  no q reaches mean 4.43 and 2-rune 15.9% together: random loss moves")
    print("  the mean without reshaping the histogram. That is H1's refutation.")

    best = min((h2p, h2n), key=lambda r: r[0])
    counts = Counter(best[2])
    total = sum(counts.values())
    print(f"\nbest model residuals (q={best[1]:.2f})")
    print(f"{'runes':>6}{'observed':>10}{'model':>9}{'resid':>8}")
    for length in range(1, MAXLEN):
        expected = counts[length] / total * n
        resid = (observed[length] - expected) / max(expected, 1) ** 0.5
        print(f"{length:>6}{observed[length]:>10}{expected:>9.0f}{resid:>+8.1f}")

    # Is the leftover chi-square real, or noise from a ~700-word base?
    boot = []
    for _ in range(120):
        resampled = [rng.choice(solved) for _ in solved]
        model: list[int] = []
        for _ in range(reps):
            model += lose_at_short(
                sample(resampled, runes, rng), best[1], rng, into_prev=True
            )
        boot.append(chi_square(model, observed, n)[0])
    boot.sort()
    above = sum(1 for b in boot if b >= best[0])
    print(
        f"\nbase resampled from its own {len(solved)} words: median chi2 "
        f"{statistics.median(boot):.0f}, 90% range {boot[6]:.0f}-{boot[-7]:.0f}"
    )
    print(
        f"draws at or above the fitted {best[0]:.0f}: {above}/120 ({100 * above / 120:.0f}%)"
    )
    print("\nSo the fit is adequate and the loss is selective, not inattentive.")
    lost = int(best[1] * observed[2] / (1 - best[1]))
    print(
        f"implied omissions: roughly {lost} separators, ~{100 * lost / n:.0f}% of words"
    )


if __name__ == "__main__":
    main()
