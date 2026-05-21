from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage52_two_block_decoder_feasibility_audit import (
    TASK_NAMES,
    build_blocked_result,
    run_stage52_audit,
    write_stage52_outputs,
)


def test_stage52_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage52_two_block_decoder_feasibility_audit"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage52_smoke_reports_two_block_decision() -> None:
    result = run_stage52_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("rope_relative", "phasewrap_bias", "no_position"),
    )
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == 3 * len(TASK_NAMES)
    assert result["decision"]["decision"] in {
        "TWO_BLOCK_CAPACITY_NOT_ESTABLISHED",
        "TWO_BLOCK_RETRIEVAL_GENERALIZATION_PRESENT_REVIEW_REQUIRED",
        "TWO_BLOCK_TRAIN_FIT_WITHOUT_RETRIEVAL_GENERALIZATION",
    }
    assert "capacity_established" in result["decision"]
    assert "learned_position_scale_mean" in result["aggregate_table"][0]


def test_stage52_outputs_are_written(tmp_path) -> None:
    result = run_stage52_audit(seeds=(307,), examples_per_length=1, epochs=2, method_names=METHOD_NAMES[:2])
    paths = write_stage52_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage52_two_block_decoder_feasibility_audit"
    assert manifest["decision"] == result["decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "per_run_results.csv").exists()
