# PhaseWrap Stage 71 Positional-Bias Copy Upper-Bound Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 71 tests whether the original Stage 10 retrieval rows are reachable if each method is given a deterministic copy upper bound: select the prefix position with the method's own positional-bias argmax, then copy that prefix token as the answer.

This is not a learned decoder. It is a no-training diagnostic that separates positional-source identifiability from learned attention and output optimization.

## Reviewer Command

```bash
python scripts/run_stage71_positional_bias_copy_upper_bound_audit.py
```

This writes:

- `logs/automated_stage_gates/stage71_positional_bias_copy_upper_bound_audit/manifest.json`
- `logs/automated_stage_gates/stage71_positional_bias_copy_upper_bound_audit/results.json`
- `logs/automated_stage_gates/stage71_positional_bias_copy_upper_bound_audit/summary.csv`
- `logs/automated_stage_gates/stage71_positional_bias_copy_upper_bound_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage71_positional_bias_copy_upper_bound_audit/per_example_results.csv`
- `logs/automated_stage_gates/stage71_positional_bias_copy_upper_bound_audit/failed_runs.json`

## Result

Stage 71 records `POSITIONAL_BIAS_COPY_PARTIAL_ORIGINAL_RETRIEVAL_UPPER_BOUND`.

| Task | Best method | Best held-out top-1 | Interpretation |
| --- | --- | ---: | --- |
| `phase_cued_retrieval` | `rope_relative` | 0.016667 | The hard positional-bias copy upper bound does not solve phase-cued retrieval. |
| `exact_offset_passkey` | `rope_relative` | 1.000000 | RoPE-relative bias can directly identify the exact-offset copy source. |
| `tiny_text_fact_qa` | `rope_relative` | 1.000000 | The query/fact layout is reachable by this deterministic copy rule for RoPE-relative. |

No runs failed.

## Interpretation

Stage 71 strengthens the negative boundary around the original phase-cued retrieval blocker.

The result shows that the exact-offset lane is reachable under a simple positional-copy upper bound, led by `rope_relative`, but the phase-cued lane remains below threshold even before learned decoder optimization is introduced. That means the current original phase-cued failure is not only a learned output-path problem.

This does not promote RoPE either: deterministic argmax copy is not standard decoder-only transformer behavior. It is a diagnostic upper bound that helps locate the blocker.

## Claim Boundary

Supported:

- evidence that direct positional-bias copy solves exact-offset passkey for `rope_relative`;
- evidence that direct positional-bias copy does not solve the phase-cued original retrieval lane;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants on unchanged original rows.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap replaces RoPE;
- a claim that deterministic argmax copy is learned decoder-only transformer behavior;
- a claim that this upper bound is positional-method promotion evidence by itself.

## Next Gate

The next gate should focus specifically on why phase-cued original retrieval is not reachable under hard positional-bias copy, then test a matched mechanism that improves phase-cued and exact-offset held-out retrieval without exposing row metadata or lookup fallback.
