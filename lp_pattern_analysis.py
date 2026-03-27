#!/usr/bin/env python3
"""Liber Primus pattern analysis: known catch phrases, reversed text, direct matching."""

import sys
sys.path.insert(0, '/home/user/aldegonde/src')

from aldegonde.c3301 import CICADA_ALPHABET, CICADA_ENGLISH_ALPHABET, r2i

# Build mappings
rune_to_eng = {}
for i, rune in enumerate(CICADA_ALPHABET):
    rune_to_eng[rune] = CICADA_ENGLISH_ALPHABET[i]

eng_to_rune = {}
for i, eng in enumerate(CICADA_ENGLISH_ALPHABET):
    eng_to_rune[eng] = CICADA_ALPHABET[i]

# ============================================================
# Parse data file into sections
# ============================================================
data = open('/home/user/aldegonde/data/page0-58.txt').read()

# Split by &\n to get major sections
raw_sections = data.split('&\n')
print(f"Raw sections from splitting by '&\\n': {len(raw_sections)}")

# Clean sections: remove $, %, strip, remove empty
sections = []
for i, s in enumerate(raw_sections):
    # Remove $ and % lines and clean
    lines = s.strip().split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line in ('$', '%', ''):
            continue
        cleaned_lines.append(line)
    if cleaned_lines:
        text = '\n'.join(cleaned_lines)
        sections.append(text)

print(f"Cleaned sections (non-empty): {len(sections)}")
for i, s in enumerate(sections):
    # Count runes
    rune_count = sum(1 for c in s if c in rune_to_eng)
    preview = s[:60].replace('\n', '|')
    print(f"  Section {i}: {rune_count} runes, preview: {preview}")

# ============================================================
# Helper functions
# ============================================================
def text_to_flat_runes(text):
    """Extract just the rune characters, preserving word/sentence structure markers."""
    result = []
    for c in text:
        if c in rune_to_eng:
            result.append(c)
        elif c in ('-', '.', '/', '\n', '%', '&', '$'):
            result.append(c)
    return ''.join(result)

def parse_sentences(text):
    """Parse text into sentences, each sentence is a list of words (list of rune strings)."""
    # Remove line breaks (/ and \n) - they are just formatting
    flat = text.replace('/', '').replace('\n', '')
    # Remove % (page breaks within a section)
    flat = flat.replace('%', '')
    # Split by . to get sentences
    raw_sentences = flat.split('.')
    sentences = []
    for sent in raw_sentences:
        sent = sent.strip()
        if not sent:
            continue
        words = sent.split('-')
        words = [w for w in words if w]  # remove empty
        if words:
            sentences.append(words)
    return sentences

def word_length_pattern(words):
    """Get the word length pattern (list of rune counts per word)."""
    return [len(w) for w in words]

def runes_to_english(rune_str):
    """Convert a rune string to English using CICADA_ENGLISH_ALPHABET."""
    return ''.join(rune_to_eng.get(r, '?') for r in rune_str)

def english_to_runeglish(eng_text):
    """Convert English text to rune-length pattern.
    Returns the runeglish string and word lengths.
    Multi-char English mappings (TH, EO, NG, OE, AE, IA, EA) map to single runes.
    """
    # Build a list of English -> rune for conversion
    # We need to handle multi-char mappings: TH, EO, NG, OE, AE, IA, EA
    # Process longest first
    multi_map = {}
    single_map = {}
    for eng, rune in zip(CICADA_ENGLISH_ALPHABET, CICADA_ALPHABET):
        if len(eng) > 1:
            multi_map[eng] = rune
        else:
            single_map[eng] = rune

    words = eng_text.split()
    rune_words = []
    for word in words:
        runes = []
        i = 0
        w = word.upper()
        while i < len(w):
            matched = False
            # Try 2-char matches first
            if i + 1 < len(w):
                digraph = w[i:i+2]
                if digraph in multi_map:
                    runes.append(multi_map[digraph])
                    i += 2
                    matched = True
            if not matched:
                if w[i] in single_map:
                    runes.append(single_map[w[i]])
                    i += 1
                else:
                    # Unknown char, skip
                    i += 1
        rune_words.append(''.join(runes))
    return rune_words

# ============================================================
# Part 1: Known Cicada Catch Phrases
# ============================================================
print("\n" + "=" * 80)
print("PART 1: KNOWN CICADA CATCH PHRASES")
print("=" * 80)

