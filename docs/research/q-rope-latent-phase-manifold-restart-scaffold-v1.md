# Restart scaffold for latent phase manifold task

## Task
- `synthetic_dual_latent_phase_manifold_residual_response`

## Future candidate
- `V_future_relational_witness_latent_phase`

## Fixed future controls
- `V_control_symbolic_coarse_lookup_regressor`
- `V_control_symbolic_analog_only_regressor`
- `V_control_symbolic_nonlinear_manifold_regressor`
- `V_control_symbolic_phase_insensitive_regressor`
- `V_control_symbolic_global_phase_regressor`

## Fixed first packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Required diagnostics
- coarse tuple mean absolute max
- within-state variation flag
- candidate/control mean MAE
- candidate/control rank correlation
- proof that latent neighborhood ids are not exposed to controls
- proof that the global phase control excludes neighborhood-conditioned residual routing

## Future gate
Do not approve implementation unless the task memo and scaffold together show all of the following:
- coarse lookup is near-null by construction
- additive analog baselines are intentionally insufficient
- the current nonlinear manifold family is intentionally insufficient
- the current phase-insensitive family is intentionally insufficient
- one bounded global-phase symbolic control family is intentionally insufficient
