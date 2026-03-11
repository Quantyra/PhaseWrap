# Q-RoPE Symbolic Insufficiency Pair-Reindex Hardening Plan v1

Date: 2026-03-10
Stories: S672

## Goal
Run one bounded pairing perturbation on `synthetic_symbolic_insufficiency_transition_response` without changing the frozen symbolic basis.

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbation: `pair_reindex=1`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Gate
- keep the branch active only if the witness still leads the frozen-basis symbolic control on both declared packet metrics
- if the perturbation is inert, record that explicitly and select a non-inert structural perturbation next
