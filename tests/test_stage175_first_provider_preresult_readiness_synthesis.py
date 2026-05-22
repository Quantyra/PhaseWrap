from __future__ import annotations

import json

from qrope.stage175_first_provider_preresult_readiness_synthesis import (
    run_stage175_preresult_readiness_synthesis,
    write_stage175_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path, *, credit_verified=False):
    stage160 = tmp_path / "stage160.json"
    stage163 = tmp_path / "stage163.json"
    stage170 = tmp_path / "stage170.json"
    stage171 = tmp_path / "stage171.json"
    stage172 = tmp_path / "stage172.json"
    stage173 = tmp_path / "stage173.json"
    stage174 = tmp_path / "stage174.json"
    _write_json(stage160, {"decision": "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS", "blockers": []})
    _write_json(
        stage163,
        {
            "decision": "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL",
            "locked_job_count": 328,
            "locked_total_shots": 1318720,
            "blockers": [],
        },
    )
    _write_json(
        stage170,
        {
            "decision": (
                "IBM_HARDWARE_PAUSE_READY_FOR_FINAL_HUMAN_GO_NO_GO"
                if credit_verified
                else "IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION"
            ),
            "first_unlock_provider": "ibm_runtime",
            "credit_balance_verified": credit_verified,
            "approval_phrase_required": "APPROVE IBM RUNTIME STAGE133 LIVE RUN",
            "locked_job_count": 328,
            "locked_total_shots": 1318720,
            "stage169_stable_target_lanes": ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"],
            "blockers": [],
        },
    )
    _write_json(stage171, {"decision": "POST_RESULT_ANALYSIS_DRY_RUN_READY_AWAITING_PROVIDER_RESULTS", "blockers": []})
    _write_json(
        stage172,
        {
            "decision": "OBJECTIVE_EVIDENCE_GAP_AUDIT_HARDWARE_RESULTS_REQUIRED",
            "provider_results_missing": True,
            "blockers": ["hardware_result_counts_missing"],
        },
    )
    _write_json(
        stage173,
        {
            "decision": "LOCKED_RESULT_INGESTION_CONTRACT_READY_AWAITING_PROVIDER_RESULTS",
            "locked_job_count": 328,
            "locked_total_shots": 1318720,
            "blockers": [],
        },
    )
    _write_json(
        stage174,
        {
            "decision": "LOCKED_INTERPRETATION_SURFACE_READY_AWAITING_PROVIDER_RESULTS",
            "stable_target_lanes": ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"],
            "matched_packet_job_count": 320,
            "calibration_count_by_window": {"w0": 4, "w1": 4},
            "blockers": [],
        },
    )
    return stage160, stage163, stage170, stage171, stage172, stage173, stage174


def test_stage175_synthesizes_credit_provider_resolution_boundary(tmp_path) -> None:
    paths = _sources(tmp_path)

    result = run_stage175_preresult_readiness_synthesis(
        stage160_results_path=paths[0],
        stage163_results_path=paths[1],
        stage170_results_path=paths[2],
        stage171_results_path=paths[3],
        stage172_results_path=paths[4],
        stage173_results_path=paths[5],
        stage174_results_path=paths[6],
    )

    assert result["decision"] == "FIRST_PROVIDER_PRERESULT_READY_FOR_CREDIT_PROVIDER_RESOLUTION"
    assert result["ready_stage_count"] == 7
    assert result["locked_job_count"] == 328
    assert result["locked_total_shots"] == 1318720
    assert result["credit_balance_verified"] is False
    assert result["blockers"] == []


def test_stage175_reports_final_human_go_ready_when_credit_verified(tmp_path) -> None:
    paths = _sources(tmp_path, credit_verified=True)

    result = run_stage175_preresult_readiness_synthesis(
        stage160_results_path=paths[0],
        stage163_results_path=paths[1],
        stage170_results_path=paths[2],
        stage171_results_path=paths[3],
        stage172_results_path=paths[4],
        stage173_results_path=paths[5],
        stage174_results_path=paths[6],
    )

    assert result["decision"] == "FIRST_PROVIDER_PRERESULT_READY_FOR_FINAL_HUMAN_GO_NO_GO"
    assert result["credit_balance_verified"] is True


def test_stage175_blocks_on_scope_mismatch(tmp_path) -> None:
    paths = _sources(tmp_path)
    stage174 = json.loads(paths[6].read_text(encoding="utf-8"))
    stage174["stable_target_lanes"] = ["ibm_product_seed314_rows16_shots4096"]
    _write_json(paths[6], stage174)

    result = run_stage175_preresult_readiness_synthesis(
        stage160_results_path=paths[0],
        stage163_results_path=paths[1],
        stage170_results_path=paths[2],
        stage171_results_path=paths[3],
        stage172_results_path=paths[4],
        stage173_results_path=paths[5],
        stage174_results_path=paths[6],
    )

    assert result["decision"] == "FIRST_PROVIDER_PRERESULT_READINESS_SYNTHESIS_BLOCKED"
    assert "stable_lane_scope_mismatch" in result["blockers"]


def test_stage175_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    paths = _sources(tmp_path)
    result = run_stage175_preresult_readiness_synthesis(
        stage160_results_path=paths[0],
        stage163_results_path=paths[1],
        stage170_results_path=paths[2],
        stage171_results_path=paths[3],
        stage172_results_path=paths[4],
        stage173_results_path=paths[5],
        stage174_results_path=paths[6],
    )

    paths_out = write_stage175_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths_out) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
