from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage176_ibm_credit_provider_resolution_handoff import DEFAULT_OUTPUT_DIR as STAGE176_OUTPUT_DIR
from qrope.stage188_replacement_semantics_packet_screen import DEFAULT_OUTPUT_DIR as STAGE188_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE189_SCHEMA_VERSION = "qrope_stage189_replacement_hardware_readiness_review_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE176_RESULTS = STAGE176_OUTPUT_DIR / "results.json"
DEFAULT_STAGE188_RESULTS = STAGE188_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage189_replacement_hardware_readiness_review"
STAGE188_SUPPORTS_REOPEN = "REPLACEMENT_SEMANTICS_SIM_SUPPORTS_HARDWARE_REOPEN"
APPROVAL_PHRASE = "APPROVE IBM RUNTIME STAGE188 REPLACEMENT LIVE RUN"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _ibm_reopen_records(stage188: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in stage188.get("candidate_records", [])
        if isinstance(record, dict)
        and record.get("provider_family") == "ibm"
        and record.get("reopen_candidate") is True
    ]


def _selected_lanes(stage188: dict[str, Any]) -> list[str]:
    selected = set()
    passing_seeds = {
        str(record.get("seed"))
        for record in _ibm_reopen_records(stage188)
        if record.get("seed")
    }
    for packet in stage188.get("packets", []):
        if not isinstance(packet, dict):
            continue
        lane_id = str(packet.get("source_lane_id", ""))
        if packet.get("provider") == "ibm_runtime" and any(f"seed{seed}_" in lane_id for seed in passing_seeds):
            selected.add(lane_id)
    return sorted(selected)


