from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage200_reduced_scope_attestation_intake import DEFAULT_OUTPUT_DIR as STAGE200_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE201_SCHEMA_VERSION = "qrope_stage201_reduced_scope_exact_approval_review_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE200_RESULTS = STAGE200_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage201_reduced_scope_exact_approval_review"
STAGE200_ACCEPTED = "REDUCED_SCOPE_CREDIT_ATTESTATION_ACCEPTED_READY_FOR_EXACT_APPROVAL_REVIEW"
STAGE200_AWAITING = "REDUCED_SCOPE_ATTESTATION_INTAKE_AWAITING_EXACT_PHRASE"
REDUCED_SCOPE_APPROVAL_PHRASE = "APPROVE IBM RUNTIME REDUCED SCOPE STAGE199 LIVE RUN"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage201_reduced_scope_exact_approval_review(
    *,
    stage200_results_path: Path = DEFAULT_STAGE200_RESULTS,
    provided_approval_phrase: str | None = None,
) -> dict[str, Any]:
    stage200 = _load_json(stage200_results_path)
    missing_sources = [] if isinstance(stage200, dict) else [str(stage200_results_path.as_posix())]
    stage200_decision = stage200.get("decision") if isinstance(stage200, dict) else None
    credit_attested = bool(stage200.get("human_credit_allowance_verified")) if isinstance(stage200, dict) else False
    attestation_ready = stage200_decision == STAGE200_ACCEPTED and credit_attested
    attestation_awaiting = stage200_decision == STAGE200_AWAITING and not credit_attested
    phrase_present = provided_approval_phrase is not None
    phrase_matches = provided_approval_phrase == REDUCED_SCOPE_APPROVAL_PHRASE
    approval_items = [
        _item(
            "credit_attestation_gate",
            "verified" if attestation_ready else "attestation_required" if attestation_awaiting else "blocked",
            "Reduced-scope exact approval requires Stage200 credit attestation to be accepted first.",
            {
                "stage200_decision": stage200_decision,
                "human_credit_allowance_verified": credit_attested,
                "required_attestation_phrase": stage200.get("required_attestation_phrase") if isinstance(stage200, dict) else None,
            },
        ),
        _item(
            "reduced_scope_exposure",
            "recorded" if isinstance(stage200, dict) else "missing",
            "Approver must have the reduced-scope exposure and cap available before exact approval can be accepted.",
            {
                "scope_id": stage200.get("scope_id") if isinstance(stage200, dict) else None,
                "estimated_total_job_count": stage200.get("estimated_total_job_count") if isinstance(stage200, dict) else None,
                "estimated_total_shots": stage200.get("estimated_total_shots") if isinstance(stage200, dict) else None,
                "budget_cap_usd": stage200.get("budget_cap_usd") if isinstance(stage200, dict) else None,
            },
        ),
        _item(
            "exact_reduced_scope_approval_phrase",
            "accepted" if attestation_ready and phrase_matches else "not_requested" if not attestation_ready else "missing_or_mismatched",
            "The reduced-scope live approval phrase is only evaluated after credit attestation and must match exactly.",
            {
                "approval_phrase_required": REDUCED_SCOPE_APPROVAL_PHRASE,
                "provided_approval_phrase_present": phrase_present,
                "approval_phrase_matches": phrase_matches if attestation_ready else False,
            },
        ),
        _item(
            "live_execution_boundary",
            "runner_preparation_review_allowed" if attestation_ready and phrase_matches else "live_run_disallowed",
            "This gate does not submit hardware; at most it allows later reduced-scope live-runner preparation review.",
            {"hardware_submitted_here": False, "live_submit_command_created_here": False},
        ),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not attestation_ready:
        blockers.append("reduced_scope_credit_attestation_not_accepted")
    if attestation_ready and not phrase_matches:
        blockers.append("exact_reduced_scope_approval_phrase_missing_or_mismatched")
    if missing_sources:
        decision = "REDUCED_SCOPE_EXACT_APPROVAL_REVIEW_INCOMPLETE"
    elif attestation_ready and phrase_matches:
        decision = "REDUCED_SCOPE_EXACT_APPROVAL_ACCEPTED_READY_FOR_LIVE_RUNNER_PREPARATION_REVIEW"
    elif attestation_awaiting:
        decision = "REDUCED_SCOPE_EXACT_APPROVAL_REVIEW_BLOCKED_CREDIT_ATTESTATION_REQUIRED"
    else:
        decision = "REDUCED_SCOPE_EXACT_APPROVAL_REVIEW_BLOCKED"
    return {
        "schema_version": STAGE201_SCHEMA_VERSION,
        "stage": "stage201_reduced_scope_exact_approval_review",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage200_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "stage200_decision": stage200_decision,
        "human_credit_allowance_verified": credit_attested,
        "scope_id": stage200.get("scope_id") if isinstance(stage200, dict) else None,
        "hardware_scope_label": stage200.get("hardware_scope_label") if isinstance(stage200, dict) else None,
        "estimated_total_job_count": stage200.get("estimated_total_job_count") if isinstance(stage200, dict) else None,
        "estimated_total_shots": stage200.get("estimated_total_shots") if isinstance(stage200, dict) else None,
        "budget_cap_usd": stage200.get("budget_cap_usd") if isinstance(stage200, dict) else None,
        "approval_phrase_required": REDUCED_SCOPE_APPROVAL_PHRASE,
        "provided_approval_phrase_present": phrase_present,
        "approval_phrase_matches": phrase_matches if attestation_ready else False,
        "approval_items": approval_items,
        "no_hardware_submission": True,
        "live_submit_command_created": False,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "reduced-scope exact approval phrase is isolated from credit attestation",
                "approval phrase matching is only accepted after Stage200 records exact credit attestation",
                "successful review permits only later reduced-scope live-runner preparation review",
            ],
            "excluded": [
                "hardware job submission",
                "provider-side IBM credit balance verification",
                "creation of a runnable live-submit command",
                "approval for the original full 4096-shot scope",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Resolve Stage200 credit attestation first. If the exact reduced-scope approval phrase is then provided, rerun "
            "Stage201 and proceed only to reduced-scope live-runner preparation review, not direct submission."
        ),
    }


def write_stage201_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "stage200_decision",
        "human_credit_allowance_verified",
        "scope_id",
        "hardware_scope_label",
        "estimated_total_job_count",
        "estimated_total_shots",
        "budget_cap_usd",
        "approval_phrase_required",
        "provided_approval_phrase_present",
        "approval_phrase_matches",
        "no_hardware_submission",
        "live_submit_command_created",
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
        for item in result["approval_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage201_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"scope_id: {result['scope_id']}")
    print(f"human_credit_allowance_verified: {result['human_credit_allowance_verified']}")
    print(f"approval_phrase_required: {result['approval_phrase_required']}")
    print(f"provided_approval_phrase_present: {result['provided_approval_phrase_present']}")
    print(f"approval_phrase_matches: {result['approval_phrase_matches']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
