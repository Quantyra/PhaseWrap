from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

from qrope.stage100_matched_cx_encoding_packet_freezer import _cx_matched_row
from qrope.stage153_simulated_noise_rehearsal import (
    DEFAULT_NOISE_MODELS,
    ENCODING_FAMILIES,
    POSITIONAL_COMPARATOR_FAMILIES,
    STRICT_COMPARATOR_FAMILIES,
    _comparison_summary,
    _simulated_execution,
)
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import _matched_row, _max_abs_delta, _stable_hash
from qrope.stage103_robustness_metric_preregistration import packet_metrics


STAGE167_SCHEMA_VERSION = "qrope_stage167_expanded_simulated_seed_stress_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage167_expanded_simulated_seed_stress_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
DEFAULT_SYNTHETIC_SEEDS: tuple[int, ...] = (314, 577, 1618, 2718)
DEFAULT_ROW_COUNT = 16
DEFAULT_SHOT_COUNT = 4096
MIN_MARGIN_SHOT_QUANTA = 2.0
MIN_STABLE_SEED_COUNT_FOR_EXPANDED_SIGNAL = 2
MIN_STABLE_NOISE_MODEL_COUNT_FOR_EXPANDED_SIGNAL = 2
MIN_STABLE_TEMPLATE_COUNT_FOR_EXPANDED_SIGNAL = 2


