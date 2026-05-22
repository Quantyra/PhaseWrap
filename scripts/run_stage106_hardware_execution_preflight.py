from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.env_utils import load_local_dotenv  # noqa: E402
from qrope.stage106_hardware_execution_preflight import (  # noqa: E402
    DEFAULT_OUTPUT_DIR,
    DEFAULT_STAGE105_MANIFEST,
    print_stage106_summary,
    run_stage106_preflight,
    write_stage106_outputs,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Stage 106 hardware execution preflight without submission.")
    parser.add_argument("--stage105-manifest", type=Path, default=DEFAULT_STAGE105_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--load-dotenv", action="store_true")
    args = parser.parse_args(argv)

    if args.load_dotenv:
        load_local_dotenv(REPO_ROOT / ".env")
    result = run_stage106_preflight(stage105_manifest_path=args.stage105_manifest)
    paths = write_stage106_outputs(result, args.output_dir)
    print_stage106_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['result']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
