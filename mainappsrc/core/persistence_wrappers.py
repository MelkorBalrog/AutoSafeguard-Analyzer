"""Persistence helper mixins for :class:`AutoMLApp`."""

from __future__ import annotations


class PersistenceWrappersMixin:
    """Simple wrappers around project persistence operations."""

    def save_diagram_png(self) -> None:
        self.diagram_export_app.save_diagram_png()

    def save_model(self) -> None:
        self.project_manager.save_model()

    def load_model(self) -> None:
        self.project_manager.load_model()

