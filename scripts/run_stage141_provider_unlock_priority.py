from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage141_provider_unlock_priority import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE139_RESULTS,
    DEFAULT_STAGE140_RESULTS,
    print_stage141_summary,
    run_stage141_priority,
    write_stage141_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prioritize the first provider unlock path for QRoPE hardware execution.")
    parser.add_argument("--stage139-results", type=Path, default=DEFAULT_STAGE139_RESULTS)
    parser.add_argument("--stage140-results", type=Path, default=DEFAULT_STAGE140_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage141_priority(stage139_results_path=args.stage139_results, stage140_results_path=args.stage140_results)
    paths = write_stage141_outputs(result, args.output_dir)
    print_stage141_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
