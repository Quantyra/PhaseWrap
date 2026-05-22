from __future__ import annotations

import json
from pathlib import Path

from qrope.stage96_claim_card_audit import run_stage96_audit, write_stage96_outputs


def _write_result(root: Path, stage_dir: str, payload: dict[str, object]) -> None:
    directory = root / stage_dir
    directory.mkdir(parents=True)
    (directory / "results.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_stage96_packages_bounded_claim_card(tmp_path) -> None:
    _write_result(
        tmp_path,
        "stage70_strongest_honest_claim_synthesis",
        {
            "strongest_honest_claim": "PhaseWrap-RoPE is compact and auditable, but not a RoPE replacement.",
            "decision": {"decision": "BOUND_STRONGEST_HONEST_CLAIM_WITH_RETRIEVAL_FAILURES"},
            "positive_evidence": [{"source": "stage88_structural_retrieval_routed_copy_expert_audit"}],
            "failure_modes": [{"stage": "stage95_headline_interval_audit"}],
            "unsupported_claims": ["PhaseWrap-RoPE replaces RoPE."],
            "reviewer_next_gate": "Run a stronger matched decoder-only transformer.",
        },
    )
    _write_result(
        tmp_path,
        "stage94_promotion_gate_readiness_audit",
        {
            "decision": {
                "decision": "PROMOTION_GATE_NOT_READY_STRONGEST_CLAIM_BOUNDED",
                "promotion_gate_ready": False,
                "failed_requirements": ["free_learned_phasewrap_original_retrieval_solve"],
                "claim_boundary": "Current evidence still lacks a free learned PhaseWrap-led solve.",
            }
        },
    )
    _write_result(
        tmp_path,
        "stage95_headline_interval_audit",
        {
            "decision": {"confidence_interval_coverage": True},
            "headline_rows": [
                {
                    "headline": "free_learned_best_phase_cued",
                    "lane": "free_learned_pointer_generator",
                    "stage_dir": "stage85_dual_auxiliary_pointer_generator_audit",
                    "task": "phase_cued_retrieval",
                    "method": "sinusoidal",
                    "status": "present",
                    "intervals": {"test_top1_accuracy": {"mean": 0.05, "ci_low": 0.0, "ci_high": 0.116667}},
                }
            ],
        },
    )

    result = run_stage96_audit(artifact_root=tmp_path)

    assert result["stage"] == "stage96_claim_card_audit"
    assert result["status"] == "completed"
    assert result["decision"]["decision"] == "CLAIM_CARD_BOUND_STRONGEST_HONEST_CLAIM"
    assert result["decision"]["promotion_gate_ready"] is False
    assert result["decision"]["headline_intervals_present"] is True
    assert result["claim_card"]["unsupported_claims"] == ["PhaseWrap-RoPE replaces RoPE."]
    assert result["claim_card"]["headline_intervals"][0]["top1_mean"] == 0.05


def test_stage96_reports_missing_sources(tmp_path) -> None:
    result = run_stage96_audit(artifact_root=tmp_path)

    assert result["decision"]["decision"] == "CLAIM_CARD_INCOMPLETE_MISSING_SOURCES"
    assert result["decision"]["missing_source_artifact_count"] == 3


def test_stage96_outputs_are_written(tmp_path) -> None:
    _write_result(
        tmp_path,
        "stage70_strongest_honest_claim_synthesis",
        {
            "strongest_honest_claim": "Bounded claim.",
            "decision": {"decision": "BOUND_STRONGEST_HONEST_CLAIM_WITH_RETRIEVAL_FAILURES"},
            "positive_evidence": [],
            "failure_modes": [],
            "unsupported_claims": ["No replacement claim."],
            "reviewer_next_gate": "Next gate.",
        },
    )
    _write_result(
        tmp_path,
        "stage94_promotion_gate_readiness_audit",
        {"decision": {"promotion_gate_ready": False, "failed_requirements": ["missing_solve"]}},
    )
    _write_result(
        tmp_path,
        "stage95_headline_interval_audit",
        {"decision": {"confidence_interval_coverage": True}, "headline_rows": []},
    )
    result = run_stage96_audit(artifact_root=tmp_path)
    paths = write_stage96_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage96_claim_card_audit"
    assert saved["claim_card"]["strongest_honest_claim"] == "Bounded claim."
    assert "unsupported_claim" in summary
