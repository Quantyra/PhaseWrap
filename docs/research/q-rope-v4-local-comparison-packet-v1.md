# Q-RoPE V4 Local Comparison Packet v1

## Scope
- Variants: `V3`, `V4`
- Datasets: `yelp`, `imdb`, `amazon`
- Seeds: `42`, `123`, `777`
- Backends:
  - `sim_local`
  - `sim_quantum_statevector`

## Execution status
- Completed as a zero-credit local packet
- Run artifacts stored under `logs/ablation_runs/` with `localcmp` and `qsimcmp` suffixes

## Important interpretation boundary
`sim_local` is not a valid `V3` vs `V4` discriminator in the current codebase.

Reason:
- the `sim_local` path uses the naive-Bayes branch in `run_real_experiment(...)`
- that branch does not use the quantum variant schedule
- therefore identical `V3` and `V4` results on `sim_local` are expected and should not be interpreted as stability evidence

The meaningful local comparison backend in this packet is `sim_quantum_statevector`.

## Statevector comparison summary

| Dataset | Variant | Mean Acc | Std Acc | Mean F1 | Std F1 | Worst Acc |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `yelp` | `V3` | 0.5417 | 0.1443 | 0.5926 | 0.1283 | 0.3750 |
| `yelp` | `V4` | 0.3333 | 0.2602 | 0.2963 | 0.3394 | 0.1250 |
| `imdb` | `V3` | 0.4167 | 0.1909 | 0.4720 | 0.0890 | 0.2500 |
| `imdb` | `V4` | 0.7083 | 0.0722 | 0.6667 | 0.0000 | 0.6250 |
| `amazon` | `V3` | 0.5417 | 0.0722 | 0.4683 | 0.1222 | 0.5000 |
| `amazon` | `V4` | 0.4167 | 0.0722 | 0.3016 | 0.0275 | 0.3750 |

## Decision against the S036 gate
S036 required:
1. `V4` lowers seed standard deviation vs `V3` on at least two local datasets
2. `V4` stays in the same rough mean-performance band as `V3`
3. `V4` does not introduce obvious new local regressions in worst-seed behavior

Current outcome on the meaningful local backend (`sim_quantum_statevector`):
- Criterion 1: `fail`
  - improved on `imdb`
  - unchanged on `amazon`
  - worse on `yelp`
- Criterion 2: `fail`
  - `V4` dropped materially on `yelp` and `amazon`
- Criterion 3: `fail`
  - worst-seed accuracy regressed on `yelp` and `amazon`

## Go / No-Go
- Decision: `NO-GO` for paid remote `V4` wave in the current form

## Why this is the correct decision
- The damped phase schedule is not yet robust enough to justify burning provider budget
- The local evidence is mixed and dataset-dependent rather than consistently stabilizing
- A paid remote wave now would test an underqualified variant rather than a credible stability improvement

## Recommended next step
1. tighten the local gate so only variant-sensitive backends are used for `V4` screening
2. redesign `V4` rather than spending remote credits on the current damped-only form

## Bottom line
`V4` is implemented and executable, but the current damped-only version did not earn a paid remote wave.
