# PhaseWrap Stage 74 Leave-One-Seed Query Support Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 74 tests whether the original phase-cued row support can be recovered from other seeds' standard train rows, without using the held-out seed's train rows and without reading row metadata at evaluation time.

For each held-out seed, the audit learns a lookup from visible query-token `reference_delta mod 16` to the phase-cued `reference_delta` using only the other seeds' train rows. It then evaluates the same deterministic copy-readout family across RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants.

This is not a matched learned decoder-only transformer. It is a leave-one-seed visible-cue support diagnostic.

## Reviewer Command

```bash
python scripts/run_stage74_leave_one_seed_query_support_audit.py
```

This writes:

- `logs/automated_stage_gates/stage74_leave_one_seed_query_support_audit/manifest.json`
- `logs/automated_stage_gates/stage74_leave_one_seed_query_support_audit/results.json`
- `logs/automated_stage_gates/stage74_leave_one_seed_query_support_audit/summary.csv`
- `logs/automated_stage_gates/stage74_leave_one_seed_query_support_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage74_leave_one_seed_query_support_audit/failed_runs.json`

## Result

Stage 74 records `LEAVE_ONE_SEED_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION`.

| Task | Best method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `rope_relative` / `no_position` / `alibi` | 1.000000 | 1.000000 |
| `phase_cued_retrieval` | `rope_relative` / `phasewrap_bias` / `phasewrap_adapter` / `no_position` / `alibi` | 0.900000 | 0.471171 |
| `exact_offset_passkey` | `rope_relative` | 0.800000 | 0.401723 |

Mean held-out phase-cued test support coverage is `1.000000`. No runs failed.

## Interpretation

Stage 74 separates the row-family solvability question from the PhaseWrap fixed-score support failure in Stage 73. The original phase-cued support can be recovered from other seeds' visible query-token train rows, and that repair solves phase-cued retrieval for `no_position` too.

This is useful positive evidence that the phase-cued row family is not inherently unsolvable from standard inputs. It is also negative promotion evidence: the repair is a deterministic cross-seed lookup plus copy readout, not a matched learned decoder-only transformer and not a PhaseWrap-specific positional advantage.

## Claim Boundary

Supported:

- evidence that leave-one-seed visible query-support recovery solves phase-cued retrieval;
- evidence that the support map generalizes across seeds in this synthetic row family;
- fair reporting across RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap replaces RoPE;
- a claim that a leave-one-seed lookup is a matched decoder-only transformer;
- a claim that cross-seed query-support recovery is positional-method promotion evidence.

## Next Gate

The next gate should move this visible-cue recovery into a genuinely learned matched decoder-only mechanism, or explicitly keep it as a data-design/lookup upper bound while returning to stronger retrieval-targeted decoder evidence.
