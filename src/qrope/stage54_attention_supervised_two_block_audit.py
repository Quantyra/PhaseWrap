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
from .stage52_two_block_decoder_feasibility_audit import (
    CAPACITY_TRAIN_TOP1_THRESHOLD,
    GENERALIZATION_TOP1_THRESHOLD,
    TINY_TEXT_TASK,
    RETRIEVAL_TASKS,
    _init_vector,
    _unpack,
)


STAGE54_SCHEMA_VERSION = "qrope_stage54_attention_supervised_two_block_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage54_attention_supervised_two_block_audit"
DEFAULT_AUDIT_SEEDS = (DEFAULT_SEEDS[0],)
DEFAULT_EXAMPLES_PER_LENGTH = 2
DEFAULT_EPOCHS = 70
DEFAULT_ATTENTION_AUX_WEIGHT = 0.6


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A target-attention-supervised diagnostic for the Stage 52/53 two-block decoder path.",
            "Evidence separating attention-selection repair from learned value-output retrieval success.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with train/validation/test metrics and failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap replaces RoPE",
            "a claim that target-attention supervision is standard free decoder generation",
            "a claim that a one-seed diagnostic satisfies the five-seed promotion standard",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    return {
        "schema_version": STAGE54_SCHEMA_VERSION,
        "stage": "stage54_attention_supervised_two_block_audit",
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


def _attend_with_attention(hidden: Any, query_hidden: Any, matrices: list[Any], method_bias: Any, pos_scale: Any, block_index: int):
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
    return anp.tanh(query_hidden + anp.dot(context, wo)), attention


def _row_outputs(vector: Any, row: Stage10Example, method_name: str):
    import autograd.numpy as anp

    emb, matrices, output, pos_scale = _unpack(vector)
    hidden = emb[anp.array(row.tokens[: row.query_pos])]
    query_hidden = emb[row.tokens[row.query_pos]]
    method_bias = anp.array(positional_bias(row, method_name))
    query_hidden, attention_1 = _attend_with_attention(hidden, query_hidden, matrices, method_bias, pos_scale, 0)
    query_hidden, attention_2 = _attend_with_attention(hidden, query_hidden, matrices, method_bias, pos_scale, 1)
    return _softmax(anp.dot(query_hidden, output)), attention_1, attention_2


def _row_loss(vector: Any, row: Stage10Example, method_name: str, attention_aux_weight: float):
    import autograd.numpy as anp

    probabilities, attention_1, attention_2 = _row_outputs(vector, row, method_name)
    target_index = int(row.target_pos)
    vocab_loss = -anp.log(probabilities[row.label_token] + 1e-12)
    attention_loss = -0.5 * (anp.log(attention_1[target_index] + 1e-12) + anp.log(attention_2[target_index] + 1e-12))
    return vocab_loss + attention_aux_weight * attention_loss


def _batch_loss(vector: Any, rows: list[Stage10Example], method_name: str, attention_aux_weight: float):
    import autograd.numpy as anp

    return anp.mean(anp.array([_row_loss(vector, row, method_name, attention_aux_weight) for row in rows]))


def train_attention_supervised_two_block_decoder(
    rows: list[Stage10Example],
    method_name: str,
    *,
    seed: int,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    attention_aux_weight: float = DEFAULT_ATTENTION_AUX_WEIGHT,
) -> dict[str, Any]:
    from autograd import grad

    vector = _init_vector(seed)
    gradient = grad(lambda current: _batch_loss(current, rows, method_name, attention_aux_weight))
    moment = np.zeros_like(vector)
    velocity = np.zeros_like(vector)
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss_value = float(_batch_loss(vector, rows, method_name, attention_aux_weight))
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
        "attention_aux_weight": attention_aux_weight,
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "learned_position_scale": round(float(pos_scale), 6),
    }


def _predict(vector: Any, row: Stage10Example, method_name: str) -> tuple[float, int, float, float]:
    probabilities, attention_1, attention_2 = _row_outputs(vector, row, method_name)
    probs = np.asarray(probabilities, dtype=float)
    sorted_indices = sorted(range(len(probs)), key=lambda index: (-float(probs[index]), index))
    target_attention = 0.5 * (float(attention_1[row.target_pos]) + float(attention_2[row.target_pos]))
    return float(probs[row.label_token]), int(sorted_indices.index(row.label_token) + 1), float(probs[sorted_indices[0]]), target_attention


