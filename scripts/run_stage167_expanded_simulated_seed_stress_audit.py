from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage167_expanded_simulated_seed_stress_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_ROW_COUNT,
    DEFAULT_SYNTHETIC_SEEDS,
    print_stage167_summary,
    run_stage167_expanded_seed_stress_audit,
    write_stage167_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run expanded simulated seed/noise stress audit.")
    parser.add_argument("--seeds", nargs="*", type=int, default=list(DEFAULT_SYNTHETIC_SEEDS))
    parser.add_argument("--row-count", type=int, default=DEFAULT_ROW_COUNT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage167_expanded_seed_stress_audit(seeds=tuple(args.seeds), row_count=args.row_count)
    paths = write_stage167_outputs(result, args.output_dir)
    print_stage167_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
