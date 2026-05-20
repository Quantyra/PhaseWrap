from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from .stage13_positional_adapter import METHOD_NAMES
from .stage26_compact_kv_qa import (
    CONTEXT_LENGTHS,
    DEFAULT_SEEDS as DATA_SEEDS,
    EXAMPLES_PER_LENGTH,
    Stage26Example,
    candidate_features,
    make_stage26_examples,
    split_examples,
)


STAGE27_SCHEMA_VERSION = "qrope_stage27_compact_kv_transformer_bridge_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage27_compact_kv_transformer_bridge"
DEFAULT_MODEL_SEEDS = (2701, 2711, 2729, 2731, 2741)
HIDDEN_DIM = 8


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _metric_ci(values: list[float], *, seed_text: str, iterations: int = 600) -> dict[str, float]:
    if not values:
        raise ValueError("cannot bootstrap an empty metric list")
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {
        "low": round(means[int(0.025 * (iterations - 1))], 6),
        "high": round(means[int(0.975 * (iterations - 1))], 6),
    }


def _init_params(feature_dim: int, *, method_name: str, model_seed: int, hidden_dim: int) -> dict[str, np.ndarray]:
    seed_text = f"stage27:{method_name}:{model_seed}:{feature_dim}:{hidden_dim}"
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16) % (2**32)
    rng = np.random.default_rng(seed)
    return {
        "w1": rng.normal(0.0, 0.04, size=(feature_dim, hidden_dim)),
        "b1": np.zeros(hidden_dim, dtype=float),
        "w2": rng.normal(0.0, 0.04, size=hidden_dim),
        "b2": np.zeros(1, dtype=float),
    }


def _forward(row: Stage26Example, method_name: str, params: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    features = candidate_features(row, method_name)
    hidden_pre = features @ params["w1"] + params["b1"]
    hidden = np.tanh(hidden_pre)
    logits = hidden @ params["w2"] + float(params["b2"][0])
    probabilities = _softmax(logits)
    return probabilities, {"features": features, "hidden": hidden, "probabilities": probabilities}


def _loss_and_gradient(
    rows: list[Stage26Example],
    method_name: str,
    params: dict[str, np.ndarray],
    l2: float,
) -> tuple[float, dict[str, np.ndarray]]:
    grads = {key: np.zeros_like(value) for key, value in params.items()}
    total_loss = 0.0
    for row in rows:
        probabilities, cache = _forward(row, method_name, params)
        target = np.zeros(len(row.candidate_positions), dtype=float)
        target[row.target_index] = 1.0
        total_loss += -math.log(max(float(probabilities[row.target_index]), 1e-12))
        grad_logits = probabilities - target
        hidden = cache["hidden"]
        features = cache["features"]
        grads["w2"] += hidden.T @ grad_logits
        grads["b2"] += np.array([float(np.sum(grad_logits))])
        grad_hidden = grad_logits[:, None] * params["w2"][None, :]
        grad_hidden_pre = grad_hidden * (1.0 - hidden * hidden)
        grads["w1"] += features.T @ grad_hidden_pre
        grads["b1"] += np.sum(grad_hidden_pre, axis=0)
    scale = 1.0 / float(len(rows))
    total_loss *= scale
    for key, value in params.items():
        grads[key] *= scale
        if key.startswith("w"):
            total_loss += 0.5 * l2 * float(np.sum(value * value))
            grads[key] += l2 * value
    return float(total_loss), grads


def train_attention_bridge(
    rows: list[Stage26Example],
    method_name: str,
    *,
    model_seed: int,
    epochs: int = 160,
    learning_rate: float = 0.2,
    l2: float = 0.001,
    hidden_dim: int = HIDDEN_DIM,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("rows must be non-empty")
    feature_dim = candidate_features(rows[0], method_name).shape[1]
    params = _init_params(feature_dim, method_name=method_name, model_seed=model_seed, hidden_dim=hidden_dim)
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        loss, grads = _loss_and_gradient(rows, method_name, params, l2)
        for key in params:
            params[key] -= learning_rate * grads[key]
        if epoch in {0, epochs // 4, epochs // 2, epochs - 1}:
            history.append({"epoch": epoch + 1, "loss": round(float(loss), 6)})
    return {
        "method": method_name,
        "model_seed": model_seed,
        "feature_dim": feature_dim,
        "hidden_dim": hidden_dim,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "params": {key: np.round(value, 8).tolist() for key, value in params.items()},
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def _params_from_record(record: dict[str, Any]) -> dict[str, np.ndarray]:
    return {key: np.array(value, dtype=float) for key, value in record["params"].items()}


def _rank(probabilities: np.ndarray, target_index: int) -> int:
    ranked = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    return ranked.index(target_index) + 1


def evaluate_attention_bridge(rows: list[Stage26Example], method_name: str, params: dict[str, np.ndarray]) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_probabilities: list[float] = []
    ranks: list[int] = []
    for row in rows:
        probabilities, _ = _forward(row, method_name, params)
        rank = _rank(probabilities, row.target_index)
        target_probability = max(float(probabilities[row.target_index]), 1e-12)
        losses.append(-math.log(target_probability))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        reciprocal_ranks.append(1.0 / float(rank))
        target_probabilities.append(target_probability)
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probabilities)), 6),
        "mean_first_relevant_rank": round(float(np.mean(ranks)), 6),
    }


