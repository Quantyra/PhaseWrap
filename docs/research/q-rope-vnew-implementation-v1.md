# Q-RoPE V_new Explicit Interference Implementation v1

## Scope
- Story: `S107`
- Boundary: local-only, zero-credit, synthetic-only restart implementation
- Out of scope: remote execution, broader benchmark expansion, additional mechanism branches

## What was implemented
- Added `V_new_explicit_interference` to the local simulator path in `src/qrope/qsim.py`
- Added explicit branch-state construction for synthetic pair rows using separable content and positional phase loading
- Added constructive/destructive interference contrast scoring via parity contrast
- Added synthetic run diagnostics in `src/qrope/run.py`

## Mechanism summary
- Branch states:
  - `|psi_i> = P(i) E(x_i) |0>`
  - `|psi_j> = P(j) E(x_j) |0>`
- Comparison primitive:
  - constructive channel from normalized `|psi_i> + |psi_j>`
  - destructive channel from normalized `|psi_i> - |psi_j>`
- Observable:
  - parity contrast `Parity_plus - Parity_minus`
- Score:
  - mapped into `[0, 1]` for the existing local evaluation path

## Validation
- Focused local suite passed:
  - `PYTHONPATH=src python -m pytest tests/test_qsim.py tests/test_run_real_mode.py tests/test_vnew_interference.py`
  - Result: `49 passed`
- First bounded smoke run succeeded:
  - `logs/ablation_runs/vnew-synthetic-s42/metrics.json`
  - `logs/ablation_runs/vnew-synthetic-s42/run_diagnostics.json`

## First smoke-run readout
- Accuracy: `0.492188`
- F1: `0.545455`
- Positive-minus-negative offset gap: `-0.011029`
- Overall score mean: `0.457883`

## Immediate interpretation
- The bounded implementation is executable and instrumented correctly.
- The first smoke result is not a success signal.
- The required next step remains the fixed falsification packet:
  - `V0` vs `V_new_explicit_interference`
  - `synthetic_offset_binary`
  - seeds `42/123/777`

## Files touched
- `src/qrope/qsim.py`
- `src/qrope/run.py`
- `tests/test_qsim.py`
- `tests/test_run_real_mode.py`
- `tests/test_vnew_interference.py`
