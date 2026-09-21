---
type: observation
---
# No Integer-Sequence Keystream Fits Any Window of the Body

## Status

**Status**: confirmed, with a planted positive control. It closes a coverage gap in
`sequence_key_sweep.py` that would have hidden a running key past rune 4,000.

## Why this needed redoing

`sequence_key_sweep.py` is the careful version of the sequence sweep: it scores a
**prefix** so a later interrupt cannot hide a correct generator, varies the sequence
start, scores with runeglish trigrams, and carries a positive control on the author's own
prime-running-key page. It has two limits that together leave most of the body untested.

- **It tests one window** — the first 57 runes. The author interrupts his keystream about
  once per 85 runes on the AN END page, so any stretch is only usable if it happens to be
  interrupt-free, and betting on the first one is betting on a single draw.
- **Its sequences are 4,000 terms long.** The body is 12,956 runes. A key that runs on
  through the book is *undefined* past rune 4,000, so it was never tested there at all.

The second is the serious one: it is not that the test failed past rune 4,000, it is that
no test existed.

## What was done

`experiments/window_sequence_sweep.py` slides a 57-rune window across the body in steps of
29 — 445 positions — and at each one tries all 24 generators, 29 alphabet offsets and both
senses. Sequences are built to 14,000 terms so a running key is defined everywhere.

Two readings of "start", because they are different hypotheses:

- **the key runs on**: at a window at rune `p` the key index is `p` minus the interrupts
  before it, so the starts that matter are `[p − 200, p]`. This covers any interrupt count
  up to 200, which at the AN END page's rate covers the whole body.
- **the key restarts**: starts `[0, 200)` at every window, which asks whether some page or
  section begins the sequence afresh.

## The control

A planted prime(n)−1 keystream over the real AN END plaintext, buried in 400 random runes
so the sweep has to locate it as well as name it:

    top hit  score +14.265 at position 224, generator prime(n)-1, start 24
    generators in the top ten: prime(n), prime(n)+1, prime(n)-1

Found, correctly placed, and the top ten contains nothing but the prime family. (The three
prime variants tie because they differ by a constant, which the 29 alphabet offsets
absorb — a check that the offset search works.)

## The result

| reading | pairs | best score | position | generator | z in its own scan |
|---|---|---|---|---|---|
| key runs on | 10,680 | 11.636 | 5,829 | totient | **+2.62** |
| key restarts | 10,680 | 11.514 | 9,425 | prime(n)−1 | **+2.55** |
| **planted control** | | **14.265** | | | |

Median 10.04, sd 0.66. **The body's best is under three sigma of a ten-thousand-cell
scan**, which is less than the maximum of that many independent draws would give, and it
is 2.6 score points — about four sigma — below what the true key scores.

## What this excludes

The body is not an additive keystream over the standard rune order from any of: prime(n),
prime(n)±1, prime index, prime gaps, fibonacci, lucas, totient, divisor sum, factorials,
squares, triangular numbers, digit sums, 3301·n and the rest of the 24 — at any phase,
with or without interrupts, restarting or running on, anywhere in the body.

That matters because a prime running key is exactly the shape
`no-running-key-depth.md` leaves open: flat, non-repeating, arithmetic rather than copied
from a text. **And it is the cipher the author used on the very next page.** The natural
guess was worth testing properly, and it fails.

## Scope

Additive keystreams over the standard rune order. A mixed alphabet inside the loop does
not linearise under subtraction and is untouched — the same scope caveat
`sequence_key_sweep.py` records. Also untouched: sequences outside the 24, and
interrupt counts above 200.

## Falsification

- If the true generator is in the list, the sweep must find it. The planted control shows
  it does, at a 2.6-point margin over the body's best.
- Widening the window makes an interrupt-free stretch rarer; narrowing it weakens the
  scorer. 57 runes is the author's own scale (one interrupt in 85 runes on AN END) and the
  control confirms it works there.
- If interrupts run at more than 200 over the body, the "runs on" arm misses. That is a
  rate above 1.5%, against the 1.2% the solved page shows.

## Scripts

- `experiments/window_sequence_sweep.py`
- `experiments/sequence_key_sweep.py` — the single-window version this extends.

## Related

- `running-key-math-sequence.md` — the hypothesis, now excluded far more thoroughly.
- `no-running-key-depth.md` — which excludes repeating and language keys and explicitly
  leaves arithmetic ones open.
- `interrupter-is-a-scribal-mark.md` — the interrupt rate this is sized against.
