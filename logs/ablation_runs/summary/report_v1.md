# Q-RoPE Ablation Report

## Summary Table

Canonical phase-1 matrix (`backend=sim_local`) only.

| Variant | Dataset | Runs | Mean Accuracy | Mean F1 |
| --- | --- | ---: | ---: | ---: |
| V0 | amazon | 3 | 0.6250 | 0.6667 |
| V0 | imdb | 3 | 0.5000 | 0.5000 |
| V0 | yelp | 3 | 0.3750 | 0.2857 |
| V1 | amazon | 3 | 0.6250 | 0.6667 |
| V1 | imdb | 3 | 0.5000 | 0.5000 |
| V1 | yelp | 3 | 0.3750 | 0.2857 |
| V2 | amazon | 3 | 0.6250 | 0.6667 |
| V2 | imdb | 3 | 0.5000 | 0.5000 |
| V2 | yelp | 3 | 0.3750 | 0.2857 |
| V3 | amazon | 3 | 0.6250 | 0.6667 |
| V3 | imdb | 3 | 0.5000 | 0.5000 |
| V3 | yelp | 3 | 0.3750 | 0.2857 |

## Run Mode Counts

| Run Mode | Count |
| --- | ---: |
| real | 60 |
| dry | 0 |

## Supplemental Backend Runs

| Run ID | Variant | Dataset | Backend | Accuracy | F1 | Data Mode |
| --- | --- | --- | --- | ---: | ---: | --- |
| v0-yelp-ibm-s123 | V0 | yelp | ibm_runtime_remote | 1.0000 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v0-yelp-ibm-s42 | V0 | yelp | ibm_runtime_remote | 0.3333 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v0-yelp-ibm-s777 | V0 | yelp | ibm_runtime_remote | 0.0000 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v0-yelp-local-s42 | V0 | yelp | sim_local | 0.3750 | 0.2857 | local_jsonl |
| v0-yelp-quandela-s123 | V0 | yelp | sim_quandela_remote | 0.0000 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v0-yelp-quandela-s42 | V0 | yelp | sim_quandela_remote | 0.3333 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v0-yelp-quandela-s777 | V0 | yelp | sim_quandela_remote | 1.0000 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v1-yelp-local-s42 | V1 | yelp | sim_local | 0.3750 | 0.2857 | local_jsonl |
| v2-yelp-ibm-s123 | V2 | yelp | ibm_runtime_remote | 0.3333 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v2-yelp-ibm-s42 | V2 | yelp | ibm_runtime_remote | 0.3333 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v2-yelp-ibm-s777 | V2 | yelp | ibm_runtime_remote | 0.3333 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v2-yelp-local-s42 | V2 | yelp | sim_local | 0.3750 | 0.2857 | local_jsonl |
| v2-yelp-quandela-s42 | V2 | yelp | sim_quandela_remote | 0.6667 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v2-yelp-quandela-s777 | V2 | yelp | sim_quandela_remote | 0.3333 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v3-yelp-aer-s42 | V3 | yelp | sim_qiskit_aer | 0.7500 | 0.8000 | local_jsonl |
| v3-yelp-ibm-s123 | V3 | yelp | ibm_runtime_remote | 0.0000 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v3-yelp-ibm-s42 | V3 | yelp | ibm_runtime_remote | 0.6667 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v3-yelp-ibm-s777 | V3 | yelp | ibm_runtime_remote | 0.6667 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v3-yelp-local-s123 | V3 | yelp | sim_local | 0.3750 | 0.2857 | local_jsonl |
| v3-yelp-local-s42 | V3 | yelp | sim_local | 0.3750 | 0.2857 | local_jsonl |
| v3-yelp-qsim-s42 | V3 | yelp | sim_quantum_statevector | 0.5000 | 0.5000 | local_jsonl |
| v3-yelp-quandela-s42 | V3 | yelp | sim_quandela_remote | 0.6667 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v3-yelp-quandela-s777 | V3 | yelp | sim_quandela_remote | 0.3333 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v3-yelp-real-s42 | V3 | yelp | sim_local | 1.0000 | 1.0000 | synthetic_fallback |
