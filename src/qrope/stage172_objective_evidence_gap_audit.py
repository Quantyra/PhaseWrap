from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE172_SCHEMA_VERSION = "qrope_stage172_objective_evidence_gap_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE103_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage103_robustness_metric_preregistration" / "results.json"
DEFAULT_STAGE137_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage137_auditability_metric_evaluator" / "results.json"
DEFAULT_STAGE138_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage138_objective_claim_gate" / "results.json"
DEFAULT_STAGE148_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage148_first_provider_statistical_interpretation_gate" / "results.json"
DEFAULT_STAGE170_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage170_ibm_hardware_pause_resolution_packet" / "results.json"
DEFAULT_STAGE171_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage171_post_result_analysis_dry_run_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage172_objective_evidence_gap_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE170_READY_DECISIONS = {
    "IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION",
    "IBM_HARDWARE_PAUSE_READY_FOR_FINAL_HUMAN_GO_NO_GO",
}
STAGE171_READY_DECISIONS = {
    "POST_RESULT_ANALYSIS_DRY_RUN_READY_AWAITING_PROVIDER_RESULTS",
    "POST_RESULT_ANALYSIS_DRY_RUN_READY_FOR_RESULT_INTERPRETATION",
}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _requirement(requirement_id: str, description: str, evidence: Any, satisfied: bool, blocker: str | None) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "description": description,
        "evidence": evidence,
        "satisfied": bool(satisfied),
        "blocker": blocker if not satisfied else None,
    }


