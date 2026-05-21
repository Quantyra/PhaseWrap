from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage71_positional_bias_copy_upper_bound_audit import (
    run_stage71_audit,
    write_stage71_outputs,
)


def test_stage71_smoke_reports_positional_copy_decision() -> None:
    result = run_stage71_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position", "rope_relative", "phasewrap_bias"),
    )
    assert result["stage"] == "stage71_positional_bias_copy_upper_bound_audit"
    assert result["status"] == "completed"
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "POSITIONAL_BIAS_COPY_SOLVES_ORIGINAL_RETRIEVAL_REVIEW_REQUIRED",
        "POSITIONAL_BIAS_COPY_PARTIAL_ORIGINAL_RETRIEVAL_UPPER_BOUND",
        "POSITIONAL_BIAS_COPY_DOES_NOT_SOLVE_ORIGINAL_RETRIEVAL",
    }
    assert set(result["decision"]["retrieval_best_top1"]) == {"phase_cued_retrieval", "exact_offset_passkey"}


def test_stage71_hard_copy_preserves_exact_offset_but_not_phase_cued_upper_bound() -> None:
    result = run_stage71_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position", "rope_relative", "phasewrap_bias"),
    )
    rows = {
        (row["task"], row["method"]): row
        for row in result["aggregate_table"]
    }
    assert rows[("exact_offset_passkey", "rope_relative")]["test_top1_accuracy_mean"] >= 0.5
    assert rows[("phase_cued_retrieval", "phasewrap_bias")]["test_top1_accuracy_mean"] < 0.5
    assert rows[("phase_cued_retrieval", "no_position")]["test_top1_accuracy_mean"] < 0.5


def test_stage71_outputs_are_written(tmp_path) -> None:
    result = run_stage71_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position",),
    )
    paths = write_stage71_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "per_example_csv", "failed_runs"}
    assert manifest["stage"] == "stage71_positional_bias_copy_upper_bound_audit"
    assert saved["method_names"] == ["no_position"]
    assert (tmp_path / "per_example_results.csv").exists()
