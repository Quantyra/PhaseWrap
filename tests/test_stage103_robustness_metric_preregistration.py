from __future__ import annotations

import json

from qrope.stage103_robustness_metric_preregistration import (
    expectation_from_counts,
    packet_metrics,
    run_stage103_preregistration,
    score_from_counts,
    write_stage103_outputs,
)


def _write_json(path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _packet(root, packet_id: str, family: str = "phasewrap", template: str = "two_ry_product_state_z_readout_v1") -> dict[str, object]:
    path = root / f"{packet_id}.json"
    payload = {
        "packet_id": packet_id,
        "provider": "ibm_runtime",
        "source_lane_id": "lane_a",
        "encoding_family": family,
        "fixed_width": {"circuit_template": template},
        "rows": [
            {"row_id": "row0", "ideal_predictions": {"score": 1.0}},
            {"row_id": "row1", "ideal_predictions": {"score": 0.0}},
        ],
    }
    _write_json(path, payload)
    return {"path": path, "payload": payload}


def test_score_reconstruction_for_product_and_cx_counts() -> None:
    assert expectation_from_counts({"00": 10}, "z0") == 1.0
    assert expectation_from_counts({"11": 10}, "z0z1") == 1.0
    assert score_from_counts({"00": 10}, "two_ry_product_state_z_readout_v1") == 1.0
    assert score_from_counts({"01": 10}, "two_ry_cx_parity_z_readout_v1") == 0.5


def test_packet_metrics_compute_error_and_rank() -> None:
    packet = _packet_payload("phasewrap")
    execution = {
        "raw_counts_by_row": [
            {"row_id": "row0", "counts": {"00": 10}},
            {"row_id": "row1", "counts": {"11": 10}},
        ]
    }

    metrics = packet_metrics(packet, execution)

    assert metrics["coverage_fraction"] == 1.0
    assert metrics["mean_absolute_score_error"] == 0.0
    assert metrics["spearman_rank_correlation"] == 1.0
    assert metrics["top1_match"] is True


def test_stage103_preregisters_metrics_and_blocks_without_counts(tmp_path) -> None:
    packet = _packet(tmp_path, "lane_a__phasewrap")
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(packet["path"])]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage102.json", {"decision": "CALIBRATION_EXECUTION_TEMPLATES_PREPARED_COUNTS_STILL_REQUIRED"})

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"
    assert result["packet_count"] == 1
    assert result["metric_record_count"] == 0
    assert result["missing_execution_count"] == 1


def test_stage103_computes_metrics_with_synthetic_counts_after_calibration(tmp_path) -> None:
    phasewrap = _packet(tmp_path, "lane_a__phasewrap", "phasewrap")
    rope = _packet(tmp_path, "lane_a__rope_like", "rope_like")
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(phasewrap["path"]), str(rope["path"])]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": True})
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    _write_json(tmp_path / "exec/lane_a__phasewrap.json", {"raw_counts_by_row": [{"row_id": "row0", "counts": {"00": 10}}, {"row_id": "row1", "counts": {"11": 10}}]})
    _write_json(tmp_path / "exec/lane_a__rope_like.json", {"raw_counts_by_row": [{"row_id": "row0", "counts": {"11": 10}}, {"row_id": "row1", "counts": {"00": 10}}]})

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
        execution_dir=tmp_path / "exec",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_READY_FOR_INTERPRETATION"
    assert result["metric_record_count"] == 2
    phasewrap_record = next(record for record in result["metric_records"] if record["encoding_family"] == "phasewrap")
    assert phasewrap_record["mean_absolute_score_error"] == 0.0


def test_stage103_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path / "stage99.json", {"packet_paths": []})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
    )

    paths = write_stage103_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage103_robustness_metric_preregistration"
    assert "mean_absolute_score_error" in summary


def _packet_payload(family: str) -> dict[str, object]:
    return {
        "packet_id": f"lane_a__{family}",
        "provider": "ibm_runtime",
        "source_lane_id": "lane_a",
        "encoding_family": family,
        "fixed_width": {"circuit_template": "two_ry_product_state_z_readout_v1"},
        "rows": [
            {"row_id": "row0", "ideal_predictions": {"score": 1.0}},
            {"row_id": "row1", "ideal_predictions": {"score": 0.0}},
        ],
    }
