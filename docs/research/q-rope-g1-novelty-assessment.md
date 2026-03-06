# Q-RoPE Gate G1 Novelty and Publishability Assessment

## Date
2026-03-05

## Inputs
- `docs/research/prior-art-gap-map.md`
- `docs/research/q-rope-concept-note-v1.md`
- `docs/research/E001-discovery-and-publication-plan.md`

## Decision
`Proceed (with claim constraints)`

## Rationale
1. A clear method gap exists between current quantum positional strategies and a RoPE-style relative-phase formulation targeted for hybrid quantum query-key comparison.
2. Theoretical framing support exists from RoPE and group-action literature to justify a principled formulation section.
3. Publishability is plausible if novelty is scoped narrowly and experiments include matched baselines plus hardware-cost reporting.

## Mandatory claim constraints
1. Do not claim invention of positional encoding for quantum transformers.
2. Claim only the specific relative-phase design, theorem conditions, and benchmark protocol contributions.
3. Mark all unresolved external-validity questions as limitations.

## Mandatory experiment constraints for S004
1. Include no-PE, additive-PE, fixed-gate-PE, and Q-RoPE ablations.
2. Report task metrics with gate/depth/qubit and noise notes.
3. Use one strong architecture family first, then extend only if signal is positive.

## Residual risks
- Cross-paper comparability remains weak in current literature.
- Benchmark-scale skepticism is likely unless at least one nontrivial dataset family is included.
- Novelty overlap risk remains if language becomes too broad.

## Next step
Proceed to S003 and S004 under the above constraints.
