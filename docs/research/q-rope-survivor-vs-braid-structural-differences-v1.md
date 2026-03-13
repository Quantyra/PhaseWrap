# Q-RoPE Survivor vs Braid Structural Differences v1

Date: 2026-03-12
Stories: S984

## Purpose
Make the surviving-transfer versus `braid` distinction operational enough to guide future transfer screening.

## Survivor Cluster
- `path`
- `loop-closure`
- `fork-join`
- `relay-binding`

## Boundary Case
- `braid`

## Difference Table
### Delayed relational dependence
- survivors: yes
- braid: weaker under deeper perturbation

### Multi-step accumulation
- survivors: explicit and necessary
- braid: present, but appears compressible after deeper reindexing

### Recombination with nontrivial state retention
- survivors: yes
- braid: present, but not stable enough to resist symbolic recovery

### Failure under deeper `pair_reindex`
- survivors: no
- braid: yes

### Likely compact symbolic recovery path
- survivors: not observed within frozen fairness family
- braid: observed at the deeper hardening boundary

## Screening Consequence
A new transfer family should be rejected before implementation if its relational target can plausibly be rewritten as:
- a shallow ordering summary,
- a reindex-stable compact tuple summary,
- or a bounded additive/quadratic recovery from declared summaries after deeper perturbation.

A new transfer family is worth memo-level advancement if it instead requires:
- delayed binding,
- path accumulation,
- closure or recombination with retained latent state,
- and continued non-compressibility under hypothetical deeper reindexing.

## Internal Recommendation
Treat `braid` as the negative exemplar in future screening. A candidate that looks too structurally close to `braid` should fail before code is reopened.
