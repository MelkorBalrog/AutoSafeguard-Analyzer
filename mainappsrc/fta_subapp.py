from __future__ import annotations

"""Fault tree analysis helpers separated from the main application."""

from config.automl_constants import dynamic_recommendations
from gui import messagebox


class FTASubApp:
    """Encapsulate fault-tree specific behaviours."""

    def generate_recommendations_for_top_event(self, app, node):
        level = app.helper.discretize_level(node.quant_value) if node.quant_value is not None else 1
        rec = dynamic_recommendations.get(level, {})
        rec_text = f"<b>Recommendations for Prototype Assurance Level (PAL) {level}:</b><br/>"
        for category in [
            "Testing Requirements",
            "IFTD Responsibilities",
            "Preventive Maintenance Actions",
            "Relevant AVSC Guidelines",
        ]:
            if category in rec:
                rec_text += f"<b>{category}:</b><br/><ul><li>{rec[category]}</li></ul><br/>"
        return rec_text

    def back_all_pages(self, app):
        if app.page_history:
            first_page = app.page_history[0]
            app.page_history = []
            for widget in app.canvas_frame.winfo_children():
                widget.destroy()
            app.open_page_diagram(first_page)
        else:
            app.close_page_diagram()

    def move_top_event_up(self, app):
        sel = app.analysis_tree.selection()
        if not sel:
            messagebox.showwarning("Move Up", "Select a top-level event to move.")
            return
        try:
            node_id = int(app.analysis_tree.item(sel[0], "tags")[0])
        except Exception:
            return
        index = next((i for i, event in enumerate(app.top_events) if event.unique_id == node_id), None)
        if index is None:
            messagebox.showwarning("Move Up", "The selected node is not a top-level event.")
            return
        if index == 0:
            messagebox.showinfo("Move Up", "This event is already at the top.")
            return
        app.top_events[index], app.top_events[index - 1] = app.top_events[index - 1], app.top_events[index]
        app.update_views()

    def move_top_event_down(self, app):
        sel = app.analysis_tree.selection()
        if not sel:
            messagebox.showwarning("Move Down", "Select a top-level event to move.")
            return
        try:
            node_id = int(app.analysis_tree.item(sel[0], "tags")[0])
        except Exception:
            return
        index = next((i for i, event in enumerate(app.top_events) if event.unique_id == node_id), None)
        if index is None:
            messagebox.showwarning("Move Down", "The selected node is not a top-level event.")
            return
        if index == len(app.top_events) - 1:
            messagebox.showinfo("Move Down", "This event is already at the bottom.")
            return
        app.top_events[index], app.top_events[index + 1] = app.top_events[index + 1], app.top_events[index]
        app.update_views()

    def get_top_level_nodes(self, app):
        all_nodes = app.get_all_nodes()
        return [node for node in all_nodes if not node.parents]
