from analysis.utils import (
    exposure_to_probability,
    controllability_to_probability,
    severity_to_probability,
    update_probability_tables,
    EXPOSURE_PROBABILITIES,
    CONTROLLABILITY_PROBABILITIES,
    SEVERITY_PROBABILITIES,
)


def test_update_probability_tables():
    defaults = (
        EXPOSURE_PROBABILITIES.copy(),
        CONTROLLABILITY_PROBABILITIES.copy(),
        SEVERITY_PROBABILITIES.copy(),
    )
    update_probability_tables({1: 0.2}, {2: 0.3}, {3: 0.4})
    assert exposure_to_probability(1) == 0.2
    assert controllability_to_probability(2) == 0.3
    assert severity_to_probability(3) == 0.4
    # Restore defaults to avoid side effects
    update_probability_tables(*defaults)
