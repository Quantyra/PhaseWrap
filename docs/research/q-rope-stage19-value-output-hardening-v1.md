# PhaseWrap-RoPE Stage 19 Value-Output Hardening Probe v1

Date: `2026-05-20`

## Purpose

Stage 19 follows the Stage 18 value-output capacity probe. It keeps attention teacher-forced to the target key positions and tests whether larger learned value embeddings plus full-batch Adam optimization can fit the value-token readout.

This is a local value-output hardening probe. It is not a production transformer benchmark, not a positional-mechanism comparison, and not proof that PhaseWrap-RoPE replaces RoPE.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage19_value_output_hardening/manifest.json`
- Results: `logs/automated_stage_gates/stage19_value_output_hardening/results.json`
- Summary CSV: `logs/automated_stage_gates/stage19_value_output_hardening/summary.csv`
- Runner: `scripts/run_stage19_value_output_hardening.py`
- Implementation: `src/qrope/stage19_value_output_hardening.py`
- Tests: `tests/test_stage19_value_output_hardening.py`

## Reproduce

```bash
python scripts/run_stage19_value_output_hardening.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Result

| Config | Split | Rows | Top-1 | MRR | Mean target value probability | Mean first relevant value rank |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `adam_embed12` | train | 120 | 1.000000 | 1.000000 | 0.997905 | 1.000000 |
| `adam_embed12` | validation | 60 | 0.500000 | 0.548195 | 0.448435 | 71.683333 |
| `adam_embed12` | test | 60 | 0.533333 | 0.552776 | 0.480821 | 71.616667 |
| `adam_embed32` | train | 120 | 1.000000 | 1.000000 | 0.998481 | 1.000000 |
| `adam_embed32` | validation | 60 | 0.533333 | 0.569068 | 0.460804 | 70.750000 |
| `adam_embed32` | test | 60 | 0.500000 | 0.536005 | 0.483142 | 74.450000 |
| `adam_embed64` | train | 120 | 1.000000 | 1.000000 | 0.998636 | 1.000000 |
| `adam_embed64` | validation | 60 | 0.516667 | 0.560726 | 0.451262 | 70.650000 |
| `adam_embed64` | test | 60 | 0.500000 | 0.535775 | 0.480739 | 80.366667 |

The hardened value-output path fits the training rows perfectly and improves held-out value-token retrieval relative to Stage 18. Because attention is teacher-forced, this does not compare PhaseWrap, RoPE, ALiBI, sinusoidal, or no-position mechanisms. It only shows that the value-output bottleneck can be improved enough to justify another positional-mechanism experiment.

## Claim Boundary

Supported:

- deterministic value-output hardening probe for the Stage 17 and Stage 18 bottleneck;
- evidence that full-batch Adam plus learned value embeddings can fit the training rows under teacher-forced attention;
- evidence that the next decoder experiment can reintroduce learned positional attention with a less underpowered value-output path.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next downstream experiment should reintroduce learned positional attention using this hardened value-output path, then compare RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants under matched training settings and multiple seeds.
