# Q-RoPE Symbolic Insufficiency Residual-Atlas Implementation Plan v1

Date: 2026-03-11
Stories: S717

## Writable Scope
- `src/qrope/run.py`
- focused tests only:
  - `tests/test_run_real_mode.py`
- no task-generator changes
- no witness changes
- no control-family proliferation

## Future Challenger
- `V_control_symbolic_symbolic_insufficiency_regressor_residual_atlas`

## Frozen Transition Set
- exactly 8 directional transitions over the 4 fixed charts:
  - `00->01`, `00->10`
  - `01->00`, `01->11`
  - `10->00`, `10->11`
  - `11->01`, `11->10`
- no diagonal self-transition features
- no all-to-all transition expansion

## Frozen Residual Interaction Set
For each allowed transition, permit exactly:
- `transition x sector_magnitude_delta`
- `transition x ordered_content_delta`
- `transition x orientation_delta`

No other residual interactions are allowed.

## Required Diagnostics
- `atlas_chart_count_frozen_pass`
- `atlas_chart_rule_global_pass`
- `atlas_hidden_lookup_absent_pass`
- `residual_transition_family_frozen_pass`
- `residual_transition_directionality_frozen_pass`
- `residual_transition_hidden_lookup_absent_pass`
- `allowed_symbolic_basis_frozen_pass`
- `forbidden_feature_family_absent_pass`

## Future Packet
- task:
  - `synthetic_symbolic_insufficiency_transition_response`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- models:
  - `V_future_relational_witness_symbolic_insufficiency`
  - `V_control_symbolic_symbolic_insufficiency_regressor_residual_atlas`

## Stop Rule
- stop immediately if the residual-atlas control matches or beats the witness on both declared packet metrics
