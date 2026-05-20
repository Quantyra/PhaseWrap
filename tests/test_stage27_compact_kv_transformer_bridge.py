from __future__ import annotations

import json

from qrope.stage27_compact_kv_transformer_bridge import (
    evaluate_attention_bridge,
    run_stage27_benchmark,
    train_attention_bridge,
    write_stage27_outputs,
)
from qrope.stage26_compact_kv_qa import make_stage26_examples, split_examples


def test_stage27_training_is_deterministic() -> None:
    rows = split_examples(
        make_stage26_examples(seeds=(2601,), context_lengths=(256, 512, 1024, 2048), examples_per_length=1)
    )["train"]
    first = train_attention_bridge(rows, "alibi", model_seed=2701, epochs=3)
    second = train_attention_bridge(rows, "alibi", model_seed=2701, epochs=3)
    assert first["training_history"] == second["training_history"]
    assert first["params"] == second["params"]


def test_stage27_evaluation_reports_required_metrics() -> None:
    splits = split_examples(
        make_stage26_examples(seeds=(2601,), context_lengths=(256, 512, 1024, 2048), examples_per_length=1)
    )
    training = train_attention_bridge(splits["train"], "phasewrap_residual_adapter", model_seed=2701, epochs=3)
    metrics = evaluate_attention_bridge(
        splits["test"],
        "phasewrap_residual_adapter",
        {key: __import__("numpy").array(value, dtype=float) for key, value in training["params"].items()},
    )
    assert metrics["row_count"] == 1
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert 0.0 < metrics["mrr"] <= 1.0
    assert 0.0 < metrics["mean_target_probability"] <= 1.0


def test_stage27_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage27_benchmark(
        data_seeds=(2601,),
        model_seeds=(2701, 2711),
        context_lengths=(256, 512, 1024, 2048),
        examples_per_length=1,
        epochs=3,
        method_names=("alibi", "phasewrap_residual_adapter"),
    )
    assert result["stage"] == "stage27_compact_kv_transformer_bridge"
    assert result["train_row_count"] == 2
    assert result["test_row_count"] == 1
    assert len(result["run_table"]) == 4
    assert len(result["table"]) == 2
    assert result["best_method_by_test_top1_mrr"] in {"alibi", "phasewrap_residual_adapter"}
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage27_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_run_csv", "weak_runs"}
    assert manifest["stage"] == "stage27_compact_kv_transformer_bridge"
    assert saved["table"] == result["table"]
