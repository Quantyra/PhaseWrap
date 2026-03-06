# Experiment Reproducibility Protocol

## Purpose
Ensure all QRoPE experiments and analyses are reproducible.

## Required metadata per experiment
- Objective and hypothesis
- Inputs and datasets (with version)
- Environment (OS, runtime, key libraries)
- Commands and parameters
- Output artifacts and locations
- Validation checks

## Logging rules
- Store experiment logs under `logs/` with stable naming.
- Record random seeds for stochastic procedures.
- Note any non-deterministic behavior and expected variance ranges.

## Reproduction check
- Before closing an experiment story, run at least one clean rerun or provide a clear limitation note.
- Document reproduction status in story notes.
