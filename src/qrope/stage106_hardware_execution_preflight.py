from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Mapping


STAGE106_SCHEMA_VERSION = "qrope_stage106_hardware_execution_preflight_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE105_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage105_independent_rerun_protocol" / "manifest.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage106_hardware_execution_preflight"
OBJECTIVE = (
    "Determine whether PhaseWrap's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
TOKEN_ENV_BY_PROVIDER: dict[str, tuple[str, ...]] = {
    "ibm_runtime": ("IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN"),
    "amazon_braket": ("AWS_ACCESS_KEY_ID", "AWS_PROFILE", "AWS_SESSION_TOKEN"),
}
BACKEND_ENV_BY_PROVIDER: dict[str, tuple[str, ...]] = {
    "ibm_runtime": ("QROPE_IBM_BACKEND", "QROPE_HARDWARE_BACKEND"),
    "amazon_braket": ("QROPE_BRAKET_DEVICE_ARN", "QROPE_BRAKET_DEVICE_ARNS"),
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _present(env: Mapping[str, str], keys: tuple[str, ...]) -> list[str]:
    return [key for key in keys if str(env.get(key, "")).strip()]


def _positive_float(env: Mapping[str, str], key: str) -> bool:
    try:
        return float(str(env.get(key, "")).strip()) > 0.0
    except ValueError:
        return False


def _positive_int(env: Mapping[str, str], key: str) -> bool:
    try:
        return int(str(env.get(key, "")).strip()) > 0
    except ValueError:
        return False


def _provider_preflight(provider: str, env: Mapping[str, str]) -> dict[str, Any]:
    credential_keys = TOKEN_ENV_BY_PROVIDER.get(provider, ())
    backend_keys = BACKEND_ENV_BY_PROVIDER.get(provider, ())
    present_credentials = _present(env, credential_keys)
    present_backends = _present(env, backend_keys)
    blockers = []
    if not present_credentials:
        blockers.append("provider_credentials_missing")
    if not present_backends:
        blockers.append("backend_selection_missing")
    if not _positive_float(env, "QROPE_HARDWARE_BUDGET_USD_CAP"):
        blockers.append("hardware_budget_cap_missing")
    if not _positive_int(env, "QROPE_HARDWARE_QUEUE_DEPTH_CAP"):
        blockers.append("queue_depth_cap_missing")
    if provider == "amazon_braket":
        if not str(env.get("QROPE_BRAKET_OUTPUT_S3_BUCKET", "")).strip():
            blockers.append("braket_output_s3_bucket_missing")
        if not str(env.get("QROPE_BRAKET_AWS_REGION", env.get("AWS_REGION", ""))).strip():
            blockers.append("braket_region_missing")
    if provider == "ibm_runtime" and not str(env.get("IBM_QUANTUM_INSTANCE_CRN", "")).strip():
        blockers.append("ibm_instance_crn_missing")
    return {
        "provider": provider,
        "status": "ready" if not blockers else "blocked",
        "credential_env_present": present_credentials,
        "backend_env_present": present_backends,
        "budget_cap_present": _positive_float(env, "QROPE_HARDWARE_BUDGET_USD_CAP"),
        "queue_depth_cap_present": _positive_int(env, "QROPE_HARDWARE_QUEUE_DEPTH_CAP"),
        "blockers": blockers,
    }


def run_stage106_preflight(
    *,
    stage105_manifest_path: Path = DEFAULT_STAGE105_MANIFEST,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    environ = os.environ if env is None else env
    stage105 = _load_json(stage105_manifest_path)
    missing_sources = [] if stage105 else [str(stage105_manifest_path.as_posix())]
    providers = [str(provider) for provider in stage105.get("providers", [])] if stage105 else []
    provider_records = [_provider_preflight(provider, environ) for provider in providers]
    ready = bool(provider_records) and all(record["status"] == "ready" for record in provider_records)
    return {
        "schema_version": STAGE106_SCHEMA_VERSION,
        "stage": "stage106_hardware_execution_preflight",
        "status": "completed" if stage105 else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "HARDWARE_EXECUTION_PREFLIGHT_READY_NO_SUBMISSION"
            if ready
            else "HARDWARE_EXECUTION_PREFLIGHT_BLOCKED_CONFIGURATION_REQUIRED"
        ),
        "source_artifacts": [str(stage105_manifest_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage105_decision": stage105.get("decision") if stage105 else None,
        "providers": providers,
        "provider_records": provider_records,
        "ready_for_hardware_submission": ready,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "required_common_env": [
            "QROPE_HARDWARE_BUDGET_USD_CAP",
            "QROPE_HARDWARE_QUEUE_DEPTH_CAP",
        ],
        "required_provider_env": {
            "ibm_runtime": [
                "IBM_QUANTUM_TOKEN or QISKIT_IBM_TOKEN",
                "QROPE_IBM_BACKEND or QROPE_HARDWARE_BACKEND",
                "IBM_QUANTUM_INSTANCE_CRN",
            ],
            "amazon_braket": [
                "AWS_ACCESS_KEY_ID or AWS_PROFILE",
                "QROPE_BRAKET_DEVICE_ARN or QROPE_BRAKET_DEVICE_ARNS",
                "QROPE_BRAKET_OUTPUT_S3_BUCKET",
                "QROPE_BRAKET_AWS_REGION or AWS_REGION",
            ],
        },
        "claim_boundary": {
            "supported": [
                "a no-submission hardware execution configuration preflight for the Stage 105 rerun protocol",
                "provider-level readiness/blocker reporting without recording secret values",
                "a gate preventing ad hoc hardware attempts without backend, budget, queue, and artifact destination configuration",
            ],
            "excluded": [
                "backend availability discovery",
                "real hardware submission",
                "completed calibration or matched packet execution",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Set provider credentials, backend selections, budget caps, queue caps, and artifact destinations; rerun Stage 106, "
            "then execute Stage 101/104 only if the preflight is ready."
        ),
    }


def write_stage106_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage105_decision": result["stage105_decision"],
        "providers": result["providers"],
        "ready_for_hardware_submission": result["ready_for_hardware_submission"],
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
                "status",
                "credential_env_present",
                "backend_env_present",
                "budget_cap_present",
                "queue_depth_cap_present",
                "blockers",
            ),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    **record,
                    "credential_env_present": "; ".join(record["credential_env_present"]),
                    "backend_env_present": "; ".join(record["backend_env_present"]),
                    "blockers": "; ".join(record["blockers"]),
                }
            )
    return paths


def print_stage106_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_for_hardware_submission: {result['ready_for_hardware_submission']}")
    print(f"providers: {', '.join(result['providers'])}")
    print(f"next_gate: {result['next_gate']}")
