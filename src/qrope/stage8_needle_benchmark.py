from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .automated_stage_gates import phase_residual, spearman


STAGE8_SCHEMA_VERSION = "qrope_stage8_needle_benchmark_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage8_needle_benchmark"
DEFAULT_SEEDS = (101, 103, 107, 109, 113)
DEFAULT_CONTEXT_LENGTHS = (128, 256, 512, 1024)
DEFAULT_EXAMPLES_PER_LENGTH = 8
VOCAB_SIZE = 32
DEFAULT_PERIOD_PAIR = (8, 12)
PERIOD_PAIR_ABLATION = (
    (4, 8),
    (6, 12),
    (7, 11),
    (8, 12),
    (8, 16),
    (8, 24),
    (12, 24),
    (16, 32),
)
METHOD_NAMES = (
    "phasewrap_rope_8_12",
    "rope_relative",
    "alibi",
    "sinusoidal",
    "no_position",
)


@dataclass(frozen=True)
class NeedleExample:
    example_id: str
    seed: int
    sequence_length: int
    query_pos: int
    query_token: int
    reference_delta: int
    target_pos: int
    target_delta: int
    tokens: tuple[int, ...]
    key_positions: tuple[int, ...]


def phasewrap_period_score(reference_delta: int, candidate_delta: int, period_pair: tuple[int, int]) -> float:
    margins = []
    for period in period_pair:
        residual = phase_residual(reference_delta, candidate_delta, period)
        margins.append(math.cos(residual) - math.cos(2.0 * math.pi / float(period)))
    return float(margins[0] * margins[1])


def _non_query_tokens(query_token: int) -> list[int]:
    return [token for token in range(VOCAB_SIZE) if token != query_token]


def _candidate_delta_pool(query_pos: int) -> list[int]:
    return list(range(2, query_pos - 1))


def _unique_phasewrap_target(reference_delta: int, candidate_deltas: list[int]) -> int | None:
    scored = [
        (phasewrap_period_score(reference_delta, delta, DEFAULT_PERIOD_PAIR), -delta, delta)
        for delta in candidate_deltas
    ]
    scored.sort(reverse=True)
    if len(scored) < 2:
        return None
    if abs(scored[0][0] - scored[1][0]) <= 1e-12:
        return None
    return scored[0][2]


