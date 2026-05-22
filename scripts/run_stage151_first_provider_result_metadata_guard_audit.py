from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage151_first_provider_result_metadata_guard_audit import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE150_RESULTS,
    print_stage151_summary,
    run_stage151_audit,
    write_stage151_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit first-provider result backend metadata guards before provider result writes.")
    parser.add_argument("--stage150-results", type=Path, default=DEFAULT_STAGE150_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage151_audit(stage150_results_path=args.stage150_results)
    paths = write_stage151_outputs(result, args.output_dir)
    print_stage151_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
