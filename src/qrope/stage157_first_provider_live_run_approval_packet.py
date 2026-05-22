from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE157_SCHEMA_VERSION = "qrope_stage157_first_provider_live_run_approval_packet_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE133_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet" / "results.json"
DEFAULT_STAGE152_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage152_first_provider_live_execution_guard" / "results.json"
DEFAULT_STAGE156_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage156_first_provider_live_run_pause" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage157_first_provider_live_run_approval_packet"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE152_READY = "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER"
STAGE156_PAUSED = "FIRST_PROVIDER_LIVE_RUN_READY_AWAITING_EXPLICIT_APPROVAL"
APPROVAL_PHRASE = "APPROVE IBM RUNTIME STAGE133 LIVE RUN"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _authorized_command_records(stage133: dict[str, Any], provider: str | None) -> list[dict[str, Any]]:
    return [
        record
        for record in stage133.get("command_records", [])
        if record.get("provider") == provider
        and record.get("command_authorized") is True
        and record.get("live_submit_command_available") is True
    ]


def run_stage157_approval_packet(
    *,
    stage133_results_path: Path = DEFAULT_STAGE133_RESULTS,
    stage152_results_path: Path = DEFAULT_STAGE152_RESULTS,
    stage156_results_path: Path = DEFAULT_STAGE156_RESULTS,
) -> dict[str, Any]:
    stage133 = _load_json(stage133_results_path)
    stage152 = _load_json(stage152_results_path)
    stage156 = _load_json(stage156_results_path)
    sources = [(stage133_results_path, stage133), (stage152_results_path, stage152), (stage156_results_path, stage156)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    first_provider = stage156.get("first_unlock_provider") if isinstance(stage156, dict) else None
    commands = _authorized_command_records(stage133, first_provider) if isinstance(stage133, dict) else []
    stage152_ready = bool(isinstance(stage152, dict) and stage152.get("decision") == STAGE152_READY)
    stage156_paused = bool(isinstance(stage156, dict) and stage156.get("decision") == STAGE156_PAUSED)
    ready_for_approval = bool(not missing_sources and stage152_ready and stage156_paused and commands)
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if not stage152_ready:
        blockers.append("stage152_not_ready_for_guarded_runner")
    if not stage156_paused:
        blockers.append("stage156_not_paused_for_explicit_approval")
    if not commands:
        blockers.append("no_authorized_first_provider_commands")
    return {
        "schema_version": STAGE157_SCHEMA_VERSION,
        "stage": "stage157_first_provider_live_run_approval_packet",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY"
            if ready_for_approval
            else "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage133_decision": stage133.get("decision") if isinstance(stage133, dict) else None,
        "stage152_decision": stage152.get("decision") if isinstance(stage152, dict) else None,
        "stage156_decision": stage156.get("decision") if isinstance(stage156, dict) else None,
        "first_unlock_provider": first_provider,
        "authorized_first_provider_runner_count": len(commands),
        "authorized_first_provider_job_count": sum(int(record.get("job_count") or 0) for record in commands),
        "approval_phrase_required": APPROVAL_PHRASE,
        "blockers": blockers,
        "approval_records": [
            {
                "provider": record.get("provider"),
                "window_id": record.get("window_id"),
                "job_count": record.get("job_count"),
                "command_authorized": record.get("command_authorized") is True,
                "live_submit_command_available": record.get("live_submit_command_available") is True,
                "command_source_artifact": str(stage133_results_path.as_posix()),
            }
            for record in commands
        ],
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "non-secret approval packet for the first IBM Runtime guarded live run",
                "authorized command counts, job counts, and source artifact references",
                "explicit approval phrase required before any hardware job submission",
            ],
            "excluded": [
                "hardware job submission",
                "runnable live-submit command strings",
                "provider credential values",
                "provider result records",
                "credit balance verification",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            f"Only after the user explicitly says `{APPROVAL_PHRASE}`, read the runnable live-submit commands from "
            "Stage 133, execute only the authorized first-provider commands, then collect Stage 114 shards through "
            "Stage 115 and assemble Stage 113 evidence."
        ),
    }


def _approval_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Stage 157 - First-provider live-run approval packet",
        "",
        f"- Decision: `{result['decision']}`",
        f"- First provider: `{result['first_unlock_provider']}`",
        f"- Authorized runner commands: `{result['authorized_first_provider_runner_count']}`",
        f"- Authorized job count: `{result['authorized_first_provider_job_count']}`",
        f"- Required approval phrase: `{result['approval_phrase_required']}`",
        "- Hardware submitted by this stage: `false`",
        "- Runnable command strings recorded here: `false`",
        "",
        "## Authorized Windows",
    ]
    for record in result["approval_records"]:
        lines.append(
            f"- `{record['window_id']}`: `{record['job_count']}` jobs, command source `{record['command_source_artifact']}`"
        )
    lines.extend(["", "## Next Gate", result["next_gate"], ""])
    return "\n".join(lines)


def write_stage157_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "first_unlock_provider": result["first_unlock_provider"],
        "authorized_first_provider_runner_count": result["authorized_first_provider_runner_count"],
        "authorized_first_provider_job_count": result["authorized_first_provider_job_count"],
        "approval_phrase_required": result["approval_phrase_required"],
        "no_hardware_submission": result["no_hardware_submission"],
        "explicit_user_approval_required": result["explicit_user_approval_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "runnable_commands_recorded": result["runnable_commands_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "approval_packet_path": str((output_dir / "approval_packet.md").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "approval_packet": str(output_dir / "approval_packet.md"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "approval_packet.md").write_text(_approval_markdown(result), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("provider", "window_id", "job_count", "command_authorized", "live_submit_command_available", "command_source_artifact"),
        )
        writer.writeheader()
        for record in result["approval_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage157_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"authorized_first_provider_runner_count: {result['authorized_first_provider_runner_count']}")
    print(f"authorized_first_provider_job_count: {result['authorized_first_provider_job_count']}")
    print(f"approval_phrase_required: {result['approval_phrase_required']}")
    print(f"next_gate: {result['next_gate']}")
