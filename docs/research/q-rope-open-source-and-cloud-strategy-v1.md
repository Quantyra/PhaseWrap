# Q-RoPE Open-Source and Cloud Strategy v1

## Date
2026-03-05

## Decision summary
1. Open-source the Q-RoPE algorithm code in phases.
2. Use photonic cloud platforms as primary execution path.
3. Use IBM Quantum as a secondary cross-hardware validation track, not the primary identity of the program.
4. Defer Xanadu Cloud from the active execution plan if its cloud access path is unavailable.

## Why open-source (recommended)
- Publishability: open code materially improves reviewer confidence and reproducibility.
- Credibility: novelty claims are easier to defend with transparent baselines and ablations.
- Adoption: easier external replication and citation.

## Open-source scope (phased)
### Phase A (immediate; recommended)
- Open:
  - Q-RoPE algorithm implementation
  - Baseline implementations (`no-PE`, additive, fixed-gate)
  - Configs, seeds, and evaluation scripts
  - Reproduction instructions
- Keep internal:
  - Any non-public datasets/keys/credentials
  - Internal cost contracts and cloud account metadata

### Phase B (after first stable ablation release)
- Open:
  - Hardware adapters that do not expose sensitive account details
  - Extended benchmark scripts

### Phase C (post-initial paper submission)
- Open:
  - Full training and evaluation pipeline with versioned release tags

## Suggested licensing posture
- Code: Apache-2.0 (research + commercial permissive default).
- Docs and figures: CC BY 4.0.
- Contributor workflow: lightweight CLA/DCO policy as needed.

## Cloud quantum strategy (Quantyra photonic bias aligned)
### Primary track: photonic cloud
- Quandela Cloud / Perceval:
  - Perceval `RemoteProcessor` supports remote QPU/simulator execution with token-authenticated access.
  - Quandela is default Perceval cloud provider.
- Xanadu photonic stack:
  - Treat as optional/future only.
  - Do not block current execution on Xanadu onboarding or cloud access.

### Secondary track: IBM Quantum
- Use as cross-platform comparator and robustness check.
- Platform operations must follow current IBM Quantum Platform model:
  - IBM Quantum Platform Classic (`quantum.ibm.com`) sunset occurred on 1 July 2025.
  - Runtime/primitives migration is required for current workflows.

## Platform recommendation matrix
| Role | Recommended platform | Why |
| --- | --- | --- |
| Primary research identity | Photonic (Quandela-first) | Aligns with Quantyra strategic bias and active available cloud path |
| Rapid ablation prototyping | Local simulators + Quandela cloud simulators | Cost control and reproducibility |
| External hardware triangulation | IBM Quantum (secondary) | Improves generality claims and reviewer confidence |

## Risk controls
1. Avoid hardware-overclaim: report platform-specific results separately.
2. Avoid lock-in: maintain backend interface abstraction in code.
3. Avoid reproducibility gaps: publish exact environment and execution metadata.

## Protocol action
- This decision is approved for S006 execution planning.
- Patent analysis remains secondary and non-blocking at this stage.

## Sources
- IBM platform migration/sunset:
  - https://docs.quantum.ibm.com/announcements/product-updates/2025-05-15-platform-deprecation
  - https://docs.quantum.ibm.com/migration-guides/qiskit-runtime
- Quandela cloud docs:
  - https://perceval.quandela.net/docs/v1.1/reference/runtime/remote_processor.html
  - https://perceval.quandela.net/docs/v1.1/reference/providers.html
  - https://perceval.quandela.net/
- Xanadu photonic hardware/cloud access references:
  - https://strawberryfields.ai/photonics/hardware/index.html
  - https://strawberryfields.ai/photonics/demos/tutorial_X8_demos.html
