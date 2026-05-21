from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import (
    DEFAULT_SEEDS,
    MODEL_DIM,
    TASK_NAMES,
    TEST_LENGTHS,
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    VOCAB_SIZE,
    Stage10Example,
    _expected_calibration_error,
    _softmax,
    autograd_available,
    make_stage10_splits,
    positional_bias,
)
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage47_adam_decoder_generalization_audit import DEFAULT_LEARNING_RATE


STAGE52_SCHEMA_VERSION = "qrope_stage52_two_block_decoder_feasibility_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage52_two_block_decoder_feasibility_audit"
DEFAULT_AUDIT_SEEDS = (DEFAULT_SEEDS[0],)
DEFAULT_EXAMPLES_PER_LENGTH = 1
DEFAULT_EPOCHS = 45
CAPACITY_TRAIN_TOP1_THRESHOLD = 0.75
GENERALIZATION_TOP1_THRESHOLD = 0.50
TINY_TEXT_TASK = "tiny_text_fact_qa"
RETRIEVAL_TASKS = tuple(task for task in TASK_NAMES if task != TINY_TEXT_TASK)


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential feasibility audit for a stronger autograd-backed two-block decoder harness.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons under the same Stage 45-51 row family.",
            "Separated train/validation/test metrics and failed-run retention before scaling the stronger decoder path.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a one-seed feasibility audit satisfies the five-seed promotion standard",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    return {
        "schema_version": STAGE52_SCHEMA_VERSION,
        "stage": "stage52_two_block_decoder_feasibility_audit",
        "status": "blocked",
        "blocked_reason": reason,
        "install_command": "python -m pip install -e \".[transformer]\"",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_AUDIT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def _init_vector(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    matrix_size = MODEL_DIM * MODEL_DIM
    # emb + two q/k/v/o attention blocks + one gated residual projection + vocab output + positional scale.
    size = VOCAB_SIZE * MODEL_DIM + 8 * matrix_size + MODEL_DIM * VOCAB_SIZE + 1
    return rng.normal(0.0, 0.035, size=size)


def _unpack(vector: Any):
    import autograd.numpy as anp

    index = 0
    emb_size = VOCAB_SIZE * MODEL_DIM
    emb = anp.reshape(vector[index : index + emb_size], (VOCAB_SIZE, MODEL_DIM))
    index += emb_size
    matrices = []
    matrix_size = MODEL_DIM * MODEL_DIM
    for _ in range(8):
        matrices.append(anp.reshape(vector[index : index + matrix_size], (MODEL_DIM, MODEL_DIM)))
        index += matrix_size
    output = anp.reshape(vector[index : index + MODEL_DIM * VOCAB_SIZE], (MODEL_DIM, VOCAB_SIZE))
    index += MODEL_DIM * VOCAB_SIZE
    return emb, matrices, output, vector[index]


def _attend(hidden: Any, query_hidden: Any, matrices: list[Any], method_bias: Any, pos_scale: Any, block_index: int):
    import autograd.numpy as anp

    offset = block_index * 4
    wq, wk, wv, wo = matrices[offset : offset + 4]
    query = anp.dot(query_hidden, wq)
    keys = anp.dot(hidden, wk)
    values = anp.dot(hidden, wv)
    logits = anp.dot(keys, query) / math.sqrt(float(MODEL_DIM))
    logits = logits + pos_scale * method_bias
    attention = _softmax(logits)
    context = anp.dot(attention, values)
    return anp.tanh(query_hidden + anp.dot(context, wo))


def _row_probabilities(vector: Any, row: Stage10Example, method_name: str):
    import autograd.numpy as anp

    emb, matrices, output, pos_scale = _unpack(vector)
    hidden = emb[anp.array(row.tokens[: row.query_pos])]
    query_hidden = emb[row.tokens[row.query_pos]]
    method_bias = anp.array(positional_bias(row, method_name))
    query_hidden = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 0)
    query_hidden = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 1)
    return _softmax(anp.dot(query_hidden, output))


def _row_loss(vector: Any, row: Stage10Example, method_name: str):
    import autograd.numpy as anp

    probabilities = _row_probabilities(vector, row, method_name)
    return -anp.log(probabilities[row.label_token] + 1e-12)


