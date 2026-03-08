# Q-RoPE Pair-State Sector Definition Memo v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Goal
Close the narrowest remaining design gap in the pair-state direction:
- define an explicit sector scheme
- define an explicit sector aggregation rule

## Candidate sector scheme
Use four sectors:
- `P_small`: positive offsets with small magnitude
- `P_large`: positive offsets with large magnitude
- `N_small`: negative offsets with small magnitude
- `N_large`: negative offsets with large magnitude

For the current synthetic family, one simple partition is:
- small magnitude: `|offset| in {1, 2}`
- large magnitude: `|offset| in {3, 4}`

## Why this sector scheme
This preserves two forms of structure:
- sign of relative offset
- coarse magnitude of relative offset

That is better than:
- one global scalar
- or sign-only collapse

Because it lets a future candidate fail visibly in more ways:
- no sign separation
- no magnitude stability
- inconsistent contrast across sub-sectors

## Candidate aggregation rule
Use:
- `O_sign = (Resp(P_small) + Resp(P_large)) - (Resp(N_small) + Resp(N_large))`

And track the auxiliary magnitude-balance diagnostic:
- `O_mag_balance = |Resp(P_small) - Resp(P_large)| + |Resp(N_small) - Resp(N_large)|`

## Intended interpretation
- `O_sign` tests signed relative-offset discrimination
- `O_mag_balance` tests whether the sign result is being driven by one unstable corner of the space rather than a coherent relational structure

## Why this is better than a proxy-like global score
This does not immediately compress the entire state into one pooled response.

It preserves:
- sign structure
- coarse magnitude structure
- asymmetry visibility

That is the minimum needed to argue that the measurement is still relational.

## Remaining gap after this memo
One important gap still remains:
- how the pair-state preparation places examples into these sectors operationally in the state construction

So this memo narrows the gap but does not eliminate it.

## Implication for approval status
This memo strengthens the pair-state angle.
It still does not justify implementation approval by itself.

## Bottom line
The pair-state direction now has a concrete candidate sector scheme and aggregation rule:
- four sectors by sign and coarse magnitude
- signed contrast as primary signal
- magnitude-balance as stability diagnostic

That is enough to continue memo-level refinement without drifting back into vague design language.

