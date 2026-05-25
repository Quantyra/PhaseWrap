from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import Any


STAGE122_SCHEMA_VERSION = "qrope_stage122_provider_adapter_skeleton_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE121_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage121_provider_adapter_bridge_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage122_provider_adapter_skeleton_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
ADAPTER_IMPORTS = {
    "amazon_braket": "qrope.provider_adapters.amazon_braket:submit",
    "ibm_runtime": "qrope.provider_adapters.ibm_runtime:submit",
}
REQUIRED_ADAPTER_HELPERS = (
    "adapter_status",
    "build_client_config",
    "build_live_client_factory_contract",
    "build_submission_plan",
    "execute_submission_plans",
    "normalize_result_counts",
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _adapter_record(provider: str, import_path: str) -> dict[str, Any]:
    module_name, _, attr_name = import_path.partition(":")
    missing = []
    status: dict[str, Any] = {}
    module_imported = False
    submitter_callable = False
    status_callable = False
    helper_callables: dict[str, bool] = {}
    synthetic_result_contract_ready = False
    synthetic_result_contract_missing: list[str] = []
    try:
        module = importlib.import_module(module_name)
        module_imported = True
        submitter_callable = callable(getattr(module, attr_name, None))
        status_callable = callable(getattr(module, "adapter_status", None))
        helper_callables = {name: callable(getattr(module, name, None)) for name in REQUIRED_ADAPTER_HELPERS}
        if status_callable:
            status = module.adapter_status()
        if all(helper_callables.values()):
            synthetic_result_contract_ready, synthetic_result_contract_missing = _synthetic_result_contract(module, provider)
    except Exception as exc:  # noqa: BLE001 - audit reports import failures as blockers.
        missing.append(f"adapter_import_failed:{exc}")
    if not module_imported:
        missing.append("adapter_module_missing")
    if not submitter_callable:
        missing.append("submitter_not_callable")
    if not status_callable:
        missing.append("adapter_status_not_callable")
    for helper, present in helper_callables.items():
        if not present:
            missing.append(f"adapter_helper_not_callable:{helper}")
    if status and status.get("provider") != provider:
        missing.append("adapter_provider_mismatch")
    if status and status.get("secret_values_recorded") is True:
        missing.append("adapter_secret_boundary_missing")
    missing.extend(synthetic_result_contract_missing)
    return {
        "provider": provider,
        "submitter_import_path": import_path,
        "adapter_module_imported": module_imported,
        "submitter_callable": submitter_callable,
        "adapter_status_callable": status_callable,
        "adapter_helper_callables": helper_callables,
        "synthetic_result_contract_ready": synthetic_result_contract_ready,
        "adapter_status": status,
        "missing_evidence": sorted(set(missing)),
        "ready": not missing and module_imported and submitter_callable and status_callable and synthetic_result_contract_ready,
    }


def _synthetic_result_contract(module: Any, provider: str) -> tuple[bool, list[str]]:
    job = {
        "job_id": f"{provider}__synthetic_job_0",
        "job_kind": "known_state_calibration",
        "provider": provider,
        "shots": 1000,
        "state": "00",
        "target_counts_key": "00",
        "window_id": f"{provider}__synthetic_window_0",
    }
    payload = {
        "job_id": job["job_id"],
        "openqasm3": "OPENQASM 3.0;\n",
        "openqasm3_sha256": "synthetic",
        "provider": provider,
        "shots": 1000,
        "target_counts_key": "00",
        "window_id": job["window_id"],
    }

    class SyntheticClient:
        def run_openqasm3(self, plan: dict[str, Any]) -> dict[str, Any]:
            return {
                "job_or_task_id": "synthetic_task_0",
                "backend_metadata": {"backend": "synthetic_backend", "provider": provider},
                "submitted_at_utc": "2026-01-01T00:00:00Z",
                "completed_at_utc": "2026-01-01T00:00:01Z",
                "raw_result": {"counts": {"00": 1000}},
            }

    missing = []
    try:
        plans = module.build_submission_plan(jobs=[job], payloads=[payload])
        records = module.execute_submission_plans(
            plans=plans,
            client=SyntheticClient(),
            submitted_at_utc="2026-01-01T00:00:00Z",
            completed_at_utc="2026-01-01T00:00:01Z",
        )
    except Exception as exc:  # noqa: BLE001 - contract audit should surface adapter failure text.
        return False, [f"synthetic_result_contract_failed:{exc}"]
    if len(records) != 1:
        missing.append("synthetic_result_contract_record_count")
        return False, missing
    record = records[0]
    for field in ("job_id", "job_or_task_id", "backend_metadata", "submitted_at_utc", "completed_at_utc", "counts"):
        if record.get(field) in (None, "", [], {}):
            missing.append(f"synthetic_result_missing:{field}")
    metadata = record.get("backend_metadata", {})
    if not isinstance(metadata, dict):
        missing.append("synthetic_result_backend_metadata")
    else:
        for field in ("provider", "backend", "window_id", "job_kind"):
            if metadata.get(field) in (None, "", []):
                missing.append(f"synthetic_result_backend_metadata:{field}")
        if metadata.get("provider") != provider:
            missing.append("synthetic_result_provider_scope")
    if record.get("counts") != {"00": 1000}:
        missing.append("synthetic_result_counts")
    return not missing, missing


def run_stage122_audit(*, stage121_results_path: Path = DEFAULT_STAGE121_RESULTS) -> dict[str, Any]:
    stage121 = _load_json(stage121_results_path)
    missing_sources = [] if isinstance(stage121, dict) else [str(stage121_results_path.as_posix())]
    adapter_records = [_adapter_record(provider, import_path) for provider, import_path in sorted(ADAPTER_IMPORTS.items())]
    ready = all(record["ready"] for record in adapter_records) and not missing_sources
    return {
        "schema_version": STAGE122_SCHEMA_VERSION,
        "stage": "stage122_provider_adapter_skeleton_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_ADAPTER_SKELETONS_READY_EXECUTION_BLOCKED"
            if ready
            else "PROVIDER_ADAPTER_SKELETONS_INCOMPLETE"
        ),
        "source_artifacts": [str(stage121_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage121_decision": stage121.get("decision") if isinstance(stage121, dict) else None,
        "adapter_count": len(adapter_records),
        "ready_adapter_count": sum(1 for record in adapter_records if record["ready"]),
        "adapter_records": adapter_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "canonical IBM Runtime and Amazon Braket adapter import paths exist",
                "adapter modules expose callable submitters and non-secret readiness metadata",
                "adapter modules expose local planning/count-normalization/result-construction helpers",
                "adapter helpers can synthesize Stage 114-compatible result records without provider SDK submission",
                "adapter submitters fail closed under current provider readiness blockers",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "authorized live provider SDK submission",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Run provider SDK implementations only after Stage 106/111 readiness clears and Stage 129 authorizes cutover."
        ),
    }


def write_stage122_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage121_decision": result["stage121_decision"],
        "adapter_count": result["adapter_count"],
        "ready_adapter_count": result["ready_adapter_count"],
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
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "provider",
                "submitter_import_path",
                "adapter_module_imported",
                "submitter_callable",
                "adapter_status_callable",
                "synthetic_result_contract_ready",
                "ready",
                "missing_evidence",
            ),
        )
        writer.writeheader()
        for record in result["adapter_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "submitter_import_path": record["submitter_import_path"],
                    "adapter_module_imported": record["adapter_module_imported"],
                    "submitter_callable": record["submitter_callable"],
                    "adapter_status_callable": record["adapter_status_callable"],
                    "synthetic_result_contract_ready": record["synthetic_result_contract_ready"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage122_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_adapter_count: {result['ready_adapter_count']}/{result['adapter_count']}")
    print(f"next_gate: {result['next_gate']}")
