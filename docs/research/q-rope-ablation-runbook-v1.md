# Q-RoPE Ablation Runbook v1 (S006)

## Objective
Execute a reproducible first ablation batch for variants `V0-V3` on the QMSAN-style text-classification track.

## Scope
- Included: configuration standards, run commands, logging schema, artifact layout.
- Excluded: manuscript drafting and final claim writing.

## Preconditions
1. Python environment with required ML + quantum dependencies installed.
2. Dataset access configured for Yelp, IMDb, and Amazon splits.
3. Backend adapter selected:
- `sim_local`
- `sim_quantum_statevector` (internal statevector quantum simulator)
- `sim_qiskit_aer` (Qiskit Aer simulator)
- `sim_quandela_remote` (Quandela remote photonic simulator path, phase-1 slice mode)
- `ibm_runtime_remote` (IBM Runtime secondary comparator path, phase-1 slice mode)
- `hw_photonic` (optional phase-1 hardware run)
- `ibm_secondary` (legacy label, superseded by `ibm_runtime_remote`)

## Directory and artifact layout
- Config root: `configs/ablation/`
- Run outputs: `logs/ablation_runs/<run_id>/`
- Aggregates: `logs/ablation_runs/summary/`

## Variant definitions
- `V0`: no positional encoding
- `V1`: additive sinusoidal positional encoding
- `V2`: fixed-gate positional encoding
- `V3`: Q-RoPE relative-phase positional encoding

## Canonical command template
```bash
python -m qrope.run \
  --config configs/ablation/base.yaml \
  --config configs/ablation/<variant>.yaml \
  --set backend=<backend> \
  --set dataset=<dataset> \
  --set run.seed=<seed> \
  --set run.id=<run_id>
```

Use `--real-run` to enable training/inference mode:
```bash
python -m qrope.run --config ... --real-run
```

Example quantum-simulator run:
```bash
python -m qrope.run \
  --config configs/ablation/base.yaml \
  --config configs/ablation/V3.yaml \
  --set backend=sim_quantum_statevector \
  --set dataset=yelp \
  --set run.seed=42 \
  --set run.id=v3-yelp-qsim-s42 \
  --real-run
```

Example Quandela remote run:
```bash
python -m qrope.run \
  --config configs/ablation/base.yaml \
  --config configs/ablation/V3.yaml \
  --set backend=sim_quandela_remote \
  --set dataset=yelp \
  --set run.seed=42 \
  --set run.id=v3-yelp-quandela-s42 \
  --real-run
```

Example IBM Runtime remote run:
```bash
python -m qrope.run \
  --config configs/ablation/base.yaml \
  --config configs/ablation/V3.yaml \
  --set backend=ibm_runtime_remote \
  --set dataset=yelp \
  --set run.seed=42 \
  --set run.id=v3-yelp-ibm-s42 \
  --real-run
```

## End-to-end command set
### V0
```bash
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V0.yaml --set backend=sim_local --set dataset=yelp --set run.seed=42 --set run.id=v0-yelp-s42
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V0.yaml --set backend=sim_local --set dataset=imdb --set run.seed=42 --set run.id=v0-imdb-s42
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V0.yaml --set backend=sim_local --set dataset=amazon --set run.seed=42 --set run.id=v0-amazon-s42
```

### V1
```bash
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V1.yaml --set backend=sim_local --set dataset=yelp --set run.seed=42 --set run.id=v1-yelp-s42
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V1.yaml --set backend=sim_local --set dataset=imdb --set run.seed=42 --set run.id=v1-imdb-s42
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V1.yaml --set backend=sim_local --set dataset=amazon --set run.seed=42 --set run.id=v1-amazon-s42
```

### V2
```bash
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V2.yaml --set backend=sim_local --set dataset=yelp --set run.seed=42 --set run.id=v2-yelp-s42
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V2.yaml --set backend=sim_local --set dataset=imdb --set run.seed=42 --set run.id=v2-imdb-s42
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V2.yaml --set backend=sim_local --set dataset=amazon --set run.seed=42 --set run.id=v2-amazon-s42
```

### V3
```bash
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V3.yaml --set backend=sim_local --set dataset=yelp --set run.seed=42 --set run.id=v3-yelp-s42
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V3.yaml --set backend=sim_local --set dataset=imdb --set run.seed=42 --set run.id=v3-imdb-s42
python -m qrope.run --config configs/ablation/base.yaml --config configs/ablation/V3.yaml --set backend=sim_local --set dataset=amazon --set run.seed=42 --set run.id=v3-amazon-s42
```

## Logging schema (required fields)
Each run writes `metrics.json` with:
- `run_id`
- `variant`
- `dataset`
- `seed`
- `backend`
- `accuracy`
- `f1`
- `train_loss_final`
- `eval_loss`
- `qubit_count`
- `gate_count_total`
- `circuit_depth`
- `shot_count`
- `noise_model`
- `wall_time_sec`
- `timestamp_utc`

## Reproducibility policy
1. Use fixed seed list: `42, 123, 777`.
2. Keep train/val/test splits fixed across `V0-V3`.
3. Keep optimizer and epoch budget unchanged across variants.
4. Log exact dependency versions and backend metadata in each run folder.

## Aggregation commands
```bash
python -m qrope.aggregate \
  --input logs/ablation_runs \
  --output logs/ablation_runs/summary/summary_v1.csv

python -m qrope.report \
  --input logs/ablation_runs/summary/summary_v1.csv \
  --output logs/ablation_runs/summary/report_v1.md
```

## Advancement criteria
Advance to broader benchmarks if:
1. `V3` beats `V2` on at least two datasets with stable variance.
2. Hardware-cost overhead is acceptable for target backend constraints.
3. Noise-robustness degradation remains within agreed tolerance bands.

## Execution note
Command modules (`qrope.run`, `qrope.aggregate`, `qrope.report`) are now bootstrapped under `src/qrope/`. Current outputs are dry-run stubs until model-training execution is integrated.
Current real-run mode supports synthetic fallback data when local dataset files are unavailable (`data/<dataset>.jsonl`).
`sim_quandela_remote` uses a balanced 12-sample remote slice in phase 1 so cloud execution cost and latency remain tractable while preserving a reproducible backend-validation path.
`ibm_runtime_remote` uses the same balanced 12-sample remote slice policy and submits batched `SamplerV2` jobs against the currently available open-instance backend.
Quandela remote execution is credit-consuming and must be treated as budgeted experimental work; see `docs/research/q-rope-credit-aware-remote-execution-policy-v1.md`.
