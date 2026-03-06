# Q-RoPE V4b Local Implementation Plan v1

## Goal
Implement `V4b` with the smallest write set that changes the positional mechanism at the shared phase layer and keeps the next validation packet zero-credit.

## Minimal write set
1. [qsim.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qsim.py)
- add `V4b` to the variant registry
- split the current phase helper into:
  - `raw_variant_phases(variant, n_qubits)`
  - `effective_variant_phases(variant, features)`
- keep `V0-V4` behavior unchanged
- implement `V4b` with:
  - base `0.18`
  - clip threshold `0.22`
  - ratio factor `0.35`

2. [qphotonic.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qphotonic.py)
- replace the direct `variant_phases(...)` use with the new effective shared helper
- keep the existing `effective_theta` bounding logic unchanged in the first pass
- do not add smoothing or retry-policy changes in this story

3. [qibm.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qibm.py)
- replace the direct raw phase aggregate with the shared effective helper
- keep the one-qubit circuit family unchanged

4. [run.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/run.py)
- add `V4b` to hardware-cost estimation with the same cost class as `V3`/`V4`
- no runner redesign

5. `configs/ablation/`
- add `V4b.yaml`
- update `manifest.md`

6. `tests/`
- extend focused unit coverage for:
  - raw vs effective phase behavior
  - `V4b` backend translation
  - local statevector path acceptance

## Shared helper shape
Recommended helper API in [qsim.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qsim.py):

```python
def raw_variant_phases(variant: str, n_qubits: int) -> list[float]:
    ...

def effective_variant_phases(variant: str, features: list[float]) -> list[float]:
    ...
```

Behavior:
- `V0-V4`: return the current raw phase schedule
- `V4b`: apply clip plus feature-relative cap

This keeps the implementation centered in one place.

## Suggested implementation order
1. add `V4b` config and raw/effective shared helpers
2. make local statevector path consume effective phases
3. update photonic and IBM translation helpers
4. add focused tests
5. run the zero-credit local packet

## Zero-credit validation packet
Backends:
- `sim_quantum_statevector`
- optional `sim_qiskit_aer`

Datasets:
- `yelp`
- `imdb`
- `amazon`

Seeds:
- `42`
- `123`
- `777`

Variants:
- `V3`
- `V4`
- `V4b`

## Promotion gate
`V4b` qualifies for any paid remote wave only if:
1. accuracy std improves or stays flat on at least two datasets vs `V3`
2. mean accuracy regression is limited to at most one dataset
3. worst-seed accuracy does not collapse vs `V3`
4. the statevector picture is cleaner than damped-only `V4`

## Non-goals for implementation
- no paid remote runs
- no larger-sample wave
- no provider-specific retuning
- no manuscript updates

## Bottom line
`V4b` can be implemented with a small write set if the shared phase logic is made explicit first.
