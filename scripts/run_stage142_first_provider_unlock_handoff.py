from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage142_first_provider_unlock_handoff import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE141_RESULTS,
    print_stage142_summary,
    run_stage142_handoff,
    write_stage142_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a first-provider unlock handoff packet.")
    parser.add_argument("--stage141-results", type=Path, default=DEFAULT_STAGE141_RESULTS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)

    result = run_stage142_handoff(stage141_results_path=args.stage141_results)
    paths = write_stage142_outputs(result, args.output_dir)
    print_stage142_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['handoff']}")
    print(f"wrote {paths['env_template']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
