# ABOUTME: Decodes the word-delimited Quagmire with a doublet dodge, measuring how often
# ABOUTME: the output-conditioned skip leaves two readings and how far apart they stay.
"""How bad is the dodge family's decoding ambiguity?

`doublet-dodge-walk.md` records the standing objection to the whole dodge family: the
skip is conditioned on the OUTPUT, so it cannot be undone, and two plaintexts collide.
That verdict was reached by exhibiting one collision. It never asked how OFTEN the
collision happens, nor how much plaintext a collision costs.

Set the decoding up properly. At position j the decoder holds the clock `k`, the base,
and the whole ciphertext, so it knows `c_(j-1)` exactly. Two hypotheses:

    N (no skip):  p = A_k^-1(base^-1(c_j)),     consistent iff c_j != c_(j-1)
    D (skip):     p = A_(k+1)^-1(base^-1(c_j)), consistent iff base(A_k(p)) == c_(j-1)

Both are checkable against the ciphertext alone, which gives three results.

**Observed doublets are never ambiguous.** N requires `c_j != c_(j-1)`, so a doublet in
the ciphertext forces D. Doublets announce themselves.

**Ambiguity is one shift diagonal.** D is consistent only when `u_j = u_(j-1) + s_(k+1)`
in K coordinates. Measured over four keys: 4.5% to 6.5% of positions, against the 3.4%
of a flat diagonal.

**Almost every ambiguity is self-punishing.** This is what the earlier verdict missed.
A rival reading leaves the clock one step out, and since a skip only ever ADDS a step
the offset is normally permanent: every later rune decodes through the wrong alphabet
and the branch turns to garbage. Between 524 and 738 of the rivals per key never rejoin
the true path, against 33 to 63 that do. They are ambiguous for one rune and obviously
wrong for the rest of the text.

The exception is a rival that defers the skip rather than dropping it:

    truth  skips at j:      k -> k+2, and reads position j+1 with A_(k+2)
    rival  skips at j+1:    k -> k+1 -> k+3, and reads position j+1 with A_(k+2)

Same alphabet at j+1, same clock after it, and the base rolls identically from there, so
the readings rejoin and differ on a handful of runes only. That needs the ciphertext to
admit a skip at j+1 as well, and it is the rarer case by a factor of ten.

So the collision is real but it costs a few letters rather than the message. A beam
search recovers 12,382 to 12,388 of 12,388 runes, exactly for two keys of the four.
Widening the beam eightfold changes nothing, and the trigram model scores the wrong
reading HIGHER than the truth, so what is left is the weakness of a rune trigram model
rather than of the cipher: FORGOTTEN decodes as FORGBTTEN, which a reader repairs and a
trigram model cannot.

Unique decodability still fails — distinct plaintexts do share a ciphertext. What the
measurement changes is the price: a handful of runes in a corpus, not the message.

Run with no arguments.
"""

from __future__ import annotations

import math
import random
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "experiments"))

from fingerprint_battery import (  # noqa: E402
    M,
    compose,
    ppow,
    prose_corpora,
    rich_order5,
)
from quagmire_dodge import alphabets, encipher, schedule  # noqa: E402
from quagmire_runner import conj_shift  # noqa: E402

SEP = M  # word separator, the 30th symbol of the plaintext language model
BEAM = 50
MERGE_DEPTH = 24  # how far a rival branch is followed before it counts as stranded


def invert(perm):
    out = [0] * len(perm)
    for x, y in enumerate(perm):
        out[y] = x
    return out


def trigram_model(corpora):
    """Add-one trigram log-probabilities over runes plus a word separator."""
    counts: dict[tuple[int, int, int], int] = {}
    context: dict[tuple[int, int], int] = {}
    for words in corpora:
        stream = [SEP, SEP]
        for word in words:
            stream.extend(word)
            stream.append(SEP)
        for i in range(2, len(stream)):
            key = (stream[i - 2], stream[i - 1], stream[i])
            counts[key] = counts.get(key, 0) + 1
            context[key[:2]] = context.get(key[:2], 0) + 1
    size = M + 1
    floor = math.log(1.0 / size)

    def score(a: int, b: int, c: int) -> float:
        total = context.get((a, b), 0)
        if not total:
            return floor
        return math.log((counts.get((a, b, c), 0) + 1) / (total + size))

    return score


