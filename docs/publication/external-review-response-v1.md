# External review response v1

Status: `CLAUDE_REVIEW_ACTIONED_INITIAL_PASS`

Date: `2026-05-18`

## High-priority corrections made

| Review issue | Response |
| --- | --- |
| Provisional application number looked inconsistent with USPTO provisional series conventions. | Public wording now uses the basic patent-pending statement and application number without extra receipt identifiers. |
| Filing date appeared future-dated. | Public wording no longer attempts to prove filing chronology; it now uses the basic patent-pending statement and application number. |
| Hardware run occurred before the USPTO receipt. | Public wording now decouples the evidence record from patent-status chronology. |
| Product-state witness was overframed as quantum evidence. | README and paper now state that the current Stage 4 circuit is a product-state angle-encoding/readout witness with no entangling gate, and that it is not evidence of entanglement, quantum speedup, or nonclassical interference. |
| Thresholds `cos(pi/4)` and `cos(pi/6)` lacked motivation. | Paper now explains that these are one-step angular thresholds for periods 8 and 12. |
| Control condition was undefined. | Paper now defines the additive single-band readout control and the cross-band product witness. |
| Reproducibility was really recomputation. | Paper now distinguishes saved-count recomputation from independent replication. |
| README lacked quickstart. | README now includes a no-credential local method check, verifier command, expected verifier output, and reviewer path. |
| Paper referenced verifier/evidence artifacts that were not staged for public review. | The public evidence bundle is prepared for publication: `src/qrope/automated_stage_gates.py`, `scripts/verify_stage4_hardware_packet.py`, and Stage 4 JSON packet files under `logs/automated_stage_gates/stage4_hardware_packet/`. |
| AGENTS.md rendered a literal `\r\n`. | Fixed. |

## Not yet done

- Publish the completed hardware comparison report in the public evidence bundle.
- Move internal process/governance materials into a cleaner public structure.
- Wait for CI to complete on GitHub and respond to any failures.
- Optional archival release and DOI metadata, if later desired.

These remaining items require new execution, repo restructuring, or external publication steps and should not be represented as complete.
