# Q-RoPE V4 Local Implementation Plan v1

## Goal
Make `V4` implementation-ready without triggering any paid remote execution.

## Code touch points
1. `configs/ablation/V4.yaml`
- Add a new variant config:
  - `variant.id = V4`
  - positional encoding type remains Q-RoPE family
  - note that this is the stability-oriented damped/clipped variant

2. `src/qrope/qsim.py`
- Extend `variant_phases(...)` with a `V4` phase base lower than `V3`
- Recommended first value:
  - `V4 = 0.14`
- Keep the same structural form as `V3`; only damp the phase scale

3. `src/qrope/qphotonic.py`
- Ensure `V4` uses the same damped phase schedule in `derive_photonic_angles(...)`
- Keep the current bounded `effective_theta` path
- Do not add smoothing in the first implementation pass

4. `src/qrope/qibm.py`
- Ensure `derive_ibm_angles(...)` translates `V4` from the same damped phase schedule
- No new circuit family in phase 1

5. `src/qrope/run.py`
- No major runner redesign needed if `V4` is added through the existing variant plumbing
- Existing backend routing should work once the phase schedule and config exist

## First local-only comparison set
- Dataset set:
  - `yelp`
  - `imdb`
  - `amazon`
- Variants:
  - `V3`
  - `V4`
- Backends:
  - `sim_local`
  - optional `sim_quantum_statevector` as a secondary local check
- Seeds:
  - `42`, `123`, `777`

## Minimum evidence before any paid remote `V4` wave
Require all of the following:
1. `V4` lowers seed standard deviation vs `V3` on at least two local datasets
2. `V4` stays in the same rough mean-performance band as `V3`
3. `V4` does not introduce obvious new local regressions in worst-seed behavior

## Remote gate
- If those conditions are met, the first paid remote `V4` wave should be the smallest packet only:
  - `yelp`
  - `V3` vs `V4`
  - one seed first
- Do not run a broad remote matrix until local stability improvement is demonstrated

## Recommended next implementation order
1. Add `V4.yaml`
2. Add `V4` phase scale in `qsim.py`
3. Propagate the same schedule into photonic and IBM adapters
4. Run local-only `V3` vs `V4` comparison set

## Bottom line
`V4` is implementation-ready with a very small write set.
The next engineering step should stay local-first and zero-credit.
