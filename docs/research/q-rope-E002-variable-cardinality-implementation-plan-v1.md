# Q-RoPE E002 Variable-Cardinality Implementation Plan v1

Date: 2026-03-14
Stories: S1332-S1333

## BLUF
- The variable-cardinality candidate is bounded enough to permit one implementation plan.
- The fairness contract remains strict: one frozen symbolic family must cover the allowed candidate-count range without count-specific basis drift.
- Execution remains closed until this bounded plan is explicitly accepted.

## Task
- `synthetic_positional_variable_cardinality_offset_selection_response`

## Witness
- `V_future_relational_witness_positional_variable_cardinality_offset_selection`

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared query summaries, per-candidate summaries, and bounded aggregate set summaries only

## Frozen Candidate-Count Range
- allowed active candidate counts: `3`, `4`, `5`
- fixed upper cap: `5`
- no implementation is allowed to widen this range inside the plan

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Required Hard-Stop Diagnostics
- `coarse_variable_cardinality_state_null_pass`
- `within_variable_cardinality_state_variation_pass`
- `candidate_count_range_nontrivial_pass`
- `variable_cardinality_target_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `distractor_insertion_nontrivial_pass`
- `cross_count_target_stability_pass`

## Required Audits
- `allowed_variable_cardinality_symbolic_basis_frozen_pass`
- `forbidden_variable_cardinality_feature_family_absent_pass`
- `single_symbolic_family_across_counts_pass`

## Execution Rule
- Reopen code for one bounded local implementation cycle only if this plan is accepted.
- Run exactly one fixed three-seed packet.
- Stop the line immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.

## Candidate-Specific Hard Stop
Stop `E002` immediately if any of the following happen during implementation:
- the task needs separate symbolic families for different candidate counts
- correctness collapses into padded fixed-cardinality behavior
- variable cardinality can only be maintained by slot-identity shortcuts
- the candidate-count cap must grow beyond `5` to remain nontrivial
