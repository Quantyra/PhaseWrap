from __future__ import annotations

import json

import numpy as np

from qrope.stage14_attention_readout import make_stage14_examples, split_examples
from qrope.stage17_small_decoder_value_model import (
    METHOD_NAMES,
    evaluate_value_model,
    run_stage17_benchmark,
    train_value_model,
    write_stage17_outputs,
)


def test_train_and_evaluate_value_model_smoke() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1)
    splits = split_examples(rows)
    training = train_value_model(splits["train"], "phasewrap_distance_adapter", epochs=4)
    params = {key: np.array(value, dtype=float) for key, value in training["params"].items()}
    metrics = evaluate_value_model(splits["test"], "phasewrap_distance_adapter", params)
    assert len(training["training_history"]) == 4
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert metrics["mrr_ci_low"] <= metrics["mrr"] <= metrics["mrr_ci_high"]


def test_run_stage17_benchmark_is_complete() -> None:
    result = run_stage17_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    assert result["stage"] == "stage17_small_decoder_value_model"
    assert result["no_hardware_submission"] is True
    assert [row["method"] for row in result["table"]] == list(METHOD_NAMES)
    assert result["best_method_by_top1_mrr"] in METHOD_NAMES
    assert result["model"]["type"] == "single_attention_readout_with_learned_value_embeddings_and_output_projection"
    assert "a claim that PhaseWrap is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage17_outputs_are_written(tmp_path) -> None:
    result = run_stage17_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    paths = write_stage17_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "task_summary_csv"}
    assert manifest["stage"] == "stage17_small_decoder_value_model"
    assert saved["table"] == result["table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "task_summary.csv").exists()
