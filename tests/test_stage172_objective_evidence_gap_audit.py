from __future__ import annotations

import json

from qrope.stage172_objective_evidence_gap_audit import run_stage172_objective_evidence_gap_audit, write_stage172_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path, *, terminal=False):
    stage103 = tmp_path / "stage103.json"
    stage137 = tmp_path / "stage137.json"
    stage138 = tmp_path / "stage138.json"
    stage148 = tmp_path / "stage148.json"
    stage170 = tmp_path / "stage170.json"
    stage171 = tmp_path / "stage171.json"
    _write_json(
        stage103,
        {
            "decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED",
            "stage104_matched_surface_ready": True,
            "stage104_complete_matched_group_count": 4,
            "ready_to_interpret_hardware_metrics": terminal,
            "missing_execution_count": 0 if terminal else 20,
        },
    )
    _write_json(
        stage137,
        {
            "decision": "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED",
            "ready_window_count": 2 if terminal else 0,
        },
    )
    _write_json(
        stage138,
        {
            "decision": "OBJECTIVE_CLAIM_GATE_SUPPORTED" if terminal else "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE",
            "objective_terminal": terminal,
            "objective_supported": terminal,
            "robustness_terminal": terminal,
            "robustness_supported": terminal,
            "auditability_ready": terminal,
            "stage110_decision": "REPLICATED_ADVANTAGE_CLAIM_SUPPORTED" if terminal else "REPLICATED_ADVANTAGE_CLAIM_BLOCKED_EVIDENCE_INTAKE_INCOMPLETE",
        },
    )
    _write_json(
        stage148,
        {
            "decision": "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_READY" if terminal else "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_BLOCKED_EVIDENCE_REQUIRED",
            "statistical_interpretation_ready": terminal,
            "ready_calibration_record_count": 2 if terminal else 0,
            "shot_noise_separated_lane_count": 2 if terminal else 0,
        },
    )
    _write_json(
        stage170,
        {
            "decision": "IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION",
        },
    )
    _write_json(
        stage171,
        {
            "decision": "POST_RESULT_ANALYSIS_DRY_RUN_READY_FOR_RESULT_INTERPRETATION" if terminal else "POST_RESULT_ANALYSIS_DRY_RUN_READY_AWAITING_PROVIDER_RESULTS",
            "provider_results_missing": not terminal,
            "missing_job_count": 0 if terminal else 328,
        },
    )
    return stage103, stage137, stage138, stage148, stage170, stage171


def test_stage172_maps_current_gap_to_missing_hardware_results(tmp_path) -> None:
    stage103, stage137, stage138, stage148, stage170, stage171 = _sources(tmp_path)

    result = run_stage172_objective_evidence_gap_audit(
        stage103_results_path=stage103,
        stage137_results_path=stage137,
        stage138_results_path=stage138,
        stage148_results_path=stage148,
        stage170_results_path=stage170,
        stage171_results_path=stage171,
    )

    assert result["decision"] == "OBJECTIVE_EVIDENCE_GAP_AUDIT_HARDWARE_RESULTS_REQUIRED"
    assert result["satisfied_requirement_count"] == 2
    assert result["objective_terminal"] is False
    assert result["provider_results_missing"] is True
    assert "hardware_result_counts_missing" in result["blockers"]
    assert "objective_gate_not_terminal" in result["blockers"]


def test_stage172_reports_terminal_when_all_requirements_are_satisfied(tmp_path) -> None:
    stage103, stage137, stage138, stage148, stage170, stage171 = _sources(tmp_path, terminal=True)

    result = run_stage172_objective_evidence_gap_audit(
        stage103_results_path=stage103,
        stage137_results_path=stage137,
        stage138_results_path=stage138,
        stage148_results_path=stage148,
        stage170_results_path=stage170,
        stage171_results_path=stage171,
    )

    assert result["decision"] == "OBJECTIVE_EVIDENCE_GAP_AUDIT_COMPLETE_OBJECTIVE_TERMINAL"
    assert result["unsatisfied_requirement_count"] == 0
    assert result["blockers"] == []


def test_stage172_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage103, stage137, stage138, stage148, stage170, stage171 = _sources(tmp_path)
    result = run_stage172_objective_evidence_gap_audit(
        stage103_results_path=stage103,
        stage137_results_path=stage137,
        stage138_results_path=stage138,
        stage148_results_path=stage148,
        stage170_results_path=stage170,
        stage171_results_path=stage171,
    )

    paths = write_stage172_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
