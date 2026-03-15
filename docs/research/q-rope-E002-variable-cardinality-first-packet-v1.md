# Q-RoPE E002 Variable-Cardinality First Packet v1

Date: 2026-03-14
Stories: S1334-S1337

## Fixed Packet
- dataset: `synthetic_positional_variable_cardinality_offset_selection_response`
- witness: `V_future_relational_witness_positional_variable_cardinality_offset_selection`
- control: `V_control_symbolic_positional_variable_cardinality_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.038947`
  - `rank_correlation = 0.465817`
  - `calibration_slope = 0.752925`
- control:
  - `mae = 0.050383`
  - `rank_correlation = 0.089800`
  - `calibration_slope = 0.278973`

## Summary CSV
- `logs/ablation_runs/summary/E002_variable_cardinality_offset_selection_v1.csv`
