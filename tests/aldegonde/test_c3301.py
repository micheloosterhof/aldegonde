import random
from collections import Counter
from pathlib import Path

import pytest

from aldegonde import c3301
from aldegonde.exceptions import AldegondeKeyError, AlphabetError


def test_welcome() -> None:
    data = [1, 28, 21, 15, 12, 0, 5, 4, 12, 1, 6, 13, 28, 28, 0, 7, 14, 16]
    seq = "".join([c3301.CICADA_ALPHABET[e] for e in data])
    assert seq == "ᚢᛠᛝᛋᛇᚠᚳᚱᛇᚢᚷᛈᛠᛠᚠᚹᛉᛏ"


def test_i2r() -> None:
    assert c3301.i2r(1) == "ᚢ"


def test_r2i() -> None:
    assert c3301.r2i("ᚢ") == 1


def test_r2v() -> None:
    assert c3301.r2v("ᚢ") == 3


def test_v2r() -> None:
    assert c3301.v2r(3) == "ᚢ"


def test_v2i() -> None:
    assert c3301.v2i(3) == 1


def test_low_doublet_null_preserves_length_and_alphabet() -> None:
    data = [i % 7 for i in range(200)]
    out = c3301.low_doublet_null()(data, random.Random(0))
    assert len(out) == len(data)
    assert all(0 <= r < len(c3301.CICADA_ALPHABET) for r in out)


def test_low_doublet_null_preserves_frequencies_exactly() -> None:
    data = [i % 7 for i in range(200)]
    out = c3301.low_doublet_null()(data, random.Random(0))
    assert Counter(out) == Counter(data)


def test_low_doublet_null_matches_observed_doublet_rate() -> None:
    # Data with a low but nonzero doublet rate, like the Liber Primus.
    rng = random.Random(0)
    data: list[int] = []
    while len(data) < 3000:
        r = rng.randrange(12)
        if data and r == data[-1] and rng.random() < 0.85:
            continue  # suppress most doublets
        data.append(r)
    observed = c3301._observed_doublet_rate(data)
    out = c3301.low_doublet_null()(data, random.Random(1))
    rate = sum(1 for a, b in zip(out, out[1:]) if a == b) / (len(out) - 1)
    assert 0.0 < observed < 0.03  # genuinely low but nonzero
    assert abs(rate - observed) < 0.01


def test_low_doublet_null_is_reproducible() -> None:
    data = [i % 5 for i in range(100)]
    model = c3301.low_doublet_null()
    assert model(data, random.Random(4)) == model(data, random.Random(4))


def test_randomrunes_with_low_doublets_removed() -> None:
    assert not hasattr(c3301, "randomrunes_with_low_doublets")


def test_dot_count_reads_the_circled_numerals() -> None:
    assert c3301.dot_count("①") == 1
    assert c3301.dot_count("③") == 3
    assert c3301.dot_count("④") == 4
    assert c3301.dot_count("⑩") == 10
    assert c3301.dot_count("⑬") == 13
    assert c3301.dot_count("⑳") == 20
    assert c3301.dot_count("㉑") == 21
    assert c3301.dot_count("㉓") == 23
    assert c3301.dot_count("㉟") == 35


def test_dot_count_refuses_the_legacy_marks() -> None:
    """The legacy encoding never recorded a count, so none can be returned."""
    for mark in "-.":
        with pytest.raises(AldegondeKeyError):
            c3301.dot_count(mark)


def test_cluster_marks_are_what_the_transcription_wrote_as_a_dot() -> None:
    """'.' collapsed every mark of four dots or more; '-' the one- and three-dot."""
    assert (
        frozenset("④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳㉑㉒㉓㉔㉕㉖㉗㉘㉙㉚㉛㉜㉝㉞㉟.")
        == c3301.CLUSTER_MARKS
    )
    assert frozenset("①②③-") == c3301.WORD_MARKS
    assert c3301.CLUSTER_MARKS | c3301.WORD_MARKS == c3301.MARKS
    assert not c3301.CLUSTER_MARKS & c3301.WORD_MARKS


def test_every_mark_in_the_corpus_is_classified() -> None:
    text = (Path(__file__).resolve().parents[2] / "data" / "page0-58.txt").read_text()
    for char in set(text) & c3301.MARKS:
        assert (char in c3301.CLUSTER_MARKS) != (char in c3301.WORD_MARKS)


def test_mark_chars_is_the_mark_set_as_a_string() -> None:
    """Scripts compose boundary sets as strings; this keeps them one source."""
    assert set(c3301.MARK_CHARS) == c3301.MARKS
    assert len(c3301.MARK_CHARS) == len(c3301.MARKS)


def test_numeral_chars_is_the_numeral_set_as_a_string() -> None:
    assert set(c3301.NUMERAL_CHARS) == c3301.NUMERALS
    assert c3301.NUMERAL_CHARS == "0123456789"


def test_word_boundary_is_marks_structure_numerals_and_quotes() -> None:
    """A script composing its own boundary set must be able to match this."""
    assert (
        frozenset(c3301.MARK_CHARS + "%&$" + c3301.NUMERAL_CHARS + c3301.QUOTE_CHARS)
        == c3301.WORD_BOUNDARY
    )


def test_randomrunes_accepts_an_injected_source() -> None:
    """A seeded source makes the draw reproducible."""
    a = c3301.randomrunes(40, rng=random.Random(9))
    b = c3301.randomrunes(40, rng=random.Random(9))
    c = c3301.randomrunes(40, rng=random.Random(10))
    assert a == b
    assert a != c


