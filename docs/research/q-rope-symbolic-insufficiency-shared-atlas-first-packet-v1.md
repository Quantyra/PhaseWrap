# Q-RoPE Symbolic Insufficiency Shared-Atlas First Packet v1

Date: 2026-03-11
Stories: S710

## Packet
- task: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate baseline:
  - `V_future_relational_witness_symbolic_insufficiency`
- challenger control:
  - `V_control_symbolic_symbolic_insufficiency_regressor_atlas`

## Mean Results
- witness:
  - `mae = 0.119724`
  - `rank_correlation = 0.967399`
  - `calibration_slope = 0.989697`
- shared-atlas control:
  - `mae = 0.302863`
  - `rank_correlation = 0.207421`
  - `calibration_slope = 0.132462`

## Audit Status
- witness forbidden-feature audit passed on all runs
- atlas frozen-basis diagnostics passed on all runs:
  - `atlas_chart_count_frozen_pass = true`
  - `atlas_chart_rule_global_pass = true`
  - `atlas_hidden_lookup_absent_pass = true`
  - `allowed_symbolic_basis_frozen_pass = true`
  - `forbidden_feature_family_absent_pass = true`

## Artifact
- summary csv:
  - `logs/ablation_runs/summary/symbolic_insufficiency_atlas_v1.csv`
