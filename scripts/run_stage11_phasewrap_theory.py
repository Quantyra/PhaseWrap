from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.stage11_phasewrap_theory import (  # noqa: E402
    DEFAULT_CONTEXT_LENGTHS,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PERIOD_PAIR,
    print_stage11_summary,
    run_phasewrap_theory_analysis,
    write_stage11_outputs,
)


def _parse_int_list(raw: str) -> tuple[int, ...]:
    values = tuple(int(item.strip()) for item in raw.split(",") if item.strip())
    if not values:
        raise argparse.ArgumentTypeError("expected at least one integer")
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run deterministic Stage 11 PhaseWrap score theory analysis.")
    parser.add_argument("--period-pair", type=_parse_int_list, default=DEFAULT_PERIOD_PAIR)
    parser.add_argument("--context-lengths", type=_parse_int_list, default=DEFAULT_CONTEXT_LENGTHS)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    if len(args.period_pair) != 2:
        raise SystemExit("--period-pair must contain exactly two integers")

    result = run_phasewrap_theory_analysis(
        period_pair=(args.period_pair[0], args.period_pair[1]),
        context_lengths=args.context_lengths,
    )
    paths = write_stage11_outputs(result, args.output_dir)
    print_stage11_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['alias_summary_csv']}")
    print(f"wrote {paths['period_pair_summary_csv']}")
    print(f"wrote {paths['residue_score_table_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
