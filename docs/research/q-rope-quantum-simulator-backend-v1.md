# Q-RoPE Quantum Simulator Backend v1

## Status
Implemented and verified in local workspace.

## Backend name
`sim_quantum_statevector`

## What it is
- Internal statevector simulator using explicit unitary evolution.
- Circuit includes per-qubit `RY` feature loading, variant-dependent `RZ` phase gates, and nearest-neighbor CNOT entangling.
- Implemented in `src/qrope/qsim.py`.

## Integration points
- `src/qrope/run.py` routes real-mode execution to quantum simulation when:
  - `--real-run` is set
  - `backend=sim_quantum_statevector`

## Verified run
- Run id: `v3-yelp-qsim-s42`
- Artifact: `logs/ablation_runs/v3-yelp-qsim-s42/metrics.json`
- `run_mode=real`, `dry_run=false`, backend marked as quantum simulator.

## Current limits
- This is local simulation, not cloud photonic hardware.
- Circuit and model are minimal and intended for backend-path validation, not final performance claims.
- Phase-2 still requires photonic cloud backend integration for hardware-relevant claims.
