from __future__ import annotations

import json

from qrope.stage106_hardware_execution_preflight import run_stage106_preflight, write_stage106_outputs


def _write_stage105(path) -> None:
    path.write_text(
        json.dumps(
            {
                "decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED",
                "providers": ["amazon_braket", "ibm_runtime"],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def test_stage106_blocks_when_configuration_is_missing(tmp_path) -> None:
    stage105 = tmp_path / "stage105.json"
    _write_stage105(stage105)

    result = run_stage106_preflight(stage105_manifest_path=stage105, env={})

    assert result["decision"] == "HARDWARE_EXECUTION_PREFLIGHT_BLOCKED_CONFIGURATION_REQUIRED"
    assert result["ready_for_hardware_submission"] is False
    assert len(result["provider_records"]) == 2
    assert "provider_credentials_missing" in result["provider_records"][0]["blockers"]
    assert result["secret_values_recorded"] is False


def test_stage106_ready_when_required_env_is_present(tmp_path) -> None:
    stage105 = tmp_path / "stage105.json"
    _write_stage105(stage105)
    env = {
        "AWS_PROFILE": "profile",
        "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-east-1::device/qpu/test",
        "QROPE_BRAKET_OUTPUT_S3_BUCKET": "bucket",
        "QROPE_BRAKET_AWS_REGION": "us-east-1",
        "IBM_QUANTUM_TOKEN": "secret",
        "QROPE_IBM_BACKEND": "ibm_backend",
        "IBM_QUANTUM_INSTANCE_CRN": "crn",
        "QROPE_HARDWARE_BUDGET_USD_CAP": "100",
        "QROPE_HARDWARE_QUEUE_DEPTH_CAP": "5",
    }

    result = run_stage106_preflight(stage105_manifest_path=stage105, env=env)

    assert result["decision"] == "HARDWARE_EXECUTION_PREFLIGHT_READY_NO_SUBMISSION"
    assert result["ready_for_hardware_submission"] is True
    assert all(record["status"] == "ready" for record in result["provider_records"])
    assert result["provider_records"][0]["credential_env_present"]


def test_stage106_reports_missing_stage105_source(tmp_path) -> None:
    result = run_stage106_preflight(stage105_manifest_path=tmp_path / "missing.json", env={})

    assert result["status"] == "incomplete"
    assert result["missing_source_artifacts"]
    assert result["providers"] == []


def test_stage106_outputs_are_written(tmp_path) -> None:
    stage105 = tmp_path / "stage105.json"
    _write_stage105(stage105)
    result = run_stage106_preflight(stage105_manifest_path=stage105, env={})

    paths = write_stage106_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage106_hardware_execution_preflight"
    assert "amazon_braket" in summary
