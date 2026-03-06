# Q-RoPE Quandela Hardening Note v1

## Change
- Kept the existing bounded `effective_theta` policy.
- Added retry with cache reset and backoff in `qrope.qphotonic.quandela_remote_score(...)`.
- Failure now escalates as an explicit runtime error that includes the blocked `effective_theta`.

## What improved
- Previously blocked seed `123` / `V0` Quandela run now completes:
  - `logs/ablation_runs/v0-yelp-quandela-s123/metrics.json`

## What did not improve
- Seed `123` still failed for:
  - `V2` at `effective_theta=0.933180`
  - `V3` at `effective_theta=0.890480`
- So the retry/cache-reset policy reduces failure but does not eliminate the provider-side rejection regime.

## Interpretation impact
- Prior supplemental remote results remain usable as recorded artifacts.
- The hardening does not justify stronger cross-provider claims.
- The Quandela path still needs an explicit remap or skip policy before we can claim robust seed coverage.
