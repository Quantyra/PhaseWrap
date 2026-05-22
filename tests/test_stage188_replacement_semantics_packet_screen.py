from __future__ import annotations

import json

from qrope.stage188_replacement_semantics_packet_screen import run_stage188_replacement_semantics_packet_screen, write_stage188_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage177(path) -> None:
    base = {
        "noise_family": "ibm_backend_properties_stochastic",
        "readout_bitflip_probability": 0.01,
        "depolarizing_observable_shrink": 0.002,
        "ry_angle_scale_error": 0.0,
        "ry_angle_offset_radians": 0.0,
        "observable_bias_component_a": 0.0,
        "observable_bias_component_b": 0.0,
    }
    _write_json(path, {"noise_models": [{**base, "noise_model_id": "ibm_backend_median_stochastic"}, {**base, "noise_model_id": "ibm_backend_p75_stochastic"}]})


def _stage187(path) -> None:
    _write_json(
        path,
        {
            "decision": "REPLACEMENT_SEMANTICS_PREREGISTERED_READY_FOR_PACKET_SCREEN",
            "semantics": {
                "semantics_id": "matched_nonzero_null_noise_sensitivity_v1",
                "hardware_reopen_thresholds": {
                    "min_matched_null_margin_shot_quanta": 2.0,
                    "min_best_positional_margin_shot_quanta": 2.0,
                    "min_independent_seed_pairs": 2,
                },
            },
        },
    )


def _source_packet(path, lane_id: str) -> None:
    rows = [
        {"row_id": f"{lane_id}_row0", "row_hash": "h0", "source": {"reference_delta": -4, "candidate_delta": 0}},
        {"row_id": f"{lane_id}_row1", "row_hash": "h1", "source": {"reference_delta": 0, "candidate_delta": 0}},
        {"row_id": f"{lane_id}_row2", "row_hash": "h2", "source": {"reference_delta": 4, "candidate_delta": 0}},
    ]
    _write_json(path, {"provider": "fixture", "backend": "fixture_backend", "config": {"shot_count": 1000}, "preregistration": {"lane_id": lane_id, "row_set_hash": "rows"}, "rows": rows})


def _source_dir(tmp_path):
    source_dir = tmp_path / "stage4"
    product_files = ("fixture_product_seed1_rows3_shots1000.json",)
    cx_files = ("fixture_cx_seed1_rows3_shots1000.json",)
    _source_packet(source_dir / product_files[0], "fixture_product_seed1_rows3_shots1000")
    _source_packet(source_dir / cx_files[0], "fixture_cx_seed1_rows3_shots1000")
    return source_dir, product_files, cx_files


def test_stage188_runs_replacement_semantics_screen_without_hardware(tmp_path) -> None:
    stage177 = tmp_path / "stage177.json"
    stage187 = tmp_path / "stage187.json"
    _stage177(stage177)
    _stage187(stage187)
    source_dir, product_files, cx_files = _source_dir(tmp_path)

    result = run_stage188_replacement_semantics_packet_screen(
        stage177_results_path=stage177,
        stage187_results_path=stage187,
        source_packet_dir=source_dir,
        product_source_packet_files=product_files,
        cx_source_packet_files=cx_files,
    )

    assert result["status"] == "completed"
    assert result["packet_count"] == 10
    assert result["comparison_group_count"] == 4
    assert result["no_hardware_submission"] is True
    assert "matched_nonzero_null_control" in {record["encoding_family"] for record in result["metric_records"]}


def test_stage188_blocks_without_stage187_ready(tmp_path) -> None:
    stage177 = tmp_path / "stage177.json"
    stage187 = tmp_path / "stage187.json"
    _stage177(stage177)
    _write_json(stage187, {"decision": "NOPE", "semantics": {"semantics_id": "matched_nonzero_null_noise_sensitivity_v1"}})
    source_dir, product_files, cx_files = _source_dir(tmp_path)

    result = run_stage188_replacement_semantics_packet_screen(
        stage177_results_path=stage177,
        stage187_results_path=stage187,
        source_packet_dir=source_dir,
        product_source_packet_files=product_files,
        cx_source_packet_files=cx_files,
    )

    assert result["decision"] == "REPLACEMENT_SEMANTICS_PACKET_SCREEN_INCOMPLETE"
    assert "stage187_replacement_semantics_not_ready" in result["blockers"]


def test_stage188_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage177 = tmp_path / "stage177.json"
    stage187 = tmp_path / "stage187.json"
    _stage177(stage177)
    _stage187(stage187)
    source_dir, product_files, cx_files = _source_dir(tmp_path)
    result = run_stage188_replacement_semantics_packet_screen(
        stage177_results_path=stage177,
        stage187_results_path=stage187,
        source_packet_dir=source_dir,
        product_source_packet_files=product_files,
        cx_source_packet_files=cx_files,
    )

    paths = write_stage188_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "packet_dir"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
