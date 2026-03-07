# Q-RoPE State-Preparation Design v1

## Decision
Use a two-branch preparation scheme with matched content loaders and branch-specific positional phase action.

Branch definitions:
- branch `A` represents token-position pair `(x_i, i)`
- branch `B` represents token-position pair `(x_j, j)`

## Exact state-preparation target
For a future restart candidate, prepare:
- `|psi_i> = P(i) E(x_i) |0^q>`
- `|psi_j> = P(j) E(x_j) |0^q>`

Where:
- `E(x)` is the content loader
- `P(t)` is the positional phase family

## Design choice
Do **not** merge content and position into a single opaque encoder before comparison.

Reason:
- the whole point of the restart is to test whether relative phase is doing useful work
- if content and position are fused too early, we lose interpretability and cannot tell whether `P(i)^dagger P(j)` is the actual driver

## Content loader requirements
The content loader `E(x)` must be:
- identical across both branches
- deterministic
- shallow enough that positional phase remains interpretable

Allowed role:
- inject token identity or token-pair content into the branch state

Disallowed role:
- bake in absolute position information
- silently absorb the positional signal that the phase family is supposed to supply

## Positional phase requirements
The phase family `P(t)` must be:
- branch-local
- applied after content loading
- commuting within the chosen basis

Reason:
- the theorem target depends on relative operator structure:
  - `P(i)^dagger P(j) = P(j - i)`

Applying phase after content loading keeps the future comparison sensitive to relative phase between the two branches.

## Branch symmetry requirements
The two branches must be symmetric in structure:
- same qubit count
- same content-loader family
- same phase family
- different token and position inputs only

Reason:
- asymmetry in the branch structure would let the comparator pick up branch artifacts instead of relative-offset structure

## Synthetic-family instantiation
For the current synthetic task family:
- `x_i` and `x_j` should be derived from the synthetic pair text fields
- `i` and `j` should map directly from `left_pos` and `right_pos`

This keeps the future restart maximally aligned to the controlled offset-label construction.

## What remains explicit before comparison
Before the future comparator is applied, the proposal must preserve explicit access to:
- branch `A` content identity
- branch `B` content identity
- branch `A` position index
- branch `B` position index

That is the minimum interpretability requirement.

## Failure modes this structure is meant to avoid
This state-preparation design is chosen specifically to avoid:
1. content-position entanglement too early in the pipeline
2. branch asymmetry masquerading as relative-offset signal
3. loss of theorem interpretability before interference is even defined

## Constraint on the next story
The comparator/interference memo must assume:
- these two branches already exist as separately prepared states
- the comparison step is responsible for exposing relative phase

So the next story is not allowed to redefine state preparation implicitly.

## Bottom line
The future mechanism branch will stand or fall on whether the comparison step can turn these explicitly prepared branch states into a useful relative-phase contrast.
This memo fixes the branch structure so that question can be asked cleanly.
