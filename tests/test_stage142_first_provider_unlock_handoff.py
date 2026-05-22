from __future__ import annotations

import json

from qrope.stage142_first_provider_unlock_handoff import run_stage142_handoff, write_stage142_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage141(path, *, ready: bool = False) -> None:
    _write_json(
        path,
        {
            "decision": "PROVIDER_UNLOCK_PRIORITY_READY_FOR_PREFLIGHT_RERUN" if ready else "PROVIDER_UNLOCK_PRIORITY_PREPARED_EXECUTION_BLOCKED",
            "first_unlock_provider": "ibm_runtime",
            "first_unlock_missing_env_groups": [] if ready else ["IBM_QUANTUM_INSTANCE_CRN"],
            "first_unlock_missing_sdk_modules": [],
            "first_unlock_minimal_actions": [
                "Rerun Stage 106/111/128/129/130/139; then execute only authorized Stage 133 commands."
            ]
            if ready
            else ["Set local env groups without committing values: IBM_QUANTUM_INSTANCE_CRN."],
            "priority_records": [
                {
                    "provider": "ibm_runtime",
                    "priority_score": -1000 if ready else 5,
                    "ready_for_preflight_rerun": ready,
                    "missing_env_groups": [] if ready else ["IBM_QUANTUM_TOKEN or QISKIT_IBM_TOKEN", "IBM_QUANTUM_INSTANCE_CRN"],
                    "missing_sdk_modules": [],
                    "stage139_context_blockers": [],
                    "prepared_job_count": 328,
                    "runner_command_count": 2,
                    "minimal_unlock_actions": ["Set local env groups without committing values."],
                }
            ],
        },
    )


def test_stage142_builds_first_provider_unlock_handoff_without_secrets(tmp_path) -> None:
    stage141 = tmp_path / "stage141.json"
    _stage141(stage141)

    result = run_stage142_handoff(stage141_results_path=stage141)

    assert result["decision"] == "FIRST_PROVIDER_UNLOCK_HANDOFF_READY_ENV_OR_SDK_REQUIRED"
    assert result["first_unlock_provider"] == "ibm_runtime"
    assert result["missing_env_groups"] == ["IBM_QUANTUM_INSTANCE_CRN"]
    assert "IBM_QUANTUM_INSTANCE_CRN=" in result["env_template"]
    assert "IBM_QUANTUM_TOKEN=" not in result["env_template"]
    assert result["minimal_unlock_actions"] == [
        "Set local env groups without committing values: IBM_QUANTUM_INSTANCE_CRN."
    ]
    assert result["secret_values_recorded"] is False


def test_stage142_reports_ready_when_stage141_first_provider_is_ready(tmp_path) -> None:
    stage141 = tmp_path / "stage141.json"
    _stage141(stage141, ready=True)

    result = run_stage142_handoff(stage141_results_path=stage141)

    assert result["decision"] == "FIRST_PROVIDER_UNLOCK_HANDOFF_READY_FOR_PREFLIGHT_RERUN"
    assert result["first_unlock_ready_for_preflight_rerun"] is True
    assert result["missing_env_groups"] == []


def test_stage142_blocks_ready_handoff_with_stage139_context_blocker(tmp_path) -> None:
    stage141 = tmp_path / "stage141.json"
    _stage141(stage141, ready=True)
    payload = json.loads(stage141.read_text(encoding="utf-8"))
    payload["priority_records"][0]["stage139_context_blockers"] = ["stage139_action_checklist_not_ready"]
    _write_json(stage141, payload)

    result = run_stage142_handoff(stage141_results_path=stage141)

    assert result["decision"] == "FIRST_PROVIDER_UNLOCK_HANDOFF_READY_ENV_OR_SDK_REQUIRED"
    assert result["first_unlock_ready_for_preflight_rerun"] is False
    assert result["stage139_context_blockers"] == ["stage139_action_checklist_not_ready"]


def test_stage142_outputs_are_written(tmp_path) -> None:
    stage141 = tmp_path / "stage141.json"
    _stage141(stage141)
    result = run_stage142_handoff(stage141_results_path=stage141)

    paths = write_stage142_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    handoff = (tmp_path / "out" / "handoff.md").read_text(encoding="utf-8")
    template = (tmp_path / "out" / "env_templates" / "ibm_runtime_first_unlock.env.template").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "handoff", "env_template"}
    assert manifest["first_unlock_provider"] == "ibm_runtime"
    assert manifest["missing_env_groups"] == ["IBM_QUANTUM_INSTANCE_CRN"]
    assert manifest["stage139_context_blockers"] == []
    assert "QRoPE Stage 142" in handoff
    assert "IBM_QUANTUM_INSTANCE_CRN=" in template
    assert "IBM_QUANTUM_TOKEN=" not in template
