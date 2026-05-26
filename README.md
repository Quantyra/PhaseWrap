# PhaseWrap

[![CI](https://github.com/Quantyra/PhaseWrap/actions/workflows/ci.yml/badge.svg)](https://github.com/Quantyra/PhaseWrap/actions/workflows/ci.yml)
[![Full non-live verification](https://github.com/Quantyra/PhaseWrap/actions/workflows/ci-full.yml/badge.svg)](https://github.com/Quantyra/PhaseWrap/actions/workflows/ci-full.yml)
[![CodeQL](https://github.com/Quantyra/PhaseWrap/actions/workflows/codeql.yml/badge.svg)](https://github.com/Quantyra/PhaseWrap/actions/workflows/codeql.yml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20387905.svg)](https://doi.org/10.5281/zenodo.20387905)

PhaseWrap is a negative-results and methodology repository for a fixed phase-wrapped relative-position score. The original positive thesis is closed: this repository does **not** claim a RoPE replacement, production transformer superiority, quantum advantage, or broad cross-backend hardware robustness.

The public project name is **PhaseWrap**. The historical Python package and frozen artifact namespace remain `qrope` for reproducibility; `phasewrap` is provided as a compatibility import surface for new code.

```python
from phasewrap import phase_margins, phase_residual, phasewrap_features, phasewrap_score

score = phasewrap_score(reference_delta=37, candidate_delta=13)
features = phasewrap_features(reference_delta=37, candidate_delta=13)
```

The same API is available from `qrope` because archived scripts, manifests, and packet IDs use that namespace.

## What This Repo Shows

PhaseWrap is organized around three evidence lanes.

| Lane | Decisive evidence | Supported conclusion | Not supported |
| --- | --- | --- | --- |
| Score theory | Stage 11 | The fixed `(8, 12)` score has period `24`, only `10` distinct residue values, mirror aliases, and Fourier support `[1, 2, 3, 5]`. | A general-purpose positional encoding. |
| Benchmark methodology | Stages 5, 67, 74/75, 80/81, 93/94/96 | Assistance pipelines can repair retrieval for `no_position` controls too, so benchmark wins must isolate whether the positional method did the work. | Novel discovery of shortcut learning, or proof that external papers are wrong. |
| Hardware-readout audit | Stages 216-218 | One archived IBM Fez packet favors PhaseWrap on normalized readout-noise delta after known-state calibration. | Transformer-scale evidence, quantum advantage, or cross-backend robustness. |

The strongest transferable result is the methodology warning: support-routed or assistance-based retrieval repairs can make a positional method look effective even when the same repair also solves the no-position control. This is a worked example of established shortcut-learning, control-task, and NoPE/NoPos concerns, not a claim that the general concern is new.

The score itself is exactly classically computable and does not need a quantum computer. The hardware lane exists to audit saved provider readout evidence, not to make a compute-advantage claim.

## Claim Boundary

Supported:

- Exact characterization of the fixed PhaseWrap score, including `SQR = m8 * m12`.
- Negative-results evidence that the original phase-cued target is exposed to simple periodic baselines such as `lookup_mod24`; Stage 5 is a motivation constraint, not a positive result.
- A reproducible worked example showing assistance-pipeline confounds in positional-retrieval benchmarks.
- No-credential verification of saved artifacts, including archived hardware readout packets.
- Bounded hardware-readout audit evidence using known-state calibration and provider-aware bitstring handling.

Not supported:

- RoPE replacement.
- Production transformer superiority.
- Quantum advantage.
- Generalization to production long-context models.
- Broad cross-backend hardware robustness.
- Patentability, commercial defensibility, or implementation exclusivity as a scientific conclusion.

## Hardware-Positive Means Bounded Readout Audit

`Hardware-positive` in this repository means a bounded two-qubit readout-audit result on archived packets. It does not imply RoPE replacement, transformer-scale improvement, quantum advantage, or general hardware robustness.

The public Stage 218 decision name is:

```text
IBM_FEZ_FROZEN_PACKET_READOUT_NOISE_DELTA_FAVORS_PHASEWRAP
```

The older manifest identifier `FULL_REPLACEMENT_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE` is preserved only as frozen historical evidence. New prose and review materials should use the bounded readout-noise wording.

## Reviewer Start

Use the no-credential public verifier first:

```bash
python -m pip install -e ".[dev]"
python -m qrope.verify_publication --profile public
```

Expected marker:

```text
PHASEWRAP_PUBLIC_VERIFY_PASS
```

Equivalent console entry point:

```bash
phasewrap-verify --profile public
```

Focused checks:

```bash
python scripts/run_stage11_phasewrap_theory.py
python scripts/run_stage80_support_routed_token_selector_audit.py
python scripts/run_stage218_full_replacement_hardware_metric_interpreter.py
python scripts/run_stage219_rope_substitution_gate.py
```

Legacy Stage 4 hardware packet verifier:

```bash
python scripts/verify_stage4_hardware_packet.py
```

Expected verifier summary:

```json
{
  "pass": true,
  "provider": "ibm_runtime",
  "backend": "ibm_fez",
  "packet_id": "qrope-hardware-73c61893576297ff",
  "job_ids": [
    "d84jbq00bvlc73d4krr0"
  ]
}
```

For a shorter human entry point, start with [REVIEWER_START.md](REVIEWER_START.md). For the canonical evidence map, see [docs/stage-to-claim-map.md](docs/stage-to-claim-map.md).

## Canonical Experiments

The full repository preserves the historical stage archive, but the public argument is carried by a small canonical set:

| Stage(s) | Role in the argument |
| --- | --- |
| 5 | Shows `lookup_mod24` and direct periodic features exactly recover the original synthetic label. |
| 11 | Characterizes the fixed score: period `24`, `10` values, aliases, and Fourier support. |
| 12 | Tests stricter non-phase-cued retrieval and shows fixed PhaseWrap is weak. |
| 30/32 and 219 | Show bounded top-1/MRR ranking parity in selected bridges while RoPE retains stronger probability/calibration. This is a ranking-parity bridge, not substitution adequacy. |
| 67 | Content-key redesign solves for all methods, including `no_position`. |
| 74/75 | Query-support recovery solves for `no_position` too. |
| 80/81 | Support-routed selectors repair phase-cued retrieval for `no_position` too. |
| 82/93/94/96 | Learned support-to-token binding and promotion gates remain bounded or fail. |
| 216-218 | Freeze and interpret the bounded IBM Fez hardware-readout packet. |

Everything else is retained for provenance, replication, or historical audit. It should not be read as a separate headline claim.

In short: support-routing repairs solve phase-cued retrieval for all tested methods, including `no_position`.

## Trained Ablations

Archived autograd-based toy transformer and bridge ablations are historical negative-results context only. They are not headline evidence for production transformer behavior. Any future positive transformer claim should be rerun in a current ML framework with preregistered metrics, strong controls, and real-task baselines.

## Repository Layout

```text
src/qrope/                 Historical package namespace and verifier code
src/phasewrap/             Compatibility import surface for new code
scripts/                   Reproduction and stage runner scripts
docs/stage-to-claim-map.md Canonical stage-to-claim map
docs/publication/          Methodology drafts, release notes, review matrices
logs/automated_stage_gates Frozen stage outputs and archived evidence
tests/                     Public API, verifier, scoring, qsim, and stage tests
```

## Documentation Pointers

- [REVIEWER_START.md](REVIEWER_START.md): 15-minute no-credential review path.
- [docs/stage-to-claim-map.md](docs/stage-to-claim-map.md): canonical experiments and claim mapping.
- [docs/publication/phasewrap-methodology-paper-v1.md](docs/publication/phasewrap-methodology-paper-v1.md): methods-paper draft.
- [docs/publication/post-publication-novelty-and-prior-work-supplement-v1.md](docs/publication/post-publication-novelty-and-prior-work-supplement-v1.md): prior-work and novelty boundary.
- [docs/reproducible-environment.md](docs/reproducible-environment.md): reviewer environment details.
- [docs/api/scoring.md](docs/api/scoring.md): public scoring API.
- [docs/publication/figures/README.md](docs/publication/figures/README.md): publication figures, including `qrope-full-replacement-metrics-v1.png`.
- [PATENTS.md](PATENTS.md): low-prominence legal notice. Patent filings are not used as scientific evidence.

## Installation

Reviewer path:

```bash
python -m pip install -r requirements-review.txt
python -m pip install -e ".[dev]"
```

Core package only:

```bash
python -m pip install -e .
```

Provider SDKs are optional and are not required for saved-artifact verification.

```bash
python -m pip install -e ".[ibm]"
python -m pip install -e ".[braket]"
python -m pip install -e ".[quandela]"
```

## Citation

Use the archived negative-results release and DOI:

```text
Quantyra. PhaseWrap negative-results evidence and reviewer-verification tooling.
Zenodo. https://doi.org/10.5281/zenodo.20387905
```

See [CITATION.cff](CITATION.cff) for machine-readable citation metadata.

## License

Code is released under `AGPL-3.0-only`. Documentation and research text are covered by the repository notices. See [LICENSE](LICENSE), [NOTICE](NOTICE), and [PATENTS.md](PATENTS.md).
