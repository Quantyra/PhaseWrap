# PhaseWrap Stage 57 Support-Aware Query-Cue Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 57 tests whether Stage 56's visible-token cue failure is caused by missing signal or by failure to decode the known query-token support. It uses:

- the visible query token's encoded `reference_delta mod 16`;
- the known generator support `5, 7, 8, 11, 12, 16, 19` to decode the full reference delta;
- copied prefix-token output.

It does not use `row.reference_delta`, `row.target_delta`, or `row.target_pos` directly.

This is still a deterministic cue-copy diagnostic. The known support prior is not a learned decoder-only transformer capability and is not positional-method promotion evidence.

## Reviewer Command

```bash
python scripts/run_stage57_support_aware_query_cue_audit.py
```

This writes:

- `logs/automated_stage_gates/stage57_support_aware_query_cue_audit/manifest.json`
- `logs/automated_stage_gates/stage57_support_aware_query_cue_audit/results.json`
- `logs/automated_stage_gates/stage57_support_aware_query_cue_audit/summary.csv`
- `logs/automated_stage_gates/stage57_support_aware_query_cue_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage57_support_aware_query_cue_audit/failed_runs.json`

## Result

Stage 57 records `SUPPORT_AWARE_QUERY_CUE_SOLVES_PHASE_CUED_NOT_PROMOTION`.

| Task | Best method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `rope_relative` | 1.000000 | 1.000000 |
| `phase_cued_retrieval` | `rope_relative` | 0.900000 | 0.471171 |
| `exact_offset_passkey` | `rope_relative` | 0.800000 | 0.401723 |

The phase-cued repair is not method-specific:

| Task | Method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `phase_cued_retrieval` | `no_position` | 0.900000 | 0.471171 |
| `phase_cued_retrieval` | `phasewrap_bias` | 0.900000 | 0.471171 |
| `phase_cued_retrieval` | `phasewrap_adapter` | 0.900000 | 0.471171 |

No runs failed.

## Interpretation

Stage 57 shows the phase-cued retrieval signal is present in the visible query token when the known reference-delta support is supplied as a prior. That separates Stage 56's failure from pure input invisibility.

It does not support a PhaseWrap positional-method claim. The same support-aware cue-copy path solves phase-cued retrieval for `no_position`, and the result depends on a deterministic support prior plus copied output rather than a learned decoder-only transformer.

## Claim Boundary

Supported:

- evidence separating missing cue signal from support-prior cue decoding;
- fair method reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap replaces RoPE;
- a claim that the known reference-delta support prior is a standard decoder-only transformer capability;
- a claim that this deterministic cue-copy diagnostic is positional-method promotion evidence.
