from __future__ import annotations

import json

from qrope.stage186_target_control_semantics_audit import run_stage186_target_control_semantics_audit, write_stage186_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _candidate(path, family: str, decision: str) -> None:
    _write_json(
        path,
        {
            "design_family_id": family,
            "decision": decision,
            "reopen_candidate_count": 0,
            "candidate_records": [
                {
                    "min_positional_margin_shot_quanta": -1.0,
                    "min_control_margin_shot_quanta": -2.0,
                },
                {
                    "min_positional_margin_shot_quanta": -3.0,
                    "min_control_margin_shot_quanta": -4.0,
                },
            ],
        },
    )


def _sources(tmp_path):
    stage182 = tmp_path / "stage182.json"
    stage183 = tmp_path / "stage183.json"
    stage184 = tmp_path / "stage184.json"
    stage185 = tmp_path / "stage185.json"
    _candidate(stage182, "pw_balanced_phase_window_v1", "BALANCED_PHASE_WINDOW_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN")
    _candidate(stage183, "pw_contrast_amplified_delta_v1", "CONTRAST_AMPLIFIED_DELTA_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN")
    _candidate(
        stage184,
        "pw_error_orthogonalized_components_v1",
        "ERROR_ORTHOGONALIZED_COMPONENTS_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN",
    )
    _write_json(stage185, {"decision": "REDESIGN_SWEEP_EXHAUSTED_NO_HARDWARE_REOPEN"})
    return stage182, stage183, stage184, stage185


def test_stage186_requires_semantics_revision_after_universal_control_dominance(tmp_path) -> None:
    stage182, stage183, stage184, stage185 = _sources(tmp_path)

    result = run_stage186_target_control_semantics_audit(
        stage182_results_path=stage182,
        stage183_results_path=stage183,
        stage184_results_path=stage184,
        stage185_results_path=stage185,
    )

    assert result["decision"] == "TARGET_CONTROL_SEMANTICS_REVISION_REQUIRED_BEFORE_HARDWARE"
    assert result["candidate_group_count"] == 6
    assert result["negative_control_margin_group_count"] == 6
    assert result["raw_mae_control_dominance_observed"] is True
    assert result["no_hardware_submission"] is True


def test_stage186_blocks_when_redesign_sweep_not_exhausted(tmp_path) -> None:
    stage182, stage183, stage184, stage185 = _sources(tmp_path)
    _write_json(stage185, {"decision": "REDESIGN_SWEEP_FOUND_HARDWARE_REOPEN_CANDIDATE"})

    result = run_stage186_target_control_semantics_audit(
        stage182_results_path=stage182,
        stage183_results_path=stage183,
        stage184_results_path=stage184,
        stage185_results_path=stage185,
    )

    assert result["decision"] == "TARGET_CONTROL_SEMANTICS_AUDIT_INCOMPLETE"
    assert "stage185_redesign_sweep_not_exhausted" in result["blockers"]


def test_stage186_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage182, stage183, stage184, stage185 = _sources(tmp_path)
    result = run_stage186_target_control_semantics_audit(
        stage182_results_path=stage182,
        stage183_results_path=stage183,
        stage184_results_path=stage184,
        stage185_results_path=stage185,
    )

    paths = write_stage186_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
