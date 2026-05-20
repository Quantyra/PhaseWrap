from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage9_trained_transformer_ablation import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SEEDS,
    EXAMPLES_PER_LENGTH,
    print_stage9_table,
    run_stage9_ablation,
    write_stage9_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Stage 9 trained positional-attention ablation.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_SEEDS)
    parser.add_argument("--examples-per-length", type=int, default=EXAMPLES_PER_LENGTH)
    parser.add_argument("--epochs", type=int, default=160)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage9_ablation(seeds=args.seeds, examples_per_length=args.examples_per_length, epochs=args.epochs)
    paths = write_stage9_outputs(result, args.output_dir)
    print_stage9_table(result)
    print(f"best_method_by_mrr: {result['best_method_by_mrr']}")
    print(f"failed_run_count: {len(result['failed_runs'])}")
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['per_seed_csv']}")
    print(f"wrote {paths['failed_runs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
