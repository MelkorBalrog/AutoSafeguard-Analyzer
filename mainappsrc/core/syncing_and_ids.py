"""Synchronization helpers for nodes keyed by unique IDs."""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Any

if TYPE_CHECKING:  # pragma: no cover - only for type hints
    from .automl_core import AutoMLApp


class Syncing_And_IDs:
    """Collect and synchronise nodes that share unique identifiers."""

    def __init__(self, app: AutoMLApp) -> None:
        self.app = app

    # ------------------------------------------------------------
    # Helpers to gather all nodes when synchronising by ID
    # ------------------------------------------------------------
    def _collect_sync_nodes_strategy1(self) -> List[Any]:
        nodes: List[Any] = []
        try:
            nodes.extend(self.app.get_all_nodes_in_model())
        except Exception:
            pass
        try:
            nodes.extend(self.app.get_all_fmea_entries())
        except Exception:
            pass
        for attr in ("all_gsn_diagrams", "gsn_diagrams"):
            for diag in getattr(self.app, attr, []):
                nodes.extend(getattr(diag, "nodes", []))
        dedup: List[Any] = []
        for n in nodes:
            if n not in dedup:
                dedup.append(n)
        return dedup

    def _collect_sync_nodes_strategy2(self) -> List[Any]:
        nodes: List[Any] = []
        try:
            nodes.extend(self.app.get_all_nodes(self.app.root_node))
        except Exception:
            pass
        try:
            nodes.extend(self.app.get_all_fmea_entries())
        except Exception:
            pass
        for attr in ("all_gsn_diagrams", "gsn_diagrams"):
            for diag in getattr(self.app, attr, []):
                nodes.extend(getattr(diag, "nodes", []))
        dedup: List[Any] = []
        for n in nodes:
            if n not in dedup:
                dedup.append(n)
        return dedup

    def _collect_sync_nodes_strategy3(self) -> List[Any]:
        visited = set()
        nodes: List[Any] = []
        for getter in (
            getattr(self.app, "get_all_nodes_in_model", None),
            lambda: getattr(self.app, "get_all_nodes", lambda *_a, **_k: [])(self.app.root_node),
            getattr(self.app, "get_all_fmea_entries", None),
        ):
            try:
                for n in getter() if getter else []:
                    if id(n) not in visited:
                        visited.add(id(n))
                        nodes.append(n)
            except Exception:
                continue
        for attr in ("all_gsn_diagrams", "gsn_diagrams"):
            for diag in getattr(self.app, attr, []):
                for n in getattr(diag, "nodes", []):
                    if id(n) not in visited:
                        visited.add(id(n))
                        nodes.append(n)
        return nodes

    def _collect_sync_nodes_strategy4(self) -> List[Any]:
        return self._collect_sync_nodes_strategy1()

    def _collect_sync_nodes(self) -> List[Any]:
        for strat in (
            self._collect_sync_nodes_strategy1,
            self._collect_sync_nodes_strategy2,
            self._collect_sync_nodes_strategy3,
            self._collect_sync_nodes_strategy4,
        ):
            try:
                nodes = strat()
                if nodes:
                    return nodes
            except Exception:
                continue
        return []

    # ------------------------------------------------------------
    # Synchronisation helpers
    # ------------------------------------------------------------
    def _sync_nodes_by_id_strategy1(self, updated_node, attrs):
        clone = updated_node if (not updated_node.is_primary_instance and updated_node.original) else None
        if clone:
            updated_node = clone.original
            self.app._copy_attrs_no_xy(updated_node, clone, attrs)
            updated_node.display_label = clone.display_label.replace(" (clone)", "")
        updated_primary_id = updated_node.unique_id
        nodes_to_check = self._collect_sync_nodes()
        for node in nodes_to_check:
            if node is updated_node or node is clone:
                continue
            if node.is_primary_instance and node.unique_id == updated_primary_id:
                self.app._copy_attrs_no_xy(node, updated_node, attrs)
                node.display_label = updated_node.display_label
            elif (
                not node.is_primary_instance
                and node.original
                and node.original.unique_id == updated_primary_id
            ):
                self.app._copy_attrs_no_xy(node, updated_node, attrs)
                node.display_label = updated_node.display_label + " (clone)"

    def _sync_nodes_by_id_strategy2(self, updated_node, attrs):
        clone = None
        if not updated_node.is_primary_instance and updated_node.original:
            clone = updated_node
            updated_node = clone.original
            self.app._copy_attrs_no_xy(updated_node, clone, attrs)
            updated_node.display_label = clone.display_label.replace(" (clone)", "")
        updated_primary_id = updated_node.unique_id
        nodes = [n for n in self._collect_sync_nodes() if n not in (updated_node, clone)]
        for node in nodes:
            if node.is_primary_instance and node.unique_id == updated_primary_id:
                self.app._copy_attrs_no_xy(node, updated_node, attrs)
                node.display_label = updated_node.display_label
            elif not node.is_primary_instance and getattr(node, "original", None) and node.original.unique_id == updated_primary_id:
                self.app._copy_attrs_no_xy(node, updated_node, attrs)
                node.display_label = updated_node.display_label + " (clone)"

    def _sync_nodes_by_id_strategy3(self, updated_node, attrs):
        clone = updated_node if (
            hasattr(updated_node, "is_primary_instance")
            and not updated_node.is_primary_instance
            and getattr(updated_node, "original", None)
        ) else None
        primary = clone.original if clone else updated_node
        if clone:
            self.app._copy_attrs_no_xy(primary, clone, attrs)
            primary.display_label = clone.display_label.replace(" (clone)", "")
        updated_primary_id = primary.unique_id
        nodes = self._collect_sync_nodes()
        for node in nodes:
            if node in (primary, clone):
                continue
            if node.is_primary_instance and node.unique_id == updated_primary_id:
                self.app._copy_attrs_no_xy(node, primary, attrs)
                node.display_label = primary.display_label
            elif not node.is_primary_instance and getattr(node, "original", None) and node.original.unique_id == updated_primary_id:
                self.app._copy_attrs_no_xy(node, primary, attrs)
                node.display_label = primary.display_label + " (clone)"

    def _sync_nodes_by_id_strategy4(self, updated_node, attrs):
        self._sync_nodes_by_id_strategy1(updated_node, attrs)

    def sync_nodes_by_id(self, updated_node):
        """Synchronize all nodes (original and clones) sharing an ID."""

        attrs = ["user_name", "description", "manager_notes"]

        for strat in (
            self._sync_nodes_by_id_strategy1,
            self._sync_nodes_by_id_strategy2,
            self._sync_nodes_by_id_strategy3,
            self._sync_nodes_by_id_strategy4,
        ):
            try:
                strat(updated_node, attrs)
                break
            except Exception:
                continue
