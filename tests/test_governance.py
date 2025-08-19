import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from gsn.governance import RelationshipStatus, can_view_gsn_argumentation
from analysis.safety_management import ALLOWED_USAGE, ALLOWED_ANALYSIS_USAGE


def test_visibility_requires_all_relationships():
    rel = RelationshipStatus(used_by=True, used_after_review=True, used_after_approval=True)
    assert can_view_gsn_argumentation(rel)


def test_visibility_fails_if_any_relationship_missing():
    rel = RelationshipStatus(used_by=True, used_after_review=False, used_after_approval=True)
    assert not can_view_gsn_argumentation(rel)
    rel = RelationshipStatus(used_by=True, used_after_review=True, used_after_approval=False)
    assert not can_view_gsn_argumentation(rel)
    rel = RelationshipStatus(used_by=False, used_after_review=True, used_after_approval=True)
    assert not can_view_gsn_argumentation(rel)


def test_gsn_safety_case_dependency_allowed():
    pair = ("GSN Argumentation", "Safety & Security Case")
    assert pair in ALLOWED_USAGE
    assert pair in ALLOWED_ANALYSIS_USAGE
