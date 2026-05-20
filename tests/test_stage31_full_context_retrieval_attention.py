from __future__ import annotations

import json

import numpy as np

from qrope.stage12_ruler_retrieval import make_stage12_examples
from qrope.stage13_positional_adapter import split_examples
from qrope.stage31_full_context_retrieval_attention import (
    PARAMETER_COUNT,
    evaluate_full_context_attention,
    full_context_features,
    run_stage31_benchmark,
    train_full_context_attention,
    write_stage31_outputs,
)


def test_stage31_features_cover_full_prefix() -> None:
    row = make_stage12_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=1)[0]
    features = full_context_features(row, "rope_relative")
    assert features.shape == (row.query_pos, PARAMETER_COUNT)
    assert int(np.sum(features[:, 1])) == len(row.key_positions)


def test_stage31_training_is_deterministic() -> None:
    rows = split_examples(make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))["train"]
    first = train_full_context_attention(rows, "rope_relative", model_seed=3101, epochs=3)
    second = train_full_context_attention(rows, "rope_relative", model_seed=3101, epochs=3)
    assert first["training_history"] == second["training_history"]
    assert first["weights_sha256"] == second["weights_sha256"]
    assert first["parameter_count"] == PARAMETER_COUNT


def test_stage31_evaluation_reports_required_metrics() -> None:
    splits = split_examples(make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))
    training = train_full_context_attention(splits["train"], "phasewrap_distance_adapter", model_seed=3101, epochs=3)
    metrics = evaluate_full_context_attention(splits["test"], "phasewrap_distance_adapter", np.array(training["weights"], dtype=float))
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert 0.0 < metrics["mrr"] <= 1.0
    assert 0.0 < metrics["mean_target_probability"] <= 1.0
    assert 0.0 <= metrics["expected_calibration_error"] <= 1.0


def test_stage31_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage31_benchmark(
        data_seeds=(401,),
        model_seeds=(3101, 3119),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=3,
        method_names=("rope_relative", "phasewrap_distance_adapter"),
    )
    assert result["stage"] == "stage31_full_context_retrieval_attention"
    assert result["train_row_count"] == 6
    assert result["test_row_count"] == 3
    assert len(result["run_table"]) == 4
    assert len(result["task_table"]) == 12
    assert result["model"]["parameter_count"] == PARAMETER_COUNT
    assert "expected_calibration_error_mean" in result["table"][0]
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage31_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_run_csv", "task_summary_csv", "weak_runs"}
    assert manifest["stage"] == "stage31_full_context_retrieval_attention"
    assert saved["selection_table"] == result["selection_table"]
