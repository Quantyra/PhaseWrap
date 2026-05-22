from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE175_SCHEMA_VERSION = "qrope_stage175_first_provider_preresult_readiness_synthesis_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE160_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage160_first_provider_post_run_analysis_packet" / "results.json"
DEFAULT_STAGE163_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage163_first_provider_prerun_lock" / "results.json"
DEFAULT_STAGE170_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage170_ibm_hardware_pause_resolution_packet" / "results.json"
DEFAULT_STAGE171_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage171_post_result_analysis_dry_run_audit" / "results.json"
DEFAULT_STAGE172_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage172_objective_evidence_gap_audit" / "results.json"
DEFAULT_STAGE173_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage173_locked_result_ingestion_contract_audit" / "results.json"
DEFAULT_STAGE174_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage174_locked_interpretation_surface_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage175_first_provider_preresult_readiness_synthesis"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
READY_DECISIONS = {
    "stage160": {"FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS"},
    "stage163": {"FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL"},
    "stage170": {"IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION", "IBM_HARDWARE_PAUSE_READY_FOR_FINAL_HUMAN_GO_NO_GO"},
    "stage171": {"POST_RESULT_ANALYSIS_DRY_RUN_READY_AWAITING_PROVIDER_RESULTS"},
    "stage172": {"OBJECTIVE_EVIDENCE_GAP_AUDIT_HARDWARE_RESULTS_REQUIRED"},
    "stage173": {"LOCKED_RESULT_INGESTION_CONTRACT_READY_AWAITING_PROVIDER_RESULTS"},
    "stage174": {"LOCKED_INTERPRETATION_SURFACE_READY_AWAITING_PROVIDER_RESULTS"},
}
BOUNDARY_BLOCKER_STAGES = {"stage160", "stage172"}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _stage_record(stage_id: str, payload: dict[str, Any] | None, purpose: str) -> dict[str, Any]:
    decision = payload.get("decision") if isinstance(payload, dict) else None
    blockers = payload.get("blockers", []) if isinstance(payload, dict) else []
    ready = decision in READY_DECISIONS[stage_id] and (not blockers or stage_id in BOUNDARY_BLOCKER_STAGES)
    return {
        "stage_id": stage_id,
        "decision": decision,
        "expected_decisions": sorted(READY_DECISIONS[stage_id]),
        "ready": ready,
        "blockers": blockers,
        "purpose": purpose,
    }


