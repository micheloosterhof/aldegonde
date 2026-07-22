# Review: `claude/bonferroni-correction-2vecyd`

Generalizes null-hypothesis comparison across cryptodiagnostics and adds
Bonferroni family-wise correction.

Commits:
- `607be1e` Generalize null-hypothesis comparison across cryptodiagnostics
- `199afff` Harden the null-comparison API after review

## Verification

- Full test suite: 298 passed (64 in the directly-affected files)
- `ruff check` on all 7 changed source files: clean
- `mypy` on the whole `stats/` package: clean except one pre-existing
  `validation.py:87` unreachable-statement error this branch never touches
  (confirmed: no commits or diff against that file)

Environment note: the `.direnv` venv had a broken scipy (linked against a
garbage-collected `openblas-0.3.32` nix store path). The pinned scipy 1.15.3
has no Python 3.14 wheel and will not build from source (no Fortran), so tests
were run against scipy 1.18.0 / numpy 2.5.1. That is a local env change only,
unrelated to the branch, but the version pins in `pyproject.toml` are
unbuildable on Python 3.14 and warrant a separate look.

## What the branch does

Consolidates the duplicated "is this statistic surprising under a null?" logic
that was copy-pasted across `kappa`, `repeats`, `kasiski`, and `isomorph` into
one `stats/diagnostics.py` module, and adds Bonferroni family-wise correction
for scans over skips/periods/positions.

## Assessment

Solid, well-tested, well-documented refactor. Recommend merge.

- **Clean abstraction.** `compare_to_null` / `compare_map_to_null` dispatch
  between an analytic closed-form null and a Monte Carlo resampler, both
  returning the same `NullComparison`, so reporting code stops caring how the
  null was evaluated. The "resampler wins when both are given" rule is
  consistent and documented in every relevant docstring.
- **The Poisson fix is the real substance.** `poisson_null` uses scipy's exact
  tails (`sf(k-1)` = P(X>=k)) instead of a normal approximation. At small mu
  the normal tail understates rare-event probability by orders of magnitude and
  would flag chance doublets as significant.
- **`bonferroni` is careful.** Validates every p-value in [0, 1] and rejects
  NaN. A test proves the degenerate single-symbol chi-square (which scipy
  returns as NaN) raises rather than silently reporting "nothing significant."
- **`uniform` null rejects duplicate alphabet symbols** — correct, since
  `random.choices` would silently over-draw a repeated symbol and make the null
  non-uniform. Tested.
- **Performance-conscious.** `observed_values` threading through
  `monte_carlo_map` avoids re-running expensive statistics (isomorph
  distributions, the quadratic kasiski distance pass) on the observed sequence
  a second time.
- **Thorough test coverage** — exact-tail values, degenerate/zero-mu
  directionality, precomputed-observed short-circuit, determinism,
  empty-sequence graceful degradation.

## Minor observations (not blockers)

- `family_comparison` / `position_frequency_family` are library API only — not
  wired into any `print_*` output yet.
- The header line still says `z = standard deviations from this null` on the
  analytic Poisson path, where the p-value is the authoritative output rather
  than z. Harmless (z is still printed per row), but slightly undersells the
  exact-tail improvement.

## Usage by `lp.py`

The framework reaches `lp.py` transitively, and only in part.

Every diagnostic `lp.py` prints goes through `print_*` functions this branch
rewired onto `diagnostics.compare_map_to_null`:

- `print_kappa` (lp.py:136-151) -> `compare_map_to_null` + `poisson_null`
- `repeats.print_repeat_statistics` (lp.py:179-186) -> same
- `kasiski.print_kasiski_statistics` (lp.py:162) -> same
- `print_isomorph_statistics` is commented out (lp.py:188), so not exercised

So `lp.py` output already benefits from the exact-Poisson-tail fix with no
change to `lp.py`. The injected-null API it uses (`null=c3301.low_doublet_null()`)
predates this branch.

`lp.py` does not call the new public surface directly: `compare_to_null`,
`compare_map_to_null`, `bonferroni`, `family_comparison`,
`position_frequency_family`, `poisson_null`, `normal_null`, `uniform`.

Notable gap: for family-wise correction of the strongest period, `lp.py:155`
uses `family_pvalue` — the older resample / max-statistic Monte Carlo path — not
the new `bonferroni`-based `family_comparison` this branch adds. The Bonferroni
half of the branch, the thing it is named after, is currently unused by
`lp.py`. That is defensible (max-statistic resampling is the stronger method
when keys are correlated, as adjacent skips are), but if the intent was for
`lp.py` to adopt Bonferroni, it has not happened.
