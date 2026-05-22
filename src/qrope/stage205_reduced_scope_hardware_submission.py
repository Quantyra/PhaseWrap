from __future__ import annotations

import csv
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from qrope.env_utils import load_local_dotenv
from qrope.stage203_reduced_scope_execution_package import DEFAULT_OUTPUT_DIR as STAGE203_OUTPUT_DIR
from qrope.stage204_reduced_scope_guarded_runner_readiness import DEFAULT_OUTPUT_DIR as STAGE204_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE205_SCHEMA_VERSION = "qrope_stage205_reduced_scope_hardware_submission_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE204_RESULTS = STAGE204_OUTPUT_DIR / "results.json"
DEFAULT_STAGE203_RESULTS = STAGE203_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage205_reduced_scope_hardware_submission_100usd"
STAGE204_READY = "REDUCED_SCOPE_GUARDED_RUNNER_READY_FOR_FINAL_EXECUTION_STEP_NOT_LIVE"
STAGE203_READY = "REDUCED_SCOPE_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED_NOT_LIVE"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_templates(stage203: dict[str, Any]) -> list[dict[str, Any]]:
    templates = [template for template in stage203.get("execution_templates", []) if isinstance(template, dict)]
    calibration = stage203.get("calibration_template")
    if isinstance(calibration, dict):
        templates.append(calibration)
    return templates


def _template_circuit_count(template: dict[str, Any]) -> int:
    if template.get("template_type") == "reduced_scope_known_state_calibration_counts":
        return len(template.get("raw_counts_by_state", []))
    return len(template.get("raw_counts_by_row", []))


def _template_shots(template: dict[str, Any]) -> int:
    return int(template.get("shots_per_state") or template.get("shot_count") or 0)


def _limited_openqasm3_to_circuit(openqasm3: str) -> Any:
    from qiskit import QuantumCircuit

    circuit = QuantumCircuit(2, 2)
    for raw_line in openqasm3.splitlines():
        line = raw_line.strip().rstrip(";")
        if not line or line in {"OPENQASM 3.0", "qubit[2] q", "bit[2] c"}:
            continue
        match = re.fullmatch(r"x q\[(\d+)\]", line)
        if match:
            circuit.x(int(match.group(1)))
            continue
        match = re.fullmatch(r"ry\(([-+0-9.eE]+)\) q\[(\d+)\]", line)
        if match:
            circuit.ry(float(match.group(1)), int(match.group(2)))
            continue
        match = re.fullmatch(r"cnot q\[(\d+)\], q\[(\d+)\]", line)
        if match:
            circuit.cx(int(match.group(1)), int(match.group(2)))
            continue
        match = re.fullmatch(r"c\[(\d+)\] = measure q\[(\d+)\]", line)
        if match:
            circuit.measure(int(match.group(2)), int(match.group(1)))
            continue
        raise ValueError(f"unsupported OpenQASM 3 line in reduced-scope template: {line}")
    return circuit


def _extract_job_id(job: Any) -> str:
    job_id = getattr(job, "job_id", "")
    return str(job_id() if callable(job_id) else job_id)


def _real_submit_template(*, template: dict[str, Any], backend_name: str) -> dict[str, Any]:
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    token = os.environ.get("IBM_QUANTUM_TOKEN") or os.environ.get("QISKIT_IBM_TOKEN")
    instance = os.environ.get("IBM_QUANTUM_INSTANCE_CRN")
    if not token or not instance:
        raise RuntimeError("IBM token or instance missing")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=instance)
    backend = service.backend(backend_name)
    rows = template.get("raw_counts_by_state") if template.get("template_type") == "reduced_scope_known_state_calibration_counts" else template.get("raw_counts_by_row")
    circuits = [_limited_openqasm3_to_circuit(str(row.get("openqasm3", ""))) for row in rows]
    pass_manager = generate_preset_pass_manager(target=backend.target, optimization_level=1)
    isa_circuits = [pass_manager.run(circuit) for circuit in circuits]
    sampler = SamplerV2(mode=backend)
    submitted_at = datetime.now(UTC).isoformat()
    job = sampler.run(isa_circuits, shots=_template_shots(template))
    return {
        "runtime_job_id": _extract_job_id(job),
        "submitted_at_utc": submitted_at,
        "completed_at_utc": "",
        "backend_metadata": {
            "backend": backend_name,
            "provider": "ibm_runtime",
            "runtime_submission_kind": "sampler_v2_async_packet_batch",
        },
    }


def _submission_record(template: dict[str, Any], submit_result: dict[str, Any] | None, *, status: str, error_type: str = "") -> dict[str, Any]:
    return {
        "template_type": template.get("template_type"),
        "packet_id": template.get("packet_id", ""),
        "source_lane_id": template.get("source_lane_id", ""),
        "encoding_family": template.get("encoding_family", ""),
        "circuit_template": template.get("circuit_template", "known_state_calibration"),
        "circuit_count": _template_circuit_count(template),
        "shots": _template_shots(template),
        "runtime_job_id": "" if submit_result is None else str(submit_result.get("runtime_job_id", "")),
        "submitted_at_utc": "" if submit_result is None else str(submit_result.get("submitted_at_utc", "")),
        "completed_at_utc": "" if submit_result is None else str(submit_result.get("completed_at_utc", "")),
        "backend_metadata": {} if submit_result is None else submit_result.get("backend_metadata", {}),
        "status": status,
        "error_type": error_type,
        "counts_retrieved": False,
    }


