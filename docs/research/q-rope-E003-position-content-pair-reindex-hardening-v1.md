# Q-RoPE E003 Position-Content Pair-Reindex Hardening v1

Date: 2026-03-14
Stories: S1373-S1375

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_gated_offset_selection_response`
- witness: `V_future_relational_witness_positional_content_gated_offset_selection`
- control: `V_control_symbolic_positional_content_gated_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `1`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 0.036784`
  - `rank_correlation = 0.449895`
  - `calibration_slope = 1.033210`
- control:
  - `mae = 0.043259`
  - `rank_correlation = -0.048069`
  - `calibration_slope = -0.297460`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The first structural packet strengthened the line relative to the nuisance packet.

## Summary CSV
- `logs/ablation_runs/summary/E003_position_content_gated_offset_selection_pair1_v1.csv`
