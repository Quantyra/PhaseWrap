from __future__ import annotations

import json

from qrope.stage81_soft_support_routed_token_selector_audit import run_stage81_audit, write_stage81_outputs


def test_stage81_smoke_reports_soft_support_routed_decision() -> None:
    result = run_stage81_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position", "rope_relative"),
        epochs=20,
        learning_rate=0.05,
        support_aux_weight=1.0,
    )
    assert result["stage"] == "stage81_soft_support_routed_token_selector_audit"
    assert result["source_stage"] == "stage80_support_routed_token_selector_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "SOFT_SUPPORT_ROUTED_TOKEN_SELECTOR_SOLVES_PHASE_CUED_NOT_PROMOTION",
        "SOFT_SUPPORT_ROUTED_TOKEN_SELECTOR_PHASE_CUED_REVIEW_REQUIRED",
        "SOFT_SUPPORT_ROUTED_TOKEN_SELECTOR_SUPPORT_RECOVERED_RETRIEVAL_FAILED",
        "SOFT_SUPPORT_ROUTED_TOKEN_SELECTOR_SUPPORT_NOT_RECOVERED",
    }


def test_stage81_records_soft_routing_policy() -> None:
    result = run_stage81_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
    )
    if result["status"] == "blocked":
        return
    assert result["support_coverage"]["307"]["exact_query_support_fraction"] == 1.0
    assert result["model"]["type"] == "same_seed_support_complete_soft_support_routed_token_selector"
    assert "learned support probabilities routed to farthest congruent token selection" in result["model"]["value_output_mode"]
    assert "hard support argmax" in result["model"]["metadata_excluded"]
    assert "row.target_delta" in result["model"]["metadata_excluded"]


def test_stage81_outputs_are_written(tmp_path) -> None:
    result = run_stage81_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
    )
    paths = write_stage81_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage81_soft_support_routed_token_selector_audit"
    assert saved["stage"] == "stage81_soft_support_routed_token_selector_audit"
    assert (tmp_path / "summary.csv").exists()
