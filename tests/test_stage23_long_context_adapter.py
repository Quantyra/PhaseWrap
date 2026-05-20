from __future__ import annotations

import json

from qrope.stage23_long_context_adapter import run_stage23_benchmark, split_long_context_examples, write_stage23_outputs
from qrope.stage12_ruler_retrieval import make_stage12_examples


def test_split_long_context_examples() -> None:
    rows = make_stage12_examples(seeds=(401,), context_lengths=(512, 1024, 2048, 4096), examples_per_task_length=1)
    splits = split_long_context_examples(rows)
    assert len(splits["train"]) == 6
    assert len(splits["validation"]) == 3
    assert len(splits["test"]) == 3


def test_run_stage23_benchmark_is_complete() -> None:
    result = run_stage23_benchmark(
        seeds=(401,),
        context_lengths=(512, 1024, 2048, 4096),
        examples_per_task_length=1,
        epochs=4,
        method_names=("rope_relative", "phasewrap_distance_adapter"),
    )
    assert result["stage"] == "stage23_long_context_adapter"
    assert result["source_stage"] == "stage22_long_context_retrieval"
    assert result["train_row_count"] == 6
    assert result["validation_row_count"] == 3
    assert result["test_row_count"] == 3
    assert {row["split"] for row in result["table"]} == {"train", "validation", "test"}
    assert result["best_method_by_test_top1_mrr"] in {"rope_relative", "phasewrap_distance_adapter"}
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage23_outputs_are_written(tmp_path) -> None:
    result = run_stage23_benchmark(
        seeds=(401,),
        context_lengths=(512, 1024, 2048, 4096),
        examples_per_task_length=1,
        epochs=4,
        method_names=("rope_relative", "phasewrap_distance_adapter"),
    )
    paths = write_stage23_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "task_summary_csv"}
    assert manifest["stage"] == "stage23_long_context_adapter"
    assert saved["table"] == result["table"]
