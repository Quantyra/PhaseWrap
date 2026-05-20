from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage8_needle_benchmark import (  # noqa: E402
    DEFAULT_CONTEXT_LENGTHS,
    DEFAULT_EXAMPLES_PER_LENGTH,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SEEDS,
    print_stage8_table,
    run_needle_benchmark,
    write_stage8_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Stage 8 local Needle-style benchmark.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_SEEDS)
    parser.add_argument("--context-lengths", type=_parse_int_list, default=DEFAULT_CONTEXT_LENGTHS)
    parser.add_argument("--examples-per-length", type=int, default=DEFAULT_EXAMPLES_PER_LENGTH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_needle_benchmark(
        seeds=args.seeds,
        context_lengths=args.context_lengths,
        examples_per_length=args.examples_per_length,
    )
    paths = write_stage8_outputs(result, args.output_dir)
    print_stage8_table(result)
    print(f"best_method_by_top1_mrr: {result['best_method_by_top1_mrr']}")
    print(f"best_period_pair_by_top1_mrr: {result['best_period_pair_by_top1_mrr']}")
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['period_pair_ablation_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

