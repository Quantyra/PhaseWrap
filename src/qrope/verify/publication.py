from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from qrope.paths import REPO_ROOT, repo_relative_posix


PUBLIC_PROFILE = "public"
VERIFIER_SCRIPT = REPO_ROOT / "scripts" / "verify_publication_package.py"


@dataclass(frozen=True)
class VerificationResult:
    profile: str
    passed: bool
    errors: tuple[str, ...]
    verifier: str


def _resolve_verifier_script(path: Path = VERIFIER_SCRIPT) -> Path:
    if path.exists():
        return path
    cwd_candidate = Path.cwd() / "scripts" / "verify_publication_package.py"
    if cwd_candidate.exists():
        return cwd_candidate
    raise FileNotFoundError(f"publication verifier not found: {path} or {cwd_candidate}")


def _load_verifier_module(path: Path = VERIFIER_SCRIPT) -> ModuleType:
    path = _resolve_verifier_script(path)
    spec = importlib.util.spec_from_file_location("_phasewrap_publication_verifier", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load publication verifier: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_publication_profile(profile: str = PUBLIC_PROFILE) -> VerificationResult:
    if profile != PUBLIC_PROFILE:
        raise ValueError(f"unsupported verification profile: {profile!r}")
    verifier_script = _resolve_verifier_script()
    module = _load_verifier_module(verifier_script)
    errors = tuple(str(error) for error in module.verify_publication_package())
    return VerificationResult(
        profile=profile,
        passed=not errors,
        errors=errors,
        verifier=repo_relative_posix(verifier_script),
    )
