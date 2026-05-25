from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, TEXT_TOKEN_IDS, VOCAB_SIZE, Stage10Example, autograd_available, make_stage10_splits, positional_bias
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage50_learned_pointer_generator_decoder_audit import _copy_indicator
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS, TINY_TEXT_TASK
from .stage55_row_metadata_cue_copy_upper_bound_audit import _aggregate, _best_row
from .stage56_standard_input_cue_copy_audit import DEFAULT_EXAMPLES_PER_LENGTH, write_stage56_outputs
from .stage57_support_aware_query_cue_audit import print_stage57_summary
from .stage58_pooled_train_query_support_audit import _query_mod


STAGE76_SCHEMA_VERSION = "qrope_stage76_integrated_support_copy_head_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage76_integrated_support_copy_head_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
DEFAULT_EPOCHS = 220
DEFAULT_LEARNING_RATE = 0.08


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential same-seed integrated learned support/copy-head audit over original Stage10 rows.",
            "Evidence about whether visible query-support recovery can be optimized through the copy-readout loss instead of pretrained as a standalone classifier.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap reporting with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap replaces RoPE",
            "a claim that this compact copy-head is a matched decoder-only transformer",
            "a claim that support/copy recovery is positional-method promotion evidence when no-position solves too",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    return {
        "schema_version": STAGE76_SCHEMA_VERSION,
        "stage": "stage76_integrated_support_copy_head_audit",
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


def _support_classes(rows: list[Stage10Example]) -> tuple[int, ...]:
    values = sorted({int(row.reference_delta) for row in rows if row.task == "phase_cued_retrieval"})
    if not values:
        raise ValueError("integrated support copy head requires phase_cued_retrieval train rows")
    return tuple(values)


def _support_features(row: Stage10Example) -> np.ndarray:
    features = np.zeros(17, dtype=float)
    features[_query_mod(row)] = 1.0
    features[-1] = 1.0
    return features


def _init_vector(classes: tuple[int, ...]) -> np.ndarray:
    weights = np.zeros((17, len(classes)), dtype=float)
    scales = np.array([0.0, 1.0, 1.0], dtype=float)
    return np.concatenate([weights.ravel(), scales])


def _unpack(vector: Any, class_count: int):
    import autograd.numpy as anp

    support_size = 17 * class_count
    weights = anp.reshape(vector[:support_size], (17, class_count))
    return weights, vector[support_size], vector[support_size + 1], vector[support_size + 2]


def _softmax(values: Any):
    import autograd.numpy as anp

    shifted = values - anp.max(values)
    exp_values = anp.exp(shifted)
    return exp_values / anp.sum(exp_values)


def _content_cue_logits(row: Stage10Example):
    import autograd.numpy as anp

    logits = np.zeros(row.query_pos, dtype=float)
    query_tokens = row.tokens[max(0, row.query_pos - 4) : row.query_pos + 1]
    entity_ids = [token for token in query_tokens if 87 <= token < 96]
    if not entity_ids:
        return anp.array(logits)
    entity_id = int(entity_ids[0])
    for index in range(3, row.query_pos):
        if (
            row.tokens[index - 3] == TEXT_TOKEN_IDS["fact"]
            and row.tokens[index - 2] == entity_id
            and row.tokens[index - 1] == TEXT_TOKEN_IDS["is"]
        ):
            logits[index] = 1.0
    return anp.array(logits)


def _support_scores(row: Stage10Example, support_weights: Any, classes: tuple[int, ...]):
    import autograd.numpy as anp

    distances = np.array([row.query_pos - index for index in range(row.query_pos)], dtype=float)
    features = anp.array(_support_features(row))
    support_distribution = _softmax(anp.dot(features, support_weights))
    scores = anp.zeros(row.query_pos)
    for class_index, reference_delta in enumerate(classes):
        exact_distance = anp.array((distances == float(reference_delta)).astype(float))
        phase_congruent = anp.array((((distances - float(reference_delta)) % 24.0) == 0.0).astype(float))
        scores = scores + support_distribution[class_index] * (exact_distance + phase_congruent)
    return scores


def _row_probabilities(vector: Any, row: Stage10Example, method_name: str, classes: tuple[int, ...]):
    import autograd.numpy as anp

    support_weights, position_scale, cue_scale, distance_scale = _unpack(vector, len(classes))
    distances = anp.array([row.query_pos - index for index in range(row.query_pos)], dtype=float)
    logits = position_scale * anp.array(positional_bias(row, method_name))
    if row.task == TINY_TEXT_TASK:
        logits = logits + cue_scale * _content_cue_logits(row)
    else:
        logits = logits + cue_scale * _support_scores(row, support_weights, classes)
    logits = logits + distance_scale * distances / max(1.0, float(row.query_pos))
    attention = _softmax(logits)
    return anp.dot(attention, _copy_indicator(row))


def _row_loss(vector: Any, row: Stage10Example, method_name: str, classes: tuple[int, ...]):
    import autograd.numpy as anp

    probabilities = _row_probabilities(vector, row, method_name, classes)
    return -anp.log(probabilities[row.label_token] + 1e-12)


def _batch_loss(vector: Any, rows: list[Stage10Example], method_name: str, classes: tuple[int, ...]):
    import autograd.numpy as anp

    return anp.mean(anp.array([_row_loss(vector, row, method_name, classes) for row in rows]))


def train_integrated_support_copy_head(
    rows: list[Stage10Example],
    method_name: str,
    *,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
) -> dict[str, Any]:
    from autograd import grad

    classes = _support_classes(rows)
    vector = _init_vector(classes)
    gradient = grad(lambda current: _batch_loss(current, rows, method_name, classes))
    moment = np.zeros_like(vector)
    velocity = np.zeros_like(vector)
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss_value = float(_batch_loss(vector, rows, method_name, classes))
        grad_value = gradient(vector)
        moment = beta1 * moment + (1.0 - beta1) * grad_value
        velocity = beta2 * velocity + (1.0 - beta2) * (grad_value * grad_value)
        moment_hat = moment / (1.0 - beta1**epoch)
        velocity_hat = velocity / (1.0 - beta2**epoch)
        vector = vector - learning_rate * moment_hat / (np.sqrt(velocity_hat) + epsilon)
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            history.append({"epoch": epoch, "loss": round(loss_value, 6)})
    support_weights, position_scale, cue_scale, distance_scale = _unpack(vector, len(classes))
    return {
        "weights": vector,
        "classes": classes,
        "optimizer": "full_batch_adam",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "learned_position_scale": round(float(position_scale), 6),
        "learned_cue_scale": round(float(cue_scale), 6),
        "learned_distance_scale": round(float(distance_scale), 6),
        "support_weight_norm": round(float(np.linalg.norm(np.asarray(support_weights, dtype=float))), 6),
    }


def _predict(vector: Any, row: Stage10Example, method_name: str, classes: tuple[int, ...]) -> tuple[float, int, float]:
    probabilities = np.asarray(_row_probabilities(vector, row, method_name, classes), dtype=float)
    sorted_indices = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    return float(probabilities[row.label_token]), int(sorted_indices.index(row.label_token) + 1), float(probabilities[sorted_indices[0]])


def evaluate_integrated_support_copy_head(rows: list[Stage10Example], method_name: str, model: dict[str, Any]) -> dict[str, float]:
    from .stage49_copy_decoder_retrieval_repair_audit import _expected_calibration_error

    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence = _predict(model["weights"], row, method_name, model["classes"])
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probs.append(target_probability)
        top1_confidences.append(top1_confidence)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": float(len(rows)),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(np.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
    }


