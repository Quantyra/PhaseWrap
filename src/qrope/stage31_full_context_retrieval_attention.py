from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from .automated_stage_gates import phase_residual
from .stage12_ruler_retrieval import (
    DEFAULT_CONTEXT_LENGTHS,
    DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    DEFAULT_SEEDS as DATA_SEEDS,
    TASK_NAMES,
    Stage12Example,
    make_stage12_examples,
)
from .stage13_positional_adapter import split_examples


STAGE31_SCHEMA_VERSION = "qrope_stage31_full_context_retrieval_attention_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage31_full_context_retrieval_attention"
DEFAULT_MODEL_SEEDS = (3101, 3119, 3121, 3137, 3163)
METHOD_NAMES = (
    "no_position",
    "alibi",
    "rope_relative",
    "sinusoidal",
    "phasewrap_bias",
    "phasewrap_distance_adapter",
)
PARAMETER_COUNT = 4


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _rope_inverse_frequencies(dim: int = 32, base: float = 10000.0) -> np.ndarray:
    return np.array([base ** (-2.0 * index / dim) for index in range(dim // 2)], dtype=float)


def _phasewrap_score(reference_delta: int, candidate_delta: int) -> float:
    margins = []
    for period in (8, 12):
        residual = phase_residual(reference_delta, candidate_delta, period)
        margins.append(math.cos(residual) - math.cos(2.0 * math.pi / float(period)))
    return float(margins[0] * margins[1])


def full_context_features(row: Stage12Example, method_name: str) -> np.ndarray:
    positions = np.arange(row.query_pos, dtype=int)
    candidate_deltas = row.query_pos - positions.astype(float)
    tokens = np.array(row.tokens[: row.query_pos], dtype=int)
    content = (tokens == row.query_token).astype(float)
    recency = -candidate_deltas / float(row.query_pos)
    diff = float(row.reference_delta) - candidate_deltas

    if method_name == "no_position":
        position_signal = np.zeros(row.query_pos, dtype=float)
    elif method_name == "alibi":
        position_signal = recency
    elif method_name == "rope_relative":
        inv_freq = _rope_inverse_frequencies()
        position_signal = np.mean(np.cos(diff[:, None] * inv_freq[None, :]), axis=1)
    elif method_name == "sinusoidal":
        periods = np.array((4.0, 8.0, 16.0, 32.0, 64.0), dtype=float)
        position_signal = np.mean(np.cos(2.0 * math.pi * diff[:, None] / periods[None, :]), axis=1)
    elif method_name == "phasewrap_bias":
        position_signal = np.array([_phasewrap_score(row.reference_delta, int(delta)) for delta in candidate_deltas], dtype=float)
    elif method_name == "phasewrap_distance_adapter":
        phase = np.array([_phasewrap_score(row.reference_delta, int(delta)) for delta in candidate_deltas], dtype=float)
        distance = -np.abs(diff) / float(row.query_pos)
        position_signal = phase + distance
    else:
        raise ValueError(f"unknown method_name: {method_name}")
    return np.column_stack([np.ones(row.query_pos), content, position_signal, content * position_signal])


def _target_distribution(row: Stage12Example) -> np.ndarray:
    targets = np.zeros(row.query_pos, dtype=float)
    for position in row.target_positions:
        targets[position] = 1.0 / float(len(row.target_positions))
    return targets


def _init_weights(*, method_name: str, model_seed: int) -> np.ndarray:
    seed_text = f"stage31:{method_name}:{model_seed}:{PARAMETER_COUNT}"
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16) % (2**32)
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, 0.03, size=PARAMETER_COUNT)


def _loss_and_gradient(rows: list[Stage12Example], method_name: str, weights: np.ndarray, l2: float) -> tuple[float, np.ndarray]:
    total_loss = 0.0
    gradient = np.zeros_like(weights)
    for row in rows:
        features = full_context_features(row, method_name)
        probabilities = _softmax(features @ weights)
        targets = _target_distribution(row)
        target_mass = max(float(np.sum(probabilities[targets > 0.0])), 1e-12)
        total_loss += -math.log(target_mass)
        gradient += features.T @ (probabilities - targets)
    scale = 1.0 / float(len(rows))
    total_loss = total_loss * scale + 0.5 * l2 * float(weights @ weights)
    gradient = gradient * scale + l2 * weights
    return float(total_loss), gradient


def train_full_context_attention(
    rows: list[Stage12Example],
    method_name: str,
    *,
    model_seed: int,
    epochs: int = 260,
    learning_rate: float = 0.18,
    l2: float = 0.001,
) -> dict[str, Any]:
    weights = _init_weights(method_name=method_name, model_seed=model_seed)
    first_moment = np.zeros_like(weights)
    second_moment = np.zeros_like(weights)
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        loss, gradient = _loss_and_gradient(rows, method_name, weights, l2)
        step = epoch + 1
        first_moment = 0.9 * first_moment + 0.1 * gradient
        second_moment = 0.999 * second_moment + 0.001 * (gradient * gradient)
        corrected_first = first_moment / (1.0 - 0.9**step)
        corrected_second = second_moment / (1.0 - 0.999**step)
        weights -= learning_rate * corrected_first / (np.sqrt(corrected_second) + 1e-8)
        if epoch in {0, epochs // 4, epochs // 2, epochs - 1}:
            history.append({"epoch": step, "loss": round(float(loss), 6)})
    rounded_weights = [round(float(value), 8) for value in weights.tolist()]
    weight_bytes = json.dumps(rounded_weights).encode("utf-8")
    return {
        "method": method_name,
        "model_seed": model_seed,
        "parameter_count": PARAMETER_COUNT,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "weights": rounded_weights,
        "weights_sha256": hashlib.sha256(weight_bytes).hexdigest(),
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def _ranked_indices(probabilities: np.ndarray) -> list[int]:
    return sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))


def _first_relevant_rank(probabilities: np.ndarray, target_positions: tuple[int, ...]) -> int:
    target_set = set(target_positions)
    for rank, index in enumerate(_ranked_indices(probabilities), start=1):
        if index in target_set:
            return rank
    raise RuntimeError("target absent from full context distribution")


def _expected_calibration_error(confidences: list[float], correctness: list[float], *, bins: int = 10) -> float:
    total = float(len(confidences))
    ece = 0.0
    for bin_index in range(bins):
        low = bin_index / float(bins)
        high = (bin_index + 1) / float(bins)
        if bin_index == bins - 1:
            indices = [index for index, value in enumerate(confidences) if low <= value <= high]
        else:
            indices = [index for index, value in enumerate(confidences) if low <= value < high]
        if not indices:
            continue
        avg_confidence = float(np.mean([confidences[index] for index in indices]))
        avg_accuracy = float(np.mean([correctness[index] for index in indices]))
        ece += (len(indices) / total) * abs(avg_confidence - avg_accuracy)
    return float(ece)


def evaluate_full_context_attention(rows: list[Stage12Example], method_name: str, weights: np.ndarray) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    top1_confidences: list[float] = []
    ranks: list[int] = []
    for row in rows:
        probabilities = _softmax(full_context_features(row, method_name) @ weights)
        rank = _first_relevant_rank(probabilities, row.target_positions)
        top_index = _ranked_indices(probabilities)[0]
        top1_correct = 1.0 if top_index in set(row.target_positions) else 0.0
        target_mass = max(float(np.sum(probabilities[list(row.target_positions)])), 1e-12)
        losses.append(-math.log(target_mass))
        top1_hits.append(top1_correct)
        reciprocal_ranks.append(1.0 / float(rank))
        target_masses.append(target_mass)
        top1_confidences.append(float(probabilities[top_index]))
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_masses)), 6),
        "target_probability_mae": round(float(np.mean([1.0 - value for value in target_masses])), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
        "mean_first_relevant_rank": round(float(np.mean(ranks)), 6),
    }


