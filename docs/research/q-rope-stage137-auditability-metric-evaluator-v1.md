# QRoPE Stage 137 - Auditability Metric Evaluator

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 137 implements the hardware-count-dependent auditability evaluator preregistered in Stage 136.

Current decision: `AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED`.

The evaluator reads the Stage 107 independent-window plan, requires each window's Stage 101 calibration result to pass, requires packet execution files to carry Stage 113 assembly status, then reconstructs `component_a` and `component_b` from the same packet execution counts used by Stage 103:

- product-state template: `component_a = E[Z0]`, `component_b = E[Z1]`
- CX/parity template: `component_a = E[Z0]`, `component_b = E[Z0 Z1]`

It computes component reconstruction mean absolute error per packet family and applies the Stage 136 auditability advantage rule against the named positional comparators.

## Claim Boundary
Supported:

- deterministic component-reconstruction auditability evaluator
- same-window binding to Stage 107 packet counts and Stage 101 calibration results
- auditability interpretation requires Stage 113-assembled packet evidence
- blocked output while real provider packet counts are missing

Excluded:

- hardware job submission
- provider credentials or secret values
- new provider result records
- a current auditability advantage claim unless this gate is ready and the advantage rule passes
- a robustness advantage claim

## Evidence
- `logs/automated_stage_gates/stage137_auditability_metric_evaluator/manifest.json`
- `logs/automated_stage_gates/stage137_auditability_metric_evaluator/results.json`
- `logs/automated_stage_gates/stage137_auditability_metric_evaluator/summary.csv`
