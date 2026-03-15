# Q-RoPE E004 Content-Alias Implementation Plan v1

Date: 2026-03-15
Stories: S1396-S1397

## BLUF
- `synthetic_positional_content_alias_disambiguation_response` passes only to one bounded local implementation cycle.
- The implementation must keep alias pressure real in every active candidate set while preserving one frozen symbolic family.
- Execution remains bounded to one fixed three-seed packet if and only if the implementation clears the hard-stop conditions below.

## Frozen Task
- task:
  - `synthetic_positional_content_alias_disambiguation_response`
- witness:
  - `V_future_relational_witness_positional_content_alias_disambiguation`
- bounded symbolic control:
  - additive and bounded-quadratic regressor over declared query summaries, per-candidate content summaries, per-candidate offset summaries, and bounded aggregate alias-ambiguity summaries only

## Frozen Bounds
- candidate-count range:
  - `3`, `4`, `5`
- content-class bound:
  - `3`
- active alias requirement:
  - at least one same-class distractor in every candidate set
- slot-rotation requirement:
  - target and same-class distractor positions must rotate across active slots

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`

## Hard-Stop Conditions
Stop E004 immediately if implementation requires:
- content-only solvability by construction
- slot-only solvability by construction
- separate symbolic families by candidate count or alias pattern
- raw token-identity shortcuts
- candidate-count cap above `5`
- content-class cap above `3`
- candidate sets without active same-class distractors

## Required Diagnostics
- `coarse_content_alias_state_null_pass`
- `within_content_alias_state_variation_pass`
- `alias_pressure_nontrivial_pass`
- `content_only_null_pass`
- `position_only_null_pass`
- `joint_target_nontrivial_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_content_class_pass`
- `bounded_candidate_count_pass`
- `alias_slot_rotation_pass`
- `joint_noncollapse_pass`

## Outcome Rule
- implement once
- run exactly one fixed three-seed packet only if the frozen fairness contract holds
- stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`
