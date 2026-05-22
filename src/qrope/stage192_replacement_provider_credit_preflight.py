from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Mapping

from qrope.stage159_first_provider_backend_preflight import DEFAULT_OUTPUT_DIR as STAGE159_OUTPUT_DIR
from qrope.stage176_ibm_credit_provider_resolution_handoff import DEFAULT_OUTPUT_DIR as STAGE176_OUTPUT_DIR
from qrope.stage191_replacement_approval_dossier import DEFAULT_OUTPUT_DIR as STAGE191_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE192_SCHEMA_VERSION = "qrope_stage192_replacement_provider_credit_preflight_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE159_RESULTS = STAGE159_OUTPUT_DIR / "results.json"
DEFAULT_STAGE176_RESULTS = STAGE176_OUTPUT_DIR / "results.json"
DEFAULT_STAGE191_RESULTS = STAGE191_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage192_replacement_provider_credit_preflight"
STAGE191_READY = "REPLACEMENT_APPROVAL_DOSSIER_READY_FOR_HUMAN_REVIEW_NOT_LIVE"
REPLACEMENT_APPROVAL_PHRASE = "APPROVE IBM RUNTIME STAGE188 REPLACEMENT LIVE RUN"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _env_present(env: Mapping[str, str], *keys: str) -> bool:
    return any(bool(str(env.get(key, "")).strip()) for key in keys)


