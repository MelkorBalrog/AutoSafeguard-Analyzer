import math
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from analysis.sotif_validation import (
    acceptance_rate,
    hazardous_behavior_rate,
    validation_time,
)


def test_hazardous_behavior_rate_example():
    # Example values from ISO 21448 Annex C.2.1
    ah = 1e-8  # acceptance criterion per hour
    p_e_hb = 0.05
    p_c_e = 0.1
    p_s_c = 0.01

    rhb = hazardous_behavior_rate(ah, p_e_hb, p_c_e, p_s_c)
    assert math.isclose(rhb, 2e-4, rel_tol=1e-9)

    # Round-trip check using Formula C.1
    assert math.isclose(acceptance_rate(rhb, p_e_hb, p_c_e, p_s_c), ah, rel_tol=1e-9)

    # Validation time for ~63% confidence with zero failures
    t = validation_time(rhb, 0.63)
    assert 4900 < t < 5100
