# First continuous target packet

## Packet
- Task: `synthetic_dual_continuous_coupled_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate: `V_future_relational_witness_continuous`
- Controls:
  - `V_control_symbolic_single_family_regressor`
  - `V_control_symbolic_two_family_regressor`
  - `V_control_symbolic_boolean_state_lookup`

## Means
| Variant | Mean MAE | Mean rank correlation | Mean calibration slope |
|---|---:|---:|---:|
| `V_future_relational_witness_continuous` | `0.539635` | `-0.867722` | `-0.588898` |
| `V_control_symbolic_single_family_regressor` | `0.397070` | `1.000000` | `0.334969` |
| `V_control_symbolic_two_family_regressor` | `0.398802` | `1.000000` | `0.334000` |
| `V_control_symbolic_boolean_state_lookup` | `0.200000` | `0.000000` | `0.000000` |

## Direct reading
- The candidate lost to every approved control on the primary metric (`MAE`).
- The candidate also failed on monotonic structure: its rank correlation was strongly negative on all three seeds.
- The bounded lookup control was the strongest baseline and materially outperformed the candidate.

## Interpretation
- The current continuous witness branch is not competitive on this task.
- This task is still structurally compressible by a bounded symbolic lookup over the three agreement bits.
- The branch therefore does not justify expansion, remote work, or a second continuous implementation iteration.

## Artifacts
- Summary: `logs/ablation_runs/summary/continuous_target_v1.csv`
- Candidate example: `logs/ablation_runs/continuous-witness-s42/metrics.json`
- Strongest control example: `logs/ablation_runs/continuous-lookup-s42/metrics.json`