def _preflight_item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage192_replacement_provider_credit_preflight(
    *,
    stage159_results_path: Path = DEFAULT_STAGE159_RESULTS,
    stage176_results_path: Path = DEFAULT_STAGE176_RESULTS,
    stage191_results_path: Path = DEFAULT_STAGE191_RESULTS,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    environ = os.environ if env is None else env
    stage159 = _load_json(stage159_results_path)
    stage176 = _load_json(stage176_results_path)
    stage191 = _load_json(stage191_results_path)
    sources = [(stage159_results_path, stage159), (stage176_results_path, stage176), (stage191_results_path, stage191)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    token_present = _env_present(environ, "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN")
    instance_present = _env_present(environ, "IBM_QUANTUM_INSTANCE_CRN")
    backend_present = _env_present(environ, "QROPE_IBM_BACKEND", "IBM_QUANTUM_BACKEND", "QROPE_HARDWARE_BACKEND")
    current_configuration_complete = token_present and instance_present and backend_present
    stage159_backend_ready = bool(isinstance(stage159, dict) and stage159.get("backend_lookup_ready"))
    stage176_credit_verified = bool(isinstance(stage176, dict) and stage176.get("credit_balance_verified"))
    stage191_ready = bool(isinstance(stage191, dict) and stage191.get("decision") == STAGE191_READY)
    stage191_phrase = stage191.get("replacement_approval_phrase_required") if isinstance(stage191, dict) else None
    replacement_phrase_ready = stage191_phrase == REPLACEMENT_APPROVAL_PHRASE
    preflight_items = [
        _preflight_item(
            "replacement_approval_dossier",
            "ready_for_human_review" if stage191_ready else "blocked",
            "Stage191 replacement approval dossier must be ready before provider or credit review.",
            {
                "stage191_decision": stage191.get("decision") if isinstance(stage191, dict) else None,
                "estimated_total_job_count": stage191.get("estimated_total_job_count") if isinstance(stage191, dict) else None,
                "estimated_total_shots": stage191.get("estimated_total_shots") if isinstance(stage191, dict) else None,
            },
        ),
        _preflight_item(
            "current_local_ibm_configuration",
            "present_non_secret" if current_configuration_complete else "missing_or_incomplete",
            "Current shell must provide non-secret presence of IBM token, instance, and backend name before any read-only refresh can run.",
            {
                "ibm_token_present": token_present,
                "ibm_instance_crn_present": instance_present,
                "ibm_backend_env_present": backend_present,
            },
        ),
        _preflight_item(
            "prior_read_only_backend_evidence",
            "available_but_old_path" if stage159_backend_ready else "not_available",
            "Prior Stage159 backend lookup evidence is informative but belongs to the archived Stage133 path, not the replacement approval phrase.",
            {
                "stage159_decision": stage159.get("decision") if isinstance(stage159, dict) else None,
                "backend_lookup_ready": stage159.get("backend_lookup_ready") if isinstance(stage159, dict) else None,
                "backend": stage159.get("backend_metadata", {}).get("backend") if isinstance(stage159, dict) else None,
                "operational": stage159.get("backend_metadata", {}).get("operational") if isinstance(stage159, dict) else None,
                "pending_jobs_at_preflight": stage159.get("backend_metadata", {}).get("pending_jobs") if isinstance(stage159, dict) else None,
            },
        ),
        _preflight_item(
            "credit_billing_runtime_allowance",
            "verified" if stage176_credit_verified else "human_verification_required",
            "IBM credit, billing, and Runtime allowance cannot be inferred from local token presence or old backend metadata.",
            {"credit_balance_verified": stage176_credit_verified},
        ),
        _preflight_item(
            "replacement_exact_approval_boundary",
            "awaiting_exact_phrase" if replacement_phrase_ready else "blocked",
            "Replacement hardware remains disallowed until credit/provider allowance is resolved and the replacement approval phrase is given.",
            {"approval_phrase_required": stage191_phrase},
        ),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not stage191_ready:
        blockers.append("stage191_approval_dossier_not_ready")
    if not current_configuration_complete:
        blockers.append("current_ibm_configuration_missing_or_incomplete")
    if not stage176_credit_verified:
        blockers.append("credit_billing_runtime_allowance_unverified")
    if not replacement_phrase_ready:
        blockers.append("replacement_approval_phrase_missing_or_mismatched")
    if missing_sources:
        decision = "REPLACEMENT_PROVIDER_CREDIT_PREFLIGHT_INCOMPLETE"
    elif blockers:
        decision = "REPLACEMENT_PROVIDER_CREDIT_PREFLIGHT_BLOCKED"
    else:
        decision = "REPLACEMENT_PROVIDER_CREDIT_PREFLIGHT_READY_FOR_READ_ONLY_REFRESH"
    return {
        "schema_version": STAGE192_SCHEMA_VERSION,
        "stage": "stage192_replacement_provider_credit_preflight",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "replacement_approval_phrase_required": stage191_phrase,
        "estimated_total_job_count": stage191.get("estimated_total_job_count") if isinstance(stage191, dict) else None,
        "estimated_total_shots": stage191.get("estimated_total_shots") if isinstance(stage191, dict) else None,
        "current_local_ibm_configuration_complete": current_configuration_complete,
        "ibm_token_present": token_present,
        "ibm_instance_crn_present": instance_present,
        "ibm_backend_env_present": backend_present,
        "credit_balance_verified": stage176_credit_verified,
        "prior_backend_lookup_ready": stage159_backend_ready,
        "preflight_items": preflight_items,
        "no_hardware_submission": True,
        "read_only_backend_lookup_attempted": False,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "replacement-run credit/provider readiness is assessed against current non-secret local configuration",
                "old Stage133 backend evidence is separated from the Stage188 replacement approval path",
                "the remaining credit/provider and exact-approval blockers are recorded before any read-only refresh or live action",
            ],
            "excluded": [
                "hardware job submission",
                "Sampler or Estimator runtime execution",
                "provider credentials, token values, CRN values, or account secrets",
                "IBM credit balance, billing plan, or dollar-cost verification",
                "runnable live-submit command strings",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Restore IBM token, instance, and backend environment variables, then perform a replacement-scoped read-only backend "
            "refresh and human credit/billing/Runtime allowance check before any exact live-run approval is considered."
        ),
    }


def write_stage192_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "replacement_approval_phrase_required",
        "estimated_total_job_count",
        "estimated_total_shots",
        "current_local_ibm_configuration_complete",
        "ibm_token_present",
        "ibm_instance_crn_present",
        "ibm_backend_env_present",
        "credit_balance_verified",
        "prior_backend_lookup_ready",
        "no_hardware_submission",
        "read_only_backend_lookup_attempted",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "explicit_user_approval_required",
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
        for item in result["preflight_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage192_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"current_local_ibm_configuration_complete: {result['current_local_ibm_configuration_complete']}")
    print(f"credit_balance_verified: {result['credit_balance_verified']}")
    print(f"estimated_total_job_count: {result['estimated_total_job_count']}")
    print(f"estimated_total_shots: {result['estimated_total_shots']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
