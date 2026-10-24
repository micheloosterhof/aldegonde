Data files
==========

Liber Primus
------------

``liber-primus__transcription--master.txt``
    The full transcription, solved and unsolved pages, 15,933 runes.
    ``liber-primus__transcription--master.md`` is the same with notes.
    ``SYMBOLS.md`` explains every non-rune character.

``page0-56.txt``
    Master pages 15 to 70: the whole unsolved body, 12,956 runes in 2,928
    words. The name counts the file's own 56 pages. This is the clean corpus
    every experiment measures; tokenize it with ``aldegonde.c3301.tokenize``
    or ``experiments/lp_corpus.load_clean``.

``page0-58.txt``
    The late corpus, 13,136 runes. Its last two ``$`` sections are solved
    (the AN END page and the plaintext Parable); exclude them.

``register_vocab.txt``
    The author's vocabulary from the solved pages, for cribbing. Rebuilt by
    ``experiments/build_register_vocab.py``.

``sample_plaintext.txt``
    Pangrams for quick checks.

``ngrams/``
    N-gram tables for English and runeglish, shipped with the package under
    ``src/aldegonde/data/ngrams``.

Samples
-------

Small classical test vectors for the cipher modules, English alphabet.

``samples/alice-plaintext.txt``
    1,033 letters of Alice in Wonderland, uppercase, no spaces.

``samples/alice-vigenere-lemon.txt``
    The same text under Vigenère with key ``LEMON``; verified with
    ``pasc.vigenere_tr``.

``samples/alice-beaufort-variant-lemon.txt``
    The same text under a Beaufort variant with key ``LEMON``. It does not
    match ``pasc.beaufort_tr`` on the standard alphabet; the variant is
    unrecorded.

``samples/kentucky-vigenere.txt``
    A plaintext about Bletchley Park and its Vigenère ciphertext under the
    keyphrase ``Northern Kentucky University``, in five-letter groups.