class Cipher:
    """The key plus the ciphertext, exposing the decoder's one-position move set."""

    def __init__(self, cipher, base0, alpha, sigma):
        self.alpha = alpha
        self.ainv = [invert(a) for a in alpha]
        self.sigma = sigma
        self.flat = [c for word in cipher for c in word]
        self.ends = []
        for word in cipher:
            self.ends.extend([False] * (len(word) - 1) + [True])
        self.start = (0, 0, tuple(base0), tuple(invert(base0)))

    def moves(self, state):
        """Every (plaintext rune, new clock) consistent with the ciphertext here."""
        j, clock, base, binv = state
        c = self.flat[j]
        previous = self.flat[j - 1] if j else None
        out = []
        if c != previous:
            out.append((self.ainv[clock % 5][binv[c]], clock + 1))
        if previous is not None:
            q = self.ainv[(clock + 1) % 5][binv[c]]
            if base[self.alpha[clock % 5][q]] == previous:
                out.append((q, clock + 2))
        return out

    def advance(self, state, clock):
        """Consume the rune, rolling the base if the word ended."""
        j, _old, base, binv = state
        if self.ends[j]:
            step = compose(list(base), compose(self.alpha[(clock - 1) % 5], self.sigma))
            return (j + 1, clock, tuple(step), tuple(invert(step)))
        return (j + 1, clock, base, binv)

    @staticmethod
    def merged(a, b):
        """Two states read every later rune identically iff these agree."""
        return (a[0], a[1] % 5, a[2]) == (b[0], b[1] % 5, b[2])


def true_path(cipher: Cipher, plain):
    """The states the encipherer passed through, one per rune."""
    states = []
    state = cipher.start
    for word in plain:
        for p in word:
            _j, clock, base, _binv = state
            states.append(state)
            if base[cipher.alpha[clock % 5][p]] == (
                cipher.flat[state[0] - 1] if state[0] else None
            ):
                clock += 1
            state = cipher.advance(state, clock + 1)
    return states


def survey(cipher: Cipher, plain, depth=MERGE_DEPTH):
    """Ambiguity rate, and how many runes a rival reads before rejoining the true path.

    A rival that rejoins agrees with the truth on every later rune, so those runes are
    the whole price of the collision. A rival that does not rejoin is reading every
    later rune through the wrong alphabet, which any reader can see.
    """
    states = true_path(cipher, plain)
    flat_p = [p for word in plain for p in word]
    ambiguous, doublets = 0, 0
    rejoined: list[int] = []
    stranded = 0
    for j, state in enumerate(states):
        options = cipher.moves(state)
        if j and cipher.flat[j] == cipher.flat[j - 1]:
            doublets += 1
            assert len(options) == 1, "an observed doublet must force the skip"
        if len(options) < 2:
            continue
        ambiguous += 1
        rival = next(m for m in options if m[0] != flat_p[j])
        cost = walk_to_merge(cipher, states, cipher.advance(state, rival[1]), depth)
        if cost < 0:
            stranded += 1
        else:
            rejoined.append(cost)
    return ambiguous, doublets, rejoined, stranded


def walk_to_merge(cipher: Cipher, states, start, limit) -> int:
    """Runes the rival reads before rejoining the true path; -1 within `limit` runes."""
    seen = {start}
    frontier = deque([(start, 1)])
    while frontier:
        state, read = frontier.popleft()
        if state[0] < len(states) and cipher.merged(state, states[state[0]]):
            return read
        if read >= limit or state[0] >= len(states):
            continue
        for _p, clock in cipher.moves(state):
            nxt = cipher.advance(state, clock)
            if nxt not in seen:
                seen.add(nxt)
                frontier.append((nxt, read + 1))
    return -1


def decode(cipher: Cipher, score, beam=BEAM):
    """Beam search over the skip/no-skip branches, scored by plaintext trigrams."""
    live = [(0.0, cipher.start, SEP, SEP, ())]
    for _j in range(len(cipher.flat)):
        nxt: dict[tuple, tuple] = {}
        for total, state, a, b, text in live:
            for p, clock in cipher.moves(state):
                after = cipher.advance(state, clock)
                carry = (after[0], after[1] % 5, after[2], b, p)
                cand = (total + score(a, b, p), after, b, p, (*text, p))
                if carry not in nxt or cand[0] > nxt[carry][0]:
                    nxt[carry] = cand
        live = sorted(nxt.values(), key=lambda s: -s[0])[:beam]
        assert live, "every branch died"
        # close the word so the separator is scored in the right place
        if cipher.ends[live[0][1][0] - 1]:
            live = [
                (total + score(a, b, SEP), state, b, SEP, (*text, SEP))
                for total, state, a, b, text in live
            ]
    best = max(live, key=lambda s: s[0])
    words, current = [], []
    for symbol in best[4]:
        if symbol == SEP:
            words.append(current)
            current = []
        else:
            current.append(symbol)
    if current:
        words.append(current)
    return words