known_phrases = [
    "AN INSTRUCTION",
    "KNOW THIS",
    "A WARNING",
    "AN END",
    "A BEGINNING",
    "SOME WISDOM",
    "THE INSTAR",
    "DIVINITY",
    "CIRCUMFERENCE",
    "CONSUMPTION",
    "COMMAND",
    "WELCOME",
    "PILGRIM",
    "LOST NOT ALL HOPE",
    "PARABLE",
    "LIKE THE INSTAR",
    "WE MUST",
    "FIND THE",
    "WITHIN",
    "FROM WITHIN",
    "THE DEEP",
    "PRIMES",
]

# Extract phrases from section 11 (solved plaintext)
print("\n--- Section 11 (solved plaintext) ---")
if len(sections) > 11:
    sect11 = sections[11]
    sect11_sentences = parse_sentences(sect11)
    print(f"Section 11 has {len(sect11_sentences)} sentences")
    for si, sent in enumerate(sect11_sentences):
        eng_words = [runes_to_english(w) for w in sent]
        print(f"  Sentence {si}: {' '.join(eng_words)}")
        # Add multi-word phrases from section 11
        phrase = ' '.join(eng_words)
        if phrase not in known_phrases:
            known_phrases.append(phrase)
        # Also add individual words >= 4 chars
        for ew in eng_words:
            if len(ew) >= 4 and ew not in known_phrases:
                known_phrases.append(ew)
else:
    print("Section 11 not found!")

# Convert known phrases to runeglish and get patterns
print("\n--- Known Phrase Patterns ---")
phrase_patterns = {}  # pattern tuple -> list of phrase names
for phrase in known_phrases:
    rune_words = english_to_runeglish(phrase)
    pattern = tuple(len(w) for w in rune_words)
    rune_repr = '-'.join(rune_words)
    eng_pattern = [len(w) for w in phrase.split()]
    print(f"  '{phrase}' -> runeglish: {rune_repr} -> eng_lengths: {eng_pattern} -> rune_lengths: {list(pattern)}")
    if pattern not in phrase_patterns:
        phrase_patterns[pattern] = []
    phrase_patterns[pattern].append(phrase)

# Parse sections 1-9 forward
print("\n--- Searching sections 1-9 for matching patterns ---")
forward_sentences = {}  # (section, sentence_idx) -> (words, pattern)
for sec_idx in range(1, min(10, len(sections))):
    sentences = parse_sentences(sections[sec_idx])
    for si, sent in enumerate(sentences):
        pattern = tuple(word_length_pattern(sent))
        forward_sentences[(sec_idx, si)] = (sent, pattern)

# Match
matches_forward = []
for (sec_idx, si), (sent, pattern) in forward_sentences.items():
    if pattern in phrase_patterns:
        eng_words = [runes_to_english(w) for w in sent]
        matches_forward.append((sec_idx, si, sent, pattern, phrase_patterns[pattern]))

print(f"\nForward matches found: {len(matches_forward)}")
for sec_idx, si, sent, pattern, phrases in matches_forward:
    rune_str = '-'.join(sent)
    eng_str = '-'.join(runes_to_english(w) for w in sent)
    print(f"  Section {sec_idx}, Sentence {si}: pattern {list(pattern)}")
    print(f"    Runes: {rune_str}")
    print(f"    English: {eng_str}")
    print(f"    Matches phrases: {phrases}")

# ============================================================
# Part 2: Reversed Text Analysis
# ============================================================
print("\n" + "=" * 80)
print("PART 2: REVERSED TEXT ANALYSIS")
print("=" * 80)

# Concatenate sections 1-9 preserving structure
combined_text = ""
for sec_idx in range(1, min(10, len(sections))):
    combined_text += sections[sec_idx] + "\n"

# Get just the meaningful characters (runes + separators)
flat = text_to_flat_runes(combined_text)

# Reverse the entire sequence
reversed_flat = flat[::-1]

print(f"\nForward text length: {len(flat)} chars")
print(f"Forward rune count: {sum(1 for c in flat if c in rune_to_eng)}")
print(f"Reversed text (first 200 chars): {reversed_flat[:200]}")

# Parse reversed text into sentences
# When reversed, the separators are still the same characters
reversed_sentences_raw = parse_sentences(reversed_flat)
print(f"\nReversed sentences count: {len(reversed_sentences_raw)}")

# Get patterns for reversed sentences
reversed_sentence_data = []
for si, sent in enumerate(reversed_sentences_raw):
    pattern = tuple(word_length_pattern(sent))
    reversed_sentence_data.append((sent, pattern))

# Compare reversed patterns against known phrases
matches_reversed = []
for si, (sent, pattern) in enumerate(reversed_sentence_data):
    if pattern in phrase_patterns:
        matches_reversed.append((si, sent, pattern, phrase_patterns[pattern]))

