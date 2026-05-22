from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage127_injected_client_submitter_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE123_RESULTS,
    DEFAULT_STAGE126_RESULTS,
    print_stage127_summary,
    run_stage127_audit,
    write_stage127_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit injected-client submitter internals before live provider SDK clients are enabled.")
    parser.add_argument("--stage123-results", type=Path, default=DEFAULT_STAGE123_RESULTS)
    parser.add_argument("--stage126-results", type=Path, default=DEFAULT_STAGE126_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage127_audit(stage123_results_path=args.stage123_results, stage126_results_path=args.stage126_results)
    paths = write_stage127_outputs(result, args.output_dir)
    print_stage127_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
