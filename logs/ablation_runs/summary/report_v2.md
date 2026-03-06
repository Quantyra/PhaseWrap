# Q-RoPE Statistical Report v2

## Dataset Summary

Canonical phase-1 matrix (`backend=sim_local`) only.

| Dataset | Variant | Runs | Mean Acc | Acc CI95 | Mean F1 | F1 CI95 | Mean Gates | Mean Depth |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| amazon | V0 | 3 | 0.6250 | 0.0000 | 0.6667 | 0.0000 | 128.0 | 8.0 |
| amazon | V1 | 3 | 0.6250 | 0.0000 | 0.6667 | 0.0000 | 160.0 | 10.0 |
| amazon | V2 | 3 | 0.6250 | 0.0000 | 0.6667 | 0.0000 | 192.0 | 12.0 |
| amazon | V3 | 3 | 0.6250 | 0.0000 | 0.6667 | 0.0000 | 224.0 | 14.0 |
| imdb | V0 | 3 | 0.5000 | 0.0000 | 0.5000 | 0.0000 | 128.0 | 8.0 |
| imdb | V1 | 3 | 0.5000 | 0.0000 | 0.5000 | 0.0000 | 160.0 | 10.0 |
| imdb | V2 | 3 | 0.5000 | 0.0000 | 0.5000 | 0.0000 | 192.0 | 12.0 |
| imdb | V3 | 3 | 0.5000 | 0.0000 | 0.5000 | 0.0000 | 224.0 | 14.0 |
| yelp | V0 | 3 | 0.3750 | 0.0000 | 0.2857 | 0.0000 | 128.0 | 8.0 |
| yelp | V1 | 3 | 0.3750 | 0.0000 | 0.2857 | 0.0000 | 160.0 | 10.0 |
| yelp | V2 | 3 | 0.3750 | 0.0000 | 0.2857 | 0.0000 | 192.0 | 12.0 |
| yelp | V3 | 3 | 0.3750 | 0.0000 | 0.2857 | 0.0000 | 224.0 | 14.0 |

## V3 Comparison

| Dataset | Comparator | Delta Acc (V3 - comp) | Delta F1 (V3 - comp) |
| --- | --- | ---: | ---: |
| amazon | V2 | 0.0000 | 0.0000 |
| amazon | V1 | 0.0000 | 0.0000 |
| amazon | V0 | 0.0000 | 0.0000 |
| imdb | V2 | 0.0000 | 0.0000 |
| imdb | V1 | 0.0000 | 0.0000 |
| imdb | V0 | 0.0000 | 0.0000 |
| yelp | V2 | 0.0000 | 0.0000 |
| yelp | V1 | 0.0000 | 0.0000 |
| yelp | V0 | 0.0000 | 0.0000 |

## Quantitative Gaps

- Confidence intervals are based on small run counts and should be treated as provisional.
- Local handcrafted datasets remain the main external-validity limitation.
- Supplemental hardware/cloud-style backend rows are tracked separately and are not folded into the canonical baseline table above.

## Supplemental Backend Rows

| Run ID | Backend | Variant | Dataset | Accuracy | F1 | Notes |
| --- | --- | --- | --- | ---: | ---: | --- |
| v0-yelp-ibm-s123 | ibm_runtime_remote | V0 | yelp | 1.0000 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v0-yelp-ibm-s42 | ibm_runtime_remote | V0 | yelp | 0.3333 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v0-yelp-ibm-s777 | ibm_runtime_remote | V0 | yelp | 0.0000 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v0-yelp-local-s42 | sim_local | V0 | yelp | 0.3750 | 0.2857 | local_jsonl |
| v0-yelp-quandela-s123 | sim_quandela_remote | V0 | yelp | 0.0000 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v0-yelp-quandela-s42 | sim_quandela_remote | V0 | yelp | 0.3333 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v0-yelp-quandela-s777 | sim_quandela_remote | V0 | yelp | 1.0000 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v1-yelp-local-s42 | sim_local | V1 | yelp | 0.3750 | 0.2857 | local_jsonl |
| v2-yelp-ibm-s123 | ibm_runtime_remote | V2 | yelp | 0.3333 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v2-yelp-ibm-s42 | ibm_runtime_remote | V2 | yelp | 0.3333 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v2-yelp-ibm-s777 | ibm_runtime_remote | V2 | yelp | 0.3333 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v2-yelp-local-s42 | sim_local | V2 | yelp | 0.3750 | 0.2857 | local_jsonl |
| v2-yelp-quandela-s123 | sim_quandela_remote | V2 | yelp | 1.0000 | 0.0000 | local_jsonl+quandela_remote_slice12+skip0 |
| v2-yelp-quandela-s42 | sim_quandela_remote | V2 | yelp | 0.6667 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v2-yelp-quandela-s777 | sim_quandela_remote | V2 | yelp | 0.3333 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v3-yelp-aer-s42 | sim_qiskit_aer | V3 | yelp | 0.7500 | 0.8000 | local_jsonl |
| v3-yelp-ibm-s123 | ibm_runtime_remote | V3 | yelp | 0.0000 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v3-yelp-ibm-s42 | ibm_runtime_remote | V3 | yelp | 0.6667 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v3-yelp-ibm-s777 | ibm_runtime_remote | V3 | yelp | 0.6667 | 0.0000 | local_jsonl+ibm_runtime_slice12 |
| v3-yelp-local-s123 | sim_local | V3 | yelp | 0.3750 | 0.2857 | local_jsonl |
| v3-yelp-local-s42 | sim_local | V3 | yelp | 0.3750 | 0.2857 | local_jsonl |
| v3-yelp-qsim-s42 | sim_quantum_statevector | V3 | yelp | 0.5000 | 0.5000 | local_jsonl |
| v3-yelp-quandela-s123 | sim_quandela_remote | V3 | yelp | 0.6667 | 0.0000 | local_jsonl+quandela_remote_slice12+skip0 |
| v3-yelp-quandela-s42 | sim_quandela_remote | V3 | yelp | 0.6667 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v3-yelp-quandela-s777 | sim_quandela_remote | V3 | yelp | 0.3333 | 0.0000 | local_jsonl+quandela_remote_slice12 |
| v3-yelp-real-s42 | sim_local | V3 | yelp | 1.0000 | 1.0000 | synthetic_fallback |
