# Q-RoPE Transfer Fork-Join Deeper Pair-Reindex Hardening v1

Date: 2026-03-12
Stories: S928

## Packet
- task:
  - `synthetic_symbolic_insufficiency_fork_join_response`
- perturbation:
  - `pair_reindex = 7`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_fork_join`
  - `V_control_symbolic_symbolic_insufficiency_fork_join_regressor`

## Mean Results
- witness:
  - `mae = 0.049771`
  - `rank_correlation = 0.148450`
  - `calibration_slope = 0.391716`
- control:
  - `mae = 0.063486`
  - `rank_correlation = -0.059172`
  - `calibration_slope = -0.403549`

## Per-Seed Result
- seed `42`
  - witness: `mae 0.043211`, `rank_correlation 0.411765`
  - control: `mae 0.070518`, `rank_correlation -0.417647`
- seed `123`
  - witness: `mae 0.041759`, `rank_correlation -0.081121`
  - control: `mae 0.027910`, `rank_correlation 0.643071`
- seed `777`
  - witness: `mae 0.064343`, `rank_correlation 0.114706`
  - control: `mae 0.092029`, `rank_correlation -0.402941`

## Interpretation
- the perturbation was non-inert
- the witness remained ahead on both declared packet metrics in the mean
- one seed favored the control on both metrics, so the branch has now reached a natural decision gate rather than another default perturbation step

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_fork_join_pair7_v1.csv`
