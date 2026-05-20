from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .automated_stage_gates import phase_residual


STAGE9_SCHEMA_VERSION = "qrope_stage9_trained_transformer_ablation_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage9_trained_transformer_ablation"
DEFAULT_SEEDS = (211, 223, 227, 229, 233)
TRAIN_LENGTHS = (64, 128)
VALIDATION_LENGTHS = (192,)
TEST_LENGTHS = (256, 512)
EXAMPLES_PER_LENGTH = 16
VALUE_VOCAB_SIZE = 64
DEFAULT_PERIOD_PAIR = (8, 12)
METHOD_NAMES = (
    "phasewrap_bias",
    "phasewrap_adapter",
    "rope_relative",
    "alibi",
    "sinusoidal",
    "no_position",
)


@dataclass(frozen=True)
class Stage9Example:
    example_id: str
    seed: int
    split: str
    sequence_length: int
    query_pos: int
    reference_delta: int
    target_pos: int
    target_delta: int
    tokens: tuple[int, ...]


def _target_delta(reference_delta: int, sequence_length: int, rng: np.random.Generator) -> int:
    query_pos = sequence_length - 1
    candidates = [delta for delta in range(reference_delta, query_pos, 24) if delta >= 3]
    if not candidates:
        return reference_delta
    # Pick the farthest phase-compatible target in most rows, with occasional shorter matches.
    if len(candidates) > 2 and float(rng.random()) < 0.25:
        return int(candidates[int(rng.integers(0, len(candidates) - 1))])
    return int(candidates[-1])


def make_stage9_splits(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    examples_per_length: int = EXAMPLES_PER_LENGTH,
) -> dict[str, list[Stage9Example]]:
    splits: dict[str, list[Stage9Example]] = {"train": [], "validation": [], "test": []}
    split_lengths = {
        "train": TRAIN_LENGTHS,
        "validation": VALIDATION_LENGTHS,
        "test": TEST_LENGTHS,
    }
    reference_deltas = (5, 7, 8, 11, 12, 16, 19, 23, 29, 31)
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for split, lengths in split_lengths.items():
            for sequence_length in lengths:
                query_pos = sequence_length - 1
                for item_index in range(examples_per_length):
                    reference_delta = int(reference_deltas[(seed + sequence_length + item_index) % len(reference_deltas)])
                    target_delta = _target_delta(reference_delta, sequence_length, rng)
                    target_pos = query_pos - target_delta
                    tokens = [int(value) for value in rng.permutation(VALUE_VOCAB_SIZE).tolist()]
                    while len(tokens) < sequence_length:
                        tokens.extend(int(value) for value in rng.permutation(VALUE_VOCAB_SIZE).tolist())
                    tokens = tokens[:sequence_length]
                    tokens[query_pos] = VALUE_VOCAB_SIZE + reference_deltas.index(reference_delta)
                    splits[split].append(
                        Stage9Example(
                            example_id=f"{split}_seed{seed}_L{sequence_length}_{item_index:03d}",
                            seed=seed,
                            split=split,
                            sequence_length=sequence_length,
                            query_pos=query_pos,
                            reference_delta=reference_delta,
                            target_pos=target_pos,
                            target_delta=target_delta,
                            tokens=tuple(tokens),
                        )
                    )
    return splits


