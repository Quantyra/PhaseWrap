from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage193_replacement_read_only_backend_refresh import DEFAULT_OUTPUT_DIR as STAGE193_OUTPUT_DIR
from qrope.stage203_reduced_scope_execution_package import DEFAULT_OUTPUT_DIR as STAGE203_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE204_SCHEMA_VERSION = "qrope_stage204_reduced_scope_guarded_runner_readiness_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE203_RESULTS = STAGE203_OUTPUT_DIR / "results.json"
DEFAULT_FRESH_STAGE193_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage193_reduced_scope_fresh_backend_refresh_100usd" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage204_reduced_scope_guarded_runner_readiness_100usd"
STAGE203_READY = "REDUCED_SCOPE_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED_NOT_LIVE"
STAGE193_READY = "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage204_reduced_scope_guarded_runner_readiness(
    *,
    stage203_results_path: Path = DEFAULT_STAGE203_RESULTS,
    fresh_stage193_results_path: Path = DEFAULT_FRESH_STAGE193_RESULTS,
) -> dict[str, Any]:
    stage203 = _load_json(stage203_results_path)
    stage193 = _load_json(fresh_stage193_results_path)
    sources = [(stage203_results_path, stage203), (fresh_stage193_results_path, stage193)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")

    stage203_ready = bool(isinstance(stage203, dict) and stage203.get("decision") == STAGE203_READY)
    backend_ready = bool(isinstance(stage193, dict) and stage193.get("decision") == STAGE193_READY and stage193.get("backend_lookup_ready") is True)
    package_backend = stage203.get("backend") if isinstance(stage203, dict) else None
    backend_metadata = stage193.get("backend_metadata", {}) if isinstance(stage193, dict) else {}
    fresh_backend = backend_metadata.get("backend")
    backend_matches = bool(package_backend and fresh_backend and package_backend == fresh_backend)
    package_contract_ready = bool(
        isinstance(stage203, dict)
        and stage203.get("packet_template_count") == 20
        and stage203.get("estimated_packet_row_job_count") == 320
        and stage203.get("estimated_calibration_job_count") == 4
        and stage203.get("estimated_total_job_count") == 324
        and stage203.get("estimated_total_shots") == 659360
        and stage203.get("budget_cap_usd") == 100.0
        and stage203.get("no_hardware_submission") is True
        and stage203.get("live_submit_command_created") is False
    )
    if not stage203_ready:
        blockers.append("stage203_reduced_scope_package_not_ready")
    if not package_contract_ready:
        blockers.append("stage203_reduced_scope_contract_mismatch")
    if not backend_ready:
        blockers.append("fresh_read_only_backend_refresh_not_ready")
    if not backend_matches:
        blockers.append("fresh_backend_does_not_match_stage203_package")

    readiness_items = [
        _item(
            "stage203_reduced_scope_package",
            "ready" if stage203_ready and package_contract_ready else "blocked",
            "The approved reduced-scope execution package must match the frozen 2048-shot, 324-job, 659360-shot contract.",
            {
                "stage203_decision": stage203.get("decision") if isinstance(stage203, dict) else None,
                "packet_template_count": stage203.get("packet_template_count") if isinstance(stage203, dict) else None,
                "estimated_total_job_count": stage203.get("estimated_total_job_count") if isinstance(stage203, dict) else None,
                "estimated_total_shots": stage203.get("estimated_total_shots") if isinstance(stage203, dict) else None,
                "budget_cap_usd": stage203.get("budget_cap_usd") if isinstance(stage203, dict) else None,
            },
        ),
        _item(
            "fresh_read_only_backend_refresh",
            "ready" if backend_ready and backend_matches else "blocked",
            "A fresh read-only IBM backend refresh must succeed and match the packaged backend before guarded execution.",
            {
                "stage193_decision": stage193.get("decision") if isinstance(stage193, dict) else None,
                "backend_lookup_ready": stage193.get("backend_lookup_ready") if isinstance(stage193, dict) else None,
                "package_backend": package_backend,
                "fresh_backend": fresh_backend,
                "operational": backend_metadata.get("operational"),
                "pending_jobs": backend_metadata.get("pending_jobs"),
            },
        ),
        _item(
            "runner_execution_boundary",
            "final_execution_step_required",
            "This gate does not emit a runnable command or submit hardware; it only clears package/backend readiness for the final guarded execution step.",
            {"hardware_submitted_here": False, "live_submit_command_created_here": False, "runnable_commands_recorded_here": False},
        ),
        _item(
            "post_result_contract",
            "required_after_execution",
            "Provider results must later populate raw counts, job IDs, timestamps, backend metadata, and calibration counts before interpretation.",
            {
                "required_execution_fields": stage203.get("required_execution_fields") if isinstance(stage203, dict) else None,
                "required_calibration_states": stage203.get("required_calibration_states") if isinstance(stage203, dict) else None,
            },
        ),
    ]
    ready = not blockers
    return {
        "schema_version": STAGE204_SCHEMA_VERSION,
        "stage": "stage204_reduced_scope_guarded_runner_readiness",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": "REDUCED_SCOPE_GUARDED_RUNNER_READY_FOR_FINAL_EXECUTION_STEP_NOT_LIVE" if ready else "REDUCED_SCOPE_GUARDED_RUNNER_READINESS_BLOCKED",
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "scope_id": stage203.get("scope_id") if isinstance(stage203, dict) else None,
        "backend": package_backend,
        "fresh_backend_metadata": backend_metadata,
        "budget_cap_usd": stage203.get("budget_cap_usd") if isinstance(stage203, dict) else None,
        "estimated_total_job_count": stage203.get("estimated_total_job_count") if isinstance(stage203, dict) else None,
        "estimated_total_shots": stage203.get("estimated_total_shots") if isinstance(stage203, dict) else None,
        "stage203_ready": stage203_ready,
        "package_contract_ready": package_contract_ready,
        "fresh_backend_ready": backend_ready,
        "fresh_backend_matches_package": backend_matches,
        "readiness_items": readiness_items,
        "no_hardware_submission": True,
        "live_submit_command_created": False,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_recorded": ready,
        "claim_boundary": {
            "supported": [
                "reduced-scope package and fresh read-only backend metadata are ready for a final guarded execution step",
                "backend target matches the approved Stage203 package",
                "no-submit readiness is separated from live hardware execution and result interpretation",
            ],
            "excluded": [
                "hardware job submission",
                "creation or recording of a runnable live-submit command",
                "provider-side result retrieval",
                "calibration pass/fail or robustness interpretation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Run the final guarded reduced-scope execution step only from this ready state; after execution, ingest provider "
            "counts and run calibration, robustness, auditability, and final objective interpretation gates."
        ),
    }


def write_stage204_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "scope_id",
        "backend",
        "fresh_backend_metadata",
        "budget_cap_usd",
        "estimated_total_job_count",
        "estimated_total_shots",
        "stage203_ready",
        "package_contract_ready",
        "fresh_backend_ready",
        "fresh_backend_matches_package",
        "no_hardware_submission",
        "live_submit_command_created",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "explicit_user_approval_recorded",
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
        for item in result["readiness_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage204_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"scope_id: {result['scope_id']}")
    print(f"backend: {result['backend']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"fresh_backend_ready: {result['fresh_backend_ready']}")
    print(f"fresh_backend_matches_package: {result['fresh_backend_matches_package']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
