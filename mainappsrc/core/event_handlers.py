"""Event handler mixins for :class:`AutoMLApp`."""

from __future__ import annotations


class EventHandlersMixin:
    """Collection of simple event callback wrappers."""

    def on_treeview_click(self, event):
        self.tree_app.on_treeview_click(self, event)

    def on_analysis_tree_double_click(self, event):
        self.tree_app.on_analysis_tree_double_click(self, event)

    def on_analysis_tree_right_click(self, event):
        self.tree_app.on_analysis_tree_right_click(self, event)

    def on_analysis_tree_select(self, _event):
        self.tree_app.on_analysis_tree_select(self, _event)

