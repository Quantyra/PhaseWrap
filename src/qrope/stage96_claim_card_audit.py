from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .stage45_matched_decoder_only_gate import METHOD_NAMES


STAGE96_SCHEMA_VERSION = "qrope_stage96_claim_card_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage96_claim_card_audit"

SOURCE_FILES: tuple[tuple[str, str], ...] = (
    ("stage70_strongest_honest_claim_synthesis", "results.json"),
    ("stage94_promotion_gate_readiness_audit", "results.json"),
    ("stage95_headline_interval_audit", "results.json"),
)


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential claim-card package for the current strongest honest PhaseWrap claim.",
            "A compact mapping from the claim to positive evidence, failure modes, unsupported claims, and next gate.",
            "A publication-facing guardrail artifact that preserves bounded wording from Stage70/94/95.",
        ],
        "excluded": [
            "a claim that PhaseWrap replaces RoPE",
            "a claim that PhaseWrap is currently better than RoPE in fair matched transformer settings",
            "a claim that structural copy experts are standard free decoder-only language modeling",
            "production transformer superiority",
            "full transformer-scale validation",
            "broad quantum advantage",
        ],
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _source_payloads(artifact_root: Path) -> tuple[dict[str, dict[str, Any]], list[str], list[str]]:
    payloads: dict[str, dict[str, Any]] = {}
    source_artifacts: list[str] = []
    missing_source_artifacts: list[str] = []
    for stage_dir, file_name in SOURCE_FILES:
        path = artifact_root / stage_dir / file_name
        source_artifacts.append(str(path.as_posix()))
        payload = _load_json(path)
        if payload is None:
            missing_source_artifacts.append(str(path.as_posix()))
            continue
        payloads[stage_dir] = payload
    return payloads, source_artifacts, missing_source_artifacts


def _headline_interval_rows(stage95: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not stage95:
        return []
    rows: list[dict[str, Any]] = []
    for row in stage95.get("headline_rows", []):
        if row.get("status") != "present":
            continue
        top1 = row.get("intervals", {}).get("test_top1_accuracy", {})
        rows.append(
            {
                "headline": row.get("headline"),
                "lane": row.get("lane"),
                "stage_dir": row.get("stage_dir"),
                "task": row.get("task"),
                "method": row.get("method"),
                "top1_mean": top1.get("mean"),
                "top1_ci_low": top1.get("ci_low"),
                "top1_ci_high": top1.get("ci_high"),
            }
        )
    return rows


def _promotion_gate_status(stage94: dict[str, Any] | None) -> dict[str, Any]:
    if not stage94:
        return {
            "ready": False,
            "decision": "missing_stage94",
            "failed_requirements": ["stage94_promotion_gate_readiness_audit"],
        }
    decision = stage94.get("decision", {})
    return {
        "ready": decision.get("promotion_gate_ready") is True,
        "decision": decision.get("decision"),
        "failed_requirements": decision.get("failed_requirements", []),
        "claim_boundary": decision.get("claim_boundary"),
    }


def _decision(stage70: dict[str, Any] | None, stage94: dict[str, Any] | None, stage95: dict[str, Any] | None, missing_source_artifacts: list[str]) -> dict[str, Any]:
    gate = _promotion_gate_status(stage94)
    intervals_present = bool(stage95 and stage95.get("decision", {}).get("confidence_interval_coverage") is True)
    if missing_source_artifacts:
        decision = "CLAIM_CARD_INCOMPLETE_MISSING_SOURCES"
        boundary = "The claim card cannot be fully assembled because source artifacts are missing."
    elif stage70 and gate["ready"] is False and intervals_present:
        decision = "CLAIM_CARD_BOUND_STRONGEST_HONEST_CLAIM"
        boundary = "The current strongest honest claim is bounded and reportable with intervals, but promotion remains unsupported."
    elif stage70 and gate["ready"] is True:
        decision = "CLAIM_CARD_PROMOTION_REVIEW_REQUIRED"
        boundary = "The claim card found promotion-gate readiness; review before changing external wording."
    else:
        decision = "CLAIM_CARD_INCOMPLETE"
        boundary = "The claim card lacks enough evidence to package the current strongest claim."
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "promotion_gate_ready": gate["ready"],
        "promotion_failed_requirements": gate["failed_requirements"],
        "headline_intervals_present": intervals_present,
        "missing_source_artifact_count": len(missing_source_artifacts),
    }


def run_stage96_audit(*, artifact_root: Path = DEFAULT_ARTIFACT_ROOT, method_names: tuple[str, ...] = METHOD_NAMES) -> dict[str, Any]:
    payloads, source_artifacts, missing_source_artifacts = _source_payloads(artifact_root)
    stage70 = payloads.get("stage70_strongest_honest_claim_synthesis")
    stage94 = payloads.get("stage94_promotion_gate_readiness_audit")
    stage95 = payloads.get("stage95_headline_interval_audit")
    supported_evidence = stage70.get("positive_evidence", []) if stage70 else []
    failure_modes = stage70.get("failure_modes", []) if stage70 else []
    unsupported_claims = stage70.get("unsupported_claims", []) if stage70 else []
    result = {
        "schema_version": STAGE96_SCHEMA_VERSION,
        "stage": "stage96_claim_card_audit",
        "status": "completed",
        "source_stage": "stage95_headline_interval_audit",
        "source_artifacts": source_artifacts,
        "missing_source_artifacts": missing_source_artifacts,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(method_names),
        "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "content_key_retrieval", "tiny_text_fact_qa"],
        "claim_boundary": _claim_boundary(),
        "claim_card": {
            "strongest_honest_claim": stage70.get("strongest_honest_claim") if stage70 else None,
            "decision": stage70.get("decision", {}).get("decision") if stage70 else None,
            "supported_evidence": supported_evidence,
            "failure_modes": failure_modes,
            "unsupported_claims": unsupported_claims,
            "promotion_gate_status": _promotion_gate_status(stage94),
            "headline_intervals": _headline_interval_rows(stage95),
            "reviewer_next_gate": stage70.get("reviewer_next_gate") if stage70 else None,
        },
    }
    result["decision"] = _decision(stage70, stage94, stage95, missing_source_artifacts)
    return result


def write_stage96_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "source_stage": result["source_stage"],
        "source_artifacts": result["source_artifacts"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "decision": result["decision"],
        "claim_boundary": result["claim_boundary"],
        "strongest_honest_claim": result["claim_card"]["strongest_honest_claim"],
        "unsupported_claims": result["claim_card"]["unsupported_claims"],
        "missing_source_artifacts": result["missing_source_artifacts"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    summary_rows = [
        {"section": "claim", "item": "strongest_honest_claim", "value": result["claim_card"]["strongest_honest_claim"]},
        {"section": "decision", "item": "decision", "value": result["decision"]["decision"]},
        {"section": "decision", "item": "promotion_gate_ready", "value": str(result["decision"]["promotion_gate_ready"])},
    ]
    summary_rows.extend(
        {"section": "unsupported_claim", "item": str(index), "value": claim}
        for index, claim in enumerate(result["claim_card"]["unsupported_claims"], start=1)
    )
    summary_rows.extend(
        {"section": "headline_interval", "item": str(row["headline"]), "value": json.dumps(row, sort_keys=True)}
        for row in result["claim_card"]["headline_intervals"]
    )
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("section", "item", "value"))
        writer.writeheader()
        writer.writerows(summary_rows)
    return paths


def print_stage96_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
    print(f"promotion_failed_requirements: {', '.join(result['decision']['promotion_failed_requirements'])}")
