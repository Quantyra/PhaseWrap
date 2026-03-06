# E001 Discovery and Publication Plan

## Objective
Run a discovery-first research cycle for Q-RoPE that prioritizes:
1. Novelty defensibility
2. Publishability potential
3. Reproducible evidence quality

Patents are tracked as a secondary stream and do not gate initial scientific planning.

## Date and scope
- Date: 2026-03-05
- Scope: E001 stories S002-S005

## Research hypothesis (working)
Relative-phase positional encoding inside hybrid quantum query-key comparison can provide measurable gains over additive/fixed positional baselines while maintaining NISQ-feasible overhead.

## Discovery track structure
### Track A: Official literature review (primary sources first)
- Corpus class A (must-read):
  - QMSAN: https://arxiv.org/abs/2403.02871
  - QASA: https://arxiv.org/abs/2504.05336
  - HQViT: https://arxiv.org/abs/2504.02730
  - RoFormer (RoPE origin): https://arxiv.org/abs/2104.09864
  - Rethinking RoPE (Lie/group framing): https://arxiv.org/abs/2504.06308
  - GRAPE (group-action positional framework): https://arxiv.org/abs/2512.07805
- Corpus class B (supporting): selected benchmarking/survey papers with direct methodological relevance.
- Exclude tertiary summaries unless used only for navigation.

### Track B: Novelty mapping
- Build claim table:
  - Existing method class (additive, fixed-gate, learned-state, none)
  - Where position enters pipeline
  - Relative-position law explicit or implicit
  - Qubit and depth overhead
  - Reported tasks and benchmark quality
- Define novelty boundary:
  - What is truly new
  - What is adaptation of known ideas
  - What cannot yet be claimed

### Track C: Publishability assessment
- Venue-fit scan (quantum ML, hybrid systems, applied ML tracks).
- Minimum publishable unit:
  - one architecture family
  - ablation with no-PE/additive/fixed/Q-RoPE
  - performance + gate/depth + noise notes
- Reviewer-risk forecast:
  - novelty-overlap objections
  - benchmark-size objections
  - NISQ realism objections

### Track D: Secondary patent sanity pass
- Run after novelty memo draft.
- Goal: flag obvious collision risks, not lead research direction.

## Deliverables and gating
1. `docs/research/prior-art-gap-map.md` (S002)
2. `docs/research/q-rope-formalization-v1.md` (S003)
3. `docs/research/q-rope-experiment-plan-v1.md` (S004)
4. `docs/research/q-rope-novelty-decision-memo-v1.md` (S005)

Gate decisions:
- Gate G1 (post-S002): novelty appears plausible -> continue or revise.
- Gate G2 (post-S003/S004): theory + experiment plan are coherent -> continue or revise.
- Gate G3 (post-S005): publishability recommendation = Proceed / Revise / Hold.

## Claim hygiene rules
- Every high-impact claim must be tagged:
  - `Taken from source`
  - `Inferred for repo`
- Claims without direct support remain provisional and cannot appear in external-facing abstracts.

## Execution cadence
- Daily: source extraction and gap-map updates.
- Every 2 stories: novelty risk checkpoint.
- Epic checkpoint update after each story milestone.
