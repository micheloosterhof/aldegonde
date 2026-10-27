aldegonde
=========

``aldegonde`` is a Python library for classical cryptography and
cryptanalysis. It is written to accommodate non-standard alphabets (not just
A-Z), which makes it suited to cipher systems with custom symbol sets such as
the 29 runes of Cicada 3301's Liber Primus.

Install
-------

.. code-block:: bash

    pip install -e ".[dev]"      # library plus the test and lint tools
    make check                   # ruff, ty and pytest, what CI runs

Use
---

.. code-block:: python

    from aldegonde import masc, pasc
    from aldegonde.stats import nioc, kappa_spectrum

    ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    key = masc.shiftedkey(ABC, shift=3)
    ciphertext = "".join(masc.masc_encrypt("ATTACKATDAWN", key=key))

    tr = pasc.vigenere_tr(ABC)
    ciphertext = "".join(pasc.pasc_encrypt("ATTACKATDAWN", keyword="LEMON", tr=tr))

Functions that index tables or do arithmetic take integers ``0..N-1`` and an
explicit alphabet size; ``aldegonde.alphabet.Alphabet`` converts symbols at
the edge. Statistics that only compare symbols for equality are generic.

Layout
------

- ``src/aldegonde/`` the library: ciphers, ``stats``, ``analysis``, ``maths``,
  and ``c3301`` for the Liber Primus (alphabet, marks, tokenizer, codecs)
- ``tests/aldegonde/`` the test suite, mirroring ``src``
- ``data/`` the Liber Primus transcriptions and sample texts (``data/README.rst``)
- ``experiments/`` analysis scripts (``experiments/CLAUDE.md`` is the guide)
- ``hypotheses/`` one file per observation or hypothesis (``INDEX.md``)
- ``docs/`` the backlog (``library-candidates.md``) and the research
  directions (``new-directions.md``)

``CLAUDE.md`` describes the conventions in full.
