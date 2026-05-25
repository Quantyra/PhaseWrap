# PhaseWrap Stage 52 Two-Block Decoder Feasibility Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 52 moves beyond the Stage 51 one-block/pointer-generator plateau by adding a stronger autograd-backed decoder feasibility harness. It keeps the Stage 45-51 row family and fair positional method set, but replaces the single attention block with two sequential attention blocks and residual query updates.

The audited method set remains:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

This is a one-seed feasibility audit, not promotion evidence. Its purpose is to test whether a stronger in-repo decoder can fit the row family and whether any retrieval generalization appears before scaling to the five-seed evidence standard.

## Reviewer Command

```bash
python scripts/run_stage52_two_block_decoder_feasibility_audit.py
```

This writes:

- `logs/automated_stage_gates/stage52_two_block_decoder_feasibility_audit/manifest.json`
- `logs/automated_stage_gates/stage52_two_block_decoder_feasibility_audit/results.json`
- `logs/automated_stage_gates/stage52_two_block_decoder_feasibility_audit/summary.csv`
- `logs/automated_stage_gates/stage52_two_block_decoder_feasibility_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage52_two_block_decoder_feasibility_audit/failed_runs.json`

## Result

Stage 52 records `TWO_BLOCK_TRAIN_FIT_WITHOUT_RETRIEVAL_GENERALIZATION`.

The stronger two-block decoder fits enough to pass the feasibility capacity threshold, and it solves tiny text-fact QA on the one-seed default packet. It still has zero held-out top-1 on both retrieval lanes.

| Task | Best method | Train top-1 | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | 1.000000 | 1.000000 | 1.000000 | 0.999012 |
| `phase_cued_retrieval` | `sinusoidal` | 1.000000 | 0.000000 | 0.042767 | 0.000040 |
| `exact_offset_passkey` | `sinusoidal` | 0.500000 | 0.000000 | 0.011834 | 0.000007 |

PhaseWrap rows remain bounded:

| Task | Method | Train top-1 | Test top-1 | Test MRR | Test target probability |
| --- | --- | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `phasewrap_bias` | 1.000000 | 1.000000 | 1.000000 | 0.999011 |
| `tiny_text_fact_qa` | `phasewrap_adapter` | 1.000000 | 1.000000 | 1.000000 | 0.999011 |
| `phase_cued_retrieval` | `phasewrap_bias` | 1.000000 | 0.000000 | 0.040936 | 0.000117 |
| `phase_cued_retrieval` | `phasewrap_adapter` | 1.000000 | 0.000000 | 0.040936 | 0.000109 |
| `exact_offset_passkey` | `phasewrap_bias` | 0.500000 | 0.000000 | 0.011834 | 0.000007 |
| `exact_offset_passkey` | `phasewrap_adapter` | 0.500000 | 0.000000 | 0.011834 | 0.000007 |

No runs failed.

## Interpretation

Stage 52 is the first post-plateau feasibility move beyond the one-block and pointer-generator path. It shows that a stronger two-block residual decoder can fit the tiny feasibility packet and reproduce the tiny text-fact QA positive, but it still does not establish retrieval generalization.

The result is useful but narrow:

- capacity is no longer the only blocker on the one-seed feasibility packet;
- tiny text-fact QA remains positive and non-discriminative across methods;
- retrieval generalization remains the blocker;
- PhaseWrap does not lead a retrieval lane;
- the audit does not meet the five-seed promotion standard.

## Claim Boundary

Supported:

- one-seed two-block decoder feasibility evidence;
- evidence that stronger decoder capacity can fit train rows and tiny text-fact QA;
- preservation of retrieval failure modes under fair positional comparisons;
- a concrete next path for scaling only if retrieval repair is targeted directly.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap replaces RoPE;
- a claim that one-seed feasibility satisfies the five-seed promotion standard.
