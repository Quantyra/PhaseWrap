from __future__ import annotations

import json

from qrope.stage178_ibm_coherent_offset_sensitivity import (
    run_stage178_ibm_coherent_offset_sensitivity,
    write_stage178_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage177 = tmp_path / "stage177.json"
    stage169 = tmp_path / "stage169.json"
    _write_json(
        stage177,
        {
            "decision": "IBM_BACKEND_INFORMED_SIM_DOES_NOT_SUPPORT_TARGETED_HARDWARE_RUN_YET",
            "noise_models": [
                {
                    "noise_model_id": "ibm_backend_median_stochastic",
                    "noise_family": "ibm_backend_properties_stochastic",
                    "readout_bitflip_probability": 0.0,
                    "depolarizing_observable_shrink": 0.0,
                    "ry_angle_scale_error": 0.0,
                    "ry_angle_offset_radians": 0.0,
                    "observable_bias_component_a": 0.0,
                    "observable_bias_component_b": 0.0,
                }
            ],
        },
    )
    _write_json(
        stage169,
        {
            "decision": "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES",
            "stable_target_lanes": ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"],
        },
    )
    return stage177, stage169


def _packet(path, lane_id: str, family: str, circuit_template: str, component_a: float, component_b: float) -> None:
    score = 0.5 + 0.25 * (component_a + component_b)
    _write_json(
        path,
        {
            "packet_id": f"{lane_id}__{family}",
            "provider": "ibm_runtime",
            "source_lane_id": lane_id,
            "encoding_family": family,
            "shot_count": 4096,
            "fixed_width": {"circuit_template": circuit_template},
            "rows": [
                {
                    "row_id": "row_0",
                    "components": {"component_a": component_a, "component_b": component_b},
                    "ideal_predictions": {"score": score},
                }
            ],
        },
    )


def _manifests(tmp_path, *, phasewrap_components=(1.0, 1.0)):
    packet_dir = tmp_path / "packets"
    packet_paths = []
    lanes = {
        "ibm_product_seed314_rows16_shots4096": "two_ry_product_state_z_readout_v1",
        "ibm_cx_seed314_rows16_shots4096": "two_ry_cx_parity_z_readout_v1",
    }
    specs = {
        "phasewrap": phasewrap_components,
        "rope_like": (0.0, 0.0),
        "sinusoidal_like": (0.1, 0.1),
        "alibi_like": (0.2, 0.2),
        "no_position_control": (0.0, 0.0),
    }
    for lane_id, template in lanes.items():
        for family, components in specs.items():
            path = packet_dir / f"{lane_id}__{family}.json"
            _packet(path, lane_id, family, template, *components)
            packet_paths.append(str(path.as_posix()))
    stage99 = tmp_path / "stage99.json"
    stage100 = tmp_path / "stage100.json"
    _write_json(stage99, {"packet_paths": packet_paths[:5]})
    _write_json(stage100, {"packet_paths": packet_paths[5:]})
    return stage99, stage100


def test_stage178_finds_signed_offset_region_for_calibration_probe(tmp_path) -> None:
    stage177, stage169 = _sources(tmp_path)
    stage99, stage100 = _manifests(tmp_path)

    result = run_stage178_ibm_coherent_offset_sensitivity(
        stage177_results_path=stage177,
        stage169_results_path=stage169,
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
        signed_offsets=(0.02,),
    )

    assert result["decision"] == "IBM_COHERENT_OFFSET_SENSITIVITY_FINDS_SIGNED_REGION_CALIBRATION_PROBE_RECOMMENDED"
    assert result["stable_offset_count"] == 1
    assert result["stable_offsets"][0]["stable_template_count"] == 2
    assert result["no_hardware_submission"] is True


def test_stage178_blocks_when_stage177_is_not_at_no_go_boundary(tmp_path) -> None:
    stage177, stage169 = _sources(tmp_path)
    stage99, stage100 = _manifests(tmp_path)
    _write_json(stage177, {"decision": "IBM_BACKEND_INFORMED_SIM_SUPPORTS_TARGETED_HARDWARE_RUN", "noise_models": []})

    result = run_stage178_ibm_coherent_offset_sensitivity(
        stage177_results_path=stage177,
        stage169_results_path=stage169,
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
    )

    assert result["decision"] == "IBM_COHERENT_OFFSET_SENSITIVITY_INCOMPLETE"
    assert "stage177_not_at_backend_informed_no_go_boundary" in result["blockers"]


def test_stage178_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage177, stage169 = _sources(tmp_path)
    stage99, stage100 = _manifests(tmp_path)
    result = run_stage178_ibm_coherent_offset_sensitivity(
        stage177_results_path=stage177,
        stage169_results_path=stage169,
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
        signed_offsets=(0.02,),
    )

    paths = write_stage178_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
