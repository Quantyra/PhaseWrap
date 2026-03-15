# Q-RoPE Successor Key-Query Offset Selection Hardening Cycle Synthesis v1

## BLUF
- `synthetic_positional_key_query_offset_selection_response` survived the full bounded hardening cycle.
- The witness stayed ahead of the bounded symbolic control on mean `mae` and mean `rank_correlation` in the base packet and in each retained hardening packet.
- The line should now be treated as preserved successor-class evidence rather than as an active perturbation branch.

## Packet Means
- base:
  - witness: `mae 0.050993`, `rank_correlation 0.571859`
  - control: `mae 0.077298`, `rank_correlation -0.012068`
- `token_permutation=cdab`:
  - witness: `mae 0.043415`, `rank_correlation 0.503784`
  - control: `mae 0.052165`, `rank_correlation 0.302508`
- `pair_reindex=1`:
  - witness: `mae 0.058901`, `rank_correlation 0.582215`
  - control: `mae 0.082388`, `rank_correlation -0.045844`
- `slot_swap=1`:
  - witness: `mae 0.067198`, `rank_correlation 0.503286`
  - control: `mae 0.082179`, `rank_correlation 0.310856`
- `pair_reindex=7`:
  - witness: `mae 0.043087`, `rank_correlation 0.488714`
  - control: `mae 0.057999`, `rank_correlation 0.107130`
