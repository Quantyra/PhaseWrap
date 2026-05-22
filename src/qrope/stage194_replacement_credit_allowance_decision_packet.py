from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Mapping

from qrope.stage191_replacement_approval_dossier import DEFAULT_OUTPUT_DIR as STAGE191_OUTPUT_DIR
from qrope.stage193_replacement_read_only_backend_refresh import DEFAULT_OUTPUT_DIR as STAGE193_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE194_SCHEMA_VERSION = "qrope_stage194_replacement_credit_allowance_decision_packet_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE191_RESULTS = STAGE191_OUTPUT_DIR / "results.json"
DEFAULT_STAGE193_RESULTS = STAGE193_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage194_replacement_credit_allowance_decision_packet"
STAGE191_READY = "REPLACEMENT_APPROVAL_DOSSIER_READY_FOR_HUMAN_REVIEW_NOT_LIVE"
STAGE193_READY = "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _positive_float(env: Mapping[str, str], key: str) -> float | None:
    try:
        value = float(str(env.get(key, "")).strip())
    except ValueError:
        return None
    return value if value > 0 else None


def _positive_int(env: Mapping[str, str], key: str) -> int | None:
    try:
        value = int(str(env.get(key, "")).strip())
    except ValueError:
        return None
    return value if value > 0 else None


