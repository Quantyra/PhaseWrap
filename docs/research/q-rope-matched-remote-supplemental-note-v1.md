# Q-RoPE Matched Remote Supplemental Note v1

## Fixed slice definition
- Dataset: `yelp`
- Seeds: `42`, `123`, `777` completed on both providers
- Slice policy: balanced 12-sample remote slice from `limit_remote_samples(...)`
- Variants: `V0`, `V2`, `V3`
- Backends: `sim_quandela_remote`, `ibm_runtime_remote`

## Results

| Seed | Backend | Variant | Accuracy | F1 | Train Loss | Eval Loss | Wall Time (s) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 42 | Quandela `sim:slos` | V0 | 0.3333 | 0.0000 | 0.6419 | 0.8768 | 250.70 |
| 42 | Quandela `sim:slos` | V2 | 0.6667 | 0.0000 | 0.6643 | 0.8366 | 247.30 |
| 42 | Quandela `sim:slos` | V3 | 0.6667 | 0.0000 | 0.6532 | 0.8514 | 283.66 |
| 42 | IBM Runtime | V0 | 0.3333 | 0.0000 | 0.8294 | 0.8704 | 28.23 |
| 42 | IBM Runtime | V2 | 0.3333 | 0.0000 | 1.2705 | 0.8443 | 27.04 |
| 42 | IBM Runtime | V3 | 0.6667 | 0.0000 | 0.9168 | 0.6954 | 23.89 |
| 123 | Quandela `sim:slos` | V0 | 0.0000 | 0.0000 | 0.6688 | 0.8709 | 234.50 |
| 123 | Quandela `sim:slos` | V2 | 1.0000 | 0.0000 | 0.6475 | 0.8260 | 240.87 |
| 123 | Quandela `sim:slos` | V3 | 0.6667 | 0.0000 | 0.6774 | 0.8515 | 237.86 |
| 123 | IBM Runtime | V0 | 1.0000 | 0.0000 | 0.5268 | 0.2948 | 27.92 |
| 123 | IBM Runtime | V2 | 0.3333 | 0.0000 | 0.7791 | 0.7549 | 28.18 |
| 123 | IBM Runtime | V3 | 0.0000 | 0.0000 | 1.1465 | 1.1146 | 30.08 |
| 777 | Quandela `sim:slos` | V0 | 1.0000 | 0.0000 | 0.6852 | 0.8100 | 251.41 |
| 777 | Quandela `sim:slos` | V2 | 0.3333 | 0.0000 | 0.6336 | 0.8570 | 212.50 |
| 777 | Quandela `sim:slos` | V3 | 0.3333 | 0.0000 | 0.6574 | 0.8480 | 247.59 |
| 777 | IBM Runtime | V0 | 0.0000 | 0.0000 | 1.1579 | 1.5725 | 276.36 |
| 777 | IBM Runtime | V2 | 0.3333 | 0.0000 | 0.9550 | 1.0114 | 277.70 |
| 777 | IBM Runtime | V3 | 0.6667 | 0.0000 | 0.8939 | 0.4477 | 277.43 |

## Readout
- Across the full matched 3-seed packet, both providers are clearly seed-sensitive.
- Quandela rank order by seed:
  - `42`: `V2 = V3 > V0`
  - `123`: `V2 > V3 > V0`
  - `777`: `V0 > V2 = V3`
- IBM rank order by seed:
  - `42`: `V3 > V2 = V0`
  - `123`: `V0 > V2 > V3`
  - `777`: `V3 > V2 > V0`
- So the remote evidence is now strong enough to reject any simple, stable cross-provider narrative on this slice.
- Absolute loss values are not directly comparable because the backend circuit families differ.
- Wall-time asymmetry is unstable across runs: some IBM runs were much faster than Quandela, while the seed `777` IBM jobs were materially slower due to backend queue/runtime conditions.

## Claim boundary
- This is matched supplemental evidence, not a publication-grade cross-hardware comparison.
- The provider circuits are not identical and should not be framed as a strict hardware bake-off.
- The current evidence is sufficient to say the remote picture is unstable across seeds and provider conditions.
- The next defensible step is analysis/synthesis of this 3-seed packet before spending more credits on broader dataset coverage.
