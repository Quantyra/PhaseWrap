from __future__ import annotations

import hashlib
import json

from qrope.stage173_locked_result_ingestion_contract_audit import run_stage173_locked_ingestion_audit, write_stage173_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sources(tmp_path):
    root = tmp_path / "stage114"
    shard = root / "job_shards" / "ibm_runtime" / "ibm_runtime__independent_window_00" / "jobs.jsonl"
    stub = root / "result_stubs" / "ibm_runtime" / "ibm_runtime__independent_window_00" / "provider_job_results.stub.jsonl"
    result_path = root / "provider_results" / "ibm_runtime" / "ibm_runtime__independent_window_00" / "provider_job_results.jsonl"
    jobs = [
        {
            "job_id": "job_cal",
            "job_kind": "known_state_calibration",
            "openqasm3": "OPENQASM 3.0;",
            "provider": "ibm_runtime",
            "shots": 1000,
            "state": "00",
            "target_counts_container": "raw_counts_by_state",
            "target_counts_key": "00",
            "target_evidence_path": "calibration.json",
            "template_path": "template.json",
            "window_id": "ibm_runtime__independent_window_00",
        },
        {
            "circuit_template": "two_ry_product_state_z_readout_v1",
            "encoding_family": "phasewrap",
            "job_id": "job_packet",
            "job_kind": "matched_packet_row",
            "openqasm3": "OPENQASM 3.0;",
            "packet_id": "packet__phasewrap",
            "provider": "ibm_runtime",
            "row_id": "hwrow-000",
            "shots": 4096,
            "source_lane_id": "ibm_product_seed314_rows16_shots4096",
            "target_counts_container": "raw_counts_by_row",
            "target_counts_key": "hwrow-000",
            "target_evidence_path": "packet.json",
            "template_path": "template.json",
            "window_id": "ibm_runtime__independent_window_00",
        },
    ]
    stubs = [
        {
            "job_id": job["job_id"],
            "job_or_task_id": "",
            "backend_metadata": {"provider": "ibm_runtime"},
            "submitted_at_utc": "",
            "completed_at_utc": "",
            "counts": {},
        }
        for job in jobs
    ]
    _write_jsonl(shard, jobs)
    _write_jsonl(stub, stubs)
    manifest = tmp_path / "stage114_manifest.json"
    schema = tmp_path / "stage114_schema.json"
    stage163 = tmp_path / "stage163.json"
    stage172 = tmp_path / "stage172.json"
    _write_json(
        manifest,
        {
            "decision": "PROVIDER_RESULT_CAPTURE_CONTRACT_PREPARED_RESULTS_REQUIRED",
            "result_stub_paths": [stub.as_posix()],
        },
    )
    _write_json(
        schema,
        {
            "required_fields": ["job_id", "job_or_task_id", "backend_metadata", "submitted_at_utc", "completed_at_utc", "counts"],
        },
    )
    _write_json(
        stage163,
        {
            "decision": "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL",
            "window_locks": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "ibm_runtime__independent_window_00",
                    "job_count": 2,
                    "total_shots": 5096,
                    "job_shard_path": shard.as_posix(),
                    "job_shard_sha256": _sha256(shard),
                    "provider_results_path": result_path.as_posix(),
                }
            ],
        },
    )
    _write_json(stage172, {"decision": "OBJECTIVE_EVIDENCE_GAP_AUDIT_HARDWARE_RESULTS_REQUIRED"})
    return manifest, schema, stage163, stage172


def test_stage173_validates_locked_job_shards_and_stubs(tmp_path) -> None:
    manifest, schema, stage163, stage172 = _sources(tmp_path)

    result = run_stage173_locked_ingestion_audit(
        stage114_manifest_path=manifest,
        stage114_schema_path=schema,
        stage163_results_path=stage163,
        stage172_results_path=stage172,
    )

    assert result["decision"] == "LOCKED_RESULT_INGESTION_CONTRACT_READY_AWAITING_PROVIDER_RESULTS"
    assert result["ready_window_count"] == 1
    assert result["locked_job_count"] == 2
    assert result["locked_total_shots"] == 5096
    assert result["blockers"] == []


def test_stage173_blocks_when_stub_ids_do_not_match(tmp_path) -> None:
    manifest, schema, stage163, stage172 = _sources(tmp_path)
    stub = tmp_path / "stage114" / "result_stubs" / "ibm_runtime" / "ibm_runtime__independent_window_00" / "provider_job_results.stub.jsonl"
    records = [json.loads(line) for line in stub.read_text(encoding="utf-8").splitlines()]
    records[0]["job_id"] = "wrong"
    _write_jsonl(stub, records)

    result = run_stage173_locked_ingestion_audit(
        stage114_manifest_path=manifest,
        stage114_schema_path=schema,
        stage163_results_path=stage163,
        stage172_results_path=stage172,
    )

    assert result["decision"] == "LOCKED_RESULT_INGESTION_CONTRACT_AUDIT_BLOCKED"
    assert "locked_window_ingestion_contract_not_ready" in result["blockers"]
    assert "result_stub_job_ids_do_not_match_job_shard" in result["window_records"][0]["blockers"]


def test_stage173_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    manifest, schema, stage163, stage172 = _sources(tmp_path)
    result = run_stage173_locked_ingestion_audit(
        stage114_manifest_path=manifest,
        stage114_schema_path=schema,
        stage163_results_path=stage163,
        stage172_results_path=stage172,
    )

    paths = write_stage173_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
