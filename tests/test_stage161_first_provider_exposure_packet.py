from __future__ import annotations

import json

from qrope.stage161_first_provider_exposure_packet import run_stage161_exposure_packet, write_stage161_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _sources(tmp_path):
    stage157 = tmp_path / "stage157.json"
    stage159 = tmp_path / "stage159.json"
    stage160 = tmp_path / "stage160.json"
    stage114 = tmp_path / "stage114"
    _write_json(
        stage157,
        {
            "decision": "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY",
            "first_unlock_provider": "ibm_runtime",
            "approval_phrase_required": "APPROVE IBM RUNTIME STAGE133 LIVE RUN",
            "approval_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "ibm_runtime__independent_window_00",
                    "job_count": 3,
                    "command_authorized": True,
                    "live_submit_command_available": True,
                }
            ],
        },
    )
    _write_json(
        stage159,
        {
            "decision": "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL",
            "backend_lookup_ready": True,
            "backend_metadata": {"pending_jobs": 3},
        },
    )
    _write_json(stage160, {"decision": "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS"})
    _write_jsonl(
        stage114 / "job_shards" / "ibm_runtime" / "ibm_runtime__independent_window_00" / "jobs.jsonl",
        [
            {
                "job_id": "cal_00",
                "job_kind": "known_state_calibration",
                "provider": "ibm_runtime",
                "shots": 1000,
                "target_evidence_path": "cal.json",
                "window_id": "ibm_runtime__independent_window_00",
            },
            {
                "encoding_family": "phasewrap",
                "job_id": "row_00",
                "job_kind": "matched_packet_row",
                "provider": "ibm_runtime",
                "shots": 4096,
                "target_evidence_path": "phasewrap.json",
                "window_id": "ibm_runtime__independent_window_00",
            },
            {
                "encoding_family": "rope_like",
                "job_id": "row_01",
                "job_kind": "matched_packet_row",
                "provider": "ibm_runtime",
                "shots": 4096,
                "target_evidence_path": "rope.json",
                "window_id": "ibm_runtime__independent_window_00",
            },
        ],
    )
    return stage157, stage159, stage160, stage114


def test_stage161_summarizes_job_and_shot_exposure(tmp_path) -> None:
    stage157, stage159, stage160, stage114 = _sources(tmp_path)

    result = run_stage161_exposure_packet(
        stage157_results_path=stage157,
        stage159_results_path=stage159,
        stage160_results_path=stage160,
        stage114_output_dir=stage114,
    )

    assert result["decision"] == "FIRST_PROVIDER_EXPOSURE_PACKET_READY_AWAITING_APPROVAL"
    assert result["job_count"] == 3
    assert result["total_shots"] == 9192
    assert result["missing_result_record_count"] == 3
    assert result["window_records"][0]["shot_by_job_kind"] == {"known_state_calibration": 1000, "matched_packet_row": 8192}
    assert result["secret_values_recorded"] is False
    assert result["runnable_commands_recorded"] is False


def test_stage161_blocks_on_job_count_mismatch(tmp_path) -> None:
    stage157, stage159, stage160, stage114 = _sources(tmp_path)
    _write_json(
        stage157,
        {
            "decision": "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY",
            "first_unlock_provider": "ibm_runtime",
            "approval_records": [
                {"provider": "ibm_runtime", "window_id": "ibm_runtime__independent_window_00", "job_count": 4, "command_authorized": True}
            ],
        },
    )

    result = run_stage161_exposure_packet(
        stage157_results_path=stage157,
        stage159_results_path=stage159,
        stage160_results_path=stage160,
        stage114_output_dir=stage114,
    )

    assert result["decision"] == "FIRST_PROVIDER_EXPOSURE_PACKET_BLOCKED"
    assert "approved_job_count_total_mismatch" in result["blockers"]
    assert "approval_job_count_mismatch" in result["window_records"][0]["blockers"]


def test_stage161_outputs_do_not_record_secrets_or_live_commands(tmp_path) -> None:
    stage157, stage159, stage160, stage114 = _sources(tmp_path)
    result = run_stage161_exposure_packet(
        stage157_results_path=stage157,
        stage159_results_path=stage159,
        stage160_results_path=stage160,
        stage114_output_dir=stage114,
    )

    paths = write_stage161_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
