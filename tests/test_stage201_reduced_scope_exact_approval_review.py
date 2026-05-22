from __future__ import annotations

import json

from qrope.stage201_reduced_scope_exact_approval_review import (
    REDUCED_SCOPE_APPROVAL_PHRASE,
    run_stage201_reduced_scope_exact_approval_review,
    write_stage201_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage200(path, *, attested: bool = False) -> None:
    decision = (
        "REDUCED_SCOPE_CREDIT_ATTESTATION_ACCEPTED_READY_FOR_EXACT_APPROVAL_REVIEW"
        if attested
        else "REDUCED_SCOPE_ATTESTATION_INTAKE_AWAITING_EXACT_PHRASE"
    )
    _write_json(
        path,
        {
            "decision": decision,
            "human_credit_allowance_verified": attested,
            "scope_id": "all_lanes_half_shots_2048",
            "hardware_scope_label": "reduced_precision_all_lanes_2048_shots_v1",
            "estimated_total_job_count": 324,
            "estimated_total_shots": 659360,
            "budget_cap_usd": 25.0,
            "required_attestation_phrase": "ATTEST IBM CREDIT FOR REDUCED SCOPE STAGE199 WITH 25 USD CAP",
        },
    )


def test_stage201_blocks_exact_approval_until_credit_attestation(tmp_path) -> None:
    stage200 = tmp_path / "stage200.json"
    _stage200(stage200, attested=False)

    result = run_stage201_reduced_scope_exact_approval_review(
        stage200_results_path=stage200,
        provided_approval_phrase=REDUCED_SCOPE_APPROVAL_PHRASE,
    )

    assert result["decision"] == "REDUCED_SCOPE_EXACT_APPROVAL_REVIEW_BLOCKED_CREDIT_ATTESTATION_REQUIRED"
    assert result["approval_phrase_matches"] is False
    assert "reduced_scope_credit_attestation_not_accepted" in result["blockers"]
    assert result["no_hardware_submission"] is True


def test_stage201_rejects_wrong_phrase_after_credit_attestation(tmp_path) -> None:
    stage200 = tmp_path / "stage200.json"
    _stage200(stage200, attested=True)

    result = run_stage201_reduced_scope_exact_approval_review(
        stage200_results_path=stage200,
        provided_approval_phrase="APPROVE IBM RUNTIME STAGE188 REPLACEMENT LIVE RUN",
    )

    assert result["decision"] == "REDUCED_SCOPE_EXACT_APPROVAL_REVIEW_BLOCKED"
    assert result["approval_phrase_matches"] is False
    assert "exact_reduced_scope_approval_phrase_missing_or_mismatched" in result["blockers"]


def test_stage201_accepts_exact_reduced_scope_phrase_after_credit_attestation(tmp_path) -> None:
    stage200 = tmp_path / "stage200.json"
    _stage200(stage200, attested=True)

    result = run_stage201_reduced_scope_exact_approval_review(
        stage200_results_path=stage200,
        provided_approval_phrase=REDUCED_SCOPE_APPROVAL_PHRASE,
    )

    assert result["decision"] == "REDUCED_SCOPE_EXACT_APPROVAL_ACCEPTED_READY_FOR_LIVE_RUNNER_PREPARATION_REVIEW"
    assert result["approval_phrase_matches"] is True
    assert result["blockers"] == []
    assert result["live_submit_command_created"] is False
    assert result["runnable_commands_recorded"] is False


def test_stage201_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage200 = tmp_path / "stage200.json"
    _stage200(stage200, attested=False)
    result = run_stage201_reduced_scope_exact_approval_review(stage200_results_path=stage200)

    paths = write_stage201_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
