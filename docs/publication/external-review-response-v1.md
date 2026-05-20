# External review response v1

Status: `CLAUDE_REVIEW_ACTIONED_INITIAL_PASS`

Date: `2026-05-18`

## High-priority corrections made

| Review issue | Response |
| --- | --- |
| Provisional application number looked inconsistent with USPTO provisional series conventions. | Public wording changed to conservative acknowledgement-receipt language. `docs/publication/patent-status-note-v1.md` now records that the Electronic Acknowledgement Receipt lists `64/068,121`, while USPTO MPEP 503 lists provisional series codes as `60/` through `63/`; final Filing Receipt review remains pending. |
| Filing date appeared future-dated. | The current repo date is `2026-05-18`; the receipt date is not future-dated as of this response. Public wording now uses the concrete receipt timestamp. |
| Hardware run occurred before the USPTO receipt. | `docs/publication/patent-status-note-v1.md` now separates the internal hardware execution timeline, USPTO receipt timeline, and later public release timeline. |
| Product-state witness was overframed as quantum evidence. | README and paper now state that the product-state Stage 4 circuit is an angle-encoding/readout witness with no entangling gate, and that it is not evidence of entanglement, quantum speedup, or nonclassical interference. The repository now separately reports an entangling CX witness family, still with bounded packet/backend/date/calibration-specific claims only. |
| Thresholds `cos(pi/4)` and `cos(pi/6)` lacked motivation. | Paper now explains that these are one-step angular thresholds for periods 8 and 12. |
| Control condition was undefined. | Paper now defines the additive single-band readout control and the cross-band product witness. |
| Reproducibility was really recomputation. | Paper now distinguishes saved-count recomputation from independent replication. |
| README lacked quickstart. | README now includes a no-credential local method check, verifier command, expected verifier output, and reviewer path. |
| Paper referenced verifier/evidence artifacts that were not staged for public review. | The public evidence bundle is prepared for publication: `src/qrope/automated_stage_gates.py`, `scripts/verify_stage4_hardware_packet.py`, `scripts/verify_stage4_hardware_sweep.py`, Stage 4 JSON packet files under `logs/automated_stage_gates/stage4_hardware_packet/`, and a provider-aware sweep manifest that passes for active IBM Fez product-state, Amazon Braket/Rigetti product-state, IBM Fez CX, and Amazon Braket CX records on Rigetti Cepheus, IQM Garnet, and IQM Emerald while listing additional IBM targets as deferred and IonQ as an excluded unavailable target. |
| Default packet and sweep evidence paths could be confused. | `stage4_hardware_packet/` remains the default single-packet reviewer path, and the same IBM Fez 2026-05-17 pass is also preserved under `stage4_hardware_packet_ibm_fez_20260517_pass/`; the sweep manifest points to the immutable named directory. |
| CI did not run the full unit suite or check README verifier drift. | CI now runs the full unit suite, skips optional Perceval-dependent tests when Perceval is unavailable, and checks the README expected single-packet verifier summary against the actual verifier output. |
| AGENTS.md rendered a literal `\r\n`. | Fixed. |

## Not yet done

- Mint a release DOI/archive after final public release tagging.
- Move internal process/governance materials into a cleaner public structure.
- Wait for CI to complete on GitHub and respond to any failures.
- Post an arXiv/OSF preprint and mint a Zenodo DOI.
- Add stronger baselines: 24-way lookup on `(reference_delta - candidate_delta) mod 24`, classical `m8`/`m12`/`m8*m12`, small MLP or regression tree on exposed deltas, and RoPE/ALiBi/sinusoidal comparisons in a concrete attention task.
- Add repeated hardware evidence across dates/calibration windows and confidence or bootstrap intervals for MAE/rank correlations.

These remaining items require new execution, repo restructuring, or external publication steps and should not be represented as complete.
