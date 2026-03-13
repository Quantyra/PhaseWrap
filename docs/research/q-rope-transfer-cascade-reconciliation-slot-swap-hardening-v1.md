# Q-RoPE Transfer Cascade Reconciliation Slot-Swap Hardening v1

## Fixed Hardening Packet
- Task: `synthetic_symbolic_insufficiency_cascade_reconciliation_response`
- Perturbation: `slot_swap=1`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_cascade_reconciliation`
  - `V_control_symbolic_symbolic_insufficiency_cascade_reconciliation_regressor`

## Mean Results
- Witness:
  - `mae = 0.090885`
  - `rank_correlation = 0.513725`
  - `calibration_slope = 0.929024`
- Control:
  - `mae = 0.120414`
  - `rank_correlation = 0.263725`
  - `calibration_slope = 0.491024`

## Interpretation
- `slot_swap=1` was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_cascade_reconciliation_slot1_v1.csv`
