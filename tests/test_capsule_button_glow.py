from gui.capsule_button import _lighten, _hex_to_rgb


def test_lighten_adds_white_and_green():
    color = "#0000ff"
    light = _lighten(color, 1.2)
    r, g, b = _hex_to_rgb(light)
    assert r > 0 and g > 0
