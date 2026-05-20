from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

from .stage12_ruler_retrieval import DEFAULT_EXAMPLES_PER_TASK_LENGTH, DEFAULT_SEEDS, TASK_NAMES, Stage12Example, make_stage12_examples
from .stage13_positional_adapter import METHOD_NAMES, evaluate_adapter, train_adapter


STAGE23_SCHEMA_VERSION = "qrope_stage23_long_context_adapter_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage23_long_context_adapter"
DEFAULT_CONTEXT_LENGTHS = (512, 1024, 2048, 4096)
TRAIN_LENGTHS = (512, 1024)
VALIDATION_LENGTHS = (2048,)
TEST_LENGTHS = (4096,)


def split_long_context_examples(rows: list[Stage12Example]) -> dict[str, list[Stage12Example]]:
    return {
        "train": [row for row in rows if row.sequence_length in TRAIN_LENGTHS],
        "validation": [row for row in rows if row.sequence_length in VALIDATION_LENGTHS],
        "test": [row for row in rows if row.sequence_length in TEST_LENGTHS],
    }


def _evaluate_split(rows: list[Stage12Example], method_name: str, weights: np.ndarray, split_name: str) -> dict[str, Any]:
    result = evaluate_adapter(rows, method_name, weights)
    result["method"] = method_name
    result["split"] = split_name
    return result


def run_stage23_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 260,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    examples = make_stage12_examples(seeds=seeds, context_lengths=context_lengths, examples_per_task_length=examples_per_task_length)
    splits = split_long_context_examples(examples)
    table: list[dict[str, Any]] = []
    task_table: list[dict[str, Any]] = []
    training_records: list[dict[str, Any]] = []
    failed_or_weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        training = train_adapter(splits["train"], method_name, epochs=epochs)
        weights = np.array(training["weights"], dtype=float)
        training_records.append(training)
        for split_name in ("train", "validation", "test"):
            split_result = _evaluate_split(splits[split_name], method_name, weights, split_name)
            table.append(split_result)
            if split_name == "test" and float(split_result["top1_accuracy"]) < 0.5:
                failed_or_weak_runs.append(
                    {
                        "method": method_name,
                        "top1_accuracy": split_result["top1_accuracy"],
                        "mrr": split_result["mrr"],
                        "criterion": "test_top1_accuracy_below_0.5",
                    }
                )
        for task_name in TASK_NAMES:
            task_rows = [row for row in splits["test"] if row.task == task_name]
            task_result = _evaluate_split(task_rows, method_name, weights, f"test:{task_name}")
            task_result["task"] = task_name
            task_table.append(task_result)
    test_rows = [row for row in table if row["split"] == "test"]
    selection_table = sorted(
        test_rows,
        key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_probability_mass"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE23_SCHEMA_VERSION,
        "stage": "stage23_long_context_adapter",
        "dataset": "deterministic_long_context_trained_positional_adapter_v1",
        "source_stage": "stage22_long_context_retrieval",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_task_length": examples_per_task_length,
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "method_names": list(method_names),
        "task_names": list(TASK_NAMES),
        "epochs": epochs,
        "failed_or_weak_runs": failed_or_weak_runs,
        "claim_boundary": {
            "supported": [
                "A deterministic train-short/test-long positional-adapter benchmark on explicit long-context retrieval rows.",
                "Evidence about whether trained PhaseWrap-derived adapters improve over the fixed PhaseWrap score through 4096-token test contexts.",
                "Reported weak or failed test rows under a predeclared top-1 threshold.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
                "general cross-backend robustness",
                "a claim that PhaseWrap-RoPE is a validated RoPE replacement",
            ],
        },
        "training_records": training_records,
        "table": table,
        "selection_table": selection_table,
        "task_table": task_table,
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
    }


def write_stage23_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "source_stage": result["source_stage"],
        "no_hardware_submission": result["no_hardware_submission"],
        "train_lengths": result["train_lengths"],
        "validation_lengths": result["validation_lengths"],
        "test_lengths": result["test_lengths"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "method_names": result["method_names"],
        "task_names": result["task_names"],
        "epochs": result["epochs"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "task_summary_csv_path": str((output_dir / "task_summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "task_summary_csv": str(output_dir / "task_summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    with (output_dir / "task_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["task_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["task_table"])
    return paths


def print_stage23_table(result: dict[str, Any]) -> None:
    columns = ("method", "split", "row_count", "top1_accuracy", "mrr", "mean_target_probability_mass", "mean_first_relevant_rank")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["table"]:
        print(" | ".join(str(row[column]) for column in columns))
