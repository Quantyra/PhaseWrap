# Q-RoPE Concept Note v1

## Working title options
- Safest: `Phase-Based Relative Positional Encoding for Hybrid Quantum Transformers`
- Bolder: `Q-RoPE: Hardware-Efficient Relative Positional Encoding for Quantum Attention`

## Core thesis
Classical RoPE injects position through rotations that induce a relative-position structure in attention. A comparable, standardized relative-phase mechanism is not yet established as a benchmarked default in hybrid quantum attention workflows. This project targets that gap with a NISQ-aware design.

## Primary research question
Can a RoPE-like relative phase encoding improve hybrid quantum attention under NISQ constraints without increasing qubit count or circuit depth too much?

## Problem framing
Observed positional strategies in related quantum attention work include:
- additive sinusoidal input positional signals;
- fixed Rx positional gates;
- learned positional quantum states or angles;
- architecture choices with limited or no explicit positional encoding.

The missing piece is a positional mechanism where relative offset emerges inside query-key comparison through multiplicative phase action, rather than from one-time additive input features.

## Proposed method
Define token encoding and positional unitary:
- Token encoder: `E(x_i)`
- Position unitary candidate family: `P(i) = tensor_l RZ(omega_l * i)` (or paired-rotation analog)

Construct query and key states:
- `|q_i> = U_q P(i) E(x_i) |0>`
- `|k_j> = U_k P(j) E(x_j) |0>`

Use overlap estimation for attention similarity (implementation-specific estimator chosen in S004).

## Theoretical target
With tied/compatible phase blocks, aim to show:
- `P(i)^dagger P(j) = P(j - i)`, so positional contribution depends on relative displacement.
- Overlap stability is preserved under shallow phase rotations.
- Cheapest implementation uses single-qubit gates and no auxiliary positional qubits.

## Novelty claim boundary (draft)
We introduce a relative-phase positional encoding for hybrid quantum attention that places position as a shallow unitary action inside query-key comparison, targeting RoPE-like relative-position inductive bias with NISQ-friendly overhead.

## Experiment program (minimum publishable unit)
1. Use one hybrid architecture and isolate positional effect.
2. Compare at least:
- no positional encoding;
- additive sinusoidal baseline;
- fixed-gate positional baseline;
- proposed Q-RoPE relative-phase method.
3. Report:
- task metric(s) by dataset;
- gate count and depth;
- noise robustness (if simulator/hardware path supports it).

## Open items from CSO pitch
- Final benchmark family selection between QMSAN-style, QASA-style, or both.
- Final source list and claim-level citation locking (handled in S002).
- Cleanup of trailing partial text in initial pitch draft before external circulation.
