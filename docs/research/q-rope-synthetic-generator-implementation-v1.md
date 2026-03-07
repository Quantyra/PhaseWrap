# Q-RoPE Synthetic Generator Implementation v1

## Completed
The first executable synthetic salvage path is now implemented.

Added:
- [synthetic.py](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\src\qrope\synthetic.py)

Updated:
- [run.py](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\src\qrope\run.py)
- [test_run_real_mode.py](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\tests\test_run_real_mode.py)
- [test_synthetic.py](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\tests\test_synthetic.py)

## What was implemented
- deterministic signed relative-offset dataset generation
- fixed train / validation / test splits
- balanced class, token-pair, and offset-magnitude construction
- generator diagnostics written beside run metrics
- runner dataset mode:
  - `synthetic_offset_binary`

## Validation
- focused local test suite:
  - `45 passed`
- first executable synthetic run succeeded:
  - [metrics.json](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\logs\ablation_runs\synthetic-v3-s42\metrics.json)
  - [generator_diagnostics.json](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\logs\ablation_runs\synthetic-v3-s42\generator_diagnostics.json)

## First run observation
The first synthetic `V3` smoke run on seed `42` is near chance:
- accuracy `0.507812`
- F1 `0.350515`

This is not yet decision-grade.
It is only an implementation smoke result.

## Why this matters
The salvage path is no longer theoretical.
We now have:
- a deterministic synthetic task
- leakage-aware diagnostics
- an executable local packet path

## Next step
Run the full first synthetic packet:
- `V0` vs `V3`
- seeds `42`, `123`, `777`
- then decide whether the salvage hypothesis has any positive signal at all
