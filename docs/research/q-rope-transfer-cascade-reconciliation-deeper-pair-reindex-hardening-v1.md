# Q-RoPE Transfer Cascade Reconciliation Deeper Pair-Reindex Hardening v1

## Fixed Hardening Packet
- Task: `synthetic_symbolic_insufficiency_cascade_reconciliation_response`
- Perturbation: `pair_reindex=7`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_cascade_reconciliation`
  - `V_control_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor`

## Mean Results
- Witness:
  - `mae = 0.084618`
  - `rank_correlation = 0.373529`
  - `calibration_slope = 0.535314`
- Control:
  - `mae = 0.143941`
  - `rank_correlation = 0.023530`
  - `calibration_slope = 0.118807`

## Interpretation
- `pair_reindex=7` was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_cascade_reconciliation_pair7_v1.csv`
