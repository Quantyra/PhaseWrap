from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import (
    TASK_NAMES,
    TEST_LENGTHS,
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    VOCAB_SIZE,
    Stage10Example,
    _expected_calibration_error,
    make_stage10_splits,
    positional_bias,
)
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS
from .stage61_support_complete_two_block_audit import DEFAULT_AUDIT_SEEDS, DEFAULT_EXAMPLES_PER_LENGTH


STAGE71_SCHEMA_VERSION = "qrope_stage71_positional_bias_copy_upper_bound_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage71_positional_bias_copy_upper_bound_audit"


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential deterministic positional-bias copy upper bound on the original Stage10 rows.",
            "Evidence about whether each tested positional method's own bias can identify the copy source before learned decoder training.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons on unchanged train-short/test-long splits.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap replaces RoPE",
            "a claim that deterministic argmax copy is learned decoder-only transformer behavior",
            "a claim that a one-step copy upper bound is positional-method promotion evidence by itself",
            "broad quantum advantage",
        ],
    }


def _hard_copy_distribution(row: Stage10Example, method_name: str) -> tuple[np.ndarray, int, int, float]:
    bias = np.asarray(positional_bias(row, method_name), dtype=float)
    if len(bias) != row.query_pos:
        raise ValueError(f"bias length {len(bias)} does not match prefix length {row.query_pos}")
    chosen_pos = int(np.argmax(bias))
    chosen_token = int(row.tokens[chosen_pos])
    probabilities = np.zeros(VOCAB_SIZE, dtype=float)
    probabilities[chosen_token] = 1.0
    return probabilities, chosen_pos, chosen_token, float(bias[chosen_pos])


def _predict(row: Stage10Example, method_name: str) -> dict[str, Any]:
    probabilities, chosen_pos, chosen_token, chosen_bias = _hard_copy_distribution(row, method_name)
    sorted_indices = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    target_rank = int(sorted_indices.index(row.label_token) + 1)
    target_probability = float(probabilities[row.label_token])
    return {
        "target_probability": target_probability,
        "target_rank": target_rank,
        "top1_hit": 1.0 if target_rank == 1 else 0.0,
        "top1_confidence": float(probabilities[sorted_indices[0]]),
        "chosen_pos": chosen_pos,
        "chosen_delta": int(row.query_pos - chosen_pos),
        "chosen_token": chosen_token,
        "chosen_bias": round(chosen_bias, 6),
    }


def evaluate_positional_bias_copy(rows: list[Stage10Example], method_name: str) -> dict[str, float]:
    predictions = [_predict(row, method_name) for row in rows]
    target_probs = [float(prediction["target_probability"]) for prediction in predictions]
    top1_hits = [float(prediction["top1_hit"]) for prediction in predictions]
    reciprocal_ranks = [1.0 / float(prediction["target_rank"]) for prediction in predictions]
    top1_confidences = [float(prediction["top1_confidence"]) for prediction in predictions]
    losses = [-math.log(max(value, 1e-12)) for value in target_probs]
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
    }


