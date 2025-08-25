from __future__ import annotations

"""Clipboard and paste functionality extracted from AutoML."""

from typing import Any
import json
from tkinter import messagebox
from gui.architecture import ARCH_WINDOWS

try:  # pragma: no cover - support direct module import
    from .models.gsn.nodes import GSNNode, ALLOWED_AWAY_TYPES
    from .models.fta.fault_tree_node import FaultTreeNode
except ImportError:  # pragma: no cover
    from models.gsn.nodes import GSNNode, ALLOWED_AWAY_TYPES
    from models.fta.fault_tree_node import FaultTreeNode


class ClipboardAndPaste:
    """Handle node clipboard operations for the AutoML application."""

    def __init__(self, app):
        self.app = app

    # ------------------------------------------------------------------
    # Diagram-level copy/cut strategies
    # ------------------------------------------------------------------
    def _diagram_copy_strategy1(self):
        win = self.app._focused_cbn_window()
        if win and getattr(win, "selected_node", None) and getattr(win, "copy_selected", None):
            self.app.selected_node = None
            self.app.clipboard_node = None
            self.app.cut_mode = False
            win.copy_selected()
            return True
        return False

    def _diagram_copy_strategy2(self):
        win = self.app._focused_gsn_window()
        if win and getattr(win, "selected_node", None) and getattr(win, "copy_selected", None):
            self.app.selected_node = None
            self.app.clipboard_node = None
            self.app.cut_mode = False
            win.copy_selected()
            return True
        return False

    def _diagram_copy_strategy3(self):
        win = getattr(self.app, "active_arch_window", None)
        if win and getattr(win, "selected_obj", None) and getattr(win, "copy_selected", None):
            self.app.selected_node = None
            self.app.clipboard_node = None
            self.app.cut_mode = False
            win.copy_selected()
            return True
        return False

    def _diagram_copy_strategy4(self):
        for ref in list(ARCH_WINDOWS):
            win = ref()
            if win and getattr(win, "selected_obj", None) and getattr(win, "copy_selected", None):
                self.app.selected_node = None
                self.app.clipboard_node = None
                self.app.cut_mode = False
                win.copy_selected()
                return True
        return False

    def _diagram_cut_strategy1(self):
        win = self.app._focused_cbn_window()
        if win and getattr(win, "selected_node", None) and getattr(win, "cut_selected", None):
            self.app.selected_node = None
            self.app.clipboard_node = None
            self.app.cut_mode = False
            win.cut_selected()
            return True
        return False

    def _diagram_cut_strategy2(self):
        win = self.app._focused_gsn_window()
        if win and getattr(win, "selected_node", None) and getattr(win, "cut_selected", None):
            self.app.selected_node = None
            self.app.clipboard_node = None
            self.app.cut_mode = False
            win.cut_selected()
            return True
        return False

    def _diagram_cut_strategy3(self):
        win = getattr(self.app, "active_arch_window", None)
        if win and getattr(win, "selected_obj", None) and getattr(win, "cut_selected", None):
            self.app.selected_node = None
            self.app.clipboard_node = None
            self.app.cut_mode = False
            win.cut_selected()
            return True
        return False

    def _diagram_cut_strategy4(self):
        for ref in list(ARCH_WINDOWS):
            win = ref()
            if win and getattr(win, "selected_obj", None) and getattr(win, "cut_selected", None):
                self.app.selected_node = None
                self.app.clipboard_node = None
                self.app.cut_mode = False
                win.cut_selected()
                return True
        return False

    # ------------------------------------------------------------------
    # Node clipboard operations
    # ------------------------------------------------------------------
    def copy_node(self):
        for strat in (
            self._diagram_copy_strategy1,
            self._diagram_copy_strategy2,
            self._diagram_copy_strategy3,
            self._diagram_copy_strategy4,
        ):
            if strat():
                return
        node = self.app.selected_node
        if (node is None or node == self.app.root_node) and hasattr(self.app, "analysis_tree"):
            sel = self.app.analysis_tree.selection()
            if sel:
                tags = self.app.analysis_tree.item(sel[0], "tags")
                if tags:
                    node = self.app.find_node_by_id(self.app.root_node, int(tags[0]))
        if node and node != self.app.root_node:
            self.app.clipboard_node = node
            self.app.selected_node = node
            self.app.cut_mode = False
            if node.parents:
                parent = node.parents[0]
                context_children = getattr(parent, "context_children", [])
                rel = "context" if node in context_children else "solved"
            else:
                rel = "solved"
            self.app.clipboard_relation = rel
            return
        messagebox.showwarning("Copy", "Select a non-root node to copy.")

    def cut_node(self):
        """Store the currently selected node for a cut & paste operation."""
        for strat in (
            self._diagram_cut_strategy1,
            self._diagram_cut_strategy2,
            self._diagram_cut_strategy3,
            self._diagram_cut_strategy4,
        ):
            if strat():
                return
        node = self.app.selected_node
        if (node is None or node == self.app.root_node) and hasattr(self.app, "analysis_tree"):
            sel = self.app.analysis_tree.selection()
            if sel:
                tags = self.app.analysis_tree.item(sel[0], "tags")
                if tags:
                    node = self.app.find_node_by_id(self.app.root_node, int(tags[0]))
        if node and node != self.app.root_node:
            self.app.clipboard_node = node
            self.app.selected_node = node
            self.app.cut_mode = True
            if node.parents:
                parent = node.parents[0]
                context_children = getattr(parent, "context_children", [])
                rel = "context" if node in context_children else "solved"
            else:
                rel = "solved"
            self.app.clipboard_relation = rel
            return
        if getattr(self.app, "active_arch_window", None) or ARCH_WINDOWS:
            return
        messagebox.showwarning("Cut", "Select a non-root node to cut.")

    # ------------------------------------------------------------------
    def _clone_for_paste_strategy1(self, node, parent=None):
        if hasattr(node, "clone"):
            if parent and getattr(node, "node_type", None) in {"Context", "Assumption", "Justification"}:
                return node.clone(parent)
            return node.clone()
        import copy
        clone = copy.deepcopy(node)
        self.app._reset_gsn_clone(clone)
        return clone

    def _clone_for_paste_strategy2(self, node, parent=None):
        import copy
        if isinstance(node, GSNNode):
            if parent and node.node_type in {"Context", "Assumption", "Justification"}:
                return node.clone(parent)
            return node.clone()
        clone = copy.deepcopy(node)
        self.app._reset_gsn_clone(clone)
        return clone

    def _clone_for_paste_strategy3(self, node, parent=None):
        try:
            if parent and getattr(node, "node_type", None) in {"Context", "Assumption", "Justification"}:
                return node.clone(parent)  # type: ignore[attr-defined]
            return node.clone()  # type: ignore[attr-defined]
        except Exception:
            import copy
            clone = copy.deepcopy(node)
            self.app._reset_gsn_clone(clone)
            return clone

    def _clone_for_paste_strategy4(self, node, parent=None):
        import copy
        clone = copy.deepcopy(node)
        self.app._reset_gsn_clone(clone)
        return clone

    def _clone_for_paste(self, node, parent=None):
        for strat in (
            self._clone_for_paste_strategy1,
            self._clone_for_paste_strategy2,
            self._clone_for_paste_strategy3,
            self._clone_for_paste_strategy4,
        ):
            try:
                clone = strat(node, parent)
                if clone is not None:
                    return clone
            except ValueError:
                messagebox.showwarning("Clone", "Cannot clone this node type.")
                return None
            except Exception:
                continue
        messagebox.showwarning("Clone", "Cannot clone this node type.")
        return None

    def _prepare_node_for_paste(self, target):
        """Return appropriate node instance when pasting."""
        if (
            isinstance(self.app.clipboard_node, GSNNode)
            and target in getattr(self.app.clipboard_node, "parents", [])
        ):
            return self._clone_for_paste(self.app.clipboard_node)
        if (
            isinstance(self.app.clipboard_node, FaultTreeNode)
            or type(self.app.clipboard_node).__name__ == "FaultTreeNode"
        ):
            return self._clone_for_paste(self.app.clipboard_node)
        return self.app.clipboard_node

    def paste_node(self):
        if self.app.clipboard_node:
            target = None
            sel = self.app.analysis_tree.selection()
            if sel:
                tags = self.app.analysis_tree.item(sel[0], "tags")
                if tags:
                    target = self.app.find_node_by_id(self.app.root_node, int(tags[0]))
            if not target:
                target = self.app.selected_node or self.app.root_node
            if not target:
                win = self.app._focused_gsn_window()
                if win and getattr(win, "diagram", None):
                    target = win.diagram.root
            if not target:
                win = self.app._focused_cbn_window()
                if win and getattr(win, "diagram", None):
                    target = win.diagram.root
            if not target:
                target = self.app.root_node
            if not target:
                win = self.app._focused_gsn_window()
                if win and getattr(win, "diagram", None):
                    target = win.diagram.root
            if not target:
                win = self.app._focused_cbn_window()
                if win and getattr(win, "diagram", None):
                    target = win.diagram.root
            if not target:
                target = self.app.root_node
            if not target:
                messagebox.showwarning("Paste", "Select a target node to paste into.")
                return
            if target.node_type.upper() in ["CONFIDENCE LEVEL", "ROBUSTNESS SCORE"]:
                messagebox.showwarning("Paste", "Cannot paste into a base event.")
                return
            if not target.is_primary_instance:
                target = target.original
            if target.unique_id == self.app.clipboard_node.unique_id:
                messagebox.showwarning("Paste", "Cannot paste a node onto itself.")
                return
            if self.app.cut_mode:
                for child in target.children:
                    if child.unique_id == self.app.clipboard_node.unique_id:
                        messagebox.showwarning("Paste", "This node is already a child of the target.")
                        return
            if self.app.cut_mode:
                if self.app.clipboard_node in self.app.top_events:
                    self.app.top_events.remove(self.app.clipboard_node)
                for p in list(self.app.clipboard_node.parents):
                    if self.app.clipboard_node in p.children:
                        p.children.remove(self.app.clipboard_node)
                self.app.clipboard_node.parents = []
                if self.app.clipboard_node.node_type.upper() == "TOP EVENT":
                    self.app.clipboard_node.node_type = "RIGOR LEVEL"
                    self.app.clipboard_node.severity = None
                    self.app.clipboard_node.is_page = False
                    self.app.clipboard_node.input_subtype = "Failure"
                self.app.clipboard_node.is_primary_instance = True
                relation = getattr(self.app, "clipboard_relation", "solved")
                if hasattr(target, "add_child"):
                    target.add_child(self.app.clipboard_node, relation=relation)
                else:
                    if relation == "context":
                        target.context_children.append(self.app.clipboard_node)
                    else:
                        target.children.append(self.app.clipboard_node)
                    self.app.clipboard_node.parents.append(target)
                if isinstance(self.app.clipboard_node, GSNNode):
                    old_diag = self.app._find_gsn_diagram(self.app.clipboard_node)
                    new_diag = self.app._find_gsn_diagram(target)
                    if old_diag and old_diag is not new_diag and self.app.clipboard_node in old_diag.nodes:
                        old_diag.nodes.remove(self.app.clipboard_node)
                    if new_diag and self.app.clipboard_node not in new_diag.nodes:
                        new_diag.add_node(self.app.clipboard_node)
                self.app.clipboard_node.x = target.x + 100
                self.app.clipboard_node.y = target.y + 100
                self.app.clipboard_node.display_label = self.app.clipboard_node.display_label.replace(" (clone)", "")
                self.app.clipboard_node = None
                self.app.cut_mode = False
                messagebox.showinfo("Paste", "Node moved successfully (cut & pasted).")
            else:
                target_diag = self.app._find_gsn_diagram(target)
                node_for_pos = self._prepare_node_for_paste(target)
                target.children.append(node_for_pos)
                node_for_pos.parents.append(target)
                if isinstance(node_for_pos, GSNNode):
                    if target_diag and node_for_pos not in target_diag.nodes:
                        target_diag.add_node(node_for_pos)
                node_for_pos.x = target.x + 100
                node_for_pos.y = target.y + 100
                if hasattr(node_for_pos, "display_label"):
                    node_for_pos.display_label = node_for_pos.display_label.replace(" (clone)", "")
                messagebox.showinfo("Paste", "Node pasted successfully (copied).")
            try:
                self.app.helper.calculate_assurance_recursive(
                    self.app.root_node,
                    self.app.top_events,
                )
            except AttributeError:
                pass
            self.app.update_views()
            return
        clip_type = getattr(self.app, "diagram_clipboard_type", None)
        win = self.app._focused_cbn_window()
        if win and getattr(self.app, "diagram_clipboard", None):
            if not clip_type or clip_type == "Causal Bayesian Network":
                if getattr(win, "paste_selected", None):
                    win.paste_selected()
                    return
        win = self.app._focused_gsn_window()
        if win and getattr(self.app, "diagram_clipboard", None):
            if not clip_type or clip_type == "GSN":
                if getattr(win, "paste_selected", None):
                    win.paste_selected()
                    return
        win = self.app._focused_arch_window(clip_type)
        if win and getattr(self.app, "diagram_clipboard", None):
            if getattr(win, "paste_selected", None):
                win.paste_selected()
                return
        messagebox.showwarning("Paste", "Clipboard is empty.")

    # ------------------------------------------------------------------
    # Attribute copying helpers
    # ------------------------------------------------------------------
    def _copy_attrs_no_xy_strategy1(self, target, source, attrs):
        tx, ty = getattr(target, "x", None), getattr(target, "y", None)
        for attr in attrs:
            setattr(target, attr, getattr(source, attr, None))
        if tx is not None:
            target.x = tx
        if ty is not None:
            target.y = ty

    def _copy_attrs_no_xy_strategy2(self, target, source, attrs):
        tx, ty = getattr(target, "x", None), getattr(target, "y", None)
        values = {a: getattr(source, a, None) for a in attrs if hasattr(source, a)}
        for a, v in values.items():
            setattr(target, a, v)
        if tx is not None:
            target.x = tx
        if ty is not None:
            target.y = ty

    def _copy_attrs_no_xy_strategy3(self, target, source, attrs):
        tx, ty = getattr(target, "x", None), getattr(target, "y", None)
        for attr in attrs:
            if attr in {"x", "y"}:
                continue
            setattr(target, attr, getattr(source, attr, None))
        if tx is not None:
            target.x = tx
        if ty is not None:
            target.y = ty

    def _copy_attrs_no_xy_strategy4(self, target, source, attrs):
        self._copy_attrs_no_xy_strategy1(target, source, attrs)

    def _copy_attrs_no_xy(self, target, source, attrs):
        for strat in (
            self._copy_attrs_no_xy_strategy1,
            self._copy_attrs_no_xy_strategy2,
            self._copy_attrs_no_xy_strategy3,
            self._copy_attrs_no_xy_strategy4,
        ):
            try:
                strat(target, source, attrs)
                break
            except Exception:
                continue

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------
    def _strip_object_positions(self, data: dict) -> dict:
        """Return a copy of *data* without concrete object positions."""

        cleaned = json.loads(json.dumps(data))

        def scrub(obj: Any) -> None:
            if isinstance(obj, dict):
                for field in ("x", "y", "modified", "modified_by", "modified_by_email"):
                    obj.pop(field, None)
                for value in obj.values():
                    scrub(value)
            elif isinstance(obj, list):
                for item in obj:
                    scrub(item)

        scrub(cleaned)
        return cleaned

    def clone_node_preserving_id(self, node, parent=None):
        """Return a clone of *node* with a new unique ID."""
        if isinstance(node, GSNNode):
            if node.node_type not in ALLOWED_AWAY_TYPES:
                raise ValueError(
                    "Only Goal, Solution, Context, Assumption, and Justification nodes can be cloned."
                )
            clone_parent = (
                parent
                if parent and node.node_type in {"Context", "Assumption", "Justification"}
                else None
            )
            new_node = node.clone(clone_parent)
            new_node.x = node.x + 100
            new_node.y = node.y + 100
            return new_node

        new_node = FaultTreeNode(node.user_name, node.node_type)
        new_node.unique_id = self.app.helper.get_next_unique_id()
        new_node.quant_value = getattr(node, "quant_value", None)
        new_node.gate_type = getattr(node, "gate_type", None)
        new_node.description = getattr(node, "description", "")
        new_node.rationale = getattr(node, "rationale", "")
        new_node.x = node.x + 100
        new_node.y = node.y + 100
        new_node.severity = getattr(node, "severity", None)
        new_node.input_subtype = getattr(node, "input_subtype", None)
        new_node.display_label = getattr(node, "display_label", "")
        new_node.equation = getattr(node, "equation", "")
        new_node.detailed_equation = getattr(node, "detailed_equation", "")
        new_node.is_page = getattr(node, "is_page", False)
        new_node.is_primary_instance = False
        new_node.original = node if node.is_primary_instance else node.original
        new_node.children = []
        return new_node

    def resolve_original(self, node):
        """Walk the clone chain until a primary instance is found."""
        while not node.is_primary_instance and node.original is not None and node.original != node:
            node = node.original
        return node
