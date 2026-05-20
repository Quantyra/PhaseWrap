from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage10_small_decoder_transformer import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    print_stage10_summary,
    run_stage10_preflight,
    write_stage10_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 10 small decoder-only transformer preflight.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero exit code when the optional transformer dependency is missing.",
    )
    args = parser.parse_args(argv)

    result = run_stage10_preflight()
    paths = write_stage10_outputs(result, args.output_dir)
    print_stage10_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['preflight']}")
    print(f"wrote {paths['summary_csv']}")
    if args.strict and result["status"] != "ready":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
