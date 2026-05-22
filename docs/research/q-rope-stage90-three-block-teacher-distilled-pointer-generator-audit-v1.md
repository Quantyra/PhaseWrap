# PhaseWrap-RoPE Stage 90 Three-Block Teacher-Distilled Pointer Generator Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 90 tests whether the Stage 89 free-retrieval failure is specific to the two-block learned decoder architecture.

It adds a third learned attention block to the pointer-generator decoder while preserving the same support-complete train rows, support auxiliary loss, target-attention auxiliary loss, and training-only Stage 88 structural teacher loss. Validation and test still use only the free learned pointer-generator distribution. No structural copy route, teacher distribution, support label, `target_pos`, `target_delta`, or `reference_delta` is available at evaluation.

## Reviewer Command

```bash
python scripts/run_stage90_three_block_teacher_distilled_pointer_generator_audit.py
```

This writes:

- `logs/automated_stage_gates/stage90_three_block_teacher_distilled_pointer_generator_audit/manifest.json`
- `logs/automated_stage_gates/stage90_three_block_teacher_distilled_pointer_generator_audit/results.json`
- `logs/automated_stage_gates/stage90_three_block_teacher_distilled_pointer_generator_audit/summary.csv`
- `logs/automated_stage_gates/stage90_three_block_teacher_distilled_pointer_generator_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage90_three_block_teacher_distilled_pointer_generator_audit/failed_runs.json`

## Result

Stage 90 records `THREE_BLOCK_TEACHER_DISTILLED_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION`.

Default run summary:

| task | best method | train top-1 | test top-1 | mean target probability |
| --- | --- | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `0.966667` | `0.866667` | `0.082555` |
| `phase_cued_retrieval` | `sinusoidal` | `0.883333` | `0.033333` | `0.029719` |
| `exact_offset_passkey` | `sinusoidal` | `1.000000` | `0.433333` | `0.058903` |

Additional decision fields:

- `generalization_top1_threshold`: `0.5`
- `generalized_original_retrieval_tasks`: `[]`
- `retrieval_attention_repaired_tasks`: `[]`
- `phase_cued_best_support_accuracy`: `0.850000`
- `failed_runs`: `[]`

## Interpretation

Stage 90 does not repair free held-out retrieval. The extra attention block improves exact-offset relative to Stage 89 but leaves it below threshold and worsens phase-cued retrieval.

This keeps the Stage 70 claim boundary unchanged: structural retrieval routes solve the row family, but the current learned decoder variants do not internalize that support-to-token binding under fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons.

## Claim Boundary

Supported:

- a no-credential support-complete three-block pointer-generator audit with training-only structural teacher distillation;
- evidence that adding a third learned attention block does not repair free held-out original retrieval under this training setup;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that a three-block toy pointer-generator is full transformer-scale validation;
- a claim that training-time structural teachers are positional-method promotion evidence;
- broad quantum advantage.

## Next Gate

The next useful gate should vary the row curriculum or support-token binding supervision rather than only increasing decoder depth, while preserving free evaluation and the fair method comparison.
