from analysis.scenario_description import template_phrases

def test_template_phrase_filters_and_single():
    phrases = template_phrases(
        "Frontal",
        "driver",
        "turns left",
        [
            ("rainy weather", "Environment", ["rain", "low visibility", "accuracy"]),
            ("guarded highway", "Infrastructure", ["guardrails"]),
            ("asphalt", "Road", ["dry"]),
        ],
        "sensor failure",
        "loss of control",
    )
    assert len(phrases) == 1
    text = phrases[0].lower()
    assert "frontal scenario" in text
    assert "[[rainy weather]] environment" in text
    assert "[[guarded highway]] infrastructure" in text
    assert "[[asphalt]] road" in text
    assert "loss of control" in text
    assert "accuracy" not in text


def test_template_phrase_no_params_word_when_none():
    phrases = template_phrases(
        "Rear",
        "",
        "stops",
        [("city street", "Road", ["accuracy", "recall"])],
        "",
        "brake loss",
    )
    assert len(phrases) == 1
    text = phrases[0].lower()
    assert "brake loss" in text
    assert "accuracy" not in text
    assert "recall" not in text
    assert "parameter" not in text


def test_template_phrase_filters_dict_strings():
    phrases = template_phrases(
        "Frontal",
        "pedestrians",
        "cross",
        [("day", "Environment", ["{'accuracy': 'ratio', 'speed': 'fast'}"])],
        "",
        "",
    )
    assert len(phrases) == 1
    text = phrases[0].lower()
    assert "accuracy" not in text
    assert "speed: fast" in text
    assert "parameter" in text


def test_template_phrase_temporal_and_movable():
    phrases = template_phrases(
        "Side",
        "car",
        "overtakes",
        [
            ("construction zone", "Temporal", []),
            ("truck", "Movable", []),
        ],
        "low battery",
        "power loss",
    )
    assert len(phrases) == 1
    text = phrases[0].lower()
    assert "during [[construction zone]] temporal condition" in text
    assert "with [[truck]] movable object" in text
    assert "low battery" in text
    assert "power loss" in text
