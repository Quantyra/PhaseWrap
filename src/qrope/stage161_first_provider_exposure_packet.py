from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


STAGE161_SCHEMA_VERSION = "qrope_stage161_first_provider_exposure_packet_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE157_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage157_first_provider_live_run_approval_packet" / "results.json"
DEFAULT_STAGE159_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage159_first_provider_backend_preflight" / "results.json"
DEFAULT_STAGE160_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage160_first_provider_post_run_analysis_packet" / "results.json"
DEFAULT_STAGE114_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage161_first_provider_exposure_packet"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE157_READY = "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY"
STAGE159_READY = "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL"
STAGE160_READY = "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS"
PROVIDER = "ibm_runtime"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _approval_windows(stage157: dict[str, Any] | None, provider: str) -> list[dict[str, Any]]:
    if not isinstance(stage157, dict):
        return []
    return [
        record
        for record in stage157.get("approval_records", [])
        if isinstance(record, dict) and record.get("provider") == provider and record.get("command_authorized") is True
    ]


def _job_shard_path(stage114_output_dir: Path, provider: str, window_id: str) -> Path:
    return stage114_output_dir / "job_shards" / provider / window_id / "jobs.jsonl"


def _result_path(stage114_output_dir: Path, provider: str, window_id: str) -> Path:
    return stage114_output_dir / "provider_results" / provider / window_id / "provider_job_results.jsonl"


def _window_record(stage114_output_dir: Path, provider: str, approval: dict[str, Any]) -> dict[str, Any]:
    window_id = str(approval.get("window_id") or "")
    job_shard = _job_shard_path(stage114_output_dir, provider, window_id)
    result_path = _result_path(stage114_output_dir, provider, window_id)
    jobs = _load_jsonl(job_shard)
    job_kind_counts: Counter[str] = Counter()
    encoding_family_counts: Counter[str] = Counter()
    shot_by_job_kind: defaultdict[str, int] = defaultdict(int)
    shot_by_family: defaultdict[str, int] = defaultdict(int)
    total_shots = 0
    unique_evidence_paths: set[str] = set()
    duplicate_job_ids: set[str] = set()
    seen_job_ids: set[str] = set()
    missing_fields = 0
    for job in jobs:
        job_id = str(job.get("job_id") or "")
        if job_id in seen_job_ids:
            duplicate_job_ids.add(job_id)
        if job_id:
            seen_job_ids.add(job_id)
        if not job_id or not job.get("job_kind") or not job.get("shots"):
            missing_fields += 1
        job_kind = str(job.get("job_kind") or "unknown")
        family = str(job.get("encoding_family") or "calibration")
        shots = _int(job.get("shots"))
        job_kind_counts[job_kind] += 1
        encoding_family_counts[family] += 1
        shot_by_job_kind[job_kind] += shots
        shot_by_family[family] += shots
        total_shots += shots
        if job.get("target_evidence_path"):
            unique_evidence_paths.add(str(job["target_evidence_path"]))
    provider_results_exist = result_path.exists()
    provider_result_records = _load_jsonl(result_path)
    blockers = []
    if not job_shard.exists():
        blockers.append("job_shard_missing")
    if _int(approval.get("job_count")) != len(jobs):
        blockers.append("approval_job_count_mismatch")
    if missing_fields:
        blockers.append("job_required_fields_missing")
    if duplicate_job_ids:
        blockers.append("duplicate_job_ids")
    return {
        "provider": provider,
        "window_id": window_id,
        "approved_job_count": approval.get("job_count"),
        "job_shard_path": str(job_shard.as_posix()),
        "job_shard_exists": job_shard.exists(),
        "job_count": len(jobs),
        "total_shots": total_shots,
        "job_kind_counts": dict(sorted(job_kind_counts.items())),
        "shot_by_job_kind": dict(sorted(shot_by_job_kind.items())),
        "encoding_family_counts": dict(sorted(encoding_family_counts.items())),
        "shot_by_encoding_family": dict(sorted(shot_by_family.items())),
        "target_evidence_path_count": len(unique_evidence_paths),
        "provider_results_path": str(result_path.as_posix()),
        "provider_results_file_exists": provider_results_exist,
        "provider_result_record_count": len(provider_result_records),
        "blockers": sorted(set(blockers)),
        "ready": not blockers,
    }