def _support_head_accuracy(rows: list[Stage10Example], model: dict[str, Any]) -> dict[str, float]:
    support_rows = [row for row in rows if row.task == "phase_cued_retrieval"]
    if not support_rows:
        return {"row_count": 0.0, "accuracy": 0.0}
    support_weights, _, _, _ = _unpack(model["weights"], len(model["classes"]))
    hits: list[float] = []
    for row in support_rows:
        probabilities = np.asarray(_softmax(np.dot(_support_features(row), np.asarray(support_weights, dtype=float))), dtype=float)
        predicted = int(model["classes"][int(np.argmax(probabilities))])
        hits.append(1.0 if predicted == int(row.reference_delta) else 0.0)
    return {"row_count": float(len(support_rows)), "accuracy": round(float(np.mean(hits)), 6)}


def _decision(aggregate_table: list[dict[str, Any]], *, support_summary: dict[str, dict[str, float]]) -> dict[str, Any]:
    retrieval_best = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_solved = [task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD]
    no_position_solved = [
        task
        for task in RETRIEVAL_TASKS
        for row in aggregate_table
        if row["task"] == task and row["method"] == "no_position" and row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_best = [task for task, row in retrieval_best.items() if row["method"].startswith("phasewrap")]
    mean_support_accuracy = round(float(np.mean([row["phase_cued_test_support_accuracy"] for row in support_summary.values()])), 6)
    if "phase_cued_retrieval" in retrieval_solved and "phase_cued_retrieval" in no_position_solved:
        decision = "INTEGRATED_SUPPORT_COPY_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION"
        boundary = "An integrated learned support/copy head solves phase-cued retrieval for no-position too; this is not positional-method promotion."
    elif retrieval_solved:
        decision = "INTEGRATED_SUPPORT_COPY_HEAD_PARTIAL_RETRIEVAL"
        boundary = "An integrated learned support/copy head solves at least one retrieval lane but not the full retrieval set."
    else:
        decision = "INTEGRATED_SUPPORT_COPY_HEAD_RETRIEVAL_FAILED"
        boundary = "An integrated learned support/copy head does not solve retrieval."
    tiny_best = _best_row(aggregate_table, task_name=TINY_TEXT_TASK)
    return {
        "decision": decision,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "retrieval_solved_tasks": retrieval_solved,
        "no_position_solved_retrieval_tasks": no_position_solved,
        "phasewrap_best_retrieval_tasks": phasewrap_best,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "retrieval_best_target_probability": {task: row["test_mean_target_probability_mean"] for task, row in retrieval_best.items()},
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
        "mean_phase_cued_test_support_accuracy": mean_support_accuracy,
        "claim_boundary": boundary,
    }


def _serializable_model(model: dict[str, Any]) -> dict[str, Any]:
    return {
        "classes": list(model["classes"]),
        "optimizer": model["optimizer"],
        "epochs": model["epochs"],
        "learning_rate": model["learning_rate"],
        "training_history": model["training_history"],
        "final_training_loss": model["final_training_loss"],
        "learned_position_scale": model["learned_position_scale"],
        "learned_cue_scale": model["learned_cue_scale"],
        "learned_distance_scale": model["learned_distance_scale"],
        "support_weight_norm": model["support_weight_norm"],
        "weights": np.asarray(model["weights"], dtype=float).round(8).tolist(),
    }


def run_stage76_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    models: dict[str, dict[str, Any]] = {}
    support_summary: dict[str, dict[str, float]] = {}
    for seed in seeds:
        train_rows_all = [row for splits in splits_by_task.values() for row in splits["train"] if row.seed == seed]
        phase_test_rows = [row for row in splits_by_task["phase_cued_retrieval"]["test"] if row.seed == seed]
        for method_name in method_names:
            try:
                model = train_integrated_support_copy_head(
                    train_rows_all,
                    _stage10_method_name(method_name),
                    epochs=epochs,
                    learning_rate=learning_rate,
                )
                model_key = f"{seed}:{method_name}"
                models[model_key] = _serializable_model(model)
                support_summary[model_key] = {
                    "phase_cued_test_support_accuracy": _support_head_accuracy(phase_test_rows, model)["accuracy"],
                    "final_training_loss": model["final_training_loss"],
                }
                for task_name, splits in splits_by_task.items():
                    train_rows = [row for row in splits["train"] if row.seed == seed]
                    validation_rows = [row for row in splits["validation"] if row.seed == seed]
                    test_rows = [row for row in splits["test"] if row.seed == seed]
                    run: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": _stage10_method_name(method_name),
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "support_class_count": len(model["classes"]),
                        "support_head_test_accuracy": support_summary[model_key]["phase_cued_test_support_accuracy"] if task_name == "phase_cued_retrieval" else 1.0,
                        "selected_position_scale": model["learned_position_scale"],
                        "selected_cue_scale": model["learned_cue_scale"],
                        "selected_distance_scale": model["learned_distance_scale"],
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_integrated_support_copy_head(split_rows, _stage10_method_name(method_name), model)
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                run[f"{split_name}_{metric_name}"] = value
                    run_table.append(run)
            except Exception as exc:  # pragma: no cover
                for task_name in TASK_NAMES:
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _aggregate(run_table, failed_runs)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (
            row["task"],
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            row["method"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE76_SCHEMA_VERSION,
        "stage": "stage76_integrated_support_copy_head_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_original_rows_same_seed_integrated_support_copy_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage75_learned_query_support_head_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "models": models,
        "support_summary": support_summary,
        "model": {
            "type": "same_seed_end_to_end_support_copy_head",
            "value_output_mode": "deterministic copied prefix-token mass",
            "metadata_excluded": ["hard query-support lookup", "standalone pretrained support head", "row.reference_delta exact value at evaluation", "row.target_pos", "row.target_delta"],
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table, support_summary=support_summary),
    }


def write_stage76_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage56_outputs(result, output_dir)


def print_stage76_summary(result: dict[str, Any]) -> None:
    print_stage57_summary(result)
