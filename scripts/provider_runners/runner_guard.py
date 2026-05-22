from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_STAGE111_RESULTS = Path("logs") / "automated_stage_gates" / "stage111_provider_sdk_backend_discovery" / "results.json"


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _provider_record(stage111: dict[str, Any] | None, provider: str) -> dict[str, Any] | None:
    if not stage111:
        return None
    for record in stage111.get("provider_records", []):
        if record.get("provider") == provider:
            return record
    return None


def run_guarded_provider_runner(provider: str, argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Guarded no-submit runner for {provider} Stage 112 jobs.")
    parser.add_argument("--job-shard", type=Path, required=True)
    parser.add_argument("--provider-results", type=Path, required=True)
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--allow-live-submit", action="store_true")
    args = parser.parse_args(argv)

    stage111 = _load_json(args.stage111_results)
    jobs = _load_jsonl(args.job_shard)
    record = _provider_record(stage111, provider)
    print(f"provider: {provider}")
    print(f"job_shard: {args.job_shard}")
    print(f"provider_results: {args.provider_results}")
    print(f"job_count: {len(jobs)}")
    if record is None:
        print("decision: PROVIDER_RUNNER_BLOCKED_STAGE111_RECORD_MISSING")
        return 2
    if record.get("status") != "ready":
        print("decision: PROVIDER_RUNNER_BLOCKED_STAGE111_NOT_READY")
        print(f"blockers: {', '.join(str(item) for item in record.get('blockers', []))}")
        return 2
    if not args.allow_live_submit:
        print("decision: PROVIDER_RUNNER_READY_LIVE_SUBMIT_FLAG_REQUIRED")
        return 3
    print("decision: PROVIDER_RUNNER_LIVE_SUBMISSION_NOT_IMPLEMENTED")
    return 4
