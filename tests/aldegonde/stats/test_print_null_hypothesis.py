import pytest

from aldegonde.analysis.kasiski import print_kasiski_statistics
from aldegonde.stats import (
    print_ioc_statistics,
    print_isomorph_statistics,
    print_kappa,
    print_mioc_statistics,
    print_repeat_statistics,
    shuffle,
)

TEXT = "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOG" * 4


def test_print_ioc_states_null(capsys: pytest.CaptureFixture[str]) -> None:
    print_ioc_statistics(TEXT, alphabetsize=26)
    assert "null hypothesis:" in capsys.readouterr().out


def test_print_ioc_with_injected_null_keeps_grid_and_label(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_ioc_statistics(
        TEXT, alphabetsize=26, null=shuffle, null_label="shuffle null", trials=20
    )
    out = capsys.readouterr().out
    assert "null hypothesis: shuffle null" in out
    assert "ΔIC2 (cut=0)" in out
    assert "ΔIC3 (cut=2)" in out
    assert "z=" in out


def test_print_repeats_with_injected_null_keeps_format_and_label(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_repeat_statistics(
        TEXT, minimum=2, maximum=4, null=shuffle, null_label="shuffle null", trials=20
    )
    out = capsys.readouterr().out
    assert "null hypothesis: shuffle null" in out
    assert "repeats length 2:" in out
    assert "z=" in out


def test_print_mioc_states_null(capsys: pytest.CaptureFixture[str]) -> None:
    print_mioc_statistics(TEXT, TEXT, alphabetsize=26)
    assert "null hypothesis:" in capsys.readouterr().out


def test_print_kappa_states_null(capsys: pytest.CaptureFixture[str]) -> None:
    print_kappa(TEXT, alphabetsize=26, maximum=10)
    assert "null hypothesis:" in capsys.readouterr().out


def test_print_kappa_with_injected_null_keeps_format_and_label(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_kappa(
        TEXT, alphabetsize=26, maximum=6, null=shuffle, null_label="shuffle null", trials=20
    )
    out = capsys.readouterr().out
    assert "null hypothesis: shuffle null" in out
    assert "kappa(mono): skip=1" in out
    assert "z=" in out


def test_print_kasiski_with_injected_null_keeps_format_and_label(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_kasiski_statistics(
        TEXT,
        min_length=3,
        max_length=4,
        max_period=6,
        null=shuffle,
        null_label="shuffle null",
        trials=20,
    )
    out = capsys.readouterr().out
    assert "null hypothesis: shuffle null" in out
    assert "period=2" in out
    assert "z=" in out


def test_print_kasiski_states_null(capsys: pytest.CaptureFixture[str]) -> None:
    print_kasiski_statistics(TEXT, min_length=3, max_length=4, max_period=10)
    assert "null hypothesis:" in capsys.readouterr().out


def test_print_repeats_states_null(capsys: pytest.CaptureFixture[str]) -> None:
    print_repeat_statistics(TEXT, minimum=2, maximum=4)
    assert "null hypothesis:" in capsys.readouterr().out


def test_print_isomorph_states_null(capsys: pytest.CaptureFixture[str]) -> None:
    print_isomorph_statistics(TEXT)
    assert "null hypothesis:" in capsys.readouterr().out
