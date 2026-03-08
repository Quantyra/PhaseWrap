# Q-RoPE First Relational Witness Packet v1

## Scope
- Story: `S158`
- Dataset: `synthetic_sector_parity_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Variants:
  - `V0`
  - `V_future_relational_witness`

## Per-seed results
| Variant | Seed | Accuracy | F1 | Task contrast mean | Anti-collapse | Forbidden inputs absent |
| --- | --- | ---: | ---: | ---: | --- | --- |
| `V0` | `42` | `0.578125` | `0.550000` | `n/a` | `n/a` | `n/a` |
| `V0` | `123` | `0.484375` | `0.459016` | `n/a` | `n/a` | `n/a` |
| `V0` | `777` | `0.500000` | `0.418182` | `n/a` | `n/a` | `n/a` |
| `V_future_relational_witness` | `42` | `1.000000` | `1.000000` | `-0.006262` | `true` | `true` |
| `V_future_relational_witness` | `123` | `1.000000` | `1.000000` | `-0.004593` | `true` | `true` |
| `V_future_relational_witness` | `777` | `1.000000` | `1.000000` | `-0.005731` | `true` | `true` |

## Packet means
| Variant | Mean accuracy | Mean F1 | Mean task contrast |
| --- | ---: | ---: | ---: |
| `V0` | `0.520833` | `0.475733` | `n/a` |
| `V_future_relational_witness` | `1.000000` | `1.000000` | `-0.005529` |

## Primary read
The relational witness branch strongly beat `V0` on the approved packet.

## Why this still needs discipline
This is a positive result, but it is still the first bounded packet.

What is already strong:
- multi-seed perfect accuracy and F1
- no forbidden inputs
- anti-collapse passed on all seeds
- coefficient audit is available

What still needs hardening:
- determine whether the head is using the intended relational evidence cleanly
- confirm the result is not dependent on one specific split policy or an unrecognized proxy inside the allowed feature set

## Correct interpretation
- `positive packet`
- `branch survives`
- `do not broaden yet`

## Bottom line
This is the strongest positive restart result in the repository so far.
The next correct move is validity hardening, not immediate expansion.
