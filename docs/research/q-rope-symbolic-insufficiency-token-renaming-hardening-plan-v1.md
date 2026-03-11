# Q-RoPE Symbolic Insufficiency Token-Renaming Hardening Plan v1

Date: 2026-03-10
Stories: S670

## Goal
Run one bounded nuisance-variable hardening step on `synthetic_symbolic_insufficiency_transition_response`.

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbation: fixed `token_permutation=cdab`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Gate
- keep the branch active only if the witness still leads the frozen-basis symbolic control on both declared packet metrics
- if the perturbation is inert, record that explicitly and choose a non-inert hardening step next
