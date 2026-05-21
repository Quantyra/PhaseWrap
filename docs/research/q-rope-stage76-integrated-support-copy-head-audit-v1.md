# PhaseWrap-RoPE Stage 76 Integrated Support Copy Head Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 76 tests whether the Stage 75 learned visible-cue recovery survives when it is optimized end-to-end through the copy-readout loss instead of trained as a standalone support classifier.

For each seed and method, the audit trains one compact support/copy head on that seed's original Stage 10 train rows. The model learns support weights and position/cue/distance scales from token-copy loss, then evaluates train, validation, and held-out test rows across RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants.

This is stricter than Stage 75, but it is still not a full matched decoder-only transformer.

## Reviewer Command

```bash
python scripts/run_stage76_integrated_support_copy_head_audit.py
```

This writes:

- `logs/automated_stage_gates/stage76_integrated_support_copy_head_audit/manifest.json`
- `logs/automated_stage_gates/stage76_integrated_support_copy_head_audit/results.json`
- `logs/automated_stage_gates/stage76_integrated_support_copy_head_audit/summary.csv`
- `logs/automated_stage_gates/stage76_integrated_support_copy_head_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage76_integrated_support_copy_head_audit/failed_runs.json`

## Result

Stage 76 records `INTEGRATED_SUPPORT_COPY_HEAD_PARTIAL_RETRIEVAL`.

| Task | Best method | Test top-1 | Test target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `rope_relative` | 1.000000 | 0.814079 |
| `phase_cued_retrieval` | `sinusoidal` | 0.000000 | 0.027769 |
| `exact_offset_passkey` | `rope_relative` | 0.600000 | 0.256630 |

Mean held-out phase-cued support accuracy is `0.000000`. No runs failed.

## Interpretation

Stage 76 is a negative result for the next promotion gate. Stage 75 showed that a standalone support head can learn the visible query cue across seeds, but Stage 76 shows that optimizing a compact integrated support/copy head through token-copy loss does not preserve phase-cued held-out retrieval.

The exact-offset lane remains partially repaired for `rope_relative`, and tiny text-fact QA remains easy for several methods. The original phase-cued blocker, however, returns to a hard failure under the integrated training objective.

This narrows the honest claim: visible-cue support is learnable in isolation, but current integrated copy-head training does not turn that cue into held-out phase-cued retrieval generalization.

## Claim Boundary

Supported:

- evidence that same-seed integrated support/copy training partially repairs exact-offset retrieval;
- evidence that integrated support/copy training does not preserve the Stage 75 phase-cued repair;
- fair reporting across RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that this compact copy-head is a matched decoder-only transformer;
- a claim that Stage 76 supports positional-method promotion.

## Next Gate

The next gate should either harden the integrated learned objective so phase-cued visible-cue recovery survives held-out evaluation, or move to a genuinely matched decoder-only architecture with explicit evidence that the recovery is learned inside the model.
