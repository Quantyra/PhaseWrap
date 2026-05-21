# PhaseWrap-RoPE Stage 58 Pooled-Train Query Support Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 58 tests whether the known support prior used by Stage 57 can be recovered from training rows instead of supplied as a fixed list. It learns a pooled train lookup from visible query-token `reference_delta mod 16` to the corresponding phase-cued `reference_delta`, then evaluates the same deterministic cue-copy readout.

This is not a matched decoder-only transformer. It is a diagnostic lookup learned from the pooled train split.

## Reviewer Command

```bash
python scripts/run_stage58_pooled_train_query_support_audit.py
```

This writes:

- `logs/automated_stage_gates/stage58_pooled_train_query_support_audit/manifest.json`
- `logs/automated_stage_gates/stage58_pooled_train_query_support_audit/results.json`
- `logs/automated_stage_gates/stage58_pooled_train_query_support_audit/summary.csv`
- `logs/automated_stage_gates/stage58_pooled_train_query_support_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage58_pooled_train_query_support_audit/failed_runs.json`

## Result

Stage 58 records `POOLED_TRAIN_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION`.

| Task | Best method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `rope_relative` | 1.000000 | 1.000000 |
| `phase_cued_retrieval` | `rope_relative` | 0.900000 | 0.471171 |
| `exact_offset_passkey` | `rope_relative` | 0.800000 | 0.401723 |

The learned pooled lookup is:

```json
{"0": 16, "3": 19, "5": 5, "7": 7, "8": 8, "11": 11, "12": 12}
```

`no_position` also solves phase-cued retrieval under this lookup. No runs failed.

## Interpretation

Stage 58 shows the known support prior from Stage 57 can be recovered from pooled train rows as a simple query-token lookup. This narrows the blocker: the phase-cued signal is visible and train-recoverable in this synthetic row family.

It still does not support a PhaseWrap positional-method claim. The repair is a deterministic pooled lookup plus copy output, not a matched learned decoder-only transformer, and `no_position` solves the phase-cued lane under the same lookup.

## Claim Boundary

Supported:

- evidence about whether Stage 57's support prior can be recovered from train rows;
- fair method reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that a pooled lookup map is a matched decoder-only transformer;
- a claim that this deterministic cue-copy diagnostic is positional-method promotion evidence.
