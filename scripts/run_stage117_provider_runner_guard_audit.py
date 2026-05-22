from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage117_provider_runner_guard_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE116_RESULTS,
    print_stage117_summary,
    run_stage117_audit,
    write_stage117_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit guarded provider runner entrypoints referenced by Stage 116.")
    parser.add_argument("--stage116-results", type=Path, default=DEFAULT_STAGE116_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage117_audit(stage116_results_path=args.stage116_results)
    paths = write_stage117_outputs(result, args.output_dir)
    print_stage117_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
