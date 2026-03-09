# Continuous target implementation

## Scope
- Implemented only the approved local synthetic branch for `synthetic_dual_continuous_coupled_response`.
- Added one candidate: `V_future_relational_witness_continuous`.
- Added three bounded symbolic regression controls:
  - `V_control_symbolic_single_family_regressor`
  - `V_control_symbolic_two_family_regressor`
  - `V_control_symbolic_boolean_state_lookup`

## Code changes
- `src/qrope/synthetic.py`
  - added `generate_dual_continuous_coupled_response_bundle(...)`
  - added continuous label mode in dual synthetic sample construction
  - extended split diagnostics with continuous target summaries
- `src/qrope/run.py`
  - added continuous dataset loader path
  - added continuous witness and control feature builders
  - added linear-regression training/evaluation helpers
  - added continuous backend runners and extra regression metrics
- `tests/`
  - added continuous synthetic and runner coverage

## Validation
- Focused suite passed:
  - `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
  - result: `113 passed`

## Packet outputs
- Packet summary: `logs/ablation_runs/summary/continuous_target_v1.csv`
- Candidate runs:
  - `logs/ablation_runs/continuous-witness-s42/metrics.json`
  - `logs/ablation_runs/continuous-witness-s123/metrics.json`
  - `logs/ablation_runs/continuous-witness-s777/metrics.json`
- Control runs:
  - `logs/ablation_runs/continuous-single-s42/metrics.json`
  - `logs/ablation_runs/continuous-single-s123/metrics.json`
  - `logs/ablation_runs/continuous-single-s777/metrics.json`
  - `logs/ablation_runs/continuous-twofam-s42/metrics.json`
  - `logs/ablation_runs/continuous-twofam-s123/metrics.json`
  - `logs/ablation_runs/continuous-twofam-s777/metrics.json`
  - `logs/ablation_runs/continuous-lookup-s42/metrics.json`
  - `logs/ablation_runs/continuous-lookup-s123/metrics.json`
  - `logs/ablation_runs/continuous-lookup-s777/metrics.json`

## Readout
- Implementation succeeded.
- The packet result is handled in the first-packet memo and decision memo.
