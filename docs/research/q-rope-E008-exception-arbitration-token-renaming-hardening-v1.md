# Q-RoPE E008 Exception Arbitration Token-Renaming Hardening v1

Date: 2026-03-16
Stories: S1522-S1524

## Fixed Packet
- dataset: `synthetic_positional_exception_conditioned_reference_selection_response`
- perturbation: `token_permutation=cdab`
- witness: `V_future_relational_witness_positional_exception_conditioned_reference_selection`
- control: `V_control_symbolic_positional_exception_conditioned_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.015870`
  - `rank_correlation = 0.284161`
  - `calibration_slope = 0.529760`
- control:
  - `mae = 0.020636`
  - `rank_correlation = -0.209642`
  - `calibration_slope = -0.208039`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The next valid move is the fixed structural hardening packet `pair_reindex=1` only.

## Summary CSV
- `logs/ablation_runs/summary/E008_exception_arbitration_cdab_v1.csv`