def run_stage175_preresult_readiness_synthesis(
    *,
    stage160_results_path: Path = DEFAULT_STAGE160_RESULTS,
    stage163_results_path: Path = DEFAULT_STAGE163_RESULTS,
    stage170_results_path: Path = DEFAULT_STAGE170_RESULTS,
    stage171_results_path: Path = DEFAULT_STAGE171_RESULTS,
    stage172_results_path: Path = DEFAULT_STAGE172_RESULTS,
    stage173_results_path: Path = DEFAULT_STAGE173_RESULTS,
    stage174_results_path: Path = DEFAULT_STAGE174_RESULTS,
) -> dict[str, Any]:
    stage160 = _load_json(stage160_results_path)
    stage163 = _load_json(stage163_results_path)
    stage170 = _load_json(stage170_results_path)
    stage171 = _load_json(stage171_results_path)
    stage172 = _load_json(stage172_results_path)
    stage173 = _load_json(stage173_results_path)
    stage174 = _load_json(stage174_results_path)
    sources = [
        (stage160_results_path, stage160),
        (stage163_results_path, stage163),
        (stage170_results_path, stage170),
        (stage171_results_path, stage171),
        (stage172_results_path, stage172),
        (stage173_results_path, stage173),
        (stage174_results_path, stage174),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    stage_records = [
        _stage_record("stage160", stage160, "post-result analysis command packet is ready and awaiting provider results"),
        _stage_record("stage163", stage163, "first-provider IBM job shards are hash-locked before execution"),
        _stage_record("stage170", stage170, "IBM hardware pause packet is ready for credit/provider resolution"),
        _stage_record("stage171", stage171, "post-result analysis command sequence has a no-submit dry-run readiness audit"),
        _stage_record("stage172", stage172, "objective evidence-gap audit is correctly waiting on hardware results"),
        _stage_record("stage173", stage173, "locked result-ingestion contract is ready for provider result JSONL records"),
        _stage_record("stage174", stage174, "locked jobs cover the fixed-width interpretation surface for stable lanes"),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    for record in stage_records:
        if not record["ready"]:
            blockers.append(f"{record['stage_id']}_not_ready")
    locked_job_count = stage163.get("locked_job_count") if isinstance(stage163, dict) else None
    exposure_job_count = stage170.get("locked_job_count") if isinstance(stage170, dict) else None
    ingestion_job_count = stage173.get("locked_job_count") if isinstance(stage173, dict) else None
    if len({locked_job_count, exposure_job_count, ingestion_job_count}) != 1:
        blockers.append("locked_job_count_mismatch")
    locked_total_shots = stage163.get("locked_total_shots") if isinstance(stage163, dict) else None
    exposure_total_shots = stage170.get("locked_total_shots") if isinstance(stage170, dict) else None
    ingestion_total_shots = stage173.get("locked_total_shots") if isinstance(stage173, dict) else None
    if len({locked_total_shots, exposure_total_shots, ingestion_total_shots}) != 1:
        blockers.append("locked_total_shots_mismatch")
    stable_lanes_170 = set(stage170.get("stage169_stable_target_lanes", [])) if isinstance(stage170, dict) else set()
    stable_lanes_174 = set(stage174.get("stable_target_lanes", [])) if isinstance(stage174, dict) else set()
    if stable_lanes_170 != stable_lanes_174 or not stable_lanes_174:
        blockers.append("stable_lane_scope_mismatch")
    provider_results_missing = bool(stage172.get("provider_results_missing")) if isinstance(stage172, dict) else True
    if provider_results_missing is not True:
        blockers.append("provider_results_missing_boundary_not_active")
    credit_balance_verified = bool(stage170.get("credit_balance_verified")) if isinstance(stage170, dict) else False
    hardware_approval_ready = credit_balance_verified and not blockers
    decision = (
        "FIRST_PROVIDER_PRERESULT_READINESS_SYNTHESIS_INCOMPLETE"
        if missing_sources
        else "FIRST_PROVIDER_PRERESULT_READY_FOR_CREDIT_PROVIDER_RESOLUTION"
        if not blockers and not credit_balance_verified
        else "FIRST_PROVIDER_PRERESULT_READY_FOR_FINAL_HUMAN_GO_NO_GO"
        if hardware_approval_ready
        else "FIRST_PROVIDER_PRERESULT_READINESS_SYNTHESIS_BLOCKED"
    )
    return {
        "schema_version": STAGE175_SCHEMA_VERSION,
        "stage": "stage175_first_provider_preresult_readiness_synthesis",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage_records": stage_records,
        "ready_stage_count": sum(1 for record in stage_records if record["ready"]),
        "stage_count": len(stage_records),
        "first_unlock_provider": stage170.get("first_unlock_provider") if isinstance(stage170, dict) else None,
        "credit_balance_verified": credit_balance_verified,
        "approval_phrase_required": stage170.get("approval_phrase_required") if isinstance(stage170, dict) else None,
        "locked_job_count": locked_job_count,
        "locked_total_shots": locked_total_shots,
        "stable_target_lanes": sorted(stable_lanes_174),
        "matched_packet_job_count": stage174.get("matched_packet_job_count") if isinstance(stage174, dict) else None,
        "calibration_count_by_window": stage174.get("calibration_count_by_window") if isinstance(stage174, dict) else None,
        "provider_results_missing": provider_results_missing,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "single no-submit synthesis of the current first-provider pre-result readiness chain",
                "cross-check that Stage163/170/173 agree on locked IBM job and shot exposure",
                "cross-check that Stage170 and Stage174 agree on the stable locked interpretation lanes",
                "explicit separation between readiness to resolve IBM credit/provider state and a noisy-hardware conclusion",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "IBM credit balance or dollar cost verification",
                "provider result records",
                "Stage103/137/148/138 interpretation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Resolve IBM credit/provider state with the user. Only after a final human GO and exact approval phrase, "
            "execute the locked IBM run, collect provider results, and run the validated post-result sequence through Stage138."
        ),
    }


def write_stage175_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "ready_stage_count": result["ready_stage_count"],
        "stage_count": result["stage_count"],
        "first_unlock_provider": result["first_unlock_provider"],
        "credit_balance_verified": result["credit_balance_verified"],
        "locked_job_count": result["locked_job_count"],
        "locked_total_shots": result["locked_total_shots"],
        "stable_target_lanes": result["stable_target_lanes"],
        "matched_packet_job_count": result["matched_packet_job_count"],
        "provider_results_missing": result["provider_results_missing"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
        "explicit_user_approval_required": result["explicit_user_approval_required"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "runnable_commands_recorded": result["runnable_commands_recorded"],
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
        writer = csv.DictWriter(handle, fieldnames=("stage_id", "decision", "ready", "purpose", "blockers"))
        writer.writeheader()
        for record in result["stage_records"]:
            writer.writerow(
                {
                    "stage_id": record["stage_id"],
                    "decision": record["decision"],
                    "ready": record["ready"],
                    "purpose": record["purpose"],
                    "blockers": "; ".join(record["blockers"]),
                }
            )
    return paths


def print_stage175_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_stage_count: {result['ready_stage_count']}/{result['stage_count']}")
    print(f"locked_job_count: {result['locked_job_count']}")
    print(f"locked_total_shots: {result['locked_total_shots']}")
    print(f"credit_balance_verified: {result['credit_balance_verified']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
