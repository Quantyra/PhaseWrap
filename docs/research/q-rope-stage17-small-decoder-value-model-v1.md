# PhaseWrap Stage 17 Small Decoder Value-Model Benchmark v1

Date: `2026-05-20`

## Purpose

Stage 17 moves one step closer to a decoder-style model by adding learned candidate value embeddings and a learned output projection. The benchmark keeps the Stage 14 non-phase-cued key-value rows, but target value recovery must now pass through learned embeddings rather than direct attention mass.

This is a compact learned readout, not a production transformer benchmark and not proof that PhaseWrap replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage17_small_decoder_value_model/manifest.json`
- Results: `logs/automated_stage_gates/stage17_small_decoder_value_model/results.json`
- Summary CSV: `logs/automated_stage_gates/stage17_small_decoder_value_model/summary.csv`
- Task summary CSV: `logs/automated_stage_gates/stage17_small_decoder_value_model/task_summary.csv`
- Runner: `scripts/run_stage17_small_decoder_value_model.py`
- Implementation: `src/qrope/stage17_small_decoder_value_model.py`
- Tests: `tests/test_stage17_small_decoder_value_model.py`

## Reproduce

```bash
python scripts/run_stage17_small_decoder_value_model.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Method | Test rows | Top-1 | 95% CI | MRR | 95% CI | Mean target value probability | Mean first relevant value rank |
| --- | ---: | ---: | --- | ---: | --- | ---: | ---: |
| `alibi` | 60 | 0.016667 | 0.000000-0.050000 | 0.035720 | 0.014190-0.074830 | 0.005180 | 112.300000 |
| `phasewrap_distance_adapter` | 60 | 0.016667 | 0.000000-0.050000 | 0.035684 | 0.013534-0.073384 | 0.005179 | 111.983333 |
| `no_position` | 60 | 0.016667 | 0.000000-0.050000 | 0.035577 | 0.014753-0.069692 | 0.005179 | 116.633333 |
| `rope_relative` | 60 | 0.016667 | 0.000000-0.066667 | 0.035220 | 0.014134-0.071050 | 0.005179 | 112.700000 |
| `phasewrap_residual_adapter` | 60 | 0.016667 | 0.000000-0.050000 | 0.035159 | 0.014221-0.080195 | 0.005179 | 110.800000 |
| `phasewrap_score` | 60 | 0.016667 | 0.000000-0.050000 | 0.034337 | 0.013603-0.071303 | 0.005179 | 110.066667 |
| `sinusoidal` | 60 | 0.016667 | 0.000000-0.050000 | 0.032703 | 0.012686-0.068529 | 0.005179 | 110.866667 |

The learned embedding/output readout is near chance for every method. This is negative evidence for the current compact decoder-style implementation. It does not contradict Stages 15-16; it shows that the direct attention-ranking advantage does not yet survive this learned value-output bottleneck.

## Claim Boundary

Supported:

- deterministic train-short/test-long learned value-token readout over non-phase-cued key-value rows;
- evidence that this compact decoder-style readout is too weak or poorly conditioned for the tested packet;
- evidence that no tested positional mechanism establishes a value-model advantage in this Stage 17 setup.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap replaces RoPE.

## Next Step

The next downstream experiment should improve the small decoder training setup before interpreting positional mechanisms: larger training packet, better optimization, validation-based checkpointing, and possibly an output objective that distinguishes train-fit failure from extrapolation failure.