def _source_rows(seed: int, row_count: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows = []
    quadrants = ("00", "01", "10", "11")
    for index in range(row_count):
        reference_delta = rng.randint(-64, 64)
        candidate_delta = rng.randint(-64, 64)
        source = {
            "seed": seed,
            "context_id": f"synthetic_s{seed}_r{index:03d}",
            "slot": index,
            "split": "synthetic_simulated_stress",
            "quadrant": quadrants[index % len(quadrants)],
            "reference_delta": reference_delta,
            "candidate_delta": candidate_delta,
            "text": f"synthetic seed:{seed} row:{index} ref_delta:{reference_delta} cand_delta:{candidate_delta}",
        }
        core = {"row_id": f"simrow-{index:03d}", "source": source}
        rows.append({**core, "row_hash": _stable_hash(core)})
    return rows


def _packet(seed: int, family: str, circuit_template: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    max_delta = _max_abs_delta(rows)
    if circuit_template == "two_ry_cx_parity_z_readout_v1":
        matched_rows = [_cx_matched_row(row, family, max_delta) for row in rows]
    else:
        matched_rows = [_matched_row(row, family, max_delta) for row in rows]
    lane_kind = "cx" if circuit_template == "two_ry_cx_parity_z_readout_v1" else "product"
    lane_id = f"ibm_{lane_kind}_seed{seed}_rows{len(rows)}_shots{DEFAULT_SHOT_COUNT}_synthetic"
    packet_core = {
        "schema_version": STAGE167_SCHEMA_VERSION,
        "packet_version": "qrope_stage167_synthetic_matched_packet_v1",
        "packet_id": f"{lane_id}__{family}",
        "source_stage": "stage167_expanded_simulated_seed_stress_audit",
        "source_lane_id": lane_id,
        "encoding_family": family,
        "provider": "ibm_runtime",
        "backend": "simulated_ibm_fixed_width",
        "row_count": len(matched_rows),
        "shot_count": DEFAULT_SHOT_COUNT,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "execution_status": "simulated_only",
        "fixed_width": {
            "measured_qubits": 2,
            "active_qubits": 2,
            "readout": "computational_basis",
            "circuit_template": circuit_template,
            "entangling_gate": "cx q0->q1" if circuit_template == "two_ry_cx_parity_z_readout_v1" else None,
        },
        "rows": matched_rows,
    }
    return {**packet_core, "packet_hash": _stable_hash(packet_core)}


def _metric_records(
    *,
    seeds: tuple[int, ...],
    row_count: int,
    noise_models: tuple[dict[str, Any], ...],
) -> list[dict[str, Any]]:
    records = []
    for seed in seeds:
        rows = _source_rows(seed, row_count)
        for circuit_template in ("two_ry_product_state_z_readout_v1", "two_ry_cx_parity_z_readout_v1"):
            for family in ENCODING_FAMILIES:
                packet = _packet(seed, family, circuit_template, rows)
                for noise_model in noise_models:
                    execution = _simulated_execution(packet, noise_model)
                    record = packet_metrics(packet, execution)
                    records.append(
                        {
                            **record,
                            "seed": seed,
                            "noise_model_id": noise_model["noise_model_id"],
                            "noise_family": noise_model["noise_family"],
                            "readout_bitflip_probability": noise_model["readout_bitflip_probability"],
                            "depolarizing_observable_shrink": noise_model["depolarizing_observable_shrink"],
                            "ry_angle_scale_error": noise_model["ry_angle_scale_error"],
                            "ry_angle_offset_radians": noise_model["ry_angle_offset_radians"],
                            "observable_bias_component_a": noise_model["observable_bias_component_a"],
                            "observable_bias_component_b": noise_model["observable_bias_component_b"],
                            "simulated_only": True,
                        }
                    )
    return records


def _enriched_comparison_summary(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries = _comparison_summary(records)
    seed_by_lane = {str(record.get("source_lane_id")): record.get("seed") for record in records}
    noise_family_by_id = {str(record.get("noise_model_id")): record.get("noise_family") for record in records}
    for summary in summaries:
        positional_margin = None
        control_margin = None
        if summary.get("phasewrap_mean_absolute_score_error") is not None:
            if summary.get("best_positional_comparator_mean_absolute_score_error") is not None:
                positional_margin = round(
                    float(summary["best_positional_comparator_mean_absolute_score_error"])
                    - float(summary["phasewrap_mean_absolute_score_error"]),
                    12,
                )
            if summary.get("no_position_control_mean_absolute_score_error") is not None:
                control_margin = round(
                    float(summary["no_position_control_mean_absolute_score_error"])
                    - float(summary["phasewrap_mean_absolute_score_error"]),
                    12,
                )
        shot_quantum = 1.0 / DEFAULT_SHOT_COUNT
        positional_quanta = positional_margin / shot_quantum if positional_margin is not None else None
        control_quanta = control_margin / shot_quantum if control_margin is not None else None
        stable = bool(
            summary.get("phasewrap_beats_all_families_including_control") is True
            and positional_quanta is not None
            and control_quanta is not None
            and positional_quanta >= MIN_MARGIN_SHOT_QUANTA
            and control_quanta >= MIN_MARGIN_SHOT_QUANTA
        )
        summary.update(
            {
                "seed": seed_by_lane.get(str(summary.get("source_lane_id"))),
                "noise_family": noise_family_by_id.get(str(summary.get("noise_model_id"))),
                "positional_margin": positional_margin,
                "control_margin": control_margin,
                "shot_quantum": shot_quantum,
                "positional_margin_shot_quanta": round(positional_quanta, 6) if positional_quanta is not None else None,
                "control_margin_shot_quanta": round(control_quanta, 6) if control_quanta is not None else None,
                "stable_strict_target": stable,
            }
        )
    return summaries


def _seed_records(comparison_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seeds = sorted({int(record.get("seed")) for record in comparison_summary if record.get("seed") is not None})
    records = []
    for seed in seeds:
        seed_records = [record for record in comparison_summary if record.get("seed") == seed]
        stable = [record for record in seed_records if record.get("stable_strict_target") is True]
        records.append(
            {
                "seed": seed,
                "comparison_group_count": len(seed_records),
                "stable_target_count": len(stable),
                "stable_template_count": len({str(record.get("circuit_template")) for record in stable}),
                "stable_noise_model_count": len({str(record.get("noise_model_id")) for record in stable}),
                "stable_noise_models": sorted({str(record.get("noise_model_id")) for record in stable}),
                "stable_templates": sorted({str(record.get("circuit_template")) for record in stable}),
            }
        )
    return records


def run_stage167_expanded_seed_stress_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_SYNTHETIC_SEEDS,
    row_count: int = DEFAULT_ROW_COUNT,
    shot_count: int = DEFAULT_SHOT_COUNT,
    noise_models: tuple[dict[str, Any], ...] = DEFAULT_NOISE_MODELS,
) -> dict[str, Any]:
    if shot_count != DEFAULT_SHOT_COUNT:
        raise ValueError("Stage167 currently uses the preregistered IBM 4096-shot simulation quantum")
    metric_records = _metric_records(seeds=seeds, row_count=row_count, noise_models=noise_models)
    comparison_summary = _enriched_comparison_summary(metric_records)
    stable_targets = [record for record in comparison_summary if record.get("stable_strict_target") is True]
    stable_seed_count = len({int(record["seed"]) for record in stable_targets})
    stable_noise_model_count = len({str(record["noise_model_id"]) for record in stable_targets})
    stable_template_count = len({str(record["circuit_template"]) for record in stable_targets})
    expanded_signal_ready = bool(
        stable_seed_count >= MIN_STABLE_SEED_COUNT_FOR_EXPANDED_SIGNAL
        and stable_noise_model_count >= MIN_STABLE_NOISE_MODEL_COUNT_FOR_EXPANDED_SIGNAL
        and stable_template_count >= MIN_STABLE_TEMPLATE_COUNT_FOR_EXPANDED_SIGNAL
    )
    decision = (
        "EXPANDED_SIMULATED_SEED_STRESS_SUPPORTS_BROADENED_HARDWARE_PROBE"
        if expanded_signal_ready
        else "EXPANDED_SIMULATED_SEED_STRESS_DOES_NOT_SUPPORT_BROADENED_HARDWARE_PROBE"
    )
    return {
        "schema_version": STAGE167_SCHEMA_VERSION,
        "stage": "stage167_expanded_simulated_seed_stress_audit",
        "status": "completed",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [],
        "synthetic_seeds": list(seeds),
        "row_count_per_seed": row_count,
        "shot_count": shot_count,
        "noise_model_count": len(noise_models),
        "metric_record_count": len(metric_records),
        "comparison_group_count": len(comparison_summary),
        "stable_target_count": len(stable_targets),
        "stable_seed_count": stable_seed_count,
        "stable_noise_model_count": stable_noise_model_count,
        "stable_template_count": stable_template_count,
        "seed_records": _seed_records(comparison_summary),
        "metric_records": metric_records,
        "comparison_summary": comparison_summary,
        "stability_thresholds": {
            "min_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_stable_seed_count_for_expanded_signal": MIN_STABLE_SEED_COUNT_FOR_EXPANDED_SIGNAL,
            "min_stable_noise_model_count_for_expanded_signal": MIN_STABLE_NOISE_MODEL_COUNT_FOR_EXPANDED_SIGNAL,
            "min_stable_template_count_for_expanded_signal": MIN_STABLE_TEMPLATE_COUNT_FOR_EXPANDED_SIGNAL,
        },
        "simulated_only": True,
        "synthetic_rows_only": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "expanded simulated-only stress over independent synthetic row seeds using the Stage99/100 fixed-width formulas",
                "shot-resolution-stable strict advantage counts across seeds, noise models, and fixed-width templates",
                "pre-hardware screening of whether the Stage165 IBM signal generalizes beyond one frozen source seed",
            ],
            "excluded": [
                "real noisy-hardware evidence",
                "provider credit or queue availability validation",
                "hardware job submission",
                "a publication-ready noisy-hardware robustness or auditability conclusion",
                "evidence from real Stage4 source rows beyond the frozen seed314 and seed2718 packets",
            ],
        },
        "next_gate": (
            "If expanded simulation is supportive, keep the IBM run scoped as a targeted probe and resolve credit/provider state "
            "before hardware. If not, add real frozen source seeds before live spend."
        ),
    }


def write_stage167_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "synthetic_seeds": result["synthetic_seeds"],
        "row_count_per_seed": result["row_count_per_seed"],
        "shot_count": result["shot_count"],
        "noise_model_count": result["noise_model_count"],
        "comparison_group_count": result["comparison_group_count"],
        "stable_target_count": result["stable_target_count"],
        "stable_seed_count": result["stable_seed_count"],
        "stable_noise_model_count": result["stable_noise_model_count"],
        "stable_template_count": result["stable_template_count"],
        "stability_thresholds": result["stability_thresholds"],
        "simulated_only": result["simulated_only"],
        "synthetic_rows_only": result["synthetic_rows_only"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "seed",
                "noise_model_id",
                "noise_family",
                "circuit_template",
                "phasewrap_mean_absolute_score_error",
                "best_positional_comparator_mean_absolute_score_error",
                "no_position_control_mean_absolute_score_error",
                "positional_margin_shot_quanta",
                "control_margin_shot_quanta",
                "stable_strict_target",
            ),
        )
        writer.writeheader()
        for record in result["comparison_summary"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage167_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"stable_target_count: {result['stable_target_count']}")
    print(f"stable_seed_count: {result['stable_seed_count']}")
    print(f"stable_noise_model_count: {result['stable_noise_model_count']}")
    print(f"stable_template_count: {result['stable_template_count']}")
    print(f"next_gate: {result['next_gate']}")
