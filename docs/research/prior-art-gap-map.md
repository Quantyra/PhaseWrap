# Prior-Art Gap Map (S002)

## Purpose
Establish claim-level novelty baseline and publishability risks for Q-RoPE.

## Method
- Primary-source-first extraction.
- One row per relevant paper/method.
- Separate observed facts from internal inference.

## Claim-verified extraction table
| Ref ID | Work | Positional strategy | Relative-position mechanism | Overhead notes | Benchmark notes | Relevance to Q-RoPE |
| --- | --- | --- | --- | --- | --- | --- |
| P001 | QMSAN, arXiv:2403.02871 | Quantum positional encoding via fixed quantum gates inside circuit | No explicit RoPE-style multiplicative relative law statement | Authors state positional encoding is introduced without extra qubit resources | Text classification including Yelp/IMDb/Amazon; paper reports positional variant improves over non-positional variant | Strong fixed-gate PE comparator |
| P002 | QASA, arXiv:2504.05336 | Fixed sinusoidal positional encoding added to embeddings | Relative mechanism is not central claim | Hybrid stack: classical transformer blocks plus quantum-enhanced final block | Synthetic time-series tasks; reports faster convergence and better generalization than selected baselines | Additive PE comparator |
| P003 | HQViT, arXiv:2504.02730 | Whole-image amplitude encoding; reports no additional positional encoding | Not framed as RoPE-like relative phase | Claims low qubit/gate scaling and hybrid resource savings | Vision datasets with reported gains vs compared methods | No-PE/implicit positional handling comparator |
| P004 | Hybrid molecular transformer, arXiv:2502.19214 | Token + positional embeddings are included in classical path and quantum path; defines learnable positional encoding angles in PQC | Not a RoPE-style relative law claim | Uses `O(log d)` qubits for quantum attention path in its analysis | Molecular generation on QM9 with hybrid decoder | Learnable quantum positional-state comparator |
| P005 | RoFormer, arXiv:2104.09864 | Rotary position embedding in classical transformers | Explicitly positions RoPE as encoding absolute position while incorporating relative dependency in attention formulation | Classical transformer setting | Long-text classification experiments in paper | Core conceptual baseline for relative rotational encoding |
| P006 | Rethinking RoPE, arXiv:2504.06308 | Lie-group/Lie-algebra framework for RoPE | Derives validity conditions via relativity and reversibility | Theory-focused | Higher-dimensional RoPE theory and experiments | Strong mathematical bridge for quantum group-action formulation |
| P007 | GRAPE, arXiv:2512.07805 | Group-action positional framework unifying multiplicative and additive families | States exact relative law under group action formulations; includes RoPE as special case | Framework-level complexity discussion | Long-context modeling orientation | Strengthens formal group-action framing for Q-RoPE |
| P008 | Survey, arXiv:2504.03192 | Surveys PQC and QLA quantum transformer lines | Documents that current PQC transformer evidence is mostly small-scale and open scalability remains | Notes trainability/resource issues and benchmark inconsistency | Multi-domain synthesis over recent studies | External support for novelty/publishability risk framing |
| P009 | Quantum ViT for HEP, arXiv:2405.10284 | Hybrid quantum-classical ViT with quantum attention modules | Not framed as relative phase law | NISQ-aware hybrid simulation study | Quark-gluon classification | Additional comparator family for quantum attention architecture choices |
| P010 | Quantum Attention for ViT in HEP, arXiv:2411.13520 | Hybrid ViT with quantum orthogonal layers in attention | Not framed as RoPE-style relative law | Architecture-level enhancement | HEP vision benchmarks | Supplemental comparator and venue-fit relevance |

## Source-anchored evidence notes
- Taken from source:
  - QMSAN introduces fixed-gate quantum positional encoding and reports accuracy deltas between positional and non-positional variants on Yelp/IMDb/Amazon.
  - QASA applies sinusoidal positional encoding in its embedding pipeline.
  - HQViT states whole-image amplitude encoding without additional positional encoding.
  - The molecular hybrid transformer explicitly defines learnable positional encoding angles in a PQC pathway.
  - RoFormer and later RoPE theory works formalize relative behavior from rotational/group-action structures.
  - The 2025 survey states current quantum-transformer empirical evidence is mostly small-scale and highlights scalability/trainability/benchmark issues.
- Inferred for repo:
  - There is a publishable opening for a benchmarked, NISQ-conscious relative-phase positional mechanism that is explicitly designed and tested as a RoPE-analogue inside hybrid quantum query-key comparisons.

## Contradiction log
1. Complexity and speedup claims vary widely across papers and are often task/setup-specific.
2. Some papers report strong gains but use different baseline strengths and preprocessing pipelines, reducing cross-paper comparability.
3. The survey flags inconsistent benchmark standards, so novelty claims must avoid overgeneralizing isolated improvements.

## Publishability assessment (Gate G1 input)
- Strengths:
  - Clear comparator taxonomy: no-PE vs additive PE vs fixed-gate PE vs learnable quantum positional states.
  - Theory bridge exists from RoPE to group-action formalism, enabling a principled method section.
  - Reviewer-relevant NISQ constraints (qubits, depth, measurement overhead) can be made first-class evaluation metrics.
- Risks:
  - Reviewer challenge on novelty overlap if claim language is too broad.
  - Reviewer challenge on external validity if only one small benchmark family is used.
  - Reviewer challenge on fairness if classical baselines are not strong/equivalent.

## Gate G1 recommendation
- Decision: `Proceed (with claim constraints)`
- Required constraints:
  1. Claim novelty as a specific relative-phase formulation and benchmarking protocol, not as the first use of quantum positional information.
  2. Require matched-strength baselines and report hardware-cost metrics alongside task metrics.
  3. Keep first manuscript framed as method-plus-ablation evidence, with explicit external-validity limits.

## Sources
- QMSAN: https://arxiv.org/abs/2403.02871
- QASA: https://arxiv.org/abs/2504.05336
- HQViT: https://arxiv.org/abs/2504.02730
- Hybrid molecular transformer: https://arxiv.org/abs/2502.19214
- RoFormer: https://arxiv.org/abs/2104.09864
- Rethinking RoPE: https://arxiv.org/abs/2504.06308
- GRAPE: https://arxiv.org/abs/2512.07805
- Quantum Transformer Survey: https://arxiv.org/abs/2504.03192
- Quantum ViT (HEP): https://arxiv.org/abs/2405.10284
- Quantum Attention ViT (HEP): https://arxiv.org/abs/2411.13520
