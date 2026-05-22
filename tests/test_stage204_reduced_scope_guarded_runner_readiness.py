from __future__ import annotations

import json

from qrope.stage204_reduced_scope_guarded_runner_readiness import run_stage204_reduced_scope_guarded_runner_readiness, write_stage204_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage203(path, *, backend: str = "ibm_fez", ready: bool = True) -> None:
    _write_json(
        path,
        {
            "decision": "REDUCED_SCOPE_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED_NOT_LIVE" if ready else "REDUCED_SCOPE_EXECUTION_PACKAGE_INCOMPLETE",
            "scope_id": "all_lanes_half_shots_2048",
            "backend": backend,
            "budget_cap_usd": 100.0,
            "packet_template_count": 20,
            "estimated_packet_row_job_count": 320,
            "estimated_calibration_job_count": 4,
            "estimated_total_job_count": 324,
            "estimated_total_shots": 659360,
            "required_execution_fields": ["job_or_task_ids", "backend_metadata", "submitted_at_utc", "completed_at_utc", "raw_counts_by_row"],
            "required_calibration_states": ["00", "01", "10", "11"],
            "no_hardware_submission": True,
            "live_submit_command_created": False,
        },
    )


def _stage193(path, *, backend: str = "ibm_fez", ready: bool = True) -> None:
    _write_json(
        path,
        {
            "decision": "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED" if ready else "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_BLOCKED",
            "backend_lookup_ready": ready,
            "backend_metadata": {"backend": backend, "operational": ready, "pending_jobs": 16},
        },
    )


def test_stage204_ready_after_package_and_fresh_backend_match(tmp_path) -> None:
    stage203 = tmp_path / "stage203.json"
    stage193 = tmp_path / "stage193.json"
    _stage203(stage203)
    _stage193(stage193)

    result = run_stage204_reduced_scope_guarded_runner_readiness(
        stage203_results_path=stage203,
        fresh_stage193_results_path=stage193,
    )

    assert result["decision"] == "REDUCED_SCOPE_GUARDED_RUNNER_READY_FOR_FINAL_EXECUTION_STEP_NOT_LIVE"
    assert result["fresh_backend_matches_package"] is True
    assert result["runnable_commands_recorded"] is False
    assert result["live_submit_command_created"] is False
    assert result["no_hardware_submission"] is True


def test_stage204_blocks_on_backend_mismatch(tmp_path) -> None:
    stage203 = tmp_path / "stage203.json"
    stage193 = tmp_path / "stage193.json"
    _stage203(stage203, backend="ibm_fez")
    _stage193(stage193, backend="ibm_other")

    result = run_stage204_reduced_scope_guarded_runner_readiness(
        stage203_results_path=stage203,
        fresh_stage193_results_path=stage193,
    )

    assert result["decision"] == "REDUCED_SCOPE_GUARDED_RUNNER_READINESS_BLOCKED"
    assert "fresh_backend_does_not_match_stage203_package" in result["blockers"]


def test_stage204_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage203 = tmp_path / "stage203.json"
    stage193 = tmp_path / "stage193.json"
    _stage203(stage203)
    _stage193(stage193)
    result = run_stage204_reduced_scope_guarded_runner_readiness(
        stage203_results_path=stage203,
        fresh_stage193_results_path=stage193,
    )

    paths = write_stage204_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
