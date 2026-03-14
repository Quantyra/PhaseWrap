# Q-RoPE Transfer Counterfactual-Handoff First Packet v1

## Packet
- Task: `synthetic_symbolic_insufficiency_counterfactual_handoff_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff`
  - `V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor`

## Mean Results
- Witness:
  - `mae = 0.054381`
  - `rank_correlation = 0.715145`
  - `calibration_slope = 1.539889`
- Control:
  - `mae = 0.140255`
  - `rank_correlation = -0.121916`
  - `calibration_slope = 0.051553`

## Interpretation
- The declared packet metrics for this line are:
  - `mae`
  - `rank_correlation`
- On both declared packet metrics, the witness led the bounded symbolic control in the mean.
- The witness also led on both declared metrics on each seed in the fixed packet.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_counterfactual_handoff_v1.csv`
