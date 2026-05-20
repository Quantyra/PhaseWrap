from __future__ import annotations

import json

import numpy as np

from qrope.stage8_needle_benchmark import (
    DEFAULT_PERIOD_PAIR,
    METHOD_NAMES,
    attention_distribution,
    evaluate_needle_method,
    make_needle_examples,
    phasewrap_period_score,
    run_needle_benchmark,
    write_stage8_outputs,
)


def test_phasewrap_period_score_is_deterministic() -> None:
    first = phasewrap_period_score(7, 19, DEFAULT_PERIOD_PAIR)
    second = phasewrap_period_score(7, 19, DEFAULT_PERIOD_PAIR)
    assert first == second


def test_needle_examples_are_deterministic_and_have_unique_targets() -> None:
    first = make_needle_examples(seeds=(101,), context_lengths=(128,), examples_per_length=3)
    second = make_needle_examples(seeds=(101,), context_lengths=(128,), examples_per_length=3)
    assert first == second
    assert len(first) == 3
    for example in first:
        assert example.target_pos in example.key_positions
        assert example.tokens[example.target_pos] == example.query_token
        assert example.tokens[example.query_pos] == example.query_token


def test_attention_distribution_is_probability_vector() -> None:
    example = make_needle_examples(seeds=(101,), context_lengths=(128,), examples_per_length=1)[0]
    distribution = attention_distribution(example, "phasewrap_rope_8_12")
    assert distribution.shape == (example.query_pos,)
    assert np.isclose(float(np.sum(distribution)), 1.0)
    assert np.all(distribution >= 0.0)


def test_evaluate_needle_method_reports_intervals() -> None:
    examples = make_needle_examples(seeds=(101,), context_lengths=(128,), examples_per_length=4)
    metrics = evaluate_needle_method(examples, "phasewrap_rope_8_12")
    assert metrics["row_count"] == 4
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert metrics["top1_ci_low"] <= metrics["top1_accuracy"] <= metrics["top1_ci_high"]
    assert metrics["mrr_ci_low"] <= metrics["mrr"] <= metrics["mrr_ci_high"]


def test_run_needle_benchmark_is_complete_and_deterministic() -> None:
    first = run_needle_benchmark(seeds=(101, 103), context_lengths=(128, 256), examples_per_length=2)
    second = run_needle_benchmark(seeds=(101, 103), context_lengths=(128, 256), examples_per_length=2)
    assert first["table"] == second["table"]
    assert [row["method"] for row in first["table"]] == list(METHOD_NAMES)
    assert first["row_count"] == 8
    assert first["best_method_by_top1_mrr"] in METHOD_NAMES
    assert [8, 12] in [row["period_pair"] for row in first["period_pair_ablation"]]


def test_stage8_outputs_are_written(tmp_path) -> None:
    result = run_needle_benchmark(seeds=(101,), context_lengths=(128,), examples_per_length=2)
    paths = write_stage8_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "period_pair_ablation_csv"}
    assert manifest["stage"] == "stage8_needle_benchmark"
    assert saved["table"] == result["table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "period_pair_ablation.csv").exists()