def _split(text: str) -> list[str]:
    """Words of a rune text under the library's boundary rule."""
    out: list[str] = []
    cur = ""
    for char in text:
        if char in c3301.RUNE_SET:
            cur += char
        elif char in c3301.WORD_BOUNDARY and cur:
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def test_a_quote_ends_a_word() -> None:
    """A quotation mark opens or closes speech, so it bounds the word."""
    assert _split('ᚠᚢ"ᚦᚩ') == ["ᚠᚢ", "ᚦᚩ"]


def test_an_apostrophe_does_not_end_a_word() -> None:
    """A contraction is one word: the apostrophe sits inside it."""
    assert _split("ᚠᚢ'ᚦᚩ") == ["ᚠᚢᚦᚩ"]


def test_rune_conversions_say_what_was_wrong() -> None:
    """A bare ValueError names neither the value nor the expectation."""
    for call in (
        lambda: c3301.r2i("Z"),
        lambda: c3301.r2v("Z"),
        lambda: c3301.v2r(4),
        lambda: c3301.v2i(4),
    ):
        with pytest.raises(AldegondeKeyError, match="Z|4"):
            call()


def test_unknown_tabula_recta_type_is_rejected_by_name() -> None:
    with pytest.raises(AlphabetError, match="nonsense"):
        c3301.valueTR("nonsense")


def test_runes_codec_agrees_with_the_rune_index() -> None:
    assert len(c3301.RUNES) == 29
    assert c3301.RUNES.encode("ᚢᛠᛝ") == [1, 28, 21]
    assert c3301.RUNES.decode([1, 28, 21]) == ["ᚢ", "ᛠ", "ᛝ"]
    for rune in c3301.CICADA_ALPHABET:
        assert c3301.RUNES.index(rune) == c3301.r2i(rune)


def test_runes_codec_rejects_a_mark() -> None:
    with pytest.raises(AlphabetError, match="not in the alphabet"):
        c3301.RUNES.encode("ᚢ①ᛠ")


def _labels(indices: list[int]) -> str:
    return "-".join(c3301.CICADA_ENGLISH_ALPHABET[i] for i in indices)


# English words and the runes the solved pages of the Liber Primus write them with.
BOOK_SPELLINGS = [
    ("THINGS", "TH-NG-S"),
    ("NOTHING", "N-O-TH-NG"),
    ("ANYTHING", "A-N-Y-TH-NG"),
    ("BEING", "B-E-NG"),
    ("GOING", "G-O-NG"),
    ("DURING", "D-U-R-NG"),
    ("GETTING", "G-E-T-T-NG"),
    ("WARNING", "W-A-R-N-NG"),
    ("FOLLOWING", "F-O-L-L-O-W-NG"),
    ("CONSUMING", "C-O-N-S-U-M-NG"),
    ("INHABITING", "I-N-H-A-B-I-T-NG"),
    ("PRESERVING", "P-R-E-S-E-R-U-NG"),
    ("BELONG", "B-E-L-O-NG"),
    ("STRONG", "S-T-R-O-NG"),
    ("CHANGE", "C-H-A-NG-E"),
    ("INSTRUCTION", "I-N-S-T-R-U-C-T-IA-N"),
    ("PRESERVATION", "P-R-E-S-E-R-U-A-T-IA-N"),
    ("ILLUSIONS", "I-L-L-U-S-IA-N-S"),
    ("BEHAVIORS", "B-E-H-A-U-IA-R-S"),
    ("CONSCIOUSNESS", "C-O-N-S-C-IA-U-S-N-E-S-S"),
    ("AETHEREAL", "AE-TH-E-R-EA-L"),
    ("QUESTION", "C-W-E-S-T-IA-N"),
    ("KNOWLEDGE", "C-N-O-W-L-E-D-G-E"),
    ("BOOK", "B-O-O-C"),
    ("LUCK", "L-U-C-C"),
    ("WEAK", "W-EA-C"),
    ("THINK", "TH-I-N-C"),
    ("VOICE", "U-O-I-C-E"),
    ("CIRCUMFERENCE", "C-I-R-C-U-M-F-E-R-E-N-C-E"),
    ("EXPERIENCE", "E-X-P-E-R-I-E-N-C-E"),
    ("JOURNEY", "J-O-U-R-N-E-Y"),
]


@pytest.mark.parametrize(("english", "runes"), BOOK_SPELLINGS)
def test_encode_english_spells_as_the_book_does(english: str, runes: str) -> None:
    assert _labels(c3301.encode_english(english)) == runes


@pytest.mark.parametrize("index", range(29))
def test_encode_english_reads_every_rune_label_as_that_rune(index: int) -> None:
    assert c3301.encode_english(c3301.CICADA_ENGLISH_ALPHABET[index]) == [index]


def test_encode_english_ignores_case() -> None:
    assert c3301.encode_english("Things") == c3301.encode_english("THINGS")


def test_encode_english_gives_letters_without_a_rune_their_nearest() -> None:
    assert _labels(c3301.encode_english("ZOO")) == "S-O-O"
    assert _labels(c3301.encode_english("IRAQ")) == "I-R-A-C"


def test_encode_english_skips_what_is_not_a_letter() -> None:
    assert _labels(c3301.encode_english("DON'T, 3 OF")) == "D-O-N-T-O-F"


def test_encode_english_forms_no_rune_across_a_gap() -> None:
    assert _labels(c3301.encode_english("AT HOME")) == "A-T-H-O-M-E"


def test_decode_english_joins_the_rune_labels() -> None:
    assert c3301.decode_english([2, 21, 15]) == "THNGS"
    assert c3301.decode_english([]) == ""


def test_decode_english_rejects_an_index_outside_the_alphabet() -> None:
    with pytest.raises(AlphabetError, match="outside the alphabet"):
        c3301.decode_english([0, 29])
