from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage71_positional_bias_copy_upper_bound_audit import (  # noqa: E402
    DEFAULT_AUDIT_SEEDS,
    DEFAULT_EXAMPLES_PER_LENGTH,
    DEFAULT_OUTPUT_DIR,
    print_stage71_summary,
    run_stage71_audit,
    write_stage71_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 71 positional-bias copy upper-bound audit.")
    parser.add_argument("--seeds", type=_parse_int_list, default=DEFAULT_AUDIT_SEEDS)
    parser.add_argument("--examples-per-length", type=int, default=DEFAULT_EXAMPLES_PER_LENGTH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage71_audit(seeds=args.seeds, examples_per_length=args.examples_per_length)
    paths = write_stage71_outputs(result, args.output_dir)
    print_stage71_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['per_run_csv']}")
    print(f"wrote {paths['per_example_csv']}")
    print(f"wrote {paths['failed_runs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
