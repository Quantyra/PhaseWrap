from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import Any


STAGE127_SCHEMA_VERSION = "qrope_stage127_injected_client_submitter_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE123_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage123_provider_submission_plan_audit" / "results.json"
DEFAULT_STAGE126_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage126_stage114_result_record_builder_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage127_injected_client_submitter_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
PROVIDER_MODULES = {
    "amazon_braket": "qrope.provider_adapters.amazon_braket",
    "ibm_runtime": "qrope.provider_adapters.ibm_runtime",
}


class FakeProviderClient:
    def __init__(self, provider: str) -> None:
        self.provider = provider
        self.calls: list[dict[str, Any]] = []

    def run_openqasm3(self, plan: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(plan)
        if self.provider == "ibm_runtime":
            raw_result = {"counts": {"00": 7, "11": 3}}
        else:
            raw_result = {"measurementCounts": {"01": 4, "10": 6}}
        return {
            "job_or_task_id": f"FAKE_TASK::{plan['job_id']}",
            "backend_metadata": {
                "backend": "fake-client-backend",
                "client_mode": "injected_fake_not_hardware",
            },
            "submitted_at_utc": "1970-01-01T00:00:00Z",
            "completed_at_utc": "1970-01-01T00:00:01Z",
            "raw_result": raw_result,
        }


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_first_plan(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return json.loads(line)
    return None


def _plan_paths(stage123_results_path: Path) -> list[Path]:
    return sorted((stage123_results_path.parent / "submission_plans").glob("*/*/submission_plans.jsonl"))


def _record_ready(record: dict[str, Any]) -> list[str]:
    missing = []
    for field in ("job_id", "job_or_task_id", "backend_metadata", "submitted_at_utc", "completed_at_utc", "counts"):
        if field not in record or record.get(field) in (None, "", []):
            missing.append(field)
    counts = record.get("counts")
    if not isinstance(counts, dict) or not counts:
        missing.append("counts")
    else:
        try:
            if sum(int(value) for value in counts.values()) <= 0:
                missing.append("counts")
        except (TypeError, ValueError):
            missing.append("counts")
    return sorted(set(missing))


def _provider_record(plan_path: Path) -> tuple[dict[str, Any], dict[str, Any] | None]:
    plan = _load_first_plan(plan_path)
    missing = []
    result_record = None
    if not plan:
        missing.append("submission_plan_missing")
        provider = plan_path.parts[-3]
        window_id = plan_path.parts[-2]
    else:
        provider = str(plan.get("provider", ""))
        window_id = str(plan.get("window_id", ""))
        try:
            module = importlib.import_module(PROVIDER_MODULES[provider])
            executor = getattr(module, "execute_submission_plans")
            client = FakeProviderClient(provider)
            records = executor(
                plans=[plan],
                client=client,
                submitted_at_utc="1970-01-01T00:00:00Z",
                completed_at_utc="1970-01-01T00:00:01Z",
            )
            if len(client.calls) != 1:
                missing.append("fake_client_call_count_mismatch")
            if len(records) != 1:
                missing.append("executor_record_count_mismatch")
            else:
                result_record = records[0]
                missing.extend(_record_ready(result_record))
        except Exception as exc:  # noqa: BLE001 - audit reports injected-client failures.
            missing.append(f"injected_client_execution_failed:{exc}")
    return (
        {
            "provider": provider,
            "window_id": window_id,
            "submission_plan_path": str(plan_path.as_posix()),
            "result_record_ready": result_record is not None and not missing,
            "missing_evidence": sorted(set(missing)),
            "ready": result_record is not None and not missing,
        },
        result_record,
    )


def run_stage127_audit(
    *,
    stage123_results_path: Path = DEFAULT_STAGE123_RESULTS,
    stage126_results_path: Path = DEFAULT_STAGE126_RESULTS,
) -> dict[str, Any]:
    stage123 = _load_json(stage123_results_path)
    stage126 = _load_json(stage126_results_path)
    sources = [(stage123_results_path, stage123), (stage126_results_path, stage126)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    provider_records = []
    built_records: dict[str, dict[str, Any]] = {}
    for plan_path in _plan_paths(stage123_results_path):
        record, result_record = _provider_record(plan_path)
        provider_records.append(record)
        if result_record:
            built_records[f"{record['provider']}::{record['window_id']}"] = result_record
    ready = bool(provider_records) and all(record["ready"] for record in provider_records) and not missing_sources
    return {
        "schema_version": STAGE127_SCHEMA_VERSION,
        "stage": "stage127_injected_client_submitter_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "INJECTED_CLIENT_SUBMITTER_PATH_READY_EXECUTION_BLOCKED"
            if ready
            else "INJECTED_CLIENT_SUBMITTER_PATH_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage123_decision": stage123.get("decision") if isinstance(stage123, dict) else None,
        "stage126_decision": stage126.get("decision") if isinstance(stage126, dict) else None,
        "provider_window_count": len(provider_records),
        "ready_provider_window_count": sum(1 for record in provider_records if record["ready"]),
        "provider_records": provider_records,
        "built_records": built_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "provider adapters expose injected-client execution paths",
                "injected clients can return provider-like raw results that normalize into Stage 114 records",
                "the submitter internals are testable before real SDK clients and credentials are enabled",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "live provider SDK submission",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Replace injected fake clients with guarded provider SDK clients after Stage 106/111 readiness clears, "
            "preserving the same plan-to-client-to-normalizer-to-Stage114-record path."
        ),
    }


def write_stage127_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    built_dir = output_dir / "injected_client_result_records"
    built_paths = []
    for key, record in result["built_records"].items():
        provider, window_id = key.split("::", 1)
        path = built_dir / provider / window_id / "provider_job_result.injected_client_sample.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        built_paths.append(str(path.as_posix()))
    result_without_built = {key: value for key, value in result.items() if key != "built_records"}
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage123_decision": result["stage123_decision"],
        "stage126_decision": result["stage126_decision"],
        "provider_window_count": result["provider_window_count"],
        "ready_provider_window_count": result["ready_provider_window_count"],
        "injected_client_result_record_paths": built_paths,
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
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
    (output_dir / "results.json").write_text(json.dumps(result_without_built, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("provider", "window_id", "result_record_ready", "ready", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "result_record_ready": record["result_record_ready"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage127_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_provider_window_count: {result['ready_provider_window_count']}/{result['provider_window_count']}")
    print(f"next_gate: {result['next_gate']}")
