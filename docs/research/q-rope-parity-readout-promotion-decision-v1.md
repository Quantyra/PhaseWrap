# Q-RoPE Parity Readout Promotion Decision v1

## Decision
Promote `parity` to the **provisional default** local screening readout.

Keep `weighted` as the reference baseline readout.

## Why this is only provisional
The evidence is good enough to justify a screening-path upgrade, but not good enough to erase all residual risk:
- `parity` clearly beats `q2`
- `parity` improves local decision usefulness on `yelp` and `imdb`
- `amazon` remains mixed

So the correct move is:
- adopt `parity` for local screening by default
- retain `weighted` as a comparator until the next local packet confirms the promotion

## Comparison summary
### `V3`
- `yelp`
  - `weighted`: mean F1 `0.4467`
  - `parity`: mean F1 `0.5665`
- `imdb`
  - `weighted`: mean F1 `0.3721`, std acc `0.2151`
  - `parity`: mean F1 `0.4632`, std acc `0.1458`
- `amazon`
  - `weighted`: mean F1 `0.6542`
  - `parity`: mean F1 `0.3834`

### `V4`
- `yelp`
  - `weighted`: mean F1 `0.3976`
  - `parity`: mean F1 `0.4922`
- `imdb`
  - `weighted`: mean F1 `0.3721`, std acc `0.2151`
  - `parity`: mean F1 `0.4982`, std acc `0.1118`
- `amazon`
  - `weighted`: mean F1 `0.5600`
  - `parity`: mean F1 `0.5733`

## Interpretation
`parity` is the strongest currently available local readout because:
- it improves local decision quality on two of three datasets for both branches
- it improves stability on the hardest dataset (`imdb`)
- it is the only alternative readout with a credible infrastructure-level case

The main caution is:
- `V3` on `amazon` is still better under `weighted`

That is why parity should be treated as:
- new default for local screening
- but not an unquestioned replacement for all reference analysis yet

## Protocol implication
From this point:
- local screening stories should default to `parity`
- any important local decision should still note the weighted comparison if it is relevant
- no remote policy changes follow from this decision

## Next local path
Use parity as the default readout in the next local packet and test whether the promoted readout actually makes future branch comparisons cleaner.

## Bottom line
Parity is strong enough to become the provisional default local screening readout.
This is an infrastructure upgrade, not a new algorithm claim.