print(f"\nReversed matches found: {len(matches_reversed)}")
for si, sent, pattern, phrases in matches_reversed:
    rune_str = '-'.join(sent)
    eng_str = '-'.join(runes_to_english(w) for w in sent)
    print(f"  Reversed Sentence {si}: pattern {list(pattern)}")
    print(f"    Runes: {rune_str}")
    print(f"    English: {eng_str}")
    print(f"    Matches phrases: {phrases}")

# Duplicate pattern analysis
print("\n--- Duplicate Pattern Analysis ---")
forward_patterns = [p for _, p in forward_sentences.values()]
reversed_patterns = [p for _, p in reversed_sentence_data]

from collections import Counter
fwd_counter = Counter(forward_patterns)
rev_counter = Counter(reversed_patterns)

fwd_dups = {k: v for k, v in fwd_counter.items() if v > 1}
rev_dups = {k: v for k, v in rev_counter.items() if v > 1}

print(f"\nForward: {len(forward_patterns)} sentences, {len(fwd_dups)} duplicate patterns")
for p, c in sorted(fwd_dups.items(), key=lambda x: -x[1]):
    print(f"  {list(p)}: {c} times")

print(f"\nReversed: {len(reversed_sentence_data)} sentences, {len(rev_dups)} duplicate patterns")
for p, c in sorted(rev_dups.items(), key=lambda x: -x[1]):
    print(f"  {list(p)}: {c} times")

# Other interesting patterns in reversed text
print("\n--- Other Patterns in Reversed Text ---")
# Check for palindromic words
palindrome_count = 0
for si, (sent, pattern) in enumerate(reversed_sentence_data):
    for w in sent:
        if len(w) >= 3 and w == w[::-1]:
            palindrome_count += 1
            eng = runes_to_english(w)
            print(f"  Palindromic rune word in reversed sentence {si}: {w} ({eng})")

print(f"  Total palindromic words (len>=3) in reversed text: {palindrome_count}")

# Check if any reversed words match forward words
print("\n--- Checking reversed words that match forward words ---")
forward_words = set()
for (sec_idx, si), (sent, _) in forward_sentences.items():
    for w in sent:
        forward_words.add(w)

reversed_words_matching = set()
for si, (sent, _) in enumerate(reversed_sentence_data):
    for w in sent:
        rev_w = w[::-1]
        if rev_w in forward_words and len(w) >= 3:
            reversed_words_matching.add((w, rev_w))

print(f"  Reversed words matching forward words (len>=3): {len(reversed_words_matching)}")
for w, rev_w in sorted(reversed_words_matching, key=lambda x: -len(x[0]))[:20]:
    print(f"    {w} ({runes_to_english(w)}) <-> {rev_w} ({runes_to_english(rev_w)})")

# ============================================================
# Part 3: Direct Pattern Matching - Complete Listing
# ============================================================
print("\n" + "=" * 80)
print("PART 3: DIRECT PATTERN MATCHING - ALL SENTENCES")
print("=" * 80)

print("\n--- FORWARD Sentences (Sections 1-9) ---")
for sec_idx in range(1, min(10, len(sections))):
    sentences = parse_sentences(sections[sec_idx])
    print(f"\n  Section {sec_idx} ({len(sentences)} sentences):")
    for si, sent in enumerate(sentences):
        pattern = tuple(word_length_pattern(sent))
        rune_str = '-'.join(sent)
        eng_str = '-'.join(runes_to_english(w) for w in sent)
        flag = ""
        if pattern in phrase_patterns:
            flag = f" *** MATCH: {phrase_patterns[pattern]}"
        print(f"    S{si}: {list(pattern)} {eng_str}{flag}")
        if flag:
            print(f"         Runes: {rune_str}")

print("\n--- REVERSED Sentences ---")
for si, (sent, pattern) in enumerate(reversed_sentence_data):
    rune_str = '-'.join(sent)
    eng_str = '-'.join(runes_to_english(w) for w in sent)
    flag = ""
    if pattern in phrase_patterns:
        flag = f" *** MATCH: {phrase_patterns[pattern]}"
    print(f"  RS{si}: {list(pattern)} {eng_str}{flag}")
    if flag:
        print(f"       Runes: {rune_str}")

# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total known phrase patterns: {len(phrase_patterns)}")
print(f"Forward sentences (sections 1-9): {len(forward_sentences)}")
print(f"Reversed sentences: {len(reversed_sentence_data)}")
print(f"Forward matches: {len(matches_forward)}")
print(f"Reversed matches: {len(matches_reversed)}")
print(f"Forward duplicate patterns: {len(fwd_dups)}")
print(f"Reversed duplicate patterns: {len(rev_dups)}")
