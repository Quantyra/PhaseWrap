# Q-RoPE Transition Orbit Listwise Pair-Reindex Hardening v1

Date: 2026-03-11
Stories: S386

## Packet
- task: `synthetic_transition_orbit_listwise_ranking`
- perturbation: `pair_reindex = 1`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_transition_orbit_listwise`
- controls:
  - `V_control_symbolic_transition_list_cross_direction`
  - `V_control_symbolic_transition_list_orbit_permuted`

## Mean Results
- witness: accuracy `0.303030`, order-F1 `0.526912`, eval loss `0.333987`
- cross-direction: accuracy `0.242424`, order-F1 `0.388745`, eval loss `0.328985`
- orbit-permuted: accuracy `0.242424`, order-F1 `0.394805`, eval loss `0.326782`

## Interpretation
- This perturbation was non-inert.
- The witness remained ahead of both retained controls on top-1 accuracy.
- The witness also widened its lead on order-F1 relative to the first packet.
- The branch survives this hardening step cleanly.
