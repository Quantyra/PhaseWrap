from __future__ import annotations

from pathlib import Path

from scripts.verify_stage4_hardware_packet import DEFAULT_STAGE4_DIR, verify_packet_files


def test_single_packet_verifier_uses_repo_relative_paths() -> None:
    verification = verify_packet_files(
        packet_path=DEFAULT_STAGE4_DIR / "frozen_packet.json",
        execution_path=DEFAULT_STAGE4_DIR / "execution.json",
        evaluation_path=DEFAULT_STAGE4_DIR / "evaluation.json",
        summary_path=DEFAULT_STAGE4_DIR / "summary.json",
    )
    for key in ("packet_path", "execution_path", "evaluation_path", "summary_path"):
        path = verification[key]
        assert path
        assert not Path(path).is_absolute()
        assert ":\\" not in path

