from analysis.scenario_description import template_phrases


def test_template_phrases_full():
    phrases = template_phrases(
        "driver", "turns left", ["rainy weather", "night"], "sensor failure", "loss of control"
    )
    assert len(phrases) == 2
    assert "driver turns left" in phrases[0]
    assert "sensor failure" in phrases[0]
    assert "loss of control" in phrases[0]


def test_template_phrases_partial():
    phrases = template_phrases("", "stops", [], "", "brake loss")
    assert phrases
    assert any(p.lower().startswith("brake loss") for p in phrases)
