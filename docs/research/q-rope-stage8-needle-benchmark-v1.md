# PhaseWrap-RoPE Stage 8 Needle-Style Benchmark v1

Date: `2026-05-20`

## Purpose

Stage 8 adds a no-credential local retrieval benchmark to test whether the PhaseWrap-RoPE scoring rule is worth keeping in the RoPE-replacement research lane. The benchmark is a modest synthetic Needle-style task with same-token distractors, multiple seeds, long context lengths, bootstrap intervals, and direct comparisons against RoPE-like, ALiBI-like, sinusoidal, and no-position scoring rules.

This is not a RULER score, not a language-model benchmark, and not production transformer evidence. It is a bounded phase-cued retrieval packet for deciding whether broader RoPE-facing experiments are justified.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage8_needle_benchmark/manifest.json`
- Results: `logs/automated_stage_gates/stage8_needle_benchmark/results.json`
- Summary CSV: `logs/automated_stage_gates/stage8_needle_benchmark/summary.csv`
- Period-pair ablation CSV: `logs/automated_stage_gates/stage8_needle_benchmark/period_pair_ablation.csv`
- Runner: `scripts/run_stage8_needle_benchmark.py`
- Implementation: `src/qrope/stage8_needle_benchmark.py`
- Tests: `tests/test_stage8_needle_benchmark.py`

## Reproduce

```bash
python scripts/run_stage8_needle_benchmark.py
```

The command is local-only. It does not submit hardware jobs and does not require provider credentials.

## Task

Each example builds a sequence of length `128`, `256`, `512`, or `1024` with a final query position. Several prior positions share the query token, so content alone is ambiguous. The target needle is selected by a hidden phase-cued positional relation under the default `(8, 12)` PhaseWrap score. Methods rank prior positions using the same content logits and different positional scoring rules.

The fixed packet uses five seeds, eight examples per length per seed, and `160` total examples.

## Result

| Method | Rows | Lengths | Top-1 | 95% CI | MRR | 95% CI | Mean rank |
| --- | ---: | --- | ---: | --- | ---: | --- | ---: |
| `phasewrap_rope_8_12` | 160 | 128-1024 | 1.000000 | 1.000000-1.000000 | 1.000000 | 1.000000-1.000000 | 1.000000 |
| `no_position` | 160 | 128-1024 | 0.068750 | 0.031250-0.106250 | 0.216054 | 0.180333-0.250577 | 9.537500 |
| `sinusoidal` | 160 | 128-1024 | 0.043750 | 0.012500-0.075000 | 0.181553 | 0.151338-0.216159 | 11.775000 |
| `rope_relative` | 160 | 128-1024 | 0.043750 | 0.012500-0.081250 | 0.180632 | 0.149406-0.214460 | 13.187500 |
| `alibi` | 160 | 128-1024 | 0.031250 | 0.006250-0.062500 | 0.160126 | 0.129624-0.191875 | 13.712500 |

On this phase-cued synthetic packet, `phasewrap_rope_8_12` is the best ranking method by top-1 and MRR.

## Period-Pair Ablation

The same packet was rerun across candidate PhaseWrap period pairs. The default `(8, 12)` pair is best on this packet:

| Period pair | Top-1 | MRR | Mean rank |
| --- | ---: | ---: | ---: |
| `8,12` | 1.000000 | 1.000000 | 1.000000 |
| `8,16` | 0.231250 | 0.411437 | 5.500000 |
| `6,12` | 0.087500 | 0.164941 | 15.225000 |
| `7,11` | 0.037500 | 0.169347 | 12.187500 |
| `16,32` | 0.037500 | 0.167811 | 10.481250 |
| `8,24` | 0.018750 | 0.233731 | 5.818750 |
| `4,8` | 0.018750 | 0.108680 | 15.825000 |
| `12,24` | 0.000000 | 0.155435 | 8.450000 |

This ablation supports the release-local choice of `(8, 12)` for the synthetic phase-cued packet. It does not prove that `(8, 12)` is globally optimal.

## Claim Boundary

Supported:

- deterministic local Needle-style retrieval comparison across PhaseWrap-RoPE, RoPE-like, ALiBI-like, sinusoidal, and no-position scoring rules;
- bootstrap intervals over benchmark rows for top-1 and MRR;
- a release-local period-pair ablation that favors `(8, 12)` on this packet;
- evidence that a broader RoPE-facing benchmark lane is worth running.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- proof that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next RoPE-facing experiment should move from this local phase-cued packet to a standard retrieval benchmark or a small transformer training/evaluation loop with multiple seeds, matched compute, and confidence intervals.
