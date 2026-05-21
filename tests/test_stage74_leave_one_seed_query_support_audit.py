from __future__ import annotations

import json

from qrope.stage74_leave_one_seed_query_support_audit import run_stage74_audit, write_stage74_outputs


def test_stage74_smoke_reports_leave_one_seed_decision() -> None:
    result = run_stage74_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=("no_position", "phasewrap_bias"),
        position_scales=(0.0,),
        cue_scales=(0.0, 8.0),
        distance_scales=(0.0, 4.0),
    )
    assert result["stage"] == "stage74_leave_one_seed_query_support_audit"
    assert result["status"] == "completed"
    assert result["source_stage"] == "stage73_phase_cued_period_pair_support_audit"
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "LEAVE_ONE_SEED_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION",
        "LEAVE_ONE_SEED_QUERY_SUPPORT_PARTIAL_RETRIEVAL",
        "LEAVE_ONE_SEED_QUERY_SUPPORT_RETRIEVAL_FAILED",
    }


def test_stage74_excludes_held_out_seed_from_support_map() -> None:
    result = run_stage74_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=("no_position",),
        position_scales=(0.0,),
        cue_scales=(8.0,),
        distance_scales=(4.0,),
    )
    maps = result["leave_one_seed_support_maps"]
    assert set(maps) == {"307", "311"}
    assert maps["307"] != maps["311"]
    assert all(isinstance(value, int) for support_map in maps.values() for value in support_map.values())


def test_stage74_outputs_are_written(tmp_path) -> None:
    result = run_stage74_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=("no_position",),
        position_scales=(0.0,),
        cue_scales=(8.0,),
        distance_scales=(4.0,),
    )
    paths = write_stage74_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage74_leave_one_seed_query_support_audit"
    assert saved["leave_one_seed_support_maps"]
    assert (tmp_path / "summary.csv").exists()
