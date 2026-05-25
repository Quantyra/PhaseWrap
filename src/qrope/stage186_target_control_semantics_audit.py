from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage182_balanced_phase_window_candidate_screen import DEFAULT_OUTPUT_DIR as STAGE182_OUTPUT_DIR
from qrope.stage183_contrast_amplified_delta_candidate_screen import DEFAULT_OUTPUT_DIR as STAGE183_OUTPUT_DIR
from qrope.stage184_error_orthogonalized_components_candidate_screen import DEFAULT_OUTPUT_DIR as STAGE184_OUTPUT_DIR
from qrope.stage185_redesign_sweep_disposition import DEFAULT_OUTPUT_DIR as STAGE185_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE186_SCHEMA_VERSION = "qrope_stage186_target_control_semantics_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE182_RESULTS = STAGE182_OUTPUT_DIR / "results.json"
DEFAULT_STAGE183_RESULTS = STAGE183_OUTPUT_DIR / "results.json"
DEFAULT_STAGE184_RESULTS = STAGE184_OUTPUT_DIR / "results.json"
DEFAULT_STAGE185_RESULTS = STAGE185_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage186_target_control_semantics_audit"
STAGE185_EXHAUSTED = "REDESIGN_SWEEP_EXHAUSTED_NO_HARDWARE_REOPEN"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _negative_margin_counts(payloads: list[dict[str, Any]]) -> dict[str, int]:
    positional_negative = 0
    control_negative = 0
    total = 0
    for payload in payloads:
        for record in payload.get("candidate_records", []):
            if not isinstance(record, dict):
                continue
            total += 1
            positional = record.get("min_positional_margin_shot_quanta")
            control = record.get("min_control_margin_shot_quanta")
            if positional is not None and float(positional) < 0.0:
                positional_negative += 1
            if control is not None and float(control) < 0.0:
                control_negative += 1
    return {
        "candidate_group_count": total,
        "negative_positional_margin_group_count": positional_negative,
        "negative_control_margin_group_count": control_negative,
    }


def _candidate_family_record(path: Path, payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "result_path": str(path.as_posix()),
            "design_family_id": None,
            "decision": None,
            "candidate_group_count": 0,
            "reopen_candidate_count": 0,
            "negative_positional_margin_group_count": 0,
            "negative_control_margin_group_count": 0,
            "control_margin_all_negative": False,
        }
    counts = _negative_margin_counts([payload])
    group_count = counts["candidate_group_count"]
    control_negative = counts["negative_control_margin_group_count"]
    return {
        "result_path": str(path.as_posix()),
        "design_family_id": payload.get("design_family_id"),
        "decision": payload.get("decision"),
        "candidate_group_count": group_count,
        "reopen_candidate_count": int(payload.get("reopen_candidate_count") or 0),
        "negative_positional_margin_group_count": counts["negative_positional_margin_group_count"],
        "negative_control_margin_group_count": control_negative,
        "control_margin_all_negative": group_count > 0 and control_negative == group_count,
    }


