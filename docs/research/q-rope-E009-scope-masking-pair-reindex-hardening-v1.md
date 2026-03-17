# Q-RoPE E009 Scope-Masking Pair-Reindex Hardening v1

Date: 2026-03-17
Stories: S1557-S1559

## Fixed Packet
- dataset: `synthetic_positional_scope_masked_reference_selection_response`
- perturbation: `pair_reindex=1`
- witness: `V_future_relational_witness_positional_scope_masked_reference_selection`
- control: `V_control_symbolic_positional_scope_masked_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.024153`
  - `rank_correlation = 0.302127`
  - `calibration_slope = 0.824590`
- control:
  - `mae = 0.024790`
  - `rank_correlation = 0.016515`
  - `calibration_slope = 0.130736`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The next valid move is the fixed structural hardening packet `slot_swap=1` only.

## Summary CSV
- `logs/ablation_runs/summary/E009_scope_masking_pair1_v1.csv`
