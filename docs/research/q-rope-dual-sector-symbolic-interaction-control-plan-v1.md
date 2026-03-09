# Q-RoPE Dual-Sector Symbolic-Interaction Control Plan v1

## Scope
- Story: `S192`
- Task: `synthetic_dual_sector_agreement_binary`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Candidate:
  - `V_future_relational_witness_dual`
- New control:
  - `V_control_symbolic_dual_interaction`

## Why a stronger control is needed
The active witness branch has now survived:
- slot swap
- token renaming
- meaningful pair reindexing

The main unresolved question is no longer robustness.
It is fairness against a stronger classical relational baseline.

## Control family
Use one bounded symbolic control with:
- explicit sector-pair interaction terms
- logistic-regression-equivalent head only
- no hidden layers
- no token identity
- no absolute position
- no numeric offsets

## Exact feature schema
Use one-hot features for the full sector pair:
- `pair_P_small__P_small`
- `pair_P_small__P_large`
- `pair_P_small__N_small`
- `pair_P_small__N_large`
- `pair_P_large__P_small`
- `pair_P_large__P_large`
- `pair_P_large__N_small`
- `pair_P_large__N_large`
- `pair_N_small__P_small`
- `pair_N_small__P_large`
- `pair_N_small__N_small`
- `pair_N_small__N_large`
- `pair_N_large__P_small`
- `pair_N_large__P_large`
- `pair_N_large__N_small`
- `pair_N_large__N_large`

Exactly one feature is active per sample.

## Why this control is fair
It is stronger than the current additive symbolic baseline because it can represent sector-pair interactions directly.

It is still bounded because it uses:
- only sector identity
- no lexical content
- no numeric offsets
- no hidden capacity

## Exact packet
Rerun the same fixed six-run packet:
- witness vs stronger interaction control
- seeds `42`, `123`, `777`
- no other changes

## Interpretation rule
### Pass for witness uniqueness
The branch gets materially stronger if:
- the witness still stays ahead of the stronger control

### Failure of uniqueness, not necessarily of utility
If the stronger control matches the witness:
- the branch remains a valid internal mechanism result
- but the uniqueness story weakens sharply

## Bottom line
This is the correct next pressure test.
It asks whether the branch beats a fairer symbolic relational baseline without opening any new task or remote path.
