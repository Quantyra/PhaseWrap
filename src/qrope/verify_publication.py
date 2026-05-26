from __future__ import annotations

import argparse
import json
import sys

from qrope.verify.publication import PUBLIC_PROFILE, verify_publication_profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify the no-credential PhaseWrap publication package.")
    parser.add_argument("--profile", default=PUBLIC_PROFILE, choices=[PUBLIC_PROFILE])
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = verify_publication_profile(profile=args.profile)
    payload = {
        "profile": result.profile,
        "passed": result.passed,
        "verifier": result.verifier,
        "errors": list(result.errors),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif result.passed:
        print("PHASEWRAP_PUBLIC_VERIFY_PASS")
        print(f"profile: {result.profile}")
        print(f"verifier: {result.verifier}")
    else:
        print("PHASEWRAP_PUBLIC_VERIFY_FAIL")
        for error in result.errors:
            print(f"- {error}")
    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
