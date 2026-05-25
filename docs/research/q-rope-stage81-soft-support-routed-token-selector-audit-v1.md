# QRoPE Stage 81 Soft Support-Routed Token Selector Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 81 tests whether Stage 80's hard support argmax can be softened without losing the phase-cued retrieval repair.

Instead of selecting one support class by hard argmax, Stage 81 routes the learned support probability distribution into farthest-congruent token selection. It still excludes metadata lookup, evaluation-time `reference_delta`, `target_pos`, and `target_delta`, and it keeps the fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparison frame.

Reviewer command:

```powershell
python scripts\run_stage81_soft_support_routed_token_selector_audit.py
```

## Result

Default run: five seeds, six methods, `examples_per_length=6`, 80 epochs, no failed runs.

| Task | Best method | Test top-1 | Mean target probability |
| --- | --- | ---: | ---: |
| `tiny_text_fact_qa` | `sinusoidal` | `1.000000` | `0.748539` |
| `phase_cued_retrieval` | `sinusoidal` | `1.000000` | `0.957496` |
| `exact_offset_passkey` | `sinusoidal` | `0.650000` | `0.340343` |

Decision:

`SOFT_SUPPORT_ROUTED_TOKEN_SELECTOR_SOLVES_PHASE_CUED_NOT_PROMOTION`

Mean phase-cued support accuracy: `1.000000`.

The phase-cued lane is solved by every tested method, including `no_position`, when the learned support distribution is routed to farthest-congruent token selection.

## Interpretation

Stage 81 strengthens the Stage 80 coupling result: the phase-cued repair does not require a hard support argmax, because the learned support probabilities are sharp enough to route token mass correctly.

It still does not support positional-method promotion. The repair is method-nonspecific; `no_position`, `sinusoidal`, `alibi`, `rope_relative`, `phasewrap_bias`, and `phasewrap_adapter` all reach phase-cued top-1 `1.000000`.

The strongest honest claim remains bounded. Stage 81 supports the claim that recovered support can be coupled to token selection in a compact diagnostic, but it does not prove that a matched decoder-only transformer learns the routing or that PhaseWrap replaces RoPE.

## Next Gate

The next useful gate is a learned matched decoder-only path that must learn support-to-token routing from standard inputs and training loss without a hard-coded farthest-congruent selector.
