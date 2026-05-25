from __future__ import annotations

import json

import numpy as np

from qrope.stage12_ruler_retrieval import make_stage12_examples
from qrope.stage13_positional_adapter import split_examples
from qrope.stage30_matched_retrieval_bridge import (
    FEATURE_DIM,
    evaluate_matched_bridge,
    matched_positional_features,
    run_stage30_benchmark,
    train_matched_bridge,
    write_stage30_outputs,
)


def test_stage30_features_have_matched_width() -> None:
    row = make_stage12_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=1)[0]
    for method in (
        "no_position",
        "alibi",
        "rope_relative",
        "sinusoidal",
        "phasewrap_bias",
        "phasewrap_residual_adapter",
        "phasewrap_distance_adapter",
    ):
        features = matched_positional_features(row, method)
        assert features.shape == (len(row.key_positions), FEATURE_DIM)


def test_stage30_training_is_deterministic() -> None:
    rows = split_examples(make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))["train"]
    first = train_matched_bridge(rows, "rope_relative", model_seed=3001, epochs=3)
    second = train_matched_bridge(rows, "rope_relative", model_seed=3001, epochs=3)
    assert first["training_history"] == second["training_history"]
    assert first["param_sha256"] == second["param_sha256"]
    assert first["parameter_count"] == second["parameter_count"]


def test_stage30_evaluation_reports_calibration_metrics() -> None:
    splits = split_examples(make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))
    training = train_matched_bridge(splits["train"], "phasewrap_distance_adapter", model_seed=3001, epochs=3)
    metrics = evaluate_matched_bridge(
        splits["test"],
        "phasewrap_distance_adapter",
        {key: np.array(value, dtype=float) for key, value in training["params"].items()},
    )
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert 0.0 < metrics["mrr"] <= 1.0
    assert 0.0 < metrics["mean_target_probability"] <= 1.0
    assert 0.0 <= metrics["expected_calibration_error"] <= 1.0
    assert metrics["target_probability_mae"] == round(1.0 - metrics["mean_target_probability"], 6)


def test_stage30_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage30_benchmark(
        data_seeds=(401,),
        model_seeds=(3001, 3011),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=3,
        method_names=("rope_relative", "phasewrap_distance_adapter"),
    )
    assert result["stage"] == "stage30_matched_retrieval_bridge"
    assert result["train_row_count"] == 6
    assert result["test_row_count"] == 3
    assert len(result["run_table"]) == 4
    assert len(result["task_table"]) == 12
    assert len(result["table"]) == 2
    assert result["model"]["parameter_count"] == result["table"][0]["parameter_count"]
    assert "expected_calibration_error_mean" in result["table"][0]
    assert "a claim that PhaseWrap is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage30_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_run_csv", "task_summary_csv", "weak_runs"}
    assert manifest["stage"] == "stage30_matched_retrieval_bridge"
    assert saved["selection_table"] == result["selection_table"]
