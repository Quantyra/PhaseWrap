# PhaseWrap-RoPE Stage 11 Score Theory Analysis v1

Date: `2026-05-20`

## Purpose

Stage 11 turns the theory feedback into machine-verifiable artifacts. It analyzes the fixed `8/12` PhaseWrap-RoPE score without hardware submission, provider credentials, or learned-model training.

Artifacts:

- Manifest: `logs/automated_stage_gates/stage11_phasewrap_theory/manifest.json`
- Results: `logs/automated_stage_gates/stage11_phasewrap_theory/results.json`
- Alias summary: `logs/automated_stage_gates/stage11_phasewrap_theory/alias_summary.csv`
- Period-pair summary: `logs/automated_stage_gates/stage11_phasewrap_theory/period_pair_summary.csv`
- Residue score table: `logs/automated_stage_gates/stage11_phasewrap_theory/residue_score_table.csv`

Reproduce:

```bash
python scripts/run_stage11_phasewrap_theory.py
```

## Result

For the default period pair `(8, 12)`, the least common period is `24`. The score is invariant under joint translations of the two offsets, invariant to shifting either offset by `24`, and symmetric under sign reversal of the offset difference.

The score is therefore a periodic positional scoring rule over `(reference_delta - candidate_delta) mod 24`, not a unique long-context address. On the residue table there are `10` distinct score values after mirrored and zero-margin aliases are accounted for.

Context alias growth:

| Context length | Unique score count | Mean alias class size | Max alias class size |
| ---: | ---: | ---: | ---: |
| 24 | 10 | 2.400000 | 6 |
| 48 | 10 | 4.800000 | 12 |
| 96 | 10 | 9.600000 | 24 |
| 192 | 10 | 19.200000 | 48 |
| 384 | 10 | 38.400000 | 96 |
| 768 | 10 | 76.800000 | 192 |
| 1024 | 10 | 102.400000 | 257 |

Fourier analysis over the mod-24 residue table gives positive frequency support `[1, 2, 3, 5]`. This means the fixed score is exactly representable as a small classical periodic feature map over the least common period.

## Interpretation

Stage 11 strengthens the mathematical audit trail but narrows the claim. The `8/12` score is compact, deterministic, and easy to verify, but it has unavoidable aliases in long contexts. Any future RoPE-replacement claim must show that a transformer mechanism can use this periodic signal beneficially despite those aliases, or combine it with other features that resolve them.

The result supports continued study of PhaseWrap-RoPE as a positional scoring rule. It does not prove the `8/12` pair is globally optimal, does not prove transformer improvement, and does not provide quantum-advantage evidence.
