# Q-RoPE Symbolic Insufficiency Hardening Memo v1

Date: 2026-03-11
Stories: S659

## Decision
- narrow the allowed symbolic family further before any implementation approval discussion

## Allowed Symbolic Basis
- coarse transition state indicators only at the declared coarse partition
- single-channel analog summaries only as first-order terms
- pairwise cross-direction summaries only as first-order terms
- one bounded quadratic layer over declared analog summaries only

## Explicitly Excluded
- interaction terms involving coarse indicators and latent path surrogates
- arbitrary polynomial expansion over mixed symbolic and analog terms
- feature generation from token identity or exact microstate keys
- any control that can emulate a lookup over hidden transition tuples

## Why This Hardening Is Necessary
- the previous memo still left too much room for symbolic-family creep
- this repo's dominant failure mode has been post-hoc discovery that the control family was stronger than intended
- the line is only worth continuing if the symbolic family is frozen before implementation

## Status
- memo-only
- implementation still blocked
