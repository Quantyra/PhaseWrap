from __future__ import annotations

import json

from qrope.stage11_phasewrap_theory import (
    DEFAULT_PERIOD_PAIR,
    alias_classes_for_context,
    fourier_support,
    invariance_checks,
    lcm,
    period_pair_summary,
    phasewrap_score,
    residue_score_table,
    run_phasewrap_theory_analysis,
    write_stage11_outputs,
)


def test_lcm_and_default_period_are_expected() -> None:
    assert lcm(8, 12) == 24
    assert lcm(*DEFAULT_PERIOD_PAIR) == 24


def test_phasewrap_score_is_periodic_and_mirrored() -> None:
    base = phasewrap_score(7, 19)
    assert phasewrap_score(7 + 24, 19) == base
    assert phasewrap_score(7, 19 + 24) == base
    assert phasewrap_score(7, 19) == phasewrap_score(19, 7)


def test_residue_score_table_has_mod24_rows() -> None:
    rows = residue_score_table()
    assert len(rows) == 24
    assert rows[0]["difference_mod_lcm"] == 0
    assert rows[-1]["difference_mod_lcm"] == 23


def test_alias_classes_grow_with_context() -> None:
    short = alias_classes_for_context(24)
    long = alias_classes_for_context(240)
    assert len(short) == len(long)
    assert max(row["alias_count"] for row in long) > max(row["alias_count"] for row in short)


def test_period_pair_summary_includes_default_pair() -> None:
    rows = period_pair_summary(context_length=128)
    default = next(row for row in rows if row["period_pair"] == [8, 12])
    assert default["fundamental_period"] == 24
    assert default["context_length"] == 128
    assert default["unique_score_count"] > 0


def test_fourier_support_is_small_and_classical() -> None:
    support = fourier_support()
    assert support["fundamental_period"] == 24
    assert support["positive_frequency_support"] == [1, 2, 3, 5]
    assert "classical" in support["interpretation"]


def test_invariance_checks_pass() -> None:
    checks = invariance_checks()
    assert checks["translation_invariance_holds"] is True
    assert checks["lcm_shift_invariance_holds"] is True
    assert checks["mirror_symmetry_holds"] is True


def test_stage11_analysis_and_outputs_are_deterministic(tmp_path) -> None:
    first = run_phasewrap_theory_analysis(context_lengths=(24, 48, 96))
    second = run_phasewrap_theory_analysis(context_lengths=(24, 48, 96))
    assert first == second
    paths = write_stage11_outputs(first, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {
        "manifest",
        "results",
        "alias_summary_csv",
        "period_pair_summary_csv",
        "residue_score_table_csv",
    }
    assert manifest["stage"] == "stage11_phasewrap_theory"
    assert saved["fundamental_period"] == 24
    assert (tmp_path / "alias_summary.csv").exists()
    assert (tmp_path / "period_pair_summary.csv").exists()
    assert (tmp_path / "residue_score_table.csv").exists()
