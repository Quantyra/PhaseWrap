# QRoPE Stage 115 Provider Result Collector

Stage 115 validates and collects Stage 114 provider/window result shards into the single Stage 113 `provider_job_results.jsonl` input.

It checks each shard for:

- missing result files;
- missing job results;
- duplicate job IDs;
- unknown job IDs;
- missing required fields;
- empty or non-numeric counts.

By default Stage 115 only validates shard readiness. With `--write-stage113-input`, it concatenates complete validated shards into `logs/automated_stage_gates/stage113_job_result_evidence_assembler/provider_job_results.jsonl` only after Stage 152 reports the guarded first-provider live-execution path ready.

Current expected decision before provider execution:

`PROVIDER_RESULTS_COLLECTION_BLOCKED_RESULTS_MISSING`

This stage does not submit hardware jobs, record credentials, assemble evidence files, validate calibration, compute metrics, or support a noisy-hardware robustness claim.
