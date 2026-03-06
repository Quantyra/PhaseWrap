# Q-RoPE V3 vs V4 Token-to-Score Sensitivity v1

## Scope
This note measures how strongly the local screening score reacts to token removal under `V3` and `V4`.

Backend:
- `sim_quantum_statevector`

Credit status:
- `0` additional Quandela credits consumed

Diagnostic artifact:
- `logs/diagnostics/v3_v4_token_sensitivity.json`

## Packet
- variants: `V3`, `V4`
- datasets: `yelp`, `imdb`, `amazon`
- seeds: `42`, `123`, `777`, `2024`, `9001`

Per-text procedure:
1. compute the base score
2. remove one token at a time
3. recompute the score
4. record:
   - mean absolute token-removal delta
   - max absolute token-removal delta
   - within-text delta dispersion

Aggregate metrics:
- mean absolute token delta
- mean max token delta
- mean within-text delta standard deviation
- overall score standard deviation
- class-mean score gap

## Aggregate result
### Yelp
- `V3`: mean abs delta `0.0879`, mean max delta `0.1629`, mean delta std `0.0457`, score std `0.0773`
- `V4`: mean abs delta `0.0704`, mean max delta `0.1349`, mean delta std `0.0377`, score std `0.0639`

### IMDb
- `V3`: mean abs delta `0.0765`, mean max delta `0.1548`, mean delta std `0.0457`, score std `0.0658`
- `V4`: mean abs delta `0.0625`, mean max delta `0.1295`, mean delta std `0.0378`, score std `0.0530`

### Amazon
- `V3`: mean abs delta `0.0771`, mean max delta `0.1473`, mean delta std `0.0444`, score std `0.0632`
- `V4`: mean abs delta `0.0616`, mean max delta `0.1206`, mean delta std `0.0365`, score std `0.0504`

## Key pattern
Across all three datasets and all five seeds:
- `V4` consistently lowers token-removal sensitivity
- `V4` consistently lowers overall score spread
- `V4` does **not** create a comparably strong improvement in class-mean separation

That means the effect of `V4` is mostly:
- score compression
- lower token responsiveness
- weaker dynamic range

not:
- cleaner class discrimination
- stronger token-selective signal formation

## Interpretation
This explains why the earlier local evidence kept stalling:
- `V4` can change raw geometry slightly
- but it does so by dampening the scoring surface
- the dampened surface does not reliably create better separation at the decision level

So the current blocker is not:
- threshold selection
- validation split choice
- another small local calibration tweak

The blocker is likely the phase-to-score coupling itself.

## Decision framework outcome
### Is a new mechanism-level variant justified later?
`Yes`, but not immediately.

The diagnostics justify a future mechanism-level variant only if it explicitly aims to:
- preserve or improve token sensitivity
- avoid score compression
- convert positional phase structure into discriminative score movement more directly

### Is more threshold-only or calibration-only work justified now?
`No`

### Should `V4` remain primary?
`No`

`V4` remains exploratory because its main measurable effect is score compression rather than better discrimination.

## Recommended next local track
Stay zero-credit and mechanism-oriented:
1. diagnose how phase changes propagate through the local circuit to the final weighted-excitation score
2. identify where dynamic range is being lost
3. define criteria for a future variant only after that coupling path is understood

## Bottom line
`V4` lowers token-to-score sensitivity almost everywhere without delivering a matching discrimination gain.
That is a mechanism warning, not a threshold-tuning opportunity.
