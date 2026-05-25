# PhaseWrap Stage 31 Full-Context Retrieval-Attention Benchmark v1

Date: `2026-05-20`

Status: `completed`

## Purpose

Stage 31 moves beyond the candidate-only bridge by making every prefix position compete in a learned retrieval-attention distribution. It reuses the Stage 12 non-phase-cued passkey, multi-needle, and aggregation rows.

Targets are selected by explicit retrieval rules, not by maximizing the PhaseWrap score.

## Reviewer Command

```bash
python scripts/run_stage31_full_context_retrieval_attention.py
```

This writes:

- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/manifest.json`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/results.json`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/summary.csv`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/per_run_results.csv`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/task_summary.csv`
- `logs/automated_stage_gates/stage31_full_context_retrieval_attention/weak_runs.json`

## Design

Every method uses:

- the same Stage 12 train/validation/test split;
- five deterministic model initialization seeds;
- a learned full-prefix attention distribution over all positions before the query;
- the same four learned attention parameters: bias, content-match scale, positional scale, and content-position interaction scale;
- the same optimizer, epochs, learning rate, and L2 penalty;
- confidence intervals over model initialization seeds;
- explicit weak-run reporting.

The compared methods are:

- `no_position`
- `alibi`
- `rope_relative`
- `sinusoidal`
- `phasewrap_bias`
- `phasewrap_distance_adapter`

## Result

On the default artifact, `rope_relative` solves the held-out full-prefix retrieval packet with mean top-1 `1.000000`, mean MRR `1.000000`, and mean target probability `0.821104`.

The PhaseWrap variants are weak in this harder setting:

- `phasewrap_bias` mean top-1: `0.016667`
- `phasewrap_bias` mean MRR: `0.080860`
- `phasewrap_distance_adapter` mean top-1: `0.000000`
- `phasewrap_distance_adapter` mean MRR: `0.050557`

## Interpretation

Stage 31 is negative evidence for the current PhaseWrap variants under full-prefix non-phase-cued retrieval. It shows that the Stage 30 candidate-bridge tie does not carry over when every prefix position competes under a four-parameter learned attention rule.

This is not a production transformer result and not a full language-model benchmark. It is a useful standard-retrieval stress test that makes the remaining mechanism gap more precise: PhaseWrap-derived features need a stronger mechanism than the current fixed score or simple distance adapter before a RoPE-replacement claim is supportable.

## Claim Boundary

Supported:

- deterministic multi-initialization full-context retrieval-attention comparison on non-phase-cued Stage 12 rows;
- same four learned attention parameters, optimizer, epochs, and train/test split across methods;
- confidence intervals over initialization seeds and explicit weak-run reporting.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness;
- a claim that PhaseWrap is a validated RoPE replacement.