def _decision_item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage194_replacement_credit_allowance_decision_packet(
    *,
    stage191_results_path: Path = DEFAULT_STAGE191_RESULTS,
    stage193_results_path: Path = DEFAULT_STAGE193_RESULTS,
    env: Mapping[str, str] | None = None,
    human_credit_allowance_verified: bool = False,
) -> dict[str, Any]:
    environ = os.environ if env is None else env
    stage191 = _load_json(stage191_results_path)
    stage193 = _load_json(stage193_results_path)
    sources = [(stage191_results_path, stage191), (stage193_results_path, stage193)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    stage191_ready = bool(isinstance(stage191, dict) and stage191.get("decision") == STAGE191_READY)
    stage193_ready = bool(isinstance(stage193, dict) and stage193.get("decision") == STAGE193_READY)
    budget_cap = _positive_float(environ, "QROPE_HARDWARE_BUDGET_USD_CAP")
    queue_depth_cap = _positive_int(environ, "QROPE_HARDWARE_QUEUE_DEPTH_CAP")
    estimated_job_count = stage191.get("estimated_total_job_count") if isinstance(stage191, dict) else None
    estimated_shots = stage191.get("estimated_total_shots") if isinstance(stage191, dict) else None
    backend_metadata = stage193.get("backend_metadata", {}) if isinstance(stage193, dict) else {}
    pending_jobs = backend_metadata.get("pending_jobs")
    queue_within_cap = (
        isinstance(pending_jobs, int)
        and queue_depth_cap is not None
        and pending_jobs <= queue_depth_cap
    )
    decision_items = [
        _decision_item(
            "replacement_approval_dossier",
            "ready" if stage191_ready else "blocked",
            "Stage191 approval dossier must quantify the replacement run exposure before credit review.",
            {
                "stage191_decision": stage191.get("decision") if isinstance(stage191, dict) else None,
                "estimated_total_job_count": estimated_job_count,
                "estimated_total_shots": estimated_shots,
            },
        ),
        _decision_item(
            "replacement_backend_reachability",
            "verified" if stage193_ready else "blocked",
            "Stage193 must verify replacement-scoped read-only backend reachability before credit allowance review.",
            {
                "stage193_decision": stage193.get("decision") if isinstance(stage193, dict) else None,
                "backend": backend_metadata.get("backend"),
                "operational": backend_metadata.get("operational"),
                "pending_jobs": pending_jobs,
            },
        ),
        _decision_item(
            "local_budget_cap",
            "present" if budget_cap is not None else "missing",
            "Local non-secret hardware budget cap is a safety bound, not proof of IBM account credit.",
            {"budget_cap_usd": budget_cap},
        ),
        _decision_item(
            "local_queue_depth_cap",
            "within_cap" if queue_within_cap else "missing_or_exceeded",
            "Current backend pending jobs should be within the local queue-depth cap before a live run is considered.",
            {"queue_depth_cap": queue_depth_cap, "backend_pending_jobs": pending_jobs},
        ),
        _decision_item(
            "ibm_credit_billing_runtime_allowance",
            "human_verified" if human_credit_allowance_verified else "human_verification_required",
            "IBM credit, billing plan, Runtime allowance, and any expected charges require human account-side verification.",
            {"human_credit_allowance_verified": human_credit_allowance_verified},
        ),
        _decision_item(
            "exact_replacement_approval",
            "not_requested",
            "Exact live-run approval must remain separate and must not be requested until credit allowance is verified.",
            {
                "approval_phrase_required": stage191.get("replacement_approval_phrase_required") if isinstance(stage191, dict) else None,
                "approval_phrase_accepted_here": False,
            },
        ),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not stage191_ready:
        blockers.append("stage191_approval_dossier_not_ready")
    if not stage193_ready:
        blockers.append("stage193_backend_refresh_not_ready")
    if budget_cap is None:
        blockers.append("local_budget_cap_missing")
    if not queue_within_cap:
        blockers.append("backend_queue_depth_missing_or_exceeded")
    if not human_credit_allowance_verified:
        blockers.append("ibm_credit_billing_runtime_allowance_unverified")
    if missing_sources:
        decision = "REPLACEMENT_CREDIT_ALLOWANCE_DECISION_PACKET_INCOMPLETE"
    elif any(blocker for blocker in blockers if blocker != "ibm_credit_billing_runtime_allowance_unverified"):
        decision = "REPLACEMENT_CREDIT_ALLOWANCE_DECISION_PACKET_BLOCKED"
    elif human_credit_allowance_verified:
        decision = "REPLACEMENT_CREDIT_ALLOWANCE_VERIFIED_READY_FOR_EXACT_APPROVAL_REVIEW"
    else:
        decision = "REPLACEMENT_CREDIT_ALLOWANCE_READY_FOR_HUMAN_ATTESTATION_NOT_LIVE"
    return {
        "schema_version": STAGE194_SCHEMA_VERSION,
        "stage": "stage194_replacement_credit_allowance_decision_packet",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "estimated_total_job_count": estimated_job_count,
        "estimated_total_shots": estimated_shots,
        "budget_cap_usd": budget_cap,
        "queue_depth_cap": queue_depth_cap,
        "backend_metadata": backend_metadata,
        "queue_depth_within_cap": queue_within_cap,
        "human_credit_allowance_verified": human_credit_allowance_verified,
        "decision_items": decision_items,
        "no_hardware_submission": True,
        "read_only_backend_lookup_attempted": False,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "local budget and queue caps are compared against replacement-run exposure and read-only backend status",
                "credit/billing/Runtime allowance is isolated as a human account-side attestation",
                "exact live-run approval remains a later, separate gate",
            ],
            "excluded": [
                "hardware job submission",
                "Sampler or Estimator runtime execution",
                "provider credentials, token values, CRN values, or account secrets",
                "provider-side IBM credit balance or dollar-cost verification",
                "acceptance of the exact live-run approval phrase",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Have the user verify IBM credit, billing plan, Runtime allowance, and willingness to spend within the local "
            "budget cap; if verified, rerun Stage194 with human_credit_allowance_verified=true before exact approval review."
        ),
    }


def write_stage194_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "estimated_total_job_count",
        "estimated_total_shots",
        "budget_cap_usd",
        "queue_depth_cap",
        "queue_depth_within_cap",
        "human_credit_allowance_verified",
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
        for item in result["decision_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage194_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"estimated_total_job_count: {result['estimated_total_job_count']}")
    print(f"estimated_total_shots: {result['estimated_total_shots']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"queue_depth_within_cap: {result['queue_depth_within_cap']}")
    print(f"human_credit_allowance_verified: {result['human_credit_allowance_verified']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
