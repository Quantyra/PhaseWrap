from __future__ import annotations

import json

from qrope.stage157_first_provider_live_run_approval_packet import run_stage157_approval_packet, write_stage157_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage133 = tmp_path / "stage133.json"
    stage152 = tmp_path / "stage152.json"
    stage156 = tmp_path / "stage156.json"
    _write_json(
        stage133,
        {
            "decision": "AUTHORIZED_RUNNER_COMMANDS_PREPARED_EXECUTION_BLOCKED",
            "command_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "job_count": 164,
                    "command_authorized": True,
                    "live_submit_command_available": True,
                    "live_submit_command": "python live.py --allow-live-submit",
                }
            ],
        },
    )
    _write_json(
        stage152,
        {
            "decision": "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER",
        },
    )
    _write_json(
        stage156,
        {
            "decision": "FIRST_PROVIDER_LIVE_RUN_READY_AWAITING_EXPLICIT_APPROVAL",
            "first_unlock_provider": "ibm_runtime",
        },
    )
    return stage133, stage152, stage156


def test_stage157_writes_approval_packet_without_runnable_commands(tmp_path) -> None:
    stage133, stage152, stage156 = _sources(tmp_path)

    result = run_stage157_approval_packet(
        stage133_results_path=stage133,
        stage152_results_path=stage152,
        stage156_results_path=stage156,
    )

    assert result["decision"] == "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY"
    assert result["approval_phrase_required"] == "APPROVE IBM RUNTIME STAGE133 LIVE RUN"
    assert result["authorized_first_provider_job_count"] == 164
    assert result["runnable_commands_recorded"] is False
    assert "live_submit_command" not in result["approval_records"][0]


def test_stage157_blocks_when_stage156_not_paused(tmp_path) -> None:
    stage133, stage152, stage156 = _sources(tmp_path)
    _write_json(stage156, {"decision": "OTHER", "first_unlock_provider": "ibm_runtime"})

    result = run_stage157_approval_packet(
        stage133_results_path=stage133,
        stage152_results_path=stage152,
        stage156_results_path=stage156,
    )

    assert result["decision"] == "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_BLOCKED"
    assert "stage156_not_paused_for_explicit_approval" in result["blockers"]


def test_stage157_outputs_do_not_include_runnable_commands(tmp_path) -> None:
    stage133, stage152, stage156 = _sources(tmp_path)
    result = run_stage157_approval_packet(
        stage133_results_path=stage133,
        stage152_results_path=stage152,
        stage156_results_path=stage156,
    )

    paths = write_stage157_outputs(result, tmp_path / "out")
    combined = "\n".join((tmp_path / "out" / name).read_text(encoding="utf-8") for name in ("results.json", "approval_packet.md", "summary.csv"))

    assert set(paths) == {"manifest", "result", "summary_csv", "approval_packet"}
    assert "--allow-live-submit" not in combined
