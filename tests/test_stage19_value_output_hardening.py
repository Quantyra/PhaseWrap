from __future__ import annotations

import json

import numpy as np

from qrope.stage14_attention_readout import make_stage14_examples, split_examples
from qrope.stage19_value_output_hardening import (
    evaluate_hardened_value_output,
    run_stage19_benchmark,
    train_hardened_value_output,
    write_stage19_outputs,
)


def test_train_hardened_value_output_smoke() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1)
    splits = split_examples(rows)
    training = train_hardened_value_output(
        splits["train"],
        config_name="test_adam_embed8",
        embed_dim=8,
        epochs=4,
        learning_rate=0.02,
    )
    params = {key: np.array(value, dtype=float) for key, value in training["params"].items()}
    metrics = evaluate_hardened_value_output(splits["test"], params, config_name="test_adam_embed8", split_name="test")
    assert training["optimizer"] == "full_batch_adam"
    assert len(training["training_history"]) == 4
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0


def test_run_stage19_benchmark_is_complete() -> None:
    result = run_stage19_benchmark(
        seeds=(401,),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        configs=({"config_name": "test_adam_embed8", "embed_dim": 8, "epochs": 4, "learning_rate": 0.02, "l2": 0.0},),
    )
    assert result["stage"] == "stage19_value_output_hardening"
    assert result["no_hardware_submission"] is True
    assert result["attention_mode"] == "teacher_forced_target_attention"
    assert {row["split"] for row in result["table"]} == {"train", "validation", "test"}
    assert result["best_config_by_test_top1_mrr"] == "test_adam_embed8"
    assert "a claim that PhaseWrap is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage19_outputs_are_written_without_params(tmp_path) -> None:
    result = run_stage19_benchmark(
        seeds=(401,),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        configs=({"config_name": "test_adam_embed8", "embed_dim": 8, "epochs": 4, "learning_rate": 0.02, "l2": 0.0},),
    )
    paths = write_stage19_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv"}
    assert manifest["stage"] == "stage19_value_output_hardening"
    assert saved["table"] == result["table"]
    assert "params" not in saved["training_records"][0]
