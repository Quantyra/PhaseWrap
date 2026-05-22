from __future__ import annotations

import json

from qrope.stage205_reduced_scope_hardware_submission import run_stage205_reduced_scope_hardware_submission, write_stage205_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _template(index: int) -> dict:
    return {
        "template_type": "reduced_scope_packet_execution_counts",
        "packet_id": f"packet-{index}",
        "source_lane_id": "lane",
        "encoding_family": "phasewrap",
        "circuit_template": "two_ry_product_state_z_readout_v1",
        "shot_count": 2048,
        "raw_counts_by_row": [{"row_id": "r0", "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\nbit[2] c;\nc[0] = measure q[0];\nc[1] = measure q[1];\n"}],
    }


def _sources(tmp_path):
    stage204 = tmp_path / "stage204.json"
    stage203 = tmp_path / "stage203.json"
    templates = [_template(index) for index in range(20)]
    calibration = {
        "template_type": "reduced_scope_known_state_calibration_counts",
        "shots_per_state": 1000,
        "raw_counts_by_state": [{"state": state, "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\nbit[2] c;\nc[0] = measure q[0];\nc[1] = measure q[1];\n"} for state in ("00", "01", "10", "11")],
    }
    _write_json(
        stage204,
        {
            "decision": "REDUCED_SCOPE_GUARDED_RUNNER_READY_FOR_FINAL_EXECUTION_STEP_NOT_LIVE",
            "backend": "ibm_fez",
            "budget_cap_usd": 100.0,
        },
    )
    _write_json(
        stage203,
        {
            "decision": "REDUCED_SCOPE_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED_NOT_LIVE",
            "scope_id": "all_lanes_half_shots_2048",
            "estimated_total_job_count": 324,
            "estimated_total_shots": 659360,
            "execution_templates": templates,
            "calibration_template": calibration,
        },
    )
    return stage204, stage203


def test_stage205_blocks_without_allow_live_submit(tmp_path) -> None:
    stage204, stage203 = _sources(tmp_path)

    result = run_stage205_reduced_scope_hardware_submission(stage204_results_path=stage204, stage203_results_path=stage203)

    assert result["decision"] == "REDUCED_SCOPE_HARDWARE_SUBMISSION_BLOCKED_OR_PARTIAL"
    assert "allow_live_submit_flag_required" in result["blockers"]
    assert result["submission_attempted"] is False
    assert result["no_hardware_submission"] is True


def test_stage205_records_fake_async_submission_ids(tmp_path) -> None:
    stage204, stage203 = _sources(tmp_path)

    def fake_submit(*, template, backend_name):
        return {
            "runtime_job_id": f"job-{template.get('packet_id', 'calibration') or 'calibration'}",
            "submitted_at_utc": "2026-05-22T00:00:00+00:00",
            "backend_metadata": {"backend": backend_name, "provider": "ibm_runtime"},
        }

    result = run_stage205_reduced_scope_hardware_submission(
        stage204_results_path=stage204,
        stage203_results_path=stage203,
        allow_live_submit=True,
        submit_template=fake_submit,
    )

    assert result["decision"] == "REDUCED_SCOPE_HARDWARE_SUBMITTED_AWAITING_RESULTS"
    assert result["submitted_runtime_job_count"] == 21
    assert result["hardware_submission_performed"] is True
    assert result["secret_values_recorded"] is False


def test_stage205_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage204, stage203 = _sources(tmp_path)
    result = run_stage205_reduced_scope_hardware_submission(stage204_results_path=stage204, stage203_results_path=stage203)

    paths = write_stage205_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
