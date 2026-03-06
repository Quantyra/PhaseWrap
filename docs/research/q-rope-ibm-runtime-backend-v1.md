# Q-RoPE IBM Runtime Backend v1

## Scope
- Provider: IBM Quantum Runtime
- Access mode: token-only, no explicit CRN required for current open-instance access
- Role: secondary remote comparator backend

## Implemented path
- Runner backend name: `ibm_runtime_remote`
- Helper: `src/qrope/qibm.py`
- Credential source: `.env` via `IBM_QUANTUM_TOKEN`
- Default backend selection order: `IBM_QUANTUM_BACKEND` env override, then `ibm_torino`, `ibm_marrakesh`, `ibm_fez`

## Execution design
- Uses a one-qubit circuit with feature-conditioned `RY` and variant-conditioned `RZ`.
- Batches train/test slice circuits into `SamplerV2` submissions to reduce remote overhead.
- Uses the same balanced 12-sample slice policy as the Quandela remote adapter.

## Empirical status
- Remote runtime connectivity succeeds without explicit instance CRN.
- Canonical artifact:
  - `logs/ablation_runs/v3-yelp-ibm-s42/metrics.json`
- This is comparator evidence only, not a matched publication-grade IBM study.

## Constraints
- Backend availability is tied to the current `open-instance` plan and may vary over time.
- IBM connectivity showed intermittent resolution instability during integration, so retries are included in the helper.
- IBM results are supplemental and do not override the photonic-primary strategy.

## Next step
- Build matched supplemental remote slices so Quandela and IBM can be compared on the same fixed sample set.
