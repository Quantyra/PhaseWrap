from __future__ import annotations

import json

import pytest

from qrope.provider_adapters.amazon_braket import execute_submission_plans as execute_braket
from qrope.provider_adapters.common import ProviderAdapterBlocked
from qrope.provider_adapters.ibm_runtime import execute_submission_plans as execute_ibm
from qrope.stage127_injected_client_submitter_audit import run_stage127_audit, write_stage127_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


class FakeClient:
    def __init__(self, raw_result):
        self.raw_result = raw_result
        self.calls = []

    def run_openqasm3(self, plan):
        self.calls.append(plan)
        return {
            "job_or_task_id": "task_0",
            "backend_metadata": {"backend": "fake"},
            "raw_result": self.raw_result,
        }


def _plan(provider: str):
    return {
        "job_id": "job_0",
        "job_kind": "known_state_calibration",
        "openqasm3_sha256": "abc",
        "provider": provider,
        "provider_submission_kind": f"{provider}_submission",
        "target_counts_key": "00",
        "window_id": "window_0",
    }


def test_injected_client_execution_builds_stage114_records() -> None:
    ibm_client = FakeClient({"counts": {"00": 3, "11": 2}})
    braket_client = FakeClient({"measurementCounts": {"01": 4, "10": 6}})

    ibm_records = execute_ibm(
        plans=[_plan("ibm_runtime")],
        client=ibm_client,
        submitted_at_utc="2026-01-01T00:00:00Z",
        completed_at_utc="2026-01-01T00:00:01Z",
    )
    braket_records = execute_braket(
        plans=[_plan("amazon_braket")],
        client=braket_client,
        submitted_at_utc="2026-01-01T00:00:00Z",
        completed_at_utc="2026-01-01T00:00:01Z",
    )

    assert ibm_records[0]["counts"] == {"00": 3, "11": 2}
    assert braket_records[0]["counts"] == {"01": 4, "10": 6}
    assert ibm_client.calls and braket_client.calls


def test_injected_client_execution_rejects_missing_method() -> None:
    with pytest.raises(ProviderAdapterBlocked):
        execute_ibm(
            plans=[_plan("ibm_runtime")],
            client=object(),
            submitted_at_utc="2026-01-01T00:00:00Z",
            completed_at_utc="2026-01-01T00:00:01Z",
        )


def _fixture(tmp_path):
    stage123 = tmp_path / "stage123" / "results.json"
    stage126 = tmp_path / "stage126.json"
    ibm_plan = tmp_path / "stage123" / "submission_plans" / "ibm_runtime" / "window_0" / "submission_plans.jsonl"
    braket_plan = tmp_path / "stage123" / "submission_plans" / "amazon_braket" / "window_0" / "submission_plans.jsonl"
    _write_json(stage123, {"decision": "PROVIDER_SUBMISSION_PLANS_READY_EXECUTION_BLOCKED"})
    _write_json(stage126, {"decision": "STAGE114_RESULT_RECORD_BUILDER_READY_EXECUTION_BLOCKED"})
    _write_jsonl(ibm_plan, [_plan("ibm_runtime")])
    _write_jsonl(braket_plan, [_plan("amazon_braket")])
    return stage123, stage126


def test_stage127_reports_injected_client_path_ready(tmp_path) -> None:
    stage123, stage126 = _fixture(tmp_path)

    result = run_stage127_audit(stage123_results_path=stage123, stage126_results_path=stage126)

    assert result["decision"] == "INJECTED_CLIENT_SUBMITTER_PATH_READY_EXECUTION_BLOCKED"
    assert result["ready_provider_window_count"] == 2
    assert len(result["built_records"]) == 2


def test_stage127_outputs_are_written(tmp_path) -> None:
    stage123, stage126 = _fixture(tmp_path)
    result = run_stage127_audit(stage123_results_path=stage123, stage126_results_path=stage126)

    paths = write_stage127_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["ready_provider_window_count"] == 2
    assert "ibm_runtime" in summary
