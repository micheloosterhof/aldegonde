---
type: observation
---
# Observation: No Window of the Body Reads as Plaintext or Monoalphabetic

## The gap this closes

`the-body-is-one-cipher.md` tests homogeneity across 9 sections and 55 pages, and proves
its own power by surfacing the Parable — a page stored as plaintext — at +7 sd. Its
stated scope limit is scale: a difference confined to a few dozen runes would not survive
averaging over a 230-rune page.

So slide a window instead of partitioning. The index of coincidence rises for plaintext
**and** for any monoalphabetic substitution of it — a fixed substitution preserves
coincidence exactly — so one statistic covers both easy cases at once.

## Result

| window | body's best | at offset | shuffled null's best | z |
|---|---|---|---|---|
| 100 | 1.301 | 31 | 1.356 ± 0.036 | −1.54 |
| 200 | 1.109 | 3,542 | 1.146 ± 0.020 | −1.88 |
| 400 | 1.074 | 10,466 | 1.075 ± 0.009 | −0.13 |

**The body's most coincidence-rich window is less coincidence-rich than a shuffled
corpus's**, at every width. That is the doublet suppression making the corpus slightly
under-dispersed, and it means there is nothing to report at any scale from 100 runes up.

## The control

Splicing a real stretch of the author's own plaintext into the body at offset 6,000:

| window | scan maximum | located at | verdict |
|---|---|---|---|
| 100 | 1.564 | 5,992 | found |
| 200 | 1.610 | 6,000 | found, exactly |
| 400 | 1.707 | 5,999 | found |

So a plaintext or monoalphabetic passage of 100 runes or more would be located, not
merely detected. The body contains none.

## Consequence

Combined with the page-level test, the body is uniform from 100 runes to 3,000. There is
no paragraph, page or section enciphered more simply, and no crib to be had by looking
for one. Every remaining approach has to work on the cipher as it stands.

## Scope

- Coincidence only. A stretch enciphered with a *different polyalphabetic* key would not
  raise IoC and is not covered — but that stretch would be no easier than the rest.
- Windows of 100 or more. A plaintext run of a few dozen runes stays invisible, and would
  be too short to crib from anyway.

## Status

**Status**: confirmed (measurement), with a splice control that locates a planted
plaintext passage at three widths. `experiments/window_ioc_scan.py`.

## Related

- `the-body-is-one-cipher.md` — the page-level test whose scale gap this closes.
- `no-known-plaintext-foothold.md` — the same conclusion reached from crib search.
