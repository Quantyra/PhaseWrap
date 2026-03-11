# Q-RoPE Symbolic Insufficiency Residual-Atlas Family v1

Date: 2026-03-11
Stories: S712

## Purpose
Define one materially stronger symbolic family than the shared-atlas control without allowing symbolic-family creep back into hidden lookup behavior.

## Family Definition
- base family remains fixed:
  - coarse transition indicators
  - first-order analog summaries
  - pairwise cross-direction summaries
  - exactly 4 global atlas chart indicators
  - bounded chart-indicator x analog interactions
- stronger extension:
  - one residual chart-transition family between atlas regions
  - transitions are only between the 4 frozen global charts
  - transition features may only use declared analog residuals:
    - `sector_magnitude_delta`
    - `ordered_content_delta`
    - `orientation_delta`
  - transition family is directional but globally shared

## Allowed Additional Basis
- `chart_ij_to_kl_exists` style indicators over the 4 fixed charts
- one bounded residual interaction family:
  - chart-transition indicator x declared analog residual
- no chart-specific free regressors beyond those residual interactions

## Forbidden Additions
- latent path ids
- exact microstate keys
- hidden tuple lookups
- per-example chart refinement
- chart count growth beyond 4
- arbitrary transition family growth after packet inspection
- uncontrolled cubic or spline residualization

## Rationale
- the shared-atlas family stayed materially weaker than the witness
- the next fairer symbolic challenge is not another wider polynomial basis
- it is one globally shared residual structure over the same frozen atlas
- this is materially stronger while still auditable
