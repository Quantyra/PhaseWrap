from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path
from typing import Any

from qrope.stage100_matched_cx_encoding_packet_freezer import DEFAULT_SOURCE_PACKET_FILES as CX_SOURCE_PACKET_FILES, _openqasm3
from qrope.stage153_simulated_noise_rehearsal import _noisy_components
from qrope.stage177_ibm_backend_informed_noise_probe import DEFAULT_OUTPUT_DIR as STAGE177_OUTPUT_DIR, PRIMARY_MODEL_IDS
from qrope.stage187_replacement_semantics_preregistration import DEFAULT_OUTPUT_DIR as STAGE187_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import (
    DEFAULT_SOURCE_PACKET_DIR,
    DEFAULT_SOURCE_PACKET_FILES as PRODUCT_SOURCE_PACKET_FILES,
    OBJECTIVE,
    SourceLane,
    _clamp,
    _components_for_family,
    _load_source_lanes,
    _max_abs_delta,
    _round_float,
    _row_delta,
    _source_packet_paths,
    _stable_hash,
)


STAGE188_SCHEMA_VERSION = "qrope_stage188_replacement_semantics_packet_screen_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE177_RESULTS = STAGE177_OUTPUT_DIR / "results.json"
DEFAULT_STAGE187_RESULTS = STAGE187_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage188_replacement_semantics_packet_screen"
STAGE187_READY = "REPLACEMENT_SEMANTICS_PREREGISTERED_READY_FOR_PACKET_SCREEN"
SEMANTICS_ID = "matched_nonzero_null_noise_sensitivity_v1"
PRODUCT_TEMPLATE = "two_ry_product_state_z_readout_v1"
CX_TEMPLATE = "two_ry_cx_parity_z_readout_v1"
SOURCE_LANE_RE = re.compile(r"^(?P<provider>.+?)_(?P<template>product|cx)_seed(?P<seed>\d+)_")
ENCODING_FAMILIES: tuple[str, ...] = (
    "phasewrap",
    "rope_like",
    "sinusoidal_like",
    "alibi_like",
    "matched_nonzero_null_control",
)
POSITIONAL_FAMILIES: tuple[str, ...] = ("rope_like", "sinusoidal_like", "alibi_like")


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _primary_noise_models(stage177: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(
        model
        for model in stage177.get("noise_models", [])
        if isinstance(model, dict) and str(model.get("noise_model_id")) in PRIMARY_MODEL_IDS
    )


def _hash_sign(value: str) -> float:
    return 1.0 if int(_stable_hash(value)[:2], 16) % 2 == 0 else -1.0


def _nonzero(value: float, floor: float = 0.125) -> float:
    magnitude = max(floor, min(1.0, abs(float(value))))
    return math.copysign(magnitude, value if value != 0.0 else 1.0)


def _components_for_replacement_family(family: str, source_row: dict[str, Any], max_abs_delta: float) -> tuple[float, float]:
    delta = _row_delta(source_row)
    if family == "matched_nonzero_null_control":
        phase_a, phase_b = _components_for_family("phasewrap", delta, max_abs_delta)
        row_id = str(source_row.get("row_id", ""))
        return (
            _clamp(_hash_sign(row_id + ":a") * abs(_nonzero(phase_b))),
            _clamp(_hash_sign(row_id + ":b") * abs(_nonzero(phase_a))),
        )
    return _components_for_family(family, delta, max_abs_delta)


def _candidate_row(source_row: dict[str, Any], family: str, max_abs_delta: float, circuit_template: str) -> dict[str, Any]:
    delta = _row_delta(source_row)
    component_a, component_b = _components_for_replacement_family(family, source_row, max_abs_delta)
    ry_q0 = math.acos(_clamp(component_a))
    ry_q1 = math.acos(_clamp(component_b))
    target_score = _score(component_a, component_b)
    observable = "0.5 + 0.25 * (E[Z0] + E[Z1])"
    readout_note = None
    circuit_parameters = {
        "template": circuit_template,
        "ry_q0": _round_float(ry_q0),
        "ry_q1": _round_float(ry_q1),
        "z0_target": _round_float(component_a),
        "z1_target": _round_float(component_b),
    }
    if circuit_template == CX_TEMPLATE:
        observable = "0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])"
        readout_note = "Under ideal CNOT readout, E[Z0 after CX] recovers component_a and E[Z0 Z1 after CX] recovers component_b."
        circuit_parameters["entangling_gate"] = "cx q0->q1"
    row_core: dict[str, Any] = {
        "row_id": source_row["row_id"],
        "source_row_hash": source_row.get("row_hash"),
        "encoding_family": family,
        "semantics_id": SEMANTICS_ID,
        "source": source_row.get("source", {}),
        "delta": _round_float(delta),
        "components": {
            "component_a": _round_float(component_a),
            "component_b": _round_float(component_b),
        },
        "component_exposure": _round_float(_component_exposure(component_a, component_b)),
        "circuit_parameters": circuit_parameters,
        "ideal_predictions": {"score": _round_float(target_score), "observable": observable},
    }
    if readout_note:
        row_core["ideal_predictions"]["readout_note"] = readout_note
    row = {**row_core, "row_hash": _stable_hash(row_core)}
    if circuit_template == CX_TEMPLATE:
        row["openqasm3"] = _openqasm3(row)
    return row


def _packet_for_lane_family(lane: SourceLane, family: str, circuit_template: str) -> dict[str, Any]:
    rows = list(lane.payload.get("rows", []))
    max_delta = _max_abs_delta(rows)
    matched_rows = [_candidate_row(row, family, max_delta, circuit_template) for row in rows]
    packet_core = {
        "schema_version": STAGE188_SCHEMA_VERSION,
        "packet_version": "qrope_stage188_replacement_semantics_packet_v1",
        "packet_id": f"{lane.lane_id}__{SEMANTICS_ID}__{family}",
        "source_stage": "stage4_preregistered_replication_packets",
        "source_packet_path": str(lane.path.as_posix()),
        "source_lane_id": lane.lane_id,
        "source_row_set_hash": lane.payload.get("preregistration", {}).get("row_set_hash"),
        "semantics_id": SEMANTICS_ID,
        "encoding_family": family,
        "provider": lane.payload.get("provider"),
        "backend": lane.payload.get("backend"),
        "row_count": len(matched_rows),
        "shot_count": lane.payload.get("config", {}).get("shot_count", lane.payload.get("shot_count")),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "execution_status": "not_submitted",
        "fixed_width": {
            "measured_qubits": 2,
            "active_qubits": 2,
            "readout": "computational_basis",
            "circuit_template": circuit_template,
            "entangling_gate": "cx q0->q1" if circuit_template == CX_TEMPLATE else None,
            "score_observable": (
                "0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])"
                if circuit_template == CX_TEMPLATE
                else "0.5 + 0.25 * (E[Z0] + E[Z1])"
            ),
        },
        "matching_policy": {
            "row_set": "identical source rows across all encoding families within each replacement-semantics lane",
            "control_policy": "matched nonzero null exposure using PhaseWrap absolute exposure with frozen row-hash signs",
            "metric_policy": "normalized noise-sensitivity delta and matched-null margin",
            "hardware_scope": "simulated packet screen only; not hardware evidence",
        },
        "rows": matched_rows,
    }
    return {**packet_core, "packet_hash": _stable_hash(packet_core)}


def _candidate_packets(source_packet_dir: Path, product_files: tuple[str, ...], cx_files: tuple[str, ...]) -> tuple[list[dict[str, Any]], list[str]]:
    product_lanes, missing_product = _load_source_lanes(_source_packet_paths(source_packet_dir, product_files))
    cx_lanes, missing_cx = _load_source_lanes(_source_packet_paths(source_packet_dir, cx_files))
    packets: list[dict[str, Any]] = []
    for lane in product_lanes:
        for family in ENCODING_FAMILIES:
            packets.append(_packet_for_lane_family(lane, family, PRODUCT_TEMPLATE))
    for lane in cx_lanes:
        for family in ENCODING_FAMILIES:
            packets.append(_packet_for_lane_family(lane, family, CX_TEMPLATE))
    return packets, missing_product + missing_cx


def _score(component_a: float, component_b: float) -> float:
    return _clamp(0.5 + 0.25 * (component_a + component_b), 0.0, 1.0)


def _component_exposure(component_a: float, component_b: float) -> float:
    return max(1.0e-9, 0.25 * (abs(component_a) + abs(component_b)))


def _packet_metric(packet: dict[str, Any], noise_model: dict[str, Any]) -> dict[str, Any]:
    template = str(packet["fixed_width"]["circuit_template"])
    errors = []
    normalized = []
    ideal_scores = []
    observed_scores = []
    for row in packet.get("rows", []):
        component_a = float(row["components"]["component_a"])
        component_b = float(row["components"]["component_b"])
        noisy_a, noisy_b = _noisy_components(row, noise_model, template)
        ideal = float(row["ideal_predictions"]["score"])
        observed = _score(noisy_a, noisy_b)
        error = abs(observed - ideal)
        exposure = _component_exposure(component_a, component_b)
        errors.append(error)
        normalized.append(error / exposure)
        ideal_scores.append(ideal)
        observed_scores.append(observed)
    shot_count = int(packet.get("shot_count") or 1024)
    return {
        "packet_id": packet["packet_id"],
        "provider": packet.get("provider"),
        "source_lane_id": packet.get("source_lane_id"),
        "encoding_family": packet.get("encoding_family"),
        "circuit_template": template,
        "noise_model_id": noise_model["noise_model_id"],
        "noise_family": noise_model["noise_family"],
        "row_count": len(packet.get("rows", [])),
        "shot_counts": [shot_count],
        "mean_absolute_score_error": _round_float(sum(errors) / len(errors) if errors else 0.0),
        "normalized_noise_sensitivity_delta": _round_float(sum(normalized) / len(normalized) if normalized else 0.0),
        "slope_retention": _round_float(_slope_retention(ideal_scores, observed_scores)),
        "rank_retention": _round_float(_rank_retention(ideal_scores, observed_scores)),
        "simulated_only": True,
    }


def _slope_retention(ideal: list[float], observed: list[float]) -> float:
    ideal_span = max(ideal) - min(ideal) if ideal else 0.0
    observed_span = max(observed) - min(observed) if observed else 0.0
    return observed_span / ideal_span if ideal_span > 0.0 else 1.0


def _rank_retention(ideal: list[float], observed: list[float]) -> float:
    if len(ideal) < 2:
        return 1.0
    return 1.0 if ideal.index(max(ideal)) == observed.index(max(observed)) else 0.0


def _metric_records(packets: list[dict[str, Any]], noise_models: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    return [_packet_metric(packet, noise_model) for packet in packets for noise_model in noise_models]


def _comparison_summary(metric_records: list[dict[str, Any]], thresholds: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str, str], dict[str, dict[str, Any]]] = {}
    for record in metric_records:
        key = (
            str(record["noise_model_id"]),
            str(record.get("provider")),
            str(record["source_lane_id"]),
            str(record["circuit_template"]),
        )
        grouped.setdefault(key, {})[str(record["encoding_family"])] = record
    summaries = []
    for (noise_model_id, provider, source_lane_id, circuit_template), by_family in sorted(grouped.items()):
        phasewrap = by_family.get("phasewrap")
        phase_metric = phasewrap.get("normalized_noise_sensitivity_delta") if phasewrap else None
        positional_metrics = [
            by_family[family]["normalized_noise_sensitivity_delta"]
            for family in POSITIONAL_FAMILIES
            if family in by_family
        ]
        control_metric = by_family.get("matched_nonzero_null_control", {}).get("normalized_noise_sensitivity_delta")
        shot_quantum = 1.0 / min(phasewrap.get("shot_counts", [1024])) if phasewrap else None
        best_positional = min(positional_metrics) if positional_metrics else None
        positional_margin = best_positional - phase_metric if best_positional is not None and phase_metric is not None else None
        control_margin = control_metric - phase_metric if control_metric is not None and phase_metric is not None else None
        positional_quanta = positional_margin / shot_quantum if positional_margin is not None and shot_quantum else None
        control_quanta = control_margin / shot_quantum if control_margin is not None and shot_quantum else None
        stable = bool(
            all(family in by_family for family in ENCODING_FAMILIES)
            and positional_quanta is not None
            and control_quanta is not None
            and positional_quanta >= float(thresholds["min_best_positional_margin_shot_quanta"])
            and control_quanta >= float(thresholds["min_matched_null_margin_shot_quanta"])
        )
        summaries.append(
            {
                "noise_model_id": noise_model_id,
                "provider": provider,
                "source_lane_id": source_lane_id,
                "circuit_template": circuit_template,
                "all_families_present": all(family in by_family for family in ENCODING_FAMILIES),
                "phasewrap_normalized_noise_sensitivity_delta": phase_metric,
                "best_positional_normalized_noise_sensitivity_delta": best_positional,
                "matched_null_control_normalized_noise_sensitivity_delta": control_metric,
                "positional_margin": _round_float(positional_margin) if positional_margin is not None else None,
                "matched_null_control_margin": _round_float(control_margin) if control_margin is not None else None,
                "positional_margin_shot_quanta": round(positional_quanta, 6) if positional_quanta is not None else None,
                "matched_null_control_margin_shot_quanta": round(control_quanta, 6) if control_quanta is not None else None,
                "stable_replacement_target": stable,
            }
        )
    return summaries


def _lane_parts(source_lane_id: str, provider: str) -> dict[str, str]:
    match = SOURCE_LANE_RE.match(source_lane_id)
    if not match:
        return {"provider_family": provider, "template_kind": "", "seed": ""}
    return {"provider_family": match.group("provider"), "template_kind": match.group("template"), "seed": match.group("seed")}


def _candidate_records(summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in summary:
        lane = _lane_parts(str(record.get("source_lane_id")), str(record.get("provider")))
        groups.setdefault((str(record.get("noise_model_id")), lane["provider_family"], lane["seed"]), []).append({**record, **lane})
    records = []
    for (noise_model_id, provider_family, seed), group in sorted(groups.items()):
        stable = [record for record in group if record.get("stable_replacement_target") is True]
        stable_templates = sorted({str(record.get("circuit_template")) for record in stable})
        records.append(
            {
                "noise_model_id": noise_model_id,
                "provider_family": provider_family,
                "seed": seed,
                "comparison_group_count": len(group),
                "stable_target_count": len(stable),
                "stable_template_count": len(stable_templates),
                "stable_templates": stable_templates,
                "min_positional_margin_shot_quanta": min((float(r["positional_margin_shot_quanta"]) for r in group if r.get("positional_margin_shot_quanta") is not None), default=None),
                "min_matched_null_margin_shot_quanta": min((float(r["matched_null_control_margin_shot_quanta"]) for r in group if r.get("matched_null_control_margin_shot_quanta") is not None), default=None),
                "reopen_candidate": len(stable_templates) >= 2,
            }
        )
    return records


def _reopen_supported(candidate_records: list[dict[str, Any]], primary_noise_model_ids: list[str], min_seed_pairs: int) -> bool:
    for model_id in primary_noise_model_ids:
        seed_pairs = {
            f"{record.get('provider_family')}:{record.get('seed')}"
            for record in candidate_records
            if record.get("noise_model_id") == model_id and record.get("reopen_candidate") is True and record.get("seed")
        }
        if len(seed_pairs) < min_seed_pairs:
            return False
    return bool(primary_noise_model_ids)


def run_stage188_replacement_semantics_packet_screen(
    *,
    stage177_results_path: Path = DEFAULT_STAGE177_RESULTS,
    stage187_results_path: Path = DEFAULT_STAGE187_RESULTS,
    source_packet_dir: Path = DEFAULT_SOURCE_PACKET_DIR,
    product_source_packet_files: tuple[str, ...] = PRODUCT_SOURCE_PACKET_FILES,
    cx_source_packet_files: tuple[str, ...] = CX_SOURCE_PACKET_FILES,
) -> dict[str, Any]:
    stage177 = _load_json(stage177_results_path)
    stage187 = _load_json(stage187_results_path)
    sources = [(stage177_results_path, stage177), (stage187_results_path, stage187)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage187, dict) and stage187.get("decision") != STAGE187_READY:
        blockers.append("stage187_replacement_semantics_not_ready")
    semantics = stage187.get("semantics", {}) if isinstance(stage187, dict) else {}
    thresholds = semantics.get("hardware_reopen_thresholds", {})
    if semantics.get("semantics_id") != SEMANTICS_ID:
        blockers.append("stage187_semantics_id_mismatch")
    noise_models = _primary_noise_models(stage177) if isinstance(stage177, dict) else ()
    if not noise_models:
        blockers.append("stage177_primary_models_missing")

    packets, missing_source_packets = _candidate_packets(source_packet_dir, product_source_packet_files, cx_source_packet_files)
    if missing_source_packets:
        blockers.append("missing_source_packets")
    expected_packet_count = (len(product_source_packet_files) + len(cx_source_packet_files)) * len(ENCODING_FAMILIES)
    if len(packets) != expected_packet_count:
        blockers.append("candidate_packet_generation_incomplete")

    metric_records: list[dict[str, Any]] = []
    comparison_summary: list[dict[str, Any]] = []
    candidate_records: list[dict[str, Any]] = []
    supports_reopen = False
    if not blockers:
        metric_records = _metric_records(packets, noise_models)
        comparison_summary = _comparison_summary(metric_records, thresholds)
        candidate_records = _candidate_records(comparison_summary)
        supports_reopen = _reopen_supported(
            candidate_records,
            [str(model["noise_model_id"]) for model in noise_models],
            int(thresholds["min_independent_seed_pairs"]),
        )

    if blockers:
        decision = "REPLACEMENT_SEMANTICS_PACKET_SCREEN_INCOMPLETE"
    elif supports_reopen:
        decision = "REPLACEMENT_SEMANTICS_SIM_SUPPORTS_HARDWARE_REOPEN"
    else:
        decision = "REPLACEMENT_SEMANTICS_SIM_DOES_NOT_SUPPORT_HARDWARE_REOPEN"

    return {
        "schema_version": STAGE188_SCHEMA_VERSION,
        "stage": "stage188_replacement_semantics_packet_screen",
        "status": "completed" if not blockers else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "semantics_id": SEMANTICS_ID,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "missing_source_packets": missing_source_packets,
        "blockers": sorted(set(blockers)),
        "primary_noise_model_ids": [str(model["noise_model_id"]) for model in noise_models],
        "packet_count": len(packets),
        "expected_packet_count": expected_packet_count,
        "metric_record_count": len(metric_records),
        "comparison_group_count": len(comparison_summary),
        "candidate_group_count": len(candidate_records),
        "reopen_candidate_count": sum(1 for record in candidate_records if record.get("reopen_candidate") is True),
        "candidate_records": candidate_records,
        "comparison_summary": comparison_summary,
        "metric_records": metric_records,
        "packets": packets,
        "stability_thresholds": thresholds,
        "simulated_only": True,
        "ibm_backend_properties_informed": bool(noise_models),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "hardware_path_status": "current_ibm_328_job_run_remains_archived",
        "claim_boundary": {
            "supported": [
                "fixed-width replacement-semantics packet generation and simulated IBM-informed screen",
                "matched nonzero null/control exposure replaced the zero-component no-position control",
                "hardware GO/NO-GO evidence under the preregistered normalized noise-sensitivity metric",
            ],
            "excluded": [
                "hardware job submission",
                "a final noisy-hardware robustness or auditability conclusion",
                "credit, billing, or provider-account validation",
            ],
        },
        "next_gate": (
            "If this simulated screen fails, keep hardware archived and reassess whether to stop the fixed-width hardware path; "
            "if it passes, perform a separate human-reviewed hardware readiness gate before any provider action."
        ),
    }


def write_stage188_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    packet_dir = output_dir / "packets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet_paths = []
    for packet in result["packets"]:
        path = packet_dir / f"{packet['packet_id']}.json"
        path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
        packet_paths.append(str(path.as_posix()))
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "semantics_id", "source_artifacts",
        "missing_source_artifacts", "missing_source_packets", "blockers", "primary_noise_model_ids", "packet_count",
        "expected_packet_count", "metric_record_count", "comparison_group_count", "candidate_group_count",
        "reopen_candidate_count", "stability_thresholds", "simulated_only", "ibm_backend_properties_informed",
        "no_hardware_submission", "provider_credentials_required", "secret_values_recorded", "runnable_commands_recorded",
        "hardware_path_status", "claim_boundary", "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["packet_paths"] = packet_paths
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv"), "packet_dir": str(packet_dir)}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("noise_model_id", "provider_family", "seed", "stable_template_count", "min_positional_margin_shot_quanta", "min_matched_null_margin_shot_quanta", "reopen_candidate"))
        writer.writeheader()
        for record in result["candidate_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage188_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"packet_count: {result['packet_count']}")
    print(f"comparison_group_count: {result['comparison_group_count']}")
    print(f"reopen_candidate_count: {result['reopen_candidate_count']}")
    print(f"next_gate: {result['next_gate']}")