def run_stage205_reduced_scope_hardware_submission(
    *,
    stage204_results_path: Path = DEFAULT_STAGE204_RESULTS,
    stage203_results_path: Path = DEFAULT_STAGE203_RESULTS,
    allow_live_submit: bool = False,
    submit_template: Callable[..., dict[str, Any]] | None = None,
    load_dotenv: bool = False,
) -> dict[str, Any]:
    if load_dotenv:
        load_local_dotenv(Path(".env"))
    stage204 = _load_json(stage204_results_path)
    stage203 = _load_json(stage203_results_path)
    sources = [(stage204_results_path, stage204), (stage203_results_path, stage203)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    stage204_ready = bool(isinstance(stage204, dict) and stage204.get("decision") == STAGE204_READY)
    stage203_ready = bool(isinstance(stage203, dict) and stage203.get("decision") == STAGE203_READY)
    if not stage204_ready:
        blockers.append("stage204_guarded_runner_not_ready")
    if not stage203_ready:
        blockers.append("stage203_execution_package_not_ready")
    if not allow_live_submit:
        blockers.append("allow_live_submit_flag_required")
    backend_name = str(stage204.get("backend") if isinstance(stage204, dict) else "" or "")
    if not backend_name:
        blockers.append("backend_missing")
    templates = _load_templates(stage203) if isinstance(stage203, dict) else []
    if len(templates) != 21:
        blockers.append("stage203_template_count_mismatch")

    submission_records: list[dict[str, Any]] = []
    submitter = submit_template or _real_submit_template
    attempted = False
    if not blockers:
        attempted = True
        for template in templates:
            try:
                submit_result = submitter(template=template, backend_name=backend_name)
                submission_records.append(_submission_record(template, submit_result, status="submitted_awaiting_results"))
            except Exception as exc:  # noqa: BLE001 - preserve submitted job IDs and fail closed.
                blockers.append("template_submission_failed")
                submission_records.append(_submission_record(template, None, status="submission_failed", error_type=type(exc).__name__))
                break
    else:
        submission_records = [_submission_record(template, None, status="not_submitted") for template in templates]

    submitted_count = sum(1 for record in submission_records if record["status"] == "submitted_awaiting_results" and record["runtime_job_id"])
    expected_runtime_job_count = len(templates)
    if attempted and submitted_count != expected_runtime_job_count:
        blockers.append("not_all_templates_submitted")
    if blockers:
        decision = "REDUCED_SCOPE_HARDWARE_SUBMISSION_BLOCKED_OR_PARTIAL"
    else:
        decision = "REDUCED_SCOPE_HARDWARE_SUBMITTED_AWAITING_RESULTS"
    return {
        "schema_version": STAGE205_SCHEMA_VERSION,
        "stage": "stage205_reduced_scope_hardware_submission",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "scope_id": stage203.get("scope_id") if isinstance(stage203, dict) else None,
        "backend": backend_name,
        "budget_cap_usd": stage204.get("budget_cap_usd") if isinstance(stage204, dict) else None,
        "allow_live_submit": allow_live_submit,
        "submission_attempted": attempted,
        "expected_runtime_job_count": expected_runtime_job_count,
        "submitted_runtime_job_count": submitted_count,
        "estimated_total_job_count": stage203.get("estimated_total_job_count") if isinstance(stage203, dict) else None,
        "estimated_total_shots": stage203.get("estimated_total_shots") if isinstance(stage203, dict) else None,
        "submission_records": submission_records,
        "no_hardware_submission": not attempted,
        "hardware_submission_performed": attempted and submitted_count > 0,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "guarded asynchronous submission of reduced-scope packet/calibration templates to IBM Runtime",
                "runtime job IDs are recorded for later result collection when submission succeeds",
                "submission remains separate from result retrieval, calibration pass/fail, and robustness interpretation",
            ],
            "excluded": [
                "provider-side result counts unless a later collector retrieves them",
                "calibration pass/fail",
                "robustness or auditability interpretation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": "Collect Runtime job results, populate Stage203 raw counts, run calibration validation, then recompute robustness and auditability metrics.",
    }


def write_stage205_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "scope_id",
        "backend",
        "budget_cap_usd",
        "allow_live_submit",
        "submission_attempted",
        "expected_runtime_job_count",
        "submitted_runtime_job_count",
        "estimated_total_job_count",
        "estimated_total_shots",
        "no_hardware_submission",
        "hardware_submission_performed",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
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
        writer = csv.DictWriter(handle, fieldnames=("template_type", "packet_id", "circuit_count", "shots", "runtime_job_id", "status", "error_type"))
        writer.writeheader()
        for record in result["submission_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage205_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"backend: {result['backend']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"submission_attempted: {result['submission_attempted']}")
    print(f"submitted_runtime_job_count: {result['submitted_runtime_job_count']}/{result['expected_runtime_job_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
