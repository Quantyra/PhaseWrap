# State-sensitive continuous implementation plan

## Approved branch
- task: `synthetic_dual_state_sensitive_continuous_response`
- candidate: `V_future_relational_witness_state_sensitive`
- controls:
  - `V_control_symbolic_coarse_lookup_regressor`
  - `V_control_symbolic_analog_only_regressor`
  - `V_control_symbolic_full_declared_regressor`

## Target rule to implement
For each dual sample, compute:
- `sign_term in {-1, +1}`
- `content_term in {-1, +1}`
- `orientation_term in {-1, +1}`
- `sector_magnitude_delta in [-1, +1]`
- `ordered_content_delta in [-1, +1]`

Use one bounded target of the form:
- `target = 0.25*sign_term + 0.15*content_term + 0.10*orientation_term + 0.15*sector_magnitude_delta + 0.10*ordered_content_delta + 0.15*(sign_term*sector_magnitude_delta) + 0.10*(content_term*ordered_content_delta)`

## Planned control schemas
- coarse lookup regressor:
  - sees only coarse agreement bits
- analog-only regressor:
  - sees only `sector_magnitude_delta`, `ordered_content_delta`
- full declared regressor:
  - sees additive coarse and analog terms only
  - does not receive explicit interaction terms

## Planned candidate schema
- witness features may include sector-first relational responses plus derived continuous witness summaries
- the implementation must not expose forbidden raw shortcuts such as direct token identity or absolute positions to the classical head

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Fixed first packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit
- no extra tasks or variants

## Required diagnostics
- target summary by split
- proof of within-state variation
- coefficient/intercept audit for all controls and candidate
- `anti_collapse_pass`
- packet summary on primary metric: `MAE`