def make_needle_examples(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
) -> list[NeedleExample]:
    examples: list[NeedleExample] = []
    reference_deltas = (5, 7, 8, 11, 12, 16, 19, 23, 29, 31, 37)
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for sequence_length in context_lengths:
            query_pos = sequence_length - 1
            pool = _candidate_delta_pool(query_pos)
            distractor_count = min(40, max(12, sequence_length // 24))
            for item_index in range(examples_per_length):
                query_token = int(rng.integers(0, VOCAB_SIZE))
                reference_delta = int(reference_deltas[(seed + sequence_length + item_index) % len(reference_deltas)])
                selected_deltas: list[int] | None = None
                target_delta: int | None = None
                for _ in range(100):
                    candidate_deltas = sorted(
                        int(value)
                        for value in rng.choice(pool, size=distractor_count + 1, replace=False).tolist()
                    )
                    target = _unique_phasewrap_target(reference_delta, candidate_deltas)
                    if target is not None:
                        selected_deltas = candidate_deltas
                        target_delta = target
                        break
                if selected_deltas is None or target_delta is None:
                    raise RuntimeError("could not build a unique synthetic needle example")

                non_query = _non_query_tokens(query_token)
                tokens = [int(non_query[int(rng.integers(0, len(non_query)))]) for _ in range(sequence_length)]
                key_positions = tuple(sorted(query_pos - delta for delta in selected_deltas))
                for position in key_positions:
                    tokens[position] = query_token
                tokens[query_pos] = query_token
                target_pos = query_pos - target_delta
                examples.append(
                    NeedleExample(
                        example_id=f"seed{seed}_L{sequence_length}_{item_index:03d}",
                        seed=seed,
                        sequence_length=sequence_length,
                        query_pos=query_pos,
                        query_token=query_token,
                        reference_delta=reference_delta,
                        target_pos=target_pos,
                        target_delta=target_delta,
                        tokens=tuple(tokens),
                        key_positions=key_positions,
                    )
                )
    return examples


def _rope_inverse_frequencies(dim: int = 32, base: float = 10000.0) -> np.ndarray:
    return np.array([base ** (-2.0 * index / dim) for index in range(dim // 2)], dtype=float)


def _rope_relative_similarity(diff: np.ndarray) -> np.ndarray:
    inv_freq = _rope_inverse_frequencies()
    return np.mean(np.cos(diff[:, None] * inv_freq[None, :]), axis=1)


def _sinusoidal_similarity(diff: np.ndarray) -> np.ndarray:
    inv_freq = _rope_inverse_frequencies(dim=16, base=1000.0)
    return np.mean(np.cos(diff[:, None] * inv_freq[None, :]), axis=1)


def _phasewrap_bias(reference_delta: int, candidate_deltas: np.ndarray, period_pair: tuple[int, int]) -> np.ndarray:
    return np.array(
        [phasewrap_period_score(reference_delta, int(candidate_delta), period_pair) for candidate_delta in candidate_deltas],
        dtype=float,
    )


def attention_distribution(
    example: NeedleExample,
    method_name: str,
    *,
    period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR,
    position_scale: float = 1.0,
) -> np.ndarray:
    candidate_positions = np.arange(example.query_pos, dtype=int)
    candidate_deltas = example.query_pos - candidate_positions
    tokens = np.array(example.tokens[: example.query_pos], dtype=int)
    content_logits = np.where(tokens == example.query_token, 2.0, -4.0).astype(float)
    diff = example.reference_delta - candidate_deltas

    if method_name.startswith("phasewrap_rope"):
        position_bias = _phasewrap_bias(example.reference_delta, candidate_deltas, period_pair)
    elif method_name == "rope_relative":
        position_bias = _rope_relative_similarity(diff.astype(float))
    elif method_name == "sinusoidal":
        position_bias = _sinusoidal_similarity(diff.astype(float))
    elif method_name == "alibi":
        position_bias = -candidate_deltas.astype(float) / float(example.query_pos)
    elif method_name == "no_position":
        position_bias = np.zeros_like(candidate_deltas, dtype=float)
    else:
        raise ValueError(f"unknown method_name: {method_name}")

    logits = content_logits + position_scale * position_bias
    shifted = logits - np.max(logits)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _target_rank(distribution: np.ndarray, target_index: int) -> int:
    sorted_indices = sorted(range(len(distribution)), key=lambda index: (-float(distribution[index]), index))
    return sorted_indices.index(target_index) + 1


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 1000) -> dict[str, float]:
    if not values:
        raise ValueError("cannot bootstrap an empty metric list")
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    low_index = int(0.025 * (iterations - 1))
    high_index = int(0.975 * (iterations - 1))
    return {
        "low": round(means[low_index], 6),
        "high": round(means[high_index], 6),
        "iterations": iterations,
        "confidence_level": 0.95,
    }


def evaluate_needle_method(
    examples: list[NeedleExample],
    method_name: str,
    *,
    period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR,
) -> dict[str, Any]:
    if not examples:
        raise ValueError("examples must be non-empty")
    target_probabilities: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    ranks: list[int] = []
    for example in examples:
        distribution = attention_distribution(example, method_name, period_pair=period_pair)
        rank = _target_rank(distribution, example.target_pos)
        target_probability = float(distribution[example.target_pos])
        ranks.append(rank)
        target_probabilities.append(target_probability)
        reciprocal_ranks.append(1.0 / rank)
        top1_hits.append(1.0 if rank == 1 else 0.0)

    top1 = float(np.mean(top1_hits))
    mrr = float(np.mean(reciprocal_ranks))
    target_probability = float(np.mean(target_probabilities))
    top1_ci = _bootstrap_ci(top1_hits, seed_text=f"{method_name}:{period_pair}:top1")
    mrr_ci = _bootstrap_ci(reciprocal_ranks, seed_text=f"{method_name}:{period_pair}:mrr")
    probability_ci = _bootstrap_ci(target_probabilities, seed_text=f"{method_name}:{period_pair}:prob")
    return {
        "method": method_name,
        "period_pair": list(period_pair) if method_name.startswith("phasewrap_rope") else None,
        "row_count": len(examples),
        "seed_count": len({example.seed for example in examples}),
        "sequence_length_min": min(example.sequence_length for example in examples),
        "sequence_length_max": max(example.sequence_length for example in examples),
        "top1_accuracy": round(top1, 6),
        "top1_ci_low": top1_ci["low"],
        "top1_ci_high": top1_ci["high"],
        "mrr": round(mrr, 6),
        "mrr_ci_low": mrr_ci["low"],
        "mrr_ci_high": mrr_ci["high"],
        "mean_target_probability": round(target_probability, 6),
        "mean_target_probability_ci_low": probability_ci["low"],
        "mean_target_probability_ci_high": probability_ci["high"],
        "mean_rank": round(float(np.mean(ranks)), 6),
        "rank_correlation": round(float(spearman([-float(rank) for rank in ranks], target_probabilities)), 6),
    }


def run_needle_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
) -> dict[str, Any]:
    examples = make_needle_examples(
        seeds=seeds,
        context_lengths=context_lengths,
        examples_per_length=examples_per_length,
    )
    table = [evaluate_needle_method(examples, method_name) for method_name in METHOD_NAMES]
    period_pair_ablation = [
        evaluate_needle_method(
            examples,
            f"phasewrap_rope_{period_a}_{period_b}",
            period_pair=(period_a, period_b),
        )
        for period_a, period_b in PERIOD_PAIR_ABLATION
    ]
    selection_table = sorted(table, key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_probability"], row["method"]), reverse=True)
    period_pair_ablation = sorted(
        period_pair_ablation,
        key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_probability"], row["method"]),
        reverse=True,
    )
    default_period_record = next(row for row in period_pair_ablation if row["period_pair"] == list(DEFAULT_PERIOD_PAIR))
    return {
        "schema_version": STAGE8_SCHEMA_VERSION,
        "stage": "stage8_needle_benchmark",
        "dataset": "synthetic_phase_cued_needle_retrieval_v1",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "examples_per_length": examples_per_length,
        "row_count": len(examples),
        "method_names": list(METHOD_NAMES),
        "task": {
            "description": "Local Needle-style attention retrieval with same-token distractors and a hidden phase-cued target relation.",
            "note": "The packet tests positional scoring behavior in a synthetic retrieval setting. It is not a RULER score, not a language-model benchmark, and not production transformer evidence.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic local Needle-style retrieval comparison across PhaseWrap-RoPE, RoPE-like, ALiBI-like, sinusoidal, and no-position scoring rules.",
                "A period-pair ablation over the same synthetic packet.",
                "Bootstrap intervals over benchmark rows for ranking metrics.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
                "general cross-backend robustness",
                "a proof that the 8/12 period pair is globally optimal",
            ],
        },
        "table": table,
        "selection_table": selection_table,
        "period_pair_ablation": period_pair_ablation,
        "best_method_by_top1_mrr": selection_table[0]["method"],
        "best_period_pair_by_top1_mrr": period_pair_ablation[0]["period_pair"],
        "default_period_pair_record": default_period_record,
    }


def write_stage8_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "seeds": result["seeds"],
        "context_lengths": result["context_lengths"],
        "examples_per_length": result["examples_per_length"],
        "row_count": result["row_count"],
        "method_names": result["method_names"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "period_pair_ablation_csv_path": str((output_dir / "period_pair_ablation.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "period_pair_ablation_csv": str(output_dir / "period_pair_ablation.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    with (output_dir / "period_pair_ablation.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["period_pair_ablation"][0].keys()))
        writer.writeheader()
        writer.writerows(result["period_pair_ablation"])
    return paths


def print_stage8_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "row_count",
        "sequence_length_min",
        "sequence_length_max",
        "top1_accuracy",
        "top1_ci_low",
        "top1_ci_high",
        "mrr",
        "mrr_ci_low",
        "mrr_ci_high",
        "mean_rank",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))

