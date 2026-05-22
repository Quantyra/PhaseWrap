from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE154_SCHEMA_VERSION = "qrope_stage154_simulated_hardware_go_no_go_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE153_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage153_simulated_noise_rehearsal" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage154_simulated_hardware_go_no_go"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _is_noisy(record: dict[str, Any]) -> bool:
    return record.get("noise_model_id") != "ideal_deterministic_counts"


def _margin(record: dict[str, Any], comparator_field: str) -> float | None:
    phasewrap = record.get("phasewrap_mean_absolute_score_error")
    comparator = record.get(comparator_field)
    if phasewrap is None or comparator is None:
        return None
    return round(float(comparator) - float(phasewrap), 12)


def _source_counts(records: list[dict[str, Any]], predicate) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        if predicate(record):
            counts[str(record["provider"])] = counts.get(str(record["provider"]), 0) + 1
    return counts


def _family_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        grouped.setdefault(str(record.get("noise_family")), []).append(record)
    summaries = []
    for family, family_records in sorted(grouped.items()):
        strict_records = [record for record in family_records if record.get("phasewrap_beats_all_families_including_control") is True]
        positional_records = [record for record in family_records if record.get("phasewrap_beats_positional_comparators") is True]
        summaries.append(
            {
                "noise_family": family,
                "noisy_group_count": len(family_records),
                "phasewrap_positional_advantage_group_count": len(positional_records),
                "phasewrap_strict_advantage_group_count": len(strict_records),
                "providers_with_strict_advantage": sorted({str(record.get("provider")) for record in strict_records}),
                "templates_with_strict_advantage": sorted({str(record.get("circuit_template")) for record in strict_records}),
            }
        )
    return summaries


