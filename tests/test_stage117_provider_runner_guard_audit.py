from __future__ import annotations

import json

from qrope.stage117_provider_runner_guard_audit import run_stage117_audit, write_stage117_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_stage117_reports_missing_stage116_source(tmp_path) -> None:
    result = run_stage117_audit(stage116_results_path=tmp_path / "missing.json")

    assert result["status"] == "incomplete"
    assert result["decision"] == "PROVIDER_RUNNER_GUARDS_INCOMPLETE"
    assert result["missing_source_artifacts"]


def test_stage117_accepts_existing_blocked_runner_script(tmp_path) -> None:
    script = tmp_path / "runner.py"
    script.write_text("print('guarded')\n", encoding="utf-8")
    _write_json(
        tmp_path / "stage116.json",
        {
            "decision": "PROVIDER_RUNNER_PLAN_PREPARED_EXECUTION_BLOCKED",
            "runner_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "status": "blocked",
                    "runner_command": f"python {script.as_posix()} --job-shard jobs.jsonl --provider-results results.jsonl",
                }
            ],
        },
    )

    result = run_stage117_audit(stage116_results_path=tmp_path / "stage116.json")

    assert result["decision"] == "PROVIDER_RUNNER_GUARDS_PREPARED_EXECUTION_BLOCKED"
    assert result["guarded_runner_count"] == 1


def test_stage117_blocks_missing_or_unblocked_runner(tmp_path) -> None:
    _write_json(
        tmp_path / "stage116.json",
        {
            "runner_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "status": "ready_to_run",
                    "runner_command": "python missing.py --job-shard jobs.jsonl --provider-results results.jsonl",
                }
            ]
        },
    )

    result = run_stage117_audit(stage116_results_path=tmp_path / "stage116.json")

    assert result["decision"] == "PROVIDER_RUNNER_GUARDS_INCOMPLETE"
    assert "runner_script_missing" in result["runner_records"][0]["missing_evidence"]
    assert "stage116_runner_not_blocked" in result["runner_records"][0]["missing_evidence"]


def test_stage117_outputs_are_written(tmp_path) -> None:
    script = tmp_path / "runner.py"
    script.write_text("print('guarded')\n", encoding="utf-8")
    _write_json(
        tmp_path / "stage116.json",
        {"runner_records": [{"provider": "ibm_runtime", "window_id": "window_0", "status": "blocked", "runner_command": f"python {script.as_posix()}"}]},
    )
    result = run_stage117_audit(stage116_results_path=tmp_path / "stage116.json")

    paths = write_stage117_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["runner_count"] == 1
    assert "window_0" in summary
