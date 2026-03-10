# Q-RoPE Transition Orbit Sign-Only Restart Scaffold v1

Date: 2026-03-11
Stories: S411

## Future Task
- `synthetic_transition_orbit_sign_only_binary`

## Future Candidate
- `V_future_relational_witness_transition_orbit_sign_only`

## Fixed Future Controls
- `V_control_symbolic_transition_sign_lookup`
- `V_control_symbolic_transition_sign_cross_direction`
- `V_control_symbolic_transition_sign_quadratic`
- `V_control_symbolic_transition_sign_orbit_permuted`

## Fixed First Packet
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`
- local-only
- zero-credit

## Primary Metrics
- accuracy
- F1

## Hard Stop Contract
- do not approve implementation until the task proves:
  - `coarse_sign_lookup_near_null_pass = true`
  - `within_state_sign_variation_pass = true`
  - `sign_label_balance_pass = true`
  - `token_view_balance_pass = true`

## Explicitly Disallowed
- reopening the failed signed-margin task
- remote execution
- benchmark expansion
- new symbolic control families
- second witness candidate
