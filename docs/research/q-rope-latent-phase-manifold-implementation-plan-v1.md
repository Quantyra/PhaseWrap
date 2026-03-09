# Latent phase manifold implementation plan

## Task
- `synthetic_dual_latent_phase_manifold_residual_response`

## Candidate
- `V_future_relational_witness_latent_phase`

## Fixed controls
- `V_control_symbolic_coarse_lookup_regressor`
- `V_control_symbolic_analog_only_regressor`
- `V_control_symbolic_nonlinear_manifold_regressor`
- `V_control_symbolic_phase_insensitive_regressor`
- `V_control_symbolic_global_phase_regressor`

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Required diagnostics
- coarse tuple mean absolute max
- within-state variation flag
- candidate/control mean MAE
- candidate/control rank correlation
- candidate/control calibration slope
- proof that latent neighborhood ids are absent from all controls
- proof that the global-phase control uses one fixed global phase family only

## Fixed first packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- task only
- candidate plus five fixed controls only

## Stop rule
Stop immediately after the first packet unless the candidate beats every fixed control on the primary regression metric while preserving strong rank ordering.
