# Q-RoPE Symbolic Insufficiency Dual-Atlas Bilinear Residual Gate Decision v1

Date: 2026-03-11
Stories: S746

## Decision
- the dual-atlas bilinear residual family is specific enough for one bounded implementation-planning step
- code remains closed in this step

## Why
- the plain dual-atlas family and the dual-atlas residual-gating family have both already lost cleanly to the witness
- the bilinear residual extension is materially stronger while staying globally frozen and auditable
- the remaining ambiguity is implementation shape, not conceptual scope

## Operational Consequence
- next valid move is one implementation-planning memo only
- do not execute the control until lattice size, chart rules, residual definitions, bilinear definitions, and bilinear interaction set are frozen in that plan
