# Q-RoPE Variant Selection Memo v1

## Decision
Select `V4` as the active local stability track.

Do not promote `V4b` further at this time.

## Why `V4`
From the redesigned local screening packet:

### `amazon`
- `V3` and `V4` are tied
- `V4b` is slightly worse on F1

### `imdb`
- `V4` reduces variance materially vs `V3`
- `V4b` also reduces variance, but does not produce a clearer overall case than `V4`

### `yelp`
- `V4` improves mean accuracy and reduces variance vs `V3`
- `V4b` improves mean accuracy, but increases variance relative to `V3`

## Why not `V4b`
`V4b` was a credible redesign experiment, but the current evidence does not justify making it the active track:
- it does not clearly beat `V4`
- it does not clearly beat `V3`
- it produces a mixed profile with no decisive advantage

## Why not stay on `V3`
`V3` remains the reference method, but not the active stability-improvement track.

The point of the current phase of work is to find a more defensible variant under local screening before any new remote spend.
On that objective, `V4` is presently the stronger candidate.

## Program posture
- Active local track: `V4`
- Reference comparator: `V3`
- Archived exploratory branch: `V4b`

## Next zero-credit step
Run a larger local packet focused on:
- `V3`
- `V4`
- redesigned local screening circuit

Purpose:
- test whether the apparent `V4` advantage survives a modest local scale-up
- avoid remote spend until the `V4` signal is less brittle

## Remote policy implication
Do not spend Quandela credits on `V4b`.
Only reconsider remote `V4` or `V4b` if a stronger local or larger-sample packet creates a clearly decision-changing question.

## Bottom line
`V4` is the most defensible active local track right now.
`V4b` remains useful as an explored branch, but not the program lead.
