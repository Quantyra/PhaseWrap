# Latent phase manifold task specification

## Task
- `synthetic_dual_latent_phase_manifold_residual_response`

## Motivation
The phase-sensitive manifold task failed because both the direct nonlinear manifold control family and the phase-insensitive control family remained sufficient. The next task must preserve auditable analog factors while making the target depend on bounded latent neighborhood structure that is not reducible to one global nonlinear transform over declared factors.

## Declared analog factors
- `sector_magnitude_delta`
- `ordered_content_delta`
- `orientation_delta`

## Latent neighborhood structure
Define one latent local neighborhood assignment over the declared analog state using a bounded partition of relational space. The assignment may depend on declared factors, but it is not itself an allowed control input. The target must vary by neighborhood-specific wrapped phase residuals rather than one global phase map.

## Target rule requirements
Let:
- `u = sector_magnitude_delta`
- `v = ordered_content_delta`
- `w = orientation_delta`
- `z = latent neighborhood id`

The raw response must satisfy all of the following:
- include one global analog backbone term over `u`, `v`, `w`
- include one bounded latent residual term whose phase or curvature changes with `z`
- preserve within-neighborhood variation
- be centered within each coarse agreement tuple so coarse lookup remains near-null

## Required properties
- coarse agreement tuple means must be near zero after centering
- additive analog controls must be intentionally insufficient
- the current direct nonlinear manifold control family must be intentionally insufficient
- the current phase-insensitive family must be intentionally insufficient
- a future symbolic control may use only declared analog factors, not latent neighborhood ids

## Rejection rule
Reject the task if any of the following is true:
- coarse lookup remains materially predictive after centering
- one global nonlinear basis over declared analog factors is sufficient
- a phase-insensitive control family remains sufficient
- the latent residual collapses into a direct closed-form transform of declared analog factors
