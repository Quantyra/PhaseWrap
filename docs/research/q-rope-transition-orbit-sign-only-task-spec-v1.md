# Q-RoPE Transition Orbit Sign-Only Task Specification v1

Date: 2026-03-11
Stories: S410

## Task ID
- `synthetic_transition_orbit_sign_only_binary`

## Objective
- predict only the sign of the latent top-two transition-orbit margin inside each fixed four-candidate list
- positive label means the directional separation favors the forward latent ordering
- negative label means the directional separation favors the opposite latent ordering

## Construction Rule
- reuse the same fixed four-candidate within-state list shape as the signed-margin line
- derive the latent signed margin from the top two latent orbit-transition candidates
- emit binary labels from the sign of that latent margin only
- remove signed-margin magnitude from the target so the task measures directional structure directly
- center class balance within each coarse transition state so coarse sign lookup should be near-null by construction

## Required Generator Diagnostics
- `coarse_sign_lookup_near_null_pass`
- `within_state_sign_variation_pass`
- `sign_label_balance_pass`
- `token_view_balance_pass`

## Why This Is Materially Different
- the stopped signed-margin branch mixed sign and magnitude in one regression target
- this line makes sign the only supervised target
- it preserves the only surviving signal from the stopped branch:
  - witness directional accuracy exceeded all fixed controls

## Rejection Rule
- reject the task if coarse transition state alone predicts sign imbalance away from the centered global rate
- reject the task if within-state sign variation collapses
