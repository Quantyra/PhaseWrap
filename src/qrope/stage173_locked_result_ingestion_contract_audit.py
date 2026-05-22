from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


STAGE173_SCHEMA_VERSION = "qrope_stage173_locked_result_ingestion_contract_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE114_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract" / "manifest.json"
DEFAULT_STAGE114_SCHEMA = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract" / "provider_job_result_schema.json"
DEFAULT_STAGE163_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage163_first_provider_prerun_lock" / "results.json"
DEFAULT_STAGE172_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage172_objective_evidence_gap_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage173_locked_result_ingestion_contract_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
REQUIRED_RESULT_FIELDS = {"job_id", "job_or_task_id", "backend_metadata", "submitted_at_utc", "completed_at_utc", "counts"}
REQUIRED_JOB_FIELDS = {
    "job_id",
    "job_kind",
    "openqasm3",
    "provider",
    "shots",
    "target_counts_container",
    "target_counts_key",
    "target_evidence_path",
    "template_path",
    "window_id",
}
MATCHED_PACKET_FIELDS = {"circuit_template", "encoding_family", "packet_id", "row_id", "source_lane_id"}
CALIBRATION_FIELDS = {"state"}
STAGE163_READY = "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL"
STAGE172_HARDWARE_REQUIRED = "OBJECTIVE_EVIDENCE_GAP_AUDIT_HARDWARE_RESULTS_REQUIRED"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stub_path_for_lock(stage114_manifest: dict[str, Any] | None, provider: str, window_id: str) -> Path | None:
    if not isinstance(stage114_manifest, dict):
        return None
    needle = f"result_stubs/{provider}/{window_id}/provider_job_results.stub.jsonl"
    for text in stage114_manifest.get("result_stub_paths", []):
        if str(text).replace("\\", "/").endswith(needle):
            return Path(str(text))
    return None


def _missing_job_fields(job: dict[str, Any]) -> list[str]:
    missing = [field for field in REQUIRED_JOB_FIELDS if job.get(field) in (None, "")]
    if job.get("job_kind") == "matched_packet_row":
        missing.extend(field for field in MATCHED_PACKET_FIELDS if job.get(field) in (None, ""))
    if job.get("job_kind") == "known_state_calibration":
        missing.extend(field for field in CALIBRATION_FIELDS if job.get(field) in (None, ""))
    return sorted(set(missing))


def _window_record(lock: dict[str, Any], stage114_manifest: dict[str, Any] | None, required_result_fields: set[str]) -> dict[str, Any]:
    provider = str(lock.get("provider") or "")
    window_id = str(lock.get("window_id") or "")
    job_shard_path = Path(str(lock.get("job_shard_path") or ""))
    result_path = Path(str(lock.get("provider_results_path") or ""))
    stub_path = _stub_path_for_lock(stage114_manifest, provider, window_id)
    jobs = _load_jsonl(job_shard_path)
    stubs = _load_jsonl(stub_path) if stub_path is not None else []
    job_ids = [str(job.get("job_id") or "") for job in jobs]
    stub_ids = [str(stub.get("job_id") or "") for stub in stubs]
    duplicate_job_ids = sorted({job_id for job_id in job_ids if job_id and job_ids.count(job_id) > 1})
    missing_job_field_count = sum(1 for job in jobs if _missing_job_fields(job))
    stub_missing_field_count = sum(1 for stub in stubs if any(field not in stub for field in required_result_fields))
    mismatched_stub_ids = sorted(set(job_ids).symmetric_difference(set(stub_ids)))
    blockers: list[str] = []
    if not job_shard_path.exists():
        blockers.append("job_shard_missing")
    elif str(lock.get("job_shard_sha256") or "") != _sha256(job_shard_path):
        blockers.append("job_shard_hash_mismatch")
    if stub_path is None or not stub_path.exists():
        blockers.append("result_stub_missing")
    if result_path.exists() and _load_jsonl(result_path):
        blockers.append("provider_result_file_not_empty_before_execution")
    if int(lock.get("job_count") or 0) != len(jobs):
        blockers.append("locked_job_count_mismatch")
    if int(lock.get("total_shots") or 0) != sum(int(job.get("shots") or 0) for job in jobs):
        blockers.append("locked_total_shots_mismatch")
    if len(stubs) != len(jobs):
        blockers.append("result_stub_count_mismatch")
    if duplicate_job_ids:
        blockers.append("duplicate_job_ids")
    if missing_job_field_count:
        blockers.append("job_records_missing_ingestion_fields")
    if stub_missing_field_count:
        blockers.append("result_stub_records_missing_required_fields")
    if mismatched_stub_ids:
        blockers.append("result_stub_job_ids_do_not_match_job_shard")
    job_kind_counts: dict[str, int] = {}
    for job in jobs:
        kind = str(job.get("job_kind") or "")
        job_kind_counts[kind] = job_kind_counts.get(kind, 0) + 1
    return {
        "provider": provider,
        "window_id": window_id,
        "job_shard_path": str(job_shard_path.as_posix()),
        "result_stub_path": str(stub_path.as_posix()) if stub_path is not None else None,
        "provider_results_path": str(result_path.as_posix()),
        "job_count": len(jobs),
        "locked_job_count": int(lock.get("job_count") or 0),
        "total_shots": sum(int(job.get("shots") or 0) for job in jobs),
        "locked_total_shots": int(lock.get("total_shots") or 0),
        "result_stub_count": len(stubs),
        "provider_results_file_exists": result_path.exists(),
        "provider_results_record_count": len(_load_jsonl(result_path)) if result_path.exists() else 0,
        "job_kind_counts": job_kind_counts,
        "duplicate_job_id_count": len(duplicate_job_ids),
        "missing_job_field_count": missing_job_field_count,
        "stub_missing_required_field_count": stub_missing_field_count,
        "mismatched_stub_job_id_count": len(mismatched_stub_ids),
        "ready": not blockers,
        "blockers": sorted(set(blockers)),
    }


