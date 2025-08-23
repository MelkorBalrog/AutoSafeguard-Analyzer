from analysis.scenario_description import template_phrases


def test_template_phrases_full():
    phrases = template_phrases(
        "Frontal",
        "driver",
        "turns left",
        [("rainy weather", "Environment"), ("night", "Environment")],
        "sensor failure",
        "loss of control",
    )
    assert len(phrases) == 2
    assert "frontal scenario" in phrases[0].lower()
    assert "rainy weather" in phrases[0]
    assert "loss of control" in " ".join(phrases)


def test_template_phrases_partial():
    phrases = template_phrases("Rear", "", "stops", [], "", "brake loss")
    assert phrases
    assert any("brake loss" in p.lower() for p in phrases)
