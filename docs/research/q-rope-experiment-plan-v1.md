# Q-RoPE Experiment Plan v1 (S004)

## Objective
Design a minimum publishable experiment that isolates positional effects in hybrid quantum attention with NISQ-relevant cost reporting.

## Benchmark-track decision
- Primary track: `QMSAN-style text classification`
- Rationale:
  - Directly relevant positional baseline already reported in source literature.
  - Supports clean ablation between positional strategies.
  - Compatible with lightweight hybrid circuits and practical simulation.

## Experimental variants
Hold architecture/training budget constant and vary only positional method:
1. `V0`: no positional encoding
2. `V1`: additive sinusoidal positional encoding (QASA-style comparator)
3. `V2`: fixed-gate quantum positional encoding (QMSAN-style comparator)
4. `V3`: proposed Q-RoPE relative-phase encoding

## Datasets (initial)
- Yelp
- IMDb
- Amazon

## Metrics
Primary:
- Accuracy / F1 (dataset-appropriate)

Secondary:
- Gate count (per forward pass)
- Circuit depth
- Qubit count
- Shot count and variance summary
- Noise-perturbed performance delta (if simulator noise model enabled)

## Fairness controls
- Same train/validation/test splits per variant.
- Same optimizer, epochs, and tuning budget.
- Same random seed schedule and number of runs.
- Report mean and dispersion across runs.

## Statistical checks
- Pairwise comparison: `V3` vs each baseline (`V0-V2`).
- Effect-size reporting in addition to p-values.
- If gains are small, prioritize confidence intervals over binary claims.

## Reproducibility requirements
- Log environment versions and hardware/simulator details.
- Publish exact config files for each run.
- Save per-run metrics and aggregate scripts under `logs/`.

## Success criteria for advancement
Advance to broader evaluation if:
1. `V3` outperforms `V2` on at least two datasets with stable variance.
2. Hardware-cost increase remains within practical NISQ envelope for selected setup.
3. No severe degradation under moderate noise settings.

## Threats to validity
- Narrow task family may limit generalization.
- Simulated-noise conclusions may not transfer perfectly to hardware.
- Performance gains may be confounded by optimizer sensitivity without strict controls.

## Next step
Prepare implementation-ready runbook and config schema (follow-on execution story).