def _review_item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage189_replacement_hardware_readiness_review(
    *,
    stage188_results_path: Path = DEFAULT_STAGE188_RESULTS,
    stage176_results_path: Path = DEFAULT_STAGE176_RESULTS,
) -> dict[str, Any]:
    stage188 = _load_json(stage188_results_path)
    stage176 = _load_json(stage176_results_path)
    sources = [(stage188_results_path, stage188), (stage176_results_path, stage176)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage188, dict) and stage188.get("decision") != STAGE188_SUPPORTS_REOPEN:
        blockers.append("stage188_replacement_sim_not_positive")

    ibm_reopen = _ibm_reopen_records(stage188) if isinstance(stage188, dict) else []
    primary_models = sorted({str(record.get("noise_model_id")) for record in ibm_reopen})
    seed_pairs_by_model = {
        model_id: sorted({f"ibm:{record.get('seed')}" for record in ibm_reopen if record.get("noise_model_id") == model_id})
        for model_id in primary_models
    }
    selected_lanes = _selected_lanes(stage188) if isinstance(stage188, dict) else []
    selected_packet_count = sum(
        1
        for packet in stage188.get("packets", [])
        if isinstance(stage188, dict)
        and isinstance(packet, dict)
        and packet.get("source_lane_id") in selected_lanes
    ) if isinstance(stage188, dict) else 0
    selected_row_job_count = sum(
        int(packet.get("row_count") or 0)
        for packet in stage188.get("packets", [])
        if isinstance(stage188, dict)
        and isinstance(packet, dict)
        and packet.get("source_lane_id") in selected_lanes
    ) if isinstance(stage188, dict) else 0
    credit_verified = bool(stage176.get("credit_balance_verified")) if isinstance(stage176, dict) else False

    review_items = [
        _review_item(
            "replacement_simulation_gate",
            "passed" if isinstance(stage188, dict) and stage188.get("decision") == STAGE188_SUPPORTS_REOPEN else "blocked",
            "Stage188 replacement-semantics IBM-informed simulation must support hardware reopen.",
            {
                "stage188_decision": stage188.get("decision") if isinstance(stage188, dict) else None,
                "reopen_candidate_count": stage188.get("reopen_candidate_count") if isinstance(stage188, dict) else None,
                "seed_pairs_by_model": seed_pairs_by_model,
            },
        ),
        _review_item(
            "replacement_execution_package",
            "required_new_artifact",
            "A new Stage190-style execution package is required because Stage188 changes semantics, control family, metric, and selected lanes.",
            {
                "selected_lanes": selected_lanes,
                "selected_packet_count": selected_packet_count,
                "estimated_packet_row_job_count_before_calibration": selected_row_job_count,
            },
        ),
        _review_item(
            "calibration_and_result_contract",
            "required_new_artifact",
            "Known-state calibration and result-ingestion contracts must be regenerated for the replacement semantics before any run.",
            {"old_stage176_handoff_reusable": False},
        ),
        _review_item(
            "credit_billing_runtime_allowance",
            "human_verification_required" if not credit_verified else "verified",
            "IBM credit, billing, and Runtime allowance must be checked by the user before any live run.",
            {"credit_balance_verified": credit_verified},
        ),
        _review_item(
            "exact_human_approval",
            "awaiting_exact_phrase",
            "Live execution remains disallowed unless the replacement-run approval phrase is provided after readiness is complete.",
            {"approval_phrase_required": APPROVAL_PHRASE},
        ),
    ]
    if any(item["status"] in {"blocked", "required_new_artifact", "human_verification_required", "awaiting_exact_phrase"} for item in review_items):
        blockers.append("replacement_hardware_readiness_requirements_open")

    if missing_sources:
        decision = "REPLACEMENT_HARDWARE_READINESS_REVIEW_INCOMPLETE"
    elif isinstance(stage188, dict) and stage188.get("decision") == STAGE188_SUPPORTS_REOPEN:
        decision = "REPLACEMENT_HARDWARE_REVIEW_REOPENED_BUT_NOT_READY_FOR_LIVE_RUN"
    else:
        decision = "REPLACEMENT_HARDWARE_REVIEW_NOT_REOPENED"

    return {
        "schema_version": STAGE189_SCHEMA_VERSION,
        "stage": "stage189_replacement_hardware_readiness_review",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "stage188_decision": stage188.get("decision") if isinstance(stage188, dict) else None,
        "stage176_decision": stage176.get("decision") if isinstance(stage176, dict) else None,
        "semantics_id": stage188.get("semantics_id") if isinstance(stage188, dict) else None,
        "primary_noise_model_ids": stage188.get("primary_noise_model_ids", []) if isinstance(stage188, dict) else [],
        "ibm_seed_pairs_by_noise_model": seed_pairs_by_model,
        "selected_lanes": selected_lanes,
        "selected_lane_count": len(selected_lanes),
        "selected_packet_count": selected_packet_count,
        "estimated_packet_row_job_count_before_calibration": selected_row_job_count,
        "review_items": review_items,
        "replacement_approval_phrase_required": APPROVAL_PHRASE,
        "simulated_only": True,
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "hardware_path_status": "human_review_reopened_by_simulation_but_live_run_disallowed",
        "claim_boundary": {
            "supported": [
                "Stage188 replacement-semantics simulation is strong enough to reopen human hardware-readiness review",
                "the old Stage176/Stage133 live path cannot be reused for the replacement semantics",
                "new execution packaging, calibration, credit verification, and exact approval remain required before provider action",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials, token values, CRN values, or account secrets",
                "runnable live-submit command strings",
                "IBM credit balance or dollar cost verification",
                "a final noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Build a replacement-semantics execution package and calibration/result-ingestion contract for the selected IBM lanes; "
            "then perform credit/provider and exact-approval review before any live run."
        ),
    }


def write_stage189_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version",
        "stage",
        "status",
        "objective",
        "decision",
        "source_artifacts",
        "missing_source_artifacts",
        "blockers",
        "stage188_decision",
        "stage176_decision",
        "semantics_id",
        "primary_noise_model_ids",
        "ibm_seed_pairs_by_noise_model",
        "selected_lanes",
        "selected_lane_count",
        "selected_packet_count",
        "estimated_packet_row_job_count_before_calibration",
        "replacement_approval_phrase_required",
        "simulated_only",
        "no_hardware_submission",
        "explicit_user_approval_required",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "hardware_path_status",
        "claim_boundary",
        "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("item_id", "status", "description"))
        writer.writeheader()
        for item in result["review_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage189_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"selected_lane_count: {result['selected_lane_count']}")
    print(f"selected_packet_count: {result['selected_packet_count']}")
    print(f"estimated_packet_row_job_count_before_calibration: {result['estimated_packet_row_job_count_before_calibration']}")
    print(f"next_gate: {result['next_gate']}")
