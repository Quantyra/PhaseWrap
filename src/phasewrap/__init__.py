"""Compatibility import surface for the PhaseWrap project name.

The historical Python package remains ``qrope`` for artifact compatibility.
New reviewers can import ``phasewrap`` without learning that legacy name first.
"""

from qrope import (  # noqa: F401
    DEFAULT_PERIOD_PAIR,
    phase_margins,
    phase_residual,
    phasewrap_features,
    phasewrap_score,
)

__all__ = [
    "DEFAULT_PERIOD_PAIR",
    "phase_residual",
    "phase_margins",
    "phasewrap_score",
    "phasewrap_features",
]