def run_stage186_target_control_semantics_audit(
    *,
    stage182_results_path: Path = DEFAULT_STAGE182_RESULTS,
    stage183_results_path: Path = DEFAULT_STAGE183_RESULTS,
    stage184_results_path: Path = DEFAULT_STAGE184_RESULTS,
    stage185_results_path: Path = DEFAULT_STAGE185_RESULTS,
) -> dict[str, Any]:
    candidate_sources = [
        (stage182_results_path, _load_json(stage182_results_path)),
        (stage183_results_path, _load_json(stage183_results_path)),
        (stage184_results_path, _load_json(stage184_results_path)),
    ]
    stage185 = _load_json(stage185_results_path)
    sources = candidate_sources + [(stage185_results_path, stage185)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage185, dict) and stage185.get("decision") != STAGE185_EXHAUSTED:
        blockers.append("stage185_redesign_sweep_not_exhausted")

    candidate_payloads = [payload for _, payload in candidate_sources if isinstance(payload, dict)]
    family_records = [_candidate_family_record(path, payload if isinstance(payload, dict) else None) for path, payload in candidate_sources]
    counts = _negative_margin_counts(candidate_payloads)
    total_reopen_candidates = sum(int(record["reopen_candidate_count"]) for record in family_records)
    all_control_margins_negative = bool(
        counts["candidate_group_count"] > 0
        and counts["negative_control_margin_group_count"] == counts["candidate_group_count"]
    )
    raw_mae_control_dominance_observed = bool(all_control_margins_negative and total_reopen_candidates == 0)
    if blockers:
        decision = "TARGET_CONTROL_SEMANTICS_AUDIT_INCOMPLETE"
    elif raw_mae_control_dominance_observed:
        decision = "TARGET_CONTROL_SEMANTICS_REVISION_REQUIRED_BEFORE_HARDWARE"
    else:
        decision = "TARGET_CONTROL_SEMANTICS_AUDIT_DOES_NOT_REQUIRE_REVISION"

    return {
        "schema_version": STAGE186_SCHEMA_VERSION,
        "stage": "stage186_target_control_semantics_audit",
        "status": "completed" if not blockers else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "candidate_family_count": len(family_records),
        "candidate_family_records": family_records,
        "candidate_group_count": counts["candidate_group_count"],
        "negative_positional_margin_group_count": counts["negative_positional_margin_group_count"],
        "negative_control_margin_group_count": counts["negative_control_margin_group_count"],
        "all_control_margins_negative": all_control_margins_negative,
        "total_reopen_candidate_count": total_reopen_candidates,
        "raw_mae_control_dominance_observed": raw_mae_control_dominance_observed,
        "semantics_finding": {
            "current_control": "zero-component no-position control",
            "current_primary_metric": "mean absolute score error against each family own ideal score",
            "observed_failure_mode": (
                "under symmetric stochastic shrink/readout, the zero-component control remains close to its own ideal "
                "while nonzero positional encodings incur score shrinkage, so strict raw-MAE wins over control are structurally hard"
            ),
            "interpretation": (
                "the failed redesign sweep is a valid hardware NO-GO for the current preregistered semantics, but it does not "
                "settle whether PhaseWrap has value under a metric that compares noise sensitivity or auditability at matched "
                "nonzero signal exposure"
            ),
        },
        "replacement_semantics_requirements": [
            "preregister a nonzero matched null/control exposure or a paired-delta null that experiences the same readout/shrink channel",
            "preserve fixed width at two measured qubits and keep product plus CX templates unless a new plan explicitly supersedes them",
            "keep PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and control families present in every comparison group",
            "use a metric that separates absolute task score error from noise sensitivity, such as normalized shrink error or slope retention",
            "freeze thresholds before simulation or hardware selection and require both IBM-informed simulated stability and independent seed stability",
            "forbid using live hardware results to tune the replacement target/control semantics",
        ],
        "simulated_only": True,
        "ibm_backend_properties_informed": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "hardware_path_status": "current_ibm_328_job_run_remains_archived",
        "claim_boundary": {
            "supported": [
                "the current raw-MAE plus zero-control semantics produced universal negative control margins across the Stage182-184 redesign sweep",
                "the current preregistered semantics should not be used to reopen IBM hardware",
                "a replacement target/control plan must be preregistered before any further hardware consideration",
            ],
            "excluded": [
                "hardware job submission",
                "a final noisy-hardware robustness or auditability conclusion",
                "a claim that PhaseWrap has no possible value under future fair semantics",
                "a replacement packet freeze or simulation result",
            ],
        },
        "next_gate": (
            "Create a replacement target/control preregistration that keeps fixed width but gives controls matched nonzero noise exposure, "
            "then run simulated IBM-informed screening before reconsidering hardware."
        ),
    }


def write_stage186_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "candidate_family_count",
        "candidate_group_count",
        "negative_positional_margin_group_count",
        "negative_control_margin_group_count",
        "all_control_margins_negative",
        "total_reopen_candidate_count",
        "raw_mae_control_dominance_observed",
        "semantics_finding",
        "replacement_semantics_requirements",
        "simulated_only",
        "ibm_backend_properties_informed",
        "no_hardware_submission",
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
                "design_family_id",
                "decision",
                "candidate_group_count",
                "negative_positional_margin_group_count",
                "negative_control_margin_group_count",
                "control_margin_all_negative",
            ),
        )
        writer.writeheader()
        for record in result["candidate_family_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage186_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"candidate_group_count: {result['candidate_group_count']}")
    print(f"negative_control_margin_group_count: {result['negative_control_margin_group_count']}")
    print(f"raw_mae_control_dominance_observed: {result['raw_mae_control_dominance_observed']}")
    print(f"next_gate: {result['next_gate']}")
