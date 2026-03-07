# Q-RoPE Broader Local Redesign Question Selection v1

## Decision
The next broader zero-credit local redesign question is:

Can a joint local circuit-plus-readout redesign improve phase-to-score separability more reliably than fixed post-`RZ` mixing tweaks?

## Why this is the right next question
The recent evidence stack is aligned on one point:
- the bottleneck is not just thresholding
- not just variant phase magnitude
- not just a single fixed mixing layer
- not just the weighted readout

What failed:
- `V4` threshold/calibration refinement as a primary rescue path
- fixed post-`RZ` mixing preset tuning

What held up:
- local parity screening is more informative than weighted alone
- dynamic range is lost after `RZ`
- weighted readout is compressive, but observable replacement alone is not enough

That means the next question has to target both:
1. phase-to-amplitude conversion in the circuit
2. final score extraction in the readout

## Selected scope
Keep the next step narrow despite the broader question.

In scope:
- local only
- `V3` primary path
- parity-default local screening
- explicit circuit/readout redesign question

Out of scope:
- remote execution
- new variant naming
- broad parameter sweeps

## Recommended framing
Treat the next branch as:
- screening-path redesign

Not as:
- a new Q-RoPE algorithm
- a publication claim
- a replacement for the current main branch before evidence exists

## Concrete next branch direction
The best next story is to choose one narrowly scoped redesign family, for example:
- interference-sensitive readout with a slightly richer final measurement basis
- or a shallow circuit redesign that uses a stronger phase-to-amplitude conversion stage plus parity shadowing

The key is to avoid reopening multiple axes at once.

## Decision on branch direction
Preferred branch:
- local screening-path redesign centered on joint circuit-plus-readout coupling

Rejected for now:
- more fixed mixing presets
- more threshold-rule tuning
- reopening `V4`
- remote budget

## Bottom line
The next defensible move is no longer a tweak.
It is a broader but still local and zero-credit redesign question:
- redesign the phase-conversion path and readout together
- keep `V3` as the primary path
- do not reopen remote execution yet
