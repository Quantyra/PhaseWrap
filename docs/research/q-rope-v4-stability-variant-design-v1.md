# Q-RoPE V4 Stability Variant Design v1

## Objective
Define a `V4` variant that explicitly trades some peak expressivity for better seed/provider stability than `V3`.

## Diagnosis from `V3`
- `V3` uses the strongest relative-phase magnitude in the current stack.
- The matched 3-seed remote packet shows rank-order flips across both providers.
- That suggests the current positional signal is likely too aggressive relative to the small-slice evaluation and backend-specific transfer functions.

## Proposed `V4`
- Name: `V4` = damped-and-clipped relative-phase Q-RoPE

## Design
1. Damped phase magnitude
- Reduce the raw `V3` phase scale before applying it.
- Example:
  - if `V3` uses base phase `0.24`
  - `V4` uses a damped base phase in the range `0.12` to `0.16`

2. Clipped effective phase contribution
- Explicitly cap the positional phase contribution so it cannot dominate feature loading.
- Goal: lower sensitivity to seed-driven feature-angle fluctuations.

3. Backend-safe translation
- For photonic and IBM adapters, derive backend-effective parameters from the same damped phase schedule rather than reusing the stronger `V3` schedule.
- This keeps `V4` semantically consistent across local and remote paths while reducing backend-specific amplification.

4. Optional evaluation-time smoothing
- For remote evaluation only, allow a small deterministic average over a tiny neighborhood of the phase parameter.
- Example:
  - evaluate at `theta - delta`, `theta`, `theta + delta`
  - average the resulting score
- This is optional because it increases cost.

## Why this is the right `V4`
- It is the smallest credible change from `V3`.
- It targets the actual observed weakness: instability, not lack of expressivity.
- It keeps the Q-RoPE identity intact instead of turning the method into a different class of model.

## Stability evaluation plan
Compare `V4` against `V3` on:
1. Mean accuracy
2. Seed standard deviation
3. Provider rank-order consistency
4. Worst-seed drop
5. Stability-adjusted score:
- `mean_accuracy - lambda * std_accuracy`

## Success criterion
`V4` is a success if:
- it lowers seed/provider variance relative to `V3`
- while keeping performance in the same rough band
- even if its best single-seed result is slightly below `V3`

## Recommended implementation order
1. Add `V4` as damped phase schedule only
2. Run local comparison vs `V3`
3. If local stability improves, test the smallest remote packet
4. Only add evaluation-time smoothing if simple damping is insufficient

## Bottom line
`V4` should not aim to be “more powerful” than `V3`.
It should aim to be more stable, easier to interpret, and more defensible under remote execution.
