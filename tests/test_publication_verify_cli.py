from __future__ import annotations

from qrope.verify.publication import verify_publication_profile
from qrope.verify_publication import main


def test_verify_publication_profile_passes() -> None:
    result = verify_publication_profile()

    assert result.profile == "public"
    assert result.passed is True
    assert result.errors == ()
    assert result.verifier == "scripts/verify_publication_package.py"


def test_verify_publication_cli_prints_pass(capsys) -> None:
    exit_code = main(["--profile", "public"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "PHASEWRAP_PUBLIC_VERIFY_PASS" in captured.out
