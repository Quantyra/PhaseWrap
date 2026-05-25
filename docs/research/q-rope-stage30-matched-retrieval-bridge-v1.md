# PhaseWrap Stage 30 Matched Retrieval-Bridge Benchmark v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 30 hardens the Stage 28 non-phase-cued retrieval bridge by equalizing the input feature width and learned parameter count across positional variants.

The benchmark reuses the Stage 12 passkey, multi-needle, and aggregation-style rows. Targets are selected by explicit retrieval rules, not by maximizing the PhaseWrap score.

## Reviewer Command

```bash
python scripts/run_stage30_matched_retrieval_bridge.py
```

This writes:

- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/manifest.json`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/results.json`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/summary.csv`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/per_run_results.csv`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/task_summary.csv`
- `logs/automated_stage_gates/stage30_matched_retrieval_bridge/weak_runs.json`

## Design

Every method uses:

- the same Stage 12 train/validation/test split;
- five deterministic model initialization seeds;
- feature width `12`;
- hidden width `10`;
- learned parameter count `141`;
- the same optimizer, epochs, learning rate, and L2 penalty;
- confidence intervals over model initialization seeds;
- explicit weak-run reporting.

The compared methods are:

- `no_position`
- `alibi`
- `rope_relative`
- `sinusoidal`
- `phasewrap_bias`
- `phasewrap_residual_adapter`
- `phasewrap_distance_adapter`

## Result

On the default artifact, `rope_relative` and `phasewrap_distance_adapter` both reach mean held-out top-1 `1.000000` and mean MRR `1.000000`.

`rope_relative` remains stronger on probability and calibration metrics:

- `rope_relative` mean target probability: `0.744078`
- `phasewrap_distance_adapter` mean target probability: `0.564161`
- `rope_relative` expected calibration error: `0.260653`
- `phasewrap_distance_adapter` expected calibration error: `0.446620`

## Interpretation

Stage 30 is useful because it removes one confound from Stage 28: uneven feature widths and learned parameter counts. Under this matched feature-budget bridge, PhaseWrap-plus-distance is competitive on argmax retrieval ranking, but RoPE-like scoring remains better calibrated and assigns more target probability mass.

This is not a production transformer result, not a full language-model benchmark, and not evidence that PhaseWrap is a validated RoPE replacement. It supports continuing the RoPE-facing research lane with a stronger decoder-only transformer or standard retrieval harness.

## Claim Boundary

Supported:

- deterministic multi-initialization retrieval-bridge comparison on non-phase-cued RULER-style rows;
- matched feature width, hidden width, optimizer, epochs, and parameter count across methods;
- confidence intervals over initialization seeds and explicit weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap is a validated RoPE replacement.
