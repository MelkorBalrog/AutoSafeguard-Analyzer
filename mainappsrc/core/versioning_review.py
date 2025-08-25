"""Review and versioning helpers separated from the main application."""
from __future__ import annotations

from typing import Any


class Versioning_Review:
    """Facade for review and version-related operations.

    This helper wraps :class:`ReviewManager` to keep
    :class:`AutoMLApp` lean and focused on orchestration.
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    # Delegated review/version operations ---------------------------------
    def add_version(self):
        return self.app.review_manager.add_version()

    def compare_versions(self):
        return self.app.review_manager.compare_versions()

    def open_review_document(self, review):
        return self.app.review_manager.open_review_document(review)

    def open_review_toolbox(self):
        return self.app.review_manager.open_review_toolbox()

    def start_joint_review(self):
        return self.app.review_manager.start_joint_review()

    def start_peer_review(self):
        return self.app.review_manager.start_peer_review()

    def merge_review_comments(self):
        return self.app.review_manager.merge_review_comments()

    def send_review_email(self, review):
        return self.app.review_manager.send_review_email(review)

    def review_is_closed(self):
        return self.app.review_manager.review_is_closed()

    def review_is_closed_for(self, review):
        return self.app.review_manager.review_is_closed_for(review)

    def invalidate_reviews_for_hara(self, name):
        return self.app.review_manager.invalidate_reviews_for_hara(name)

    def invalidate_reviews_for_requirement(self, req_id):
        return self.app.review_manager.invalidate_reviews_for_requirement(req_id)

    def get_review_targets(self):
        return self.app.review_manager.get_review_targets()
