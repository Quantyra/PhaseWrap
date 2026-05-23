from __future__ import annotations

import json

from qrope.stage213_full_replacement_job_status_poll import run_stage213_full_replacement_job_status_poll, write_stage213_outputs
from qrope.stage214_full_replacement_result_collector import run_stage214_full_replacement_result_collector, write_stage214_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage212(path) -> None:
    records = [{"template_type": "replacement_packet_execution_counts", "packet_id": f"p{i}", "runtime_job_id": f"job-{i}", "submitted_at_utc": "t0", "backend_metadata": {"backend": "ibm_fez"}} for i in range(20)]
    records.append({"template_type": "replacement_known_state_calibration_counts", "packet_id": "", "runtime_job_id": "job-cal", "submitted_at_utc": "t0", "backend_metadata": {"backend": "ibm_fez"}})
    _write_json(path, {"decision": "FULL_REPLACEMENT_HARDWARE_SUBMITTED_AWAITING_RESULTS", "submission_records": records})


def _stage190(path) -> None:
    templates = [
        {
            "template_type": "replacement_packet_execution_counts",
            "packet_id": f"p{i}",
            "raw_counts_by_row": [{"row_id": "r0", "counts": {}}, {"row_id": "r1", "counts": {}}],
        }
        for i in range(20)
    ]
    calibration = {"template_type": "replacement_known_state_calibration_counts", "raw_counts_by_state": [{"state": "00", "counts": {}}, {"state": "01", "counts": {}}]}
    _write_json(path, {"execution_templates": templates, "calibration_template": calibration})


def test_stage213_polls_pending_jobs(tmp_path) -> None:
    stage212 = tmp_path / "stage212.json"
    _stage212(stage212)

    result = run_stage213_full_replacement_job_status_poll(
        stage212_results_path=stage212,
        fetch_status=lambda runtime_job_id: {"runtime_job_id": runtime_job_id, "status": "QUEUED"},
    )

    assert result["decision"] == "FULL_REPLACEMENT_RUNTIME_JOBS_SUBMITTED_RESULTS_PENDING"
    assert result["polled_runtime_job_count"] == 21
    assert result["completed_runtime_job_count"] == 0


def test_stage213_marks_complete_when_all_done(tmp_path) -> None:
    stage212 = tmp_path / "stage212.json"
    _stage212(stage212)

    result = run_stage213_full_replacement_job_status_poll(
        stage212_results_path=stage212,
        fetch_status=lambda runtime_job_id: {"runtime_job_id": runtime_job_id, "status": "DONE"},
    )

    assert result["decision"] == "FULL_REPLACEMENT_RUNTIME_JOBS_COMPLETE_READY_FOR_RESULT_COLLECTION"
    assert result["completed_runtime_job_count"] == 21


def test_stage214_collects_completed_counts(tmp_path) -> None:
    stage212 = tmp_path / "stage212.json"
    stage190 = tmp_path / "stage190.json"
    _stage212(stage212)
    _stage190(stage190)

    def fake_fetch(runtime_job_id):
        return {"status": "DONE", "counts_by_circuit": [{"00": 9, "11": 1}, {"01": 8, "10": 2}]}

    result = run_stage214_full_replacement_result_collector(stage212_results_path=stage212, stage190_results_path=stage190, fetch_result=fake_fetch)

    assert result["decision"] == "FULL_REPLACEMENT_RESULT_COUNTS_COLLECTED_READY_FOR_CALIBRATION"
    assert result["collected_template_count"] == 21
    assert result["collected_templates"][0]["raw_counts_by_row"][0]["counts"] == {"00": 9, "11": 1}


def test_stage214_blocks_when_jobs_pending(tmp_path) -> None:
    stage212 = tmp_path / "stage212.json"
    stage190 = tmp_path / "stage190.json"
    _stage212(stage212)
    _stage190(stage190)

    result = run_stage214_full_replacement_result_collector(
        stage212_results_path=stage212,
        stage190_results_path=stage190,
        fetch_result=lambda runtime_job_id: {"status": "QUEUED", "counts_by_circuit": []},
    )

    assert result["decision"] == "FULL_REPLACEMENT_RESULT_COLLECTION_PENDING_OR_BLOCKED"
    assert "runtime_jobs_not_complete" in result["blockers"]
    assert result["collected_template_count"] == 0


def test_stage213_and_214_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage212 = tmp_path / "stage212.json"
    stage190 = tmp_path / "stage190.json"
    _stage212(stage212)
    _stage190(stage190)
    result213 = run_stage213_full_replacement_job_status_poll(
        stage212_results_path=stage212,
        fetch_status=lambda runtime_job_id: {"runtime_job_id": runtime_job_id, "status": "QUEUED"},
    )
    result214 = run_stage214_full_replacement_result_collector(
        stage212_results_path=stage212,
        stage190_results_path=stage190,
        fetch_result=lambda runtime_job_id: {"status": "QUEUED", "counts_by_circuit": []},
    )

    write_stage213_outputs(result213, tmp_path / "out213")
    write_stage214_outputs(result214, tmp_path / "out214")
    written = "\n".join(
        [
            (tmp_path / "out213" / "results.json").read_text(encoding="utf-8"),
            (tmp_path / "out213" / "summary.csv").read_text(encoding="utf-8"),
            (tmp_path / "out214" / "results.json").read_text(encoding="utf-8"),
            (tmp_path / "out214" / "summary.csv").read_text(encoding="utf-8"),
        ]
    )

    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
