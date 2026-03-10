# Q-RoPE Transition Orbit Sign-Consistency Implementation Plan v1

Date: 2026-03-11
Stories: S423

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed First Packet
- task: `synthetic_transition_orbit_sign_consistency_binary`
- candidate: `V_future_relational_witness_transition_orbit_sign_consistency`
- controls:
  - `V_control_symbolic_transition_consistency_lookup`
  - `V_control_symbolic_transition_consistency_cross_direction`
  - `V_control_symbolic_transition_consistency_quadratic`
  - `V_control_symbolic_transition_consistency_orbit_permuted`
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`

## Primary Metrics
- accuracy
- F1

## Required Outputs
- implementation note
- first packet memo
- decision memo
- summary CSV
- generator diagnostics for every run

## Prohibitions
- no remote adapters
- no broader task family changes
- no additional controls
- no uncontrolled metric changes
