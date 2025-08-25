"""Structure tree manipulation helpers extracted from AutoML core."""

from __future__ import annotations

from gui.controls import messagebox


class Structure_Tree_Operations:
    """Encapsulates tree and node manipulation routines."""

    def __init__(self, app):
        self.app = app

    def insert_node_in_tree(self, parent_item, node):
        app = self.app
        if not node.parents or node.node_type.upper() == "TOP EVENT" or node.is_page:
            txt = node.name
            item_id = app.analysis_tree.insert(parent_item, "end", text=txt, open=True, tags=(str(node.unique_id),))
            for child in node.children:
                self.insert_node_in_tree(item_id, child)
        else:
            for child in node.children:
                self.insert_node_in_tree(parent_item, child)

    def _move_subtree_strategy1(self, node, dx, dy):
        for child in getattr(node, "children", []):
            if not getattr(child, "is_primary_instance", True):
                continue
            child.x += dx
            child.y += dy
            self._move_subtree_strategy1(child, dx, dy)

    def _move_subtree_strategy2(self, node, dx, dy):
        for child in [c for c in getattr(node, "children", []) if getattr(c, "is_primary_instance", True)]:
            child.x += dx
            child.y += dy
            self._move_subtree_strategy2(child, dx, dy)

    def _move_subtree_strategy3(self, node, dx, dy):
        children = getattr(node, "children", [])
        for child in children:
            if not getattr(child, "is_primary_instance", True):
                continue
            child.x += dx
            child.y += dy
            self._move_subtree_strategy3(child, dx, dy)

    def _move_subtree_strategy4(self, node, dx, dy):
        for child in list(getattr(node, "children", [])):
            if not getattr(child, "is_primary_instance", True):
                continue
            child.x += dx
            child.y += dy
            self._move_subtree_strategy4(child, dx, dy)

    def move_subtree(self, node, dx, dy):
        for strat in (
            self._move_subtree_strategy1,
            self._move_subtree_strategy2,
            self._move_subtree_strategy3,
            self._move_subtree_strategy4,
        ):
            try:
                strat(node, dx, dy)
                return
            except Exception:
                continue

    def find_node_by_id(self, node, unique_id, visited=None):
        if visited is None:
            visited = set()
        if node.unique_id in visited:
            return None
        visited.add(node.unique_id)
        if node.unique_id == unique_id:
            return node
        for c in node.children:
            res = self.find_node_by_id(c, unique_id, visited)
            if res:
                return res
        return None

    def is_descendant(self, node, possible_ancestor):
        if node == possible_ancestor:
            return True
        for p in node.parents:
            if self.is_descendant(p, possible_ancestor):
                return True
        return False

    def remove_node(self):
        app = self.app
        app.push_undo_state()
        sel = app.analysis_tree.selection()
        target = None
        if sel:
            tags = app.analysis_tree.item(sel[0], "tags")
            target = self.find_node_by_id(app.root_node, int(tags[0]))
        elif app.selected_node:
            target = app.selected_node
        if target and target != app.root_node:
            if target.parents:
                for p in target.parents:
                    if target in p.children:
                        p.children.remove(target)
                target.parents = []
            app.update_views()
        else:
            messagebox.showwarning("Invalid", "Cannot remove the root node.")

    def remove_connection(self, node):
        app = self.app
        app.push_undo_state()
        if node and node != app.root_node:
            if node.parents:
                for p in node.parents:
                    if node in p.children:
                        p.children.remove(node)
                node.parents = []
                if node not in app.top_events:
                    app.top_events.append(node)
                app.update_views()
                messagebox.showinfo(
                    "Remove Connection",
                    f"Disconnected {node.name} from its parent(s) and made it a top-level event.",
                )
            else:
                messagebox.showwarning("Remove Connection", "Node has no parent connection.")
        else:
            messagebox.showwarning("Remove Connection", "Cannot disconnect the root node.")

    def delete_node_and_subtree(self, node):
        app = self.app
        app.push_undo_state()
        if node:
            if node in app.top_events:
                app.top_events.remove(node)
            else:
                for p in node.parents:
                    if node in p.children:
                        p.children.remove(node)
                node.parents = []
            app.update_views()
            messagebox.showinfo("Delete Node", f"Deleted {node.name} and its subtree.")
        else:
            messagebox.showwarning("Delete Node", "Select a node to delete.")

    def find_node_by_id_all(self, unique_id):
        app = self.app
        for top in app.top_events:
            result = self.find_node_by_id(top, unique_id)
            if result is not None:
                return result

        for entry in app.fmea_entries:
            if getattr(entry, "unique_id", None) == unique_id:
                return entry

        for fmea in app.fmeas:
            for e in fmea.get("entries", []):
                if getattr(e, "unique_id", None) == unique_id:
                    return e

        for d in app.fmedas:
            for e in d.get("entries", []):
                if getattr(e, "unique_id", None) == unique_id:
                    return e

        return None

    def get_all_nodes_no_filter(self, node):
        return self.app.fta_app.get_all_nodes_no_filter(self.app, node)

    def get_all_nodes(self, node=None):
        if node is None:
            result = []
            for te in self.app.top_events:
                result.extend(self.get_all_nodes(te))
            return result

        visited = set()

        def rec(n):
            if n.unique_id in visited:
                return []
            visited.add(n.unique_id)
            if n != self.app.root_node and any(parent.is_page for parent in n.parents):
                return []
            result = [n]
            for c in n.children:
                result.extend(rec(c))
            return result

        return rec(node)

    def get_all_nodes_table(self, root_node):
        return self.app.fta_app.get_all_nodes_table(self.app, root_node)

    def get_all_nodes_in_model(self):
        return self.app.fta_app.get_all_nodes_in_model(self.app)

    def node_map_from_data(self, top_events):
        return self.app.review_manager.node_map_from_data(top_events)
