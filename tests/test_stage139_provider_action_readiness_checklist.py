from __future__ import annotations

import json

from qrope.stage139_provider_action_readiness_checklist import run_stage139_checklist, write_stage139_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path, *, ready: bool = False):
    _write_json(
        tmp_path / "stage130.json",
        {
            "decision": "LIVE_CUTOVER_REMEDIATION_PACKET_READY" if ready else "LIVE_CUTOVER_REMEDIATION_PACKET_READY_EXECUTION_BLOCKED",
            "rerun_sequence": ["python scripts/run_stage106_hardware_execution_preflight.py"],
            "provider_records": [
                {
                    "provider": "ibm_runtime",
                    "cutover_authorized": ready,
                    "stage106_status": "ready" if ready else "blocked",
                    "stage111_status": "ready" if ready else "blocked",
                    "stage128_ready": True,
                    "stage129_blockers": [] if ready else ["stage106:ibm_instance_crn_missing"],
                    "stage106_blockers": [] if ready else ["ibm_instance_crn_missing"],
                    "stage111_blockers": [] if ready else ["stage106_provider_preflight_not_ready"],
                    "stage128_client_blockers": [],
                    "required_provider_env": ["IBM_QUANTUM_INSTANCE_CRN"],
                    "required_common_env": ["QROPE_HARDWARE_BUDGET_USD_CAP"],
                    "sdk_modules": {"qiskit": True, "qiskit_ibm_runtime": True},
                    "remediation_actions": [] if ready else ["Set IBM_QUANTUM_INSTANCE_CRN."],
                }
            ],
        },
    )
    _write_json(
        tmp_path / "stage133.json",
        {
            "decision": "AUTHORIZED_RUNNER_COMMANDS_READY" if ready else "AUTHORIZED_RUNNER_COMMANDS_PREPARED_EXECUTION_BLOCKED",
            "command_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "w0",
                    "job_count": 2,
                    "command_authorized": ready,
                }
            ],
        },
    )
    _write_json(tmp_path / "stage138.json", {"decision": "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE"})
    return tmp_path / "stage130.json", tmp_path / "stage133.json", tmp_path / "stage138.json"


def test_stage139_reports_blocked_provider_actions(tmp_path) -> None:
    stage130, stage133, stage138 = _fixture(tmp_path, ready=False)

    result = run_stage139_checklist(stage130_results_path=stage130, stage133_results_path=stage133, stage138_results_path=stage138)

    record = result["provider_records"][0]
    assert result["decision"] == "PROVIDER_ACTION_CHECKLIST_READY_EXECUTION_BLOCKED"
    assert result["live_ready_provider_count"] == 0
    assert result["authorized_runner_count"] == 0
    assert record["first_blocker"] == "stage106:ibm_instance_crn_missing"
    assert record["ready_for_live_runner_execution"] is False
    assert result["secret_values_recorded"] is False


def test_stage139_reports_ready_provider_when_cutover_and_commands_are_authorized(tmp_path) -> None:
    stage130, stage133, stage138 = _fixture(tmp_path, ready=True)

    result = run_stage139_checklist(stage130_results_path=stage130, stage133_results_path=stage133, stage138_results_path=stage138)

    assert result["decision"] == "PROVIDER_ACTION_CHECKLIST_READY_FOR_LIVE_RUNNER_EXECUTION"
    assert result["live_ready_provider_count"] == 1
    assert result["authorized_runner_count"] == 1
    assert result["provider_records"][0]["ready_for_live_runner_execution"] is True


def test_stage139_outputs_are_written(tmp_path) -> None:
    stage130, stage133, stage138 = _fixture(tmp_path, ready=False)
    result = run_stage139_checklist(stage130_results_path=stage130, stage133_results_path=stage133, stage138_results_path=stage138)

    paths = write_stage139_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["prepared_job_count"] == 2
    assert "ibm_runtime" in summary
