# Q-RoPE Quandela Remote Backend v1

## Scope
- Provider: Quandela Cloud
- Platform: `sim:slos`
- Role: photonic-primary remote execution slice for backend validation

## Implemented path
- Runner backend name: `sim_quandela_remote`
- Entry point: `src/qrope/run.py`
- Remote helper: `src/qrope/qphotonic.py`
- Credential source: `.env` via `QUANDELA_CLOUD_TOKEN`

## Execution design
- Uses a minimal two-mode photonic circuit accepted by the active `sim:slos` provider path.
- Encodes text-dependent and variant-dependent information into an effective beam-splitter rotation parameter.
- Scores are derived from remote probability mass on `|2,0>`, `|1,1>`, and `|0,2>` outcomes.
- Phase-1 remote evaluation is capped to a balanced 12-sample slice to keep cloud latency and submission volume tractable.

## Empirical status
- Authenticated remote execution succeeded.
- Canonical artifact:
  - `logs/ablation_runs/v3-yelp-quandela-s42/metrics.json`
- Current result is backend-validation evidence, not matched-matrix publication evidence.

## Constraints
- Richer Perceval circuit compositions attempted during integration triggered provider-side `400` errors on `sim:slos`.
- The current adapter therefore uses a provider-accepted minimal circuit rather than a broader photonic architecture claim.
- Supplemental backend rows are tracked separately from the canonical `sim_local` publication baseline in `report_v1.md` and `report_v2.md`.

## Next step
- Add IBM Runtime remote adapter as secondary comparator backend.