def _rope_inverse_frequencies(dim: int = 32, base: float = 10000.0) -> np.ndarray:
    return np.array([base ** (-2.0 * index / dim) for index in range(dim // 2)], dtype=float)


def _phasewrap_score(reference_delta: int, candidate_delta: int, period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR) -> float:
    margins = []
    for period in period_pair:
        residual = phase_residual(reference_delta, candidate_delta, period)
        margins.append(math.cos(residual) - math.cos(2.0 * math.pi / float(period)))
    return float(margins[0] * margins[1])


def positional_features(example: Stage9Example, method_name: str) -> np.ndarray:
    candidate_deltas = example.query_pos - np.arange(example.query_pos, dtype=float)
    diff = float(example.reference_delta) - candidate_deltas
    if method_name == "no_position":
        return np.zeros((example.query_pos, 1), dtype=float)
    if method_name == "alibi":
        return (-candidate_deltas / float(example.query_pos)).reshape(-1, 1)
    if method_name == "sinusoidal":
        periods = np.array((4.0, 8.0, 16.0, 32.0), dtype=float)
        return np.cos(2.0 * math.pi * diff[:, None] / periods[None, :])
    if method_name == "rope_relative":
        inv_freq = _rope_inverse_frequencies()
        return np.cos(diff[:, None] * inv_freq[None, :])
    if method_name == "phasewrap_bias":
        scores = [_phasewrap_score(example.reference_delta, int(delta)) for delta in candidate_deltas]
        return np.array(scores, dtype=float).reshape(-1, 1)
    if method_name == "phasewrap_adapter":
        residual8 = np.array([phase_residual(example.reference_delta, int(delta), 8) for delta in candidate_deltas], dtype=float)
        residual12 = np.array([phase_residual(example.reference_delta, int(delta), 12) for delta in candidate_deltas], dtype=float)
        cos8 = np.cos(residual8)
        cos12 = np.cos(residual12)
        score = np.array([_phasewrap_score(example.reference_delta, int(delta)) for delta in candidate_deltas], dtype=float)
        distance = np.abs(diff) / float(example.query_pos)
        return np.column_stack([score, cos8, cos12, cos8 * cos12, -distance])
    raise ValueError(f"unknown method_name: {method_name}")


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _loss_and_gradient(rows: list[Stage9Example], method_name: str, weights: np.ndarray, l2: float) -> tuple[float, np.ndarray]:
    total_loss = 0.0
    grad = np.zeros_like(weights)
    for row in rows:
        features = positional_features(row, method_name)
        logits = features @ weights
        probabilities = _softmax(logits)
        target_index = row.target_pos
        target_probability = max(float(probabilities[target_index]), 1e-12)
        total_loss += -math.log(target_probability)
        delta = probabilities.copy()
        delta[target_index] -= 1.0
        grad += features.T @ delta
    total_loss = total_loss / float(len(rows)) + 0.5 * l2 * float(weights @ weights)
    grad = grad / float(len(rows)) + l2 * weights
    return float(total_loss), grad


def train_positional_attention(
    rows: list[Stage9Example],
    method_name: str,
    *,
    epochs: int = 160,
    learning_rate: float = 0.4,
    l2: float = 0.001,
) -> dict[str, Any]:
    feature_dim = positional_features(rows[0], method_name).shape[1]
    weights = np.zeros(feature_dim, dtype=float)
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        loss, grad = _loss_and_gradient(rows, method_name, weights, l2)
        weights -= learning_rate * grad
        if epoch in {0, epochs // 4, epochs // 2, epochs - 1}:
            history.append({"epoch": epoch + 1, "loss": round(loss, 6)})
    return {
        "method": method_name,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "weights": [round(float(value), 8) for value in weights.tolist()],
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def _target_rank(probabilities: np.ndarray, target_index: int) -> int:
    sorted_indices = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    return sorted_indices.index(target_index) + 1


def evaluate_positional_attention(rows: list[Stage9Example], method_name: str, weights: np.ndarray) -> dict[str, Any]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probabilities: list[float] = []
    ranks: list[int] = []
    for row in rows:
        features = positional_features(row, method_name)
        probabilities = _softmax(features @ weights)
        target_probability = max(float(probabilities[row.target_pos]), 1e-12)
        rank = _target_rank(probabilities, row.target_pos)
        losses.append(-math.log(target_probability))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probabilities.append(target_probability)
        ranks.append(rank)
    return {
        "row_count": len(rows),
        "sequence_length_min": min(row.sequence_length for row in rows),
        "sequence_length_max": max(row.sequence_length for row in rows),
        "loss": round(float(np.mean(losses)), 6),
        "perplexity": round(float(math.exp(np.mean(losses))), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probabilities)), 6),
        "mean_rank": round(float(np.mean(ranks)), 6),
    }


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 1000) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    low_index = int(0.025 * (iterations - 1))
    high_index = int(0.975 * (iterations - 1))
    return {
        "low": round(means[low_index], 6),
        "high": round(means[high_index], 6),
        "iterations": iterations,
        "confidence_level": 0.95,
    }


def run_stage9_ablation(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    examples_per_length: int = EXAMPLES_PER_LENGTH,
    epochs: int = 160,
) -> dict[str, Any]:
    splits = make_stage9_splits(seeds=seeds, examples_per_length=examples_per_length)
    seed_tables: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    for seed in seeds:
        train_rows = [row for row in splits["train"] if row.seed == seed]
        validation_rows = [row for row in splits["validation"] if row.seed == seed]
        test_rows = [row for row in splits["test"] if row.seed == seed]
        for method_name in METHOD_NAMES:
            try:
                trained = train_positional_attention(train_rows, method_name, epochs=epochs)
                weights = np.array(trained["weights"], dtype=float)
                validation_metrics = evaluate_positional_attention(validation_rows, method_name, weights)
                test_metrics = evaluate_positional_attention(test_rows, method_name, weights)
                seed_tables.append(
                    {
                        "seed": seed,
                        "method": method_name,
                        "epochs": epochs,
                        "train_row_count": len(train_rows),
                        "validation_loss": validation_metrics["loss"],
                        "test_loss": test_metrics["loss"],
                        "test_perplexity": test_metrics["perplexity"],
                        "test_top1_accuracy": test_metrics["top1_accuracy"],
                        "test_mrr": test_metrics["mrr"],
                        "test_mean_target_probability": test_metrics["mean_target_probability"],
                        "test_mean_rank": test_metrics["mean_rank"],
                        "weights": trained["weights"],
                        "training_history": trained["training_history"],
                    }
                )
            except Exception as exc:  # pragma: no cover - retained for artifact completeness.
                failed_runs.append({"seed": seed, "method": method_name, "error": str(exc)})

    aggregate_table: list[dict[str, Any]] = []
    for method_name in METHOD_NAMES:
        rows = [row for row in seed_tables if row["method"] == method_name]
        if not rows:
            continue
        for metric_name in ("test_loss", "test_perplexity", "test_top1_accuracy", "test_mrr", "test_mean_target_probability"):
            values = [float(row[metric_name]) for row in rows]
            ci = _bootstrap_ci(values, seed_text=f"stage9:{method_name}:{metric_name}", iterations=1000)
            if metric_name == "test_loss":
                method_record: dict[str, Any] = {
                    "method": method_name,
                    "seed_count": len(rows),
                    "failed_run_count": len([run for run in failed_runs if run["method"] == method_name]),
                    "test_sequence_length_min": min(TEST_LENGTHS),
                    "test_sequence_length_max": max(TEST_LENGTHS),
                }
                aggregate_table.append(method_record)
            aggregate_table[-1][f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
            aggregate_table[-1][f"{metric_name}_ci_low"] = ci["low"]
            aggregate_table[-1][f"{metric_name}_ci_high"] = ci["high"]

    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (row["test_mrr_mean"], row["test_top1_accuracy_mean"], -row["test_loss_mean"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE9_SCHEMA_VERSION,
        "stage": "stage9_trained_transformer_ablation",
        "dataset": "synthetic_train_short_test_long_phase_retrieval_v1",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "seed_count": len(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "method_names": list(METHOD_NAMES),
        "task": {
            "description": "Trained decoder-style positional attention ablation with short-context training and longer-context retrieval evaluation.",
            "note": "This is the first executable Stage 9 subset. It trains positional attention mechanisms under matched controls, but it is not a full language-model benchmark and not a production transformer result.",
        },
        "training_controls": {
            "matched_seeds": list(seeds),
            "matched_examples_per_length": examples_per_length,
            "matched_epochs": epochs,
            "matched_optimizer": "deterministic full-batch gradient descent over positional attention weights",
            "provider_credentials_required": False,
        },
        "claim_boundary": {
            "supported": [
                "A no-credential trained positional attention ablation under matched seeds, data budget, optimizer, and epochs.",
                "Train-short/test-long retrieval evaluation with confidence intervals over seeds.",
                "A first executable Stage 9 artifact for the RoPE-replacement research lane.",
            ],
            "excluded": [
                "production transformer superiority",
                "full language-model validation",
                "proof that PhaseWrap-RoPE replaces RoPE",
                "broad quantum advantage",
                "general cross-backend robustness",
            ],
        },
        "splits": {name: {"row_count": len(rows), "lengths": sorted({row.sequence_length for row in rows})} for name, rows in splits.items()},
        "failed_runs": failed_runs,
        "per_seed_table": seed_tables,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "best_method_by_mrr": ranking_table[0]["method"] if ranking_table else None,
    }


def write_stage9_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "seeds": result["seeds"],
        "train_lengths": result["train_lengths"],
        "validation_lengths": result["validation_lengths"],
        "test_lengths": result["test_lengths"],
        "examples_per_length": result["examples_per_length"],
        "method_names": result["method_names"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_seed_csv_path": str((output_dir / "per_seed_results.csv").as_posix()),
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_seed_csv": str(output_dir / "per_seed_results.csv"),
        "failed_runs": str(output_dir / "failed_runs.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "failed_runs.json").write_text(json.dumps(result["failed_runs"], indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["aggregate_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["aggregate_table"])
    per_seed_rows = [{key: value for key, value in row.items() if key not in {"weights", "training_history"}} for row in result["per_seed_table"]]
    with (output_dir / "per_seed_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_seed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(per_seed_rows)
    return paths


def print_stage9_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "seed_count",
        "failed_run_count",
        "test_sequence_length_min",
        "test_sequence_length_max",
        "test_loss_mean",
        "test_perplexity_mean",
        "test_top1_accuracy_mean",
        "test_mrr_mean",
        "test_mean_target_probability_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
