# Q-RoPE Symbolic Insufficiency Implementation v1

Date: 2026-03-10
Stories: S667

## Scope
- task: `synthetic_symbolic_insufficiency_transition_response`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`
- seeds: `42`, `123`, `777`
- backend: `sim_quantum_statevector`

## Changes
- added `generate_symbolic_insufficiency_transition_response_bundle(...)` in `src/qrope/synthetic.py`
- added `symbolic_insufficiency_latent_ids(...)` and symbolic-insufficiency label mode support in `src/qrope/synthetic.py`
- added dataset routing, witness features, symbolic control features, and bounded backend runners in `src/qrope/run.py`
- added focused coverage in `tests/test_synthetic.py` and `tests/test_run_real_mode.py`

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- result: `255 passed`

## Gate Enforcement
- generator diagnostics passed on all six runs:
  - `coarse_state_null_pass = true`
  - `within_state_variation_pass = true`
  - `latent_path_diversity_pass = true`
  - `token_view_balance_pass = true`
- witness runs passed:
  - `bounded_feature_audit_pass = true`
  - `forbidden_feature_family_absent_pass = true`
- control runs passed:
  - `allowed_symbolic_basis_frozen_pass = true`
  - `forbidden_feature_family_absent_pass = true`
