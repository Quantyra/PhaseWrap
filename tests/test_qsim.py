import pytest

from qrope.qibm import derive_ibm_angles
from qrope.qphotonic import derive_photonic_angles
from qrope.qsim import variant_phases


def test_v4_phase_schedule_is_damped_relative_to_v3() -> None:
    v3 = variant_phases("V3", 3)
    v4 = variant_phases("V4", 3)
    assert len(v3) == len(v4) == 3
    assert all(v4_i < v3_i for v4_i, v3_i in zip(v4, v3))
    assert v4 == pytest.approx([0.14, 0.28, 0.42])


def test_v4_backend_angle_translation_is_damped_relative_to_v3() -> None:
    text = "quiet room and fast check in"
    seed = 42

    _, _, rel_v3 = derive_photonic_angles(text=text, variant="V3", seed=seed)
    _, _, rel_v4 = derive_photonic_angles(text=text, variant="V4", seed=seed)
    _, ibm_v3 = derive_ibm_angles(text=text, variant="V3", seed=seed)
    _, ibm_v4 = derive_ibm_angles(text=text, variant="V4", seed=seed)

    assert rel_v4 < rel_v3
    assert ibm_v4 < ibm_v3
