from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, Stage10Example, make_stage10_splits
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS, TINY_TEXT_TASK
from .stage55_row_metadata_cue_copy_upper_bound_audit import (
    DEFAULT_CUE_SCALES,
    DEFAULT_DISTANCE_SCALES,
    DEFAULT_POSITION_SCALES,
    _aggregate,
    _best_row,
)
from .stage56_standard_input_cue_copy_audit import DEFAULT_EXAMPLES_PER_LENGTH, write_stage56_outputs
from .stage57_support_aware_query_cue_audit import print_stage57_summary
from .stage58_pooled_train_query_support_audit import (
    _query_mod,
    _select_scales,
    evaluate_pooled_train_query_support,
    learn_query_support_map,
)


STAGE74_SCHEMA_VERSION = "qrope_stage74_leave_one_seed_query_support_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage74_leave_one_seed_query_support_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential leave-one-seed-out visible query-support diagnostic over original Stage10 rows.",
            "Evidence about whether phase-cued support can be recovered from other seeds' standard train rows.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap reporting with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a leave-one-seed lookup is a matched decoder-only transformer",
            "a claim that cross-seed query-support recovery is positional-method promotion evidence",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "unexpected_preflight_block") -> dict[str, Any]:
    return {
        "schema_version": STAGE74_SCHEMA_VERSION,
        "stage": "stage74_leave_one_seed_query_support_audit",
        "status": "blocked",
        "blocked_reason": reason,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_AUDIT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def _support_coverage(rows: list[Stage10Example], learned_support: dict[int, int]) -> dict[str, Any]:
    query_mods = [_query_mod(row) for row in rows]
    known = [query_mod for query_mod in query_mods if query_mod in learned_support]
    return {
        "row_count": len(rows),
        "known_count": len(known),
        "known_fraction": round(float(len(known) / len(rows)), 6) if rows else 0.0,
        "query_mods": sorted(set(query_mods)),
        "known_query_mods": sorted(set(known)),
        "missing_query_mods": sorted(set(query_mods) - set(learned_support)),
    }


def _decision(aggregate_table: list[dict[str, Any]], *, phase_cued_test_coverage: dict[str, dict[str, Any]]) -> dict[str, Any]:
    retrieval_best = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_solved = [task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD]
    no_position_solved = [
        task
        for task in RETRIEVAL_TASKS
        for row in aggregate_table
        if row["task"] == task and row["method"] == "no_position" and row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_best = [task for task, row in retrieval_best.items() if row["method"].startswith("phasewrap")]
    mean_phase_cued_coverage = round(float(np.mean([coverage["known_fraction"] for coverage in phase_cued_test_coverage.values()])), 6)
    if "phase_cued_retrieval" in retrieval_solved and "phase_cued_retrieval" in no_position_solved:
        decision = "LEAVE_ONE_SEED_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION"
        boundary = "Cross-seed visible query-support recovery solves phase-cued retrieval for no-position too; this is not positional-method promotion."
    elif retrieval_solved:
        decision = "LEAVE_ONE_SEED_QUERY_SUPPORT_PARTIAL_RETRIEVAL"
        boundary = "Cross-seed visible query-support recovery solves at least one retrieval lane but not the full retrieval set."
    else:
        decision = "LEAVE_ONE_SEED_QUERY_SUPPORT_RETRIEVAL_FAILED"
        boundary = "Cross-seed visible query-support recovery does not solve retrieval."
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
        "mean_phase_cued_test_support_coverage": mean_phase_cued_coverage,
        "claim_boundary": boundary,
    }


def run_stage74_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
    position_scales: tuple[float, ...] = DEFAULT_POSITION_SCALES,
    cue_scales: tuple[float, ...] = DEFAULT_CUE_SCALES,
    distance_scales: tuple[float, ...] = DEFAULT_DISTANCE_SCALES,
) -> dict[str, Any]:
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    support_maps: dict[str, dict[str, int]] = {}
    phase_cued_test_coverage: dict[str, dict[str, Any]] = {}
    for held_out_seed in seeds:
        cross_seed_train_rows = [
            row
            for splits in splits_by_task.values()
            for row in splits["train"]
            if row.seed != held_out_seed
        ]
        learned_support = learn_query_support_map(cross_seed_train_rows)
        support_maps[str(held_out_seed)] = {str(key): value for key, value in learned_support.items()}
        phase_test_rows = [
            row
            for row in splits_by_task["phase_cued_retrieval"]["test"]
            if row.seed == held_out_seed
        ]
        phase_cued_test_coverage[str(held_out_seed)] = _support_coverage(phase_test_rows, learned_support)
        for task_name, splits in splits_by_task.items():
            train_rows = [row for row in splits["train"] if row.seed == held_out_seed]
            validation_rows = [row for row in splits["validation"] if row.seed == held_out_seed]
            test_rows = [row for row in splits["test"] if row.seed == held_out_seed]
            for method_name in method_names:
                try:
                    selected = _select_scales(
                        validation_rows,
                        method_name,
                        learned_support=learned_support,
                        position_scales=position_scales,
                        cue_scales=cue_scales,
                        distance_scales=distance_scales,
                    )
                    row: dict[str, Any] = {
                        "task": task_name,
                        "seed": held_out_seed,
                        "method": method_name,
                        "stage10_method_alias": _stage10_method_name(method_name),
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "leave_one_seed_support_size": len(learned_support),
                        "test_support_known_fraction": (
                            phase_cued_test_coverage[str(held_out_seed)]["known_fraction"]
                            if task_name == "phase_cued_retrieval"
                            else 1.0
                        ),
                        **selected,
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_pooled_train_query_support(
                            split_rows,
                            method_name,
                            learned_support=learned_support,
                            position_scale=selected["selected_position_scale"],
                            cue_scale=selected["selected_cue_scale"],
                            distance_scale=selected["selected_distance_scale"],
                        )
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
                except Exception as exc:  # pragma: no cover
                    failed_runs.append({"task": task_name, "seed": held_out_seed, "method": method_name, "error": str(exc)})
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
        "schema_version": STAGE74_SCHEMA_VERSION,
        "stage": "stage74_leave_one_seed_query_support_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_original_rows_leave_one_seed_query_support_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage73_phase_cued_period_pair_support_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "leave_one_seed_support_maps": support_maps,
        "phase_cued_test_support_coverage": phase_cued_test_coverage,
        "model": {
            "type": "leave_one_seed_query_token_support_lookup_copy_diagnostic",
            "value_output_mode": "deterministic copied prefix-token mass",
            "metadata_excluded": ["held-out seed train rows", "row.reference_delta exact value at evaluation", "row.target_pos", "row.target_delta"],
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table, phase_cued_test_coverage=phase_cued_test_coverage),
    }


def write_stage74_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage56_outputs(result, output_dir)


def print_stage74_summary(result: dict[str, Any]) -> None:
    print_stage57_summary(result)