def _recommended_targets(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    strict_records = [record for record in records if record.get("phasewrap_beats_all_families_including_control") is True]
    targets = []
    for record in sorted(
        strict_records,
        key=lambda item: (
            str(item.get("noise_model_id")),
            str(item.get("provider")),
            str(item.get("source_lane_id")),
            str(item.get("circuit_template")),
        ),
    ):
        targets.append(
            {
                "noise_model_id": record.get("noise_model_id"),
                "noise_family": record.get("noise_family"),
                "provider": record.get("provider"),
                "source_lane_id": record.get("source_lane_id"),
                "circuit_template": record.get("circuit_template"),
                "phasewrap_mean_absolute_score_error": record.get("phasewrap_mean_absolute_score_error"),
                "best_positional_comparator_mean_absolute_score_error": record.get(
                    "best_positional_comparator_mean_absolute_score_error"
                ),
                "no_position_control_mean_absolute_score_error": record.get("no_position_control_mean_absolute_score_error"),
                "positional_margin": _margin(record, "best_positional_comparator_mean_absolute_score_error"),
                "control_margin": _margin(record, "no_position_control_mean_absolute_score_error"),
            }
        )
    return targets


def run_stage154_go_no_go(*, stage153_results_path: Path = DEFAULT_STAGE153_RESULTS) -> dict[str, Any]:
    stage153 = _load_json(stage153_results_path)
    missing_sources = [] if isinstance(stage153, dict) else [str(stage153_results_path.as_posix())]
    comparison = stage153.get("comparison_summary", []) if isinstance(stage153, dict) else []
    noisy_records = [record for record in comparison if isinstance(record, dict) and _is_noisy(record)]
    complete_noisy_records = [record for record in noisy_records if record.get("all_families_present") is True]
    positional_records = [record for record in complete_noisy_records if record.get("phasewrap_beats_positional_comparators") is True]
    strict_records = [record for record in complete_noisy_records if record.get("phasewrap_beats_all_families_including_control") is True]
    provider_count = len({str(record.get("provider")) for record in complete_noisy_records})
    template_count = len({str(record.get("circuit_template")) for record in complete_noisy_records})
    strict_provider_count = len({str(record.get("provider")) for record in strict_records})
    strict_template_count = len({str(record.get("circuit_template")) for record in strict_records})
    positional_fraction = len(positional_records) / len(complete_noisy_records) if complete_noisy_records else 0.0
    strict_fraction = len(strict_records) / len(complete_noisy_records) if complete_noisy_records else 0.0
    targeted_ready = bool(
        strict_records
        and strict_provider_count >= min(2, provider_count)
        and strict_template_count >= min(2, template_count)
        and positional_fraction >= 0.25
        and strict_fraction >= 0.10
    )
    broad_ready = bool(
        targeted_ready
        and positional_fraction >= 0.50
        and strict_fraction >= 0.25
        and strict_provider_count == provider_count
        and strict_template_count == template_count
    )
    if missing_sources:
        decision = "SIMULATED_HARDWARE_GO_NO_GO_INCOMPLETE"
    elif broad_ready:
        decision = "SIMULATED_NOISE_BROAD_HARDWARE_FOLLOWUP_RECOMMENDED"
    elif targeted_ready:
        decision = "SIMULATED_NOISE_TARGETED_HARDWARE_FOLLOWUP_RECOMMENDED"
    else:
        decision = "SIMULATED_NOISE_HARDWARE_FOLLOWUP_NOT_RECOMMENDED_YET"
    return {
        "schema_version": STAGE154_SCHEMA_VERSION,
        "stage": "stage154_simulated_hardware_go_no_go",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage153_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage153_decision": stage153.get("decision") if isinstance(stage153, dict) else None,
        "noisy_comparison_group_count": len(complete_noisy_records),
        "phasewrap_positional_advantage_group_count": len(positional_records),
        "phasewrap_strict_advantage_group_count": len(strict_records),
        "phasewrap_positional_advantage_fraction": round(positional_fraction, 12),
        "phasewrap_strict_advantage_fraction": round(strict_fraction, 12),
        "provider_count": provider_count,
        "strict_advantage_provider_count": strict_provider_count,
        "template_count": template_count,
        "strict_advantage_template_count": strict_template_count,
        "strict_advantage_by_provider": _source_counts(
            complete_noisy_records, lambda record: record.get("phasewrap_beats_all_families_including_control") is True
        ),
        "positional_advantage_by_provider": _source_counts(
            complete_noisy_records, lambda record: record.get("phasewrap_beats_positional_comparators") is True
        ),
        "noise_family_records": _family_records(complete_noisy_records),
        "recommended_targets": _recommended_targets(complete_noisy_records),
        "simulated_only": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "simulated-only go/no-go interpretation of Stage 153 matched-packet noise rehearsal",
                "target selection for any later live-provider spend based on strict simulated wins",
                "explicit separation between targeted hardware follow-up and broad simulated advantage",
            ],
            "excluded": [
                "real noisy-hardware evidence",
                "credit or provider availability validation",
                "hardware job submission",
                "a Stage 110, Stage 138, or publication-ready noisy-hardware advantage claim",
            ],
        },
        "next_gate": (
            "If targeted follow-up is accepted, clear IBM configuration and run only the selected Stage 107/112/133 "
            "first-provider windows through the guarded live path; otherwise broaden simulator stress tests first."
        ),
    }


def write_stage154_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage153_decision": result["stage153_decision"],
        "noisy_comparison_group_count": result["noisy_comparison_group_count"],
        "phasewrap_positional_advantage_group_count": result["phasewrap_positional_advantage_group_count"],
        "phasewrap_strict_advantage_group_count": result["phasewrap_strict_advantage_group_count"],
        "phasewrap_positional_advantage_fraction": result["phasewrap_positional_advantage_fraction"],
        "phasewrap_strict_advantage_fraction": result["phasewrap_strict_advantage_fraction"],
        "provider_count": result["provider_count"],
        "strict_advantage_provider_count": result["strict_advantage_provider_count"],
        "template_count": result["template_count"],
        "strict_advantage_template_count": result["strict_advantage_template_count"],
        "simulated_only": result["simulated_only"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "noise_model_id",
                "noise_family",
                "provider",
                "source_lane_id",
                "circuit_template",
                "phasewrap_mean_absolute_score_error",
                "best_positional_comparator_mean_absolute_score_error",
                "no_position_control_mean_absolute_score_error",
                "positional_margin",
                "control_margin",
            ),
        )
        writer.writeheader()
        for record in result["recommended_targets"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage154_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"noisy_comparison_group_count: {result['noisy_comparison_group_count']}")
    print(f"phasewrap_positional_advantage_group_count: {result['phasewrap_positional_advantage_group_count']}")
    print(f"phasewrap_strict_advantage_group_count: {result['phasewrap_strict_advantage_group_count']}")
    print(f"recommended_target_count: {len(result['recommended_targets'])}")
    print(f"next_gate: {result['next_gate']}")
