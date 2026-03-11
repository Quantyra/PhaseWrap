# Q-RoPE Symbolic Insufficiency Token-Renaming Hardening v1

Date: 2026-03-10
Stories: S670

## Packet
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- perturbation: `token_permutation=cdab`
- candidate: `V_future_relational_witness_symbolic_insufficiency`
- control: `V_control_symbolic_symbolic_insufficiency_regressor`

## Means
- witness:
  - mean MAE `0.189371`
  - mean rank correlation `0.956863`
  - mean calibration slope `1.073694`
- control:
  - mean MAE `0.263307`
  - mean rank correlation `0.204089`
  - mean calibration slope `0.168935`

## Readout
- the perturbation was not inert; the witness MAE degraded materially relative to the base packet
- the witness still beat the frozen-basis symbolic control on both declared packet metrics across all three seeds
- generator diagnostics still passed on all six runs and the control still satisfied the frozen-basis audit

## Artifact
- summary: `logs/ablation_runs/summary/symbolic_insufficiency_cdab_v1.csv`
