from __future__ import annotations

import json

import numpy as np

from qrope.stage9_trained_transformer_ablation import (
    METHOD_NAMES,
    evaluate_positional_attention,
    make_stage9_splits,
    positional_features,
    run_stage9_ablation,
    train_positional_attention,
    write_stage9_outputs,
)


def test_stage9_splits_are_deterministic_and_extrapolate() -> None:
    first = make_stage9_splits(seeds=(211,), examples_per_length=2)
    second = make_stage9_splits(seeds=(211,), examples_per_length=2)
    assert first == second
    assert sorted({row.sequence_length for row in first["train"]}) == [64, 128]
    assert sorted({row.sequence_length for row in first["test"]}) == [256, 512]
    for row in first["test"]:
        assert row.target_pos < row.query_pos
        assert row.query_pos - row.target_pos == row.target_delta


def test_stage9_positional_features_have_expected_shapes() -> None:
    row = make_stage9_splits(seeds=(211,), examples_per_length=1)["train"][0]
    dimensions = {method: positional_features(row, method).shape for method in METHOD_NAMES}
    assert dimensions["no_position"] == (row.query_pos, 1)
    assert dimensions["phasewrap_bias"] == (row.query_pos, 1)
    assert dimensions["phasewrap_adapter"][0] == row.query_pos
    assert dimensions["phasewrap_adapter"][1] > dimensions["phasewrap_bias"][1]
    assert dimensions["rope_relative"][1] > 1


def test_stage9_training_and_evaluation_are_deterministic() -> None:
    splits = make_stage9_splits(seeds=(211,), examples_per_length=2)
    first = train_positional_attention(splits["train"], "phasewrap_adapter", epochs=12)
    second = train_positional_attention(splits["train"], "phasewrap_adapter", epochs=12)
    assert first == second
    metrics = evaluate_positional_attention(splits["validation"], "phasewrap_adapter", np.array(first["weights"], dtype=float))
    assert metrics["row_count"] == len(splits["validation"])
    assert metrics["loss"] > 0.0
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert 0.0 <= metrics["mrr"] <= 1.0


def test_stage9_ablation_reports_all_methods_and_failed_runs() -> None:
    result = run_stage9_ablation(seeds=(211, 223), examples_per_length=2, epochs=12)
    assert result["stage"] == "stage9_trained_transformer_ablation"
    assert result["no_hardware_submission"] is True
    assert result["failed_runs"] == []
    assert [row["method"] for row in result["aggregate_table"]] == list(METHOD_NAMES)
    assert len(result["per_seed_table"]) == len(METHOD_NAMES) * 2
    assert result["best_method_by_mrr"] in METHOD_NAMES


def test_stage9_outputs_are_written(tmp_path) -> None:
    result = run_stage9_ablation(seeds=(211,), examples_per_length=1, epochs=8)
    paths = write_stage9_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    failed = json.loads((tmp_path / "failed_runs.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_seed_csv", "failed_runs"}
    assert manifest["stage"] == "stage9_trained_transformer_ablation"
    assert saved["aggregate_table"] == result["aggregate_table"]
    assert failed == []
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "per_seed_results.csv").exists()
