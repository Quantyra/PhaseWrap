from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage26_compact_kv_qa import CONTEXT_LENGTHS, EXAMPLES_PER_LENGTH  # noqa: E402
from qrope.stage27_compact_kv_transformer_bridge import (  # noqa: E402
    DATA_SEEDS,
    DEFAULT_MODEL_SEEDS,
    DEFAULT_OUTPUT_DIR,
    print_stage27_table,
    run_stage27_benchmark,
    write_stage27_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 27 compact key-value QA transformer-bridge benchmark.")
    parser.add_argument("--data-seeds", type=_parse_int_list, default=DATA_SEEDS)
    parser.add_argument("--model-seeds", type=_parse_int_list, default=DEFAULT_MODEL_SEEDS)
    parser.add_argument("--context-lengths", type=_parse_int_list, default=CONTEXT_LENGTHS)
    parser.add_argument("--examples-per-length", type=int, default=EXAMPLES_PER_LENGTH)
    parser.add_argument("--epochs", type=int, default=160)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    result = run_stage27_benchmark(
        data_seeds=args.data_seeds,
        model_seeds=args.model_seeds,
        context_lengths=args.context_lengths,
        examples_per_length=args.examples_per_length,
        epochs=args.epochs,
    )
    paths = write_stage27_outputs(result, args.output_dir)
    print_stage27_table(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['per_run_csv']}")
    print(f"wrote {paths['weak_runs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
