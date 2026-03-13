# Relay-Binding Transfer Implementation v1

Status: completed

Scope:
- Implemented `synthetic_symbolic_insufficiency_relay_binding_response`.
- Added `V_future_relational_witness_symbolic_insufficiency_relay_binding`.
- Added `V_control_symbolic_symbolic_insufficiency_relay_binding_regressor`.

Code paths:
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

Notes:
- The generator enforces relay-specific diagnostics at dataset build time.
- The witness/control packet was rerun with the correct `variant.id` override after discarding an invalid initial launch that bound `model.variant` instead.
- Focused validation passed before packet execution.
