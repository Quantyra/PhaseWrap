# Q-RoPE Internal Recommendation Memo v1

Date: 2026-03-12
Stories: S908

## BLUF
Recommendation: `CONTINUE AT LOW INTENSITY`, not `SUNSET`, and not `ESCALATE`.

## Decision
- Do not sunset the line.
- Do not escalate into hardware or externalization.
- Preserve the line as a low-intensity internal mechanism program with a high bar for any new execution.

## Why Not Sunset
1. The repo now contains one standing internal benchmark result that survived a long bounded fairness ladder.
2. That result also survived two bounded transfer families under hardening.
3. Earlier phases of the repo were dominated by null or collapsing branches; this line is different enough to justify preservation.

## Why Not Escalate
1. No hardware evidence exists for the current strongest line.
2. Transfer evidence is still bounded to two task families.
3. The current result is still best interpreted as an internal mechanism result, not an applied or external claim.

## Recommended Operating Mode
- keep the current witness as the standing internal benchmark
- require memo-level approval before any new execution line
- prefer theory and task-design work over new packet execution by default
- require materially different transfer families for future execution

## Resource Guidance
- engineering: low
- cloud/hardware budget: zero
- research attention: selective
- documentation upkeep: maintain current package as reference material

## Explicit No-Go Zones
- no default same-family fairness escalation
- no hardware execution by default
- no publication packaging
- no NISQ usefulness claims

## Explicit Go Conditions
Open a new execution line only if at least one is true:
1. a third materially different transfer family is specified and approved
2. a theory-backed branch creates a substantially different falsifiable question
3. leadership explicitly prioritizes this line over competing research programs

## Program Status
- standing benchmark: preserved
- bounded transfer: preserved
- hardware: blocked
- externalization: blocked
- theory/reporting: ready
