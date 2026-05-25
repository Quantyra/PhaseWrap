from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE139_SCHEMA_VERSION = "qrope_stage139_provider_action_readiness_checklist_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE130_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage130_live_cutover_remediation_packet" / "results.json"
DEFAULT_STAGE133_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet" / "results.json"
DEFAULT_STAGE138_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage138_objective_claim_gate" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage139_provider_action_readiness_checklist"
OBJECTIVE = (
    "Determine whether PhaseWrap's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _commands_for_provider(stage133: dict[str, Any] | None, provider: str) -> list[dict[str, Any]]:
    if not isinstance(stage133, dict):
        return []
    return [record for record in stage133.get("command_records", []) if record.get("provider") == provider]


def _first_blocker(record: dict[str, Any]) -> str:
    blockers = list(record.get("stage129_blockers", []))
    if blockers:
        return blockers[0]
    for field in ("stage106_blockers", "stage111_blockers", "stage128_client_blockers"):
        values = list(record.get(field, []))
        if values:
            return f"{field}:{values[0]}"
    if record.get("cutover_authorized") is not True:
        return "cutover_not_authorized"
    return ""


def _provider_record(stage130_record: dict[str, Any], command_records: list[dict[str, Any]]) -> dict[str, Any]:
    provider = str(stage130_record["provider"])
    command_count = len(command_records)
    authorized_command_count = sum(1 for command in command_records if command.get("command_authorized") is True)
    job_count = sum(int(command.get("job_count") or 0) for command in command_records)
    first_blocker = _first_blocker(stage130_record)
    actions = list(stage130_record.get("remediation_actions", []))
    if command_count and authorized_command_count == 0:
        actions.append("After remediation reruns, execute only Stage 133 command records with command_authorized=true.")
    return {
        "provider": provider,
        "cutover_authorized": stage130_record.get("cutover_authorized") is True,
        "stage106_status": stage130_record.get("stage106_status"),
        "stage111_status": stage130_record.get("stage111_status"),
        "stage128_ready": stage130_record.get("stage128_ready"),
        "first_blocker": first_blocker,
        "required_provider_env": stage130_record.get("required_provider_env", []),
        "required_common_env": stage130_record.get("required_common_env", []),
        "sdk_modules": stage130_record.get("sdk_modules", {}),
        "action_count": len(actions),
        "actions": actions,
        "runner_command_count": command_count,
        "authorized_runner_command_count": authorized_command_count,
        "prepared_job_count": job_count,
        "ready_for_live_runner_execution": bool(stage130_record.get("cutover_authorized") is True and authorized_command_count == command_count and command_count > 0),
    }


def run_stage139_checklist(
    *,
    stage130_results_path: Path = DEFAULT_STAGE130_RESULTS,
    stage133_results_path: Path = DEFAULT_STAGE133_RESULTS,
    stage138_results_path: Path = DEFAULT_STAGE138_RESULTS,
) -> dict[str, Any]:
    stage130 = _load_json(stage130_results_path)
    stage133 = _load_json(stage133_results_path)
    stage138 = _load_json(stage138_results_path)
    sources = [(stage130_results_path, stage130), (stage133_results_path, stage133), (stage138_results_path, stage138)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    providers = stage130.get("provider_records", []) if isinstance(stage130, dict) else []
    provider_records = [
        _provider_record(record, _commands_for_provider(stage133, str(record.get("provider"))))
        for record in providers
        if record.get("provider")
    ]
    live_ready_count = sum(1 for record in provider_records if record["ready_for_live_runner_execution"])
    action_count = sum(record["action_count"] for record in provider_records)
    return {
        "schema_version": STAGE139_SCHEMA_VERSION,
        "stage": "stage139_provider_action_readiness_checklist",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_ACTION_CHECKLIST_READY_FOR_LIVE_RUNNER_EXECUTION"
            if provider_records and live_ready_count == len(provider_records) and not missing_sources
            else "PROVIDER_ACTION_CHECKLIST_READY_EXECUTION_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage130_decision": stage130.get("decision") if isinstance(stage130, dict) else None,
        "stage133_decision": stage133.get("decision") if isinstance(stage133, dict) else None,
        "stage138_decision": stage138.get("decision") if isinstance(stage138, dict) else None,
        "provider_count": len(provider_records),
        "live_ready_provider_count": live_ready_count,
        "total_action_count": action_count,
        "prepared_runner_count": sum(record["runner_command_count"] for record in provider_records),
        "authorized_runner_count": sum(record["authorized_runner_command_count"] for record in provider_records),
        "prepared_job_count": sum(record["prepared_job_count"] for record in provider_records),
        "provider_records": provider_records,
        "rerun_sequence": stage130.get("rerun_sequence", []) if isinstance(stage130, dict) else [],
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "provider-level non-secret action checklist derived from Stage 130 remediation and Stage 133 runner commands",
                "ready/not-ready live-runner execution status per provider",
                "explicit preservation of the Stage 138 no-claim boundary while provider execution is blocked",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "live provider SDK client creation",
                "real provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Complete the listed provider actions, rerun the remediation sequence, then execute only Stage 133 commands "
            "that report command_authorized=true before Stage 115 collection and Stage 138 objective gating."
        ),
    }


def write_stage139_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage130_decision": result["stage130_decision"],
        "stage133_decision": result["stage133_decision"],
        "stage138_decision": result["stage138_decision"],
        "provider_count": result["provider_count"],
        "live_ready_provider_count": result["live_ready_provider_count"],
        "total_action_count": result["total_action_count"],
        "prepared_runner_count": result["prepared_runner_count"],
        "authorized_runner_count": result["authorized_runner_count"],
        "prepared_job_count": result["prepared_job_count"],
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
                "cutover_authorized",
                "first_blocker",
                "action_count",
                "runner_command_count",
                "authorized_runner_command_count",
                "prepared_job_count",
                "ready_for_live_runner_execution",
            ),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage139_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"live_ready_provider_count: {result['live_ready_provider_count']}/{result['provider_count']}")
    print(f"authorized_runner_count: {result['authorized_runner_count']}/{result['prepared_runner_count']}")
    print(f"prepared_job_count: {result['prepared_job_count']}")
    print(f"next_gate: {result['next_gate']}")