def _aggregate(run_table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregate_table: list[dict[str, Any]] = []
    for task_name in TASK_NAMES:
        for method_name in METHOD_NAMES:
            rows = [row for row in run_table if row["task"] == task_name and row["method"] == method_name]
            if not rows:
                continue
            record: dict[str, Any] = {
                "task": task_name,
                "method": method_name,
                "seed_count": len(rows),
                "failed_run_count": 0,
            }
            for metric_name in (
                "train_loss",
                "train_perplexity",
                "train_top1_accuracy",
                "train_mrr",
                "train_mean_target_probability",
                "train_mean_top1_confidence",
                "train_expected_calibration_error",
                "validation_loss",
                "validation_perplexity",
                "validation_top1_accuracy",
                "validation_mrr",
                "validation_mean_target_probability",
                "validation_mean_top1_confidence",
                "validation_expected_calibration_error",
                "test_loss",
                "test_perplexity",
                "test_top1_accuracy",
                "test_mrr",
                "test_mean_target_probability",
                "test_mean_top1_confidence",
                "test_expected_calibration_error",
            ):
                record[f"{metric_name}_mean"] = round(float(np.mean([row[metric_name] for row in rows])), 6)
            aggregate_table.append(record)
    return aggregate_table


def _best_row(rows: list[dict[str, Any]], *, task_name: str, split: str = "test") -> dict[str, Any]:
    return sorted(
        [row for row in rows if row["task"] == task_name],
        key=lambda row: (
            row[f"{split}_top1_accuracy_mean"],
            row[f"{split}_mrr_mean"],
            row[f"{split}_mean_target_probability_mean"],
            -row[f"{split}_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )[0]


def _decision(aggregate_table: list[dict[str, Any]]) -> dict[str, Any]:
    retrieval_best = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_generalized = [
        task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_retrieval_generalized = [
        task for task in retrieval_generalized if retrieval_best[task]["method"].startswith("phasewrap")
    ]
    if all(task in retrieval_generalized for task in RETRIEVAL_TASKS):
        decision = "POSITIONAL_BIAS_COPY_SOLVES_ORIGINAL_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "A deterministic positional-bias copy upper bound solves both original retrieval lanes; review method ordering before any claim update."
    elif retrieval_generalized:
        decision = "POSITIONAL_BIAS_COPY_PARTIAL_ORIGINAL_RETRIEVAL_UPPER_BOUND"
        boundary = "A deterministic positional-bias copy upper bound solves at least one original retrieval lane, but not the full gate."
    else:
        decision = "POSITIONAL_BIAS_COPY_DOES_NOT_SOLVE_ORIGINAL_RETRIEVAL"
        boundary = "Even deterministic positional-bias copy does not solve original held-out retrieval."
    tiny_best = _best_row(aggregate_table, task_name="tiny_text_fact_qa")
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "retrieval_generalized_tasks": retrieval_generalized,
        "phasewrap_retrieval_generalized_tasks": phasewrap_retrieval_generalized,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
    }


def run_stage71_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    per_example_table: list[dict[str, Any]] = []
    for task_name, splits in splits_by_task.items():
        for seed in seeds:
            split_rows = {
                split_name: [row for row in rows if row.seed == seed]
                for split_name, rows in splits.items()
            }
            for method_name in method_names:
                stage10_method = _stage10_method_name(method_name)
                row: dict[str, Any] = {
                    "task": task_name,
                    "seed": seed,
                    "method": method_name,
                    "stage10_method_alias": stage10_method,
                    "train_row_count": len(split_rows["train"]),
                    "validation_row_count": len(split_rows["validation"]),
                    "test_row_count": len(split_rows["test"]),
                }
                for split_name, rows in split_rows.items():
                    metrics = evaluate_positional_bias_copy(rows, stage10_method)
                    for metric_name, value in metrics.items():
                        if metric_name != "row_count":
                            row[f"{split_name}_{metric_name}"] = value
                    for example in rows:
                        prediction = _predict(example, stage10_method)
                        per_example_table.append(
                            {
                                "task": task_name,
                                "split": split_name,
                                "seed": seed,
                                "method": method_name,
                                "example_id": example.example_id,
                                "sequence_length": example.sequence_length,
                                "query_pos": example.query_pos,
                                "reference_delta": example.reference_delta,
                                "target_delta": example.target_delta,
                                "target_pos": example.target_pos,
                                "label_token": example.label_token,
                                **prediction,
                            }
                        )
                run_table.append(row)
    aggregate_table = _aggregate(run_table)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (
            row["task"],
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            -row["test_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE71_SCHEMA_VERSION,
        "stage": "stage71_positional_bias_copy_upper_bound_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_original_rows_positional_bias_copy_upper_bound_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage70_strongest_honest_claim_synthesis",
        "source_rows": "stage10 original train-short/test-long rows",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "model": {
            "type": "deterministic_positional_bias_argmax_copy_upper_bound",
            "trained_parameters": "none",
            "row_policy": "select argmax of each method's positional bias over prefix positions and copy that prefix token",
            "value_output_mode": "hard one-token copy distribution",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": [],
        "run_table": run_table,
        "per_example_table": per_example_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage71_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "per_example_csv_path": str((output_dir / "per_example_results.csv").as_posix()),
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()),
        "decision": result["decision"],
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
        "per_example_csv": str(output_dir / "per_example_results.csv"),
        "failed_runs": str(output_dir / "failed_runs.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["aggregate_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["aggregate_table"])
    with (output_dir / "per_run_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["run_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["run_table"])
    with (output_dir / "per_example_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["per_example_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["per_example_table"])
    (output_dir / "failed_runs.json").write_text(json.dumps(result["failed_runs"], indent=2, sort_keys=True), encoding="utf-8")
    return paths


def print_stage71_summary(result: dict[str, Any]) -> None:
    columns = (
        "task",
        "method",
        "seed_count",
        "test_top1_accuracy_mean",
        "test_mrr_mean",
        "test_mean_target_probability_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
