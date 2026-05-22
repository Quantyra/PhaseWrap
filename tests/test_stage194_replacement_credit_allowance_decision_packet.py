from __future__ import annotations

import json

from qrope.stage194_replacement_credit_allowance_decision_packet import (
    run_stage194_replacement_credit_allowance_decision_packet,
    write_stage194_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path, *, pending_jobs: int = 16):
    stage191 = tmp_path / "stage191.json"
    stage193 = tmp_path / "stage193.json"
    _write_json(
        stage191,
        {
            "decision": "REPLACEMENT_APPROVAL_DOSSIER_READY_FOR_HUMAN_REVIEW_NOT_LIVE",
            "estimated_total_job_count": 324,
            "estimated_total_shots": 1314720,
            "replacement_approval_phrase_required": "APPROVE IBM RUNTIME STAGE188 REPLACEMENT LIVE RUN",
        },
    )
    _write_json(
        stage193,
        {
            "decision": "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED",
            "backend_metadata": {"backend": "ibm_fez", "operational": True, "pending_jobs": pending_jobs},
        },
    )
    return stage191, stage193


def test_stage194_ready_for_human_attestation_when_local_caps_pass(tmp_path) -> None:
    stage191, stage193 = _sources(tmp_path)

    result = run_stage194_replacement_credit_allowance_decision_packet(
        stage191_results_path=stage191,
        stage193_results_path=stage193,
        env={"QROPE_HARDWARE_BUDGET_USD_CAP": "25", "QROPE_HARDWARE_QUEUE_DEPTH_CAP": "25"},
    )

    assert result["decision"] == "REPLACEMENT_CREDIT_ALLOWANCE_READY_FOR_HUMAN_ATTESTATION_NOT_LIVE"
    assert result["budget_cap_usd"] == 25.0
    assert result["queue_depth_within_cap"] is True
    assert result["blockers"] == ["ibm_credit_billing_runtime_allowance_unverified"]
    assert result["no_hardware_submission"] is True


def test_stage194_blocks_when_queue_exceeds_local_cap(tmp_path) -> None:
    stage191, stage193 = _sources(tmp_path, pending_jobs=31)

    result = run_stage194_replacement_credit_allowance_decision_packet(
        stage191_results_path=stage191,
        stage193_results_path=stage193,
        env={"QROPE_HARDWARE_BUDGET_USD_CAP": "25", "QROPE_HARDWARE_QUEUE_DEPTH_CAP": "25"},
    )

    assert result["decision"] == "REPLACEMENT_CREDIT_ALLOWANCE_DECISION_PACKET_BLOCKED"
    assert "backend_queue_depth_missing_or_exceeded" in result["blockers"]


def test_stage194_can_record_human_credit_attestation_without_accepting_live_approval(tmp_path) -> None:
    stage191, stage193 = _sources(tmp_path)

    result = run_stage194_replacement_credit_allowance_decision_packet(
        stage191_results_path=stage191,
        stage193_results_path=stage193,
        env={"QROPE_HARDWARE_BUDGET_USD_CAP": "25", "QROPE_HARDWARE_QUEUE_DEPTH_CAP": "25"},
        human_credit_allowance_verified=True,
    )

    assert result["decision"] == "REPLACEMENT_CREDIT_ALLOWANCE_VERIFIED_READY_FOR_EXACT_APPROVAL_REVIEW"
    assert result["human_credit_allowance_verified"] is True
    exact_item = [item for item in result["decision_items"] if item["item_id"] == "exact_replacement_approval"][0]
    assert exact_item["status"] == "not_requested"
    assert exact_item["evidence"]["approval_phrase_accepted_here"] is False


def test_stage194_outputs_do_not_record_secret_values_or_live_submit(tmp_path) -> None:
    stage191, stage193 = _sources(tmp_path)
    result = run_stage194_replacement_credit_allowance_decision_packet(
        stage191_results_path=stage191,
        stage193_results_path=stage193,
        env={
            "QROPE_HARDWARE_BUDGET_USD_CAP": "25",
            "QROPE_HARDWARE_QUEUE_DEPTH_CAP": "25",
            "IBM_QUANTUM_TOKEN": "do-not-write-token",
            "IBM_QUANTUM_INSTANCE_CRN": "crn:v1:do-not-write-crn",
        },
    )

    paths = write_stage194_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "do-not-write-token" not in written
    assert "crn:v1:do-not-write-crn" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
