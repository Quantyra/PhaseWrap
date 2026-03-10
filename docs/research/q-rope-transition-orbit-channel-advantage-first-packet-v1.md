# Q-RoPE Transition Orbit Channel-Advantage First Packet v1

Date: 2026-03-10
Stories: S452

## Packet
- dataset: `synthetic_transition_orbit_channel_advantage_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- candidate: `V_future_relational_witness_transition_orbit_channel_advantage`
- controls:
  - `V_control_symbolic_transition_channel_lookup_regressor`
  - `V_control_symbolic_transition_channel_cross_direction_regressor`
  - `V_control_symbolic_transition_channel_quadratic_regressor`
  - `V_control_symbolic_transition_channel_orbit_permuted_regressor`

## Means
- witness:
  - mean MAE `1.4355570057684293e+85`
  - mean rank correlation `0.116667`
  - mean calibration slope `0.000255`
- lookup:
  - mean MAE `0.024761`
  - mean rank correlation `0.000000`
- cross-direction:
  - mean MAE `0.030308`
  - mean rank correlation `0.097619`
- quadratic:
  - mean MAE `0.029765`
  - mean rank correlation `0.109524`
- orbit-permuted:
  - mean MAE `0.027744`
  - mean rank correlation `0.095238`

## Readout
- the witness was numerically unstable on seeds `42` and `777`
- witness MAE exploded to `1.6071426177858414e+61` on seed `42`
- witness MAE exploded to `4.306671017305288e+85` on seed `777`
- the fixed symbolic regressors remained finite and materially better on the primary metric

## Artifact
- summary: `logs/ablation_runs/summary/transition_orbit_channel_advantage_v1.csv`