def _aggregate_runs(run_rows: list[dict[str, Any]], *, method_name: str) -> dict[str, Any]:
    metric_names = ("loss", "top1_accuracy", "mrr", "mean_target_probability", "mean_first_relevant_rank")
    aggregate: dict[str, Any] = {"method": method_name, "run_count": len(run_rows), "row_count": run_rows[0]["row_count"]}
    for metric_name in metric_names:
        values = [float(row[metric_name]) for row in run_rows]
        ci = _metric_ci(values, seed_text=f"stage27:{method_name}:{metric_name}")
        aggregate[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        aggregate[f"{metric_name}_ci_low"] = ci["low"]
        aggregate[f"{metric_name}_ci_high"] = ci["high"]
    return aggregate


def run_stage27_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = CONTEXT_LENGTHS,
    examples_per_length: int = EXAMPLES_PER_LENGTH,
    epochs: int = 160,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    rows = make_stage26_examples(seeds=data_seeds, context_lengths=context_lengths, examples_per_length=examples_per_length)
    splits = split_examples(rows)
    training_records: list[dict[str, Any]] = []
    run_table: list[dict[str, Any]] = []
    weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        for model_seed in model_seeds:
            training = train_attention_bridge(splits["train"], method_name, model_seed=model_seed, epochs=epochs)
            training_records.append(training)
            params = _params_from_record(training)
            row = evaluate_attention_bridge(splits["test"], method_name, params)
            row["method"] = method_name
            row["model_seed"] = model_seed
            run_table.append(row)
            if float(row["top1_accuracy"]) < 0.5:
                weak_runs.append(
                    {
                        "method": method_name,
                        "model_seed": model_seed,
                        "top1_accuracy": row["top1_accuracy"],
                        "mrr": row["mrr"],
                        "criterion": "test_top1_accuracy_below_0.5",
                    }
                )
    table = [_aggregate_runs([row for row in run_table if row["method"] == method_name], method_name=method_name) for method_name in method_names]
    selection_table = sorted(
        table,
        key=lambda row: (
            row["top1_accuracy_mean"],
            row["mrr_mean"],
            row["mean_target_probability_mean"],
            row["method"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE27_SCHEMA_VERSION,
        "stage": "stage27_compact_kv_transformer_bridge",
        "dataset": "stage26_compact_key_value_qa_retrieval_v1",
        "no_hardware_submission": True,
        "data_seeds": list(data_seeds),
        "model_seeds": list(model_seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": [256, 512],
        "validation_lengths": [1024],
        "test_lengths": [2048],
        "examples_per_length": examples_per_length,
        "candidate_count": 32,
        "method_names": list(method_names),
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "model": {
            "type": "one_hidden_layer_attention_bridge_over_stage26_candidate_features",
            "hidden_dim": HIDDEN_DIM,
            "epochs": epochs,
            "trained_parameters": "feature-to-hidden weights, hidden bias, hidden-to-attention-logit weights, logit bias",
        },
        "task": {
            "description": "Compact train-short/test-long key-value QA attention bridge with explicit content keys.",
            "target_construction": "The target is the latest candidate with the matching content key; it is not selected by the PhaseWrap score.",
            "scope": "This is a compact attention/value bridge, not a full decoder-only language-model benchmark.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic multi-initialization attention-bridge comparison on the Stage 26 compact QA packet.",
                "Evidence about whether learned nonlinear attention over PhaseWrap-derived candidate features is competitive on this compact non-PhaseWrap-labeled task.",
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
        "table": table,
        "selection_table": selection_table,
        "weak_runs": weak_runs,
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
    }


def write_stage27_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "data_seeds": result["data_seeds"],
        "model_seeds": result["model_seeds"],
        "train_lengths": result["train_lengths"],
        "validation_lengths": result["validation_lengths"],
        "test_lengths": result["test_lengths"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "method_names": result["method_names"],
        "model": result["model"],
        "task": result["task"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "weak_runs_path": str((output_dir / "weak_runs.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
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
    return paths


def print_stage27_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "run_count",
        "top1_accuracy_mean",
        "top1_accuracy_ci_low",
        "top1_accuracy_ci_high",
        "mrr_mean",
        "mrr_ci_low",
        "mrr_ci_high",
        "mean_target_probability_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
