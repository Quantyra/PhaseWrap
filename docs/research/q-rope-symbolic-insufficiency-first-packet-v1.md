# Q-RoPE Symbolic Insufficiency First Packet v1

Date: 2026-03-10
Stories: S668

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Means
- witness:
  - mean MAE `0.119724`
  - mean rank correlation `0.967399`
  - mean calibration slope `0.989697`
- control:
  - mean MAE `0.262984`
  - mean rank correlation `0.263411`
  - mean calibration slope `0.457492`

## Readout
- the witness beat the frozen-basis symbolic control on both declared packet metrics across all three seeds
- the witness also stayed near calibration slope `1.0`, while the control stayed materially weaker on both fit and ordering
- all generator hard-stop diagnostics passed on all packet runs

## Artifact
- summary: `logs/ablation_runs/summary/symbolic_insufficiency_v1.csv`
