from __future__ import annotations

import json
from pathlib import Path
from typing import Any


STAGE142_SCHEMA_VERSION = "qrope_stage142_first_provider_unlock_handoff_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE141_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage141_provider_unlock_priority" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage142_first_provider_unlock_handoff"
OBJECTIVE = (
    "Determine whether PhaseWrap's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_keys(group: str) -> list[str]:
    return [part.strip() for part in group.split(" or ") if part.strip()]


def _template_lines(provider: str, missing_env_groups: list[str]) -> list[str]:
    lines = [
        f"# {provider} first-unlock environment placeholders.",
        "# Fill locally only; do not commit credential values.",
    ]
    keys: list[str] = []
    for group in missing_env_groups:
        keys.extend(_candidate_keys(group))
    for key in sorted(set(keys)):
        lines.append(f"{key}=")
    return lines + [""]


def _first_record(stage141: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(stage141, dict):
        return None
    provider = stage141.get("first_unlock_provider")
    for record in stage141.get("priority_records", []):
        if record.get("provider") == provider:
            return record
    return None


def _handoff_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# QRoPE Stage 142 - First Provider Unlock Handoff",
        "",
        f"Provider: `{result['first_unlock_provider']}`",
        f"Decision: `{result['decision']}`",
        "",
        "## Missing Environment Groups",
    ]
    lines.extend(f"- `{group}`" for group in result["missing_env_groups"] or ["none"])
    lines.extend(["", "## Missing SDK Modules"])
    lines.extend(f"- `{module}`" for module in result["missing_sdk_modules"] or ["none"])
    lines.extend(["", "## Stage 139 Context Blockers"])
    lines.extend(f"- `{blocker}`" for blocker in result["stage139_context_blockers"] or ["none"])
    lines.extend(["", "## Rerun Commands"])
    lines.extend(f"- `{command}`" for command in result["rerun_commands"])
    lines.extend(
        [
            "",
            "## Boundary",
            "- This handoff records only environment key names and placeholders.",
            "- No provider credential values are recorded.",
            "- No hardware submission or live provider client creation occurs.",
        ]
    )
    return "\n".join(lines) + "\n"


def run_stage142_handoff(*, stage141_results_path: Path = DEFAULT_STAGE141_RESULTS) -> dict[str, Any]:
    stage141 = _load_json(stage141_results_path)
    missing_sources = [] if isinstance(stage141, dict) else [str(stage141_results_path.as_posix())]
    first = _first_record(stage141)
    top_level_missing_env = stage141.get("first_unlock_missing_env_groups", []) if isinstance(stage141, dict) else []
    top_level_missing_sdk = stage141.get("first_unlock_missing_sdk_modules", []) if isinstance(stage141, dict) else []
    top_level_actions = stage141.get("first_unlock_minimal_actions", []) if isinstance(stage141, dict) else []
    missing_env = list(top_level_missing_env or (first.get("missing_env_groups", []) if first else []))
    missing_sdk = list(top_level_missing_sdk or (first.get("missing_sdk_modules", []) if first else []))
    stage139_context_blockers = list(first.get("stage139_context_blockers", []) if first else [])
    ready = bool(first and first.get("ready_for_preflight_rerun") is True and not stage139_context_blockers)
    provider = first.get("provider") if first else None
    rerun_commands = [
        "python scripts/run_stage140_local_provider_configuration_readiness.py --load-dotenv",
        "python scripts/run_stage106_hardware_execution_preflight.py --load-dotenv",
        "python scripts/run_stage111_provider_sdk_backend_discovery.py",
        "python scripts/run_stage128_sdk_client_factory_audit.py",
        "python scripts/run_stage129_live_cutover_authorization_audit.py",
        "python scripts/run_stage130_live_cutover_remediation_packet.py",
        "python scripts/run_stage139_provider_action_readiness_checklist.py",
        "python scripts/run_stage141_provider_unlock_priority.py",
    ]
    return {
        "schema_version": STAGE142_SCHEMA_VERSION,
        "stage": "stage142_first_provider_unlock_handoff",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_UNLOCK_HANDOFF_READY_FOR_PREFLIGHT_RERUN"
            if ready
            else "FIRST_PROVIDER_UNLOCK_HANDOFF_READY_ENV_OR_SDK_REQUIRED"
        ),
        "source_artifacts": [str(stage141_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage141_decision": stage141.get("decision") if isinstance(stage141, dict) else None,
        "first_unlock_provider": provider,
        "first_unlock_ready_for_preflight_rerun": ready,
        "priority_score": first.get("priority_score") if first else None,
        "missing_env_groups": missing_env,
        "missing_sdk_modules": missing_sdk,
        "stage139_context_blockers": stage139_context_blockers,
        "prepared_job_count": first.get("prepared_job_count") if first else None,
        "runner_command_count": first.get("runner_command_count") if first else None,
        "minimal_unlock_actions": list(top_level_actions or (first.get("minimal_unlock_actions", []) if first else [])),
        "rerun_commands": rerun_commands,
        "env_template_file": f"{provider}_first_unlock.env.template" if provider else None,
        "env_template": "\n".join(_template_lines(str(provider), missing_env)) if provider else "",
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "first-provider unlock handoff using Stage 141 priority evidence",
                "Stage 139 action-checklist context blockers are preserved before local preflight rerun readiness",
                "non-secret environment placeholder template for the first provider",
                "ordered rerun commands after local configuration is filled",
            ],
            "excluded": [
                "provider credential values",
                "hardware job submission",
                "live provider SDK client creation",
                "real provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Fill the first-provider local environment outside git, rerun Stage 142/140, then follow the listed rerun "
            "commands before any Stage 133 live runner command."
        ),
    }


def write_stage142_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    template_dir = output_dir / "env_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_path = template_dir / str(result["env_template_file"])
    if result["env_template_file"]:
        template_path.write_text(result["env_template"], encoding="utf-8")
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage141_decision": result["stage141_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "first_unlock_ready_for_preflight_rerun": result["first_unlock_ready_for_preflight_rerun"],
        "priority_score": result["priority_score"],
        "missing_env_groups": result["missing_env_groups"],
        "missing_sdk_modules": result["missing_sdk_modules"],
        "stage139_context_blockers": result["stage139_context_blockers"],
        "minimal_unlock_actions": result["minimal_unlock_actions"],
        "prepared_job_count": result["prepared_job_count"],
        "runner_command_count": result["runner_command_count"],
        "env_template_path": str(template_path.as_posix()) if result["env_template_file"] else None,
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "handoff_path": str((output_dir / "handoff.md").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "handoff": str(output_dir / "handoff.md"),
        "env_template": str(template_path),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "handoff.md").write_text(_handoff_markdown(result), encoding="utf-8")
    return paths


def print_stage142_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"first_unlock_ready_for_preflight_rerun: {result['first_unlock_ready_for_preflight_rerun']}")
    print(f"next_gate: {result['next_gate']}")
