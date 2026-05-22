from __future__ import annotations

import json

from qrope.stage104_matched_packet_execution_package import (
    build_packet_execution_template,
    run_stage104_package,
    write_stage104_outputs,
)


def _write_json(path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _packet(path, packet_id: str, template: str = "two_ry_product_state_z_readout_v1") -> None:
    payload = {
        "packet_id": packet_id,
        "packet_hash": f"{packet_id}-hash",
        "source_lane_id": "lane_a",
        "provider": "ibm_runtime",
        "backend": "BACKEND",
        "encoding_family": "phasewrap",
        "shot_count": 128,
        "fixed_width": {"circuit_template": template},
        "rows": [
            {
                "row_id": "row0",
                "circuit_parameters": {"ry_q0": 0.0, "ry_q1": 1.0},
                "ideal_predictions": {"score": 0.75},
            }
        ],
    }
    _write_json(path, payload)


def test_build_packet_execution_template_includes_rows_and_programs(tmp_path) -> None:
    packet_path = tmp_path / "packet.json"
    _packet(packet_path, "packet")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))

    template = build_packet_execution_template(packet)

    assert template["packet_id"] == "packet"
    assert template["raw_counts_by_row"][0]["row_id"] == "row0"
    assert "ry(0.0) q[0];" in template["raw_counts_by_row"][0]["openqasm3"]
    assert template["raw_counts_by_row"][0]["counts"] == {}
    assert template["required_execution_fields"] == [
        "job_or_task_ids",
        "backend_metadata",
        "submitted_at_utc",
        "completed_at_utc",
        "raw_counts_by_row",
    ]


def test_stage104_prepares_template_for_each_matched_packet(tmp_path) -> None:
    packet_a = tmp_path / "packet_a.json"
    packet_b = tmp_path / "packet_b.json"
    _packet(packet_a, "packet_a")
    _packet(packet_b, "packet_b", template="two_ry_cx_parity_z_readout_v1")
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(packet_a)]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": [str(packet_b)]})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})

    result = run_stage104_package(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
    )

    assert result["status"] == "incomplete"
    assert result["template_count"] == 2
    assert result["stage101_known_state_calibration_pass"] is False
    assert "raw_counts_by_row" in result["evidence_records"][0]["missing_evidence"]


def test_stage104_marks_complete_for_twenty_packet_template_surface(tmp_path) -> None:
    paths = []
    for index in range(20):
        packet_path = tmp_path / f"packet_{index}.json"
        _packet(packet_path, f"packet_{index}")
        paths.append(str(packet_path))
    _write_json(tmp_path / "stage99.json", {"packet_paths": paths[:10]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": paths[10:]})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": True})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})

    result = run_stage104_package(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
    )

    assert result["status"] == "completed"
    assert result["decision"] == "MATCHED_PACKET_EXECUTION_TEMPLATES_PREPARED_CALIBRATION_AND_COUNTS_REQUIRED"
    assert result["template_count"] == 20


def test_stage104_outputs_are_written(tmp_path) -> None:
    paths = []
    for index in range(20):
        packet_path = tmp_path / f"packet_{index}.json"
        _packet(packet_path, f"packet_{index}")
        paths.append(str(packet_path))
    _write_json(tmp_path / "stage99.json", {"packet_paths": paths[:10]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": paths[10:]})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})
    result = run_stage104_package(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
    )

    paths_out = write_stage104_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    templates = sorted((tmp_path / "out" / "packet_execution_templates").glob("*.json"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths_out) == {"manifest", "result", "summary_csv", "template_dir"}
    assert manifest["template_count"] == 20
    assert len(templates) == 20
    assert "packet_0" in summary
