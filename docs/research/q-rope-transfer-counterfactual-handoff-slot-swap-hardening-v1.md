# Q-RoPE Transfer Counterfactual-Handoff Slot-Swap Hardening v1

## Packet
- Task: `synthetic_symbolic_insufficiency_counterfactual_handoff_response`
- Perturbation: `slot_swap=1`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff`
  - `V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor`

## Mean Results
- Witness:
  - `mae = 0.055611`
  - `rank_correlation = 0.281026`
  - `calibration_slope = 0.363778`
- Control:
  - `mae = 0.084467`
  - `rank_correlation = -0.023168`
  - `calibration_slope = 0.066013`

## Interpretation
- The `slot_swap=1` packet was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.
- The line remains active under the retained-model structural-hardening gate.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_counterfactual_handoff_slot1_v1.csv`
