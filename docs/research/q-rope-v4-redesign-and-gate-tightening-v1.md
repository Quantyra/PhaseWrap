# Q-RoPE V4 Redesign And Gate Tightening v1

## What S039 had to resolve
1. exclude non-variant-sensitive local backends from `V4` promotion decisions
2. document why the damped-only `V4` failed
3. define the next redesign direction without spending remote credits

## Tightened local gate
The local promotion gate for future `V4`-style variants should use only backends that actually consume the variant schedule.

Allowed for local screening:
- `sim_quantum_statevector`
- optional `sim_qiskit_aer`

Disallowed for variant promotion decisions:
- `sim_local`

Reason:
- `sim_local` uses the naive-Bayes path in [run.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/run.py)
- it does not consume `variant_phases(...)`
- it is useful for pipeline smoke coverage, not for variant-quality decisions

## Failure mode of damped-only `V4`
The current `V4` changed only one thing:
- reduced phase magnitude from `V3` to a damped base phase of `0.14`

That was too weak as a redesign because:
- it improved only one dataset (`imdb`) on the meaningful local backend
- it regressed `yelp`
- it regressed `amazon`
- it did not produce a consistent reduction in seed variance

The evidence suggests the current problem is not simply “phase too large everywhere.”
It looks more dataset-dependent than that.

## Answer on sample size
No, adding samples has not yet been shown to improve outcomes because we did not run a larger-sample comparison wave in S038.

What actually changed in S038:
- more local comparison runs across datasets and seeds
- no expansion of the remote 12-sample packet
- no larger local holdout construction beyond the current local datasets

So the correct statement is:
- current evidence does not show that increased sample size improved `V4`
- that question remains open

## Recommended redesign direction
The next `V4` iteration should not be “more damping.”
It should be a more targeted stability variant.

Recommended next design:
- `V4b = clipped-relative-phase plus light feature/phase ratio control`

Elements:
1. keep a moderate phase base rather than the current blunt damping
2. clip the relative positional contribution before backend translation
3. limit how much positional phase can exceed feature-loading contribution

Why this is better:
- it targets phase dominance directly
- it preserves more expressivity than the current damped-only form
- it is still a small change from `V3`

## Promotion rule before any paid remote wave
Require all of the following on a variant-sensitive local backend:
1. improved or unchanged accuracy standard deviation on at least two datasets
2. no material mean-accuracy regression on more than one dataset
3. no worst-seed collapse relative to `V3`

If that gate is not met:
- do not spend Quandela credits

## Bottom line
The right move is not a remote rerun.
The right move is to redesign `V4` and screen it only on variant-sensitive local backends first.
