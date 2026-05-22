from __future__ import annotations

import json

from qrope.stage189_replacement_hardware_readiness_review import run_stage189_replacement_hardware_readiness_review, write_stage189_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage188(path) -> None:
    packets = []
    for seed in (314, 577):
        for template in ("product", "cx"):
            lane = f"ibm_{template}_seed{seed}_rows16_shots4096"
            for family in ("phasewrap", "rope_like", "sinusoidal_like", "alibi_like", "matched_nonzero_null_control"):
                packets.append({"provider": "ibm_runtime", "source_lane_id": lane, "encoding_family": family, "row_count": 16})
    _write_json(
        path,
        {
            "decision": "REPLACEMENT_SEMANTICS_SIM_SUPPORTS_HARDWARE_REOPEN",
            "semantics_id": "matched_nonzero_null_noise_sensitivity_v1",
            "primary_noise_model_ids": ["ibm_backend_median_stochastic", "ibm_backend_p75_stochastic"],
            "candidate_records": [
                {"provider_family": "ibm", "seed": "314", "noise_model_id": "ibm_backend_median_stochastic", "reopen_candidate": True},
                {"provider_family": "ibm", "seed": "577", "noise_model_id": "ibm_backend_median_stochastic", "reopen_candidate": True},
                {"provider_family": "ibm", "seed": "314", "noise_model_id": "ibm_backend_p75_stochastic", "reopen_candidate": True},
                {"provider_family": "ibm", "seed": "577", "noise_model_id": "ibm_backend_p75_stochastic", "reopen_candidate": True},
            ],
            "packets": packets,
        },
    )


def test_stage189_reopens_review_but_blocks_live_run(tmp_path) -> None:
    stage188 = tmp_path / "stage188.json"
    stage176 = tmp_path / "stage176.json"
    _stage188(stage188)
    _write_json(stage176, {"decision": "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_READY_FOR_HUMAN_CHECK", "credit_balance_verified": False})

    result = run_stage189_replacement_hardware_readiness_review(stage188_results_path=stage188, stage176_results_path=stage176)

    assert result["decision"] == "REPLACEMENT_HARDWARE_REVIEW_REOPENED_BUT_NOT_READY_FOR_LIVE_RUN"
    assert result["selected_lane_count"] == 4
    assert result["selected_packet_count"] == 20
    assert result["estimated_packet_row_job_count_before_calibration"] == 320
    assert result["no_hardware_submission"] is True
    assert "replacement_hardware_readiness_requirements_open" in result["blockers"]


def test_stage189_blocks_when_stage188_not_positive(tmp_path) -> None:
    stage188 = tmp_path / "stage188.json"
    stage176 = tmp_path / "stage176.json"
    _write_json(stage188, {"decision": "REPLACEMENT_SEMANTICS_SIM_DOES_NOT_SUPPORT_HARDWARE_REOPEN", "candidate_records": [], "packets": []})
    _write_json(stage176, {"decision": "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_READY_FOR_HUMAN_CHECK"})

    result = run_stage189_replacement_hardware_readiness_review(stage188_results_path=stage188, stage176_results_path=stage176)

    assert result["decision"] == "REPLACEMENT_HARDWARE_REVIEW_NOT_REOPENED"
    assert "stage188_replacement_sim_not_positive" in result["blockers"]


def test_stage189_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage188 = tmp_path / "stage188.json"
    stage176 = tmp_path / "stage176.json"
    _stage188(stage188)
    _write_json(stage176, {"decision": "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_READY_FOR_HUMAN_CHECK", "credit_balance_verified": False})
    result = run_stage189_replacement_hardware_readiness_review(stage188_results_path=stage188, stage176_results_path=stage176)

    paths = write_stage189_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
