from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage188_replacement_semantics_packet_screen import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE177_RESULTS,
    DEFAULT_STAGE187_RESULTS,
    print_stage188_summary,
    run_stage188_replacement_semantics_packet_screen,
    write_stage188_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run replacement-semantics fixed-width IBM-informed simulated screen.")
    parser.add_argument("--stage177-results", type=Path, default=DEFAULT_STAGE177_RESULTS)
    parser.add_argument("--stage187-results", type=Path, default=DEFAULT_STAGE187_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage188_replacement_semantics_packet_screen(
        stage177_results_path=args.stage177_results,
        stage187_results_path=args.stage187_results,
    )
    paths = write_stage188_outputs(result, args.output_dir)
    print_stage188_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    print(f"wrote {paths['packet_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
