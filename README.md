# Quantyra QRoPE Research

This repository is the planning and research operations hub for Quantyra's Quantum Rotational Positional Embeddings (QRoPE) program.

## Working titles
- Safest: `Phase-Based Relative Positional Encoding for Hybrid Quantum Transformers`
- Bolder: `Q-RoPE: Hardware-Efficient Relative Positional Encoding for Quantum Attention`

## Purpose
- Capture QRoPE research questions, constraints, and requirements.
- Translate research needs into epics and stories.
- Track decisions, evidence, and reproducible artifacts.
- Coordinate theory, experiments, and implementation planning.

## Protocols
Follow the protocols from the main `../Quantyra` repository. Additional QRoPE-specific protocols are defined here:
- `docs/protocols/research-charter.md`
- `docs/protocols/quantum-claims-and-evidence.md`
- `docs/protocols/experiment-reproducibility.md`

## Structure
- `docs/` - Research notes, process docs, and protocol docs
- `epics/` - Epic definitions
- `stories/` - Story definitions
- `templates/` - Standard templates for planning and evidence
- `logs/` - Checkpoint system and operational logs

## How to use
1. Start from an epic in `epics/` using `templates/EPIC_TEMPLATE.md`.
2. Create stories in `stories/` using `templates/STORY_TEMPLATE.md`.
3. Track progress and action state in `logs/checkpoint.json`.
4. Keep evidence and references up to date for each story.
5. Commit each completed story or distinct protocol step to git with a clear message.

## Current focus
- `epics/E001-quantum-rotational-positional-embeddings-foundation.md`
- `docs/research/q-rope-concept-note-v1.md`