def run_stage161_exposure_packet(
    *,
    stage157_results_path: Path = DEFAULT_STAGE157_RESULTS,
    stage159_results_path: Path = DEFAULT_STAGE159_RESULTS,
    stage160_results_path: Path = DEFAULT_STAGE160_RESULTS,
    stage114_output_dir: Path = DEFAULT_STAGE114_OUTPUT_DIR,
) -> dict[str, Any]:
    stage157 = _load_json(stage157_results_path)
    stage159 = _load_json(stage159_results_path)
    stage160 = _load_json(stage160_results_path)
    sources = [
        (stage157_results_path, stage157),
        (stage159_results_path, stage159),
        (stage160_results_path, stage160),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    provider = str(stage157.get("first_unlock_provider") if isinstance(stage157, dict) else PROVIDER)
    approval_records = _approval_windows(stage157, provider)
    window_records = [_window_record(stage114_output_dir, provider, record) for record in approval_records]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if provider != PROVIDER:
        blockers.append("first_provider_not_ibm_runtime")
    if not isinstance(stage157, dict) or stage157.get("decision") != STAGE157_READY:
        blockers.append("stage157_approval_packet_not_ready")
    if not isinstance(stage159, dict) or stage159.get("decision") != STAGE159_READY:
        blockers.append("stage159_backend_preflight_not_ready")
    if not isinstance(stage160, dict) or stage160.get("decision") != STAGE160_READY:
        blockers.append("stage160_post_run_packet_not_ready_for_results")
    if not window_records:
        blockers.append("authorized_window_records_missing")
    if any(not record["ready"] for record in window_records):
        blockers.append("window_exposure_record_blockers_present")
    approved_job_count = sum(_int(record.get("approved_job_count")) for record in window_records)
    job_count = sum(record["job_count"] for record in window_records)
    if approved_job_count != job_count:
        blockers.append("approved_job_count_total_mismatch")
    total_provider_result_records = sum(record["provider_result_record_count"] for record in window_records)
    missing_result_records = max(job_count - total_provider_result_records, 0)
    decision = (
        "FIRST_PROVIDER_EXPOSURE_PACKET_INCOMPLETE"
        if missing_sources
        else "FIRST_PROVIDER_EXPOSURE_PACKET_READY_AWAITING_APPROVAL"
        if not blockers
        else "FIRST_PROVIDER_EXPOSURE_PACKET_BLOCKED"
    )
    return {
        "schema_version": STAGE161_SCHEMA_VERSION,
        "stage": "stage161_first_provider_exposure_packet",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage157_decision": stage157.get("decision") if isinstance(stage157, dict) else None,
        "stage159_decision": stage159.get("decision") if isinstance(stage159, dict) else None,
        "stage160_decision": stage160.get("decision") if isinstance(stage160, dict) else None,
        "first_unlock_provider": provider,
        "approval_phrase_required": stage157.get("approval_phrase_required") if isinstance(stage157, dict) else None,
        "backend_lookup_ready": stage159.get("backend_lookup_ready") if isinstance(stage159, dict) else None,
        "backend_pending_jobs_at_preflight": (
            stage159.get("backend_metadata", {}).get("pending_jobs") if isinstance(stage159, dict) else None
        ),
        "window_count": len(window_records),
        "approved_job_count": approved_job_count,
        "job_count": job_count,
        "total_shots": sum(record["total_shots"] for record in window_records),
        "provider_result_record_count": total_provider_result_records,
        "missing_result_record_count": missing_result_records,
        "window_records": window_records,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "credit_balance_verified": False,
        "claim_boundary": {
            "supported": [
                "exact no-submit IBM job and shot exposure from Stage 114 job shards",
                "per-window job-kind, encoding-family, and target-evidence path counts before any approved live run",
                "binding of exposure totals to Stage 157 approval, Stage 159 backend preflight, and Stage 160 analysis readiness",
                "an explicit missing-result count before post-run analysis can start",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "runnable Stage 133 live-submit command strings",
                "IBM credit balance or dollar cost verification",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Use this exposure packet when deciding whether to approve the live IBM run. If approved, submit only the "
            "Stage 157 first-provider windows, then expect the same job count in provider result records before Stage 160 analysis."
        ),
    }


def write_stage161_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage157_decision": result["stage157_decision"],
        "stage159_decision": result["stage159_decision"],
        "stage160_decision": result["stage160_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "backend_lookup_ready": result["backend_lookup_ready"],
        "backend_pending_jobs_at_preflight": result["backend_pending_jobs_at_preflight"],
        "window_count": result["window_count"],
        "approved_job_count": result["approved_job_count"],
        "job_count": result["job_count"],
        "total_shots": result["total_shots"],
        "provider_result_record_count": result["provider_result_record_count"],
        "missing_result_record_count": result["missing_result_record_count"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
        "explicit_user_approval_required": result["explicit_user_approval_required"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "runnable_commands_recorded": result["runnable_commands_recorded"],
        "credit_balance_verified": result["credit_balance_verified"],
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
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "provider",
                "window_id",
                "job_count",
                "total_shots",
                "provider_result_record_count",
                "missing_result_records",
                "ready",
                "blockers",
            ),
        )
        writer.writeheader()
        for record in result["window_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "job_count": record["job_count"],
                    "total_shots": record["total_shots"],
                    "provider_result_record_count": record["provider_result_record_count"],
                    "missing_result_records": max(record["job_count"] - record["provider_result_record_count"], 0),
                    "ready": record["ready"],
                    "blockers": "; ".join(record["blockers"]),
                }
            )
    return paths


def print_stage161_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"window_count: {result['window_count']}")
    print(f"job_count: {result['job_count']}")
    print(f"total_shots: {result['total_shots']}")
    print(f"provider_result_record_count: {result['provider_result_record_count']}")
    print(f"missing_result_record_count: {result['missing_result_record_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