def evaluate_attention_supervised_two_block(rows: list[Stage10Example], method_name: str, vector: Any) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    target_attentions: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence, target_attention = _predict(vector, row, method_name)
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probs.append(target_probability)
        top1_confidences.append(top1_confidence)
        target_attentions.append(target_attention)
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
        "mean_target_attention": round(float(np.mean(target_attentions)), 6),
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
        f"{split}_mean_target_attention",
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
                ci = _bootstrap_ci(values, seed_text=f"stage54:{task_name}:{method_name}:{metric_name}")
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
            row[f"{split}_mean_target_attention_mean"],
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
    attention_repaired = [
        task for task, row in retrieval_best.items() if row["test_mean_target_attention_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_retrieval_generalized = [
        task for task in retrieval_generalized if retrieval_best[task]["method"].startswith("phasewrap")
    ]
    if retrieval_generalized:
        decision = "ATTENTION_SUPERVISED_RETRIEVAL_GENERALIZATION_PRESENT_REVIEW_REQUIRED"
        boundary = "Target-attention supervision produced at least one held-out retrieval lane above top-1 threshold; review method ordering before any claim update."
    elif attention_repaired:
        decision = "ATTENTION_REPAIRED_VALUE_OUTPUT_FAILED"
        boundary = "Target-attention supervision repairs attention mass for at least one retrieval lane, but learned value output still fails top-1."
    else:
        decision = "ATTENTION_SUPERVISION_RETRIEVAL_REPAIR_FAILED"
        boundary = "Target-attention supervision does not establish retrieval generalization or attention repair."
    tiny_best = _best_row(aggregate_table, task_name=TINY_TEXT_TASK)
    return {
        "decision": decision,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "attention_repair_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "retrieval_generalized_tasks": retrieval_generalized,
        "attention_repaired_tasks": attention_repaired,
        "phasewrap_retrieval_generalized_tasks": phasewrap_retrieval_generalized,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "retrieval_best_target_attention": {task: row["test_mean_target_attention_mean"] for task, row in retrieval_best.items()},
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
        "claim_boundary": boundary,
    }


def run_stage54_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    attention_aux_weight: float = DEFAULT_ATTENTION_AUX_WEIGHT,
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
                    trained = train_attention_supervised_two_block_decoder(
                        train_rows,
                        stage10_method,
                        seed=seed,
                        epochs=epochs,
                        learning_rate=learning_rate,
                        attention_aux_weight=attention_aux_weight,
                    )
                    row: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": stage10_method,
                        "epochs": epochs,
                        "learning_rate": learning_rate,
                        "attention_aux_weight": attention_aux_weight,
                        "optimizer": trained["optimizer"],
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "final_training_loss": trained["final_training_loss"],
                        "learned_position_scale": trained["learned_position_scale"],
                        "training_history": trained["training_history"],
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_attention_supervised_two_block(split_rows, stage10_method, trained["weights"])
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
                except Exception as exc:  # pragma: no cover - retained for artifact completeness.
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _aggregate(run_table, failed_runs)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (
            row["task"],
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            row["test_mean_target_attention_mean"],
            row["method"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE54_SCHEMA_VERSION,
        "stage": "stage54_attention_supervised_two_block_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10/stage45 matched decoder-only rows",
        "source_stage": "stage53_two_block_retrieval_hardening_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "attention_aux_weight": attention_aux_weight,
        "model": {
            "type": "target_attention_supervised_two_block_residual_decoder",
            "model_dim": MODEL_DIM,
            "vocab_size": VOCAB_SIZE,
            "optimizer": "full_batch_adam",
            "trained_parameters": "token embeddings, two q/k/v/o attention blocks, vocab output projection, positional scale",
            "value_output_mode": "learned vocab softmax, no fixed copy output",
            "auxiliary_loss": "target-position attention negative log likelihood on both attention blocks",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage54_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage54_summary(result: dict[str, Any]) -> None:
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
        "train_mean_target_attention_mean",
        "test_mean_target_attention_mean",
        "test_top1_accuracy_mean",
        "test_mean_target_probability_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
