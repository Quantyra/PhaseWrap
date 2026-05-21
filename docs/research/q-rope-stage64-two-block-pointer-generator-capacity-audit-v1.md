# PhaseWrap-RoPE Stage 64 Two-Block Pointer-Generator Capacity Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 64 tests whether the Stage 63 copy-output capacity repair survives a learned output mixture.

It keeps the support-complete Stage 61-63 row setup and the fair method set:

- RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons;
- all five default seeds;
- `examples_per_length = 6`;
- `80` training epochs;
- two learned q/k/v/o attention blocks;
- no lookup output and no fallback cue decoder.

The change from Stage 63 is the output path: Stage 64 uses a learned mixture of full-vocab softmax generation and copied prefix-token mass, controlled by a learned copy/vocab gate.

## Reviewer Command

```bash
python scripts/run_stage64_two_block_pointer_generator_capacity_audit.py
```

This writes:

- `logs/automated_stage_gates/stage64_two_block_pointer_generator_capacity_audit/manifest.json`
- `logs/automated_stage_gates/stage64_two_block_pointer_generator_capacity_audit/results.json`
- `logs/automated_stage_gates/stage64_two_block_pointer_generator_capacity_audit/summary.csv`
- `logs/automated_stage_gates/stage64_two_block_pointer_generator_capacity_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage64_two_block_pointer_generator_capacity_audit/failed_runs.json`

## Result

Stage 64 records `TWO_BLOCK_POINTER_GENERATOR_CAPACITY_WITHOUT_RETRIEVAL_GENERALIZATION`.

The learned copy/vocab mixture establishes train capacity: the best train top-1 is `1.000000`, above the `0.750000` threshold. It does not establish retrieval generalization: phase-cued retrieval reaches only `0.016667` best held-out top-1, and exact-offset passkey reaches only `0.050000`.

| Task | Best train method | Best train top-1 | Best test method | Best test top-1 |
| --- | --- | ---: | --- | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | `sinusoidal` | 0.583334 |
| `phase_cued_retrieval` | `sinusoidal` | 1.000000 | `phasewrap_adapter` / `rope_relative` / `phasewrap_bias` | 0.016667 |
| `exact_offset_passkey` | `sinusoidal` / `rope_relative` | 1.000000 | `rope_relative` | 0.050000 |

No runs failed.

The learned copy gate is high on retrieval rows, around `0.95`, so the model mostly preserves the Stage 63 copied-prefix output path.

## Interpretation

Stage 64 strengthens the output-path diagnosis. Stage 62 showed that longer vocab-softmax training still missed capacity. Stage 63 showed copied-prefix output can establish capacity but not retrieval generalization. Stage 64 shows that a learned copy/vocab mixture can also establish capacity, but it still does not make retrieval generalize.

This is positive evidence for the capacity repair and negative evidence for positional-method promotion. PhaseWrap-derived methods share the weak best phase-cued held-out top-1, but the absolute result remains far below threshold and RoPE-relative remains best on exact-offset passkey.

## Claim Boundary

Supported:

- evidence that learned pointer-generation preserves the copy-output capacity repair;
- evidence that capacity repair still does not establish held-out retrieval generalization;
- evidence that the output path, not support coverage alone, was an immediate Stage 62 bottleneck;
- fair reporting across RoPE/ALiBI/sinusoidal/no-position/PhaseWrap variants;
- failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that learned pointer-generation is full decoder-only language-model validation;
- a claim that Stage 64 is positional-method promotion evidence.
