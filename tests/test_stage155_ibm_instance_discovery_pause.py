from __future__ import annotations

import json

from qrope.stage155_ibm_instance_discovery_pause import (
    run_stage155_ibm_instance_discovery_pause,
    write_stage155_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage154 = tmp_path / "stage154.json"
    stage140 = tmp_path / "stage140.json"
    _write_json(stage154, {"decision": "SIMULATED_NOISE_TARGETED_HARDWARE_FOLLOWUP_RECOMMENDED"})
    _write_json(stage140, {"decision": "LOCAL_PROVIDER_CONFIGURATION_BLOCKED_ENV_OR_SDK_REQUIRED"})
    return stage154, stage140


def test_stage155_records_single_discovered_instance_without_secret_values(tmp_path) -> None:
    stage154, stage140 = _sources(tmp_path)

    result = run_stage155_ibm_instance_discovery_pause(
        stage154_results_path=stage154,
        stage140_results_path=stage140,
        env={"IBM_QUANTUM_TOKEN": "token"},
        allow_live_discovery=True,
        discover_instances=lambda env: [
            {
                "name": "open-instance",
                "plan": "open",
                "region": "us-east",
                "crn": "crn:v1:example",
            }
        ],
    )

    assert result["decision"] == "IBM_INSTANCE_CRN_DISCOVERED_LOCAL_DOTENV_UPDATE_REQUIRED"
    assert result["discovered_instance_count"] == 1
    assert result["discovered_crn_count"] == 1
    assert result["secret_values_recorded"] is False
    assert result["discovered_instances"] == [
        {"name": "open-instance", "plan": "open", "region": "us-east", "crn_discovered": True}
    ]


def test_stage155_does_not_discover_without_explicit_live_discovery_flag(tmp_path) -> None:
    stage154, stage140 = _sources(tmp_path)

    result = run_stage155_ibm_instance_discovery_pause(
        stage154_results_path=stage154,
        stage140_results_path=stage140,
        env={"IBM_QUANTUM_TOKEN": "token"},
        allow_live_discovery=False,
        discover_instances=lambda env: [{"crn": "crn:v1:example"}],
    )

    assert result["decision"] == "IBM_INSTANCE_DISCOVERY_PAUSED_LIVE_DISCOVERY_NOT_REQUESTED"
    assert result["live_discovery_attempted"] is False
    assert result["discovered_instances"] == []


def test_stage155_outputs_are_written_without_crn(tmp_path) -> None:
    stage154, stage140 = _sources(tmp_path)
    result = run_stage155_ibm_instance_discovery_pause(
        stage154_results_path=stage154,
        stage140_results_path=stage140,
        env={"IBM_QUANTUM_TOKEN": "token"},
        allow_live_discovery=True,
        discover_instances=lambda env: [{"name": "open-instance", "plan": "open", "crn": "crn:v1:secret"}],
    )

    paths = write_stage155_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "crn:v1" not in written
    assert "crn:v1" not in summary
