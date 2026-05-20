# PhaseWrap-RoPE Stage 23 Long-Context Adapter v1

Date: `2026-05-20`

## Purpose

Stage 23 trains positional adapters on the explicit long-context retrieval rows introduced in Stage 22. It trains on `512` and `1024` token contexts, validates on `2048`, and tests on `4096`. Targets remain explicit passkey, multi-needle, and aggregation rules; they are not selected by the PhaseWrap score.

This is a deterministic local positional-adapter benchmark. It is not a full transformer benchmark and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage23_long_context_adapter/manifest.json`
- Results: `logs/automated_stage_gates/stage23_long_context_adapter/results.json`
- Summary CSV: `logs/automated_stage_gates/stage23_long_context_adapter/summary.csv`
- Task summary CSV: `logs/automated_stage_gates/stage23_long_context_adapter/task_summary.csv`
- Runner: `scripts/run_stage23_long_context_adapter.py`
- Implementation: `src/qrope/stage23_long_context_adapter.py`
- Tests: `tests/test_stage23_long_context_adapter.py`

## Reproduce

```bash
python scripts/run_stage23_long_context_adapter.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Method | Test rows | Top-1 | MRR | Mean target probability mass | Mean first relevant rank |
| --- | ---: | ---: | ---: | ---: | ---: |
| `rope_relative` | 60 | 1.000000 | 1.000000 | 0.910440 | 1.000000 |
| `phasewrap_distance_adapter` | 60 | 1.000000 | 1.000000 | 0.600201 | 1.000000 |
| `sinusoidal` | 60 | 0.716667 | 0.852778 | 0.467265 | 1.316667 |
| `phasewrap_residual_adapter` | 60 | 0.566667 | 0.759722 | 0.358606 | 1.583333 |
| `no_position` | 60 | 0.050000 | 0.112677 | 0.037879 | 20.700000 |
| `phasewrap_score` | 60 | 0.000000 | 0.082042 | 0.047273 | 15.566667 |
| `alibi` | 60 | 0.000000 | 0.153361 | 0.040537 | 14.083333 |

The trained `phasewrap_distance_adapter` recovers top-1 and MRR on the held-out `4096` token rows, matching `rope_relative` on argmax ranking. `rope_relative` still has substantially higher mean target probability mass. The fixed `phasewrap_score` remains weak. This supports the adapter direction, not a replacement claim.

## Claim Boundary

Supported:

- deterministic train-short/test-long positional-adapter benchmark on explicit long-context retrieval rows;
- evidence that PhaseWrap-plus-distance can recover argmax ranking through 4096-token held-out contexts after training;
- evidence that RoPE-like scoring remains better calibrated by target probability mass on this packet.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should put the long-context adapter result into a stronger small decoder-only transformer or compact retrieval model with token/value learning, multiple seeds, confidence intervals, and failed-run artifacts.
