import pytest

from analysis.requirement_quality import check_requirement_quality


def test_detects_bad_verb_form():
    text = "Safety engineer shall assesses the <object1_id> (<object1_class>)."
    passed, issues = check_requirement_quality(text)
    assert not passed
    assert any("base form" in msg for msg in issues)


def test_detects_missing_connectors():
    text = (
        "Safety engineer shall assess the <object1_id> (<object1_class>) using the "
        "<object0_id> (<object0_class>), mitigates the <object2_id> (<object2_class>), "
        "develops the <object3_id> (<object3_class>), verify the <object4_id> (<object4_class>), "
        "and produces the <object5_id> (<object5_class>) constrained by <constraint>."
    )
    passed, issues = check_requirement_quality(text)
    assert not passed
    assert any("connecting word" in msg for msg in issues)


def test_accepts_well_formed_requirement():
    text = (
        "Safety engineer shall assess the <object1_id> (<object1_class>) using the "
        "<object0_id> (<object0_class>), ensuring it mitigates the <object2_id> (<object2_class>), "
        "that develops the <object3_id> (<object3_class>), that verifies the <object4_id> (<object4_class>), "
        "and produces the <object5_id> (<object5_class>) constrained by <constraint>."
    )
    passed, issues = check_requirement_quality(text)
    assert passed, issues