def total_score(words, score) -> float:
    a, b, out = SEP, SEP, 0.0
    for word in words:
        for r in (*word, SEP):
            out += score(a, b, r)
            a, b = b, r
    return out


def draw_key(rng):
    K = rng.sample(range(M), M)
    offsets = schedule(rng, zeros=1)
    return (
        offsets,
        alphabets(K, offsets),
        conj_shift(rng.sample(range(M), M), rng.randrange(1, M)),
        rng.sample(range(M), M),
    )


def run_key(plain, score, key, *, check_beam: bool):
    offsets, alpha, sigma, base0 = key
    cipher = Cipher(encipher(plain, base0, alpha, sigma), base0, alpha, sigma)
    n = len(cipher.flat)
    ambiguous, doublets, rejoined, stranded = survey(cipher, plain)
    assert doublets > 0, "a one-zero schedule should still emit doublets"
    assert 0.4 / M < ambiguous / n < 3.0 / M, "ambiguity should sit near one diagonal"

    # A rival either rejoins the true path, costing the runes it read on the way, or
    # reads every later rune through a clock one step out. How many rejoin depends on
    # the horizon allowed, so report the count at two of them rather than one.
    near = len([c for c in rejoined if c <= MERGE_DEPTH // 2])
    got = decode(cipher, score)
    runes_ok = sum(
        x == y for a, b in zip(got, plain) for x, y in zip(a, b) if len(a) == len(b)
    )
    print(
        f"{str(offsets)[:21]:<22} {doublets:>5} {ambiguous:>6} {ambiguous / n:>8.4f} "
        f"{near:>7} {len(rejoined):>7} {stranded:>9} {runes_ok:>7,}/{n:,}"
    )
    assert stranded > 3 * len(rejoined), (
        "the common case must be a rival that strands itself, since a skip only adds "
        "steps and the clock offset is therefore permanent"
    )
    assert runes_ok / n > 0.998, "the beam search should recover nearly every rune"
    if not check_beam:
        return
    assert decode(cipher, score, beam=BEAM * 8) == got, (
        "a beam 8x wider must change nothing, or the true path is being pruned"
    )
    truth, found = total_score(plain, score), total_score(got, score)
    print(f"\nbeam {BEAM * 8} decode identical, so the true path is never pruned")
    print(f"trigram score  truth {truth:.2f}   decoded {found:.2f}")
    assert found >= truth, (
        "if the truth scored higher the search would have found it; the residual "
        "errors must be the language model, not the cipher"
    )
    print("the residual errors score HIGHER than the truth: the limit is the model\n")


def draw_walk_key(rng):
    """The same cipher with `g^k` in place of the Quagmire's five alphabets.

    `doublet_dodge_walk.encipher` is this code with `alpha[k] = g^k`, base step
    included, so the decoder needs no change and the two models can be compared on the
    same measurement.
    """
    g = rich_order5(rng)
    return (
        ["g^k"],
        [ppow(g, k) for k in range(5)],
        conj_shift(rng.sample(range(M), M), rng.randrange(1, M)),
        rng.sample(range(M), M),
    )


def self_test() -> None:
    rng = random.Random(3301)
    train, plain = prose_corpora(2928, 2)
    score = trigram_model([train])
    print(
        f"{len(plain):,} words; a flat shift diagonal would give an ambiguity "
        f"rate of {1 / M:.4f}\n"
    )
    header = (
        f"{'letter step':<22} {'dblts':>5} {'ambig':>6} {'rate':>8} "
        f"{'<=12':>7} {'<=24':>7} {'stranded':>9} {'runes recovered':>16}"
    )
    print("Quagmire schedule with one zero offset (quagmire-dodge.md)")
    print(header)
    for i in range(4):
        run_key(plain, score, draw_key(rng), check_beam=i == 0)

    # The objection this measurement retracts is recorded against the WALK, so measure
    # the walk too rather than carry the Quagmire's numbers across to it.
    print("\nlength-clocked walk, g of order 5 (doublet-dodge-walk.md)")
    print(header)
    for _ in range(3):
        run_key(plain, score, draw_walk_key(rng), check_beam=False)
    print("\nself-test passed")


if __name__ == "__main__":
    self_test()