def _metric_ci(values: list[float], *, seed_text: str, iterations: int = 600) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def _aggregate_runs(run_rows: list[dict[str, Any]], *, method_name: str) -> dict[str, Any]:
    metric_names = (
        "loss",
        "top1_accuracy",
        "mrr",
        "mean_target_probability",
        "target_probability_mae",
        "mean_top1_confidence",
        "expected_calibration_error",
        "mean_first_relevant_rank",
    )
    row: dict[str, Any] = {"method": method_name, "run_count": len(run_rows), "row_count": run_rows[0]["row_count"], "parameter_count": PARAMETER_COUNT}
    for metric_name in metric_names:
        values = [float(item[metric_name]) for item in run_rows]
        ci = _metric_ci(values, seed_text=f"stage31:{method_name}:{metric_name}")
        row[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        row[f"{metric_name}_ci_low"] = ci["low"]
        row[f"{metric_name}_ci_high"] = ci["high"]
    return row


def run_stage31_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 260,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    rows = make_stage12_examples(seeds=data_seeds, context_lengths=context_lengths, examples_per_task_length=examples_per_task_length)
    splits = split_examples(rows)
    training_records: list[dict[str, Any]] = []
    run_table: list[dict[str, Any]] = []
    task_table: list[dict[str, Any]] = []
    weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        for model_seed in model_seeds:
            training = train_full_context_attention(splits["train"], method_name, model_seed=model_seed, epochs=epochs)
            training_records.append(training)
            weights = np.array(training["weights"], dtype=float)
            row = evaluate_full_context_attention(splits["test"], method_name, weights)
            row["method"] = method_name
            row["model_seed"] = model_seed
            run_table.append(row)
            if float(row["top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "model_seed": model_seed, "top1_accuracy": row["top1_accuracy"], "mrr": row["mrr"], "criterion": "test_top1_accuracy_below_0.5"})
            for task_name in TASK_NAMES:
                task_rows = [example for example in splits["test"] if example.task == task_name]
                task_result = evaluate_full_context_attention(task_rows, method_name, weights)
                task_result["method"] = method_name
                task_result["model_seed"] = model_seed
                task_result["task"] = task_name
                task_table.append(task_result)
    table = [_aggregate_runs([row for row in run_table if row["method"] == method_name], method_name=method_name) for method_name in method_names]
    selection_table = sorted(table, key=lambda row: (row["top1_accuracy_mean"], row["mrr_mean"], row["mean_target_probability_mean"], row["method"]), reverse=True)
    return {
        "schema_version": STAGE31_SCHEMA_VERSION,
        "stage": "stage31_full_context_retrieval_attention",
        "dataset": "stage12_non_phase_cued_ruler_style_retrieval_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "data_seeds": list(data_seeds),
        "model_seeds": list(model_seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": [128, 256],
        "validation_lengths": [512],
        "test_lengths": [1024],
        "examples_per_task_length": examples_per_task_length,
        "task_names": list(TASK_NAMES),
        "method_names": list(method_names),
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "model": {
            "type": "learned_full_context_single_head_retrieval_attention",
            "parameter_count": PARAMETER_COUNT,
            "epochs": epochs,
            "trained_parameters": "bias, content-match scale, positional scale, content-position interaction scale",
        },
        "task": {
            "description": "Full-prefix non-phase-cued passkey, multi-needle, and aggregation-style retrieval over Stage 12 rows.",
            "target_construction": "Targets are selected by explicit retrieval rules, not by the PhaseWrap score.",
            "scope": "This is a learned full-context retrieval-attention harness, not a full decoder-only language-model benchmark.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic multi-initialization full-context retrieval-attention comparison on Stage 12 non-phase-cued rows.",
                "Every positional variant uses the same four learned attention parameters, optimizer, epochs, and train/test split.",
                "Confidence intervals over initialization seeds and explicit weak-run reporting.",
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
        "run_table": run_table,
        "task_table": task_table,
        "table": table,
        "selection_table": selection_table,
        "weak_runs": weak_runs,
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
    }


def write_stage31_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "data_seeds": result["data_seeds"],
        "model_seeds": result["model_seeds"],
        "train_lengths": result["train_lengths"],
        "validation_lengths": result["validation_lengths"],
        "test_lengths": result["test_lengths"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "task_names": result["task_names"],
        "method_names": result["method_names"],
        "model": result["model"],
        "task": result["task"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "task_summary_csv_path": str((output_dir / "task_summary.csv").as_posix()),
        "weak_runs_path": str((output_dir / "weak_runs.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
        "task_summary_csv": str(output_dir / "task_summary.csv"),
        "weak_runs": str(output_dir / "weak_runs.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "weak_runs.json").write_text(json.dumps(result["weak_runs"], indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    with (output_dir / "per_run_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["run_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["run_table"])
    with (output_dir / "task_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["task_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["task_table"])
    return paths


def print_stage31_table(result: dict[str, Any]) -> None:
    columns = ("method", "run_count", "parameter_count", "top1_accuracy_mean", "mrr_mean", "mean_target_probability_mean", "expected_calibration_error_mean")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
