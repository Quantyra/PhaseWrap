# Q-RoPE Successor Key-Query Offset Selection Deeper Pair-Reindex Hardening v1

## Fixed Hardening Packet
- dataset: `synthetic_positional_key_query_offset_selection_response`
- perturbation: `pair_reindex=7`
- witness: `V_future_relational_witness_positional_key_query_offset_selection`
- control: `V_control_symbolic_positional_key_query_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.043087`
  - `rank_correlation = 0.488714`
  - `calibration_slope = 0.847273`
- control:
  - `mae = 0.057999`
  - `rank_correlation = 0.107130`
  - `calibration_slope = 0.285498`

## Summary CSV
- `logs/ablation_runs/summary/successor_key_query_offset_selection_pair7_v1.csv`
