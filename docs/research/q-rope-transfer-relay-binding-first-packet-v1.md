# Relay-Binding Transfer First Packet v1

Status: completed

Packet:
- task: `synthetic_symbolic_insufficiency_relay_binding_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- witness: `V_future_relational_witness_symbolic_insufficiency_relay_binding`
- control: `V_control_symbolic_symbolic_insufficiency_relay_binding_regressor`

Generator diagnostics:
- `coarse_relay_state_null_pass = true`
- `within_relay_state_variation_pass = true`
- `latent_relay_diversity_pass = true`
- `token_view_balance_pass = true`
- `relay_length_balance_pass = true`
- `binding_target_nontrivial_pass = true`

Corrected packet means:
- witness:
  - `mae = 0.076905`
  - `rank_correlation = 0.405686`
  - `calibration_slope = 0.761817`
- control:
  - `mae = 0.096542`
  - `rank_correlation = -0.094722`
  - `calibration_slope = -0.299738`

Per-seed witness:
- `s42`: `mae=0.056701`, `rank=0.399411`
- `s123`: `mae=0.062374`, `rank=0.385294`
- `s777`: `mae=0.111639`, `rank=0.432353`

Per-seed control:
- `s42`: `mae=0.068278`, `rank=-0.154754`
- `s123`: `mae=0.074191`, `rank=-0.150000`
- `s777`: `mae=0.147157`, `rank=0.020588`

Interpretation:
- The relay-binding witness beat the bounded symbolic control on both declared packet metrics in the corrected fixed packet.
- The relay line is valid for bounded hardening.
