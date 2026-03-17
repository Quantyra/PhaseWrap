# Q-RoPE E008 Exception Arbitration Pair-Reindex Hardening Plan v1

Date: 2026-03-16
Stories: S1522-S1524

## Next Step
- Run the fixed structural hardening packet with `pair_reindex=1`.

## Frozen Conditions
- Keep only:
  - `V_future_relational_witness_positional_exception_conditioned_reference_selection`
  - `V_control_symbolic_positional_exception_conditioned_reference_selection_regressor`
- Keep the same dataset and seed packet:
  - `synthetic_positional_exception_conditioned_reference_selection_response`
  - `42`, `123`, `777`
- Stop immediately if the control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