def run_stage172_objective_evidence_gap_audit(
    *,
    stage103_results_path: Path = DEFAULT_STAGE103_RESULTS,
    stage137_results_path: Path = DEFAULT_STAGE137_RESULTS,
    stage138_results_path: Path = DEFAULT_STAGE138_RESULTS,
    stage148_results_path: Path = DEFAULT_STAGE148_RESULTS,
    stage170_results_path: Path = DEFAULT_STAGE170_RESULTS,
    stage171_results_path: Path = DEFAULT_STAGE171_RESULTS,
) -> dict[str, Any]:
    stage103 = _load_json(stage103_results_path)
    stage137 = _load_json(stage137_results_path)
    stage138 = _load_json(stage138_results_path)
    stage148 = _load_json(stage148_results_path)
    stage170 = _load_json(stage170_results_path)
    stage171 = _load_json(stage171_results_path)
    sources = [
        (stage103_results_path, stage103),
        (stage137_results_path, stage137),
        (stage138_results_path, stage138),
        (stage148_results_path, stage148),
        (stage170_results_path, stage170),
        (stage171_results_path, stage171),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    stage103_matched_surface_ready = bool(stage103.get("stage104_matched_surface_ready")) if isinstance(stage103, dict) else False
    stage103_ready = bool(stage103.get("ready_to_interpret_hardware_metrics")) if isinstance(stage103, dict) else False
    stage137_ready = int(stage137.get("ready_window_count") or 0) > 0 if isinstance(stage137, dict) else False
    stage148_ready = bool(stage148.get("statistical_interpretation_ready")) if isinstance(stage148, dict) else False
    stage138_terminal = bool(stage138.get("objective_terminal")) if isinstance(stage138, dict) else False
    stage138_supported = bool(stage138.get("objective_supported")) if isinstance(stage138, dict) else False
    stage170_ready = stage170.get("decision") in STAGE170_READY_DECISIONS if isinstance(stage170, dict) else False
    stage171_ready = stage171.get("decision") in STAGE171_READY_DECISIONS if isinstance(stage171, dict) else False
    provider_results_missing = bool(stage171.get("provider_results_missing")) if isinstance(stage171, dict) else True
    requirements = [
        _requirement(
            "fixed_width_matched_surface",
            "Fixed-width matched PhaseWrap/RoPE-like/sinusoidal-like/ALIBI-like/no-position comparator surface is prepared.",
            {
                "stage103_decision": stage103.get("decision") if isinstance(stage103, dict) else None,
                "stage104_matched_surface_ready": stage103_matched_surface_ready,
                "stage104_complete_matched_group_count": stage103.get("stage104_complete_matched_group_count") if isinstance(stage103, dict) else None,
            },
            stage103_matched_surface_ready,
            "fixed_width_matched_surface_not_ready",
        ),
        _requirement(
            "hardware_result_counts",
            "Real provider packet/calibration counts exist for the locked first-provider hardware scope.",
            {
                "stage103_missing_execution_count": stage103.get("missing_execution_count") if isinstance(stage103, dict) else None,
                "stage171_provider_results_missing": provider_results_missing,
                "stage171_missing_job_count": stage171.get("missing_job_count") if isinstance(stage171, dict) else None,
            },
            not provider_results_missing and stage103_ready,
            "hardware_result_counts_missing",
        ),
        _requirement(
            "statistical_interpretation",
            "First-provider statistical interpretation has calibrated lane evidence and shot-noise separation where needed.",
            {
                "stage148_decision": stage148.get("decision") if isinstance(stage148, dict) else None,
                "statistical_interpretation_ready": stage148_ready,
                "ready_calibration_record_count": stage148.get("ready_calibration_record_count") if isinstance(stage148, dict) else None,
                "shot_noise_separated_lane_count": stage148.get("shot_noise_separated_lane_count") if isinstance(stage148, dict) else None,
            },
            stage148_ready,
            "statistical_interpretation_not_ready",
        ),
        _requirement(
            "robustness_terminal",
            "Robustness gate is terminal for the objective, either supported or not supported from complete evidence.",
            {
                "stage138_stage110_decision": stage138.get("stage110_decision") if isinstance(stage138, dict) else None,
                "robustness_terminal": stage138.get("robustness_terminal") if isinstance(stage138, dict) else None,
                "robustness_supported": stage138.get("robustness_supported") if isinstance(stage138, dict) else None,
            },
            bool(stage138.get("robustness_terminal")) if isinstance(stage138, dict) else False,
            "robustness_gate_not_terminal",
        ),
        _requirement(
            "auditability_terminal",
            "Auditability gate is terminal for the objective, either supported or not supported from complete evidence.",
            {
                "stage137_decision": stage137.get("decision") if isinstance(stage137, dict) else None,
                "stage137_ready_window_count": stage137.get("ready_window_count") if isinstance(stage137, dict) else None,
                "stage138_auditability_ready": stage138.get("auditability_ready") if isinstance(stage138, dict) else None,
            },
            bool(stage138.get("auditability_ready")) if isinstance(stage138, dict) else False,
            "auditability_gate_not_terminal",
        ),
        _requirement(
            "objective_terminal",
            "Objective-level Stage138 claim gate is terminal before any final conclusion is stated.",
            {
                "stage138_decision": stage138.get("decision") if isinstance(stage138, dict) else None,
                "objective_terminal": stage138_terminal,
                "objective_supported": stage138_supported,
            },
            stage138_terminal,
            "objective_gate_not_terminal",
        ),
        _requirement(
            "pre_hardware_pause_ready",
            "IBM credit/provider pause packet and post-result analysis dry-run are ready before live execution.",
            {
                "stage170_decision": stage170.get("decision") if isinstance(stage170, dict) else None,
                "stage171_decision": stage171.get("decision") if isinstance(stage171, dict) else None,
            },
            stage170_ready and stage171_ready,
            "pre_hardware_pause_or_post_result_dry_run_not_ready",
        ),
    ]
    blockers = [record["blocker"] for record in requirements if record["blocker"]]
    if missing_sources:
        blockers.append("source_artifacts_missing")
    decision = (
        "OBJECTIVE_EVIDENCE_GAP_AUDIT_INCOMPLETE"
        if missing_sources
        else "OBJECTIVE_EVIDENCE_GAP_AUDIT_COMPLETE_OBJECTIVE_TERMINAL"
        if not blockers and stage138_terminal
        else "OBJECTIVE_EVIDENCE_GAP_AUDIT_HARDWARE_RESULTS_REQUIRED"
        if "hardware_result_counts_missing" in blockers
        else "OBJECTIVE_EVIDENCE_GAP_AUDIT_BLOCKED"
    )
    return {
        "schema_version": STAGE172_SCHEMA_VERSION,
        "stage": "stage172_objective_evidence_gap_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "requirement_records": requirements,
        "satisfied_requirement_count": sum(1 for record in requirements if record["satisfied"]),
        "unsatisfied_requirement_count": sum(1 for record in requirements if not record["satisfied"]),
        "objective_terminal": stage138_terminal,
        "objective_supported": stage138_supported,
        "provider_results_missing": provider_results_missing,
        "stage170_ready": stage170_ready,
        "stage171_ready": stage171_ready,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "requirement-by-requirement evidence map for the persistent noisy-hardware objective",
                "explicit distinction between simulated/pre-hardware readiness and terminal noisy-hardware evidence",
                "confirmation that the fixed-width matched comparator surface is ready while real hardware counts remain absent",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "IBM credit balance or dollar cost verification",
                "execution of post-result analysis commands",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Resolve IBM credit/provider state, execute only after exact approval, collect locked provider results, run the "
            "validated Stage160 sequence, and require Stage138 to become terminal before answering the objective."
        ),
    }


def write_stage172_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "satisfied_requirement_count": result["satisfied_requirement_count"],
        "unsatisfied_requirement_count": result["unsatisfied_requirement_count"],
        "objective_terminal": result["objective_terminal"],
        "objective_supported": result["objective_supported"],
        "provider_results_missing": result["provider_results_missing"],
        "stage170_ready": result["stage170_ready"],
        "stage171_ready": result["stage171_ready"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
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
        writer = csv.DictWriter(handle, fieldnames=("requirement_id", "satisfied", "blocker", "description"))
        writer.writeheader()
        for record in result["requirement_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage172_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"satisfied_requirement_count: {result['satisfied_requirement_count']}")
    print(f"unsatisfied_requirement_count: {result['unsatisfied_requirement_count']}")
    print(f"objective_terminal: {result['objective_terminal']}")
    print(f"provider_results_missing: {result['provider_results_missing']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
