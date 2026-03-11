# Q-RoPE Symbolic Insufficiency Stronger Symbolic Basis v1

Date: 2026-03-10
Stories: S687

## Goal
Define one stricter symbolic family that is stronger than the current frozen basis but still bounded, auditable, and non-lookup.

## Stronger Allowed Symbolic Basis
- coarse transition indicators
- first-order single-channel analog summaries
- first-order pairwise cross-direction summaries
- one bounded quadratic layer over declared analog summaries only
- one bounded cubic layer over declared analog summaries only
- one bounded gated interaction family where a coarse transition indicator may modulate a declared analog summary

## Still Forbidden
- latent path-state ids
- exact microstate keys
- hidden tuple lookups
- explicit per-latent bucket parameters
- uncontrolled mixed symbolic-analog basis growth
- arbitrary higher-than-cubic analog expansion

## Fairness Argument
- the stronger basis is still global and shared across all samples
- it cannot memorize arbitrary latent-path identities because latent-state keys remain excluded
- the only new capacity is low-order smooth interaction structure over already declared summaries
- if this stronger basis catches up later, that is still a fair failure for the current branch rather than symbolic cheating
