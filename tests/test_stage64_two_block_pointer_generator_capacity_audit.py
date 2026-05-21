from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage64_two_block_pointer_generator_capacity_audit import build_blocked_result, run_stage64_audit, write_stage64_outputs


def test_stage64_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage64_two_block_pointer_generator_capacity_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that learned pointer-generation is equivalent to full decoder-only language-model validation" in result["claim_boundary"]["excluded"]


def test_stage64_smoke_reports_pointer_generator_decision_or_blocked() -> None:
    result = run_stage64_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position", "rope_relative"),
    )
    assert result["stage"] == "stage64_two_block_pointer_generator_capacity_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["support_coverage"]["307"]["test_known_fraction"] == 1.0
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "TWO_BLOCK_POINTER_GENERATOR_CAPACITY_NOT_ESTABLISHED",
        "TWO_BLOCK_POINTER_GENERATOR_RETRIEVAL_REVIEW_REQUIRED",
        "TWO_BLOCK_POINTER_GENERATOR_CAPACITY_WITHOUT_RETRIEVAL_GENERALIZATION",
    }


def test_stage64_outputs_are_written(tmp_path) -> None:
    result = run_stage64_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage64_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage64_two_block_pointer_generator_capacity_audit"
    assert saved["stage"] == "stage64_two_block_pointer_generator_capacity_audit"
