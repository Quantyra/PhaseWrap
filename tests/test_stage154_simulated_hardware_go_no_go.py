from __future__ import annotations

import json

from qrope.stage154_simulated_hardware_go_no_go import run_stage154_go_no_go, write_stage154_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _record(noise, provider, template, *, positional: bool, strict: bool) -> dict[str, object]:
    return {
        "noise_model_id": noise,
        "noise_family": noise.split("_")[0],
        "provider": provider,
        "source_lane_id": f"{provider}_{template}",
        "circuit_template": template,
        "all_families_present": True,
        "phasewrap_beats_positional_comparators": positional,
        "phasewrap_beats_all_families_including_control": strict,
        "phasewrap_mean_absolute_score_error": 0.01,
        "best_positional_comparator_mean_absolute_score_error": 0.02 if positional else 0.005,
        "no_position_control_mean_absolute_score_error": 0.03 if strict else 0.0,
    }


def _stage153(path, records) -> None:
    _write_json(
        path,
        {
            "decision": "SIMULATED_NOISE_PHASEWRAP_STRICT_ADVANTAGE_OBSERVED",
            "comparison_summary": records,
        },
    )


def test_stage154_recommends_targeted_followup_for_cross_provider_strict_wins(tmp_path) -> None:
    stage153 = tmp_path / "stage153.json"
    records = [
        _record("ideal_deterministic_counts", "ibm_runtime", "product", positional=True, strict=False),
        _record("ry_offset_0p02rad", "ibm_runtime", "product", positional=True, strict=True),
        _record("ry_offset_0p02rad", "ibm_runtime", "cx", positional=True, strict=True),
        _record("biased_observable_plus_2pct", "amazon_braket", "product", positional=True, strict=True),
        _record("biased_observable_plus_2pct", "amazon_braket", "cx", positional=True, strict=True),
        _record("readout_bitflip_1pct", "ibm_runtime", "cx", positional=True, strict=False),
        _record("readout_bitflip_1pct", "amazon_braket", "cx", positional=False, strict=False),
        _record("observable_depolarizing_5pct", "ibm_runtime", "product", positional=False, strict=False),
        _record("observable_depolarizing_5pct", "amazon_braket", "product", positional=False, strict=False),
        _record("ry_underrotation_2pct", "ibm_runtime", "cx", positional=False, strict=False),
        _record("ry_underrotation_2pct", "amazon_braket", "cx", positional=False, strict=False),
        _record("ry_overrotation_2pct", "ibm_runtime", "product", positional=False, strict=False),
        _record("ry_overrotation_2pct", "amazon_braket", "product", positional=False, strict=False),
        _record("combined_noise", "ibm_runtime", "cx", positional=False, strict=False),
        _record("combined_noise", "amazon_braket", "cx", positional=False, strict=False),
    ]
    _stage153(stage153, records)

    result = run_stage154_go_no_go(stage153_results_path=stage153)

    assert result["decision"] == "SIMULATED_NOISE_TARGETED_HARDWARE_FOLLOWUP_RECOMMENDED"
    assert result["simulated_only"] is True
    assert result["phasewrap_strict_advantage_group_count"] == 4
    assert result["strict_advantage_provider_count"] == 2
    assert result["strict_advantage_template_count"] == 2
    assert len(result["recommended_targets"]) == 4


def test_stage154_does_not_recommend_hardware_without_strict_control_wins(tmp_path) -> None:
    stage153 = tmp_path / "stage153.json"
    records = [
        _record("readout_bitflip_1pct", "ibm_runtime", "product", positional=True, strict=False),
        _record("readout_bitflip_1pct", "ibm_runtime", "cx", positional=True, strict=False),
        _record("readout_bitflip_1pct", "amazon_braket", "product", positional=False, strict=False),
        _record("readout_bitflip_1pct", "amazon_braket", "cx", positional=False, strict=False),
    ]
    _stage153(stage153, records)

    result = run_stage154_go_no_go(stage153_results_path=stage153)

    assert result["decision"] == "SIMULATED_NOISE_HARDWARE_FOLLOWUP_NOT_RECOMMENDED_YET"
    assert result["phasewrap_strict_advantage_group_count"] == 0
    assert result["recommended_targets"] == []


def test_stage154_outputs_are_written(tmp_path) -> None:
    stage153 = tmp_path / "stage153.json"
    _stage153(
        stage153,
        [
            _record("ry_offset_0p02rad", "ibm_runtime", "product", positional=True, strict=True),
            _record("ry_offset_0p02rad", "ibm_runtime", "cx", positional=True, strict=True),
        ],
    )
    result = run_stage154_go_no_go(stage153_results_path=stage153)

    paths = write_stage154_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["simulated_only"] is True
    assert "control_margin" in summary