def _batch_loss(vector: Any, rows: list[Stage10Example], method_name: str):
    import autograd.numpy as anp

    return anp.mean(anp.array([_row_loss(vector, row, method_name) for row in rows]))


def train_two_block_decoder(
    rows: list[Stage10Example],
    method_name: str,
    *,
    seed: int,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
) -> dict[str, Any]:
    from autograd import grad

    vector = _init_vector(seed)
    gradient = grad(lambda current: _batch_loss(current, rows, method_name))
    moment = np.zeros_like(vector)
    velocity = np.zeros_like(vector)
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss_value = float(_batch_loss(vector, rows, method_name))
        grad_value = gradient(vector)
        moment = beta1 * moment + (1.0 - beta1) * grad_value
        velocity = beta2 * velocity + (1.0 - beta2) * (grad_value * grad_value)
        moment_hat = moment / (1.0 - beta1**epoch)
        velocity_hat = velocity / (1.0 - beta2**epoch)
        vector = vector - learning_rate * moment_hat / (np.sqrt(velocity_hat) + epsilon)
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            history.append({"epoch": epoch, "loss": round(loss_value, 6)})
    _, _, _, pos_scale = _unpack(vector)
    return {
        "weights": vector,
        "optimizer": "full_batch_adam",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "learned_position_scale": round(float(pos_scale), 6),
    }


def _predict(vector: Any, row: Stage10Example, method_name: str) -> tuple[float, int, float]:
    probabilities = np.asarray(_row_probabilities(vector, row, method_name), dtype=float)
    sorted_indices = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    return float(probabilities[row.label_token]), int(sorted_indices.index(row.label_token) + 1), float(probabilities[sorted_indices[0]])


def evaluate_two_block_decoder(rows: list[Stage10Example], method_name: str, vector: Any) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence = _predict(vector, row, method_name)
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probs.append(target_probability)
        top1_confidences.append(top1_confidence)
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


