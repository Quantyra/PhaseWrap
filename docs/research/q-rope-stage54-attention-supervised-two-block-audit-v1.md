# PhaseWrap-RoPE Stage 54 Attention-Supervised Two-Block Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 54 tests whether the Stage 52/53 two-block decoder retrieval failure is primarily an attention-selection failure or a learned value-output failure. It keeps the same fair positional method set:

- `rope_relative`
- `alibi`
- `sinusoidal`
- `no_position`
- `phasewrap_bias`
- `phasewrap_adapter`

The decoder remains a learned two-block residual decoder with a learned vocabulary softmax and no fixed copy output. Stage 54 adds an auxiliary target-position attention loss during training, then reports both vocabulary retrieval metrics and target-position attention mass.

This is a diagnostic audit, not promotion evidence. Target-attention supervision is an extra teacher signal and the default run is one seed.

## Reviewer Command

```bash
python scripts/run_stage54_attention_supervised_two_block_audit.py
```

This writes:

- `logs/automated_stage_gates/stage54_attention_supervised_two_block_audit/manifest.json`
- `logs/automated_stage_gates/stage54_attention_supervised_two_block_audit/results.json`
- `logs/automated_stage_gates/stage54_attention_supervised_two_block_audit/summary.csv`
- `logs/automated_stage_gates/stage54_attention_supervised_two_block_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage54_attention_supervised_two_block_audit/failed_runs.json`

## Result

Stage 54 records `ATTENTION_SUPERVISION_RETRIEVAL_REPAIR_FAILED`.

| Task | Best method | Train target attention | Test target attention | Test top-1 | Test target probability |
| --- | --- | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `alibi` | 1.000000 | 0.526987 | 0.500000 | 0.499754 |
| `phase_cued_retrieval` | `rope_relative` | 0.582363 | 0.012690 | 0.000000 | 0.000026 |
| `exact_offset_passkey` | `phasewrap_bias` | 0.999962 | 0.030917 | 0.000000 | 0.000078 |

PhaseWrap rows remain bounded:

| Task | Method | Train target attention | Test target attention | Test top-1 | Test target probability |
| --- | --- | ---: | ---: | ---: | ---: |
| `tiny_text_fact_qa` | `phasewrap_bias` | 1.000000 | 0.642159 | 0.500000 | 0.499750 |
| `tiny_text_fact_qa` | `phasewrap_adapter` | 1.000000 | 0.635189 | 0.500000 | 0.499751 |
| `phase_cued_retrieval` | `phasewrap_bias` | 0.710797 | 0.022905 | 0.000000 | 0.000022 |
| `phase_cued_retrieval` | `phasewrap_adapter` | 0.706657 | 0.025349 | 0.000000 | 0.000023 |
| `exact_offset_passkey` | `phasewrap_bias` | 0.999962 | 0.030917 | 0.000000 | 0.000078 |
| `exact_offset_passkey` | `phasewrap_adapter` | 0.999975 | 0.028805 | 0.000000 | 0.000075 |

No runs failed.

## Interpretation

Stage 54 does not repair retrieval. Target-attention supervision drives high training target attention for the tiny QA and exact-offset rows, and partially raises training attention for phase-cued retrieval, but held-out retrieval target attention remains far below the `0.50` repair threshold. Both retrieval lanes remain at zero held-out top-1.

This result narrows the next step. The Stage 52/53 two-block path is not merely failing because the vocabulary head cannot decode from already-generalized target attention; in this setup, target-attention supervision also fails to generalize retrieval attention itself. The next fair-comparison gate should redesign the retrieval-capable matched decoder path rather than broadening claims from this auxiliary-loss diagnostic.

## Claim Boundary

Supported:

- target-attention-supervised diagnostics for the bounded Stage 52/53 two-block decoder path;
- evidence separating attention-selection repair from learned value-output retrieval success;
- fair method comparison with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that target-attention supervision is standard free decoder generation;
- a claim that Stage 54 satisfies the five-seed promotion standard.
