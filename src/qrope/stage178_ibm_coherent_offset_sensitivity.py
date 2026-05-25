from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage153_simulated_noise_rehearsal import (
    DEFAULT_STAGE100_MANIFEST,
    DEFAULT_STAGE99_MANIFEST,
    _comparison_summary,
    _metric_records,
)
from qrope.stage177_ibm_backend_informed_noise_probe import (
    DEFAULT_STAGE169_RESULTS,
    DEFAULT_OUTPUT_DIR as STAGE177_OUTPUT_DIR,
    MIN_MARGIN_SHOT_QUANTA,
    _enrich_summary,
)


STAGE178_SCHEMA_VERSION = "qrope_stage178_ibm_coherent_offset_sensitivity_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE177_RESULTS = STAGE177_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage178_ibm_coherent_offset_sensitivity"
OBJECTIVE = (
    "Determine whether PhaseWrap's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
DEFAULT_SIGNED_OFFSETS: tuple[float, ...] = (-0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04)
PRIMARY_STAGE177_MODEL_IDS = {"ibm_backend_median_stochastic", "ibm_backend_p75_stochastic"}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _packet_paths(manifest_path: Path) -> list[Path]:
    manifest = _load_json(manifest_path)
    if not isinstance(manifest, dict):
        return []
    return [Path(str(path)) for path in manifest.get("packet_paths", [])]


def _primary_stage177_models(stage177: dict[str, Any]) -> list[dict[str, Any]]:
    models = []
    for model in stage177.get("noise_models", []):
        if isinstance(model, dict) and str(model.get("noise_model_id")) in PRIMARY_STAGE177_MODEL_IDS:
            models.append(model)
    return models


def _signed_offset_models(stage177: dict[str, Any], offsets: tuple[float, ...]) -> tuple[dict[str, Any], ...]:
    models = []
    for base in _primary_stage177_models(stage177):
        for offset in offsets:
            label = f"{offset:+.3f}".replace("+", "p").replace("-", "m").replace(".", "p")
            models.append(
                {
                    **base,
                    "noise_model_id": f"{base['noise_model_id']}__signed_ry_offset_{label}rad",
                    "noise_family": "ibm_backend_properties_stochastic_plus_signed_ry_offset_sweep",
                    "base_noise_model_id": base["noise_model_id"],
                    "ry_angle_offset_radians": offset,
                    "signed_offset_radians": offset,
                }
            )
    return tuple(models)


def _offset_records(comparison_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    keys = sorted(
        {
            (str(record.get("base_noise_model_id")), float(record.get("signed_offset_radians")))
            for record in comparison_summary
            if record.get("locked_target_lane") is True
        }
    )
    records = []
    for base_model_id, offset in keys:
        locked = [
            record
            for record in comparison_summary
            if record.get("locked_target_lane") is True
            and record.get("base_noise_model_id") == base_model_id
            and float(record.get("signed_offset_radians")) == offset
        ]
        stable = [record for record in locked if record.get("stable_strict_target") is True]
        records.append(
            {
                "base_noise_model_id": base_model_id,
                "signed_offset_radians": offset,
                "locked_template_count": len({str(record.get("circuit_template")) for record in locked}),
                "stable_target_count": len(stable),
                "stable_template_count": len({str(record.get("circuit_template")) for record in stable}),
                "stable_templates": sorted({str(record.get("circuit_template")) for record in stable}),
                "min_positional_margin_shot_quanta": min(
                    (float(record.get("positional_margin_shot_quanta")) for record in locked if record.get("positional_margin_shot_quanta") is not None),
                    default=None,
                ),
                "min_control_margin_shot_quanta": min(
                    (float(record.get("control_margin_shot_quanta")) for record in locked if record.get("control_margin_shot_quanta") is not None),
                    default=None,
                ),
            }
        )
    return records


def _annotate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated = []
    for record in records:
        base_model = str(record.get("noise_model_id")).split("__signed_ry_offset_")[0]
        offset = record.get("ry_angle_offset_radians")
        annotated.append(
            {
                **record,
                "base_noise_model_id": base_model,
                "signed_offset_radians": offset,
                "primary_ibm_properties_model": True,
            }
        )
    return annotated


def _comparison_summary_with_offset_fields(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    model_fields = {
        str(record.get("noise_model_id")): {
            "base_noise_model_id": record.get("base_noise_model_id"),
            "signed_offset_radians": record.get("signed_offset_radians"),
        }
        for record in records
    }
    summaries = _comparison_summary(records)
    for summary in summaries:
        summary.update(model_fields.get(str(summary.get("noise_model_id")), {}))
    return summaries


def run_stage178_ibm_coherent_offset_sensitivity(
    *,
    stage177_results_path: Path = DEFAULT_STAGE177_RESULTS,
    stage169_results_path: Path = DEFAULT_STAGE169_RESULTS,
    stage99_manifest_path: Path = DEFAULT_STAGE99_MANIFEST,
    stage100_manifest_path: Path = DEFAULT_STAGE100_MANIFEST,
    signed_offsets: tuple[float, ...] = DEFAULT_SIGNED_OFFSETS,
) -> dict[str, Any]:
    stage177 = _load_json(stage177_results_path)
    stage169 = _load_json(stage169_results_path)
    missing_sources = [
        str(path.as_posix())
        for path, payload in ((stage177_results_path, stage177), (stage169_results_path, stage169))
        if not isinstance(payload, dict)
    ]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage177, dict) and stage177.get("decision") != "IBM_BACKEND_INFORMED_SIM_DOES_NOT_SUPPORT_TARGETED_HARDWARE_RUN_YET":
        blockers.append("stage177_not_at_backend_informed_no_go_boundary")
    if not isinstance(stage177, dict) or not _primary_stage177_models(stage177):
        blockers.append("stage177_primary_ibm_models_missing")
    if isinstance(stage169, dict) and stage169.get("decision") != "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES":
        blockers.append("stage169_target_scope_not_locked")

    noise_models = _signed_offset_models(stage177, signed_offsets) if isinstance(stage177, dict) and not blockers else ()
    packet_paths = _packet_paths(stage99_manifest_path) + _packet_paths(stage100_manifest_path)
    metric_records, missing_packets = _metric_records(packet_paths, noise_models) if noise_models else ([], [])
    if missing_packets:
        blockers.append("missing_matched_packets")
    annotated_metric_records = _annotate(metric_records)
    locked_lanes = set(stage169.get("stable_target_lanes", [])) if isinstance(stage169, dict) else set()
    comparison_summary = (
        _enrich_summary(_comparison_summary_with_offset_fields(annotated_metric_records), annotated_metric_records, locked_lanes)
        if annotated_metric_records
        else []
    )
    offset_records = _offset_records(comparison_summary)
    stable_offsets = [record for record in offset_records if record.get("stable_template_count") == 2]
    signed_nonzero_stable_offsets = [record for record in stable_offsets if abs(float(record.get("signed_offset_radians") or 0.0)) > 0.0]

    if blockers:
        decision = "IBM_COHERENT_OFFSET_SENSITIVITY_INCOMPLETE"
    elif stable_offsets:
        decision = "IBM_COHERENT_OFFSET_SENSITIVITY_FINDS_SIGNED_REGION_CALIBRATION_PROBE_RECOMMENDED"
    elif signed_nonzero_stable_offsets:
        decision = "IBM_COHERENT_OFFSET_SENSITIVITY_FINDS_SIGNED_REGION_CALIBRATION_PROBE_RECOMMENDED"
    else:
        decision = "IBM_COHERENT_OFFSET_SENSITIVITY_DOES_NOT_RECOVER_TARGETED_SIGNAL"

    return {
        "schema_version": STAGE178_SCHEMA_VERSION,
        "stage": "stage178_ibm_coherent_offset_sensitivity",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [
            str(stage177_results_path.as_posix()),
            str(stage169_results_path.as_posix()),
            str(stage99_manifest_path.as_posix()),
            str(stage100_manifest_path.as_posix()),
        ],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "signed_offsets_radians": list(signed_offsets),
        "base_noise_model_ids": [model["noise_model_id"] for model in _primary_stage177_models(stage177)] if isinstance(stage177, dict) else [],
        "locked_target_lanes": sorted(locked_lanes),
        "noise_model_count": len(noise_models),
        "comparison_group_count": len(comparison_summary),
        "locked_offset_record_count": len(offset_records),
        "stable_offset_count": len(stable_offsets),
        "stable_offsets": stable_offsets,
        "offset_records": offset_records,
        "comparison_summary": comparison_summary,
        "simulated_only": True,
        "ibm_backend_properties_informed": bool(noise_models),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "stability_thresholds": {
            "min_positional_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_control_margin_shot_quanta": MIN_MARGIN_SHOT_QUANTA,
            "min_stable_template_count": 2,
        },
        "claim_boundary": {
            "supported": [
                "simulated signed coherent-offset sensitivity map on top of IBM backend-property stochastic noise",
                "screening evidence for whether a cheaper coherent-offset calibration probe is worth designing",
                "explicit non-submitting separation from the full 328-job IBM hardware run",
            ],
            "excluded": [
                "hardware job submission",
                "IBM credit or billing verification",
                "direct measurement of signed coherent RY offset on IBM hardware",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "If a stable signed-offset region exists, design a small calibration probe for signed coherent bias before any "
            "full hardware run. If not, archive the current IBM hardware path or redesign the encoding target."
        ),
    }


def write_stage178_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        key: result[key]
        for key in (
            "schema_version",
            "stage",
            "status",
            "objective",
            "decision",
            "source_artifacts",
            "missing_source_artifacts",
            "blockers",
            "signed_offsets_radians",
            "base_noise_model_ids",
            "locked_target_lanes",
            "noise_model_count",
            "comparison_group_count",
            "locked_offset_record_count",
            "stable_offset_count",
            "stable_offsets",
            "simulated_only",
            "ibm_backend_properties_informed",
            "no_hardware_submission",
            "provider_credentials_required",
            "secret_values_recorded",
            "runnable_commands_recorded",
            "stability_thresholds",
            "claim_boundary",
            "next_gate",
        )
    }
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
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
                "base_noise_model_id",
                "signed_offset_radians",
                "locked_template_count",
                "stable_target_count",
                "stable_template_count",
                "min_positional_margin_shot_quanta",
                "min_control_margin_shot_quanta",
            ),
        )
        writer.writeheader()
        for record in result["offset_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage178_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"stable_offset_count: {result['stable_offset_count']}")
    print(f"next_gate: {result['next_gate']}")
