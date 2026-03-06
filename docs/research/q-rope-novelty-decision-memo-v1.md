# Q-RoPE Novelty Decision Memo v1 (S005)

## Date
2026-03-05

## Decision
`Proceed` with scoped novelty and publishability positioning.

## Basis
- S002 prior-art mapping indicates a gap in benchmarked, RoPE-analogue relative-phase methods inside hybrid quantum query-key comparison.
- S003 defines theorem-condition scaffolding and explicit failure cases.
- S004 defines a controlled ablation protocol with matched baselines and hardware-cost reporting.

## Allowed claims
1. We propose a relative-phase positional encoding method for hybrid quantum attention.
2. We provide explicit conditions under which positional contribution depends on relative offset.
3. We provide a NISQ-conscious ablation protocol comparing no-PE, additive PE, fixed-gate PE, and Q-RoPE.
4. We demonstrate remote execution feasibility on both a photonic provider path and an IBM Runtime comparator path, while observing strong seed/provider sensitivity on the current matched slice.

## Disallowed claims
1. "First positional encoding for quantum transformers."
2. "Universal improvement across domains."
3. "Hardware-agnostic superiority" without direct hardware evidence.
4. "Stable remote superiority" on the basis of the current 3-seed matched packet.
5. "Cross-provider agreement" on the basis of the current remote packet.

## Publishability view
- Current status: `Promising but conditional`
- Why promising:
  - Clear gap framing and strong baseline taxonomy.
  - Theory-plus-experiment story is coherent.
- Why conditional:
  - Evidence currently planning-heavy; empirical results still required.
  - External-validity scope should remain narrow in first manuscript.
  - Remote evidence now exists, but it is unstable and should be framed as boundary-setting rather than validating broad superiority.

## Reviewer objection forecast
1. Novelty overlap with prior quantum positional methods.
  - Response: narrow claim boundary and explicit comparator matrix.
2. Small benchmark scale.
  - Response: frame as minimum publishable unit and publish extension plan.
3. NISQ practicality concerns.
  - Response: report gate/depth/qubit/shot costs and noise sensitivity.

## Patent posture (secondary)
- Patent search remains secondary and non-blocking for research planning.
- Perform a targeted patent sanity pass after first positive ablation signal.

## Next recommended action
Tighten publication-facing claims against the current remote packet and keep empirical framing explicitly bounded.