def run_stage173_locked_ingestion_audit(
    *,
    stage114_manifest_path: Path = DEFAULT_STAGE114_MANIFEST,
    stage114_schema_path: Path = DEFAULT_STAGE114_SCHEMA,
    stage163_results_path: Path = DEFAULT_STAGE163_RESULTS,
    stage172_results_path: Path = DEFAULT_STAGE172_RESULTS,
) -> dict[str, Any]:
    stage114_manifest = _load_json(stage114_manifest_path)
    stage114_schema = _load_json(stage114_schema_path)
    stage163 = _load_json(stage163_results_path)
    stage172 = _load_json(stage172_results_path)
    sources = [
        (stage114_manifest_path, stage114_manifest),
        (stage114_schema_path, stage114_schema),
        (stage163_results_path, stage163),
        (stage172_results_path, stage172),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    required_result_fields = set(stage114_schema.get("required_fields", [])) if isinstance(stage114_schema, dict) else set()
    window_records = [
        _window_record(lock, stage114_manifest, required_result_fields)
        for lock in (stage163.get("window_locks", []) if isinstance(stage163, dict) else [])
        if isinstance(lock, dict)
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if isinstance(stage114_manifest, dict) and stage114_manifest.get("decision") != "PROVIDER_RESULT_CAPTURE_CONTRACT_PREPARED_RESULTS_REQUIRED":
        blockers.append("stage114_contract_not_ready")
    if isinstance(stage163, dict) and stage163.get("decision") != STAGE163_READY:
        blockers.append("stage163_lock_not_ready")
    if isinstance(stage172, dict) and stage172.get("decision") != STAGE172_HARDWARE_REQUIRED:
        blockers.append("stage172_objective_gap_not_at_hardware_results_boundary")
    if not REQUIRED_RESULT_FIELDS.issubset(required_result_fields):
        blockers.append("stage114_required_result_fields_incomplete")
    if not window_records:
        blockers.append("locked_windows_missing")
    if any(not record["ready"] for record in window_records):
        blockers.append("locked_window_ingestion_contract_not_ready")
    locked_job_count = sum(record["job_count"] for record in window_records)
    locked_total_shots = sum(record["total_shots"] for record in window_records)
    decision = (
        "LOCKED_RESULT_INGESTION_CONTRACT_AUDIT_INCOMPLETE"
        if missing_sources
        else "LOCKED_RESULT_INGESTION_CONTRACT_READY_AWAITING_PROVIDER_RESULTS"
        if not blockers
        else "LOCKED_RESULT_INGESTION_CONTRACT_AUDIT_BLOCKED"
    )
    return {
        "schema_version": STAGE173_SCHEMA_VERSION,
        "stage": "stage173_locked_result_ingestion_contract_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage114_decision": stage114_manifest.get("decision") if isinstance(stage114_manifest, dict) else None,
        "stage163_decision": stage163.get("decision") if isinstance(stage163, dict) else None,
        "stage172_decision": stage172.get("decision") if isinstance(stage172, dict) else None,
        "required_result_fields": sorted(required_result_fields),
        "window_count": len(window_records),
        "ready_window_count": sum(1 for record in window_records if record["ready"]),
        "locked_job_count": locked_job_count,
        "locked_total_shots": locked_total_shots,
        "window_records": window_records,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "no-submit verification that locked IBM job shards match the Stage163 pre-run lock",
                "no-submit verification that locked jobs have the target evidence fields needed for Stage115/113 ingestion",
                "no-submit verification that Stage114 result stubs match locked job ids and required result fields",
                "confirmation that provider result files are still absent before live execution",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "completed provider results",
                "Stage115 collection or Stage113 evidence assembly",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After exact approval and provider execution, populate the locked Stage114 provider result JSONL files, "
            "rerun Stage164 and Stage115, then assemble Stage113 evidence."
        ),
    }


def write_stage173_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage114_decision": result["stage114_decision"],
        "stage163_decision": result["stage163_decision"],
        "stage172_decision": result["stage172_decision"],
        "window_count": result["window_count"],
        "ready_window_count": result["ready_window_count"],
        "locked_job_count": result["locked_job_count"],
        "locked_total_shots": result["locked_total_shots"],
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
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "provider",
                "window_id",
                "ready",
                "job_count",
                "total_shots",
                "result_stub_count",
                "provider_results_record_count",
                "blockers",
            ),
        )
        writer.writeheader()
        for record in result["window_records"]:
            writer.writerow({**{field: record.get(field) for field in writer.fieldnames}, "blockers": "; ".join(record["blockers"])})
    return paths


def print_stage173_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_window_count: {result['ready_window_count']}/{result['window_count']}")
    print(f"locked_job_count: {result['locked_job_count']}")
    print(f"locked_total_shots: {result['locked_total_shots']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
