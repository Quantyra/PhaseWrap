from __future__ import annotations

import phasewrap
import qrope


def test_phasewrap_alias_matches_qrope_scoring_surface() -> None:
    assert phasewrap.DEFAULT_PERIOD_PAIR == qrope.DEFAULT_PERIOD_PAIR
    assert phasewrap.phasewrap_score(37, 13) == qrope.phasewrap_score(37, 13)
    assert phasewrap.phasewrap_features(37, 13) == qrope.phasewrap_features(37, 13)
