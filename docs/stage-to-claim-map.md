# Stage-To-Claim Map

Status: `REVIEWER_FRONT_DOOR`

This map separates the headline evidence from the full historical stage archive.

## Headline Path

| Claim question | Decisive stage(s) | Current result | Review command |
| --- | --- | --- | --- |
| Is the original phase-cued target tautological with respect to exposed periodic features? | Stage 5 | `lookup_mod24` and direct `m8*m12` features recover the original synthetic label exactly. | `python scripts/run_stage5_attention_baselines.py` |
| What is the exact structure of the fixed score? | Stage 11 | Fixed `(8, 12)` score has period `24`, `10` distinct residue values, mirror aliases, and Fourier support `[1, 2, 3, 5]`. | `python scripts/run_stage11_phasewrap_theory.py` |
| Does fixed PhaseWrap solve stricter non-phase-cued retrieval? | Stage 12 | RoPE-like and sinusoidal baselines solve; fixed PhaseWrap is weak. | `python scripts/run_stage12_ruler_retrieval.py` |
| Can assistance pipelines solve retrieval without isolating the positional method? | Stage 67, 74/75, 80/81, 82, 93/94/96 | Content-key, support-recovery, and support-routing paths repeatedly repair retrieval for `no_position` too; learned support-to-token binding remains bounded. | `python scripts/run_stage80_support_routed_token_selector_audit.py` |
| Do PhaseWrap-derived adapters reach bounded rank parity while losing calibration/probability? | Stage 219 | Top-1/MRR parity in Stage 30/32 bridges, with measured probability and ECE degradation versus RoPE. | `python scripts/run_stage219_rope_substitution_gate.py` |
| What is the hardware evidence? | Stage 216-218 | One frozen IBM Fez packet favors PhaseWrap on normalized readout-noise delta after known-state calibration. This is hardware-readout audit evidence only. | `python scripts/run_stage218_full_replacement_hardware_metric_interpreter.py` |

## Claim Boundary

| Supported | Not supported |
| --- | --- |
| Negative-results methodology around benchmark assistance confounds. | RoPE replacement. |
| Exact score theory for the fixed `(8, 12)` scalar. | Production transformer improvement. |
| Reproducible no-credential verification of saved artifacts. | Quantum advantage. |
| Bounded readout-audit interpretation of archived hardware packets. | Broad cross-backend hardware robustness. |
| A worked example of established shortcut/control-task/NoPE concerns. | Novel discovery of the general shortcut-learning warning. |

## Full Audit Pointers

- Reviewer start: [../REVIEWER_START.md](../REVIEWER_START.md)
- Methodology paper draft: [publication/phasewrap-methodology-paper-v1.md](publication/phasewrap-methodology-paper-v1.md)
- Prior-work novelty supplement: [publication/post-publication-novelty-and-prior-work-supplement-v1.md](publication/post-publication-novelty-and-prior-work-supplement-v1.md)
- Publication package verifier: `python -m qrope.verify_publication --profile public`
- Full logs: `logs/automated_stage_gates/`
- Full stage scripts: `scripts/run_stage*.py`
- Public API: [api/scoring.md](api/scoring.md)
