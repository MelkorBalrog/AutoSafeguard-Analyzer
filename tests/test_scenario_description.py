from analysis.scenario_description import template_phrases


def test_template_phrases_full():
    phrases = template_phrases(
        "Frontal",
        "driver",
        "turns left",
        [
            ("rainy weather", "Environment", ["rain", "low visibility"]),
            ("guarded highway", "Infrastructure", ["guardrails"]),
            ("asphalt", "Road", ["dry"]),
        ],
        "sensor failure",
        "loss of control",
    )
    assert len(phrases) == 2
    first = phrases[0].lower()
    assert "frontal scenario" in first
    assert "rainy weather environment" in first
    assert "guarded highway infrastructure" in first
    assert "asphalt road" in first
    assert "loss of control" in " ".join(phrases)


def test_template_phrases_partial():
    phrases = template_phrases(
        "Rear",
        "",
        "stops",
        [("city street", "Road", ["wet"])],
        "",
        "brake loss",
    )
    assert phrases
    assert any("brake loss" in p.lower() for p in phrases)
