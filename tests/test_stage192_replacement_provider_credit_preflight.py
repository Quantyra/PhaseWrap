from __future__ import annotations

import json

from qrope.stage192_replacement_provider_credit_preflight import run_stage192_replacement_provider_credit_preflight, write_stage192_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path, *, credit_verified: bool = False):
    stage159 = tmp_path / "stage159.json"
    stage176 = tmp_path / "stage176.json"
    stage191 = tmp_path / "stage191.json"
    _write_json(
        stage159,
        {
            "decision": "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL",
            "backend_lookup_ready": True,
            "backend_metadata": {"backend": "ibm_fez", "operational": True, "pending_jobs": 3},
        },
    )
    _write_json(stage176, {"credit_balance_verified": credit_verified})
    _write_json(
        stage191,
        {
            "decision": "REPLACEMENT_APPROVAL_DOSSIER_READY_FOR_HUMAN_REVIEW_NOT_LIVE",
            "replacement_approval_phrase_required": "APPROVE IBM RUNTIME STAGE188 REPLACEMENT LIVE RUN",
            "estimated_total_job_count": 324,
            "estimated_total_shots": 1314720,
        },
    )
    return stage159, stage176, stage191


def test_stage192_blocks_when_current_ibm_configuration_missing(tmp_path) -> None:
    stage159, stage176, stage191 = _sources(tmp_path)

    result = run_stage192_replacement_provider_credit_preflight(
        stage159_results_path=stage159,
        stage176_results_path=stage176,
        stage191_results_path=stage191,
        env={},
    )

    assert result["decision"] == "REPLACEMENT_PROVIDER_CREDIT_PREFLIGHT_BLOCKED"
    assert result["current_local_ibm_configuration_complete"] is False
    assert "current_ibm_configuration_missing_or_incomplete" in result["blockers"]
    assert "credit_billing_runtime_allowance_unverified" in result["blockers"]
    assert result["no_hardware_submission"] is True
    assert result["read_only_backend_lookup_attempted"] is False


def test_stage192_ready_for_read_only_refresh_when_config_and_credit_are_verified(tmp_path) -> None:
    stage159, stage176, stage191 = _sources(tmp_path, credit_verified=True)

    result = run_stage192_replacement_provider_credit_preflight(
        stage159_results_path=stage159,
        stage176_results_path=stage176,
        stage191_results_path=stage191,
        env={
            "IBM_QUANTUM_TOKEN": "secret-token",
            "IBM_QUANTUM_INSTANCE_CRN": "secret-crn",
            "QROPE_IBM_BACKEND": "ibm_fez",
        },
    )

    assert result["decision"] == "REPLACEMENT_PROVIDER_CREDIT_PREFLIGHT_READY_FOR_READ_ONLY_REFRESH"
    assert result["current_local_ibm_configuration_complete"] is True
    assert result["blockers"] == []
    assert result["secret_values_recorded"] is False


def test_stage192_outputs_do_not_record_secret_values_or_live_submit(tmp_path) -> None:
    stage159, stage176, stage191 = _sources(tmp_path, credit_verified=True)
    result = run_stage192_replacement_provider_credit_preflight(
        stage159_results_path=stage159,
        stage176_results_path=stage176,
        stage191_results_path=stage191,
        env={
            "IBM_QUANTUM_TOKEN": "do-not-write-this-token",
            "IBM_QUANTUM_INSTANCE_CRN": "crn:v1:do-not-write-this-crn",
            "QROPE_IBM_BACKEND": "ibm_fez",
        },
    )

    paths = write_stage192_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "do-not-write-this-token" not in written
    assert "crn:v1:do-not-write-this-crn" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
