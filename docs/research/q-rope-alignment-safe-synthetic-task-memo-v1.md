# Q-RoPE Alignment-Safe Synthetic Task Memo v1

## Purpose
Define the next memo-level research angle after the archived pair-state branch:
- preserve a relational synthetic setting
- remove the direct sign-to-label shortcut
- keep the task falsifiable before any future implementation restarts

## Problem with the current synthetic family
The current `synthetic_offset_binary` family labels examples by the sign of the relative offset.

That was useful for early mechanism checks, but it created a structural risk:
- any representation that makes signed sectors explicit can align too directly with the target

The pair-state branch exposed that risk clearly.

## New angle
The next synthetic family should still be relational, but its label should be:
- derived from a relation over offset sectors
- not equal to the sign of the offset itself

## Best candidate family
- `sector-parity relational classification`

Example design principle:
- keep the same four sectors:
  - `P_small`
  - `P_large`
  - `N_small`
  - `N_large`
- define the label by a cross-sector rule such as:
  - positive for `P_small` or `N_large`
  - negative for `N_small` or `P_large`

Why this is the best next memo angle:
- it preserves relational structure
- it breaks the old direct sign shortcut
- it reuses the existing sector language
- it directly pressure-tests whether future pair-state-like ideas are learning relation or just sign

## What this does not mean
This is not approval for implementation.

It is only a preserved design direction for a future restart brief.

## Success condition for a future restart
A future branch using an alignment-safe task family should only be considered credible if:
- it beats `V0`
- it remains multi-seed stable
- and its advantage cannot be reduced to the old sign-label alignment

## Bottom line
The strongest next memo-level angle is not another comparator tweak.

It is a new synthetic task family that keeps relational structure while removing the direct sign-label shortcut exposed by the pair-state validity control.
