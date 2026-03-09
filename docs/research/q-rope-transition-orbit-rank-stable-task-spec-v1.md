# Transition Orbit Rank-Stable Task Spec v1

## Task
- `synthetic_transition_orbit_rank_stable_response`

## Target rule
- target is ordinal-first rather than absolute-response first
- preserve ordered orbit-transition structure
- score examples by a stable latent ordering functional over orbit-transition compatibility bands
- evaluation primary metric should be rank correlation, with MAE treated as secondary calibration support rather than the branch gate

## Rejection rule
- reject any design whose target collapses to a small symbolic lookup over coarse orbit states
