# Q-RoPE E002 Variable-Cardinality Token-Renaming Hardening Plan v1

Date: 2026-03-14
Stories: S1334-S1337

## BLUF
- The first packet survived.
- The next retained hardening step is `token_permutation=cdab` only.
- No wider `E002` perturbation expansion is active.

## Fixed Hardening Packet
- dataset: `synthetic_positional_variable_cardinality_offset_selection_response`
- witness: `V_future_relational_witness_positional_variable_cardinality_offset_selection`
- control: `V_control_symbolic_positional_variable_cardinality_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- token permutation: `cdab`
- seeds: `42`, `123`, `777`

## Stop Rule
- Stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
