"""Governance rules for Safety & Security Case visibility of GSN diagrams."""
from dataclasses import dataclass

@dataclass
class RelationshipStatus:
    """Status of relationships between GSN argumentation and Safety & Security Case.

    A diagram is visible only when all relationships are satisfied.
    """
    used_by: bool = False
    used_after_review: bool = False
    used_after_approval: bool = False


def can_view_gsn_argumentation(rel: RelationshipStatus) -> bool:
    """Return True if the Safety & Security Case may view GSN diagrams.

    The rule requires the GSN argumentation to be used by the case and
    to have passed both review and approval.
    """
    return rel.used_by and rel.used_after_review and rel.used_after_approval
