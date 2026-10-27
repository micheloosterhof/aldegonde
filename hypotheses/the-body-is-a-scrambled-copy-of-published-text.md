---
type: hypothesis
---
# Hypothesis: The Body Is a Word-Scrambled Re-Encipherment of Text the Author Already Published

## Claim

The plaintext is not new. It is text Cicada published elsewhere (the 2012 to 2014
messages, the poems, the onion-site texts, the solved pages themselves), with the words
of each sentence shuffled (`the-words-are-transposed-within-sentences.md`) and enciphered.
If so the body is a known-plaintext problem, and the word lengths, which are public,
identify the source sentence by sentence.

## Status

**Status**: unresolved; the solved pages are excluded as the source. Proposed 2026-10-25.

## Mechanism

A shuffled sentence keeps its multiset of word lengths and its rune total. The body's
spans between cluster marks are the sentences (`the-four-dot-may-be-a-displaced-stop.md`
notwithstanding, the span is the unit the test needs). Match each span's sorted length
multiset against every sentence of a candidate source, allowing the joining rule of
`short-units-are-written-joined.md` (a 2-rune word absorbed into a neighbour) when
comparing.

## Evidence for

- E1/E2: the block lengths have the marginal of running text and the serial order of
  nothing, which is what shuffled sentences look like. October 2026: measured directly — adjacent block lengths inside a span are independent, z −0.10 against the body's own within-span shuffle, where intact order with the body's joining applied reads +5.1 on the author's pages and +5.8 to +17.1 on prose at the body's size (`experiments/length_adjacency_self_null.py`).
- The author re-uses his own text: the Parable and the AN END page appear in the book and
  outside it.
- Cribs broke the early pages; a shuffled known text defeats a phrase crib while keeping
  the words.

## Evidence against

- `experiments/closed_channels_october_2026.py copy`: of 137 body spans, **0** share a
  word-length multiset with any of the author's 94 known sentences, against 2.9 for a
  null that recuts the author's own words. The solved pages are not the source.
- The other candidate sources are not in the repository, so the test stops here.

## Predictions

1. For the true source, spans of eight words or more match sentences by multiset and
   rune total at a rate no recut null approaches; one such match for a long span is
   already decisive, since the chance of an exact multiset match for a 10-word sentence
   is small.
2. Matches would cluster by document: a page of the body maps onto a passage of the
   source in order, even with the words inside each sentence shuffled.

## Scripts

- `experiments/closed_channels_october_2026.py copy` — the solved-page run.
- To add: a loader for the external texts (`build_register_vocab.py` names them: the
  2012–2013 messages, the 2014 stage-11 English) and the join-tolerant matcher.

## Related

- `the-words-are-transposed-within-sentences.md`, `the-rearrangement-is-not-a-simple-rule.md`
- `rubrication-crib-candidates.md` — the only cribs the body offers today, 52 words.

## Verdict

Open for the external sources, closed for the solved pages.
