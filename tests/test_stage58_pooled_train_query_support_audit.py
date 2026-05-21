from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage58_pooled_train_query_support_audit import TASK_NAMES, build_blocked_result, run_stage58_audit, write_stage58_outputs


def test_stage58_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage58_pooled_train_query_support_audit"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that a pooled lookup map is a matched decoder-only transformer" in result["claim_boundary"]["excluded"]


def test_stage58_smoke_reports_pooled_support_decision() -> None:
    result = run_stage58_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=("rope_relative", "phasewrap_bias", "no_position"),
        position_scales=(0.0, 1.0),
        cue_scales=(0.0, 4.0),
        distance_scales=(0.0, 4.0),
    )
    assert result["status"] == "completed"
    assert result["stage"] == "stage58_pooled_train_query_support_audit"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == 3 * len(TASK_NAMES)
    assert result["decision"]["decision"] in {
        "POOLED_TRAIN_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION",
        "POOLED_TRAIN_QUERY_SUPPORT_PARTIAL_RETRIEVAL",
        "POOLED_TRAIN_QUERY_SUPPORT_RETRIEVAL_FAILED",
    }


def test_stage58_outputs_are_written(tmp_path) -> None:
    result = run_stage58_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=METHOD_NAMES[:2],
        position_scales=(0.0, 1.0),
        cue_scales=(0.0, 4.0),
        distance_scales=(0.0, 4.0),
    )
    paths = write_stage58_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage58_pooled_train_query_support_audit"
    assert manifest["decision"] == result["decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
