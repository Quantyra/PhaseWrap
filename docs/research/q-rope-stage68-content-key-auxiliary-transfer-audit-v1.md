# PhaseWrap-RoPE Stage 68 Content-Key Auxiliary Transfer Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 68 tests whether the Stage 67 content-key retrieval success transfers back to the original Stage 10 retrieval blocker.

For each original task and seed, the audit trains the Stage 64 two-block learned pointer-generator on:

- the original same-seed Stage 10 train rows for that task;
- plus same-seed Stage 67 `content_key_retrieval` auxiliary train rows.

Validation and test rows are unchanged original Stage 10 rows. The audit keeps the fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparison and evaluates whether auxiliary visible content-key training helps original phase-cued or exact-offset held-out retrieval.

## Reviewer Command

```bash
python scripts/run_stage68_content_key_auxiliary_transfer_audit.py
```

This writes:

- `logs/automated_stage_gates/stage68_content_key_auxiliary_transfer_audit/manifest.json`
- `logs/automated_stage_gates/stage68_content_key_auxiliary_transfer_audit/results.json`
- `logs/automated_stage_gates/stage68_content_key_auxiliary_transfer_audit/summary.csv`
- `logs/automated_stage_gates/stage68_content_key_auxiliary_transfer_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage68_content_key_auxiliary_transfer_audit/failed_runs.json`

## Result

Stage 68 records `CONTENT_KEY_AUXILIARY_TRANSFER_WITHOUT_RETRIEVAL_GENERALIZATION`.

| Task | Best train method | Best train top-1 | Best test method | Best test top-1 |
| --- | --- | ---: | --- | ---: |
| `phase_cued_retrieval` | `sinusoidal` | 1.000000 | `alibi` | 0.016667 |
| `exact_offset_passkey` | `sinusoidal` | 0.966667 | `sinusoidal` | 0.033333 |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | `sinusoidal` | 0.566667 |

No runs failed.

## Interpretation

Stage 68 is negative evidence for transfer from content-key solvability to the original retrieval gate.

The result preserves the Stage 67 positive: the current harness can learn a standard visible content-key retrieval row design. But adding that auxiliary signal to original-task training does not repair held-out phase-cued or exact-offset retrieval. The best original retrieval top-1 remains far below the `0.500000` generalization threshold.

This tightens the current boundary: Stage 67 is harness/data-design evidence, not a bridge into original-row generalization and not PhaseWrap-specific promotion evidence.

## Claim Boundary

Supported:

- evidence that content-key auxiliary training preserves original-task train capacity in the two-block pointer-generator path;
- evidence that content-key auxiliary training does not transfer into original held-out retrieval generalization;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that content-key auxiliary success is equivalent to solving the original phase-cued/exact-offset gate;
- a claim that Stage 68 is positional-method promotion evidence.
