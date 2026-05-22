from __future__ import annotations

import json

from qrope.stage167_expanded_simulated_seed_stress_audit import (
    run_stage167_expanded_seed_stress_audit,
    write_stage167_outputs,
)


def test_stage167_runs_expanded_simulated_stress_without_hardware() -> None:
    result = run_stage167_expanded_seed_stress_audit(seeds=(314, 577), row_count=8)

    assert result["status"] == "completed"
    assert result["simulated_only"] is True
    assert result["synthetic_rows_only"] is True
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["comparison_group_count"] == 2 * 2 * 9
    assert result["metric_record_count"] == 2 * 2 * 5 * 9
    assert len(result["seed_records"]) == 2


def test_stage167_rejects_non_preregistered_shot_count() -> None:
    try:
        run_stage167_expanded_seed_stress_audit(seeds=(314,), row_count=8, shot_count=1000)
    except ValueError as exc:
        assert "4096-shot" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_stage167_outputs_are_written(tmp_path) -> None:
    result = run_stage167_expanded_seed_stress_audit(seeds=(314,), row_count=8)

    paths = write_stage167_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["synthetic_rows_only"] is True
    assert "stable_strict_target" in summary
