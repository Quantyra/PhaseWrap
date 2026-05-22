# PhaseWrap-RoPE Stage 96 Claim Card Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 96 packages the current strongest honest PhaseWrap-RoPE claim into a compact claim card.

It reads Stage 70, Stage 94, and Stage 95 artifacts, then emits the current claim, positive evidence, failure modes, unsupported claims, promotion-gate status, headline intervals, and next gate in one machine-readable artifact.

## Reviewer Command

```bash
python scripts/run_stage96_claim_card_audit.py
```

This writes:

- `logs/automated_stage_gates/stage96_claim_card_audit/manifest.json`
- `logs/automated_stage_gates/stage96_claim_card_audit/results.json`
- `logs/automated_stage_gates/stage96_claim_card_audit/summary.csv`

## Result

Stage 96 records `CLAIM_CARD_BOUND_STRONGEST_HONEST_CLAIM`.

Claim-card summary:

- strongest claim: PhaseWrap-RoPE is compact, auditable, and supported by bounded diagnostic evidence, but not by fair evidence for RoPE replacement;
- promotion gate: not ready;
- remaining failed requirement: `free_learned_phasewrap_original_retrieval_solve`;
- headline intervals: present through Stage 95;
- unsupported claims: replacement, superiority over RoPE in current fair matched transformer settings, PhaseWrap-specific content-key success, tiny-text implying original retrieval generalization, and production LM quality from bounded hardware/readout witnesses.

## Interpretation

Stage 96 does not expand the claim. It makes the current bounded claim harder to misquote by tying every positive statement to the recorded exclusions and failure modes.

## Claim Boundary

Supported:

- a no-credential claim-card package for the current strongest honest PhaseWrap-RoPE claim;
- a compact mapping from the claim to positive evidence, failure modes, unsupported claims, and next gate;
- a publication-facing guardrail artifact that preserves bounded wording from Stage 70/94/95.

Excluded:

- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that PhaseWrap-RoPE is currently better than RoPE in fair matched transformer settings;
- a claim that structural copy experts are standard free decoder-only language modeling;
- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage.

## Next Gate

Use the claim card when reporting the current research posture. Reopen promotion only after a free learned matched decoder/transformer artifact solves both original retrieval tasks with PhaseWrap-led methods or otherwise satisfies a predeclared non-phase-labeled promotion benchmark.
