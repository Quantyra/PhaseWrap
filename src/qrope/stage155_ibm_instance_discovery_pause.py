from __future__ import annotations

import csv
import importlib.util
import json
import os
import re
from pathlib import Path
from typing import Any, Callable, Mapping


STAGE155_SCHEMA_VERSION = "qrope_stage155_ibm_instance_discovery_pause_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE154_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage154_simulated_hardware_go_no_go" / "results.json"
DEFAULT_STAGE140_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage140_local_provider_configuration_readiness" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage155_ibm_instance_discovery_pause"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
TARGETED_GO_DECISION = "SIMULATED_NOISE_TARGETED_HARDWARE_FOLLOWUP_RECOMMENDED"
IBM_CRN_RE = re.compile(r"crn:v1:[^\\s,;]+", re.IGNORECASE)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _module_present(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _token_present(env: Mapping[str, str]) -> bool:
    return bool(str(env.get("IBM_QUANTUM_TOKEN") or env.get("QISKIT_IBM_TOKEN") or "").strip())


def _crn_present(env: Mapping[str, str]) -> bool:
    return bool(str(env.get("IBM_QUANTUM_INSTANCE_CRN") or "").strip())


def _sanitize_error(message: str) -> str:
    return IBM_CRN_RE.sub("<redacted-crn>", message)


def _discover_instances_with_qiskit(env: Mapping[str, str]) -> list[dict[str, Any]]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    token = str(env.get("IBM_QUANTUM_TOKEN") or env.get("QISKIT_IBM_TOKEN") or "").strip()
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
    return [dict(instance) for instance in service.instances()]


def _public_instance_record(instance: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "name": instance.get("name"),
        "plan": instance.get("plan"),
        "region": instance.get("region"),
        "crn_discovered": bool(str(instance.get("crn") or "").strip()),
    }


def run_stage155_ibm_instance_discovery_pause(
    *,
    stage154_results_path: Path = DEFAULT_STAGE154_RESULTS,
    stage140_results_path: Path = DEFAULT_STAGE140_RESULTS,
    env: Mapping[str, str] | None = None,
    allow_live_discovery: bool = False,
    discover_instances: Callable[[Mapping[str, str]], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    environ = os.environ if env is None else env
    stage154 = _load_json(stage154_results_path)
    stage140 = _load_json(stage140_results_path)
    missing_sources = [
        str(path.as_posix())
        for path, loaded in ((stage154_results_path, stage154), (stage140_results_path, stage140))
        if not isinstance(loaded, dict)
    ]
    stage154_targeted_go = bool(isinstance(stage154, dict) and stage154.get("decision") == TARGETED_GO_DECISION)
    token_ready = _token_present(environ)
    crn_ready = _crn_present(environ)
    sdk_ready = _module_present("qiskit") and _module_present("qiskit_ibm_runtime")
    discovery_attempted = False
    discovery_error: dict[str, str] | None = None
    public_instances: list[dict[str, Any]] = []
    if not missing_sources and stage154_targeted_go and token_ready and sdk_ready and not crn_ready and allow_live_discovery:
        discovery_attempted = True
        try:
            discover = discover_instances or _discover_instances_with_qiskit
            public_instances = [_public_instance_record(instance) for instance in discover(environ)]
        except Exception as exc:  # pragma: no cover - exercised by integration use, not by network-free tests.
            discovery_error = {"type": type(exc).__name__, "message": _sanitize_error(str(exc))}

    discovered_crn_count = sum(1 for instance in public_instances if instance["crn_discovered"])
    if missing_sources:
        decision = "IBM_INSTANCE_DISCOVERY_PAUSE_INCOMPLETE"
    elif not stage154_targeted_go:
        decision = "IBM_INSTANCE_DISCOVERY_NOT_NEEDED_WITHOUT_TARGETED_SIMULATED_GO"
    elif crn_ready:
        decision = "IBM_INSTANCE_CRN_ALREADY_CONFIGURED_RERUN_PREFLIGHT"
    elif not token_ready:
        decision = "IBM_INSTANCE_DISCOVERY_BLOCKED_TOKEN_REQUIRED"
    elif not sdk_ready:
        decision = "IBM_INSTANCE_DISCOVERY_BLOCKED_SDK_REQUIRED"
    elif not allow_live_discovery:
        decision = "IBM_INSTANCE_DISCOVERY_PAUSED_LIVE_DISCOVERY_NOT_REQUESTED"
    elif discovery_error:
        decision = "IBM_INSTANCE_DISCOVERY_BLOCKED_DISCOVERY_ERROR"
    elif discovered_crn_count == 1:
        decision = "IBM_INSTANCE_CRN_DISCOVERED_LOCAL_DOTENV_UPDATE_REQUIRED"
    elif discovered_crn_count > 1:
        decision = "IBM_INSTANCE_DISCOVERY_MULTIPLE_INSTANCES_SELECT_ONE"
    else:
        decision = "IBM_INSTANCE_DISCOVERY_NO_INSTANCE_FOUND_ACCOUNT_REVIEW_REQUIRED"

    return {
        "schema_version": STAGE155_SCHEMA_VERSION,
        "stage": "stage155_ibm_instance_discovery_pause",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage154_results_path.as_posix()), str(stage140_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage154_decision": stage154.get("decision") if isinstance(stage154, dict) else None,
        "stage140_decision": stage140.get("decision") if isinstance(stage140, dict) else None,
        "stage154_targeted_hardware_followup_recommended": stage154_targeted_go,
        "ibm_token_present": token_ready,
        "ibm_instance_crn_present": crn_ready,
        "qiskit_sdk_ready": sdk_ready,
        "live_discovery_allowed": allow_live_discovery,
        "live_discovery_attempted": discovery_attempted,
        "discovered_instance_count": len(public_instances),
        "discovered_crn_count": discovered_crn_count,
        "discovered_instances": public_instances,
        "discovery_error": discovery_error,
        "credit_exhaustion_proven": False,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "post-Stage154 pause-point check for whether IBM instance discovery can identify a configured instance",
                "non-secret evidence that the blocker is local CRN population rather than proven credit exhaustion",
                "explicit separation between instance discovery and hardware job submission",
            ],
            "excluded": [
                "recording IBM token or CRN values",
                "hardware job submission",
                "credit balance verification",
                "backend queue or calibration validation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Populate IBM_QUANTUM_INSTANCE_CRN locally, then rerun Stage 140 with --load-dotenv followed by "
            "Stage 106, Stage 111, Stage 128, Stage 129, Stage 130, Stage 139, Stage 144, and Stage 152 before "
            "any guarded Stage 133 live-submit command."
        ),
    }


def write_stage155_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage154_decision": result["stage154_decision"],
        "stage140_decision": result["stage140_decision"],
        "ibm_token_present": result["ibm_token_present"],
        "ibm_instance_crn_present": result["ibm_instance_crn_present"],
        "qiskit_sdk_ready": result["qiskit_sdk_ready"],
        "live_discovery_allowed": result["live_discovery_allowed"],
        "live_discovery_attempted": result["live_discovery_attempted"],
        "discovered_instance_count": result["discovered_instance_count"],
        "discovered_crn_count": result["discovered_crn_count"],
        "credit_exhaustion_proven": result["credit_exhaustion_proven"],
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
        writer = csv.DictWriter(handle, fieldnames=("name", "plan", "region", "crn_discovered"))
        writer.writeheader()
        for record in result["discovered_instances"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage155_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"live_discovery_attempted: {result['live_discovery_attempted']}")
    print(f"discovered_instance_count: {result['discovered_instance_count']}")
    print(f"discovered_crn_count: {result['discovered_crn_count']}")
    print(f"next_gate: {result['next_gate']}")