def _metric_names(split: str) -> tuple[str, ...]:
    return (
        f"{split}_loss",
        f"{split}_perplexity",
        f"{split}_top1_accuracy",
        f"{split}_mrr",
        f"{split}_mean_target_probability",
        f"{split}_mean_top1_confidence",
        f"{split}_expected_calibration_error",
    )


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 300) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def _aggregate(run_table: list[dict[str, Any]], failed_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
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
                "failed_run_count": len([run for run in failed_runs if run["task"] == task_name and run["method"] == method_name]),
                "learned_position_scale_mean": round(float(np.mean([row["learned_position_scale"] for row in rows])), 6),
            }
            for metric_name in _metric_names("train") + _metric_names("validation") + _metric_names("test") + ("final_training_loss",):
                values = [float(row[metric_name]) for row in rows]
                ci = _bootstrap_ci(values, seed_text=f"stage52:{task_name}:{method_name}:{metric_name}")
                record[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
                record[f"{metric_name}_ci_low"] = ci["low"]
                record[f"{metric_name}_ci_high"] = ci["high"]
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
    best_train = sorted(
        aggregate_table,
        key=lambda row: (row["train_top1_accuracy_mean"], row["train_mrr_mean"], row["train_mean_target_probability_mean"], row["method"]),
        reverse=True,
    )[0]
    retrieval_best = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_generalized = [
        task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_retrieval_generalized = [
        task for task in retrieval_generalized if retrieval_best[task]["method"].startswith("phasewrap")
    ]
    capacity_established = best_train["train_top1_accuracy_mean"] >= CAPACITY_TRAIN_TOP1_THRESHOLD
    if not capacity_established:
        decision = "TWO_BLOCK_CAPACITY_NOT_ESTABLISHED"
        boundary = "The stronger two-block decoder does not fit train rows well enough for positional-method promotion."
    elif retrieval_generalized:
        decision = "TWO_BLOCK_RETRIEVAL_GENERALIZATION_PRESENT_REVIEW_REQUIRED"
        boundary = "At least one retrieval lane generalizes; review method ordering before any claim update."
    else:
        decision = "TWO_BLOCK_TRAIN_FIT_WITHOUT_RETRIEVAL_GENERALIZATION"
        boundary = "The stronger two-block decoder fits enough to pass capacity but does not generalize retrieval."
    tiny_best = _best_row(aggregate_table, task_name=TINY_TEXT_TASK)
    return {
        "decision": decision,
        "capacity_train_top1_threshold": CAPACITY_TRAIN_TOP1_THRESHOLD,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "best_train_task": best_train["task"],
        "best_train_method": best_train["method"],
        "best_train_top1": best_train["train_top1_accuracy_mean"],
        "capacity_established": capacity_established,
        "retrieval_generalized_tasks": retrieval_generalized,
        "phasewrap_retrieval_generalized_tasks": phasewrap_retrieval_generalized,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
        "claim_boundary": boundary,
    }


def run_stage52_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    for task_name, splits in splits_by_task.items():
        for seed in seeds:
            train_rows = [row for row in splits["train"] if row.seed == seed]
            validation_rows = [row for row in splits["validation"] if row.seed == seed]
            test_rows = [row for row in splits["test"] if row.seed == seed]
            for method_name in method_names:
                try:
                    stage10_method = _stage10_method_name(method_name)
                    trained = train_two_block_decoder(train_rows, stage10_method, seed=seed, epochs=epochs, learning_rate=learning_rate)
                    row: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": stage10_method,
                        "epochs": epochs,
                        "learning_rate": learning_rate,
                        "optimizer": trained["optimizer"],
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "final_training_loss": trained["final_training_loss"],
                        "learned_position_scale": trained["learned_position_scale"],
                        "training_history": trained["training_history"],
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_two_block_decoder(split_rows, stage10_method, trained["weights"])
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
                except Exception as exc:  # pragma: no cover - retained for artifact completeness.
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _aggregate(run_table, failed_runs)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (row["task"], row["test_top1_accuracy_mean"], row["test_mrr_mean"], row["test_mean_target_probability_mean"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE52_SCHEMA_VERSION,
        "stage": "stage52_two_block_decoder_feasibility_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10/stage45 matched decoder-only rows",
        "source_stage": "stage51_decoder_path_plateau_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "model": {
            "type": "single_query_two_block_residual_decoder",
            "model_dim": MODEL_DIM,
            "vocab_size": VOCAB_SIZE,
            "optimizer": "full_batch_adam",
            "trained_parameters": "token embeddings, two q/k/v/o attention blocks, vocab output projection, positional scale",
            "value_output_mode": "learned vocab softmax, no fixed copy output",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage52_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result_name = "results.json" if result["status"] == "completed" else "preflight.json"
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "result_path": str((output_dir / result_name).as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()) if result["status"] == "completed" else None,
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()) if result["status"] == "completed" else None,
        "decision": result.get("decision"),
        "claim_boundary": result.get("claim_boundary", {}),
    }
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / result_name), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / result_name).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if result["status"] != "completed":
        with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=("stage", "status", "blocked_reason", "install_command"))
            writer.writeheader()
            writer.writerow({"stage": result["stage"], "status": result["status"], "blocked_reason": result.get("blocked_reason", ""), "install_command": result.get("install_command", "")})
        return paths
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["aggregate_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["aggregate_table"])
    per_run_rows = [{key: value for key, value in row.items() if key != "training_history"} for row in result["run_table"]]
    with (output_dir / "per_run_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_run_rows[0].keys()))
        writer.writeheader()
        writer.writerows(per_run_rows)
    (output_dir / "failed_runs.json").write_text(json.dumps(result["failed_runs"], indent=2, sort_keys=True), encoding="utf-8")
    paths["per_run_csv"] = str(output_dir / "per_run_results.csv")
    paths["failed_runs"] = str(output_dir / "failed_runs.json")
    return paths


def print_stage52_summary(result: dict[str, Any]) -> None:
    if result["status"] != "completed":
        print("stage | status | blocked_reason | install_command")
        print("--- | --- | --- | ---")
        print(" | ".join((result["stage"], result["status"], result.get("blocked_reason", ""), result.get("install_command", ""))))
        return
    columns = (
        "task",
        "method",
        "seed_count",
        "failed_run_count",
        "train_top1_accuracy_mean",
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
