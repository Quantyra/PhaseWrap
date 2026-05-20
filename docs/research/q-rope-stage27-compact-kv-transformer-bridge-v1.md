# PhaseWrap-RoPE Stage 27 Compact KV Transformer-Bridge Benchmark v1

Date: `2026-05-20`

Status: `complete`

## Purpose

Stage 27 is a no-credential benchmark increment toward the next transformer milestone. It takes the Stage 26 compact content-key QA packet and trains a one-hidden-layer attention bridge over each positional feature family across five deterministic initialization seeds.

The target is not selected by the PhaseWrap score. For each row, the target is the latest candidate whose content key matches the query key. This keeps the benchmark aligned with the RoPE-facing roadmap while staying small enough to run locally without provider credentials or external datasets.

Stage 27 is not a full decoder-only language-model benchmark and does not prove that PhaseWrap-RoPE replaces RoPE.

## Command

```bash
python scripts/run_stage27_compact_kv_transformer_bridge.py
```

## Artifacts

- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/manifest.json`
- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/results.json`
- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/summary.csv`
- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage27_compact_kv_transformer_bridge/weak_runs.json`

## Current Result

Held-out test rows use length `2048`; train rows use lengths `256` and `512`. Each method is trained across five model initialization seeds.

| Method | Mean top-1 | Mean MRR | Mean target probability |
| --- | ---: | ---: | ---: |
| `phasewrap_distance_adapter` | `0.950000` | `0.975000` | `0.823006` |
| `alibi` | `0.950000` | `0.975000` | `0.821886` |
| `phasewrap_residual_adapter` | `0.920000` | `0.960000` | `0.801163` |
| `sinusoidal` | `0.810000` | `0.905000` | `0.719015` |
| `rope_relative` | `0.320000` | `0.541381` | `0.316363` |
| `phasewrap_score` | `0.300000` | `0.610000` | `0.328851` |
| `no_position` | `0.000000` | `0.325000` | `0.319258` |

`phasewrap_distance_adapter` and `alibi` tie on top-1 and MRR in this compact bridge. `phasewrap_distance_adapter` has a slightly higher mean target probability on this run. The fixed `phasewrap_score` remains weak.

## Interpretation

Stage 27 is constructive evidence for the PhaseWrap-plus-distance adapter shape on one compact content-key QA packet. It also keeps the current claim boundary intact:

- it is a compact attention bridge, not a full transformer;
- it is a deterministic local benchmark, not hardware evidence;
- it does not establish production transformer superiority;
- it does not establish that PhaseWrap-RoPE replaces RoPE.

## Next Step

The next stronger experiment is still the roadmap milestone in `docs/research/q-rope-next-transformer-benchmark-roadmap-v1.md`: a matched small decoder-only transformer or standard retrieval/QA benchmark with RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap variants, multiple seeds, confidence intervals, failed-run artifacts, and at least one task whose target is not constructed from the PhaseWrap score.
