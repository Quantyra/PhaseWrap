from __future__ import annotations

import json

from qrope.stage10_small_decoder_transformer import TASK_NAMES
from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage67_content_key_retrieval_audit import CONTENT_KEY_TASK
from qrope.stage68_content_key_auxiliary_transfer_audit import (
    build_blocked_result,
    run_stage68_audit,
    write_stage68_outputs,
)


def test_stage68_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage68_content_key_auxiliary_transfer_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["tasks"] == list(TASK_NAMES)
    assert result["auxiliary_task"] == CONTENT_KEY_TASK


def test_stage68_smoke_reports_auxiliary_transfer_decision_or_blocked() -> None:
    result = run_stage68_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("no_position", "rope_relative"),
    )
    assert result["stage"] == "stage68_content_key_auxiliary_transfer_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["auxiliary_task"] == CONTENT_KEY_TASK
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "CONTENT_KEY_AUXILIARY_TRANSFER_CAPACITY_NOT_ESTABLISHED",
        "CONTENT_KEY_AUXILIARY_TRANSFER_RETRIEVAL_REVIEW_REQUIRED",
        "CONTENT_KEY_AUXILIARY_TRANSFER_PARTIAL_RETRIEVAL",
        "CONTENT_KEY_AUXILIARY_TRANSFER_WITHOUT_RETRIEVAL_GENERALIZATION",
    }
    first_run = result["run_table"][0]
    assert first_run["auxiliary_task"] == CONTENT_KEY_TASK
    assert first_run["train_row_count"] > first_run["base_train_row_count"]
    assert first_run["auxiliary_train_row_count"] > 0


def test_stage68_outputs_are_written(tmp_path) -> None:
    result = run_stage68_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage68_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage68_content_key_auxiliary_transfer_audit"
    assert saved["stage"] == "stage68_content_key_auxiliary_transfer_audit"
