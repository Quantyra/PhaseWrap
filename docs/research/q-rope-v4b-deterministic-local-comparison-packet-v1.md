# Q-RoPE V4b Deterministic Local Comparison Packet v1

## Scope
- Backend: `sim_quantum_statevector`
- Variants: `V3`, `V4`, `V4b`
- Datasets: `yelp`, `imdb`, `amazon`
- Seeds: `42`, `123`, `777`
- Credit usage: `0`

## Result
After fixing deterministic local feature encoding, the local packet became reproducible.

But it also revealed a deeper issue:
- `V3`, `V4`, and `V4b` produced identical aggregate outcomes on every dataset and seed in the deterministic packet

## Deterministic packet summary

| Dataset | Variant | Mean Acc | Std Acc | Mean F1 | Std F1 | Worst Acc |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `amazon` | `V3` | 0.4583 | 0.1909 | 0.4405 | 0.1688 | 0.2500 |
| `amazon` | `V4` | 0.4583 | 0.1909 | 0.4405 | 0.1688 | 0.2500 |
| `amazon` | `V4b` | 0.4583 | 0.1909 | 0.4405 | 0.1688 | 0.2500 |
| `imdb` | `V3` | 0.7083 | 0.0722 | 0.7071 | 0.1202 | 0.6250 |
| `imdb` | `V4` | 0.7083 | 0.0722 | 0.7071 | 0.1202 | 0.6250 |
| `imdb` | `V4b` | 0.7083 | 0.0722 | 0.7071 | 0.1202 | 0.6250 |
| `yelp` | `V3` | 0.2500 | 0.1250 | 0.2315 | 0.2228 | 0.1250 |
| `yelp` | `V4` | 0.2500 | 0.1250 | 0.2315 | 0.2228 | 0.1250 |
| `yelp` | `V4b` | 0.2500 | 0.1250 | 0.2315 | 0.2228 | 0.1250 |

## Interpretation
This does **not** mean the variants are proven equivalent.

It means the current local statevector screening setup is not discriminating between these positional variants at the decision level.

## Likely reason
The current one-measurement local circuit is too weakly coupled to the positional phase differences we are injecting.

So the gate has shifted:
- before S044, the local packet was invalid because it was nondeterministic
- after S044, it is reproducible, but it is not discriminative

## Decision
- Decision: `NO-GO` for remote `V4b` wave based on current local gate

Reason:
- a local gate that cannot distinguish `V3` from `V4` from `V4b` is not a credible promotion filter

## Required next step
Strengthen the local quantum screening circuit so positional-phase differences can actually affect the readout used for evaluation.

## Bottom line
The reproducibility bug is fixed.
The next blocker is local discriminability, not local determinism.
