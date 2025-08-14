# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import tkinter as tk
import tkinter.font as tkFont
import textwrap
from tkinter import ttk, simpledialog
from gui import messagebox
import json
import math
import re
from dataclasses import dataclass, field, asdict, replace
from typing import Dict, List, Tuple

from sysml.sysml_repository import SysMLRepository, SysMLDiagram, SysMLElement
from gui.style_manager import StyleManager

from sysml.sysml_spec import SYSML_PROPERTIES
from analysis.models import (
    global_requirements,
    ASIL_ORDER,
    StpaDoc,
    REQUIREMENT_WORK_PRODUCTS,
    REQUIREMENT_TYPE_OPTIONS,
)
from analysis.safety_management import ALLOWED_PROPAGATIONS

# ---------------------------------------------------------------------------
# Appearance customization
# ---------------------------------------------------------------------------
# Colors for AutoML object types come from the global StyleManager so diagrams
# can be easily re-themed.
OBJECT_COLORS = StyleManager.get_instance().styles


_next_obj_id = 1
# Pixel distance used when detecting clicks on connection lines
CONNECTION_SELECT_RADIUS = 15


def _get_next_id() -> int:
    global _next_obj_id
    val = _next_obj_id
    _next_obj_id += 1
    return val


def _parse_float(val: str | None, default: float) -> float:
    """Convert *val* to ``float`` or return ``default`` if conversion fails."""
    try:
        return float(val)
    except (TypeError, ValueError):
        return default


def _part_prop_key(raw: str) -> str:
    """Return canonical property name for a raw part property entry."""
    if not raw:
        return ""
    part = raw.split(":", 1)[0]
    part = part.split("[", 1)[0]
    return part.strip()


def _part_elem_keys(elem) -> set[str]:
    """Return canonical keys for a Part element."""
    if not elem:
        return set()
    name = elem.name or ""
    comp = elem.properties.get("component", "")
    if comp and (not name or name.startswith("Part")):
        name = comp
    if "_" in name and name.rsplit("_", 1)[1].isdigit():
        name = name.rsplit("_", 1)[0]
    base = _part_prop_key(name)
    keys = {base}
    definition = elem.properties.get("definition")
    if definition:
        keys.add(f"{base}:{definition}")
    return keys

def _part_elem_key(elem) -> str:
    """Return a single canonical key (for backward compatibility)."""
    keys = _part_elem_keys(elem)
    return next(iter(keys), "")


def parse_part_property(raw: str) -> tuple[str, str]:
    """Return (property name, block name) parsed from a part property entry."""
    raw = raw.strip()
    prop = raw
    block = raw
    if ":" in raw:
        prop, block = raw.split(":", 1)
    prop = prop.split("[", 1)[0].strip()
    block = block.split("[", 1)[0].strip()
    return (prop or block, block)


def _find_parent_blocks(repo: SysMLRepository, block_id: str) -> set[str]:
    """Return all blocks that directly use ``block_id`` as a part or are
    associated with it."""
    parents: set[str] = set()
    # check IBDs for parts referencing this block
    for parent_id, diag_id in repo.element_diagrams.items():
        diag = repo.diagrams.get(diag_id)
        if not diag:
            continue
        for obj in getattr(diag, "objects", []):
            if obj.get("obj_type") != "Part":
                continue
            if obj.get("properties", {}).get("definition") == block_id:
                parents.add(parent_id)
                break
    # also follow Association and Generalization relationships
    for rel in repo.relationships:
        if rel.rel_type not in ("Association", "Generalization"):
            continue
        if rel.rel_type == "Generalization":
            if rel.source == block_id and rel.target in repo.elements:
                parents.add(rel.target)
            continue
        if rel.source == block_id and rel.target in repo.elements:
            parents.add(rel.target)
        elif rel.target == block_id and rel.source in repo.elements:
            parents.add(rel.source)
    # include father block from internal block diagram linkage
    diag_id = repo.get_linked_diagram(block_id)
    diag = repo.diagrams.get(diag_id)
    if diag and getattr(diag, "father", None) in repo.elements:
        parents.add(diag.father)
    return parents


def _collect_parent_parts(repo: SysMLRepository, block_id: str, visited=None) -> list[str]:
    """Recursively gather parts from all parent blocks of ``block_id``."""
    if visited is None:
        visited = set()
    parts: list[str] = []
    for parent in _find_parent_blocks(repo, block_id):
        if parent in visited:
            continue
        visited.add(parent)
        elem = repo.elements.get(parent)
        if elem:
            parts.extend(
                [
                    p.strip()
                    for p in elem.properties.get("partProperties", "").split(",")
                    if p.strip()
                ]
            )
        parts.extend(_collect_parent_parts(repo, parent, visited))
    seen = []
    for p in parts:
        if p not in seen:
            seen.append(p)
    return seen


def extend_block_parts_with_parents(repo: SysMLRepository, block_id: str) -> None:
    """Merge parts from generalization parents into ``block_id``."""

    block = repo.elements.get(block_id)
    if not block:
        return

    def _parent_parts() -> list[str]:
        return _collect_parent_parts(repo, block_id)

    names = [p.strip() for p in block.properties.get("partProperties", "").split(",") if p.strip()]
    for p in _parent_parts():
        if p not in names:
            names.append(p)

    joined = ", ".join(names)
    block.properties["partProperties"] = joined
    for d in repo.diagrams.values():
        for o in getattr(d, "objects", []):
            if o.get("element_id") == block_id:
                o.setdefault("properties", {})["partProperties"] = joined


def _find_blocks_with_part(repo: SysMLRepository, part_id: str) -> set[str]:
    """Return all blocks that directly include ``part_id`` as a part."""
    blocks: set[str] = set()
    for blk_id, diag_id in repo.element_diagrams.items():
        diag = repo.diagrams.get(diag_id)
        if not diag:
            continue
        for obj in getattr(diag, "objects", []):
            if obj.get("obj_type") != "Part":
                continue
            if obj.get("properties", {}).get("definition") == part_id:
                blocks.add(blk_id)
                break
    return blocks


def _find_blocks_with_aggregation(repo: SysMLRepository, part_id: str) -> set[str]:
    """Return blocks that have an aggregation relationship to ``part_id``."""
    blocks: set[str] = set()
    for rel in repo.relationships:
        if (
            rel.rel_type in ("Aggregation", "Composite Aggregation")
            and rel.target == part_id
        ):
            blocks.add(rel.source)
    return blocks


def _aggregation_exists(repo: SysMLRepository, whole_id: str, part_id: str) -> bool:
    """Return ``True`` if ``whole_id`` or its ancestors already aggregate ``part_id``."""

    src_ids = [whole_id] + _collect_generalization_parents(repo, whole_id)
    diag_id = repo.get_linked_diagram(whole_id)
    diag = repo.diagrams.get(diag_id)
    father = getattr(diag, "father", None) if diag else None
    if father:
        src_ids.append(father)
        src_ids.extend(_collect_generalization_parents(repo, father))

    for rel in repo.relationships:
        if (
            rel.rel_type in ("Aggregation", "Composite Aggregation")
            and rel.source in src_ids
            and rel.target == part_id
        ):
            return True

    for sid in src_ids[1:]:
        diag_id = repo.get_linked_diagram(sid)
        diag = repo.diagrams.get(diag_id)
        if not diag:
            continue
        for obj in getattr(diag, "objects", []):
            if (
                obj.get("obj_type") == "Part"
                and obj.get("properties", {}).get("definition") == part_id
            ):
                return True
    return False


def _reverse_aggregation_exists(
    repo: SysMLRepository, whole_id: str, part_id: str
) -> bool:
    """Return ``True`` if ``part_id`` or its ancestors aggregate ``whole_id``."""

    src_ids = [part_id] + _collect_generalization_parents(repo, part_id)
    for rel in repo.relationships:
        if (
            rel.rel_type in ("Aggregation", "Composite Aggregation")
            and rel.source in src_ids
            and rel.target == whole_id
        ):
            return True
    return False


def _parse_multiplicity_range(mult: str) -> tuple[int, int | None]:
    """Return (lower, upper) bounds parsed from *mult*."""

    mult = mult.strip()
    if not mult:
        return 1, 1
    if ".." in mult:
        low, high = mult.split("..", 1)
        low_val = int(low) if low.isdigit() else 0
        if high == "*" or not high:
            return low_val, None
        return low_val, int(high)
    if mult == "*":
        return 0, None
    if mult.isdigit():
        val = int(mult)
        return val, val
    return 1, None


def _is_default_part_name(def_name: str, part_name: str) -> bool:
    """Return ``True`` if *part_name* is derived from ``def_name``."""

    if not part_name:
        return True
    if part_name == def_name:
        return True
    pattern = re.escape(def_name) + r"\[\d+\]$"
    return re.fullmatch(pattern, part_name) is not None

def _multiplicity_limit_exceeded(
    repo: SysMLRepository,
    parent_id: str,
    def_id: str,
    diagram_objects: list,
    self_elem_id: str | None = None,
) -> bool:
    """Return ``True`` if assigning *def_id* would exceed multiplicity."""

    rels = [
        r
        for r in repo.relationships
        if r.source == parent_id
        and r.target == def_id
        and r.rel_type in ("Aggregation", "Composite Aggregation")
    ]
    if not rels:
        return False

    limit: int | None = 0
    for rel in rels:
        mult = rel.properties.get("multiplicity", "1")

        low, high = _parse_multiplicity_range(mult)
        if high is None:
            limit = None
            break
        limit += high

    if limit is None:
        return False

    # gather all diagrams containing parts for this block
    diag_ids: set[str] = set()
    linked = repo.get_linked_diagram(parent_id)
    if linked:
        diag_ids.add(linked)
    for d in repo.diagrams.values():
        if d.diag_type != "Internal Block Diagram":
            continue
        for o in getattr(d, "objects", []):
            if o.get("obj_type") == "Block Boundary" and o.get("element_id") == parent_id:
                diag_ids.add(d.diag_id)
                break

    seen: set[str] = set()
    count = 0
    for did in diag_ids:
        diag = repo.diagrams.get(did)
        if not diag:
            continue
        for o in getattr(diag, "objects", []):
            if (
                o.get("obj_type") == "Part"
                and o.get("properties", {}).get("definition") == def_id
            ):
                elem_id = o.get("element_id")
                if elem_id != self_elem_id and elem_id not in seen:
                    seen.add(elem_id)
                    count += 1

    for obj in diagram_objects:
        data = obj.__dict__ if hasattr(obj, "__dict__") else obj
        if (
            data.get("obj_type") == "Part"
            and data.get("properties", {}).get("definition") == def_id
        ):
            elem_id = data.get("element_id")
            if elem_id != self_elem_id and elem_id not in seen:
                seen.add(elem_id)
                count += 1

    return count >= limit


def _part_name_exists(
    repo: SysMLRepository,
    parent_id: str,
    name: str,
    self_elem_id: str | None = None,
) -> bool:
    """Return ``True`` if another part with ``name`` already exists."""

    if not name:
        return False

    diag_ids: set[str] = set()
    linked = repo.get_linked_diagram(parent_id)
    if linked:
        diag_ids.add(linked)
    for d in repo.diagrams.values():
        if d.diag_type != "Internal Block Diagram":
            continue
        for o in getattr(d, "objects", []):
            if o.get("obj_type") == "Block Boundary" and o.get("element_id") == parent_id:
                diag_ids.add(d.diag_id)
                break

    for did in diag_ids:
        diag = repo.diagrams.get(did)
        if not diag:
            continue
        for obj in getattr(diag, "objects", []):
            if obj.get("obj_type") != "Part":
                continue
            if obj.get("element_id") == self_elem_id:
                continue
            elem_id = obj.get("element_id")
            if elem_id in repo.elements and repo.elements[elem_id].name == name:
                return True

    return False

def _find_generalization_children(repo: SysMLRepository, parent_id: str) -> set[str]:
    """Return all blocks that generalize ``parent_id``."""
    children: set[str] = set()
    for rel in repo.relationships:
        if rel.rel_type == "Generalization" and rel.target == parent_id:
            children.add(rel.source)
    return children


def _collect_generalization_parents(
    repo: SysMLRepository, block_id: str, visited: set[str] | None = None
) -> list[str]:
    """Return all parent blocks of ``block_id`` reachable through generalizations."""

    if visited is None:
        visited = set()
    parents: list[str] = []
    for rel in repo.relationships:
        if rel.rel_type == "Generalization" and rel.source == block_id:
            target = rel.target
            if target in visited:
                continue
            visited.add(target)
            parents.append(target)
            parents.extend(_collect_generalization_parents(repo, target, visited))
    return parents


def _shared_generalization_parent(
    repo: SysMLRepository, a_id: str, b_id: str
) -> bool:
    """Return ``True`` if *a_id* and *b_id* share a common direct parent."""

    a_parents = {
        rel.target
        for rel in repo.relationships
        if rel.rel_type == "Generalization" and rel.source == a_id
    }
    if not a_parents:
        return False
    b_parents = {
        rel.target
        for rel in repo.relationships
        if rel.rel_type == "Generalization" and rel.source == b_id
    }
    return bool(a_parents & b_parents)


def rename_block(repo: SysMLRepository, block_id: str, new_name: str) -> None:
    """Rename ``block_id`` and propagate changes to related blocks."""
    repo.push_undo_state()
    block = repo.elements.get(block_id)
    if not block or block.elem_type != "Block":
        return
    old_name = block.name
    new_name = repo.ensure_unique_element_name(new_name, block_id)
    if old_name == new_name:
        return
    block.name = new_name
    # update part elements referencing this block
    for elem in repo.elements.values():
        if elem.elem_type != "Part":
            continue
        def_val = elem.properties.get("definition")
        if def_val == block_id or def_val == old_name:
            elem.name = new_name
            elem.properties["definition"] = block_id
    for diag in repo.diagrams.values():
        for obj in getattr(diag, "objects", []):
            if obj.get("obj_type") != "Part":
                continue
            def_val = obj.get("properties", {}).get("definition")
            if def_val == old_name:
                obj.setdefault("properties", {})["definition"] = block_id
    # update blocks that include this block as a part
    related = _find_blocks_with_part(repo, block_id) | _find_blocks_with_aggregation(repo, block_id)
    for parent_id in related:
        parent = repo.elements.get(parent_id)
        if not parent:
            continue
        parts = [p.strip() for p in parent.properties.get("partProperties", "").split(",") if p.strip()]
        changed = False
        for idx, val in enumerate(parts):
            base = val.split("[")[0].strip()
            suffix = val[len(base):]
            if base == old_name or base == block_id:
                parts[idx] = new_name + suffix
                changed = True
        if changed:
            for child_id in _find_generalization_children(repo, parent_id):
                remove_inherited_block_properties(repo, child_id, parent_id)
            parent.properties["partProperties"] = ", ".join(parts)
            for d in repo.diagrams.values():
                for o in getattr(d, "objects", []):
                    if o.get("element_id") == parent_id:
                        o.setdefault("properties", {})["partProperties"] = parent.properties["partProperties"]
            for child_id in _find_generalization_children(repo, parent_id):
                inherit_block_properties(repo, child_id)
    # propagate property inheritance to children blocks
    for child_id in _find_generalization_children(repo, block_id):
        inherit_block_properties(repo, child_id)

    # update any Block Boundary objects referencing this block
    for diag in repo.diagrams.values():
        updated = False
        for obj in getattr(diag, "objects", []):
            if obj.get("element_id") == block_id:
                if obj.get("obj_type") == "Block Boundary" or obj.get("obj_type") == "Block":
                    obj.setdefault("properties", {})["name"] = new_name
                    updated = True
        if updated:
            repo.touch_diagram(diag.diag_id)

    # update Block objects referencing this block
    for diag in repo.diagrams.values():
        updated = False
        for obj in getattr(diag, "objects", []):
            if obj.get("obj_type") == "Block" and obj.get("element_id") == block_id:
                obj.setdefault("properties", {})["name"] = new_name
                updated = True
        if updated:
            repo.touch_diagram(diag.diag_id)


def add_aggregation_part(
    repo: SysMLRepository,
    whole_id: str,
    part_id: str,
    multiplicity: str = "",
    app=None,
) -> None:
    """Add *part_id* as a part of *whole_id* block."""
    repo.push_undo_state()
    whole = repo.elements.get(whole_id)
    part = repo.elements.get(part_id)
    if not whole or not part:
        return
    if part_id == whole_id:
        return
    if part_id in _collect_generalization_parents(repo, whole_id):
        return
    if _reverse_aggregation_exists(repo, whole_id, part_id):
        return
    name = part.name or part_id
    entry = f"{name}[{multiplicity}]" if multiplicity else name
    parts = [p.strip() for p in whole.properties.get("partProperties", "").split(",") if p.strip()]
    base = [p.split("[")[0].strip() for p in parts]
    if name in base:
        for idx, b in enumerate(base):
            if b == name:
                parts[idx] = entry
                break
    else:
        parts.append(entry)
    whole.properties["partProperties"] = ", ".join(parts)
    for d in repo.diagrams.values():
        for o in getattr(d, "objects", []):
            if o.get("element_id") == whole_id:
                o.setdefault("properties", {})["partProperties"] = ", ".join(parts)

    # ensure a Part element exists representing the aggregation
    rel = next(
        (
            r
            for r in repo.relationships
            if r.rel_type == "Aggregation"
            and r.source == whole_id
            and r.target == part_id
        ),
        None,
    )
    if not rel:
        rel = next(
            (
                r
                for r in repo.relationships
                if r.rel_type == "Composite Aggregation"
                and r.source == whole_id
                and r.target == part_id
            ),
            None,
        )
    if not rel:
        rel = repo.create_relationship("Aggregation", whole_id, part_id, record_undo=False)
    if multiplicity:
        rel.properties["multiplicity"] = multiplicity
    else:
        rel.properties.pop("multiplicity", None)
    if not rel.properties.get("part_elem"):
        part_elem = repo.create_element(
            "Part",
            name=repo.elements.get(part_id).name or part_id,
            properties={"definition": part_id},
            owner=repo.root_package.elem_id,
        )
        repo._undo_stack.pop()
        rel.properties["part_elem"] = part_elem.elem_id

    # propagate changes to any generalization children
    for child_id in _find_generalization_children(repo, whole_id):
        remove_inherited_block_properties(repo, child_id, whole_id)
        inherit_block_properties(repo, child_id)
    # ensure multiplicity instances if composite diagram exists
    add_multiplicity_parts(repo, whole_id, part_id, multiplicity, app=app)


def add_composite_aggregation_part(
    repo: SysMLRepository,
    whole_id: str,
    part_id: str,
    multiplicity: str = "",
    app=None,
) -> None:
    """Add *part_id* as a composite part of *whole_id* block and create the
    part object in the whole's Internal Block Diagram if present."""
    repo.push_undo_state()

    add_aggregation_part(repo, whole_id, part_id, multiplicity, app=app)
    diag_id = repo.get_linked_diagram(whole_id)
    diag = repo.diagrams.get(diag_id)
    # locate the relationship for future reference
    rel = next(
        (
            r
            for r in repo.relationships
            if r.rel_type == "Composite Aggregation"
            and r.source == whole_id
            and r.target == part_id
        ),
        None,
    )
    if not rel:
        rel = repo.create_relationship("Composite Aggregation", whole_id, part_id, record_undo=False)
    if multiplicity:
        rel.properties["multiplicity"] = multiplicity
    else:
        rel.properties.pop("multiplicity", None)
    if not diag or diag.diag_type != "Internal Block Diagram":
        if rel and not rel.properties.get("part_elem"):
            part_elem = repo.create_element(
                "Part",
                name=repo.elements.get(part_id).name or part_id,
                properties={"definition": part_id, "force_ibd": "true"},
                owner=repo.root_package.elem_id,
            )
            repo._undo_stack.pop()
            rel.properties["part_elem"] = part_elem.elem_id
        elif rel and rel.properties.get("part_elem"):
            pid = rel.properties["part_elem"]
            elem = repo.elements.get(pid)
            if elem:
                elem.properties["force_ibd"] = "true"
        return
    diag.objects = getattr(diag, "objects", [])
    existing_defs = {
        o.get("properties", {}).get("definition")
        for o in diag.objects
        if o.get("obj_type") == "Part"
    }
    if part_id in existing_defs:
        return
    if rel and rel.properties.get("part_elem") and rel.properties["part_elem"] in repo.elements:
        part_elem = repo.elements[rel.properties["part_elem"]]
        part_elem.properties["force_ibd"] = "true"
    else:
        part_elem = repo.create_element(
            "Part",
            name=repo.elements.get(part_id).name or part_id,
            properties={"definition": part_id, "force_ibd": "true"},
            owner=repo.root_package.elem_id,
        )
        if rel:
            rel.properties["part_elem"] = part_elem.elem_id
    repo.add_element_to_diagram(diag.diag_id, part_elem.elem_id)
    obj_dict = {
        "obj_id": _get_next_id(),
        "obj_type": "Part",
        "x": 50.0,
        "y": 50.0 + 60.0 * len(existing_defs),
        "element_id": part_elem.elem_id,
        "properties": {"definition": part_id},
        "locked": True,
    }
    diag.objects.append(obj_dict)
    _add_ports_for_part(repo, diag, obj_dict, app=app)
    if app:
        for win in getattr(app, "ibd_windows", []):
            if getattr(win, "diagram_id", None) == diag.diag_id:
                win.objects.append(SysMLObject(**obj_dict))
                win.redraw()
                win._sync_to_repository()

    # ensure additional instances per multiplicity
    add_multiplicity_parts(repo, whole_id, part_id, multiplicity, app=app)

    # propagate composite part addition to any generalization children
    for child_id in _find_generalization_children(repo, whole_id):
        inherit_block_properties(repo, child_id)


def add_multiplicity_parts(
    repo: SysMLRepository,
    whole_id: str,
    part_id: str,
    multiplicity: str,
    count: int | None = None,
    app=None,
) -> list[dict]:
    """Ensure ``count`` part instances exist according to ``multiplicity``."""

    low, high = _parse_multiplicity_range(multiplicity)

    diag_id = repo.get_linked_diagram(whole_id)
    diag = repo.diagrams.get(diag_id)
    if not diag or diag.diag_type != "Internal Block Diagram":
        return []
    diag.objects = getattr(diag, "objects", [])
    existing = [
        o
        for o in diag.objects
        if o.get("obj_type") == "Part"
        and o.get("properties", {}).get("definition") == part_id
    ]
    total = len(existing)

    desired = count if count is not None else low
    if high is not None:
        desired = min(desired, high)
    if count is not None:
        target_total = total + desired
        if high is not None:
            target_total = min(target_total, high)
    else:
        target_total = total
        if total < low:
            target_total = low
        if high is not None and target_total > high:
            target_total = high


    added: list[dict] = []
    base_name = repo.elements.get(part_id).name or part_id

    # remove extra part objects if multiplicity decreased
    if total > target_total:
        to_remove = existing[target_total:]
        remove_ids = {o["obj_id"] for o in to_remove}
        for obj in to_remove:
            diag.objects.remove(obj)
            repo.delete_element(obj.get("element_id"))
            repo._undo_stack.pop()
        diag.objects = [
            o
            for o in diag.objects
            if not (
                o.get("obj_type") == "Port"
                and o.get("properties", {}).get("parent") in {str(rid) for rid in remove_ids}
            )
        ]
        existing = existing[:target_total]
        total = target_total
        if app:
            for win in getattr(app, "ibd_windows", []):
                if getattr(win, "diagram_id", None) == diag.diag_id:
                    win.objects = [
                        o
                        for o in win.objects
                        if getattr(o, "obj_id", None) not in remove_ids
                    ]
                    win.redraw()
                    win._sync_to_repository()

    # rename remaining part elements if they still have default names
    for idx, obj in enumerate(existing):
        elem = repo.elements.get(obj.get("element_id"))
        if elem:
            expected = repo.ensure_unique_element_name(
                f"{base_name}[{idx + 1}]", elem.elem_id
            )
            if _is_default_part_name(base_name, elem.name) and elem.name != expected:
                elem.name = expected

    base_x = 50.0
    base_y = 50.0 + 60.0 * len(diag.objects)
    for i in range(total, target_total):
        part_elem = repo.create_element(
            "Part",
            name=f"{base_name}[{i + 1}]",
            properties={"definition": part_id, "force_ibd": "true"},
            owner=repo.root_package.elem_id,
        )
        repo.add_element_to_diagram(diag.diag_id, part_elem.elem_id)
        obj_dict = {
            "obj_id": _get_next_id(),
            "obj_type": "Part",
            "x": base_x,
            "y": base_y,
            "element_id": part_elem.elem_id,
            "properties": {"definition": part_id},
            "locked": True,
        }
        base_y += 60.0
        diag.objects.append(obj_dict)
        _add_ports_for_part(repo, diag, obj_dict, app=app)
        if app:
            for win in getattr(app, "ibd_windows", []):
                if getattr(win, "diagram_id", None) == diag.diag_id:
                    win.objects.append(SysMLObject(**obj_dict))
                    win.redraw()
                    win._sync_to_repository()
        added.append(obj_dict)
    # rename all part elements to ensure sequential numbering
    all_objs = [
        o
        for o in diag.objects
        if o.get("obj_type") == "Part"
        and o.get("properties", {}).get("definition") == part_id
    ]
    for idx, obj in enumerate(all_objs):
        elem = repo.elements.get(obj.get("element_id"))
        if elem:
            expected = repo.ensure_unique_element_name(
                f"{base_name}[{idx + 1}]", elem.elem_id
            )
            if _is_default_part_name(base_name, elem.name) and elem.name != expected:
                elem.name = expected

    return added


def _enforce_ibd_multiplicity(
    repo: SysMLRepository, block_id: str, app=None
) -> list[dict]:
    """Ensure ``block_id``'s IBD obeys aggregation multiplicities.

    Returns a list of added part object dictionaries."""

    added: list[dict] = []
    src_ids = [block_id] + _collect_generalization_parents(repo, block_id)
    for rel in repo.relationships:
        if (
            rel.rel_type in ("Aggregation", "Composite Aggregation")
            and rel.source in src_ids
        ):
            mult = rel.properties.get("multiplicity", "")
            if mult:
                added.extend(
                    add_multiplicity_parts(repo, block_id, rel.target, mult, app=app)
                )
    return added


def _sync_ibd_composite_parts(
    repo: SysMLRepository, block_id: str, app=None
) -> list[dict]:
    """Ensure *block_id*'s IBD includes parts for existing composite aggregations.

    Returns the list of added part object dictionaries."""

    diag_id = repo.get_linked_diagram(block_id)
    diag = repo.diagrams.get(diag_id)
    if not diag or diag.diag_type != "Internal Block Diagram":
        return []
    diag.objects = getattr(diag, "objects", [])
    existing_defs = {
        o.get("properties", {}).get("definition")
        for o in diag.objects
        if o.get("obj_type") == "Part"
    }
    src_ids = [block_id] + _collect_generalization_parents(repo, block_id)
    rels = [
        rel
        for rel in repo.relationships
        if rel.rel_type == "Composite Aggregation" and rel.source in src_ids
    ]
    added: list[dict] = []
    base_x = 50.0
    base_y = 50.0 + 60.0 * len(existing_defs)
    for rel in rels:
        pid = rel.target
        if pid in existing_defs:
            continue
        if rel.properties.get("part_elem") and rel.properties["part_elem"] in repo.elements:
            part_elem = repo.elements[rel.properties["part_elem"]]
            part_elem.properties["force_ibd"] = "true"
        else:
            part_elem = repo.create_element(
                "Part",
                name=repo.elements.get(pid).name or pid,
                properties={"definition": pid, "force_ibd": "true"},
                owner=repo.root_package.elem_id,
            )
            rel.properties["part_elem"] = part_elem.elem_id
        repo.add_element_to_diagram(diag.diag_id, part_elem.elem_id)
        obj_dict = {
            "obj_id": _get_next_id(),
            "obj_type": "Part",
            "x": base_x,
            "y": base_y,
            "element_id": part_elem.elem_id,
            "properties": {"definition": pid},
            "locked": True,
        }
        base_y += 60.0
        diag.objects.append(obj_dict)
        added.append(obj_dict)
        added += _add_ports_for_part(repo, diag, obj_dict, app=app)
        if app:
            for win in getattr(app, "ibd_windows", []):
                if getattr(win, "diagram_id", None) == diag.diag_id:
                    win.objects.append(SysMLObject(**obj_dict))
                    win.redraw()
                    win._sync_to_repository()
    return added


def _sync_ibd_aggregation_parts(
    repo: SysMLRepository, block_id: str, app=None
) -> list[dict]:
    """Ensure ``block_id``'s IBD includes parts for regular aggregations.

    Returns the list of added part object dictionaries."""

    diag_id = repo.get_linked_diagram(block_id)
    diag = repo.diagrams.get(diag_id)
    if not diag or diag.diag_type != "Internal Block Diagram":
        return []
    diag.objects = getattr(diag, "objects", [])
    existing_defs = {
        o.get("properties", {}).get("definition")
        for o in diag.objects
        if o.get("obj_type") == "Part"
    }
    src_ids = [block_id] + _collect_generalization_parents(repo, block_id)
    rels = [
        rel
        for rel in repo.relationships
        if rel.rel_type == "Aggregation" and rel.source in src_ids
    ]
    added: list[dict] = []
    base_x = 50.0
    base_y = 50.0 + 60.0 * len(existing_defs)
    for rel in rels:
        pid = rel.target
        if pid in existing_defs:
            continue
        if rel.properties.get("part_elem") and rel.properties["part_elem"] in repo.elements:
            part_elem = repo.elements[rel.properties["part_elem"]]
        else:
            part_elem = repo.create_element(
                "Part",
                name=repo.elements.get(pid).name or pid,
                properties={"definition": pid},
                owner=repo.root_package.elem_id,
            )
            rel.properties["part_elem"] = part_elem.elem_id
        repo.add_element_to_diagram(diag.diag_id, part_elem.elem_id)
        obj_dict = {
            "obj_id": _get_next_id(),
            "obj_type": "Part",
            "x": base_x,
            "y": base_y,
            "element_id": part_elem.elem_id,
            "properties": {"definition": pid},
        }
        base_y += 60.0
        diag.objects.append(obj_dict)
        added.append(obj_dict)
        added += _add_ports_for_part(repo, diag, obj_dict, app=app)
        if app:
            for win in getattr(app, "ibd_windows", []):
                if getattr(win, "diagram_id", None) == diag.diag_id:
                    win.objects.append(SysMLObject(**obj_dict))
                    win.redraw()
                    win._sync_to_repository()
    return added


def _sync_ibd_partproperty_parts(
    repo: SysMLRepository,
    block_id: str,
    names: list[str] | None = None,
    app=None,
    visible: bool = False,
    hidden: bool | None = None,
) -> list[dict]:
    """Ensure ``block_id``'s IBD includes parts for given ``names``.

    If *names* is ``None``, the block's ``partProperties`` attribute is parsed.
    Returns the list of added part object dictionaries.

    ``hidden`` is provided for backwards compatibility and overrides the
    ``visible`` flag when specified."""

    if hidden is not None:
        visible = not hidden

    diag_id = repo.get_linked_diagram(block_id)
    diag = repo.diagrams.get(diag_id)
    if not diag or diag.diag_type != "Internal Block Diagram":
        return []
    block = repo.elements.get(block_id)
    if not block:
        return []

    diag.objects = getattr(diag, "objects", [])
    existing_defs = {
        o.get("properties", {}).get("definition")
        for o in diag.objects
        if o.get("obj_type") == "Part"
    }
    existing_keys: set[str] = set()
    for o in diag.objects:
        if o.get("obj_type") == "Part" and o.get("element_id") in repo.elements:
            existing_keys.update(_part_elem_keys(repo.elements[o.get("element_id")]))
    if names is None:
        entries = [p for p in block.properties.get("partProperties", "").split(",") if p.strip()]
    else:
        entries = [n for n in names if n.strip()]
    parsed_raw = [parse_part_property(e) for e in entries]
    seen_keys = set()
    parsed = []
    for prop_name, block_name in parsed_raw:
        key = _part_prop_key(prop_name)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        parsed.append((prop_name, block_name))
    added: list[dict] = []
    boundary = next((o for o in diag.objects if o.get("obj_type") == "Block Boundary"), None)
    existing_count = sum(1 for o in diag.objects if o.get("obj_type") == "Part")
    if boundary:
        base_x = boundary["x"] - boundary["width"] / 2 + 30.0
        base_y = boundary["y"] - boundary["height"] / 2 + 30.0 + 60.0 * existing_count
    else:
        base_x = 50.0
        base_y = 50.0 + 60.0 * existing_count
    for prop_name, block_name in parsed:
        target_id = next(
            (
                eid
                for eid, elem in repo.elements.items()
                if elem.elem_type == "Block" and elem.name == block_name
            ),
            None,
        )
        if not target_id:
            continue
        base = _part_prop_key(prop_name)
        cand_key = f"{base}:{target_id}"
        if cand_key in existing_keys or base in existing_keys:
            continue
        # enforce multiplicity based on aggregation relationships
        limit = None
        for rel in repo.relationships:
            if (
                rel.source == block_id
                and rel.target == target_id
                and rel.rel_type in ("Aggregation", "Composite Aggregation")
            ):
                mult = rel.properties.get("multiplicity", "")
                low, high = _parse_multiplicity_range(mult)
                if high is not None:
                    limit = high
                break
        if limit is not None:
            current = sum(
                1
                for o in diag.objects
                if o.get("obj_type") == "Part"
                and o.get("properties", {}).get("definition") == target_id
            )
            if current >= limit:
                continue
        part_elem = repo.create_element(
            "Part",
            name=prop_name,
            properties={"definition": target_id, "force_ibd": "true"},
            owner=repo.root_package.elem_id,
        )
        repo.add_element_to_diagram(diag.diag_id, part_elem.elem_id)
        obj_dict = {
            "obj_id": _get_next_id(),
            "obj_type": "Part",
            "x": base_x,
            "y": base_y,
            "width": 80.0,
            "height": 40.0,
            "element_id": part_elem.elem_id,
            "properties": {"definition": target_id},
            "hidden": not visible,
        }
        base_y += 60.0
        diag.objects.append(obj_dict)
        added.append(obj_dict)
        existing_keys.update(_part_elem_keys(part_elem))
        existing_defs.add(target_id)
        if app:
            for win in getattr(app, "ibd_windows", []):
                if getattr(win, "diagram_id", None) == diag.diag_id:
                    win.objects.append(SysMLObject(**obj_dict))
                    win.redraw()
                    win._sync_to_repository()

    boundary = next(
        (o for o in diag.objects if o.get("obj_type") == "Block Boundary"), None
    )
    if boundary and any(not a.get("hidden", False) for a in added):
        b_obj = SysMLObject(**boundary)
        objs = [SysMLObject(**o) for o in diag.objects]
        ensure_boundary_contains_parts(b_obj, objs)
        boundary["width"] = b_obj.width
        boundary["height"] = b_obj.height
        boundary["x"] = b_obj.x
        boundary["y"] = b_obj.y
        if app:
            for win in getattr(app, "ibd_windows", []):
                if getattr(win, "diagram_id", None) == diag.diag_id:
                    for obj in win.objects:
                        if obj.obj_type == "Block Boundary":
                            obj.width = b_obj.width
                            obj.height = b_obj.height
                            obj.x = b_obj.x
                            obj.y = b_obj.y
                            win.redraw()
                            win._sync_to_repository()

    return added


def _propagate_boundary_parts(
    repo: SysMLRepository, block_id: str, parts: list[dict], app=None
) -> None:
    """Insert *parts* into diagrams containing boundaries for ``block_id``."""

    for diag in repo.diagrams.values():
        if diag.diag_type != "Internal Block Diagram":
            continue
        boundary = next(
            (
                o
                for o in getattr(diag, "objects", [])
                if o.get("obj_type") == "Block Boundary" and o.get("element_id") == block_id
            ),
            None,
        )
        if not boundary:
            continue
        diag.objects = getattr(diag, "objects", [])
        existing = {o.get("element_id") for o in diag.objects if o.get("obj_type") == "Part"}
        base_x = boundary["x"] - boundary["width"] / 2 + 30.0
        base_y = boundary["y"] - boundary["height"] / 2 + 30.0
        for obj in parts:
            if obj.get("element_id") in existing:
                continue
            new_obj = obj.copy()
            new_obj["obj_id"] = _get_next_id()
            new_obj["x"] = base_x
            new_obj["y"] = base_y
            new_obj["hidden"] = False
            diag.objects.append(new_obj)
            repo.add_element_to_diagram(diag.diag_id, new_obj["element_id"])
            base_y += 60.0
            if app:
                for win in getattr(app, "ibd_windows", []):
                    if getattr(win, "diagram_id", None) == diag.diag_id:
                        win.objects.append(SysMLObject(**new_obj))
                        win.redraw()
                        win._sync_to_repository()



def _sync_block_parts_from_ibd(repo: SysMLRepository, diag_id: str) -> None:
    """Ensure the block linked to ``diag_id`` lists all part definitions."""

    diag = repo.diagrams.get(diag_id)
    if not diag or diag.diag_type != "Internal Block Diagram":
        return
    block_id = (
        getattr(diag, "father", None)
        or next((eid for eid, did in repo.element_diagrams.items() if did == diag_id), None)
    )
    if not block_id or block_id not in repo.elements:
        return
    block = repo.elements[block_id]
    names = [
        p.strip()
        for p in block.properties.get("partProperties", "").split(",")
        if p.strip()
    ]
    bases = {n.split("[")[0].strip() for n in names}
    for obj in getattr(diag, "objects", []):
        if obj.get("obj_type") != "Part":
            continue
        def_id = obj.get("properties", {}).get("definition")
        if def_id and def_id in repo.elements:
            pname = repo.elements[def_id].name or def_id
            if pname not in bases:
                names.append(pname)
                bases.add(pname)
    if names:
        joined = ", ".join(names)
        block.properties["partProperties"] = joined
        for d in repo.diagrams.values():
            for o in getattr(d, "objects", []):
                if o.get("element_id") == block_id:
                    o.setdefault("properties", {})["partProperties"] = joined
        for child_id in _find_generalization_children(repo, block_id):
            inherit_block_properties(repo, child_id)


def _ensure_ibd_boundary(repo: SysMLRepository, diagram: SysMLDiagram, block_id: str, app=None) -> list[dict]:
    """Create a boundary object for the IBD father block if needed."""

    diagram.objects = getattr(diagram, "objects", [])
    boundary = next((o for o in diagram.objects if o.get("obj_type") == "Block Boundary"), None)
    added: list[dict] = []
    if not boundary:
        obj_dict = {
            "obj_id": _get_next_id(),
            "obj_type": "Block Boundary",
            "x": 100.0,
            "y": 80.0,
            "width": 200.0,
            "height": 120.0,
            "element_id": block_id,
            "properties": {"name": repo.elements.get(block_id).name or block_id},
        }
        diagram.objects.insert(0, obj_dict)
        added.append(obj_dict)
        added += _add_ports_for_boundary(repo, diagram, obj_dict, app=app)
    else:
        if boundary.get("element_id") != block_id:
            boundary["element_id"] = block_id
        added += _add_ports_for_boundary(repo, diagram, boundary, app=app)
    # propagate parts for the boundary from the block's own IBD or definition
    diag_id = repo.get_linked_diagram(block_id)
    src = repo.diagrams.get(diag_id)
    parts: list[dict] = []
    if src and src.diag_type == "Internal Block Diagram":
        parts = [o for o in getattr(src, "objects", []) if o.get("obj_type") == "Part"]
    else:
        block = repo.elements.get(block_id)
        if block:
            entries = [p for p in block.properties.get("partProperties", "").split(",") if p.strip()]
            base_x = boundary["x"] - boundary["width"] / 2 + 30.0
            base_y = boundary["y"] - boundary["height"] / 2 + 30.0
            for prop_name, blk_name in [parse_part_property(e) for e in entries]:
                target_id = next(
                    (eid for eid, elem in repo.elements.items() if elem.elem_type == "Block" and elem.name == blk_name),
                    None,
                )
                if not target_id:
                    continue
                part_elem = repo.create_element(
                    "Part",
                    name=prop_name,
                    properties={"definition": target_id, "force_ibd": "true"},
                    owner=repo.root_package.elem_id,
                )
                obj = {
                    "obj_id": _get_next_id(),
                    "obj_type": "Part",
                    "x": base_x,
                    "y": base_y,
                    "width": 80.0,
                    "height": 40.0,
                    "element_id": part_elem.elem_id,
                    "properties": {"definition": target_id},
                    "hidden": False,
                }
                base_y += 60.0
                parts.append(obj)
    if parts:
        _propagate_boundary_parts(repo, block_id, parts, app=app)
    return added


def _remove_ibd_boundary(repo: SysMLRepository, diagram: SysMLDiagram) -> None:
    """Remove boundary object and ports from the diagram."""

    diagram.objects = getattr(diagram, "objects", [])
    boundary = next((o for o in diagram.objects if o.get("obj_type") == "Block Boundary"), None)
    if not boundary:
        return
    bid = boundary.get("obj_id")
    diagram.objects = [o for o in diagram.objects if not (o.get("obj_type") == "Port" and o.get("properties", {}).get("parent") == str(bid))]
    diagram.objects.remove(boundary)


def set_ibd_father(
    repo: SysMLRepository, diagram: SysMLDiagram, father_id: str | None, app=None
) -> list[dict]:
    """Assign *father_id* as the block represented by *diagram*.

    Links the diagram to the block and syncs composite parts. Returns any added
    part object dictionaries."""

    prev = getattr(diagram, "father", None)
    diagram.father = father_id
    if prev and prev != father_id:
        repo.link_diagram(prev, None)
    if father_id:
        repo.link_diagram(father_id, diagram.diag_id)
    added = _sync_ibd_composite_parts(repo, father_id, app=app) if father_id else []
    if father_id:
        added += _ensure_ibd_boundary(repo, diagram, father_id, app=app)
        added += _sync_ibd_partproperty_parts(repo, father_id, app=app, visible=True)
        parts = [o for o in getattr(diagram, "objects", []) if o.get("obj_type") == "Part"]
        _propagate_boundary_parts(repo, father_id, parts, app=app)
    else:
        _remove_ibd_boundary(repo, diagram)
    return added


def link_block_to_ibd(
    repo: SysMLRepository, block_id: str, diag_id: str | None, app=None
) -> list[dict]:
    """Link *block_id* to *diag_id* and ensure the IBD boundary is created."""

    if diag_id and diag_id in repo.diagrams:
        diagram = repo.diagrams[diag_id]
        if diagram.diag_type == "Internal Block Diagram":
            return set_ibd_father(repo, diagram, block_id, app=app)
    repo.link_diagram(block_id, diag_id)
    return []


def update_block_parts_from_ibd(repo: SysMLRepository, diagram: SysMLDiagram) -> None:
    """Sync the father block's ``partProperties`` from diagram part objects."""

    if diagram.diag_type != "Internal Block Diagram":
        return
    block_id = getattr(diagram, "father", None)
    if not block_id:
        block_id = next((eid for eid, did in repo.element_diagrams.items() if did == diagram.diag_id), None)
    if not block_id or block_id not in repo.elements:
        return
    block = repo.elements[block_id]
    existing = [p.strip() for p in block.properties.get("partProperties", "").split(",") if p.strip()]
    diag_entries: list[tuple[str, str]] = []
    diag_bases: set[str] = set()
    for obj in getattr(diagram, "objects", []):
        if obj.get("obj_type") != "Part":
            continue
        name = ""
        elem_id = obj.get("element_id")
        if elem_id and elem_id in repo.elements:
            elem = repo.elements[elem_id]
            name = elem.name or elem.properties.get("component", "")
        if not name:
            def_id = obj.get("properties", {}).get("definition")
            if def_id and def_id in repo.elements:
                name = repo.elements[def_id].name or def_id
        if not name:
            name = obj.get("properties", {}).get("component", "")
        base = name.split("[")[0].strip() if name else ""
        def_id = obj.get("properties", {}).get("definition")
        base_def = ""
        if def_id and def_id in repo.elements:
            base_def = (repo.elements[def_id].name or def_id).split("[")[0].strip()
        key = base_def or base
        if key and key not in diag_bases:
            diag_entries.append((key, name or key))
            diag_bases.add(key)

    merged_names = list(existing)
    bases = {n.split("[")[0].strip() for n in merged_names}
    for base, name in diag_entries:
        if base not in bases:
            merged_names.append(name)
            bases.add(base)

    if merged_names != existing:
        joined = ", ".join(merged_names)
        block.properties["partProperties"] = joined
        for d in repo.diagrams.values():
            for o in getattr(d, "objects", []):
                if o.get("element_id") == block_id:
                    o.setdefault("properties", {})["partProperties"] = joined
        for child_id in _find_generalization_children(repo, block_id):
            inherit_block_properties(repo, child_id)
        repo.touch_element(block_id)


def remove_aggregation_part(
    repo: SysMLRepository,
    whole_id: str,
    part_id: str,
    remove_object: bool = False,
    app=None,
) -> None:
    """Remove *part_id* from *whole_id* block's part list.

    If *remove_object* is True, also delete any part object representing
    *part_id* in the Internal Block Diagram linked to *whole_id*.
    """
    repo.push_undo_state()
    whole = repo.elements.get(whole_id)
    part = repo.elements.get(part_id)
    if not whole or not part:
        return
    name = part.name or part_id
    parts = [p.strip() for p in whole.properties.get("partProperties", "").split(",") if p.strip()]
    new_parts = [p for p in parts if p.split("[")[0].strip() != name]
    if len(new_parts) != len(parts):
        if new_parts:
            whole.properties["partProperties"] = ", ".join(new_parts)
        else:
            whole.properties.pop("partProperties", None)
        for d in repo.diagrams.values():
            for o in getattr(d, "objects", []):
                if o.get("element_id") == whole_id:
                    if new_parts:
                        o.setdefault("properties", {})["partProperties"] = ", ".join(new_parts)
                    else:
                        o.setdefault("properties", {}).pop("partProperties", None)

    # propagate removals to any generalization children
    for child_id in _find_generalization_children(repo, whole_id):
        child = repo.elements.get(child_id)
        if not child:
            continue
        child_parts = [
            p.strip() for p in child.properties.get("partProperties", "").split(",") if p.strip()
        ]
        child_parts = [p for p in child_parts if p.split("[")[0].strip() != name]
        if child_parts:
            child.properties["partProperties"] = ", ".join(child_parts)
        else:
            child.properties.pop("partProperties", None)
        for d in repo.diagrams.values():
            for o in getattr(d, "objects", []):
                if o.get("element_id") == child_id:
                    if child_parts:
                        o.setdefault("properties", {})["partProperties"] = ", ".join(child_parts)
                    else:
                        o.setdefault("properties", {}).pop("partProperties", None)
    if remove_object:
        diag_id = repo.get_linked_diagram(whole_id)
        diag = repo.diagrams.get(diag_id)
        if diag and diag.diag_type == "Internal Block Diagram":
            diag.objects = getattr(diag, "objects", [])
            before = len(diag.objects)
            diag.objects = [
                o
                for o in diag.objects
                if not (
                    o.get("obj_type") == "Part"
                    and o.get("properties", {}).get("definition") == part_id
                )
            ]
            if len(diag.objects) != before and app:
                for win in getattr(app, "ibd_windows", []):
                    if getattr(win, "diagram_id", None) == diag_id:
                        win.objects = [
                            o
                            for o in win.objects
                            if not (
                                o.obj_type == "Part"
                                and o.properties.get("definition") == part_id
                            )
                        ]
                        win.redraw()
                        win._sync_to_repository()
        # remove stored part element if any
        rel = next(
            (
                r
                for r in repo.relationships
                if r.rel_type in ("Composite Aggregation", "Aggregation")
                and r.source == whole_id
                and r.target == part_id
            ),
            None,
        )
        if rel:
            pid = rel.properties.pop("part_elem", None)
            if pid and pid in repo.elements:
                repo.delete_element(pid)
                repo._undo_stack.pop()


def _propagate_part_removal(
    repo: SysMLRepository,
    block_id: str,
    prop_name: str,
    target_id: str,
    remove_object: bool = False,
    app=None,
) -> None:
    """Helper used by :func:`remove_partproperty_entry` to drop a part.

    This delegates to :func:`remove_aggregation_part` which already handles
    updating descendant blocks and any diagrams linked to ``block_id`` when
    ``remove_object`` is ``True``.
    """

    remove_aggregation_part(
        repo,
        block_id,
        target_id,
        remove_object=remove_object,
        app=app,
    )


def _remove_parts_from_ibd(
    repo: SysMLRepository, block_id: str, target_id: str, app=None
) -> None:
    """Remove part objects referencing ``target_id`` from ``block_id``'s IBD."""

    diag_id = repo.get_linked_diagram(block_id)
    diag = repo.diagrams.get(diag_id)
    if not diag or diag.diag_type != "Internal Block Diagram":
        return
    diag.objects = getattr(diag, "objects", [])
    before = len(diag.objects)
    diag.objects = [
        o
        for o in diag.objects
        if not (
            o.get("obj_type") == "Part"
            and o.get("properties", {}).get("definition") == target_id
        )
    ]
    if len(diag.objects) != before and app:
        for win in getattr(app, "ibd_windows", []):
            if getattr(win, "diagram_id", None) == diag_id:
                win.objects = [
                    o
                    for o in win.objects
                    if not (
                        o.obj_type == "Part"
                        and o.properties.get("definition") == target_id
                    )
                ]
                win.redraw()
                win._sync_to_repository()


def _propagate_ibd_part_removal(
    repo: SysMLRepository, block_id: str, target_id: str, app=None
) -> None:
    """Recursively remove part objects from descendants of ``block_id``."""

    for child_id in _find_generalization_children(repo, block_id):
        _remove_parts_from_ibd(repo, child_id, target_id, app=app)
        _propagate_ibd_part_removal(repo, child_id, target_id, app=app)


def remove_partproperty_entry(
    repo: SysMLRepository, block_id: str, entry: str, app=None
) -> None:
    """Remove a part property entry and update descendant diagrams."""
    repo.push_undo_state()

    block = repo.elements.get(block_id)
    if not block:
        return
    prop_name, blk_name = parse_part_property(entry)
    target_id = next(
        (
            eid
            for eid, elem in repo.elements.items()
            if elem.elem_type == "Block" and elem.name == blk_name
        ),
        None,
    )
    if not target_id:
        return

    parts = [p.strip() for p in block.properties.get("partProperties", "").split(",") if p.strip()]
    parts = [p for p in parts if _part_prop_key(p) != _part_prop_key(entry)]
    if parts:
        block.properties["partProperties"] = ", ".join(parts)
    else:
        block.properties.pop("partProperties", None)
    for d in repo.diagrams.values():
        for o in getattr(d, "objects", []):
            if o.get("element_id") == block_id:
                if parts:
                    o.setdefault("properties", {})["partProperties"] = ", ".join(parts)
                else:
                    o.setdefault("properties", {}).pop("partProperties", None)

    _propagate_part_removal(
        repo,
        block_id,
        prop_name,
        target_id,
        remove_object=True,
        app=app,
    )
    _remove_parts_from_ibd(repo, block_id, target_id, app=app)
    _propagate_ibd_part_removal(repo, block_id, target_id, app=app)


def inherit_block_properties(repo: SysMLRepository, block_id: str) -> None:
    """Merge parent block properties into the given block."""
    extend_block_parts_with_parents(repo, block_id)
    block = repo.elements.get(block_id)
    if not block:
        return
    for parent_id in _find_parent_blocks(repo, block_id):
        parent = repo.elements.get(parent_id)
        if not parent:
            continue
        for prop in SYSML_PROPERTIES.get("BlockUsage", []):
            if prop == "partProperties":
                continue
            if prop == "operations":
                child_ops = parse_operations(block.properties.get(prop, ""))
                child_names = {o.name for o in child_ops}
                for op in parse_operations(parent.properties.get(prop, "")):
                    if op.name not in child_names:
                        child_ops.append(op)
                        child_names.add(op.name)
                block.properties[prop] = operations_to_json(child_ops)
            else:
                child_vals = [
                    v.strip() for v in block.properties.get(prop, "").split(",") if v.strip()
                ]
                parent_vals = [
                    v.strip() for v in parent.properties.get(prop, "").split(",") if v.strip()
                ]
                for v in parent_vals:
                    if v not in child_vals:
                        child_vals.append(v)
                if child_vals:
                    block.properties[prop] = ", ".join(child_vals)
    for d in repo.diagrams.values():
        for o in getattr(d, "objects", []):
            if o.get("element_id") == block_id:
                o.setdefault("properties", {}).update(block.properties)


def remove_inherited_block_properties(repo: SysMLRepository, child_id: str, parent_id: str) -> None:
    """Remove properties of *parent_id* from *child_id* block."""
    child = repo.elements.get(child_id)
    parent = repo.elements.get(parent_id)
    if not child or not parent:
        return

    # handle partProperties separately
    child_parts = [
        v.strip() for v in child.properties.get("partProperties", "").split(",") if v.strip()
    ]
    parent_parts = [
        v.strip() for v in parent.properties.get("partProperties", "").split(",") if v.strip()
    ]
    parent_bases = {p.split("[")[0].strip() for p in parent_parts}

    removed_parts = [
        v for v in child_parts if v.split("[")[0].strip() in parent_bases
    ]

    child_parts = [
        v for v in child_parts if v.split("[")[0].strip() not in parent_bases
    ]

    if child_parts:
        child.properties["partProperties"] = ", ".join(child_parts)
    else:
        child.properties.pop("partProperties", None)

    # remove inherited part objects from child IBDs
    for entry in removed_parts:
        _pname, blk_name = parse_part_property(entry)
        target_id = next(
            (
                eid
                for eid, elem in repo.elements.items()
                if elem.elem_type == "Block" and elem.name == blk_name
            ),
            None,
        )
        if target_id:
            _remove_parts_from_ibd(repo, child_id, target_id)
            _propagate_ibd_part_removal(repo, child_id, target_id)

    for prop in SYSML_PROPERTIES.get("BlockUsage", []):
        if prop == "partProperties":
            continue
        if prop == "operations":
            child_ops = parse_operations(child.properties.get(prop, ""))
            parent_ops = parse_operations(parent.properties.get(prop, ""))
            parent_names = {o.name for o in parent_ops}
            child_ops = [op for op in child_ops if op.name not in parent_names]
            if child_ops:
                child.properties[prop] = operations_to_json(child_ops)
            else:
                child.properties.pop(prop, None)
        else:
            child_vals = [v.strip() for v in child.properties.get(prop, "").split(",") if v.strip()]
            parent_vals = [
                v.strip() for v in parent.properties.get(prop, "").split(",") if v.strip()
            ]
            child_vals = [v for v in child_vals if v not in parent_vals]
            if child_vals:
                child.properties[prop] = ", ".join(child_vals)
            else:
                child.properties.pop(prop, None)

    # propagate changes to diagrams referencing the child block
    for d in repo.diagrams.values():
        for o in getattr(d, "objects", []):
            if o.get("element_id") == child_id:
                o.setdefault("properties", {}).update(child.properties)

    # ensure child's internal block diagram matches updated parts
    _sync_ibd_partproperty_parts(repo, child_id, hidden=False)


def inherit_father_parts(repo: SysMLRepository, diagram: SysMLDiagram) -> list[dict]:
    """Copy parts from the diagram's father block into the diagram.

    Returns a list with the inherited object dictionaries (parts and ports)."""
    father = getattr(diagram, "father", None)
    if not father:
        return []
    father_diag_id = repo.get_linked_diagram(father)
    father_diag = repo.diagrams.get(father_diag_id)
    if not father_diag:
        return []
    diagram.objects = getattr(diagram, "objects", [])
    added: list[dict] = []
    # Track existing parts by element id and canonical name to avoid duplicates
    existing = {o.get("element_id") for o in diagram.objects if o.get("obj_type") == "Part"}
    existing_keys: set[str] = set()
    for eid in existing:
        if eid in repo.elements:
            existing_keys.update(_part_elem_keys(repo.elements[eid]))

    # Map of source part obj_id -> new obj_id so ports can be updated
    part_map: dict[int, int] = {}

    # Pre-filter father diagram objects so the logic matches older releases
    father_parts = [
        o for o in getattr(father_diag, "objects", []) if o.get("obj_type") == "Part"
    ]

    # ------------------------------------------------------------------
    # Copy parts from the father diagram
    # ------------------------------------------------------------------
    for obj in father_parts:
        if obj.get("obj_type") != "Part":
            continue
        if obj.get("element_id") in existing:
            continue
        key_set: set[str] = set()
        if obj.get("element_id") in repo.elements:
            key_set = _part_elem_keys(repo.elements[obj.get("element_id")])
        if any(k in existing_keys for k in key_set):
            continue
        new_obj = obj.copy()
        new_obj["obj_id"] = _get_next_id()
        diagram.objects.append(new_obj)
        repo.add_element_to_diagram(diagram.diag_id, obj.get("element_id"))
        added.append(new_obj)
        part_map[obj.get("obj_id")] = new_obj["obj_id"]
        existing.add(obj.get("element_id"))
        if key_set:
            existing_keys.update(key_set)

    # ------------------------------------------------------------------
    # Copy ports belonging to the inherited parts so orientation and other
    # attributes are preserved. Only ports referencing a copied part are
    # considered.
    # ------------------------------------------------------------------
    for obj in getattr(father_diag, "objects", []):
        if obj.get("obj_type") != "Port":
            continue
        parent_id = obj.get("properties", {}).get("parent")
        if not parent_id:
            continue
        try:
            parent_id_int = int(parent_id)
        except Exception:
            continue
        new_parent = part_map.get(parent_id_int)
        if not new_parent:
            continue
        new_obj = obj.copy()
        new_obj["obj_id"] = _get_next_id()
        new_obj.setdefault("properties", {})["parent"] = str(new_parent)
        diagram.objects.append(new_obj)
        added.append(new_obj)
    # update child block partProperties with inherited names
    child_id = next(
        (eid for eid, did in repo.element_diagrams.items() if did == diagram.diag_id),
        None,
    )
    if child_id and father in repo.elements:
        child = repo.elements[child_id]
        father_elem = repo.elements[father]
        names = [
            p.strip() for p in child.properties.get("partProperties", "").split(",") if p.strip()
        ]
        father_names = [
            p.strip()
            for p in father_elem.properties.get("partProperties", "").split(",")
            if p.strip()
        ]
        for n in father_names:
            if n not in names:
                names.append(n)
        joined = ", ".join(names)
        child.properties["partProperties"] = joined
        for d in repo.diagrams.values():
            for o in getattr(d, "objects", []):
                if o.get("element_id") == child_id:
                    o.setdefault("properties", {})["partProperties"] = joined
        inherit_block_properties(repo, child_id)
    return added


@dataclass
class SysMLObject:
    obj_id: int
    obj_type: str
    x: float
    y: float
    element_id: str | None = None
    width: float = 80.0
    height: float = 40.0
    properties: Dict[str, str] = field(default_factory=dict)
    requirements: List[dict] = field(default_factory=list)
    locked: bool = False
    hidden: bool = False
    collapsed: Dict[str, bool] = field(default_factory=dict)
    phase: str | None = field(default_factory=lambda: SysMLRepository.get_instance().active_phase)


@dataclass
class OperationParameter:
    """Representation of a SysML parameter."""

    name: str
    type: str = ""
    direction: str = "in"


@dataclass
class OperationDefinition:
    """Operation with a list of parameters and an optional return type."""

    name: str
    parameters: List[OperationParameter] = field(default_factory=list)
    return_type: str = ""


def calculate_allocated_asil(requirements: List[dict]) -> str:
    """Return highest ASIL level from the given requirement list."""
    asil = "QM"
    for req in requirements:
        level = req.get("asil") or global_requirements.get(req.get("id"), {}).get("asil", "QM")
        if ASIL_ORDER.get(level, 0) > ASIL_ORDER.get(asil, 0):
            asil = level
    return asil


def remove_orphan_ports(objs: List[SysMLObject]) -> None:
    """Delete ports that don't reference an existing parent part."""
    part_ids = {o.obj_id for o in objs if o.obj_type in ("Part", "Block Boundary")}
    filtered: List[SysMLObject] = []
    for o in objs:
        if o.obj_type == "Port":
            pid = o.properties.get("parent")
            if not pid or int(pid) not in part_ids:
                continue
        filtered.append(o)
    objs[:] = filtered


def rename_port(
    repo: SysMLRepository, port: SysMLObject, objs: List[SysMLObject], new_name: str
) -> None:
    """Rename *port* and update its parent's port list."""

    old_name = port.properties.get("name", "")
    if old_name == new_name:
        return
    port.properties["name"] = new_name
    if port.element_id and port.element_id in repo.elements:
        repo.elements[port.element_id].name = new_name
        repo.elements[port.element_id].properties["name"] = new_name
    parent_id = port.properties.get("parent")
    if not parent_id:
        return
    try:
        pid = int(parent_id)
    except (TypeError, ValueError):
        return
    parent = next((o for o in objs if o.obj_id == pid), None)
    if not parent:
        return
    ports = [p.strip() for p in parent.properties.get("ports", "").split(",") if p.strip()]
    if old_name in ports:
        ports[ports.index(old_name)] = new_name
    elif new_name not in ports:
        ports.append(new_name)
    joined = ", ".join(ports)
    parent.properties["ports"] = joined
    if parent.element_id and parent.element_id in repo.elements:
        repo.elements[parent.element_id].properties["ports"] = joined


def remove_port(
    repo: SysMLRepository, port: SysMLObject, objs: List[SysMLObject]
) -> None:
    """Remove *port* from *objs* and update the parent's port list."""

    parent_id = port.properties.get("parent")
    if parent_id:
        try:
            pid = int(parent_id)
        except (TypeError, ValueError):
            pid = None
        if pid is not None:
            parent = next((o for o in objs if o.obj_id == pid), None)
            if parent:
                ports = [p.strip() for p in parent.properties.get("ports", "").split(",") if p.strip()]
                if port.properties.get("name") in ports:
                    ports.remove(port.properties.get("name"))
                    joined = ", ".join(ports)
                    parent.properties["ports"] = joined
                    if parent.element_id and parent.element_id in repo.elements:
                        repo.elements[parent.element_id].properties["ports"] = joined


def snap_port_to_parent_obj(port: SysMLObject, parent: SysMLObject) -> None:
    """Position *port* along the closest edge of *parent*."""
    px = port.x
    py = port.y
    left = parent.x - parent.width / 2
    right = parent.x + parent.width / 2
    top = parent.y - parent.height / 2
    bottom = parent.y + parent.height / 2
    d_left = abs(px - left)
    d_right = abs(px - right)
    d_top = abs(py - top)
    d_bottom = abs(py - bottom)
    min_d = min(d_left, d_right, d_top, d_bottom)
    if min_d == d_left:
        port.x = left
        port.y = min(max(py, top), bottom)
        port.properties["side"] = "W"
    elif min_d == d_right:
        port.x = right
        port.y = min(max(py, top), bottom)
        port.properties["side"] = "E"
    elif min_d == d_top:
        port.y = top
        port.x = min(max(px, left), right)
        port.properties["side"] = "N"
    else:
        port.y = bottom
        port.x = min(max(px, left), right)
        port.properties["side"] = "S"


def update_ports_for_part(part: SysMLObject, objs: List[SysMLObject]) -> None:
    """Snap all ports referencing *part* to its border."""
    for o in objs:
        if o.obj_type == "Port" and o.properties.get("parent") == str(part.obj_id):
            snap_port_to_parent_obj(o, part)


def update_ports_for_boundary(boundary: SysMLObject, objs: List[SysMLObject]) -> None:
    """Snap all ports referencing *boundary* to its border."""
    for o in objs:
        if o.obj_type == "Port" and o.properties.get("parent") == str(boundary.obj_id):
            snap_port_to_parent_obj(o, boundary)


def _boundary_min_size(boundary: SysMLObject, objs: List[SysMLObject]) -> tuple[float, float]:
    """Return minimum width and height for *boundary* to contain all parts."""
    parts = [
        o for o in objs if o.obj_type == "Part" and not getattr(o, "hidden", False)
    ]
    if not parts:
        return (20.0, 20.0)
    pad = 20.0
    left = min(p.x - p.width / 2 for p in parts)
    right = max(p.x + p.width / 2 for p in parts)
    top = min(p.y - p.height / 2 for p in parts)
    bottom = max(p.y + p.height / 2 for p in parts)
    return right - left + pad, bottom - top + pad


def ensure_boundary_contains_parts(boundary: SysMLObject, objs: List[SysMLObject]) -> None:
    """Expand *boundary* if any part lies outside its borders."""
    parts = [
        o for o in objs if o.obj_type == "Part" and not getattr(o, "hidden", False)
    ]
    if not parts:
        return
    min_w, min_h = _boundary_min_size(boundary, objs)
    if boundary.width < min_w:
        boundary.width = min_w
    if boundary.height < min_h:
        boundary.height = min_h
    left = min(p.x - p.width / 2 for p in parts)
    right = max(p.x + p.width / 2 for p in parts)
    top = min(p.y - p.height / 2 for p in parts)
    bottom = max(p.y + p.height / 2 for p in parts)
    boundary.x = (left + right) / 2
    boundary.y = (top + bottom) / 2


def _add_ports_for_part(
    repo: SysMLRepository,
    diag: SysMLDiagram,
    part_obj: dict,
    app=None,
) -> list[dict]:
    """Create port objects for ``part_obj`` based on its block definition."""

    part_elem = repo.elements.get(part_obj.get("element_id"))
    if not part_elem:
        return []
    block_id = part_elem.properties.get("definition")
    names: list[str] = []
    if block_id and block_id in repo.elements:
        block_elem = repo.elements[block_id]
        names.extend([
            p.strip()
            for p in block_elem.properties.get("ports", "").split(",")
            if p.strip()
        ])
    names.extend([
        p.strip() for p in part_elem.properties.get("ports", "").split(",") if p.strip()
    ])
    if not names:
        return []
    added: list[dict] = []
    parent = SysMLObject(
        part_obj.get("obj_id"),
        "Part",
        part_obj.get("x", 0.0),
        part_obj.get("y", 0.0),
        element_id=part_obj.get("element_id"),
        width=part_obj.get("width", 80.0),
        height=part_obj.get("height", 40.0),
        properties=part_obj.get("properties", {}).copy(),
        locked=part_obj.get("locked", False),
    )
    for name in names:
        port = SysMLObject(
            _get_next_id(),
            "Port",
            parent.x + parent.width / 2 + 20,
            parent.y,
            properties={
                "name": name,
                "parent": str(parent.obj_id),
                "side": "E",
                "labelX": "8",
                "labelY": "-8",
            },
        )
        snap_port_to_parent_obj(port, parent)
        port_dict = asdict(port)
        diag.objects.append(port_dict)
        added.append(port_dict)
        if app:
            for win in getattr(app, "ibd_windows", []):
                if getattr(win, "diagram_id", None) == diag.diag_id:
                    win.objects.append(port)
                    win.redraw()
                    win._sync_to_repository()
    part_obj.setdefault("properties", {})["ports"] = ", ".join(names)
    part_elem.properties["ports"] = ", ".join(names)
    return added


def _add_ports_for_boundary(
    repo: SysMLRepository,
    diag: SysMLDiagram,
    boundary_obj: dict,
    app=None,
) -> list[dict]:
    """Create port objects for a boundary based on its block definition."""

    block = repo.elements.get(boundary_obj.get("element_id"))
    if not block:
        return []
    names = [p.strip() for p in block.properties.get("ports", "").split(",") if p.strip()]
    if not names:
        return []
    added: list[dict] = []
    parent = SysMLObject(
        boundary_obj.get("obj_id"),
        "Block Boundary",
        boundary_obj.get("x", 0.0),
        boundary_obj.get("y", 0.0),
        width=boundary_obj.get("width", 160.0),
        height=boundary_obj.get("height", 100.0),
    )
    for name in names:
        port = SysMLObject(
            _get_next_id(),
            "Port",
            parent.x + parent.width / 2 + 20,
            parent.y,
            properties={
                "name": name,
                "parent": str(parent.obj_id),
                "side": "E",
                "labelX": "8",
                "labelY": "-8",
            },
        )
        snap_port_to_parent_obj(port, parent)
        port_dict = asdict(port)
        diag.objects.append(port_dict)
        added.append(port_dict)
        if app:
            for win in getattr(app, "ibd_windows", []):
                if getattr(win, "diagram_id", None) == diag.diag_id:
                    win.objects.append(port)
                    win.redraw()
                    win._sync_to_repository()
    boundary_obj.setdefault("properties", {})["ports"] = ", ".join(names)
    block.properties["ports"] = ", ".join(names)
    return added


def _sync_ports_for_part(repo: SysMLRepository, diag: SysMLDiagram, part_obj: dict) -> None:
    """Update port objects for ``part_obj`` to match its definition."""

    part_elem = repo.elements.get(part_obj.get("element_id"))
    if not part_elem:
        return
    block_id = part_elem.properties.get("definition")
    names: list[str] = []
    if block_id and block_id in repo.elements:
        block_elem = repo.elements[block_id]
        names.extend([
            p.strip()
            for p in block_elem.properties.get("ports", "").split(",")
            if p.strip()
        ])
    names.extend([
        p.strip() for p in part_elem.properties.get("ports", "").split(",") if p.strip()
    ])
    names = list(dict.fromkeys(names))
    part_obj.setdefault("properties", {})["ports"] = ", ".join(names)
    part_elem.properties["ports"] = ", ".join(names)

    existing = [
        o
        for o in list(diag.objects)
        if o.get("obj_type") == "Port" and o.get("properties", {}).get("parent") == str(part_obj.get("obj_id"))
    ]
    existing_names = {o.get("properties", {}).get("name") for o in existing}
    parent = SysMLObject(
        part_obj.get("obj_id"),
        "Part",
        part_obj.get("x", 0.0),
        part_obj.get("y", 0.0),
        width=part_obj.get("width", 80.0),
        height=part_obj.get("height", 40.0),
    )
    for name in names:
        if name in existing_names:
            continue
        port = SysMLObject(
            _get_next_id(),
            "Port",
            parent.x + parent.width / 2 + 20,
            parent.y,
            properties={
                "name": name,
                "parent": str(parent.obj_id),
                "side": "E",
                "labelX": "8",
                "labelY": "-8",
            },
        )
        snap_port_to_parent_obj(port, parent)
        diag.objects.append(asdict(port))
    for obj in existing:
        if obj.get("properties", {}).get("name") not in names:
            diag.objects.remove(obj)


def _sync_ports_for_boundary(repo: SysMLRepository, diag: SysMLDiagram, boundary_obj: dict) -> None:
    """Update port objects for ``boundary_obj`` to match its block definition."""

    block_id = boundary_obj.get("element_id")
    block_elem = repo.elements.get(block_id)
    if not block_elem:
        return
    names = [p.strip() for p in block_elem.properties.get("ports", "").split(",") if p.strip()]
    boundary_obj.setdefault("properties", {})["ports"] = ", ".join(names)

    existing = [
        o
        for o in list(diag.objects)
        if o.get("obj_type") == "Port" and o.get("properties", {}).get("parent") == str(boundary_obj.get("obj_id"))
    ]
    existing_names = {o.get("properties", {}).get("name") for o in existing}
    parent = SysMLObject(
        boundary_obj.get("obj_id"),
        "Block Boundary",
        boundary_obj.get("x", 0.0),
        boundary_obj.get("y", 0.0),
        width=boundary_obj.get("width", 160.0),
        height=boundary_obj.get("height", 100.0),
    )
    for name in names:
        if name in existing_names:
            continue
        port = SysMLObject(
            _get_next_id(),
            "Port",
            parent.x + parent.width / 2 + 20,
            parent.y,
            properties={
                "name": name,
                "parent": str(parent.obj_id),
                "side": "E",
                "labelX": "8",
                "labelY": "-8",
            },
        )
        snap_port_to_parent_obj(port, parent)
        diag.objects.append(asdict(port))
    for obj in existing:
        if obj.get("properties", {}).get("name") not in names:
            diag.objects.remove(obj)


def propagate_block_port_changes(repo: SysMLRepository, block_id: str) -> None:
    """Propagate port updates on ``block_id`` to all parts referencing it."""

    block = repo.elements.get(block_id)
    if not block or block.elem_type != "Block":
        return
    names = [p.strip() for p in block.properties.get("ports", "").split(",") if p.strip()]
    for elem in repo.elements.values():
        if elem.elem_type != "Part" or elem.properties.get("definition") != block_id:
            continue
        elem.properties["ports"] = ", ".join(names)
        for diag in repo.diagrams.values():
            if diag.diag_type != "Internal Block Diagram":
                continue
            diag.objects = getattr(diag, "objects", [])
            updated = False
            for obj in diag.objects:
                if obj.get("obj_type") == "Part" and obj.get("element_id") == elem.elem_id:
                    obj.setdefault("properties", {})["ports"] = ", ".join(names)
                    _sync_ports_for_part(repo, diag, obj)
                    updated = True
            if updated:
                repo.touch_diagram(diag.diag_id)

    # update boundaries referencing this block
    for diag in repo.diagrams.values():
        if diag.diag_type != "Internal Block Diagram":
            continue
        diag.objects = getattr(diag, "objects", [])
        updated = False
        for obj in diag.objects:
            if obj.get("obj_type") == "Block Boundary" and obj.get("element_id") == block_id:
                obj.setdefault("properties", {})["ports"] = ", ".join(names)
                _sync_ports_for_boundary(repo, diag, obj)
                updated = True
        if updated:
            repo.touch_diagram(diag.diag_id)


def propagate_block_part_changes(repo: SysMLRepository, block_id: str) -> None:
    """Propagate attribute updates on ``block_id`` to all parts referencing it."""

    block = repo.elements.get(block_id)
    if not block or block.elem_type != "Block":
        return
    props = ["operations", "partProperties", "behaviors"]
    for elem in repo.elements.values():
        if elem.elem_type != "Part" or elem.properties.get("definition") != block_id:
            continue
        elem.name = repo.ensure_unique_element_name(block.name, elem.elem_id)

        for prop in props:
            if prop in block.properties:
                elem.properties[prop] = block.properties[prop]
            else:
                elem.properties.pop(prop, None)


def _propagate_block_requirement_changes(
    repo: SysMLRepository, parent_id: str, child_id: str
) -> None:
    """Add requirements from ``parent_id`` objects to ``child_id`` objects."""

    parent_req_ids: set[str] = set()
    for diag in repo.diagrams.values():
        for obj in getattr(diag, "objects", []):
            if obj.get("element_id") != block_id:
                continue
            for req in obj.get("requirements", []):
                if req not in reqs:
                    reqs.append(req)
    return reqs


def _collect_block_requirements(repo: SysMLRepository, block_id: str) -> list[dict]:
    """Return a unique list of requirements associated with ``block_id``."""

    reqs: list[dict] = []
    seen: set[str] = set()
    for diag in repo.diagrams.values():
        for obj in getattr(diag, "objects", []):
            if obj.get("element_id") != block_id:
                continue
            for req in obj.get("requirements", []):
                rid = req.get("id")
                if rid is not None:
                    if rid in seen:
                        continue
                    seen.add(rid)
                reqs.append(req)
    return reqs


def _propagate_requirements(repo: SysMLRepository, src_reqs: list[dict], dst_id: str) -> None:
    """Merge *src_reqs* into all objects referencing *dst_id*."""
    if not src_reqs:
        return
    for diag in repo.diagrams.values():
        updated = False
        for obj in getattr(diag, "objects", []):
            if obj.get("element_id") != dst_id:
                continue
            obj.setdefault("requirements", [])
            existing = {r.get("id") for r in obj["requirements"]}
            for req in src_reqs:
                if req.get("id") not in existing:
                    obj["requirements"].append(req)
                    existing.add(req.get("id"))
                    updated = True
        if updated:
            repo.touch_diagram(diag.diag_id)


def propagate_block_changes(repo: SysMLRepository, block_id: str, visited: set[str] | None = None) -> None:
    """Propagate updates on ``block_id`` to blocks that generalize it."""

    if visited is None:
        visited = set()
    if block_id in visited:
        return
    visited.add(block_id)
    reqs = _collect_block_requirements(repo, block_id)
    for child_id in _find_generalization_children(repo, block_id):
        inherit_block_properties(repo, child_id)
        propagate_block_port_changes(repo, child_id)
        _propagate_requirements(repo, reqs, child_id)
        _sync_ibd_partproperty_parts(repo, child_id, hidden=False)
        propagate_block_changes(repo, child_id, visited)


def parse_operations(raw: str) -> List[OperationDefinition]:
    """Return a list of operations parsed from *raw* JSON or comma text."""
    if not raw:
        return []
    try:
        data = json.loads(raw)
        ops = []
        for o in data:
            params = [OperationParameter(**p) for p in o.get("parameters", [])]
            ops.append(OperationDefinition(o.get("name", ""), params, o.get("return_type", "")))
        return ops
    except Exception:
        return [OperationDefinition(n) for n in [p.strip() for p in raw.split(",") if p.strip()]]


def format_operation(op: OperationDefinition) -> str:
    """Return a readable string for an operation."""
    plist = ", ".join(f"{p.name}: {p.type}" if p.type else p.name for p in op.parameters)
    ret = f" : {op.return_type}" if op.return_type else ""
    return f"{op.name}({plist}){ret}"


def operations_to_json(ops: List[OperationDefinition]) -> str:
    return json.dumps([asdict(o) for o in ops])


@dataclass
class BehaviorAssignment:
    """Mapping of a block operation to an activity diagram."""

    operation: str
    diagram: str


def parse_behaviors(raw: str) -> List[BehaviorAssignment]:
    """Return a list of BehaviorAssignments from *raw* JSON."""
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return [BehaviorAssignment(**b) for b in data]
    except Exception:
        return []


def behaviors_to_json(behaviors: List[BehaviorAssignment]) -> str:
    return json.dumps([asdict(b) for b in behaviors])


def get_block_behavior_elements(repo: "SysMLRepository", block_id: str) -> List["SysMLElement"]:
    """Return Action, Activity and Operation elements that define behaviors of ``block_id``."""
    elements: List["SysMLElement"] = []
    block = repo.elements.get(block_id)
    if not block:
        return elements
    behaviors = parse_behaviors(block.properties.get("behaviors", ""))
    for beh in behaviors:
        # operations with matching name
        for elem in repo.elements.values():
            if elem.elem_type == "Operation" and elem.name == beh.operation:
                elements.append(elem)
        diag = repo.diagrams.get(beh.diagram)
        if not diag:
            continue
        # elements referenced in the diagram
        for obj in getattr(diag, "objects", []):
            elem_id = obj.get("element_id")
            typ = obj.get("obj_type") or obj.get("type")
            if elem_id and typ in ("Action", "Action Usage", "CallBehaviorAction", "Activity"):
                elem = repo.elements.get(elem_id)
                if elem:
                    elements.append(elem)
        for elem_id in getattr(diag, "elements", []):
            elem = repo.elements.get(elem_id)
            if elem and elem.elem_type in ("Action", "Activity"):
                elements.append(elem)
    seen: set[str] = set()
    unique = []
    for e in elements:
        if e.elem_id not in seen:
            unique.append(e)
            seen.add(e.elem_id)
    return unique


@dataclass
class DiagramConnection:
    src: int
    dst: int
    conn_type: str
    style: str = "Straight"  # Straight, Squared, Custom
    points: List[Tuple[float, float]] = field(default_factory=list)
    src_pos: Tuple[float, float] | None = None  # relative anchor (x,y)
    dst_pos: Tuple[float, float] | None = None
    name: str = ""
    arrow: str = "none"  # none, forward, backward, both
    mid_arrow: bool = False
    guard: List[str] = field(default_factory=list)
    guard_ops: List[str] = field(default_factory=list)
    element_id: str = ""
    stereotype: str = ""
    multiplicity: str = ""
    stereotype: str = ""
    phase: str | None = field(default_factory=lambda: SysMLRepository.get_instance().active_phase)


def format_control_flow_label(
    conn: DiagramConnection, repo: "SysMLRepository", diag_type: str | None
) -> str:
    """Return the label to display for a connection.

    For control flow diagrams, guards are combined with configured logical
    operators and shown before the action or activity name.
    """
    label = conn.name or ""
    if conn.conn_type == "Control Action" and not label and conn.element_id:
        elem = repo.elements.get(conn.element_id)
        if elem:
            label = elem.name or ""
    stereo = conn.stereotype or conn.conn_type.lower()
    if diag_type == "Control Flow Diagram" and conn.conn_type in (
        "Control Action",
        "Feedback",
    ):
        base = f"<<{stereo}>> {label}".strip() if stereo else label
        if conn.guard:
            lines: List[str] = []
            for i, g in enumerate(conn.guard):
                if i == 0:
                    lines.append(g)
                else:
                    op = conn.guard_ops[i - 1] if i - 1 < len(conn.guard_ops) else "AND"
                    lines.append(f"{op} {g}")
            guard_text = "\n".join(lines)
            return f"[{guard_text}] / {base}" if base else f"[{guard_text}]"
        return base
    if stereo:
        return f"<<{stereo}>> {label}".strip() if label else f"<<{stereo}>>"
    return label


def diagram_type_abbreviation(diag_type: str | None) -> str:
    """Return an abbreviation for a diagram type.

    The abbreviation is formed by taking the first letter of each word in the
    diagram type and uppercasing it. For example, "Control Flow Diagram" becomes
    "CFD" and "Internal Block Diagram" becomes "IBD".
    """
    if not diag_type:
        return ""
    return "".join(word[0] for word in diag_type.split()).upper()


def format_diagram_name(diagram: "SysMLDiagram | None") -> str:
    """Return the diagram name with its stereotype abbreviation appended."""
    if not diagram:
        return ""
    abbr = diagram_type_abbreviation(diagram.diag_type)
    name = diagram.name or diagram.diag_id
    return f"{name} : {abbr}" if abbr else name


class SysMLDiagramWindow(tk.Frame):
    """Base frame for AutoML diagrams with zoom and pan support."""

    def __init__(self, master, title, tools, diagram_id: str | None = None, app=None, history=None):
        super().__init__(master)
        self.app = app
        self.diagram_history: list[str] = list(history) if history else []
        self.master.title(title) if isinstance(self.master, tk.Toplevel) else None
        if isinstance(self.master, tk.Toplevel):
            self.master.geometry("800x600")

        self.repo = SysMLRepository.get_instance()
        if diagram_id and diagram_id in self.repo.diagrams:
            diagram = self.repo.diagrams[diagram_id]
        else:
            diagram = self.repo.create_diagram(title, name=title, diag_id=diagram_id)
        self.diagram_id = diagram.diag_id
        if isinstance(self.master, tk.Toplevel):
            self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        # Load any saved objects and connections for this diagram
        self.objects: List[SysMLObject] = []
        for data in self.repo.visible_objects(diagram.diag_id):
            if "requirements" not in data:
                data["requirements"] = []
            obj = SysMLObject(**data)
            if obj.obj_type == "Part":
                asil = calculate_allocated_asil(obj.requirements)
                obj.properties.setdefault("asil", asil)
                if obj.element_id and obj.element_id in self.repo.elements:
                    self.repo.elements[obj.element_id].properties.setdefault(
                        "asil", asil
                    )
            self.objects.append(obj)
        self.sort_objects()
        self.connections: List[DiagramConnection] = [
            DiagramConnection(**data)
            for data in self.repo.visible_connections(diagram.diag_id)
        ]
        if self.objects:
            global _next_obj_id
            _next_obj_id = max(o.obj_id for o in self.objects) + 1

        self.zoom = 1.0
        self.font = tkFont.Font(family="Arial", size=int(8 * self.zoom))
        self.current_tool = None
        self.start = None
        self.selected_obj: SysMLObject | None = None
        self.selected_objs: list[SysMLObject] = []
        self.selected_conn: DiagramConnection | None = None
        self.drag_offset = (0, 0)
        self.dragging_point_index: int | None = None
        self.dragging_endpoint: str | None = None  # "src" or "dst"
        self.conn_drag_offset: tuple[float, float] | None = None
        self.clipboard: SysMLObject | None = None
        self.resizing_obj: SysMLObject | None = None
        self.resize_edge: str | None = None
        self.select_rect_start: tuple[float, float] | None = None
        self.select_rect_id: int | None = None
        self.temp_line_end: tuple[float, float] | None = None
        self.endpoint_drag_pos: tuple[float, float] | None = None
        self.rc_dragged = False

        self.toolbox = ttk.Frame(self)
        self.toolbox.pack(side=tk.LEFT, fill=tk.Y)

        self.back_btn = ttk.Button(self.toolbox, text="Go Back", command=self.go_back)
        self.back_btn.pack(fill=tk.X, padx=2, pady=2)
        self.back_btn.configure(state=tk.NORMAL if self.diagram_history else tk.DISABLED)

        # Always provide a select tool
        tools = ["Select"] + tools
        for tool in tools:
            ttk.Button(self.toolbox, text=tool, command=lambda t=tool: self.select_tool(t)).pack(
                fill=tk.X, padx=2, pady=2
            )

        self.prop_frame = ttk.LabelFrame(self.toolbox, text="Properties")
        self.prop_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        self.prop_view = ttk.Treeview(
            self.prop_frame,
            columns=("field", "value"),
            show="headings",
            height=8,
        )
        self.prop_view.heading("field", text="Field")
        self.prop_view.heading("value", text="Value")
        self.prop_view.column("field", width=80, anchor="w")
        self.prop_view.column("value", width=120, anchor="w")
        self.prop_view.pack(fill=tk.BOTH, expand=True)

        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        vbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        hbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vbar.grid(row=0, column=1, sticky="ns")
        hbar.grid(row=1, column=0, sticky="ew")
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        # Keep references to gradient images used for element backgrounds
        self.gradient_cache: dict[int, tk.PhotoImage] = {}
        # Track bounding boxes for compartment toggle buttons
        self.compartment_buttons: list[tuple[int, str, tuple[float, float, float, float]]] = []

        self.canvas.bind("<Button-1>", self.on_left_press)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<ButtonPress-3>", self.on_rc_press)
        self.canvas.bind("<B3-Motion>", self.on_rc_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_rc_release)
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.canvas.bind("<Delete>", self.delete_selected)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Control-MouseWheel>", self.on_ctrl_mousewheel)
        self.bind("<Control-c>", self.copy_selected)
        self.bind("<Control-x>", self.cut_selected)
        self.bind("<Control-v>", self.paste_selected)
        if self.app:
            self.bind("<Control-z>", lambda e: self.app.undo())
        self.bind("<Delete>", self.delete_selected)
        # Refresh from the repository whenever the window gains focus
        self.bind("<FocusIn>", self.refresh_from_repository)

        self.redraw()
        self.update_property_view()
        if not isinstance(self.master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def update_property_view(self) -> None:
        """Display properties and metadata for the selected object."""
        if not hasattr(self, "prop_view"):
            return
        self.prop_view.delete(*self.prop_view.get_children())
        obj = self.selected_obj
        if not obj:
            return
        self.prop_view.insert("", "end", values=("Type", obj.obj_type))
        name = obj.properties.get("name", "")
        if name:
            self.prop_view.insert("", "end", values=("Name", name))
        for k, v in obj.properties.items():
            if k == "name":
                continue
            self.prop_view.insert("", "end", values=(k, v))
        if obj.element_id:
            elem = self.repo.elements.get(obj.element_id)
            if elem:
                self.prop_view.insert("", "end", values=("Author", getattr(elem, "author", "")))
                self.prop_view.insert("", "end", values=("Created", getattr(elem, "created", "")))
                self.prop_view.insert("", "end", values=("Modified", getattr(elem, "modified", "")))
                self.prop_view.insert("", "end", values=("ModifiedBy", getattr(elem, "modified_by", "")))

    def select_tool(self, tool):
        self.current_tool = tool
        self.start = None
        self.temp_line_end = None
        self.selected_obj = None
        self.selected_objs = []
        self.selected_conn = None
        self.dragging_point_index = None
        self.dragging_endpoint = None
        self.conn_drag_offset = None
        cursor = "arrow"
        if tool != "Select":
            cursor = (
                "crosshair"
                if tool
                in (
                    "Association",
                    "Include",
                    "Extend",
                    "Flow",
                    "Propagate",
                    "Propagate by Review",
                    "Propagate by Approval",
                    "Re-use",
                    "Connector",
                    "Generalize",
                    "Generalization",
                    "Communication Path",
                    "Aggregation",
                    "Composite Aggregation",
                    "Control Action",
                    "Feedback",
                )
                else "tcross"
            )
        self.canvas.configure(cursor=cursor)
        self.update_property_view()

    # ------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------
    def validate_connection(
        self, src: SysMLObject, dst: SysMLObject, conn_type: str
    ) -> tuple[bool, str]:
        """Return (valid, message) for a potential connection."""
        diag = self.repo.diagrams.get(self.diagram_id)
        diag_type = diag.diag_type if diag else ""

        if conn_type in (
            "Association",
            "Include",
            "Extend",
            "Flow",
            "Propagate",
            "Propagate by Review",
            "Propagate by Approval",
            "Re-use",
            "Connector",
            "Generalize",
            "Generalization",
            "Communication Path",
            "Aggregation",
            "Composite Aggregation",
            "Control Action",
            "Feedback",
        ):
            if src == dst:
                return False, "Cannot connect an element to itself"

        if diag_type == "Use Case Diagram":
            if conn_type == "Association":
                actors = {"Actor"}
                if not (
                    (src.obj_type in actors and dst.obj_type == "Use Case")
                    or (dst.obj_type in actors and src.obj_type == "Use Case")
                ):
                    return False, "Associations must connect an Actor and a Use Case"
            elif conn_type in ("Include", "Extend"):
                if src.obj_type != "Use Case" or dst.obj_type != "Use Case":
                    return False, f"{conn_type} relationships must connect two Use Cases"
            elif conn_type == "Generalize":
                if src.obj_type != dst.obj_type or src.obj_type not in ("Actor", "Use Case"):
                    return False, "Generalizations must link two Actors or two Use Cases"
            elif conn_type == "Communication Path":
                if src.obj_type != "Actor" or dst.obj_type != "Actor":
                    return False, "Communication Paths must connect two Actors"

        elif diag_type == "Block Diagram":
            if conn_type == "Association":
                if src.obj_type != "Block" or dst.obj_type != "Block":
                    return False, "Associations in block diagrams must connect Blocks"
            elif conn_type == "Generalization":
                if src.obj_type != "Block" or dst.obj_type != "Block":
                    return False, "Generalizations in block diagrams must connect Blocks"
                if _shared_generalization_parent(
                    self.repo, src.element_id, dst.element_id
                ):
                    return False, "Blocks already share a generalized parent"
                if dst.element_id in _collect_generalization_parents(
                    self.repo, src.element_id
                ) or src.element_id in _collect_generalization_parents(
                    self.repo, dst.element_id
                ):
                    return False, "Blocks cannot generalize each other"
            elif conn_type in ("Aggregation", "Composite Aggregation"):
                if src.obj_type != "Block" or dst.obj_type != "Block":
                    return False, "Aggregations must connect Blocks"
                if _aggregation_exists(self.repo, src.element_id, dst.element_id):
                    return False, "Aggregation already defined for this block"
                if _reverse_aggregation_exists(self.repo, src.element_id, dst.element_id):
                    return False, "Blocks cannot aggregate each other"

        elif diag_type == "Internal Block Diagram":
            if conn_type == "Connector":
                if src.obj_type not in ("Port", "Part") or dst.obj_type not in (
                    "Port",
                    "Part",
                ):
                    return False, "Connectors must link Parts or Ports"
                if src.obj_type == "Block Boundary" or dst.obj_type == "Block Boundary":
                    return False, "Connectors must link Parts or Ports"
                if src.obj_type == "Port" and dst.obj_type == "Port":
                    dir_a = src.properties.get("direction", "inout").lower()
                    dir_b = dst.properties.get("direction", "inout").lower()
                    if {dir_a, dir_b} != {"in", "out"}:
                        return False, "Ports must connect one 'in' and one 'out'"
                    def flow_dir(conn: DiagramConnection, port_id: int) -> str | None:
                        if conn.arrow == "both":
                            return None
                        if port_id == conn.src:
                            if conn.arrow == "forward":
                                return "out"
                            if conn.arrow == "backward":
                                return "in"
                        elif port_id == conn.dst:
                            if conn.arrow == "forward":
                                return "in"
                            if conn.arrow == "backward":
                                return "out"
                        return None
                    new_dir_a = "out" if dir_a == "out" else "in"
                    new_dir_b = "out" if dir_b == "out" else "in"
                    connections = getattr(self, "connections", None)
                    if connections is None:
                        return False, "Inconsistent data flow on port"
                    for c in connections:
                        if c.conn_type != "Connector":
                            continue
                        if src.obj_id in (c.src, c.dst):
                            ex = flow_dir(c, src.obj_id)
                            if ex and ex != new_dir_a:
                                return False, "Inconsistent data flow on port"
                        if dst.obj_id in (c.src, c.dst):
                            ex = flow_dir(c, dst.obj_id)
                            if ex and ex != new_dir_b:
                                return False, "Inconsistent data flow on port"

        elif diag_type == "Control Flow Diagram":
            if conn_type in ("Control Action", "Feedback"):
                max_offset = (src.width + dst.width) / 2
                if abs(src.x - dst.x) > max_offset:
                    return False, "Connections must be vertical"

        elif diag_type == "Activity Diagram":
            # Basic control flow rules
            allowed = {
                "Initial": {
                    "Action",
                    "CallBehaviorAction",
                    "Decision",
                    "Merge",
                    "Fork",
                    "Join",
                },
                "Action": {
                    "Action",
                    "CallBehaviorAction",
                    "Decision",
                    "Merge",
                    "Fork",
                    "Join",
                    "Final",
                },
                "CallBehaviorAction": {
                    "Action",
                    "CallBehaviorAction",
                    "Decision",
                    "Merge",
                    "Fork",
                    "Join",
                    "Final",
                },
                "Decision": {
                    "Action",
                    "CallBehaviorAction",
                    "Decision",
                    "Merge",
                    "Fork",
                    "Join",
                    "Final",
                },
                "Merge": {
                    "Action",
                    "CallBehaviorAction",
                    "Decision",
                    "Fork",
                    "Join",
                },
                "Fork": {
                    "Action",
                    "CallBehaviorAction",
                    "Decision",
                    "Merge",
                    "Fork",
                    "Join",
                },
                "Join": {
                    "Action",
                    "CallBehaviorAction",
                    "Decision",
                    "Merge",
                },
                "Final": set(),
            }
            if src.obj_type == "Final":
                return False, "Flows cannot originate from Final nodes"
            if dst.obj_type == "Initial":
                return False, "Flows cannot terminate at an Initial node"
            valid_targets = allowed.get(src.obj_type)
            if valid_targets and dst.obj_type not in valid_targets:
                return (
                    False,
                    f"Flow from {src.obj_type} to {dst.obj_type} is not allowed",
                )
        elif diag_type == "BPMN Diagram":
            if conn_type in (
                "Propagate",
                "Propagate by Review",
                "Propagate by Approval",
            ):
                if src.obj_type != "Work Product" or dst.obj_type != "Work Product":
                    return False, "Propagation links must connect Work Products"
                src_name = src.properties.get("name")
                dst_name = dst.properties.get("name")
                if (src_name, dst_name) not in ALLOWED_PROPAGATIONS:
                    return False, f"Propagation from {src_name} to {dst_name} is not allowed"
            elif conn_type == "Re-use":
                if src.obj_type not in ("Work Product", "Lifecycle Phase") or dst.obj_type != "Lifecycle Phase":
                    return False, "Re-use links must originate from a Work Product or Lifecycle Phase and target a Lifecycle Phase"
            else:
                allowed = {
                    "Initial": {
                        "Action",
                        "Decision",
                        "Merge",
                    },
                    "Action": {
                        "Action",
                        "Decision",
                        "Merge",
                        "Final",
                    },
                    "Decision": {
                        "Action",
                        "Decision",
                        "Merge",
                        "Final",
                    },
                    "Merge": {
                        "Action",
                        "Decision",
                        "Merge",
                    },
                    "Final": set(),
                }
                if src.obj_type == "Final":
                    return False, "Flows cannot originate from Final nodes"
                if dst.obj_type == "Initial":
                    return False, "Flows cannot terminate at an Initial node"
                valid_targets = allowed.get(src.obj_type)
                if valid_targets and dst.obj_type not in valid_targets:
                    return (
                        False,
                        f"Flow from {src.obj_type} to {dst.obj_type} is not allowed",
                    )

        return True, ""

    def _constrain_horizontal_movement(
        self, obj: SysMLObject, new_x: float
    ) -> float:
        """Return adjusted x to keep control flow connectors vertical."""
        diag = self.repo.diagrams.get(self.diagram_id)
        if not diag or diag.diag_type != "Control Flow Diagram":
            return new_x
        adjusted_x = new_x
        for conn in self.connections:
            if conn.conn_type in ("Control Action", "Feedback") and (
                conn.src == obj.obj_id or conn.dst == obj.obj_id
            ):
                other_id = conn.dst if conn.src == obj.obj_id else conn.src
                for other in self.objects:
                    if other.obj_id == other_id:
                        max_diff = (obj.width + other.width) / 2
                        diff = adjusted_x - other.x
                        if diff > max_diff:
                            adjusted_x = other.x + max_diff
                        elif diff < -max_diff:
                            adjusted_x = other.x - max_diff
        return adjusted_x

    def _constrain_control_flow_x(
        self, conn: DiagramConnection, new_x: float
    ) -> float:
        """Clamp connector x within the horizontal overlap of its objects."""
        diag = self.repo.diagrams.get(self.diagram_id)
        if not diag or diag.diag_type != "Control Flow Diagram":
            return new_x
        src = next((o for o in self.objects if o.obj_id == conn.src), None)
        dst = next((o for o in self.objects if o.obj_id == conn.dst), None)
        if not src or not dst:
            return new_x
        min_x = max(src.x - src.width / 2, dst.x - dst.width / 2)
        max_x = min(src.x + src.width / 2, dst.x + dst.width / 2)
        if new_x < min_x:
            return min_x
        if new_x > max_x:
            return max_x
        return new_x

    def on_left_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        conn_tools = (
            "Association",
            "Include",
            "Extend",
            "Flow",
            "Propagate",
            "Propagate by Review",
            "Propagate by Approval",
            "Re-use",
            "Connector",
            "Generalize",
            "Generalization",
            "Communication Path",
            "Aggregation",
            "Composite Aggregation",
            "Control Action",
            "Feedback",
        )
        prefer = self.current_tool in conn_tools
        t = self.current_tool
        if t in (None, "Select"):
            conn = self.find_connection(x, y)
            if conn:
                if (event.state & 0x0001) and conn.style == "Custom":
                    conn.points.append((x / self.zoom, y / self.zoom))
                    self._sync_to_repository()
                self.selected_conn = conn
                self.selected_obj = None
                self.selected_objs = []
                self.dragging_point_index = None
                self.dragging_endpoint = None
                self.update_property_view()
                if conn.style == "Custom":
                    for idx, (px, py) in enumerate(conn.points):
                        hx = px * self.zoom
                        hy = py * self.zoom
                        if abs(hx - x) <= 4 and abs(hy - y) <= 4:
                            self.dragging_point_index = idx
                            self.conn_drag_offset = (x - hx, y - hy)
                            break
                elif conn.style == "Squared":
                    src_obj = self.get_object(conn.src)
                    dst_obj = self.get_object(conn.dst)
                    if src_obj and dst_obj:
                        mx = (
                            conn.points[0][0] * self.zoom
                            if conn.points
                            else ((src_obj.x + dst_obj.x) / 2 * self.zoom)
                        )
                        my = (src_obj.y + dst_obj.y) / 2 * self.zoom
                        if abs(mx - x) <= 4 and abs(my - y) <= 4:
                            self.dragging_point_index = 0
                            self.conn_drag_offset = (x - mx, 0)
                elif (
                    self.repo.diagrams.get(self.diagram_id).diag_type
                    == "Control Flow Diagram"
                    and conn.conn_type in ("Control Action", "Feedback")
                ):
                    src_obj = self.get_object(conn.src)
                    dst_obj = self.get_object(conn.dst)
                    if src_obj and dst_obj:
                        x_val = (
                            conn.points[0][0]
                            if conn.points
                            else (
                                max(
                                    src_obj.x - src_obj.width / 2,
                                    dst_obj.x - dst_obj.width / 2,
                                )
                                + min(
                                    src_obj.x + src_obj.width / 2,
                                    dst_obj.x + dst_obj.width / 2,
                                )
                            )
                            / 2
                        )
                        x_val = SysMLDiagramWindow._constrain_control_flow_x(
                            self, conn, x_val
                        )
                        mx = x_val * self.zoom
                        my = (src_obj.y + dst_obj.y) / 2 * self.zoom
                        if abs(mx - x) <= 4 and abs(my - y) <= 4:
                            self.dragging_point_index = 0
                            self.conn_drag_offset = (x - mx, 0)
                # check for dragging endpoints
                src_obj = self.get_object(conn.src)
                dst_obj = self.get_object(conn.dst)
                if src_obj and dst_obj:
                    sx, sy = self.edge_point(
                        src_obj,
                        dst_obj.x * self.zoom,
                        dst_obj.y * self.zoom,
                        conn.src_pos,
                    )
                    dxp, dyp = self.edge_point(
                        dst_obj,
                        src_obj.x * self.zoom,
                        src_obj.y * self.zoom,
                        conn.dst_pos,
                    )
                    if abs(sx - x) <= 6 and abs(sy - y) <= 6:
                        self.dragging_endpoint = "src"
                        self.conn_drag_offset = (x - sx, y - sy)
                        self.endpoint_drag_pos = None
                    elif abs(dxp - x) <= 6 and abs(dyp - y) <= 6:
                        self.dragging_endpoint = "dst"
                        self.conn_drag_offset = (x - dxp, y - dyp)
                        self.endpoint_drag_pos = None
                self.redraw()
                return

        obj = self.find_object(x, y, prefer_port=prefer)

        if obj and obj.obj_type == "Block" and t in (None, "Select"):
            hit = self.hit_compartment_toggle(obj, x, y)
            if hit:
                obj.collapsed[hit] = not obj.collapsed.get(hit, False)
                self._sync_to_repository()
                self.redraw()
                return

        if t in (
            "Association",
            "Include",
            "Extend",
            "Flow",
            "Propagate",
            "Propagate by Review",
            "Propagate by Approval",
            "Re-use",
            "Connector",
            "Generalize",
            "Generalization",
            "Communication Path",
            "Aggregation",
            "Composite Aggregation",
            "Control Action",
            "Feedback",
        ):
            if self.start is None:
                if obj:
                    self.start = obj
                    # Do not highlight objects while adding a connection
                    self.selected_obj = None
                    self.update_property_view()
                    self.temp_line_end = (x, y)
                    self.redraw()
            else:
                if obj and obj != self.start:
                    valid, msg = self.validate_connection(self.start, obj, t)
                    if valid:
                        if t == "Control Action":
                            arrow_default = "forward"
                        elif t == "Feedback":
                            arrow_default = "backward"
                        elif t in (
                            "Flow",
                            "Generalize",
                            "Generalization",
                            "Include",
                            "Extend",
                            "Propagate",
                            "Propagate by Review",
                            "Propagate by Approval",
                            "Re-use",
                        ):
                            arrow_default = "forward"
                        else:
                            arrow_default = "none"
                        conn_stereo = (
                            "control action"
                            if t == "Control Action"
                            else "feedback" if t == "Feedback" else t.lower()
                        )
                        rel = self.repo.create_relationship(
                            t, src_id, dst_id, stereotype=rel_stereo
                        )
                        self.repo.add_relationship_to_diagram(
                            self.diagram_id, rel.rel_id
                        )
                    self._sync_to_repository()
                    ConnectionDialog(self, conn)
                else:
                    messagebox.showwarning("Invalid Connection", msg)
                self.start = None
                self.temp_line_end = None
                self.selected_obj = None
                self.update_property_view()
                # Return to select mode after completing a connection
                self.current_tool = "Select"
                self.canvas.configure(cursor="arrow")
                self.redraw()
        elif t and t != "Select":
            if t == "Existing Element":
                names = []
                id_map = {}
                diag = self.repo.diagrams.get(self.diagram_id)
                allowed = {"Actor", "Block"} if diag and diag.diag_type == "Control Flow Diagram" else None
                for eid, el in self.repo.elements.items():
                    if el.elem_type != "Package" and (not allowed or el.elem_type in allowed):
                        name = el.name or eid
                        names.append(name)
                        id_map[name] = eid
                if not names:
                    messagebox.showinfo("Add Element", "No elements available")
                    return
                dlg = SysMLObjectDialog.SelectElementDialog(self, names, title="Select Element")
                selected = dlg.result
                if not selected:
                    return
                elem_id = id_map[selected]
                element = self.repo.elements.get(elem_id)
                self.repo.add_element_to_diagram(self.diagram_id, elem_id)
                new_obj = SysMLObject(
                    _get_next_id(),
                    "Existing Element",
                    x / self.zoom,
                    y / self.zoom,
                    element_id=elem_id,
                    properties={"name": element.name if element else selected},
                )
            else:
                if t == "Port":
                    parent_obj = (
                        obj if obj and obj.obj_type in ("Part", "Block Boundary") else None
                    )
                    if parent_obj is None:
                        # Default to the IBD boundary if present
                        parent_obj = next(
                            (o for o in self.objects if o.obj_type == "Block Boundary"),
                            None,
                        )
                    if parent_obj is None:
                        return
                pkg = self.repo.diagrams[self.diagram_id].package
                element = self.repo.create_element(t, owner=pkg)
                self.repo.add_element_to_diagram(self.diagram_id, element.elem_id)
                new_obj = SysMLObject(
                    _get_next_id(),
                    t,
                    x / self.zoom,
                    y / self.zoom,
                    element_id=element.elem_id,
                )
            if t == "Block":
                new_obj.height = 140.0
                new_obj.width = 160.0
            elif t == "System Boundary":
                new_obj.width = 200.0
                new_obj.height = 120.0
            elif t in ("Decision", "Merge"):
                new_obj.width = 40.0
                new_obj.height = 40.0
            elif t == "Initial":
                new_obj.width = 20.0
                new_obj.height = 20.0
            elif t == "Final":
                new_obj.width = 30.0
                new_obj.height = 30.0
            elif t in ("Fork", "Join"):
                new_obj.width = 60.0
                new_obj.height = 10.0
            key = f"{t.replace(' ', '')}Usage"

            for prop in SYSML_PROPERTIES.get(key, []):
                new_obj.properties.setdefault(prop, "")
            if t == "Port":
                new_obj.properties.setdefault("labelX", "8")
                new_obj.properties.setdefault("labelY", "-8")
                if parent_obj:
                    new_obj.properties["parent"] = str(parent_obj.obj_id)
                    self.snap_port_to_parent(new_obj, parent_obj)
                    # Persist the port by adding it to the parent object's list
                    pname = new_obj.properties.get("name") or ""
                    ports = [
                        p.strip()
                        for p in parent_obj.properties.get("ports", "").split(",")
                        if p.strip()
                    ]
                    if not pname:
                        base = "Port"
                        idx = 1
                        existing = set(ports)
                        existing.update(
                            p.properties.get("name")
                            for p in self.objects
                            if p.obj_type == "Port"
                            and p.properties.get("parent") == str(parent_obj.obj_id)
                        )
                        pname = base
                        while pname in existing:
                            pname = f"{base}{idx}"
                            idx += 1
                        new_obj.properties["name"] = pname
                        element.name = pname
                    if pname not in ports:
                        ports.append(pname)
                        parent_obj.properties["ports"] = ", ".join(ports)
                        if parent_obj.element_id and parent_obj.element_id in self.repo.elements:
                            self.repo.elements[parent_obj.element_id].properties["ports"] = (
                                parent_obj.properties["ports"]
                            )
            element.properties.update(new_obj.properties)
            self.ensure_text_fits(new_obj)
            if t == "System Boundary":
                self.objects.insert(0, new_obj)
            else:
                self.objects.append(new_obj)
            self.sort_objects()
            self._sync_to_repository()
            self.selected_obj = new_obj
            # After placing one object, revert to select mode so additional
            # clicks do not keep adding elements unintentionally
            self.current_tool = "Select"
            self.canvas.configure(cursor="arrow")
            self.redraw()
            self.update_property_view()
        else:
            if obj:
                self.selected_obj = obj
                self.selected_objs = [obj]
                self.drag_offset = (x / self.zoom - obj.x, y / self.zoom - obj.y)
                self.resizing_obj = None
                self.resize_edge = self.hit_resize_handle(obj, x, y)
                if self.resize_edge:
                    self.resizing_obj = obj
                self.redraw()
                self.update_property_view()
            else:
                conn = self.find_connection(x, y)
                if conn:
                    if (event.state & 0x0001) and conn.style == "Custom":
                        conn.points.append((x / self.zoom, y / self.zoom))
                        self._sync_to_repository()
                    self.selected_conn = conn
                    self.selected_obj = None
                    self.selected_objs = []
                    self.dragging_point_index = None
                    self.dragging_endpoint = None
                    self.update_property_view()
                    if conn.style == "Custom":
                        for idx, (px, py) in enumerate(conn.points):
                            hx = px * self.zoom
                            hy = py * self.zoom
                            if abs(hx - x) <= 4 and abs(hy - y) <= 4:
                                self.dragging_point_index = idx
                                self.conn_drag_offset = (x - hx, y - hy)
                                break
                    elif conn.style == "Squared":
                        src_obj = self.get_object(conn.src)
                        dst_obj = self.get_object(conn.dst)
                        if src_obj and dst_obj:
                            mx = (
                                conn.points[0][0] * self.zoom
                                if conn.points
                                else ((src_obj.x + dst_obj.x) / 2 * self.zoom)
                            )
                            my = (src_obj.y + dst_obj.y) / 2 * self.zoom
                            if abs(mx - x) <= 4 and abs(my - y) <= 4:
                                self.dragging_point_index = 0
                                self.conn_drag_offset = (x - mx, 0)
                    # check for dragging endpoints
                    src_obj = self.get_object(conn.src)
                    dst_obj = self.get_object(conn.dst)
                    if src_obj and dst_obj:
                        sx, sy = self.edge_point(
                            src_obj,
                            dst_obj.x * self.zoom,
                            dst_obj.y * self.zoom,
                            conn.src_pos,
                        )
                        dxp, dyp = self.edge_point(
                            dst_obj,
                            src_obj.x * self.zoom,
                            src_obj.y * self.zoom,
                            conn.dst_pos,
                        )
                        if abs(sx - x) <= 6 and abs(sy - y) <= 6:
                            self.dragging_endpoint = "src"
                            self.conn_drag_offset = (x - sx, y - sy)
                            self.endpoint_drag_pos = None
                        elif abs(dxp - x) <= 6 and abs(dyp - y) <= 6:
                            self.dragging_endpoint = "dst"
                            self.conn_drag_offset = (x - dxp, y - dyp)
                            self.endpoint_drag_pos = None
                    self.redraw()
                else:
                    # allow clicking on the resize handle even if outside the object
                    if self.selected_obj:
                        self.resize_edge = self.hit_resize_handle(self.selected_obj, x, y)
                        if self.resize_edge:
                            self.resizing_obj = self.selected_obj
                            return
                    self.selected_obj = None
                    self.selected_objs = []
                    self.selected_conn = None
                    self.resizing_obj = None
                    self.resize_edge = None
                    if self.current_tool == "Select":
                        self.select_rect_start = (x, y)
                        self.select_rect_id = self.canvas.create_rectangle(
                            x, y, x, y, dash=(2, 2), outline="blue"
                        )
                    self.redraw()
                    self.update_property_view()

    def on_left_drag(self, event):
        if self.start and self.current_tool in (
            "Association",
            "Include",
            "Extend",
            "Flow",
            "Propagate",
            "Propagate by Review",
            "Propagate by Approval",
            "Re-use",
            "Connector",
            "Generalization",
            "Generalize",
            "Communication Path",
            "Aggregation",
            "Composite Aggregation",
            "Control Action",
            "Feedback",
        ):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.temp_line_end = (x, y)
            self.redraw()
            return
        if self.select_rect_start:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.canvas.coords(
                self.select_rect_id,
                self.select_rect_start[0],
                self.select_rect_start[1],
                x,
                y,
            )
            self._update_drag_selection(x, y)
            return
        if (
            self.dragging_endpoint is not None
            and self.selected_conn
            and self.current_tool == "Select"
        ):
            x = self.canvas.canvasx(event.x) - self.conn_drag_offset[0]
            y = self.canvas.canvasy(event.y) - self.conn_drag_offset[1]
            if self.dragging_endpoint == "src":
                obj = self.get_object(self.selected_conn.src)
            else:
                obj = self.get_object(self.selected_conn.dst)
            if obj:
                cx = obj.x * self.zoom
                cy = obj.y * self.zoom
                w = obj.width * self.zoom / 2
                h = obj.height * self.zoom / 2
                thresh = max(w, h) + CONNECTION_SELECT_RADIUS
                if math.hypot(x - cx, y - cy) <= thresh:
                    self.endpoint_drag_pos = None
                    ex, ey = self.edge_point(obj, x, y, apply_radius=False)
                    rx = (ex / self.zoom - obj.x) / (obj.width / 2)
                    ry = (ey / self.zoom - obj.y) / (obj.height / 2)
                    if self.dragging_endpoint == "src":
                        self.selected_conn.src_pos = (rx, ry)
                    else:
                        self.selected_conn.dst_pos = (rx, ry)
                else:
                    self.endpoint_drag_pos = (x, y)
            self.redraw()
            return
        if (
            self.dragging_point_index is not None
            and self.selected_conn
            and self.current_tool == "Select"
        ):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            px = (x - self.conn_drag_offset[0]) / self.zoom
            py = (y - self.conn_drag_offset[1]) / self.zoom
            if self.selected_conn.style == "Squared":
                if not self.selected_conn.points:
                    self.selected_conn.points.append((px, 0))
                else:
                    self.selected_conn.points[0] = (px, 0)
            elif (
                self.repo.diagrams.get(self.diagram_id).diag_type
                == "Control Flow Diagram"
                and self.selected_conn.conn_type in ("Control Action", "Feedback")
            ):
                px = SysMLDiagramWindow._constrain_control_flow_x(
                    self, self.selected_conn, px
                )
                if not self.selected_conn.points:
                    self.selected_conn.points.append((px, 0))
                else:
                    self.selected_conn.points[0] = (px, 0)
            else:
                self.selected_conn.points[self.dragging_point_index] = (px, py)
            self.redraw()
            return
        if not self.selected_obj:
            return
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        if self.resizing_obj:
            obj = self.resizing_obj
            if obj.obj_type in (
                "Initial",
                "Final",
                "Actor",
                "Decision",
                "Merge",
                "Work Product",
            ):
                return
            min_w, min_h = (10.0, 10.0)
            if obj.obj_type == "Block":
                min_w, min_h = self._min_block_size(obj)
            elif obj.obj_type in ("Action", "CallBehaviorAction"):
                min_w, min_h = self._min_action_size(obj)
            elif obj.obj_type == "Block Boundary":
                min_w, min_h = _boundary_min_size(obj, self.objects)
            left = obj.x - obj.width / 2
            right = obj.x + obj.width / 2
            top = obj.y - obj.height / 2
            bottom = obj.y + obj.height / 2
            if "e" in self.resize_edge:
                new_right = x / self.zoom
                if new_right - left < min_w:
                    new_right = left + min_w
                right = new_right
            if "w" in self.resize_edge:
                new_left = x / self.zoom
                if right - new_left < min_w:
                    new_left = right - min_w
                left = new_left
            if obj.obj_type not in ("Fork", "Join", "Existing Element"):
                if "s" in self.resize_edge:
                    new_bottom = y / self.zoom
                    if new_bottom - top < min_h:
                        new_bottom = top + min_h
                    bottom = new_bottom
                if "n" in self.resize_edge:
                    new_top = y / self.zoom
                    if bottom - new_top < min_h:
                        new_top = bottom - min_h
                    top = new_top
            new_w = right - left
            new_h = bottom - top
            obj.x = (left + right) / 2
            obj.y = (top + bottom) / 2
            obj.width = new_w
            obj.height = new_h
            if obj.obj_type == "Part":
                update_ports_for_part(obj, self.objects)
            if obj.obj_type == "Block Boundary":
                update_ports_for_boundary(obj, self.objects)
                ensure_boundary_contains_parts(obj, self.objects)
            self.redraw()
            return
        if self.selected_obj.obj_type == "Port" and "parent" in self.selected_obj.properties:
            parent = self.get_object(int(self.selected_obj.properties["parent"]))
            if parent:
                self.selected_obj.x = x / self.zoom
                self.selected_obj.y = y / self.zoom
                self.snap_port_to_parent(self.selected_obj, parent)
        else:
            old_x = self.selected_obj.x
            old_y = self.selected_obj.y
            new_x = x / self.zoom - self.drag_offset[0]
            new_x = self._constrain_horizontal_movement(self.selected_obj, new_x)
            self.selected_obj.x = new_x
            self.selected_obj.y = y / self.zoom - self.drag_offset[1]
            dx = self.selected_obj.x - old_x
            dy = self.selected_obj.y - old_y
            if self.selected_obj.obj_type in ("Part", "Block Boundary"):
                for p in self.objects:
                    if p.obj_type == "Port" and p.properties.get("parent") == str(
                        self.selected_obj.obj_id
                    ):
                        p.x += dx
                        p.y += dy
                        self.snap_port_to_parent(p, self.selected_obj)
            if self.selected_obj.obj_type == "Block Boundary":
                for o in self.objects:
                    if o.obj_type == "Part":
                        o.x += dx
                        o.y += dy
                        for p in self.objects:
                            if (
                                p.obj_type == "Port"
                                and p.properties.get("parent") == str(o.obj_id)
                            ):
                                p.x += dx
                                p.y += dy
            if self.selected_obj.obj_type == "System Boundary":
                for o in self.objects:
                    if o.properties.get("boundary") == str(self.selected_obj.obj_id):
                        o.x += dx
                        o.y += dy
            boundary = self.get_ibd_boundary()
            if boundary:
                ensure_boundary_contains_parts(boundary, self.objects)
        self.redraw()
        self._sync_to_repository()
        if self.app:
            self.app.update_views()

    def on_left_release(self, event):
        if self.start and self.current_tool in (
            "Association",
            "Include",
            "Extend",
            "Flow",
            "Propagate",
            "Propagate by Review",
            "Propagate by Approval",
            "Re-use",
            "Connector",
            "Generalization",
            "Generalize",
            "Communication Path",
            "Aggregation",
            "Composite Aggregation",
            "Control Action",
            "Feedback",
        ):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            obj = self.find_object(
                x,
                y,
                prefer_port=True,
            )
            if obj and obj != self.start:
                valid, msg = self.validate_connection(self.start, obj, self.current_tool)
                if valid:
                    if self.current_tool == "Control Action":
                        arrow_default = "forward"
                    elif self.current_tool == "Feedback":
                        arrow_default = "backward"
                    elif self.current_tool in (
                        "Flow",
                        "Generalize",
                        "Generalization",
                        "Include",
                        "Extend",
                        "Propagate",
                        "Propagate by Review",
                        "Propagate by Approval",
                        "Re-use",
                    ):
                        arrow_default = "forward"
                    else:
                        arrow_default = "none"
                    conn_stereo = (
                        "control action"
                        if self.current_tool == "Control Action"
                        else "feedback" if self.current_tool == "Feedback" else self.current_tool.lower()
                    )
                    conn = DiagramConnection(
                        self.start.obj_id,
                        obj.obj_id,
                        self.current_tool,
                        arrow=arrow_default,
                        stereotype=conn_stereo,
                    )
                    if self.current_tool == "Connector":
                        src_flow = self.start.properties.get("flow") if self.start.obj_type == "Port" else None
                        dst_flow = obj.properties.get("flow") if obj.obj_type == "Port" else None
                        if src_flow or dst_flow:
                            conn.mid_arrow = True
                            if src_flow and dst_flow:
                                dir_a = self.start.properties.get("direction", "out").lower()
                                dir_b = obj.properties.get("direction", "out").lower()
                                if dir_a == "out":
                                    conn.name = src_flow
                                    conn.arrow = "forward"
                                elif dir_b == "out":
                                    conn.name = dst_flow
                                    conn.arrow = "backward"
                                else:
                                    conn.name = src_flow
                                    conn.arrow = "both"
                            elif src_flow:
                                conn.name = src_flow
                                dir_attr = self.start.properties.get("direction", "out")
                                if dir_attr == "in":
                                    conn.arrow = "backward"
                                elif dir_attr == "out":
                                    conn.arrow = "forward"
                                else:
                                    conn.arrow = "both"
                            else:
                                conn.name = dst_flow
                                dir_attr = obj.properties.get("direction", "out")
                                if dir_attr == "in":
                                    conn.arrow = "forward"
                                elif dir_attr == "out":
                                    conn.arrow = "backward"
                                else:
                                    conn.arrow = "both"
                    self.connections.append(conn)
                    if self.start.element_id and obj.element_id:
                        rel_stereo = (
                            "control action"
                            if self.current_tool == "Control Action"
                            else "feedback"
                            if self.current_tool == "Feedback"
                            else None
                        )
                        rel = self.repo.create_relationship(
                            self.current_tool,
                            self.start.element_id,
                            obj.element_id,
                            stereotype=rel_stereo,
                        )
                        self.repo.add_relationship_to_diagram(
                            self.diagram_id, rel.rel_id
                        )
                        if self.current_tool == "Generalization":
                            inherit_block_properties(self.repo, self.start.element_id)
                    self._sync_to_repository()
                    ConnectionDialog(self, conn)
                else:
                    messagebox.showwarning("Invalid Connection", msg)
        if self.select_rect_start:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.canvas.coords(
                self.select_rect_id,
                self.select_rect_start[0],
                self.select_rect_start[1],
                x,
                y,
            )
            self._update_drag_selection(x, y)
            self.canvas.delete(self.select_rect_id)
            self.select_rect_start = None
            self.select_rect_id = None
        self.start = None
        self.temp_line_end = None
        # Return to select mode after completing a connection
        self.current_tool = "Select"
        self.canvas.configure(cursor="arrow")
        self.resizing_obj = None
        self.resize_edge = None
        if self.dragging_point_index is not None and self.selected_conn:
            self._sync_to_repository()
        self.dragging_point_index = None
        if self.dragging_endpoint is not None and self.selected_conn:
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            obj = self.find_object(x, y, prefer_port=True)
            src_obj = self.get_object(self.selected_conn.src)
            dst_obj = self.get_object(self.selected_conn.dst)
            if obj and obj not in (src_obj, dst_obj):
                if self.dragging_endpoint == "src":
                    valid, msg = self.validate_connection(
                        obj, dst_obj, self.selected_conn.conn_type
                    )
                else:
                    valid, msg = self.validate_connection(
                        src_obj, obj, self.selected_conn.conn_type
                    )
                if valid and src_obj and dst_obj and obj.element_id:
                    for rel in self.repo.relationships:
                        if (
                            rel.source == src_obj.element_id
                            and rel.target == dst_obj.element_id
                            and rel.rel_type == self.selected_conn.conn_type
                        ):
                            if self.selected_conn.conn_type == "Generalization":
                                if self.dragging_endpoint == "dst":
                                    msgbox = "Changing inheritance will remove all inherited parts, properties and attributes. Continue?"
                                    if not messagebox.askyesno("Change Inheritance", msgbox):
                                        break
                                    remove_inherited_block_properties(
                                        self.repo, src_obj.element_id, dst_obj.element_id
                                    )
                                    rel.target = obj.element_id
                                    self.selected_conn.dst = obj.obj_id
                                    inherit_block_properties(self.repo, src_obj.element_id)
                                else:
                                    msgbox = "Changing inheritance will remove all inherited parts, properties and attributes. Continue?"
                                    if not messagebox.askyesno("Change Inheritance", msgbox):
                                        break
                                    remove_inherited_block_properties(
                                        self.repo, src_obj.element_id, dst_obj.element_id
                                    )
                                    rel.source = obj.element_id
                                    self.selected_conn.src = obj.obj_id
                                    inherit_block_properties(self.repo, obj.element_id)
                            else:
                                if self.selected_conn.conn_type in (
                                    "Aggregation",
                                    "Composite Aggregation",
                                ):
                                    msg = "Delete aggregation and its part?"
                                    if messagebox.askyesno(
                                        "Remove Aggregation", msg
                                    ):
                                        remove_aggregation_part(
                                            self.repo,
                                            src_obj.element_id,
                                            dst_obj.element_id,
                                            remove_object=self.selected_conn.conn_type
                                            == "Composite Aggregation",
                                            app=getattr(self, "app", None),
                                        )
                                if self.dragging_endpoint == "dst":
                                    rel.target = obj.element_id
                                    self.selected_conn.dst = obj.obj_id
                                    new_whole = src_obj.element_id
                                    new_part = obj.element_id
                                else:
                                    rel.source = obj.element_id
                                    self.selected_conn.src = obj.obj_id
                                    new_whole = obj.element_id
                                    new_part = dst_obj.element_id
                                if self.selected_conn.conn_type == "Composite Aggregation":
                                    add_composite_aggregation_part(
                                        self.repo,
                                        new_whole,
                                        new_part,
                                        self.selected_conn.multiplicity,
                                        app=getattr(self, "app", None),
                                    )
                                elif self.selected_conn.conn_type == "Aggregation":
                                    add_aggregation_part(
                                        self.repo,
                                        new_whole,
                                        new_part,
                                        self.selected_conn.multiplicity,
                                        app=getattr(self, "app", None),
                                    )
                                else:
                                    if self.dragging_endpoint == "dst":
                                        rel.target = obj.element_id
                                        self.selected_conn.dst = obj.obj_id
                                    else:
                                        rel.source = obj.element_id
                                        self.selected_conn.src = obj.obj_id
                            break
                    self._sync_to_repository()
                elif not valid:
                    messagebox.showwarning("Invalid Connection", msg)
            elif obj is None:
                if self.selected_conn in self.connections:
                    self.connections.remove(self.selected_conn)
                    if (
                        src_obj
                        and dst_obj
                        and src_obj.element_id
                        and dst_obj.element_id
                    ):
                        for rel in list(self.repo.relationships):
                            if (
                                rel.source == src_obj.element_id
                                and rel.target == dst_obj.element_id
                                and rel.rel_type == self.selected_conn.conn_type
                            ):
                                self.repo.relationships.remove(rel)
                                diag = self.repo.diagrams.get(self.diagram_id)
                                if diag and rel.rel_id in diag.relationships:
                                    diag.relationships.remove(rel.rel_id)
                                if self.selected_conn.conn_type == "Generalization":
                                    remove_inherited_block_properties(
                                        self.repo,
                                        src_obj.element_id,
                                        dst_obj.element_id,
                                    )
                                    inherit_block_properties(
                                        self.repo, src_obj.element_id
                                    )
                                elif self.selected_conn.conn_type in (
                                    "Aggregation",
                                    "Composite Aggregation",
                                ):
                                    remove_aggregation_part(
                                        self.repo,
                                        src_obj.element_id,
                                        dst_obj.element_id,
                                        remove_object=self.selected_conn.conn_type
                                        == "Composite Aggregation",
                                        app=getattr(self, "app", None),
                                    )
                                break
                    self.selected_conn = None
                    self._sync_to_repository()
            else:
                self._sync_to_repository()
            self.dragging_endpoint = None
            self.conn_drag_offset = None
            self.endpoint_drag_pos = None
        else:
            self.dragging_endpoint = None
            self.conn_drag_offset = None
            self.endpoint_drag_pos = None
        if self.selected_obj and self.current_tool == "Select":
            if self.selected_obj.obj_type != "System Boundary":
                b = self.find_boundary_for_obj(self.selected_obj)
                if b:
                    self.selected_obj.properties["boundary"] = str(b.obj_id)
                else:
                    self.selected_obj.properties.pop("boundary", None)
            self._sync_to_repository()
        self.redraw()

    def on_mouse_move(self, event):
        if self.start and self.current_tool in (
            "Association",
            "Include",
            "Extend",
            "Flow",
            "Propagate",
            "Propagate by Review",
            "Propagate by Approval",
            "Re-use",
            "Connector",
            "Generalization",
            "Generalize",
            "Communication Path",
            "Aggregation",
            "Composite Aggregation",
            "Control Action",
            "Feedback",
        ):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.temp_line_end = (x, y)
            self.redraw()

    def on_mouse_move(self, event):
        if self.start and self.current_tool in (
            "Association",
            "Include",
            "Extend",
            "Flow",
            "Propagate",
            "Propagate by Review",
            "Propagate by Approval",
            "Re-use",
            "Connector",
            "Generalization",
            "Generalize",
            "Communication Path",
            "Aggregation",
            "Composite Aggregation",
            "Control Action",
            "Feedback",
        ):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.temp_line_end = (x, y)
            self.redraw()

    def on_double_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        conn = self.find_connection(x, y)
        obj = None
        if conn is None:
            obj = self.find_object(x, y)
        if conn:
            ConnectionDialog(self, conn)
            self.redraw()
        elif obj:
            if self._open_linked_diagram(obj):
                return
            SysMLObjectDialog(self, obj)
            self._sync_to_repository()
            self.redraw()
            if getattr(self, "app", None):
                self.app.update_views()

    def on_rc_press(self, event):
        self.rc_dragged = False
        self.canvas.scan_mark(event.x, event.y)

    def on_rc_drag(self, event):
        self.rc_dragged = True
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def on_rc_release(self, event):
        if not self.rc_dragged:
            self.show_context_menu(event)

    def show_context_menu(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        conn = self.find_connection(x, y)
        obj = None
        if not conn:
            obj = self.find_object(x, y)
            if not obj:
                diag = self.repo.diagrams.get(self.diagram_id)
                if diag and diag.diag_type == "Internal Block Diagram":
                    menu = tk.Menu(self, tearoff=0)
                    menu.add_command(label="Set Father", command=self._set_diagram_father)
                    menu.tk_popup(event.x_root, event.y_root)
                return
        self.selected_obj = obj
        self.selected_conn = conn
        menu = tk.Menu(self, tearoff=0)
        if obj:
            menu.add_command(label="Properties", command=lambda: self._edit_object(obj))
            diag_id = self.repo.get_linked_diagram(obj.element_id)
            if diag_id and diag_id in self.repo.diagrams or obj.properties.get("view"):
                menu.add_command(
                    label="Open Linked Diagram", command=lambda: self._open_linked_diagram(obj)
                )
            menu.add_separator()
            menu.add_command(label="Copy", command=self.copy_selected)
            menu.add_command(label="Cut", command=self.cut_selected)
            menu.add_command(label="Paste", command=self.paste_selected)
            diag = self.repo.diagrams.get(self.diagram_id)
            if diag and diag.diag_type == "Internal Block Diagram" and obj.obj_type == "Part":
                menu.add_separator()
                menu.add_command(
                    label="Remove Part from Diagram",
                    command=lambda: self.remove_part_diagram(obj),
                )
                menu.add_command(
                    label="Remove Part from Model",
                    command=lambda: self.remove_part_model(obj),
                )
            menu.add_separator()
            menu.add_command(label="Delete", command=self.delete_selected)
        elif conn:
            menu.add_command(label="Properties", command=lambda: ConnectionDialog(self, conn))
            menu.add_separator()
            menu.add_command(label="Delete", command=self.delete_selected)
        menu.tk_popup(event.x_root, event.y_root)

    def _edit_object(self, obj):
        SysMLObjectDialog(self, obj)
        self._sync_to_repository()
        self.redraw()
        if self.app:
            self.app.update_views()
        self.update_property_view()
        if getattr(self, "app", None):
            self.app.update_views()

    def _open_linked_diagram(self, obj) -> bool:
        diag_id = self.repo.get_linked_diagram(obj.element_id)
        if not diag_id and obj.obj_type == "Part":
            def_id = obj.properties.get("definition")
            if def_id:
                diag_id = self.repo.get_linked_diagram(def_id)
        view_id = obj.properties.get("view")
        if (
            obj.obj_type in ("CallBehaviorAction", "Action")
            and diag_id
            and view_id
            and view_id in self.repo.diagrams
        ):
            if messagebox.askyesno("Open Diagram", "Open Behavior Diagram?\nChoose No for View"):
                chosen = diag_id
            else:
                chosen = view_id
        else:
            chosen = diag_id or view_id
        if not chosen or chosen not in self.repo.diagrams:
            return False
        # Avoid opening duplicate windows for the same diagram within the
        # current container. If a child frame already displays the chosen
        # diagram, simply return.
        for child in self.master.winfo_children():
            if getattr(child, "diagram_id", None) == chosen:
                return True
        diag = self.repo.diagrams[chosen]
        history = self.diagram_history + [self.diagram_id]
        if diag.diag_type == "Use Case Diagram":
            UseCaseDiagramWindow(self.master, self.app, diagram_id=chosen, history=history)
        elif diag.diag_type == "Activity Diagram":
            ActivityDiagramWindow(self.master, self.app, diagram_id=chosen, history=history)
        elif diag.diag_type == "BPMN Diagram":
            BPMNDiagramWindow(self.master, self.app, diagram_id=chosen, history=history)
        elif diag.diag_type == "Block Diagram":
            BlockDiagramWindow(self.master, self.app, diagram_id=chosen, history=history)
        elif diag.diag_type == "Internal Block Diagram":
            InternalBlockDiagramWindow(self.master, self.app, diagram_id=chosen, history=history)
        self._sync_to_repository()
        self.destroy()
        return True

    def _set_diagram_father(self) -> None:
        diag = self.repo.diagrams.get(self.diagram_id)
        if not diag or diag.diag_type != "Internal Block Diagram":
            return
        dlg = DiagramPropertiesDialog(self, diag)
        for data in getattr(dlg, "added_parts", []):
            self.objects.append(SysMLObject(**data))
        self._sync_to_repository()
        self.redraw()
        if self.app:
            self.app.update_views()

    def go_back(self):
        if not self.diagram_history:
            return
        prev_id = self.diagram_history.pop()
        diag = self.repo.diagrams.get(prev_id)
        if not diag:
            return
        if diag.diag_type == "Use Case Diagram":
            UseCaseDiagramWindow(
                self.master, self.app, diagram_id=prev_id, history=self.diagram_history
            )
        elif diag.diag_type == "Activity Diagram":
            ActivityDiagramWindow(
                self.master, self.app, diagram_id=prev_id, history=self.diagram_history
            )
        elif diag.diag_type == "BPMN Diagram":
            BPMNDiagramWindow(
                self.master, self.app, diagram_id=prev_id, history=self.diagram_history
            )
        elif diag.diag_type == "Block Diagram":
            BlockDiagramWindow(
                self.master, self.app, diagram_id=prev_id, history=self.diagram_history
            )
        elif diag.diag_type == "Internal Block Diagram":
            InternalBlockDiagramWindow(
                self.master, self.app, diagram_id=prev_id, history=self.diagram_history
            )
        self._sync_to_repository()
        self.destroy()

    def on_ctrl_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    # ------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------
    def find_object(self, x: float, y: float, prefer_port: bool = False) -> SysMLObject | None:
        """Return the diagram object under ``(x, y)``.

        When ``prefer_port`` is ``True`` ports are looked up first so they
        are selected over overlapping parent objects like a Block Boundary.
        """
        if prefer_port:
            for obj in reversed(self.objects):
                if obj.obj_type != "Port":
                    continue
                ox = obj.x * self.zoom
                oy = obj.y * self.zoom
                w = obj.width * self.zoom / 2
                h = obj.height * self.zoom / 2
                if ox - w <= x <= ox + w and oy - h <= y <= oy + h:
                    return obj

        for obj in reversed(self.objects):
            ox = obj.x * self.zoom
            oy = obj.y * self.zoom
            w = obj.width * self.zoom / 2
            h = obj.height * self.zoom / 2
            if obj.obj_type in ("Initial", "Final"):
                r = min(w, h)
                if (x - ox) ** 2 + (y - oy) ** 2 <= r**2:
                    return obj
            elif ox - w <= x <= ox + w and oy - h <= y <= oy + h:
                return obj
        return None

    def hit_resize_handle(self, obj: SysMLObject, x: float, y: float) -> str | None:
        if obj.obj_type in (
            "Initial",
            "Final",
            "Actor",
            "Decision",
            "Merge",
            "Work Product",
        ):
            return None
        margin = 5
        ox = obj.x * self.zoom
        oy = obj.y * self.zoom
        w = obj.width * self.zoom / 2
        h = obj.height * self.zoom / 2
        left = ox - w
        right = ox + w
        top = oy - h
        bottom = oy + h
        near_left = abs(x - left) <= margin
        near_right = abs(x - right) <= margin
        near_top = abs(y - top) <= margin
        near_bottom = abs(y - bottom) <= margin
        if near_left and near_top:
            return "nw"
        if near_right and near_top:
            return "ne"
        if near_left and near_bottom:
            return "sw"
        if near_right and near_bottom:
            return "se"
        if near_left:
            return "w"
        if near_right:
            return "e"
        if near_top:
            return "n"
        if near_bottom:
            return "s"
        return None

    def hit_compartment_toggle(self, obj: SysMLObject, x: float, y: float) -> str | None:
        """Return the label of the compartment toggle hit at *(x, y)* or ``None``."""
        for oid, label, (x1, y1, x2, y2) in self.compartment_buttons:
            if oid == obj.obj_id and x1 <= x <= x2 and y1 <= y <= y2:
                return label
        return None

    def _dist_to_segment(self, p, a, b) -> float:
        px, py = p
        ax, ay = a
        bx, by = b
        if ax == bx and ay == by:
            return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
        t = ((px - ax) * (bx - ax) + (py - ay) * (by - ay)) / ((bx - ax) ** 2 + (by - ay) ** 2)
        t = max(0, min(1, t))
        lx = ax + t * (bx - ax)
        ly = ay + t * (by - ay)
        return ((px - lx) ** 2 + (py - ly) ** 2) ** 0.5

    def _segment_intersection(self, p1, p2, p3, p4):
        """Return intersection point (x, y, t) of segments *p1*-*p2* and *p3*-*p4* or None."""
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if denom == 0:
            return None
        t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / denom
        u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / denom
        if 0 <= t <= 1 and 0 <= u <= 1:
            ix = x1 + t * (x2 - x1)
            iy = y1 + t * (y2 - y1)
            return ix, iy, t
        return None

    def _nearest_diamond_corner(self, obj: SysMLObject, tx: float, ty: float) -> Tuple[float, float]:
        """Return the diamond corner of *obj* closest to the target (*tx*, *ty*)."""
        x = obj.x * self.zoom
        y = obj.y * self.zoom
        w = obj.width * self.zoom / 2
        h = obj.height * self.zoom / 2
        corners = [
            (x, y - h),
            (x + w, y),
            (x, y + h),
            (x - w, y),
        ]
        return min(corners, key=lambda p: (p[0] - tx) ** 2 + (p[1] - ty) ** 2)

    def find_connection(self, x: float, y: float) -> DiagramConnection | None:
        diag = self.repo.diagrams.get(self.diagram_id)
        for conn in self.connections:
            src = self.get_object(conn.src)
            dst = self.get_object(conn.dst)
            if not src or not dst:
                continue
            # Control flow connectors are drawn as a vertical line between
            # elements. Mirror that behavior so they can be located when
            # selecting.
            if diag and diag.diag_type == "Control Flow Diagram" and conn.conn_type in (
                "Control Action",
                "Feedback",
            ):
                a_left = src.x - src.width / 2
                a_right = src.x + src.width / 2
                b_left = dst.x - dst.width / 2
                b_right = dst.x + dst.width / 2
                cx_val = (
                    conn.points[0][0]
                    if conn.points
                    else (max(a_left, b_left) + min(a_right, b_right)) / 2
                )
                cx_val = SysMLDiagramWindow._constrain_control_flow_x(
                    self, conn, cx_val
                )
                cx = cx_val * self.zoom
                ayc = src.y * self.zoom
                byc = dst.y * self.zoom
                if ayc <= byc:
                    cy1 = ayc + src.height / 2 * self.zoom
                    cy2 = byc - dst.height / 2 * self.zoom
                else:
                    cy1 = ayc - src.height / 2 * self.zoom
                    cy2 = byc + dst.height / 2 * self.zoom
                if (
                    self._dist_to_segment((x, y), (cx, cy1), (cx, cy2))
                    <= CONNECTION_SELECT_RADIUS
                ):
                    return conn
                continue

            if conn.src == conn.dst:
                sx, sy = self.edge_point(src, 0, 0, (1, 0))
                size = max(src.width, src.height) * 0.5 * self.zoom
                points = [
                    (sx, sy),
                    (sx + size, sy),
                    (sx + size, sy - size),
                    (sx, sy - size),
                    (sx, sy),
                ]
            else:
                sx, sy = self.edge_point(
                    src,
                    dst.x * self.zoom,
                    dst.y * self.zoom,
                    conn.src_pos,
                )
                points = [(sx, sy)]
                if conn.style == "Squared":
                    if conn.points:
                        mx = conn.points[0][0] * self.zoom
                    else:
                        mx = (src.x + dst.x) / 2 * self.zoom
                    points.extend([(mx, points[-1][1]), (mx, dst.y * self.zoom)])
                elif conn.style == "Custom":
                    for px, py in conn.points:
                        xpt = px * self.zoom
                        ypt = py * self.zoom
                        last = points[-1]
                        points.extend([(xpt, last[1]), (xpt, ypt)])
                ex, ey = self.edge_point(
                    dst,
                    src.x * self.zoom,
                    src.y * self.zoom,
                    conn.dst_pos,
                )
                points.append((ex, ey))
            for a, b in zip(points[:-1], points[1:]):
                if self._dist_to_segment((x, y), a, b) <= CONNECTION_SELECT_RADIUS:
                    return conn
        return None

    def snap_port_to_parent(self, port: SysMLObject, parent: SysMLObject) -> None:
        snap_port_to_parent_obj(port, parent)

    def edge_point(
        self,
        obj: SysMLObject,
        tx: float,
        ty: float,
        rel: tuple[float, float] | None = None,
        apply_radius: bool = True,
    ) -> Tuple[float, float]:
        cx = obj.x * self.zoom
        cy = obj.y * self.zoom

        def _intersect(vx: float, vy: float, w: float, h: float, r: float) -> Tuple[float, float]:
            """Return intersection of a ray from the origin with a rounded rectangle."""
            if vx == 0 and vy == 0:
                return 0.0, 0.0

            wi, hi = w - r, h - r
            signx = 1 if vx >= 0 else -1
            signy = 1 if vy >= 0 else -1
            candidates: list[tuple[float, float, float]] = []

            if vx != 0:
                t_v = (signx * w) / vx
                if t_v >= 0:
                    y_v = vy * t_v
                    if abs(y_v) <= hi:
                        candidates.append((t_v, signx * w, y_v))

            if vy != 0:
                t_h = (signy * h) / vy
                if t_h >= 0:
                    x_h = vx * t_h
                    if abs(x_h) <= wi:
                        candidates.append((t_h, x_h, signy * h))

            if r > 0:
                cx_arc, cy_arc = signx * wi, signy * hi
                a = vx * vx + vy * vy
                b = -2 * (vx * cx_arc + vy * cy_arc)
                c = cx_arc * cx_arc + cy_arc * cy_arc - r * r
                disc = b * b - 4 * a * c
                if disc >= 0:
                    sqrt_disc = math.sqrt(disc)
                    for t_arc in ((-b - sqrt_disc) / (2 * a), (-b + sqrt_disc) / (2 * a)):
                        if t_arc >= 0:
                            x_arc = vx * t_arc
                            y_arc = vy * t_arc
                            if signx * x_arc >= wi and signy * y_arc >= hi:
                                candidates.append((t_arc, x_arc, y_arc))

            if not candidates:
                return 0.0, 0.0

            t, ix, iy = min(candidates, key=lambda c: c[0])
            return ix, iy

        if obj.obj_type == "Port":
            # Ports are drawn as 12x12 squares regardless of object width/height.
            # Compute the intersection with this square so connectors touch its edge
            # rather than reaching the center.
            w = h = 6 * self.zoom
            if rel is not None:
                rx, ry = rel
                vx = rx * w
                vy = ry * h
            else:
                vx = tx - cx
                vy = ty - cy
            ix, iy = _intersect(vx, vy, w, h, 0.0)
            return cx + ix, cy + iy

        w = obj.width * self.zoom / 2
        h = obj.height * self.zoom / 2
        radius = 0.0
        if apply_radius:
            if obj.obj_type == "Block":
                radius = 6 * self.zoom
            elif obj.obj_type == "System Boundary":
                radius = 12 * self.zoom
            elif obj.obj_type in ("Action Usage", "Action", "CallBehaviorAction"):
                radius = 8 * self.zoom

        if rel is not None:
            rx, ry = rel
            if obj.obj_type in ("Decision", "Merge"):
                if abs(rx) >= abs(ry):
                    return (cx + (w if rx >= 0 else -w), cy)
                else:
                    return (cx, cy + (h if ry >= 0 else -h))
            vx = rx * obj.width / 2 * self.zoom
            vy = ry * obj.height / 2 * self.zoom
            ix, iy = _intersect(vx, vy, w, h, radius if apply_radius else 0.0)
            return cx + ix, cy + iy

        dx = tx - cx
        dy = ty - cy
        if obj.obj_type in ("Initial", "Final"):
            r = min(w, h)
            dist = (dx**2 + dy**2) ** 0.5 or 1
            return cx + dx / dist * r, cy + dy / dist * r
        if obj.obj_type in ("Decision", "Merge"):
            points = [
                (cx, cy - h),
                (cx + w, cy),
                (cx, cy + h),
                (cx - w, cy),
            ]
            best = None
            for i in range(len(points)):
                p3 = points[i]
                p4 = points[(i + 1) % len(points)]
                inter = SysMLDiagramWindow._segment_intersection(
                    self, (cx, cy), (tx, ty), p3, p4
                )
                if inter:
                    ix, iy, t = inter
                    if best is None or t < best[2]:
                        best = (ix, iy, t)
            if best:
                return best[0], best[1]

        ix, iy = _intersect(dx, dy, w, h, radius)
        return cx + ix, cy + iy

    def sync_ports(self, part: SysMLObject) -> None:
        names: List[str] = []
        block_id = part.properties.get("definition")
        if block_id and block_id in self.repo.elements:
            block_elem = self.repo.elements[block_id]
            names.extend(
                [p.strip() for p in block_elem.properties.get("ports", "").split(",") if p.strip()]
            )
        names.extend([p.strip() for p in part.properties.get("ports", "").split(",") if p.strip()])
        existing_ports = [
            o
            for o in self.objects
            if o.obj_type == "Port" and o.properties.get("parent") == str(part.obj_id)
        ]
        existing: dict[str, SysMLObject] = {}
        for p in list(existing_ports):
            name = p.properties.get("name")
            if name in existing:
                self.objects.remove(p)
            else:
                existing[name] = p
        for n in names:
            if n not in existing:
                port = SysMLObject(
                    _get_next_id(),
                    "Port",
                    part.x + part.width / 2 + 20,
                    part.y,
                    properties={
                        "name": n,
                        "parent": str(part.obj_id),
                        "side": "E",
                        "labelX": "8",
                        "labelY": "-8",
                    },
                )
                self.snap_port_to_parent(port, part)
                self.objects.append(port)
                existing[n] = port
        for n, obj in list(existing.items()):
            if n not in names:
                self.objects.remove(obj)
        self.sort_objects()

    def sync_boundary_ports(self, boundary: SysMLObject) -> None:
        names: List[str] = []
        block_id = boundary.element_id
        if block_id and block_id in self.repo.elements:
            block_elem = self.repo.elements[block_id]
            names.extend([
                p.strip() for p in block_elem.properties.get("ports", "").split(",") if p.strip()
            ])
        existing_ports = [
            o
            for o in self.objects
            if o.obj_type == "Port" and o.properties.get("parent") == str(boundary.obj_id)
        ]
        existing: dict[str, SysMLObject] = {}
        for p in list(existing_ports):
            name = p.properties.get("name")
            if name in existing:
                self.objects.remove(p)
            else:
                existing[name] = p
        for n in names:
            if n not in existing:
                port = SysMLObject(
                    _get_next_id(),
                    "Port",
                    boundary.x + boundary.width / 2 + 20,
                    boundary.y,
                    properties={
                        "name": n,
                        "parent": str(boundary.obj_id),
                        "side": "E",
                        "labelX": "8",
                        "labelY": "-8",
                    },
                )
                self.snap_port_to_parent(port, boundary)
                self.objects.append(port)
                existing[n] = port
        for n, obj in list(existing.items()):
            if n not in names:
                self.objects.remove(obj)
        self.sort_objects()

    def zoom_in(self):
        self.zoom *= 1.2
        self.font.config(size=int(8 * self.zoom))
        self.redraw()

    def zoom_out(self):
        self.zoom /= 1.2
        self.font.config(size=int(8 * self.zoom))
        self.redraw()

    def _block_compartments(self, obj: SysMLObject) -> list[tuple[str, str]]:
        """Return the list of compartments displayed for a Block."""
        parts = "\n".join(
            p.strip()
            for p in obj.properties.get("partProperties", "").split(",")
            if p.strip()
        )
        operations = "\n".join(
            format_operation(op)
            for op in parse_operations(obj.properties.get("operations", ""))
        )
        ports = "\n".join(
            p.strip() for p in obj.properties.get("ports", "").split(",") if p.strip()
        )
        reliability = "\n".join(
            f"{label}={obj.properties.get(key, '')}"
            for label, key in (
                ("FIT", "fit"),
                ("Qual", "qualification"),
                ("FM", "failureModes"),
            )
            if obj.properties.get(key, "")
        )
        requirements = "\n".join(r.get("id") for r in obj.requirements)
        return [
            ("Parts", parts),
            ("Operations", operations),
            ("Ports", ports),
            ("Reliability", reliability),
            ("Requirements", requirements),
        ]

    def _min_block_size(self, obj: SysMLObject) -> tuple[float, float]:
        """Return minimum width and height to display all Block text."""
        header = f"<<block>> {obj.properties.get('name', '')}".strip()
        width_px = self.font.measure(header) + 8 * self.zoom
        compartments = self._block_compartments(obj)
        total_lines = 1
        button_w = 12 * self.zoom
        for label, text in compartments:
            collapsed = obj.collapsed.get(label, False)
            lines = text.splitlines() if text else [""]
            if collapsed:
                # When collapsed only show the compartment name, not the first
                # element. Previously the first line of the compartment content
                # was appended which caused the label to display e.g.
                # "Parts: Motor". The design has changed to only display the
                # compartment title when collapsed so that it simply reads
                # "Parts".
                disp = f"{label}:"
                width_px = max(width_px, self.font.measure(disp) + button_w + 8 * self.zoom)
                total_lines += 1
            else:
                disp = f"{label}:"
                width_px = max(width_px, self.font.measure(disp) + button_w + 8 * self.zoom)
                for line in lines:
                    width_px = max(width_px, self.font.measure(line) + 8 * self.zoom)
                total_lines += 1 + len(lines)
        height_px = total_lines * 20 * self.zoom
        return width_px / self.zoom, height_px / self.zoom

    def _min_action_size(self, obj: SysMLObject) -> tuple[float, float]:
        """Return minimum width and height to display Action text without wrapping."""
        full_width_obj = replace(obj, width=10_000)
        lines = self._object_label_lines(full_width_obj)
        if not lines:
            return (10.0, 10.0)
        text_width = max(self.font.measure(line) for line in lines)
        text_height = self.font.metrics("linespace") * len(lines)
        padding = 6 * self.zoom
        return (text_width + padding) / self.zoom, (text_height + padding) / self.zoom

    def _wrap_text_to_width(self, text: str, width_px: float) -> list[str]:
        """Return *text* wrapped to fit within *width_px* pixels."""
        if self.font.measure(text) <= width_px:
            return [text]
        words = text.split()
        if not words:
            words = [text]

        if len(words) == 1 and self.font.measure(words[0]) > width_px:
            # single long word - wrap by characters
            lines: list[str] = []
            current = ""
            for ch in words[0]:
                if self.font.measure(current + ch) <= width_px:
                    current += ch
                else:
                    if current:
                        lines.append(current)
                    current = ch
            if current:
                lines.append(current)
            return lines

        lines: list[str] = []
        current = words[0]
        for word in words[1:]:
            candidate = current + " " + word
            if self.font.measure(candidate) <= width_px:
                current = candidate
            else:
                lines.append(current)
                if self.font.measure(word) <= width_px:
                    current = word
                else:
                    # break long word
                    part = ""
                    for ch in word:
                        if self.font.measure(part + ch) <= width_px:
                            part += ch
                        else:
                            if part:
                                lines.append(part)
                            part = ch
                    current = part
        if current:
            lines.append(current)
        return lines

    def _object_label_lines(self, obj: SysMLObject) -> list[str]:
        """Return the lines of text displayed inside *obj*."""
        if obj.obj_type == "System Boundary" or obj.obj_type == "Block Boundary":
            name = obj.properties.get("name", "")
            return [name] if name else []

        if obj.obj_type in ("Block", "Port"):
            # Blocks and ports use custom drawing logic
            return []

        name = obj.properties.get("name", "")
        has_name = False
        def_id = obj.properties.get("definition")
        if obj.element_id and obj.element_id in self.repo.elements:
            elem = self.repo.elements[obj.element_id]
            name = elem.name or elem.properties.get("component", "")
            def_id = def_id or elem.properties.get("definition")
            def_name = ""
            if def_id and def_id in self.repo.elements:
                def_name = self.repo.elements[def_id].name or def_id
            has_name = bool(name) and not _is_default_part_name(def_name, name)

        if not has_name:
            name = ""
        if obj.obj_type == "Part":
            asil = calculate_allocated_asil(obj.requirements)
            if obj.properties.get("asil") != asil:
                obj.properties["asil"] = asil
                if obj.element_id and obj.element_id in self.repo.elements:
                    self.repo.elements[obj.element_id].properties["asil"] = asil
            def_id = obj.properties.get("definition")
            mult = None
            comp = obj.properties.get("component", "")
            if def_id and def_id in self.repo.elements:
                def_name = self.repo.elements[def_id].name or def_id
                diag = self.repo.diagrams.get(self.diagram_id)
                block_id = (
                    getattr(diag, "father", None)
                    or next(
                        (
                            eid
                            for eid, did in self.repo.element_diagrams.items()
                            if did == self.diagram_id
                        ),
                        None,
                    )
                )
                if block_id:
                    for rel in self.repo.relationships:
                        if (
                            rel.rel_type in ("Aggregation", "Composite Aggregation")
                            and rel.source == block_id
                            and rel.target == def_id
                        ):
                            mult = rel.properties.get("multiplicity", "1")
                            if mult in ("", "1"):
                                mult = None
                            break
                base = name
                index = None
                m = re.match(r"^(.*)\[(\d+)\]$", name)
                if m:
                    base = m.group(1)
                    index = int(m.group(2))
                if index is not None:
                    base = f"{base} {index}"
                name = base
                if obj.element_id and obj.element_id in self.repo.elements and not comp:
                    comp = self.repo.elements[obj.element_id].properties.get("component", "")
                if comp and comp == def_name:
                    comp = ""
                if mult:
                    if ".." in mult:
                        upper = mult.split("..", 1)[1] or "*"
                        disp = f"{index or 1}..{upper}"
                    elif mult == "*":
                        disp = f"{index or 1}..*"
                    else:
                        disp = f"{index or 1}..{mult}"
                    def_part = f"{def_name} [{disp}]"
                else:
                    def_part = def_name
                if comp:
                    def_part = f"{comp} / {def_part}"
                if name and def_part != name:
                    name = f"{name} : {def_part}"
                elif not name:
                    name = f" : {def_part}"

        lines: list[str] = []
        diag_id = self.repo.get_linked_diagram(obj.element_id)
        if diag_id and diag_id in self.repo.diagrams:
            diag = self.repo.diagrams[diag_id]
            diag_name = diag.name or diag_id
            lines.append(diag_name)

        if obj.obj_type in ("Action", "CallBehaviorAction") and name:
            max_width = obj.width * self.zoom - 6 * self.zoom
            if max_width > 0:
                wrapped = self._wrap_text_to_width(name, max_width)
                lines.extend(wrapped)
            else:
                lines.append(name)
        elif obj.obj_type == "Work Product" and name:
            lines.extend(name.split())
        else:
            lines.append(name)

        key = obj.obj_type.replace(" ", "")
        if not key.endswith("Usage"):
            key += "Usage"
        for prop in SYSML_PROPERTIES.get(key, []):
            if obj.obj_type == "Part" and prop in (
                "fit",
                "qualification",
                "failureModes",
                "asil",
            ):
                continue
            val = obj.properties.get(prop)
            if val:
                lines.append(f"{prop}: {val}")

        if obj.obj_type == "Part":
            rel_items = []
            for lbl, key in (
                ("ASIL", "asil"),
                ("FIT", "fit"),
                ("Qual", "qualification"),
                ("FM", "failureModes"),
            ):
                val = obj.properties.get(key)
                if val:
                    rel_items.append(f"{lbl}: {val}")
            if rel_items:
                lines.extend(rel_items)
            reqs = "; ".join(r.get("id") for r in obj.requirements)
            if reqs:
                lines.append(f"Reqs: {reqs}")

        return lines

    def ensure_text_fits(self, obj: SysMLObject) -> None:
        """Expand the object's size so its label is fully visible."""
        if obj.obj_type == "Block":
            b_w, b_h = self._min_block_size(obj)
            min_w, min_h = b_w, b_h
        else:
            label_lines = self._object_label_lines(obj)
            if not label_lines:
                return

            text_width = max(self.font.measure(line) for line in label_lines)
            text_height = self.font.metrics("linespace") * len(label_lines)
            if obj.obj_type in ("Action", "CallBehaviorAction"):
                padding = 6 * self.zoom
                if text_width + padding <= obj.width * self.zoom:
                    min_w = obj.width
                else:
                    min_w = (text_width + padding) / self.zoom
            else:
                padding = 10 * self.zoom
                min_w = (text_width + padding) / self.zoom
            min_h = (text_height + padding) / self.zoom

        if obj.obj_type in ("Block",):
            # _min_block_size already accounts for text padding
            pass
        elif obj.obj_type in (
            "Fork",
            "Join",
            "Initial",
            "Final",
            "Decision",
            "Merge",
        ):
            min_h = obj.height  # height remains unchanged for these types
        if min_w > obj.width:
            obj.width = min_w
        if obj.obj_type not in (
            "Fork",
            "Join",
            "Initial",
            "Final",
            "Decision",
            "Merge",
        ) and min_h > obj.height:
            obj.height = min_h

    def sort_objects(self) -> None:
        """Order objects so boundaries render behind and their ports above."""

        def key(o: SysMLObject) -> int:
            if o.obj_type in ("System Boundary", "Block Boundary", "Existing Element"):
                return 0
            if o.obj_type == "Port":
                parent_id = o.properties.get("parent")
                if parent_id:
                    try:
                        pid = int(parent_id)
                    except (TypeError, ValueError):
                        pid = None
                    if pid is not None:
                        for obj in self.objects:
                            if obj.obj_id == pid and obj.obj_type == "Block Boundary":
                                return 2
            return 1

        self.objects.sort(key=key)

    def redraw(self):
        self.canvas.delete("all")
        self.gradient_cache.clear()
        self.compartment_buttons = []
        self.sort_objects()
        remove_orphan_ports(self.objects)
        for obj in list(self.objects):
            if getattr(obj, "hidden", False):
                continue
            if obj.obj_type == "Part":
                self.sync_ports(obj)
            if obj.obj_type == "Block Boundary":
                self.sync_boundary_ports(obj)
            self.ensure_text_fits(obj)
            self.draw_object(obj)
        for conn in self.connections:
            src = self.get_object(conn.src)
            dst = self.get_object(conn.dst)
            if (
                src
                and dst
                and not getattr(src, "hidden", False)
                and not getattr(dst, "hidden", False)
            ):
                if (
                    conn is self.selected_conn
                    and self.dragging_endpoint is not None
                    and self.endpoint_drag_pos
                ):
                    continue
                self.draw_connection(src, dst, conn, conn is self.selected_conn)
        if (
            self.selected_conn
            and self.dragging_endpoint is not None
            and self.endpoint_drag_pos
        ):
            other = (
                self.get_object(self.selected_conn.dst)
                if self.dragging_endpoint == "src"
                else self.get_object(self.selected_conn.src)
            )
            if other:
                rel = (
                    self.selected_conn.dst_pos
                    if self.dragging_endpoint == "src"
                    else self.selected_conn.src_pos
                )
                sx, sy = self.edge_point(other, *self.endpoint_drag_pos, rel)
                ex, ey = self.endpoint_drag_pos
                forward = self.selected_conn.arrow in ("forward", "both")
                backward = self.selected_conn.arrow in ("backward", "both")
                if self.dragging_endpoint == "src":
                    arrow_start = backward
                    arrow_end = forward
                else:
                    arrow_start = backward
                    arrow_end = forward
                if arrow_start and arrow_end:
                    style = tk.BOTH
                elif arrow_end:
                    style = tk.LAST
                elif arrow_start:
                    style = tk.FIRST
                else:
                    style = tk.NONE
                self.canvas.create_line(
                    sx,
                    sy,
                    ex,
                    ey,
                    dash=(2, 2),
                    arrow=style,
                    tags="connection",
                )
        if (
            self.start
            and self.temp_line_end
            and self.current_tool
            in (
                "Association",
                "Include",
                "Extend",
                "Flow",
                "Connector",
                "Generalization",
                "Generalize",
                "Communication Path",
                "Aggregation",
                "Composite Aggregation",
                "Control Action",
                "Feedback",
            )
        ):
            sx, sy = self.edge_point(self.start, *self.temp_line_end)
            ex, ey = self.temp_line_end
            self.canvas.create_line(
                sx, sy, ex, ey, dash=(2, 2), arrow=tk.LAST, tags="connection"
            )
        self.canvas.tag_raise("connection")
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _create_round_rect(self, x1, y1, x2, y2, radius=10, **kwargs):
        """Draw a rectangle with rounded corners on the canvas."""
        rad = min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2)
        points = [
            x1 + rad,
            y1,
            x2 - rad,
            y1,
            x2,
            y1,
            x2,
            y1 + rad,
            x2,
            y2 - rad,
            x2,
            y2,
            x2 - rad,
            y2,
            x1 + rad,
            y2,
            x1,
            y2,
            x1,
            y2 - rad,
            x1,
            y1 + rad,
            x1,
            y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, splinesteps=36, **kwargs)

    def _create_gradient_image(self, width: int, height: int, color: str) -> tk.PhotoImage:
        """Return a left-to-right gradient image from white to *color*."""
        width = max(1, int(width))
        height = max(1, int(height))
        img = tk.PhotoImage(width=width, height=height)
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        for x in range(width):
            ratio = x / (width - 1) if width > 1 else 1
            nr = int(255 * (1 - ratio) + r * ratio)
            ng = int(255 * (1 - ratio) + g * ratio)
            nb = int(255 * (1 - ratio) + b * ratio)
            img.put(f"#{nr:02x}{ng:02x}{nb:02x}", to=(x, 0, x + 1, height))
        return img

    def _draw_gradient_rect(self, x1: float, y1: float, x2: float, y2: float, color: str, obj_id: int) -> None:
        """Draw a gradient rectangle on the canvas and cache the image."""
        img = self._create_gradient_image(abs(int(x2 - x1)), abs(int(y2 - y1)), color)
        self.canvas.create_image(min(x1, x2), min(y1, y2), anchor="nw", image=img)
        self.gradient_cache[obj_id] = img


    def _draw_open_arrow(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str = "black",
        width: int = 1,
        tags: str = "connection",
    ) -> None:
        """Draw an open triangular arrow head from *start* to *end*.

        This helper creates the classic hollow triangle used for
        generalization relationships. The interior is filled with the
        canvas background so the outline color defines the arrow shape.
        """
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        size = 10 * self.zoom
        angle = math.atan2(dy, dx)
        spread = math.radians(20)
        p1 = (
            end[0] - size * math.cos(angle - spread),
            end[1] - size * math.sin(angle - spread),
        )
        p2 = (
            end[0] - size * math.cos(angle + spread),
            end[1] - size * math.sin(angle + spread),
        )
        # Draw the arrowhead as a small white triangle with the requested
        # outline color. Using a filled polygon ensures the arrowhead remains
        # visible regardless of the canvas background color.
        self.canvas.create_polygon(
            end,
            p1,
            p2,
            fill="white",
            outline=color,
            width=width,
            tags=tags,
        )

    def _draw_line_arrow(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str = "black",
        width: int = 1,
        tags: str = "connection",
    ) -> None:
        """Draw an open arrow using only line segments.

        The arrow head is composed of two lines so that the center line of
        the connection meets the arrow tip directly, providing a cleaner
        look for port direction indicators.
        """
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        # Use a slightly smaller arrow head so the direction indicator
        # fits nicely on the tiny port square.
        size = 6 * self.zoom
        angle = math.atan2(dy, dx)
        spread = math.radians(20)
        p1 = (
            end[0] - size * math.cos(angle - spread),
            end[1] - size * math.sin(angle - spread),
        )
        p2 = (
            end[0] - size * math.cos(angle + spread),
            end[1] - size * math.sin(angle + spread),
        )
        self.canvas.create_line(
            end[0],
            end[1],
            p1[0],
            p1[1],
            fill=color,
            width=width,
            tags=tags,
        )
        self.canvas.create_line(
            end[0],
            end[1],
            p2[0],
            p2[1],
            fill=color,
            width=width,
            tags=tags,
        )

    def _draw_line_arrow(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str = "black",
        width: int = 1,
        tags: str = "connection",
    ) -> None:
        """Draw an open arrow using only line segments.

        The arrow head is composed of two lines so that the center line of
        the connection meets the arrow tip directly, providing a cleaner
        look for port direction indicators.
        """
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        # Use a tiny arrow head so the indicator does not dwarf the port.
        size = 3 * self.zoom
        angle = math.atan2(dy, dx)
        spread = math.radians(20)
        p1 = (
            end[0] - size * math.cos(angle - spread),
            end[1] - size * math.sin(angle - spread),
        )
        p2 = (
            end[0] - size * math.cos(angle + spread),
            end[1] - size * math.sin(angle + spread),
        )
        self.canvas.create_line(
            end[0],
            end[1],
            p1[0],
            p1[1],
            fill=color,
            width=width,
            tags=tags,
        )
        self.canvas.create_line(
            end[0],
            end[1],
            p2[0],
            p2[1],
            fill=color,
            width=width,
            tags=tags,
        )

    def _draw_filled_arrow(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str = "black",
        width: int = 1,
        tags: str = "connection",
    ) -> None:
        """Draw a filled triangular arrow from *start* to *end*."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        size = 10 * self.zoom
        angle = math.atan2(dy, dx)
        spread = math.radians(20)
        p1 = (
            end[0] - size * math.cos(angle - spread),
            end[1] - size * math.sin(angle - spread),
        )
        p2 = (
            end[0] - size * math.cos(angle + spread),
            end[1] - size * math.sin(angle + spread),
        )
        self.canvas.create_polygon(
            end,
            p1,
            p2,
            fill=color,
            outline=color,
            width=width,
            tags=tags,
        )

    def _draw_open_diamond(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str = "black",
        width: int = 1,
        tags: str = "connection",
    ) -> None:
        """Draw an open diamond from *start* to *end*."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        size = 10 * self.zoom
        angle = math.atan2(dy, dx)
        p1 = (
            end[0] - size * math.cos(angle),
            end[1] - size * math.sin(angle),
        )
        p2 = (
            p1[0] - size * math.sin(angle) / 2,
            p1[1] + size * math.cos(angle) / 2,
        )
        p3 = (
            end[0] - 2 * size * math.cos(angle),
            end[1] - 2 * size * math.sin(angle),
        )
        p4 = (
            p1[0] + size * math.sin(angle) / 2,
            p1[1] - size * math.cos(angle) / 2,
        )
        self.canvas.create_polygon(
            end,
            p2,
            p3,
            p4,
            fill=self.canvas.cget("background"),
            outline=color,
            width=width,
            tags=tags,
        )

    def _draw_filled_diamond(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str = "black",
        width: int = 1,
        tags: str = "connection",
    ) -> None:
        """Draw a filled diamond from *start* to *end*."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        size = 10 * self.zoom
        angle = math.atan2(dy, dx)
        p1 = (
            end[0] - size * math.cos(angle),
            end[1] - size * math.sin(angle),
        )
        p2 = (
            p1[0] - size * math.sin(angle) / 2,
            p1[1] + size * math.cos(angle) / 2,
        )
        p3 = (
            end[0] - 2 * size * math.cos(angle),
            end[1] - 2 * size * math.sin(angle),
        )
        p4 = (
            p1[0] + size * math.sin(angle) / 2,
            p1[1] - size * math.cos(angle) / 2,
        )
        self.canvas.create_polygon(
            end,
            p2,
            p3,
            p4,
            fill=color,
            outline=color,
            width=width,
            tags=tags,
        )

    def _draw_center_triangle(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str = "black",
        width: int = 1,
        tags: str = "connection",
    ) -> None:
        """Draw a small triangular arrow pointing from *start* to *end*.

        The triangle is centered on the line segment defined by the start
        and end points and scales with the current zoom level.
        """
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2
        # Slightly enlarge the arrowhead to make flow direction clearer
        size = 10 * self.zoom
        angle = math.atan2(dy, dx)
        spread = math.radians(20)
        p1 = (mx, my)
        p2 = (
            mx - size * math.cos(angle - spread),
            my - size * math.sin(angle - spread),
        )
        p3 = (
            mx - size * math.cos(angle + spread),
            my - size * math.sin(angle + spread),
        )
        self.canvas.create_polygon(
            p1,
            p2,
            p3,
            fill=color,
            outline=color,
            width=width,
            tags=tags,
        )

    def _draw_subdiagram_marker(self, right: float, bottom: float) -> None:
        """Draw a small indicator showing a linked lower level diagram."""

        size = 8 * self.zoom
        pad = 2 * self.zoom
        x1 = right - size - pad
        y1 = bottom - size - pad
        x2 = right - pad
        y2 = bottom - pad
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="white")
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        self.canvas.create_text(
            cx,
            cy,
            text="∞",
            font=("Arial", int(6 * self.zoom)),
            fill="black",
        )

    def draw_object(self, obj: SysMLObject):
        x = obj.x * self.zoom
        y = obj.y * self.zoom
        w = obj.width * self.zoom / 2
        h = obj.height * self.zoom / 2
        color = StyleManager.get_instance().get_color(obj.obj_type)
        outline = "black"
        if obj.obj_type == "Actor":
            sx = obj.width / 80.0 * self.zoom
            sy = obj.height / 40.0 * self.zoom
            self.canvas.create_oval(
                x - 10 * sx,
                y - 30 * sy,
                x + 10 * sx,
                y - 10 * sy,
                outline=outline,
                fill=color,
            )
            self.canvas.create_line(x, y - 10 * sy, x, y + 20 * sy, fill=outline)
            self.canvas.create_line(x - 15 * sx, y, x + 15 * sx, y, fill=outline)
            self.canvas.create_line(
                x,
                y + 20 * sy,
                x - 10 * sx,
                y + 40 * sy,
                fill=outline,
            )
            self.canvas.create_line(
                x,
                y + 20 * sy,
                x + 10 * sx,
                y + 40 * sy,
                fill=outline,
            )
        elif obj.obj_type == "Use Case":
            self.canvas.create_oval(
                x - w,
                y - h,
                x + w,
                y + h,
                fill=color,
                outline=outline,
            )
        elif obj.obj_type == "System Boundary":
            self._draw_gradient_rect(x - w, y - h, x + w, y + h, color, obj.obj_id)
            self._create_round_rect(
                x - w,
                y - h,
                x + w,
                y + h,
                radius=12 * self.zoom,
                dash=(4, 2),
                outline=outline,
                fill="",
            )
            label = obj.properties.get("name", "")
            if label:
                diag = self.repo.diagrams.get(self.diagram_id)
                if diag and diag.diag_type in ("Activity Diagram", "BPMN Diagram"):
                    lx = x - w - 4 * self.zoom
                    ly = y
                    self.canvas.create_text(
                        lx,
                        ly,
                        text=label,
                        angle=90,
                        anchor="e",
                        font=self.font,
                    )
                else:
                    lx = x
                    ly = y - h - 4 * self.zoom
                    self.canvas.create_text(
                        lx,
                        ly,
                        text=label,
                        anchor="s",
                        font=self.font,
                    )
        elif obj.obj_type == "Block Boundary":
            self._create_round_rect(
                x - w,
                y - h,
                x + w,
                y + h,
                radius=12 * self.zoom,
                dash=(4, 2),
                outline=outline,
                fill="",
            )
            label = obj.properties.get("name", "")
            if label:
                lx = x
                ly = y - h - 4 * self.zoom
                self.canvas.create_text(
                    lx,
                    ly,
                    text=label,
                    anchor="s",
                    font=self.font,
                )
        elif obj.obj_type == "Work Product":
            label = obj.properties.get("name", "")
            diagram_products = {
                "Architecture Diagram",
                "Safety & Security Concept",
                "Product Goal Specification",
                *REQUIREMENT_WORK_PRODUCTS,
            }
            analysis_products = {
                "HAZOP",
                "STPA",
                "Threat Analysis",
                "FI2TC",
                "TC2FI",
                "Risk Assessment",
                "FTA",
                "FMEA",
                "FMEDA",
            }
            if label in diagram_products:
                color = "#cfe2f3"
            elif label in analysis_products:
                color = "#d5e8d4"
            else:
                color = "#ffffff"
            self._create_round_rect(
                x - w,
                y - h,
                x + w,
                y + h,
                radius=8 * self.zoom,
                outline=outline,
                fill=color,
            )
            fold = 10 * self.zoom
            fold_color = "#fdfdfd"
            self.canvas.create_polygon(
                x + w - fold,
                y - h,
                x + w,
                y - h,
                x + w,
                y - h + fold,
                fill=fold_color,
                outline=outline,
            )
            self.canvas.create_line(
                x + w - fold,
                y - h,
                x + w - fold,
                y - h + fold,
                fill=outline,
            )
            if label:
                self.canvas.create_text(
                    x,
                    y,
                    text=label.replace(" ", "\n"),
                    anchor="center",
                    font=self.font,
                    width=obj.width * self.zoom,
                )
        elif obj.obj_type == "Lifecycle Phase":
            color = "#F4D698"
            tab_h = 10 * self.zoom
            tab_w = min(obj.width * self.zoom / 2, 40 * self.zoom)
            body_top = y - h + tab_h
            self._draw_gradient_rect(x - w, body_top, x + w, y + h, color, obj.obj_id)
            self.canvas.create_rectangle(
                x - w,
                body_top,
                x + w,
                y + h,
                outline=outline,
                fill="",
            )
            self.canvas.create_rectangle(
                x - w,
                y - h,
                x - w + tab_w,
                body_top,
                outline=outline,
                fill=color,
            )
            label = obj.properties.get("name", "")
            if label:
                self.canvas.create_text(
                    x,
                    y,
                    text=label,
                    anchor="center",
                    font=self.font,
                    width=obj.width * self.zoom,
                )
        elif obj.obj_type == "Existing Element":
            element = self.repo.elements.get(obj.element_id)
            if element:
                color = StyleManager.get_instance().get_color(element.elem_type)
            outline = color
            self._draw_gradient_rect(x - w, y - h, x + w, y + h, color, obj.obj_id)
            self._create_round_rect(
                x - w,
                y - h,
                x + w,
                y + h,
                radius=12 * self.zoom,
                dash=(),
                outline=outline,
                fill="",
            )
            diag = self.repo.diagrams.get(self.diagram_id)
            if not diag or diag.diag_type != "Control Flow Diagram":
                label = obj.properties.get("name", "")
                if label:
                    lx = x
                    ly = y - h - 4 * self.zoom
                    self.canvas.create_text(
                        lx,
                        ly,
                        text=label,
                        anchor="s",
                        font=self.font,
                    )
        elif obj.obj_type in ("Action Usage", "Action", "CallBehaviorAction", "Part", "Port"):
            dash = ()
            if obj.obj_type == "Part":
                dash = (4, 2)
            if obj.obj_type == "Port":
                side = obj.properties.get("side", "E")
                sz = 6 * self.zoom
                self._draw_gradient_rect(x - sz, y - sz, x + sz, y + sz, color, obj.obj_id)
                self.canvas.create_rectangle(
                    x - sz,
                    y - sz,
                    x + sz,
                    y + sz,
                    fill="",
                    outline=outline,
                )
                arrow_len = sz * 1.2
                half = arrow_len / 2
                direction = obj.properties.get("direction", "out")

                if side in ("E", "W"):
                    if side == "E":
                        inside = -half
                        outside = half
                    else:
                        inside = half
                        outside = -half
                    if direction == "in":
                        self.canvas.create_line(x + outside, y, x + inside, y)
                        self._draw_line_arrow(
                            (x + outside, y),
                            (x + inside, y),
                            color=outline,
                            tags="connection",
                        )
                    elif direction == "out":
                        self.canvas.create_line(x + inside, y, x + outside, y)
                        self._draw_line_arrow(
                            (x + inside, y),
                            (x + outside, y),
                            color=outline,
                            tags="connection",
                        )
                    else:
                        self.canvas.create_line(x - half, y, x + half, y)
                        self._draw_line_arrow(
                            (x, y),
                            (x + half, y),
                            color=outline,
                            tags="connection",
                        )
                        self._draw_line_arrow(
                            (x, y),
                            (x - half, y),
                            color=outline,
                            tags="connection",
                        )
                else:  # N or S
                    if side == "S":
                        inside = -half
                        outside = half
                    else:
                        inside = half
                        outside = -half
                    if direction == "in":
                        self.canvas.create_line(x, y + outside, x, y + inside)
                        self._draw_line_arrow(
                            (x, y + outside),
                            (x, y + inside),
                            color=outline,
                            tags="connection",
                        )
                    elif direction == "out":
                        self.canvas.create_line(x, y + inside, x, y + outside)
                        self._draw_line_arrow(
                            (x, y + inside),
                            (x, y + outside),
                            color=outline,
                            tags="connection",
                        )
                    else:
                        self.canvas.create_line(x, y - half, x, y + half)
                        self._draw_line_arrow(
                            (x, y),
                            (x, y + half),
                            color=outline,
                            tags="connection",
                        )
                        self._draw_line_arrow(
                            (x, y),
                            (x, y - half),
                            color=outline,
                            tags="connection",
                        )

                lx_off = _parse_float(obj.properties.get("labelX"), 8.0)
                ly_off = _parse_float(obj.properties.get("labelY"), -8.0)
                lx = x + lx_off * self.zoom
                ly = y + ly_off * self.zoom
                self.canvas.create_text(
                    lx,
                    ly,
                    text=obj.properties.get("name", ""),
                    anchor="center",
                    font=self.font,
                )
            else:
                if obj.obj_type in ("Action Usage", "Action", "CallBehaviorAction"):
                    self._draw_gradient_rect(x - w, y - h, x + w, y + h, color, obj.obj_id)
                    self._create_round_rect(
                        x - w,
                        y - h,
                        x + w,
                        y + h,
                        radius=8 * self.zoom,
                        dash=dash,
                        fill="",
                        outline=outline,
                    )
                else:
                    self._draw_gradient_rect(x - w, y - h, x + w, y + h, color, obj.obj_id)
                    self.canvas.create_rectangle(
                        x - w,
                        y - h,
                        x + w,
                        y + h,
                        dash=dash,
                        fill="",
                        outline=outline,
                    )
        elif obj.obj_type == "Block":
            left, top = x - w, y - h
            right, bottom = x + w, y + h
            self._draw_gradient_rect(left, top, right, bottom, color, obj.obj_id)
            self._create_round_rect(
                left,
                top,
                right,
                bottom,
                radius=6 * self.zoom,
                fill="",
                outline=outline,
            )
            header = f"<<block>> {obj.properties.get('name', '')}".strip()
            self.canvas.create_line(left, top + 20 * self.zoom, right, top + 20 * self.zoom)
            self.canvas.create_text(
                left + 4 * self.zoom,
                top + 10 * self.zoom,
                text=header,
                anchor="w",
                font=self.font,
            )
            compartments = self._block_compartments(obj)
            cy = top + 20 * self.zoom
            for label, text in compartments:
                lines = text.splitlines() if text else [""]
                collapsed = obj.collapsed.get(label, False)
                self.canvas.create_line(left, cy, right, cy)
                btn_sz = 8 * self.zoom
                bx1 = left + 2 * self.zoom
                by1 = cy + (20 * self.zoom - btn_sz) / 2
                bx2 = bx1 + btn_sz
                by2 = by1 + btn_sz
                self.canvas.create_rectangle(bx1, by1, bx2, by2, outline="black", fill="white")
                self.canvas.create_text((bx1 + bx2) / 2, (by1 + by2) / 2, text="-" if not collapsed else "+", font=self.font)
                self.compartment_buttons.append((obj.obj_id, label, (bx1, by1, bx2, by2)))
                tx = bx2 + 2 * self.zoom
                if collapsed:
                    # Only display the compartment title when collapsed rather
                    # than showing the first item's text. This keeps the
                    # collapsed view concise and avoids confusion when the
                    # compartment contains multiple elements.
                    self.canvas.create_text(
                        tx,
                        cy + 10 * self.zoom,
                        text=f"{label}:",
                        anchor="w",
                        font=self.font,
                    )
                    cy += 20 * self.zoom
                else:
                    self.canvas.create_text(
                        tx,
                        cy + 10 * self.zoom,
                        text=f"{label}:",
                        anchor="w",
                        font=self.font,
                    )
                    cy += 20 * self.zoom
                    for line in lines:
                        self.canvas.create_text(
                            left + 4 * self.zoom,
                            cy + 10 * self.zoom,
                            text=line,
                            anchor="w",
                            font=self.font,
                        )
                        cy += 20 * self.zoom
        elif obj.obj_type in ("Initial", "Final"):
            if obj.obj_type == "Initial":
                r = min(obj.width, obj.height) / 2 * self.zoom
                self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="black")
            else:
                r = min(obj.width, obj.height) / 2 * self.zoom
                inner = max(r - 5 * self.zoom, 0)
                self.canvas.create_oval(x - r, y - r, x + r, y + r)
                self.canvas.create_oval(x - inner, y - inner, x + inner, y + inner, fill="black")
        elif obj.obj_type in ("Decision", "Merge"):
            self.canvas.create_polygon(
                x,
                y - h,
                x + w,
                y,
                x,
                y + h,
                x - w,
                y,
                fill=color,
                outline=outline,
            )
        elif obj.obj_type in ("Fork", "Join"):
            half = obj.width / 2 * self.zoom
            self.canvas.create_rectangle(
                x - half, y - 5 * self.zoom, x + half, y + 5 * self.zoom, fill="black"
            )
        else:
            self._create_round_rect(
                x - w,
                y - h,
                x + w,
                y + h,
                radius=6 * self.zoom,
                fill=color,
                outline=outline,
            )

        if obj.obj_type not in (
            "Block",
            "System Boundary",
            "Block Boundary",
            "Port",
            "Work Product",
        ):
            name = obj.properties.get("name", obj.obj_type)
            label = name
            if obj.obj_type == "Part":
                def_id = obj.properties.get("definition")
                if def_id and def_id in self.repo.elements:
                    def_name = self.repo.elements[def_id].name or def_id
                    label = f"{name} : {def_name}" if name else def_name
            diag_id = self.repo.get_linked_diagram(obj.element_id)
            label_lines = []
            if diag_id and diag_id in self.repo.diagrams:
                diag = self.repo.diagrams[diag_id]
                diag_name = diag.name or diag_id
                label_lines.append(diag_name)
            label_lines.append(label)
            key = obj.obj_type.replace(" ", "")
            if not key.endswith("Usage"):
                key += "Usage"
            for prop in SYSML_PROPERTIES.get(key, []):
                if obj.obj_type == "Part" and prop in (
                    "fit",
                    "qualification",
                    "failureModes",
                    "asil",
                ):
                    continue
                val = obj.properties.get(prop)
                if val:
                    label_lines.append(f"{prop}: {val}")
            if obj.obj_type == "Part":
                rel_items = []
                for lbl, key in (
                    ("ASIL", "asil"),
                    ("FIT", "fit"),
                    ("Qual", "qualification"),
                    ("FM", "failureModes"),
                ):
                    val = obj.properties.get(key)
                    if val:
                        rel_items.append(f"{lbl}: {val}")
                if rel_items:
                    label_lines.extend(rel_items)
                reqs = "; ".join(r.get("id") for r in obj.requirements)
                if reqs:
                    label_lines.append(f"Reqs: {reqs}")
            if obj.obj_type == "Actor":
                sy = obj.height / 40.0 * self.zoom
                label_x = x
                label_y = y + 40 * sy + 10 * self.zoom
                self.canvas.create_text(
                    label_x,
                    label_y,
                    text="\n".join(label_lines),
                    anchor="n",
                    font=self.font,
                )
            elif obj.obj_type in ("Initial", "Final"):
                label_y = y + obj.height / 2 * self.zoom + 10 * self.zoom
                self.canvas.create_text(
                    x,
                    label_y,
                    text="\n".join(label_lines),
                    anchor="n",
                    font=self.font,
                )
            else:
                self.canvas.create_text(
                    x,
                    y,
                    text="\n".join(label_lines),
                    anchor="center",
                    font=self.font,
                )

        show_marker = False
        if obj.obj_type in ("Block", "Action Usage", "Action", "CallBehaviorAction"):
            diag_id = self.repo.get_linked_diagram(obj.element_id)
            view_id = obj.properties.get("view")
            show_marker = bool(
                (diag_id and diag_id in self.repo.diagrams)
                or (view_id and view_id in self.repo.diagrams)
            )
        if show_marker:
            self._draw_subdiagram_marker(x + w, y + h)

        if obj in self.selected_objs:
            bx = x - w
            by = y - h
            ex = x + w
            ey = y + h
            self.canvas.create_rectangle(bx, by, ex, ey, outline="red", dash=(2, 2))
            if obj == self.selected_obj and obj.obj_type != "Actor":
                s = 4
                for hx, hy in [(bx, by), (bx, ey), (ex, by), (ex, ey)]:
                    self.canvas.create_rectangle(
                        hx - s,
                        hy - s,
                        hx + s,
                        hy + s,
                        outline="red",
                        fill="white",
                    )

    def draw_connection(
        self, a: SysMLObject, b: SysMLObject, conn: DiagramConnection, selected: bool = False
    ):
        axc, ayc = a.x * self.zoom, a.y * self.zoom
        bxc, byc = b.x * self.zoom, b.y * self.zoom
        dash = ()
        diag = self.repo.diagrams.get(self.diagram_id)
        label = format_control_flow_label(
            conn, self.repo, diag.diag_type if diag else None
        )
        if diag and diag.diag_type == "Control Flow Diagram" and conn.conn_type in ("Control Action", "Feedback"):
            a_left = a.x - a.width / 2
            a_right = a.x + a.width / 2
            b_left = b.x - b.width / 2
            b_right = b.x + b.width / 2
            x_val = (
                conn.points[0][0]
                if conn.points
                else (max(a_left, b_left) + min(a_right, b_right)) / 2
            )
            x_val = SysMLDiagramWindow._constrain_control_flow_x(
                self, conn, x_val
            )
            if conn.points:
                conn.points[0] = (x_val, 0)
            x = x_val * self.zoom
            if ayc <= byc:
                y1 = ayc + a.height / 2 * self.zoom
                y2 = byc - b.height / 2 * self.zoom
            else:
                y1 = ayc - a.height / 2 * self.zoom
                y2 = byc + b.height / 2 * self.zoom
            color = "red" if selected else "black"
            width = 2 if selected else 1
            self.canvas.create_line(
                x,
                y1,
                x,
                y2,
                arrow=tk.LAST,
                dash=(),
                fill=color,
                width=width,
                tags="connection",
            )
            if label:
                self.canvas.create_text(
                    x,
                    (y1 + y2) / 2 - 10 * self.zoom,
                    text=label,
                    font=self.font,
                    tags="connection",
                )
            if selected:
                s = 3
                for hx, hy in [(x, y1), (x, y2), (x, (y1 + y2) / 2)]:
                    self.canvas.create_rectangle(
                        hx - s,
                        hy - s,
                        hx + s,
                        hy + s,
                        outline="red",
                        fill="white",
                        tags="connection",
                    )
            return
        if a.obj_id == b.obj_id:
            ax, ay = self.edge_point(a, 0, 0, (1, 0))
            bx, by = ax, ay
        else:
            ax, ay = self.edge_point(a, bxc, byc, conn.src_pos)
            bx, by = self.edge_point(b, axc, ayc, conn.dst_pos)
        if conn.conn_type in ("Include", "Extend"):
            dash = (4, 2)
            if label and ">> " in label:
                label = label.replace(">> ", ">>\n", 1)
        elif conn.conn_type in ("Generalize", "Generalization", "Communication Path"):
            dash = (2, 2)
        src_flow = a.properties.get("flow") if a.obj_type == "Port" else None
        dst_flow = b.properties.get("flow") if b.obj_type == "Port" else None
        points = [(ax, ay)]
        if a.obj_id == b.obj_id:
            size = max(a.width, a.height) * 0.5 * self.zoom
            points.extend(
                [
                    (ax + size, ay),
                    (ax + size, ay - size),
                    (ax, ay - size),
                ]
            )
        elif conn.style == "Squared":
            if conn.points:
                mx = conn.points[0][0] * self.zoom
            else:
                mx = (ax + bx) / 2
            points.extend([(mx, ay), (mx, by)])
        elif conn.style == "Custom":
            for px, py in conn.points:
                x = px * self.zoom
                y = py * self.zoom
                last = points[-1]
                points.extend([(x, last[1]), (x, y)])
        points.append((bx, by))
        flat = [coord for pt in points for coord in pt]
        color = "red" if selected else "black"
        width = 2 if selected else 1
        arrow_style = tk.NONE
        open_arrow = conn.conn_type in ("Include", "Extend")
        diamond_src = conn.conn_type in ("Aggregation", "Composite Aggregation")
        filled_diamond = conn.conn_type == "Composite Aggregation"
        forward = conn.arrow in ("forward", "both")
        backward = conn.arrow in ("backward", "both")
        mid_forward = forward
        mid_backward = backward
        if conn.conn_type == "Connector" and (src_flow or dst_flow):
            arrow_style = tk.NONE
            conn.mid_arrow = True
            if src_flow and dst_flow:
                dir_a = a.properties.get("direction", "out").lower()
                dir_b = b.properties.get("direction", "out").lower()
                if dir_a == "out":
                    label = src_flow
                    mid_forward, mid_backward = True, False
                elif dir_b == "out":
                    label = dst_flow
                    mid_forward, mid_backward = False, True
                else:
                    label = src_flow
                    mid_forward, mid_backward = True, True
            elif src_flow:
                label = src_flow
                dir_attr = a.properties.get("direction", "out")
                if dir_attr == "in":
                    mid_forward, mid_backward = False, True
                elif dir_attr == "out":
                    mid_forward, mid_backward = True, False
                else:
                    mid_forward, mid_backward = True, True
            else:
                label = dst_flow
                dir_attr = b.properties.get("direction", "out")
                if dir_attr == "in":
                    mid_forward, mid_backward = True, False
                elif dir_attr == "out":
                    mid_forward, mid_backward = False, True
                else:
                    mid_forward, mid_backward = True, True
            label = f"<<{conn.stereotype or conn.conn_type.lower()}>> {label}".strip()
        self.canvas.create_line(
            *flat,
            arrow=arrow_style,
            dash=dash,
            fill=color,
            width=width,
            tags="connection",
        )
        if open_arrow:
            if forward:
                self._draw_open_arrow(
                    points[-2], points[-1], color=color, width=width, tags="connection"
                )
            if backward:
                self._draw_open_arrow(
                    points[1], points[0], color=color, width=width, tags="connection"
                )
        elif conn.conn_type in ("Generalize", "Generalization"):
            # SysML uses an open triangular arrow head for generalization
            # relationships. Use the open arrow drawing helper so the arrow
            # interior matches the canvas background (typically white).
            if forward:
                self._draw_open_arrow(
                    points[-2], points[-1], color=color, width=width, tags="connection"
                )
            if backward:
                self._draw_filled_arrow(
                    points[1], points[0], color=color, width=width, tags="connection"
                )
        elif diamond_src:
            if filled_diamond:
                self._draw_filled_diamond(
                    points[1], points[0], color=color, width=width, tags="connection"
                )
            else:
                self._draw_open_diamond(
                    points[1], points[0], color=color, width=width, tags="connection"
                )
        else:
            if forward:
                self._draw_filled_arrow(
                    points[-2], points[-1], color=color, width=width, tags="connection"
                )
            if backward:
                self._draw_filled_arrow(
                    points[1], points[0], color=color, width=width, tags="connection"
                )
        flow_port = None
        flow_name = ""
        if a.obj_type == "Port" and a.properties.get("flow"):
            flow_port = a
            flow_name = a.properties.get("flow", "")
        elif b.obj_type == "Port" and b.properties.get("flow"):
            flow_port = b
            flow_name = b.properties.get("flow", "")

        if conn.mid_arrow or flow_port:
            mid_idx = len(points) // 2
            if mid_idx > 0:
                mstart = points[mid_idx - 1]
                mend = points[mid_idx]
                if flow_port:
                    direction = flow_port.properties.get("direction", "")
                    if flow_port is b:
                        direction = "in" if direction == "out" else "out" if direction == "in" else direction
                    if direction == "inout":
                        self._draw_center_triangle(
                            mstart, mend, color=color, width=width, tags="connection"
                        )
                        self._draw_center_triangle(
                            mend, mstart, color=color, width=width, tags="connection"
                        )
                    elif direction == "in":
                        self._draw_center_triangle(
                            mend, mstart, color=color, width=width, tags="connection"
                        )
                    else:
                        self._draw_center_triangle(
                            mstart, mend, color=color, width=width, tags="connection"
                        )
                    mx = (mstart[0] + mend[0]) / 2
                    my = (mstart[1] + mend[1]) / 2
                    self.canvas.create_text(
                        mx,
                        my - 10 * self.zoom,
                        text=flow_name,
                        font=self.font,
                        tags="connection",
                    )
                else:
                    if mid_forward or not mid_backward:
                        self._draw_center_triangle(
                            mstart, mend, color=color, width=width, tags="connection"
                        )
                    if mid_backward:
                        self._draw_center_triangle(
                            mend, mstart, color=color, width=width, tags="connection"
                        )
        if selected:
            if conn.style == "Custom":
                for px, py in conn.points:
                    hx = px * self.zoom
                    hy = py * self.zoom
                    s = 3
                    self.canvas.create_rectangle(
                    hx - s,
                    hy - s,
                    hx + s,
                    hy + s,
                    outline="red",
                    fill="white",
                    tags="connection",
                )
            elif conn.style == "Squared":
                if conn.points:
                    mx = conn.points[0][0] * self.zoom
                else:
                    mx = (ax + bx) / 2
                hy = (ay + by) / 2
                s = 3
                self.canvas.create_rectangle(
                    mx - s,
                    hy - s,
                    mx + s,
                    hy + s,
                    outline="red",
                    fill="white",
                    tags="connection",
                )
            # draw endpoint handles
            for hx, hy in [(ax, ay), (bx, by)]:
                s = 3
                self.canvas.create_rectangle(
                    hx - s,
                    hy - s,
                    hx + s,
                    hy + s,
                    outline="red",
                    fill="white",
                    tags="connection",
                )
        if conn.multiplicity and conn.conn_type in ("Aggregation", "Composite Aggregation"):
            end_x, end_y = points[-1]
            prev_x, prev_y = points[-2]
            dx = prev_x - end_x
            dy = prev_y - end_y
            length = math.hypot(dx, dy)
            if length:
                offset = 15 * self.zoom
                mx = end_x + dx / length * offset
                my = end_y + dy / length * offset
            else:
                mx, my = end_x, end_y
            self.canvas.create_text(
                mx,
                my - 10 * self.zoom,
                text=conn.multiplicity,
                font=self.font,
                tags="connection",
            )
        if label:
            mx, my = (ax + bx) / 2, (ay + by) / 2
            self.canvas.create_text(
                mx,
                my - 10 * self.zoom,
                text=label,
                font=self.font,
                tags="connection",
            )

    def get_object(self, oid: int) -> SysMLObject | None:
        for o in self.objects:
            if o.obj_id == oid:
                return o
        return None

    def get_ibd_boundary(self) -> SysMLObject | None:
        """Return the Block Boundary object if present."""
        for o in self.objects:
            if o.obj_type == "Block Boundary":
                return o
        return None

    def _object_within(self, obj: SysMLObject, boundary: SysMLObject) -> bool:
        left = boundary.x - boundary.width / 2
        right = boundary.x + boundary.width / 2
        top = boundary.y - boundary.height / 2
        bottom = boundary.y + boundary.height / 2
        ox = obj.x
        oy = obj.y
        return left <= ox <= right and top <= oy <= bottom

    def find_boundary_for_obj(self, obj: SysMLObject) -> SysMLObject | None:
        for b in self.objects:
            if b.obj_type == "System Boundary" and self._object_within(obj, b):
                return b
        return None

    def _update_drag_selection(self, x: float, y: float) -> None:
        if not self.select_rect_start:
            return
        x0, y0 = self.select_rect_start
        left, right = sorted([x0, x])
        top, bottom = sorted([y0, y])
        selected: list[SysMLObject] = []
        for obj in self.objects:
            ox = obj.x * self.zoom
            oy = obj.y * self.zoom
            w = obj.width * self.zoom / 2
            h = obj.height * self.zoom / 2
            if left <= ox - w and ox + w <= right and top <= oy - h and oy + h <= bottom:
                selected.append(obj)
        self.selected_objs = selected
        self.selected_obj = selected[0] if len(selected) == 1 else None
        self.redraw()
        self.update_property_view()

    # ------------------------------------------------------------
    # Clipboard operations
    # ------------------------------------------------------------
    def copy_selected(self, _event=None):
        if self.selected_obj:
            import copy

            self.clipboard = copy.deepcopy(self.selected_obj)

    def cut_selected(self, _event=None):
        if self.selected_obj:
            import copy

            self.clipboard = copy.deepcopy(self.selected_obj)
            self.remove_object(self.selected_obj)
            self.selected_obj = None
            self._sync_to_repository()
            self.redraw()
            self.update_property_view()

    def paste_selected(self, _event=None):
        if self.clipboard:
            import copy

            new_obj = copy.deepcopy(self.clipboard)
            new_obj.obj_id = _get_next_id()
            new_obj.x += 20
            new_obj.y += 20
            if new_obj.obj_type == "System Boundary":
                self.objects.insert(0, new_obj)
            else:
                self.objects.append(new_obj)
            self.sort_objects()
            diag = self.repo.diagrams.get(self.diagram_id)
            if diag and new_obj.element_id and new_obj.element_id not in diag.elements:
                diag.elements.append(new_obj.element_id)
            self.selected_obj = new_obj
            self._sync_to_repository()
            self.redraw()
            self.update_property_view()

    def delete_selected(self, _event=None):
        if self.selected_objs:
            result = messagebox.askyesnocancel(
                "Delete",
                "Remove element from model?\nYes = Model, No = Diagram",
            )
            if result is None:
                return
            for obj in list(self.selected_objs):
                if result:
                    if obj.obj_type == "Part":
                        self.remove_part_model(obj)
                    else:
                        self.remove_element_model(obj)
                else:
                    if obj.obj_type == "Work Product":
                        name = obj.properties.get("name", "")
                        if getattr(self.app, "can_remove_work_product", None):
                            if not self.app.can_remove_work_product(name):
                                messagebox.showerror(
                                    "Delete",
                                    f"Cannot delete work product '{name}' with existing artifacts.",
                                )
                                continue
                            getattr(self.app, "disable_work_product", lambda *_: None)(name)
                    self.remove_object(obj)
            self.selected_objs = []
            self.selected_obj = None
            return
        if self.selected_conn:
            if self.selected_conn in self.connections:
                src_elem = self.get_object(self.selected_conn.src)
                dst_elem = self.get_object(self.selected_conn.dst)
                if (
                    self.selected_conn.conn_type == "Generalization"
                    and src_elem
                    and dst_elem
                ):
                    msg = (
                        "Removing this inheritance will delete all inherited parts, "
                        "properties and attributes. Continue?"
                    )
                    if not messagebox.askyesno("Remove Inheritance", msg):
                        return
                elif self.selected_conn.conn_type in (
                    "Aggregation",
                    "Composite Aggregation",
                ):
                    msg = "Delete aggregation and its part?"
                    if not messagebox.askyesno("Remove Aggregation", msg):
                        return
                self.connections.remove(self.selected_conn)
                # remove matching repository relationship
                if src_elem and dst_elem and src_elem.element_id and dst_elem.element_id:
                    for rel in list(self.repo.relationships):
                        if (
                            rel.source == src_elem.element_id
                            and rel.target == dst_elem.element_id
                            and rel.rel_type == self.selected_conn.conn_type
                        ):
                            self.repo.relationships.remove(rel)
                            diag = self.repo.diagrams.get(self.diagram_id)
                            if diag and rel.rel_id in diag.relationships:
                                diag.relationships.remove(rel.rel_id)
                            if self.selected_conn.conn_type == "Generalization":
                                remove_inherited_block_properties(
                                    self.repo, src_elem.element_id, dst_elem.element_id
                                )
                                inherit_block_properties(self.repo, src_elem.element_id)
                            elif self.selected_conn.conn_type in ("Aggregation", "Composite Aggregation"):
                                remove_aggregation_part(
                                    self.repo,
                                    src_elem.element_id,
                                    dst_elem.element_id,
                                    remove_object=self.selected_conn.conn_type == "Composite Aggregation",
                                    app=getattr(self, "app", None),
                                )
                            break
                self.selected_conn = None
                self._sync_to_repository()
                self.redraw()
                self.update_property_view()

    def remove_object(self, obj: SysMLObject) -> None:
        if getattr(obj, "locked", False):
            return
        removed_ids = {obj.obj_id}
        if obj in self.objects:
            self.objects.remove(obj)
        if obj.obj_type == "Part":
            before = {o.obj_id for o in self.objects}
            remove_orphan_ports(self.objects)
            removed_ids.update(before - {o.obj_id for o in self.objects})
        elif obj.obj_type == "Port":
            remove_port(self.repo, obj, self.objects)
        self.connections = [
            c for c in self.connections if c.src not in removed_ids and c.dst not in removed_ids
        ]
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag and obj.element_id in diag.elements:
            diag.elements.remove(obj.element_id)

        prev_parts = None
        block_id = None
        if obj.obj_type == "Part" and diag:
            block_id = getattr(diag, "father", None) or next(
                (eid for eid, did in self.repo.element_diagrams.items() if did == self.diagram_id),
                None,
            )
            if block_id and block_id in self.repo.elements:
                block = self.repo.elements[block_id]
                prev_parts = block.properties.get("partProperties")

        self._sync_to_repository()

        if prev_parts is not None and block_id and block_id in self.repo.elements:
            block = self.repo.elements[block_id]
            if prev_parts:
                block.properties["partProperties"] = prev_parts
            else:
                block.properties.pop("partProperties", None)
            for d in self.repo.diagrams.values():
                for o in getattr(d, "objects", []):
                    if o.get("element_id") == block_id:
                        if prev_parts:
                            o.setdefault("properties", {})["partProperties"] = prev_parts
                        else:
                            o.setdefault("properties", {}).pop("partProperties", None)

    # ------------------------------------------------------------
    # Part removal helpers
    # ------------------------------------------------------------
    def remove_part_diagram(self, obj: SysMLObject) -> None:
        """Remove *obj* from the current diagram but keep it in the model."""
        if obj.obj_type != "Part":
            return
        obj.hidden = True
        self.selected_obj = None
        self._sync_to_repository()
        self.redraw()
        self.update_property_view()

    def remove_part_model(self, obj: SysMLObject) -> None:
        """Remove *obj* from the repository and all diagrams."""
        if obj.obj_type != "Part":
            return
        self.remove_object(obj)
        part_id = obj.element_id
        repo = self.repo
        # remove from other diagrams
        for diag in repo.diagrams.values():
            diag.objects = [o for o in getattr(diag, "objects", []) if o.get("element_id") != part_id]
            if part_id in getattr(diag, "elements", []):
                diag.elements.remove(part_id)
        # update any open windows
        app = getattr(self, "app", None)
        if app:
            for win in getattr(app, "ibd_windows", []):
                win.objects = [o for o in win.objects if o.element_id != part_id]
                remove_orphan_ports(win.objects)
                win.redraw()
                win._sync_to_repository()
        # update block properties
        diag = repo.diagrams.get(self.diagram_id)
        block_id = getattr(diag, "father", None) or next((eid for eid, did in repo.element_diagrams.items() if did == self.diagram_id), None)
        name = ""
        elem = repo.elements.get(part_id)
        if elem:
            name = elem.name or elem.properties.get("component", "")
            def_id = elem.properties.get("definition")
            if not name and def_id and def_id in repo.elements:
                name = repo.elements[def_id].name or def_id
        if block_id and name and block_id in repo.elements:
            block = repo.elements[block_id]
            parts = [p.strip() for p in block.properties.get("partProperties", "").split(",") if p.strip()]
            parts = [p for p in parts if p.split("[")[0].strip() != name]
            if parts:
                block.properties["partProperties"] = ", ".join(parts)
            else:
                block.properties.pop("partProperties", None)
            for d in repo.diagrams.values():
                for o in getattr(d, "objects", []):
                    if o.get("element_id") == block_id:
                        if parts:
                            o.setdefault("properties", {})["partProperties"] = ", ".join(parts)
                        else:
                            o.setdefault("properties", {}).pop("partProperties", None)
        repo.delete_element(part_id)
        repo._undo_stack.pop()
        self._sync_to_repository()
        self.redraw()
        self.update_property_view()

    def remove_element_model(self, obj: SysMLObject) -> None:
        """Remove *obj* and its element from all diagrams and the repository."""
        elem_id = obj.element_id
        if not elem_id:
            self.remove_object(obj)
            return
        self.remove_object(obj)
        repo = self.repo
        for diag in repo.diagrams.values():
            removed_ids = [o.get("obj_id") for o in getattr(diag, "objects", []) if o.get("element_id") == elem_id]
            if removed_ids:
                diag.objects = [o for o in diag.objects if o.get("element_id") != elem_id]
                diag.connections = [
                    c
                    for c in getattr(diag, "connections", [])
                    if c.get("src") not in removed_ids and c.get("dst") not in removed_ids
                ]
            if elem_id in getattr(diag, "elements", []):
                diag.elements.remove(elem_id)
        # remove part elements that reference this element
        to_delete = [
            eid
            for eid, e in repo.elements.items()
            if e.elem_type == "Part" and e.properties.get("definition") == elem_id
        ]
        for pid in to_delete:
            for diag in repo.diagrams.values():
                removed = [o.get("obj_id") for o in getattr(diag, "objects", []) if o.get("element_id") == pid]
                if removed:
                    diag.objects = [o for o in diag.objects if o.get("element_id") != pid]
                    diag.connections = [
                        c
                        for c in getattr(diag, "connections", [])
                        if c.get("src") not in removed and c.get("dst") not in removed
                    ]
                if pid in getattr(diag, "elements", []):
                    diag.elements.remove(pid)
            repo.delete_element(pid)
            if repo._undo_stack:
                repo._undo_stack.pop()

        repo.delete_element(elem_id)
        if repo._undo_stack:
            repo._undo_stack.pop()

        self._sync_to_repository()
        self.redraw()
        self.update_property_view()

    def _sync_to_repository(self) -> None:
        """Persist current objects and connections back to the repository."""
        self.repo.push_undo_state()
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag:
            existing_objs = getattr(diag, "objects", [])
            hidden_objs = [
                o for o in existing_objs if not self.repo.object_visible(o, self.diagram_id)
            ]
            diag.objects = hidden_objs + [obj.__dict__ for obj in self.objects]
            existing_conns = getattr(diag, "connections", [])
            hidden_conns = [
                c
                for c in existing_conns
                if not self.repo.connection_visible(c, self.diagram_id)
            ]
            diag.connections = hidden_conns + [conn.__dict__ for conn in self.connections]
            update_block_parts_from_ibd(self.repo, diag)
            self.repo.touch_diagram(self.diagram_id)
            _sync_block_parts_from_ibd(self.repo, self.diagram_id)
            if diag.diag_type == "Internal Block Diagram":
                block_id = (
                    getattr(diag, "father", None)
                    or next(
                        (
                            eid
                            for eid, did in self.repo.element_diagrams.items()
                            if did == self.diagram_id
                        ),
                        None,
                    )
                )
                if block_id:
                    added_mult = _enforce_ibd_multiplicity(
                        self.repo, block_id, app=getattr(self, "app", None)
                    )
                    if added_mult and not getattr(self, "app", None):
                        for data in added_mult:
                            if not any(
                                o.obj_id == data["obj_id"] for o in self.objects
                            ):
                                self.objects.append(SysMLObject(**data))

    def refresh_from_repository(self, _event=None) -> None:
        """Reload diagram objects from the repository and redraw."""
        diag = self.repo.diagrams.get(self.diagram_id)
        if not diag:
            return
        self.objects = []
        for data in self.repo.visible_objects(diag.diag_id):
            if "requirements" not in data:
                data["requirements"] = []
            obj = SysMLObject(**data)
            if obj.obj_type == "Part":
                asil = calculate_allocated_asil(obj.requirements)
                obj.properties.setdefault("asil", asil)
                if obj.element_id and obj.element_id in self.repo.elements:
                    self.repo.elements[obj.element_id].properties.setdefault(
                        "asil", asil
                    )
            self.objects.append(obj)
        self.sort_objects()
        self.connections = []
        for data in self.repo.visible_connections(diag.diag_id):
            data.setdefault("stereotype", data.get("conn_type", "").lower())
            self.connections.append(DiagramConnection(**data))
        if self.objects:
            global _next_obj_id
            _next_obj_id = max(o.obj_id for o in self.objects) + 1
        self.redraw()
        self.update_property_view()

    def on_close(self):
        self._sync_to_repository()
        self.destroy()


class SysMLObjectDialog(simpledialog.Dialog):
    """Simple dialog for editing AutoML object properties."""

    def __init__(self, master, obj: SysMLObject):
        if not hasattr(obj, "requirements"):
            obj.requirements = []
        self.obj = obj
        super().__init__(master, title=f"Edit {obj.obj_type}")

    class SelectRequirementsDialog(simpledialog.Dialog):
        def __init__(self, parent, title="Select Requirements"):
            self.selected_vars = {}
            super().__init__(parent, title=title)

        def body(self, master):
            ttk.Label(master, text="Select requirements:").pack(padx=5, pady=5)
            container = ttk.Frame(master)
            container.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(container, borderwidth=0)
            scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
            self.check_frame = ttk.Frame(canvas)
            self.check_frame.bind(
                "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=self.check_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            for req_id, req in global_requirements.items():
                var = tk.BooleanVar(value=False)
                self.selected_vars[req_id] = var
                text = f"[{req['id']}] {req['text']}"
                ttk.Checkbutton(self.check_frame, text=text, variable=var).pack(
                    anchor="w", padx=2, pady=2
                )
            return self.check_frame

        def apply(self):
            self.result = [rid for rid, var in self.selected_vars.items() if var.get()]

    class SelectComponentsDialog(simpledialog.Dialog):
        """Dialog to choose which components should become parts."""

        def __init__(self, parent, components):
            self.components = components
            self.selected = {}
            super().__init__(parent, title="Select Components")

        def body(self, master):
            ttk.Label(master, text="Select components:").pack(padx=5, pady=5)
            frame = ttk.Frame(master)
            frame.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(frame, borderwidth=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            self.check_frame = ttk.Frame(canvas)
            self.check_frame.bind(
                "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=self.check_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            for comp in self.components:
                var = tk.BooleanVar(value=True)
                self.selected[comp] = var
                ttk.Checkbutton(self.check_frame, text=comp.name, variable=var).pack(
                    anchor="w", padx=2, pady=2
                )
            return self.check_frame

        def apply(self):
            self.result = [c for c, var in self.selected.items() if var.get()]

    class SelectNamesDialog(simpledialog.Dialog):
        """Dialog to choose which part names should be added."""

        def __init__(self, parent, names, title="Select Parts"):
            self.names = names
            self.selected = {}
            super().__init__(parent, title=title)

        def body(self, master):
            ttk.Label(master, text="Select parts:").pack(padx=5, pady=5)
            frame = ttk.Frame(master)
            frame.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(frame, borderwidth=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            self.check_frame = ttk.Frame(canvas)
            self.check_frame.bind(
                "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=self.check_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            for name in self.names:
                var = tk.BooleanVar(value=True)
                self.selected[name] = var
                ttk.Checkbutton(self.check_frame, text=name, variable=var).pack(
                    anchor="w", padx=2, pady=2
                )
            return self.check_frame

        def apply(self):
            self.result = [n for n, var in self.selected.items() if var.get()]

    class SelectElementDialog(simpledialog.Dialog):
        """Dialog to choose a single existing element."""

        def __init__(self, parent, names, title="Select Element"):
            self.names = names
            self.result = None
            super().__init__(parent, title=title)

        def body(self, master):
            ttk.Label(master, text="Select element:").pack(padx=5, pady=5)
            self.listbox = tk.Listbox(master)
            for name in self.names:
                self.listbox.insert(tk.END, name)
            self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            return self.listbox

        def apply(self):
            sel = self.listbox.curselection()
            if sel:
                self.result = self.names[sel[0]]

    class ManagePartsDialog(simpledialog.Dialog):
        """Dialog to toggle visibility of contained parts."""

        def __init__(self, parent, names, visible, hidden):
            self.names = names
            self.visible = visible
            self.hidden = hidden
            self.selected = {}
            super().__init__(parent, title="Add Contained Parts")

        def body(self, master):
            ttk.Label(master, text="Select parts to show:").pack(padx=5, pady=5)
            frame = ttk.Frame(master)
            frame.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(frame, borderwidth=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            self.check_frame = ttk.Frame(canvas)
            self.check_frame.bind(
                "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            canvas.create_window((0, 0), window=self.check_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            for name in self.names:
                var = tk.BooleanVar(value=name in self.visible)
                self.selected[name] = var
                ttk.Checkbutton(self.check_frame, text=name, variable=var).pack(
                    anchor="w", padx=2, pady=2
                )
            return self.check_frame

        def apply(self):
            self.result = [n for n, var in self.selected.items() if var.get()]

    def body(self, master):
        # Disable window resizing so the layout remains consistent
        self.resizable(False, False)

        # Use a notebook to keep the dialog compact by grouping fields
        self.nb = ttk.Notebook(master)
        self.nb.grid(row=0, column=0, columnspan=3, sticky="nsew")

        gen_frame = ttk.Frame(self.nb)
        prop_frame = ttk.Frame(self.nb)
        rel_frame = ttk.Frame(self.nb)
        link_frame = ttk.Frame(self.nb)
        req_frame = ttk.Frame(self.nb)

        self.nb.add(gen_frame, text="General")
        self.nb.add(prop_frame, text="Properties")
        self.nb.add(rel_frame, text="Reliability")
        self.nb.add(link_frame, text="Links")
        self.nb.add(req_frame, text="Requirements")

        gen_row = 0
        ttk.Label(gen_frame, text="Name:").grid(row=gen_row, column=0, sticky="e", padx=4, pady=4)
        self.name_var = tk.StringVar(value=self.obj.properties.get("name", ""))
        name_state = "readonly" if self.obj.obj_type == "Work Product" else "normal"
        ttk.Entry(gen_frame, textvariable=self.name_var, state=name_state).grid(
            row=gen_row, column=1, padx=4, pady=4
        )
        gen_row += 1
        ttk.Label(gen_frame, text="Width:").grid(row=gen_row, column=0, sticky="e", padx=4, pady=2)
        self.width_var = tk.StringVar(value=str(self.obj.width))
        width_state = (
            "readonly"
            if self.obj.obj_type in ("Initial", "Final", "Actor", "Decision", "Merge")
            else "normal"
        )
        ttk.Entry(gen_frame, textvariable=self.width_var, state=width_state).grid(
            row=gen_row, column=1, padx=4, pady=2
        )
        gen_row += 1
        if self.obj.obj_type not in ("Fork", "Join"):
            ttk.Label(gen_frame, text="Height:").grid(
                row=gen_row, column=0, sticky="e", padx=4, pady=2
            )
            self.height_var = tk.StringVar(value=str(self.obj.height))
            height_state = (
                "readonly"
                if self.obj.obj_type
                in ("Initial", "Final", "Actor", "Decision", "Merge")
                else "normal"
            )
            ttk.Entry(gen_frame, textvariable=self.height_var, state=height_state).grid(
                row=gen_row, column=1, padx=4, pady=2
            )
            gen_row += 1
        else:
            self.height_var = tk.StringVar(value=str(self.obj.height))
        self.entries = {}
        self.listboxes = {}
        self._operations: List[OperationDefinition] = []
        self._behaviors: List[BehaviorAssignment] = []
        prop_row = 0
        rel_row = 0
        if self.obj.obj_type == "Part":
            self.obj.properties.setdefault("asil", calculate_allocated_asil(self.obj.requirements))
        key = f"{self.obj.obj_type.replace(' ', '')}Usage"
        if key not in SYSML_PROPERTIES and self.obj.obj_type == "Block Boundary":
            key = "BlockUsage"
        list_props = {
            "ports",
            "operations",
            "behaviors",
            "failureModes",
        }
        editable_list_props = {"ports"}
        if self.obj.obj_type != "Block":
            list_props.add("partProperties")
            editable_list_props.add("partProperties")
        reliability_props = {
            "analysis",
            "component",
            "fit",
            "qualification",
            "failureModes",
            "asil",
        }
        app = getattr(self.master, "app", None)
        props = SYSML_PROPERTIES.get(key, [])
        if self.obj.obj_type == "Block":
            props = [p for p in props if p != "partProperties"]
        for prop in props:
            frame = rel_frame if prop in reliability_props else prop_frame
            row = rel_row if prop in reliability_props else prop_row
            ttk.Label(frame, text=f"{prop}:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
            if prop == "operations":
                lb = tk.Listbox(frame, height=4)
                self._operations = parse_operations(self.obj.properties.get(prop, ""))
                for op in self._operations:
                    lb.insert(tk.END, format_operation(op))
                lb.grid(row=row, column=1, padx=4, pady=2, sticky="we")
                btnf = ttk.Frame(frame)
                btnf.grid(row=row, column=2, padx=2)
                ttk.Button(btnf, text="Add", command=self.add_operation).pack(side=tk.TOP)
                ttk.Button(btnf, text="Edit", command=self.edit_operation).pack(side=tk.TOP)
                ttk.Button(btnf, text="Remove", command=self.remove_operation).pack(side=tk.TOP)
                self.listboxes[prop] = lb
            elif prop == "behaviors":
                lb = tk.Listbox(frame, height=4)
                self._behaviors = parse_behaviors(self.obj.properties.get(prop, ""))
                repo = SysMLRepository.get_instance()
                for beh in self._behaviors:
                    name = repo.diagrams.get(beh.diagram)
                    label = f"{beh.operation} -> {name.name if name else beh.diagram}"
                    lb.insert(tk.END, label)
                lb.grid(row=row, column=1, padx=4, pady=2, sticky="we")
                btnf = ttk.Frame(frame)
                btnf.grid(row=row, column=2, padx=2)
                ttk.Button(btnf, text="Add", command=self.add_behavior).pack(side=tk.TOP)
                ttk.Button(btnf, text="Edit", command=self.edit_behavior).pack(side=tk.TOP)
                ttk.Button(btnf, text="Remove", command=self.remove_behavior).pack(side=tk.TOP)
                self.listboxes[prop] = lb
            elif prop in list_props:
                lb = tk.Listbox(frame, height=4)
                items = [
                    p.strip() for p in self.obj.properties.get(prop, "").split(",") if p.strip()
                ]
                for it in items:
                    lb.insert(tk.END, it)
                lb.grid(row=row, column=1, padx=4, pady=2, sticky="we")
                btnf = ttk.Frame(frame)
                btnf.grid(row=row, column=2, padx=2)
                if prop == "ports":
                    ttk.Button(btnf, text="Add", command=self.add_port).pack(side=tk.TOP)
                else:
                    ttk.Button(
                        btnf, text="Add", command=lambda p=prop: self.add_list_item(p)
                    ).pack(side=tk.TOP)
                if prop in editable_list_props:
                    if prop == "ports":
                        ttk.Button(btnf, text="Edit", command=self.edit_port).pack(side=tk.TOP)
                    else:
                        ttk.Button(
                            btnf, text="Edit", command=lambda p=prop: self.edit_list_item(p)
                        ).pack(side=tk.TOP)
                ttk.Button(
                    btnf, text="Remove", command=lambda p=prop: self.remove_list_item(p)
                ).pack(side=tk.TOP)
                self.listboxes[prop] = lb
            elif prop == "direction":
                var = tk.StringVar(value=self.obj.properties.get(prop, "in"))
                conns = [
                    c
                    for c in self.master.connections
                    if c.conn_type == "Connector" and self.obj.obj_id in (c.src, c.dst)
                ]
                state = "readonly" if conns else "normal"
                ttk.Combobox(
                    frame,
                    textvariable=var,
                    values=["in", "out", "inout"],
                    state=state,
                ).grid(row=row, column=1, padx=4, pady=2)
                self.entries[prop] = var
            elif self.obj.obj_type == "Use Case" and prop == "useCaseDefinition":
                repo = SysMLRepository.get_instance()
                diags = [
                    d
                    for d in repo.diagrams.values()
                    if d.diag_type == "Use Case Diagram" and d.diag_id != self.master.diagram_id
                ]
                idmap = {d.name or d.diag_id: d.diag_id for d in diags}
                self.ucdef_map = idmap
                cur_id = self.obj.properties.get(prop, "")
                cur_name = next((n for n, i in idmap.items() if i == cur_id), "")
                var = tk.StringVar(value=cur_name)
                ttk.Combobox(frame, textvariable=var, values=list(idmap.keys())).grid(
                    row=row, column=1, padx=4, pady=2
                )
                self.entries[prop] = var
            elif self.obj.obj_type == "Use Case" and prop == "includedUseCase":
                repo = SysMLRepository.get_instance()
                targets = [
                    repo.elements[t].name or t
                    for rel in repo.relationships
                    if rel.rel_type == "Include" and rel.source == self.obj.element_id
                    if (t := rel.target) in repo.elements
                ]
                ttk.Label(frame, text=", ".join(targets)).grid(
                    row=row, column=1, sticky="w", padx=4, pady=2
                )
            elif prop == "analysis" and app:
                analyses = getattr(app, "reliability_analyses", [])
                names = [ra.name for ra in analyses]
                var = tk.StringVar(value=self.obj.properties.get(prop, ""))
                cb = ttk.Combobox(frame, textvariable=var, values=names, state="readonly")
                cb.grid(row=row, column=1, padx=4, pady=2)
                self.entries[prop] = var
                self._analysis_map = {ra.name: ra for ra in analyses}

                def sync_analysis(_):
                    name = var.get()
                    ra = self._analysis_map.get(name)
                    if not ra:
                        return
                    if "fit" in self.entries:
                        self.entries["fit"].set(f"{ra.total_fit:.2f}")
                    else:
                        self.obj.properties["fit"] = f"{ra.total_fit:.2f}"
                    # update part list preview from analysis BOM
                    names = [c.name for c in ra.components]
                    joined = ", ".join(names)
                    if "partProperties" in self.listboxes:
                        lb = self.listboxes["partProperties"]
                        lb.delete(0, tk.END)
                        for n in names:
                            lb.insert(tk.END, n)
                    else:
                        self.obj.properties["partProperties"] = joined

                cb.bind("<<ComboboxSelected>>", sync_analysis)
            elif prop == "component" and app:
                comps = [
                    c
                    for ra in getattr(app, "reliability_analyses", [])
                    for c in ra.components
                    if c.comp_type != "circuit"
                ]
                comps.extend(
                    c
                    for c in getattr(app, "reliability_components", [])
                    if c.comp_type != "circuit"
                )
                names = list({c.name for c in comps})
                var = tk.StringVar(value=self.obj.properties.get(prop, ""))
                cb = ttk.Combobox(frame, textvariable=var, values=names, state="readonly")
                cb.grid(row=row, column=1, padx=4, pady=2)
                self.entries[prop] = var
                self._comp_map = {c.name: c for c in comps}

                def sync_component(_):
                    name = var.get()
                    comp = self._comp_map.get(name)
                    if not comp:
                        return
                    if "fit" in self.entries:
                        self.entries["fit"].set(f"{comp.fit:.2f}")
                    else:
                        self.obj.properties["fit"] = f"{comp.fit:.2f}"
                    if "qualification" in self.entries:
                        self.entries["qualification"].set(comp.qualification)
                    else:
                        self.obj.properties["qualification"] = comp.qualification
                    modes = self._get_failure_modes(app, comp.name)
                    if "failureModes" in self.entries:
                        self.entries["failureModes"].set(modes)
                    else:
                        self.obj.properties["failureModes"] = modes

                cb.bind("<<ComboboxSelected>>", sync_component)
            else:
                var = tk.StringVar(value=self.obj.properties.get(prop, ""))
                state = "normal"
                if self.obj.obj_type == "Block" and prop in ("fit", "qualification"):
                    state = "readonly"
                if self.obj.obj_type == "Part" and prop == "asil":
                    state = "readonly"
                ttk.Entry(frame, textvariable=var, state=state).grid(
                    row=row, column=1, padx=4, pady=2
                )
                self.entries[prop] = var
            if prop in reliability_props:
                rel_row += 1
            else:
                prop_row += 1

        # Display inherited reliability values only for Blocks
        if self.obj.obj_type == "Block":
            for prop in ("fit", "qualification"):
                if prop not in self.entries and self.obj.properties.get(prop, ""):
                    ttk.Label(rel_frame, text=f"{prop}:").grid(
                        row=rel_row, column=0, sticky="e", padx=4, pady=2
                    )
                    var = tk.StringVar(value=self.obj.properties.get(prop, ""))
                    ttk.Entry(rel_frame, textvariable=var, state="readonly").grid(
                        row=rel_row, column=1, padx=4, pady=2
                    )
                    self.entries[prop] = var
                    rel_row += 1

        repo = SysMLRepository.get_instance()
        current_diagram = repo.diagrams.get(getattr(self.master, "diagram_id", ""))
        link_row = 0
        if self.obj.obj_type == "Block":
            diags = [d for d in repo.diagrams.values() if d.diag_type == "Internal Block Diagram"]
            ids = {d.name or d.diag_id: d.diag_id for d in diags}
            ttk.Label(link_frame, text="Internal Block Diagram:").grid(
                row=link_row, column=0, sticky="e", padx=4, pady=2
            )
            self.diag_map = ids
            cur_id = repo.get_linked_diagram(self.obj.element_id)
            cur_name = next((n for n, i in ids.items() if i == cur_id), "")
            self.diagram_var = tk.StringVar(value=cur_name)
            ttk.Combobox(link_frame, textvariable=self.diagram_var, values=list(ids.keys())).grid(
                row=link_row, column=1, padx=4, pady=2
            )
            link_row += 1
        elif self.obj.obj_type == "Use Case":
            diagrams = [d for d in repo.diagrams.values() if d.diag_type == "BPMN Diagram"]
            self.behavior_map = {d.name or d.diag_id: d.diag_id for d in diagrams}
            ttk.Label(link_frame, text="Behavior Diagram:").grid(
                row=link_row, column=0, sticky="e", padx=4, pady=2
            )
            cur_id = repo.get_linked_diagram(self.obj.element_id)
            cur_name = next((n for n, i in self.behavior_map.items() if i == cur_id), "")
            self.behavior_var = tk.StringVar(value=cur_name)
            ttk.Combobox(
                link_frame, textvariable=self.behavior_var, values=list(self.behavior_map.keys())
            ).grid(row=link_row, column=1, padx=4, pady=2)
            link_row += 1
        elif self.obj.obj_type in ("Action Usage", "Action"):
            if (
                self.obj.obj_type == "Action"
                and current_diagram
                and current_diagram.diag_type == "BPMN Diagram"
            ):
                diagrams = [
                    d for d in repo.diagrams.values() if d.diag_type == "BPMN Diagram"
                ]
            else:
                diagrams = [
                    d
                    for d in repo.diagrams.values()
                    if d.diag_type in ("Activity Diagram", "BPMN Diagram")
                ]
            self.behavior_map = {d.name or d.diag_id: d.diag_id for d in diagrams}
            ttk.Label(link_frame, text="Behavior Diagram:").grid(
                row=link_row, column=0, sticky="e", padx=4, pady=2
            )
            cur_id = repo.get_linked_diagram(self.obj.element_id)
            cur_name = next((n for n, i in self.behavior_map.items() if i == cur_id), "")
            self.behavior_var = tk.StringVar(value=cur_name)
            ttk.Combobox(
                link_frame, textvariable=self.behavior_var, values=list(self.behavior_map.keys())
            ).grid(row=link_row, column=1, padx=4, pady=2)
            link_row += 1
        elif self.obj.obj_type == "CallBehaviorAction":
            bdiags = [
                d
                for d in repo.diagrams.values()
                if d.diag_type in ("Activity Diagram", "BPMN Diagram")
            ]
            self.behavior_map = {d.name or d.diag_id: d.diag_id for d in bdiags}
            ttk.Label(link_frame, text="Behavior Diagram:").grid(
                row=link_row, column=0, sticky="e", padx=4, pady=2
            )
            cur_id = repo.get_linked_diagram(self.obj.element_id)
            cur_name = next((n for n, i in self.behavior_map.items() if i == cur_id), "")
            self.behavior_var = tk.StringVar(value=cur_name)
            ttk.Combobox(
                link_frame, textvariable=self.behavior_var, values=list(self.behavior_map.keys())
            ).grid(row=link_row, column=1, padx=4, pady=2)
            link_row += 1
            vdiags = [d for d in repo.diagrams.values() if d.diag_type == "Internal Block Diagram"]
            self.view_map = {d.name or d.diag_id: d.diag_id for d in vdiags}
            ttk.Label(link_frame, text="View:").grid(
                row=link_row, column=0, sticky="e", padx=4, pady=2
            )
            view_id = self.obj.properties.get("view", "")
            vname = next((n for n, i in self.view_map.items() if i == view_id), "")
            self.view_var = tk.StringVar(value=vname)
            ttk.Combobox(
                link_frame, textvariable=self.view_var, values=list(self.view_map.keys())
            ).grid(row=link_row, column=1, padx=4, pady=2)
            link_row += 1
        elif self.obj.obj_type == "Part":
            blocks = [e for e in repo.elements.values() if e.elem_type == "Block"]
            idmap = {b.name or b.elem_id: b.elem_id for b in blocks}
            ttk.Label(link_frame, text="Definition:").grid(
                row=link_row, column=0, sticky="e", padx=4, pady=2
            )
            self.def_map = idmap
            cur_id = self.obj.properties.get("definition", "")
            cur_name = next((n for n, i in idmap.items() if i == cur_id), "")
            self.def_var = tk.StringVar(value=cur_name)
            self.def_cb = ttk.Combobox(
                link_frame, textvariable=self.def_var, values=list(idmap.keys())
            )
            self.def_cb.grid(row=link_row, column=1, padx=4, pady=2)
            self.def_cb.bind("<<ComboboxSelected>>", self._on_def_selected)
            self._current_def_id = cur_id
            link_row += 1

        # Requirement allocation section
        req_row = 0
        ttk.Label(req_frame, text="Requirements:").grid(
            row=req_row, column=0, sticky="ne", padx=4, pady=2
        )
        self.req_list = tk.Listbox(req_frame, height=4)
        self.req_list.grid(row=req_row, column=1, padx=4, pady=2, sticky="we")
        btnf = ttk.Frame(req_frame)
        btnf.grid(row=req_row, column=2, padx=2)
        ttk.Button(btnf, text="Add", command=self.add_requirement).pack(side=tk.TOP)
        ttk.Button(btnf, text="Remove", command=self.remove_requirement).pack(side=tk.TOP)
        for r in self.obj.requirements:
            self.req_list.insert(tk.END, f"[{r.get('id')}] {r.get('text','')}")
        req_row += 1
        self._update_asil()

    def add_port(self):
        name = simpledialog.askstring("Port", "Name:", parent=self)
        if name:
            self.listboxes["ports"].insert(tk.END, name)

    def remove_port(self):
        sel = list(self.listboxes["ports"].curselection())
        for idx in reversed(sel):
            self.listboxes["ports"].delete(idx)

    def edit_port(self):
        lb = self.listboxes["ports"]
        sel = lb.curselection()
        if not sel:
            return
        idx = sel[0]
        cur = lb.get(idx)
        name = simpledialog.askstring("Port", "Name:", initialvalue=cur, parent=self)
        if name:
            lb.delete(idx)
            lb.insert(idx, name)

    def add_list_item(self, prop: str):
        val = simpledialog.askstring(prop, "Value:", parent=self)
        if val:
            self.listboxes[prop].insert(tk.END, val)

    def remove_list_item(self, prop: str):
        lb = self.listboxes[prop]
        sel = list(lb.curselection())
        for idx in reversed(sel):
            lb.delete(idx)

    def edit_list_item(self, prop: str):
        lb = self.listboxes[prop]
        sel = lb.curselection()
        if not sel:
            return
        idx = sel[0]
        cur = lb.get(idx)
        val = simpledialog.askstring(prop, "Value:", initialvalue=cur, parent=self)
        if val:
            lb.delete(idx)
            lb.insert(idx, val)

    class OperationDialog(simpledialog.Dialog):
        def __init__(self, parent, operation=None):
            self.operation = operation
            super().__init__(parent, title="Operation")

        def body(self, master):
            ttk.Label(master, text="Name:").grid(row=0, column=0, padx=4, pady=2, sticky="e")
            self.name_var = tk.StringVar(value=getattr(self.operation, "name", ""))
            ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, padx=4, pady=2)
            ttk.Label(master, text="Parameters (name:type:dir)").grid(
                row=1, column=0, columnspan=2, padx=4, pady=2
            )
            self.param_text = tk.Text(master, height=4, width=30)
            if self.operation:
                lines = [f"{p.name}:{p.type}:{p.direction}" for p in self.operation.parameters]
                self.param_text.insert("1.0", "\n".join(lines))
            self.param_text.grid(row=2, column=0, columnspan=2, padx=4, pady=2)
            ttk.Label(master, text="Return type:").grid(row=3, column=0, padx=4, pady=2, sticky="e")
            self.ret_var = tk.StringVar(value=getattr(self.operation, "return_type", ""))
            ttk.Entry(master, textvariable=self.ret_var).grid(row=3, column=1, padx=4, pady=2)

        def apply(self):
            name = self.name_var.get().strip()
            params = []
            for line in self.param_text.get("1.0", tk.END).splitlines():
                line = line.strip()
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) == 1:
                    params.append(OperationParameter(name=parts[0]))
                elif len(parts) == 2:
                    params.append(OperationParameter(name=parts[0], type=parts[1]))
                else:
                    params.append(
                        OperationParameter(name=parts[0], type=parts[1], direction=parts[2])
                    )
            self.result = OperationDefinition(name, params, self.ret_var.get().strip())

    class BehaviorDialog(simpledialog.Dialog):
        def __init__(self, parent, operations: list[str], diag_map: dict[str, str], assignment=None):
            self.operations = operations
            self.diag_map = diag_map
            self.assignment = assignment
            super().__init__(parent, title="Behavior")

        def body(self, master):
            ttk.Label(master, text="Operation:").grid(row=0, column=0, padx=4, pady=2, sticky="e")
            self.op_var = tk.StringVar(value=getattr(self.assignment, "operation", ""))
            ttk.Combobox(master, textvariable=self.op_var, values=self.operations, state="readonly").grid(
                row=0, column=1, padx=4, pady=2
            )
            ttk.Label(master, text="Diagram:").grid(row=1, column=0, padx=4, pady=2, sticky="e")
            cur_name = next((n for n, i in self.diag_map.items() if i == getattr(self.assignment, "diagram", "")), "")
            self.diag_var = tk.StringVar(value=cur_name)
            ttk.Combobox(master, textvariable=self.diag_var, values=list(self.diag_map.keys()), state="readonly").grid(
                row=1, column=1, padx=4, pady=2
            )

        def apply(self):
            op = self.op_var.get().strip()
            diag_id = self.diag_map.get(self.diag_var.get(), "")
            self.result = BehaviorAssignment(operation=op, diagram=diag_id)

    def add_operation(self):
        dlg = self.OperationDialog(self)
        if dlg.result:
            self._operations.append(dlg.result)
            self.listboxes["operations"].insert(tk.END, format_operation(dlg.result))

    def edit_operation(self):
        lb = self.listboxes["operations"]
        sel = lb.curselection()
        if not sel:
            return
        idx = sel[0]
        op = self._operations[idx]
        dlg = self.OperationDialog(self, op)
        if dlg.result:
            self._operations[idx] = dlg.result
            lb.delete(idx)
            lb.insert(idx, format_operation(dlg.result))

    def remove_operation(self):
        lb = self.listboxes["operations"]
        sel = list(lb.curselection())
        for idx in reversed(sel):
            lb.delete(idx)
            del self._operations[idx]

    def add_behavior(self):
        repo = SysMLRepository.get_instance()
        diagrams = [
            d
            for d in repo.diagrams.values()
            if d.diag_type in ("Activity Diagram", "BPMN Diagram")
        ]
        diag_map = {d.name or d.diag_id: d.diag_id for d in diagrams}
        ops = [op.name for op in self._operations]
        dlg = self.BehaviorDialog(self, ops, diag_map)
        if dlg.result:
            self._behaviors.append(dlg.result)
            name = repo.diagrams.get(dlg.result.diagram)
            label = f"{dlg.result.operation} -> {name.name if name else dlg.result.diagram}"
            self.listboxes["behaviors"].insert(tk.END, label)

    def edit_behavior(self):
        lb = self.listboxes["behaviors"]
        sel = lb.curselection()
        if not sel:
            return
        idx = sel[0]
        repo = SysMLRepository.get_instance()
        diagrams = [
            d
            for d in repo.diagrams.values()
            if d.diag_type in ("Activity Diagram", "BPMN Diagram")
        ]
        diag_map = {d.name or d.diag_id: d.diag_id for d in diagrams}
        ops = [op.name for op in self._operations]
        dlg = self.BehaviorDialog(self, ops, diag_map, self._behaviors[idx])
        if dlg.result:
            self._behaviors[idx] = dlg.result
            name = repo.diagrams.get(dlg.result.diagram)
            label = f"{dlg.result.operation} -> {name.name if name else dlg.result.diagram}"
            lb.delete(idx)
            lb.insert(idx, label)

    def remove_behavior(self):
        lb = self.listboxes["behaviors"]
        sel = list(lb.curselection())
        for idx in reversed(sel):
            lb.delete(idx)
            del self._behaviors[idx]

    def add_requirement(self):
        if not global_requirements:
            messagebox.showinfo("No Requirements", "No requirements defined.")
            return
        dialog = self.SelectRequirementsDialog(self)
        if dialog.result:
            for rid in dialog.result:
                req = global_requirements.get(rid)
                if req and not any(r.get("id") == rid for r in self.obj.requirements):
                    self.obj.requirements.append(req)
                    self.req_list.insert(tk.END, f"[{req['id']}] {req.get('text','')}")
        self._update_asil()

    def remove_requirement(self):
        sel = list(self.req_list.curselection())
        for idx in reversed(sel):
            del self.obj.requirements[idx]
            self.req_list.delete(idx)
        self._update_asil()

    def _update_asil(self) -> None:
        """Recompute ASIL based on allocated requirements."""
        if self.obj.obj_type != "Part":
            return
        asil = calculate_allocated_asil(self.obj.requirements)
        self.obj.properties["asil"] = asil
        if "asil" in self.entries:
            self.entries["asil"].set(asil)
        repo = SysMLRepository.get_instance()
        if self.obj.element_id and self.obj.element_id in repo.elements:
            repo.elements[self.obj.element_id].properties["asil"] = asil

    def _get_failure_modes(self, app, comp_name: str) -> str:
        """Return comma separated failure modes for a component name."""
        modes = set()
        for e in getattr(app, "fmea_entries", []):
            if getattr(e, "fmea_component", "") == comp_name:
                label = getattr(e, "description", "") or getattr(e, "user_name", "")
                if label:
                    modes.add(label)
        for fmea in getattr(app, "fmeas", []):
            for e in fmea.get("entries", []):
                if getattr(e, "fmea_component", "") == comp_name:
                    label = getattr(e, "description", "") or getattr(e, "user_name", "")
                    if label:
                        modes.add(label)
        return ", ".join(sorted(modes))

    def _on_def_selected(self, event=None):
        """Callback when the definition combobox is changed."""
        repo = SysMLRepository.get_instance()
        name = self.def_var.get()
        def_id = self.def_map.get(name)
        if not def_id:
            self._current_def_id = ""
            return

        parent_id = None
        if hasattr(self.master, "diagram_id"):
            diag = repo.diagrams.get(self.master.diagram_id)
            if diag and diag.diag_type == "Internal Block Diagram":
                parent_id = getattr(diag, "father", None) or next(
                    (eid for eid, did in repo.element_diagrams.items() if did == diag.diag_id),
                    None,
                )

        if parent_id and _multiplicity_limit_exceeded(
            repo,
            parent_id,
            def_id,
            getattr(self.master, "objects", []),
            self.obj.element_id,
        ):
            messagebox.showinfo(
                "Add Part",
                "Maximum number of parts of that type has been reached",
            )
            prev_name = next(
                (n for n, i in self.def_map.items() if i == self._current_def_id),
                "",
            )
            self.def_var.set(prev_name)
            return

        self._current_def_id = def_id

    def apply(self):
        repo = SysMLRepository.get_instance()
        parent_id = None
        if self.obj.obj_type != "Work Product":
            new_name = self.name_var.get()
            if self.obj.obj_type == "Part" and hasattr(self.master, "diagram_id"):
                diag = repo.diagrams.get(self.master.diagram_id)
                if diag and diag.diag_type == "Internal Block Diagram":
                    parent_id = getattr(diag, "father", None) or next(
                        (eid for eid, did in repo.element_diagrams.items() if did == diag.diag_id),
                        None,
                    )
            if parent_id and _part_name_exists(repo, parent_id, new_name, self.obj.element_id):
                messagebox.showinfo("Add Part", "A part with that name already exists")
                new_name = self.obj.properties.get("name", "")
            new_name = repo.ensure_unique_element_name(new_name, self.obj.element_id)
            if self.obj.obj_type == "Port" and hasattr(self.master, "objects"):
                rename_port(repo, self.obj, self.master.objects, new_name)
            self.obj.properties["name"] = new_name
            if self.obj.element_id and self.obj.element_id in repo.elements:
                elem = repo.elements[self.obj.element_id]
                if self.obj.obj_type in ("Block", "Block Boundary") and elem.elem_type == "Block":
                    rename_block(repo, elem.elem_id, new_name)
                else:
                    elem.name = new_name
            if self.obj.obj_type == "Port" and hasattr(self.master, "objects"):
                rename_port(repo, self.obj, self.master.objects, new_name)
        else:
            new_name = self.obj.properties.get("name", "")
        for prop, var in self.entries.items():
            self.obj.properties[prop] = var.get()
            if self.obj.element_id and self.obj.element_id in repo.elements:
                repo.elements[self.obj.element_id].properties[prop] = var.get()
        removed_parts = []
        prev_parts = []
        if (
            self.obj.element_id
            and self.obj.element_id in repo.elements
            and "partProperties" in repo.elements[self.obj.element_id].properties
        ):
            prev_parts = [
                p.strip()
                for p in repo.elements[self.obj.element_id]
                .properties.get("partProperties", "")
                .split(",")
                if p.strip()
            ]

        for prop, lb in self.listboxes.items():
            if prop == "operations":
                self.obj.properties[prop] = operations_to_json(self._operations)
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties[prop] = self.obj.properties[prop]
            elif prop == "behaviors":
                self.obj.properties[prop] = behaviors_to_json(self._behaviors)
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties[prop] = self.obj.properties[prop]
            else:
                items = [lb.get(i) for i in range(lb.size())]
                joined = ", ".join(items)
                self.obj.properties[prop] = joined
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties[prop] = joined
                if prop == "partProperties" and prev_parts:
                    prev_keys = {_part_prop_key(p) for p in prev_parts}
                    new_keys = {_part_prop_key(i) for i in items}
                    removed_parts = [p for p in prev_parts if _part_prop_key(p) not in new_keys]

        if self.obj.element_id and self.obj.element_id in repo.elements:
            elem_type = repo.elements[self.obj.element_id].elem_type
            if elem_type == "Block" and self.obj.obj_type in ("Block", "Block Boundary"):
                propagate_block_port_changes(repo, self.obj.element_id)
                propagate_block_part_changes(repo, self.obj.element_id)
                propagate_block_changes(repo, self.obj.element_id)
                app_ref = getattr(self.master, "app", None)
                added = _sync_ibd_partproperty_parts(
                    repo,
                    self.obj.element_id,
                    app=app_ref,
                    visible=True,
                )
                for data in added:
                    data["hidden"] = False
                _propagate_boundary_parts(repo, self.obj.element_id, added, app=app_ref)
                father_diag_id = repo.get_linked_diagram(self.obj.element_id)
                for diag in repo.diagrams.values():
                    if (
                        diag.diag_type == "Internal Block Diagram"
                        and getattr(diag, "father", None) == self.obj.element_id
                        and diag.diag_id != father_diag_id
                    ):
                        added_child = inherit_father_parts(repo, diag)
                        for obj in added_child:
                            if obj.get("obj_type") == "Part":
                                obj["hidden"] = False
                        if app_ref:
                            for win in getattr(app_ref, "ibd_windows", []):
                                if getattr(win, "diagram_id", None) == diag.diag_id:
                                    for obj in added_child:
                                        win.objects.append(SysMLObject(**obj))
                                    win.redraw()
                                    win._sync_to_repository()
        try:
            if self.obj.obj_type not in (
                "Initial",
                "Final",
                "Decision",
                "Merge",
            ):
                self.obj.width = float(self.width_var.get())
                self.obj.height = float(self.height_var.get())
        except ValueError:
            pass

        if hasattr(self.master, "ensure_text_fits"):
            self.master.ensure_text_fits(self.obj)

        self._update_asil()

        # ensure block shows BOM components as part names when an analysis is set
        if (
            self.obj.obj_type == "Block"
            and "analysis" in self.obj.properties
            and hasattr(self, "_analysis_map")
        ):
            ra = self._analysis_map.get(self.obj.properties["analysis"], None)
            if ra:
                cur = [
                    p.strip()
                    for p in self.obj.properties.get("partProperties", "").split(",")
                    if p.strip()
                ]
                names = [c.name for c in ra.components]
                for n in names:
                    if n not in cur:
                        cur.append(n)
                joined = ", ".join(cur)
                self.obj.properties["partProperties"] = joined
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties["partProperties"] = joined
                if self.obj.element_id:
                    inherit_block_properties(repo, self.obj.element_id)
                    self.obj.properties["partProperties"] = repo.elements[
                        self.obj.element_id
                    ].properties["partProperties"]

        # Update linked diagram if applicable
        link_id = None
        if hasattr(self, "behavior_var") and self.behavior_var.get():
            link_id = self.behavior_map.get(self.behavior_var.get())
        elif hasattr(self, "diagram_var"):
            link_id = self.diag_map.get(self.diagram_var.get())
        if hasattr(self, "behavior_var") or hasattr(self, "diagram_var"):
            if (
                self.obj.obj_type == "Block"
                and hasattr(self, "diagram_var")
                and link_id
                and link_id in repo.diagrams
                and repo.diagrams[link_id].diag_type == "Internal Block Diagram"
            ):
                link_block_to_ibd(
                    repo,
                    self.obj.element_id,
                    link_id,
                    app=getattr(self.master, "app", None),
                )
            else:
                repo.link_diagram(self.obj.element_id, link_id)
        if hasattr(self, "view_var"):
            view_id = self.view_map.get(self.view_var.get())
            if view_id:
                self.obj.properties["view"] = view_id
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties["view"] = view_id
            else:
                self.obj.properties.pop("view", None)
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties.pop("view", None)
        if hasattr(self, "def_var"):
            name = self.def_var.get()
            def_id = self.def_map.get(name)
            if def_id:
                parent_id = None
                if hasattr(self.master, "diagram_id"):
                    diag = repo.diagrams.get(self.master.diagram_id)
                    if diag and diag.diag_type == "Internal Block Diagram":
                        parent_id = getattr(diag, "father", None) or next(
                            (eid for eid, did in repo.element_diagrams.items() if did == diag.diag_id),
                            None,
                        )
                if parent_id:
                    rel = next(
                        (
                            r
                            for r in repo.relationships
                            if r.source == parent_id
                            and r.target == def_id
                            and r.rel_type in ("Aggregation", "Composite Aggregation")
                        ),
                        None,
                    )
                    limit_exceeded = _multiplicity_limit_exceeded(
                        repo,
                        parent_id,
                        def_id,
                        getattr(self.master, "objects", []),
                        self.obj.element_id,
                    )
                    if limit_exceeded:
                        messagebox.showinfo(
                            "Add Part",
                            "Maximum number of parts of that type has been reached",
                        )
                        def_id = None
                if def_id:
                    self.obj.properties["definition"] = def_id
                    if self.obj.element_id and self.obj.element_id in repo.elements:
                        repo.elements[self.obj.element_id].properties["definition"] = def_id
        if hasattr(self, "ucdef_var"):
            name = self.ucdef_var.get()
            def_id = self.ucdef_map.get(name)
            if def_id:
                self.obj.properties["useCaseDefinition"] = def_id
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties["useCaseDefinition"] = def_id

        # ------------------------------------------------------------
        # Add parts from selected analysis BOM
        # ------------------------------------------------------------
        if (
            self.obj.obj_type == "Block"
            and "analysis" in self.obj.properties
            and hasattr(self, "diag_map")
        ):
            diag_id = repo.get_linked_diagram(self.obj.element_id)
            if diag_id:
                ra_name = self.obj.properties.get("analysis", "")
                ra = getattr(self, "_analysis_map", {}).get(ra_name)
                if ra and ra.components:
                    comps = list(ra.components)
                    dlg = self.SelectComponentsDialog(self, comps)
                    selected = dlg.result or []
                    if selected:
                        diag = repo.diagrams.get(diag_id)
                        if diag is not None:
                            diag.objects = getattr(diag, "objects", [])
                            existing = {
                                o.get("properties", {}).get("component")
                                for o in diag.objects
                                if o.get("obj_type") == "Part"
                            }
                            base_x = 50.0
                            base_y = 50.0
                            offset = 60.0
                            for idx, c in enumerate(selected):
                                if c.name in existing:
                                    continue
                                elem = repo.create_element(
                                    "Part",
                                    name=c.name,
                                    properties={
                                        "component": c.name,
                                        "fit": f"{c.fit:.2f}",
                                        "qualification": c.qualification,
                                        "failureModes": self._get_failure_modes(
                                            getattr(self.master, "app", None), c.name
                                        ),
                                    },
                                    owner=repo.root_package.elem_id,
                                )
                                repo.add_element_to_diagram(diag_id, elem.elem_id)
                                obj = SysMLObject(
                                    _get_next_id(),
                                    "Part",
                                    base_x,
                                    base_y + offset * idx,
                                    element_id=elem.elem_id,
                                    properties=elem.properties.copy(),
                                )
                                diag.objects.append(obj.__dict__)
                                # update any open windows for this diagram
                                app = getattr(self.master, "app", None)
                                if app:
                                    for win in getattr(app, "ibd_windows", []):
                                        if win.diagram_id == diag_id:
                                            win.objects.append(obj)
                                            win.redraw()
                                            win._sync_to_repository()
                            # update block partProperties with newly added components
                            new_names = [c.name for c in selected if c.name not in existing]
                            if new_names:
                                cur = self.obj.properties.get("partProperties", "")
                                names = [n.strip() for n in cur.split(",") if n.strip()]
                                for name in new_names:
                                    if name not in names:
                                        names.append(name)
                                joined = ", ".join(names)
                                self.obj.properties["partProperties"] = joined
                                if self.obj.element_id and self.obj.element_id in repo.elements:
                                    repo.elements[self.obj.element_id].properties[
                                        "partProperties"
                                    ] = joined
                                # update all diagram objects referencing this block element
                                for d in repo.diagrams.values():
                                    for o in getattr(d, "objects", []):
                                        if o.get("element_id") == self.obj.element_id:
                                            o.setdefault("properties", {})[
                                                "partProperties"
                                            ] = joined
                                # include parent block parts
                                if self.obj.element_id:
                                    inherit_block_properties(repo, self.obj.element_id)
                                    joined = repo.elements[self.obj.element_id].properties[
                                        "partProperties"
                                    ]
                                    self.obj.properties["partProperties"] = joined
                            repo.diagrams[diag_id] = diag
                            repo.touch_diagram(diag_id)
                            if self.obj.element_id:
                                repo.touch_element(self.obj.element_id)
                            if hasattr(self.master, "_sync_to_repository"):
                                self.master._sync_to_repository()


class ConnectionDialog(simpledialog.Dialog):
    """Edit connection style and custom routing points."""

    def __init__(self, master, connection: DiagramConnection):
        self.connection = connection
        super().__init__(master, title="Connection Properties")

    def body(self, master):
        # Disable window resizing so the property layout stays consistent
        self.resizable(False, False)
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.name_var = tk.StringVar(value=self.connection.name)
        ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, columnspan=2, padx=4, pady=4, sticky="we")

        ttk.Label(master, text="Style:").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.style_var = tk.StringVar(value=self.connection.style)
        ttk.Combobox(master, textvariable=self.style_var,
                     values=["Straight", "Squared", "Custom"]).grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(master, text="Points:").grid(row=2, column=0, sticky="ne", padx=4, pady=4)
        self.point_list = tk.Listbox(master, height=4)
        for px, py in self.connection.points:
            self.point_list.insert(tk.END, f"{px:.1f},{py:.1f}")
        self.point_list.grid(row=2, column=1, padx=4, pady=4, sticky="we")
        btnf = ttk.Frame(master)
        btnf.grid(row=2, column=2, padx=2)
        ttk.Button(btnf, text="Add", command=self.add_point).pack(side=tk.TOP)
        ttk.Button(btnf, text="Remove", command=self.remove_point).pack(side=tk.TOP)

        ttk.Label(master, text="Arrows:").grid(row=3, column=0, sticky="e", padx=4, pady=4)
        self.arrow_var = tk.StringVar(value=self.connection.arrow)
        self.arrow_cb = ttk.Combobox(
            master,
            textvariable=self.arrow_var,
            values=["none", "forward", "backward", "both"],
        )
        self.arrow_cb.grid(row=3, column=1, padx=4, pady=4)
        self.mid_var = tk.BooleanVar(value=self.connection.mid_arrow)
        self.mid_check = ttk.Checkbutton(
            master, text="Arrow", variable=self.mid_var
        )
        self.mid_check.grid(row=3, column=2, padx=4, pady=4)
        if self.connection.conn_type in (
            "Flow",
            "Generalize",
            "Generalization",
            "Include",
            "Extend",
        ):
            self.arrow_cb.configure(state="disabled")
            self.mid_check.configure(state="disabled")
        row = 4
        if self.connection.conn_type == "Control Action":
            repo = SysMLRepository.get_instance()
            src_obj = self.master.get_object(self.connection.src)
            beh_elems = get_block_behavior_elements(repo, getattr(src_obj, "element_id", ""))
            self.elem_map = {e.name or e.elem_id: e.elem_id for e in beh_elems}
            ttk.Label(master, text="Element:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
            cur_name = next(
                (n for n, i in self.elem_map.items() if i == self.connection.element_id),
                "",
            )
            self.elem_var = tk.StringVar(value=cur_name)
            ttk.Combobox(
                master,
                textvariable=self.elem_var,
                values=list(self.elem_map.keys()),
            ).grid(row=row, column=1, padx=4, pady=4, sticky="we")
            row += 1
            ttk.Label(master, text="Guard:").grid(row=row, column=0, sticky="ne", padx=4, pady=4)
            self.guard_list = tk.Listbox(master, height=4)
            for g in self.connection.guard:
                self.guard_list.insert(tk.END, g)
            self.guard_list.grid(row=row, column=1, padx=4, pady=4, sticky="we")
            gbtn = ttk.Frame(master)
            gbtn.grid(row=row, column=2, padx=2)
            ttk.Button(gbtn, text="Add", command=self.add_guard).pack(side=tk.TOP)
            ttk.Button(gbtn, text="Remove", command=self.remove_guard).pack(side=tk.TOP)
            row += 1
            ttk.Label(master, text="Guard Ops:").grid(row=row, column=0, sticky="ne", padx=4, pady=4)
            self.guard_ops_list = tk.Listbox(master, height=4)
            for op in self.connection.guard_ops:
                self.guard_ops_list.insert(tk.END, op)
            self.guard_ops_list.grid(row=row, column=1, padx=4, pady=4, sticky="we")
            opbtn = ttk.Frame(master)
            opbtn.grid(row=row, column=2, padx=2)
            self.guard_op_choice = tk.StringVar(value="AND")
            ttk.Combobox(opbtn, textvariable=self.guard_op_choice, values=["AND", "OR"], state="readonly").pack(side=tk.TOP)
            ttk.Button(opbtn, text="Add", command=self.add_guard_op).pack(side=tk.TOP)
            ttk.Button(opbtn, text="Remove", command=self.remove_guard_op).pack(side=tk.TOP)
            row += 1

        if self.connection.conn_type in ("Aggregation", "Composite Aggregation"):
            ttk.Label(master, text="Multiplicity:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
            self.mult_var = tk.StringVar(value=self.connection.multiplicity)
            ttk.Combobox(
                master,
                textvariable=self.mult_var,
                values=["1", "0..1", "1..*", "0..*", "2", "3", "4", "5"],
            ).grid(row=row, column=1, padx=4, pady=4, sticky="we")

    def add_point(self):
        x = simpledialog.askfloat("Point", "X:", parent=self)
        y = simpledialog.askfloat("Point", "Y:", parent=self)
        if x is not None and y is not None:
            self.point_list.insert(tk.END, f"{x},{y}")

    def remove_point(self):
        sel = list(self.point_list.curselection())
        for idx in reversed(sel):
            self.point_list.delete(idx)

    def add_guard(self):
        txt = simpledialog.askstring("Guard", "Condition:", parent=self)
        if txt:
            self.guard_list.insert(tk.END, txt)

    def remove_guard(self):
        sel = list(self.guard_list.curselection())
        for idx in reversed(sel):
            self.guard_list.delete(idx)

    def add_guard_op(self):
        op = self.guard_op_choice.get()
        self.guard_ops_list.insert(tk.END, op)

    def remove_guard_op(self):
        sel = list(self.guard_ops_list.curselection())
        for idx in reversed(sel):
            self.guard_ops_list.delete(idx)

    def apply(self):
        self.connection.name = self.name_var.get()
        self.connection.style = self.style_var.get()
        pts = []
        for i in range(self.point_list.size()):
            txt = self.point_list.get(i)
            try:
                x_str, y_str = txt.split(",")
                pts.append((float(x_str), float(y_str)))
            except ValueError:
                continue
        self.connection.points = pts
        self.connection.arrow = self.arrow_var.get()
        self.connection.mid_arrow = self.mid_var.get()
        if hasattr(self, "mult_var"):
            self.connection.multiplicity = self.mult_var.get()
        if hasattr(self, "guard_list"):
            self.connection.guard = [self.guard_list.get(i) for i in range(self.guard_list.size())]
        if hasattr(self, "guard_ops_list"):
            self.connection.guard_ops = [
                self.guard_ops_list.get(i) for i in range(self.guard_ops_list.size())
            ]
        if hasattr(self, "elem_var"):
            sel = self.elem_var.get()
            self.connection.element_id = self.elem_map.get(sel, "")
            if self.connection.element_id:
                repo = SysMLRepository.get_instance()
                elem = repo.elements.get(self.connection.element_id)
                if elem and not self.connection.name:
                    self.connection.name = elem.name
                if hasattr(self.master, "repo"):
                    self.master.repo.add_element_to_diagram(
                        self.master.diagram_id, self.connection.element_id
                    )
        if hasattr(self.master, "_sync_to_repository"):
            self.master._sync_to_repository()
        if self.connection.conn_type in ("Aggregation", "Composite Aggregation"):
            if hasattr(self.master, "repo"):
                whole = self.master.get_object(self.connection.src).element_id
                part = self.master.get_object(self.connection.dst).element_id
                if self.connection.conn_type == "Composite Aggregation":
                    add_composite_aggregation_part(
                        self.master.repo,
                        whole,
                        part,
                        self.connection.multiplicity,
                        app=getattr(self.master, "app", None),
                    )
                else:
                    add_aggregation_part(
                        self.master.repo,
                        whole,
                        part,
                        self.connection.multiplicity,
                        app=getattr(self.master, "app", None),
                    )
                if hasattr(self.master, "_sync_to_repository"):
                    self.master._sync_to_repository()


class UseCaseDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None, history=None):
        tools = [
            "Actor",
            "Use Case",
            "System Boundary",
            "Association",
            "Communication Path",
            "Generalize",
            "Include",
            "Extend",
        ]
        super().__init__(master, "Use Case Diagram", tools, diagram_id, app=app, history=history)


class ActivityDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None, history=None):
        tools = [
            "Action",
            "CallBehaviorAction",
            "Initial",
            "Final",
            "Decision",
            "Merge",
            "Fork",
            "Join",
            "Flow",
            "System Boundary",
        ]
        super().__init__(master, "Activity Diagram", tools, diagram_id, app=app, history=history)
        ttk.Button(
            self.toolbox,
            text="Add Block Operations",
            command=self.add_block_operations,
        ).pack(fill=tk.X, padx=2, pady=2)

    class SelectOperationsDialog(simpledialog.Dialog):
        def __init__(self, parent, operations):
            self.operations = operations
            self.selected = {}
            super().__init__(parent, title="Select Operations")

        def body(self, master):
            ttk.Label(master, text="Select operations:").pack(padx=5, pady=5)
            frame = ttk.Frame(master)
            frame.pack(fill=tk.BOTH, expand=True)
            canvas = tk.Canvas(frame, borderwidth=0)
            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            self.check_frame = ttk.Frame(canvas)
            self.check_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=self.check_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            for label, op, diag in self.operations:
                var = tk.BooleanVar(value=True)
                self.selected[(op, diag)] = var
                ttk.Checkbutton(self.check_frame, text=label, variable=var).pack(anchor="w", padx=2, pady=2)
            return self.check_frame

        def apply(self):
            self.result = [(op, diag) for (op, diag), var in self.selected.items() if var.get()]

    def add_block_operations(self):
        repo = self.repo
        blocks = []
        for elem in repo.elements.values():
            if elem.elem_type != "Block":
                continue
            for beh in parse_behaviors(elem.properties.get("behaviors", "")):
                if beh.diagram == self.diagram_id:
                    blocks.append(elem)
                    break
        operations = []
        for blk in blocks:
            ops = parse_operations(blk.properties.get("operations", ""))
            behs = {b.operation: b.diagram for b in parse_behaviors(blk.properties.get("behaviors", ""))}
            for op in ops:
                diag_id = behs.get(op.name)
                if diag_id:
                    label = f"{blk.name}.{format_operation(op)}"
                    operations.append((label, op.name, diag_id))
        if not operations:
            messagebox.showinfo("Add Block Operations", "No operations available")
            return
        dlg = self.SelectOperationsDialog(self, operations)
        selected = dlg.result or []
        if not selected:
            return
        diag = repo.diagrams.get(self.diagram_id)
        base_x = 50.0
        base_y = 50.0
        offset = 60.0
        for idx, (op_name, d_id) in enumerate(selected):
            elem = repo.create_element("CallBehaviorAction", name=op_name, owner=diag.package)
            repo.add_element_to_diagram(self.diagram_id, elem.elem_id)
            repo.link_diagram(elem.elem_id, d_id)
            obj = SysMLObject(
                _get_next_id(),
                "CallBehaviorAction",
                base_x,
                base_y + offset * idx,
                element_id=elem.elem_id,
                properties={"name": op_name},
            )
            diag.objects.append(obj.__dict__)
            self.objects.append(obj)
        self.redraw()
        self._sync_to_repository()


class BPMNDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None, history=None):
        tools = [
            "Action",
            "Initial",
            "Final",
            "Decision",
            "Merge",
            "Flow",
            "System Boundary",
        ]
        super().__init__(master, "BPMN Diagram", tools, diagram_id, app=app, history=history)
        for child in self.toolbox.winfo_children():
            if isinstance(child, ttk.Button) and child.cget("text") == "Action":
                child.configure(text="Task")

        canvas_frame = self.canvas.master
        canvas_frame.pack_forget()

        bpmn_panel = ttk.LabelFrame(self, text="BPMN")
        bpmn_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=2, pady=2)

        for name in (
            "Propagate",
            "Propagate by Review",
            "Propagate by Approval",
            "Re-use",
        ):
            ttk.Button(
                bpmn_panel,
                text=name,
                command=lambda t=name: self.select_tool(t),
            ).pack(fill=tk.X, padx=2, pady=2)

        ttk.Button(
            bpmn_panel,
            text="Add Work Product",
            command=self.add_work_product,
        ).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(
            bpmn_panel,
            text="Add Process Area",
            command=self.add_process_area,
        ).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(
            bpmn_panel,
            text="Add Lifecycle Phase",
            command=self.add_lifecycle_phase,
        ).pack(fill=tk.X, padx=2, pady=2)

        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self._activate_parent_phase()
        self.refresh_from_repository()

    def _activate_parent_phase(self) -> None:
        """Activate the lifecycle phase containing this diagram.

        When a BPMN diagram window is opened, switch the application's active
        lifecycle phase to the module that owns the diagram. Any tooling not
        enabled for that phase is hidden via ``on_lifecycle_selected`` or
        ``refresh_tool_enablement``.
        """

        app = getattr(self, "app", None)
        if not app or not getattr(app, "safety_mgmt_toolbox", None):
            return
        toolbox = app.safety_mgmt_toolbox
        diag = self.repo.diagrams.get(self.diagram_id)
        if not diag:
            return
        name = diag.name or ""
        phase = toolbox.module_for_diagram(name)
        if not phase:
            return
        if hasattr(app, "lifecycle_var"):
            try:
                app.lifecycle_var.set(phase)
            except Exception:
                pass
        if hasattr(app, "on_lifecycle_selected"):
            try:
                app.on_lifecycle_selected()
                return
            except Exception:
                pass
        toolbox.set_active_module(phase)
        if hasattr(app, "refresh_tool_enablement"):
            try:
                app.refresh_tool_enablement()
            except Exception:
                pass

    class _SelectDialog(simpledialog.Dialog):  # pragma: no cover - requires tkinter
        def __init__(self, parent, title: str, options: list[str]):
            self.options = options
            self.selection = ""
            super().__init__(parent, title)

        def body(self, master):  # pragma: no cover - requires tkinter
            ttk.Label(master, text="Select:").pack(padx=5, pady=5)
            self.var = tk.StringVar(value=self.options[0] if self.options else "")
            combo = ttk.Combobox(
                master,
                textvariable=self.var,
                values=self.options,
                state="readonly",
            )
            combo.pack(padx=5, pady=5)
            return combo

        def apply(self):  # pragma: no cover - requires tkinter
            self.selection = self.var.get()

    def add_work_product(self):  # pragma: no cover - requires tkinter
        def _fmt(req: str) -> str:
            return " ".join(
                word.upper() if word.isupper() else word.capitalize()
                for word in req.split()
            )

        options = [
            "Architecture Diagram",
            "Safety & Security Concept",
            *REQUIREMENT_WORK_PRODUCTS,
            "HAZOP",
            "STPA",
            "Threat Analysis",
            "FI2TC",
            "TC2FI",
            "Risk Assessment",
            "Product Goal Specification",
            "FTA",
            "FMEA",
            "FMEDA",
        ]
        options.extend(
            f"{_fmt(rt)} Requirement Specification" for rt in REQUIREMENT_TYPE_OPTIONS
        )
        dlg = self._SelectDialog(self, "Add Work Product", options)
        name = getattr(dlg, "selection", "")
        if not name:
            return
        area_map = {
            "Architecture Diagram": "System Design (Item Definition)",
            "Safety & Security Concept": "System Design (Item Definition)",
            "Product Goal Specification": "System Design (Item Definition)",
            **{wp: "System Design (Item Definition)" for wp in REQUIREMENT_WORK_PRODUCTS},
            "HAZOP": "Hazard & Threat Analysis",
            "STPA": "Hazard & Threat Analysis",
            "Threat Analysis": "Hazard & Threat Analysis",
            "FI2TC": "Hazard & Threat Analysis",
            "TC2FI": "Hazard & Threat Analysis",
            "Risk Assessment": "Risk Assessment",
            "FTA": "Safety Analysis",
            "FMEA": "Safety Analysis",
            "FMEDA": "Safety Analysis",
        }
        for rt in REQUIREMENT_TYPE_OPTIONS:
            area_map[f"{_fmt(rt)} Requirement Specification"] = "System Design (Item Definition)"
        required = area_map.get(name)
        if required and not any(
            o.obj_type == "System Boundary" and o.properties.get("name") == required
            for o in self.objects
        ):
            messagebox.showerror(
                "Missing Process Area",
                f"Add process area '{required}' before adding this work product.",
            )
            return
        obj = SysMLObject(
            _get_next_id(),
            "Work Product",
            100.0,
            100.0,
            width=60.0,
            height=80.0,
            properties={"name": name},
        )
        self.objects.append(obj)
        self.sort_objects()
        self._sync_to_repository()
        self.redraw()
        if getattr(self.app, "enable_work_product", None):
            self.app.enable_work_product(name)
        toolbox = getattr(self.app, "safety_mgmt_toolbox", None)
        if toolbox:
            diag = self.repo.diagrams.get(self.diagram_id)
            diagram_name = diag.name if diag else ""
            toolbox.add_work_product(diagram_name, name, "")

    def add_process_area(self):  # pragma: no cover - requires tkinter
        options = [
            "System Design (Item Definition)",
            "Hazard & Threat Analysis",
            "Risk Assessment",
            "Safety Analysis",
        ]
        dlg = self._SelectDialog(self, "Add Process Area", options)
        name = getattr(dlg, "selection", "")
        if not name:
            return
        obj = SysMLObject(
            _get_next_id(),
            "System Boundary",
            100.0,
            100.0,
            width=200.0,
            height=150.0,
            properties={"name": name},
        )
        self.objects.insert(0, obj)
        self.sort_objects()
        self._sync_to_repository()
        self.redraw()
        if getattr(self.app, "enable_process_area", None):
            self.app.enable_process_area(name)

    def add_lifecycle_phase(self):  # pragma: no cover - requires tkinter
        toolbox = getattr(self.app, "safety_mgmt_toolbox", None)
        if not toolbox:
            return

        def _collect(mod, prefix=""):
            path = f"{prefix}{mod.name}" if prefix else mod.name
            names.append(path)
            for sub in mod.modules:
                _collect(sub, path + "/")

        names: List[str] = []
        for mod in getattr(toolbox, "modules", []):
            _collect(mod)
        if not names:
            return

        dlg = self._SelectDialog(self, "Add Lifecycle Phase", names)
        name = getattr(dlg, "selection", "")
        if not name:
            return
        obj = SysMLObject(
            _get_next_id(),
            "Lifecycle Phase",
            100.0,
            100.0,
            width=120.0,
            height=80.0,
            properties={"name": name},
        )
        self.objects.append(obj)
        self.sort_objects()
        self._sync_to_repository()
        self.redraw()


class BlockDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None, history=None):
        tools = [
            "Block",
            "Association",
            "Generalization",
            "Aggregation",
            "Composite Aggregation",
        ]
        super().__init__(master, "Block Diagram", tools, diagram_id, app=app, history=history)
        ttk.Button(
            self.toolbox,
            text="Add Blocks",
            command=self.add_blocks,
        ).pack(fill=tk.X, padx=2, pady=2)

    def _add_block_relationships(self) -> None:
        """Add connections for any existing relationships between blocks."""
        repo = self.repo
        diag = repo.diagrams.get(self.diagram_id)
        if not diag:
            return
        obj_map = {
            o.element_id: o.obj_id
            for o in self.objects
            if o.obj_type == "Block" and o.element_id
        }
        existing = {
            (c.src, c.dst, c.conn_type)
            for c in self.connections
        } | {
            (c.dst, c.src, c.conn_type)
            for c in self.connections
        }
        for rel in repo.relationships:
            if rel.rel_type not in (
                "Association",
                "Generalization",
                "Aggregation",
                "Composite Aggregation",
            ):
                continue
            if rel.source in obj_map and rel.target in obj_map:
                src_id = obj_map[rel.source]
                dst_id = obj_map[rel.target]
                if (src_id, dst_id, rel.rel_type) in existing:
                    continue
                if (dst_id, src_id, rel.rel_type) in existing:
                    continue
                conn = DiagramConnection(
                    src_id,
                    dst_id,
                    rel.rel_type,
                    arrow="forward" if rel.rel_type == "Generalization" else "none",
                    stereotype=rel.stereotype or "",
                )
                self.connections.append(conn)
                diag.connections.append(conn.__dict__)
                repo.add_relationship_to_diagram(self.diagram_id, rel.rel_id)

    def add_blocks(self) -> None:
        repo = self.repo
        diag = repo.diagrams.get(self.diagram_id)
        if not diag:
            return
        existing = {
            o.element_id
            for o in self.objects
            if o.obj_type == "Block" and o.element_id
        }
        candidates = set()
        for d in repo.diagrams.values():
            if d.diag_type != "Block Diagram" or d.diag_id == self.diagram_id:
                continue
            for obj in getattr(d, "objects", []):
                if obj.get("obj_type") == "Block" and obj.get("element_id"):
                    candidates.add(obj["element_id"])
        names = []
        id_map = {}
        for bid in candidates:
            if bid in existing or bid not in repo.elements:
                continue
            name = repo.elements[bid].name or bid
            names.append(name)
            id_map[name] = bid
        if not names:
            messagebox.showinfo("Add Blocks", "No blocks available")
            return
        dlg = SysMLObjectDialog.SelectNamesDialog(self, names, title="Add Blocks")
        selected = dlg.result or []
        if not selected:
            return
        base_x = 50.0
        base_y = 50.0
        offset = 180.0
        for idx, name in enumerate(selected):
            blk_id = id_map.get(name)
            if not blk_id:
                continue
            repo.add_element_to_diagram(self.diagram_id, blk_id)
            elem = repo.elements.get(blk_id)
            props = elem.properties.copy() if elem else {}
            props["name"] = elem.name if elem else blk_id
            obj = SysMLObject(
                _get_next_id(),
                "Block",
                base_x,
                base_y + offset * idx,
                element_id=blk_id,
                width=160.0,
                height=140.0,
                properties=props,
            )
            diag.objects.append(obj.__dict__)
            self.objects.append(obj)
        if hasattr(self, "_add_block_relationships"):
            self._add_block_relationships()
        self.redraw()
        self._sync_to_repository()


class InternalBlockDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None, history=None):
        tools = [
            "Part",
            "Port",
            "Connector",
        ]
        super().__init__(master, "Internal Block Diagram", tools, diagram_id, app=app, history=history)
        ttk.Button(
            self.toolbox,
            text="Add Contained Parts",
            command=self.add_contained_parts,
        ).pack(fill=tk.X, padx=2, pady=2)

    def _get_failure_modes(self, comp_name: str) -> str:
        """Return comma separated failure modes for a component name."""
        app = getattr(self, "app", None)
        modes = set()
        for e in getattr(app, "fmea_entries", []):
            if getattr(e, "fmea_component", "") == comp_name:
                label = getattr(e, "description", "") or getattr(e, "user_name", "")
                if label:
                    modes.add(label)
        for fmea in getattr(app, "fmeas", []):
            for entry in fmea.get("entries", []):
                if getattr(entry, "fmea_component", "") == comp_name:
                    label = getattr(entry, "description", "") or getattr(entry, "user_name", "")
                    if label:
                        modes.add(label)
        return ", ".join(sorted(modes))

    def _get_part_name(self, obj: SysMLObject) -> str:
        repo = self.repo
        name = ""
        has_name = False
        def_id = obj.properties.get("definition")
        if obj.element_id and obj.element_id in repo.elements:
            elem = repo.elements[obj.element_id]
            name = elem.name or elem.properties.get("component", "")
            def_id = def_id or elem.properties.get("definition")
            def_name = ""
            if def_id and def_id in repo.elements:
                def_name = repo.elements[def_id].name or def_id
            has_name = bool(name) and not _is_default_part_name(def_name, name)
        if not has_name:
            name = obj.properties.get("component", "")

        def_id = obj.properties.get("definition")
        def_name = ""
        mult = ""
        comp = obj.properties.get("component", "")
        if def_id and def_id in repo.elements:
            def_name = repo.elements[def_id].name or def_id
            diag = repo.diagrams.get(self.diagram_id)
            block_id = (
                getattr(diag, "father", None)
                or next(
                    (eid for eid, did in repo.element_diagrams.items() if did == self.diagram_id),
                    None,
                )
            )
            if block_id:
                for rel in repo.relationships:
                    if (
                        rel.rel_type in ("Aggregation", "Composite Aggregation")
                        and rel.source == block_id
                        and rel.target == def_id
                    ):
                        mult = rel.properties.get("multiplicity", "1")
                        if mult in ("", "1"):
                            mult = ""
                        break

        if obj.element_id and obj.element_id in repo.elements and not comp:
            comp = repo.elements[obj.element_id].properties.get("component", "")
        if comp and comp == def_name:
            comp = ""

        base = name
        index = None
        m = re.match(r"^(.*)\[(\d+)\]$", name)
        if m:
            base = m.group(1)
            index = int(m.group(2))
            base = f"{base} {index}"

        label = base
        if def_name:
            if mult:
                if ".." in mult:
                    upper = mult.split("..", 1)[1] or "*"
                    disp = f"{index or 1}..{upper}"
                elif mult == "*":
                    disp = f"{index or 1}..*"
                else:
                    disp = f"{index or 1}..{mult}"
                def_part = f"{def_name} [{disp}]"
            else:
                def_part = def_name
            if comp:
                def_part = f"{comp} / {def_part}"
            if label and def_part != label:
                label = f"{label} : {def_part}"
            elif not label:
                label = f" : {def_part}"

        return label

    def _get_part_key(self, obj: SysMLObject) -> str:
        """Return canonical key for identifying ``obj`` regardless of renaming."""
        repo = self.repo
        def_id = obj.properties.get("definition")
        if not def_id and obj.element_id and obj.element_id in repo.elements:
            def_id = repo.elements[obj.element_id].properties.get("definition")
        name = ""
        if def_id and def_id in repo.elements:
            name = repo.elements[def_id].name or def_id
        else:
            name = self._get_part_name(obj)
        return _part_prop_key(name)

    def add_contained_parts(self) -> None:
        repo = self.repo
        block_id = next((eid for eid, did in repo.element_diagrams.items() if did == self.diagram_id), None)
        if not block_id or block_id not in repo.elements:
            messagebox.showinfo("Add Contained Parts", "No block is linked to this diagram")
            return
        block = repo.elements[block_id]
        diag = repo.diagrams.get(self.diagram_id)

        # inherit and sync aggregation/composite parts
        added_parent = inherit_father_parts(repo, diag) if diag else []
        for data in added_parent:
            self.objects.append(SysMLObject(**data))
        added_agg = _sync_ibd_aggregation_parts(repo, block_id, app=getattr(self, "app", None))
        added_comp = _sync_ibd_composite_parts(repo, block_id, app=getattr(self, "app", None))
        for data in added_agg + added_comp:
            self.objects.append(SysMLObject(**data))

        ra_name = block.properties.get("analysis", "")
        analyses = getattr(self.app, "reliability_analyses", [])
        ra_map = {ra.name: ra for ra in analyses}
        ra = ra_map.get(ra_name)
        if ra_name and (not ra or not ra.components):
            messagebox.showinfo("Add Contained Parts", "Analysis has no components")
            return
        comps = list(ra.components) if ra_name and ra and ra.components else []

        # existing parts on the diagram
        visible: dict[str, list[SysMLObject]] = {}
        hidden: dict[str, list[SysMLObject]] = {}
        def_objs: dict[str, list[SysMLObject]] = {}
        for obj in self.objects:
            if obj.obj_type != "Part":
                continue
            key = getattr(self, "_get_part_key", self._get_part_name)(obj)
            def_id = obj.properties.get("definition")
            def_objs.setdefault(def_id or "", []).append(obj)
            if getattr(obj, "hidden", False):
                hidden.setdefault(key, []).append(obj)
            else:
                visible.setdefault(key, []).append(obj)

        part_names = [n.strip() for n in block.properties.get("partProperties", "").split(",") if n.strip()]
        comp_names = [c.name for c in comps]
        prop_map = { _part_prop_key(n): n for n in part_names }
        all_keys = set(prop_map) | set(visible) | set(hidden) | { _part_prop_key(n) for n in comp_names }
        display_map: dict[str, str] = {}
        for key in all_keys:
            if key in prop_map:
                display_map[key] = prop_map[key]
            elif key in visible:
                display_map[key] = self._get_part_name(visible[key][0])
            elif key in hidden:
                display_map[key] = self._get_part_name(hidden[key][0])
            else:
                comp = next((c for c in comps if _part_prop_key(c.name) == key), None)
                display_map[key] = comp.name if comp else key

        names_list = [display_map[k] for k in sorted(display_map)]
        visible_names = {display_map[k] for k in visible}
        hidden_names = {display_map[k] for k in hidden}

        placeholder_map: dict[str, tuple[str, str]] = {}
        for rel in repo.relationships:
            if rel.rel_type in ("Aggregation", "Composite Aggregation") and rel.source == block_id:
                mult = rel.properties.get("multiplicity", "")
                if not mult:
                    continue
                target = rel.target
                low, high = _parse_multiplicity_range(mult)
                expected = high if high is not None else low
                existing = def_objs.get(target, [])
                for i in range(len(existing), expected):
                    def_name = repo.elements[target].name or target
                    if ".." in mult:
                        upper = mult.split("..", 1)[1] or "*"
                        disp = f"{i+1}..{upper}"
                    elif mult == "*":
                        disp = f"{i+1}..*"
                    elif mult.isdigit() and mult == str(expected):
                        disp = mult
                    else:
                        disp = f"{i+1}..{mult}"
                    label = f" : {def_name} [{disp}]"
                    placeholder_map[label] = (target, mult)
                    names_list.append(label)

        dlg = SysMLObjectDialog.ManagePartsDialog(
            self, names_list, visible_names, hidden_names
        )
        selected = dlg.result
        if selected is None:
            # User cancelled the dialog -> keep current visibility unchanged
            return
        selected_keys = { _part_prop_key(n) for n in selected if n not in placeholder_map }
        selected_placeholders = [placeholder_map[n] for n in selected if n in placeholder_map]

        to_add_comps = [c for c in comps if _part_prop_key(c.name) in selected_keys and _part_prop_key(c.name) not in visible and _part_prop_key(c.name) not in hidden]
        to_add_names = [n for n in part_names if _part_prop_key(n) in selected_keys and _part_prop_key(n) not in visible and _part_prop_key(n) not in hidden]
        added_ph: list[dict] = []
        for def_id, mult in selected_placeholders:
            added_ph.extend(
                add_multiplicity_parts(
                    repo, block_id, def_id, mult, count=1, app=getattr(self, "app", None)
                )
            )
        if added_ph and not self.app:
            for data in added_ph:
                if not any(o.obj_id == data["obj_id"] for o in self.objects):
                    self.objects.append(SysMLObject(**data))

        for key, objs in visible.items():
            if key not in selected_keys:
                for obj in objs:
                    obj.hidden = True
        for key, objs in hidden.items():
            if key in selected_keys:
                for obj in objs:
                    obj.hidden = False

        base_x = 50.0
        base_y = 50.0
        offset = 60.0
        added = []
        for idx, comp in enumerate(to_add_comps):
            elem = repo.create_element(
                "Part",
                name=comp.name,
                properties={
                    "component": comp.name,
                    "fit": f"{comp.fit:.2f}",
                    "qualification": comp.qualification,
                    "failureModes": self._get_failure_modes(comp.name),
                },
                owner=repo.root_package.elem_id,
            )
            repo.add_element_to_diagram(self.diagram_id, elem.elem_id)
            obj = SysMLObject(
                _get_next_id(),
                "Part",
                base_x,
                base_y + offset * idx,
                element_id=elem.elem_id,
                properties=elem.properties.copy(),
            )
            diag.objects.append(obj.__dict__)
            self.objects.append(obj)
            added.append(comp.name)

        if to_add_names:
            # Directly sync new part property parts to the repository without
            # updating windows. We then insert the returned objects ourselves so
            # we can ensure they are visible immediately.
            added_props = _sync_ibd_partproperty_parts(
                repo, block_id, names=to_add_names, app=None, hidden=True
            )
            for data in added_props:
                data["hidden"] = False
                # Avoid duplicates if the sync function already populated this
                # window via the application.
                if not any(o.obj_id == data["obj_id"] for o in self.objects):
                    self.objects.append(SysMLObject(**data))

        if added:
            names = [
                n.strip()
                for n in block.properties.get("partProperties", "").split(",")
                if n.strip()
            ]
            for name in added:
                if name not in names:
                    names.append(name)
            joined = ", ".join(names)
            block.properties["partProperties"] = joined
            inherit_block_properties(repo, block_id)
            joined = repo.elements[block_id].properties["partProperties"]
            for d in repo.diagrams.values():
                for o in getattr(d, "objects", []):
                    if o.get("element_id") == block_id:
                        o.setdefault("properties", {})["partProperties"] = joined

        # enforce multiplicity for aggregated parts
        added_mult = _enforce_ibd_multiplicity(
            repo, block_id, app=getattr(self, "app", None)
        )
        if added_mult and not self.app:
            for data in added_mult:
                if not any(o.obj_id == data["obj_id"] for o in self.objects):
                    self.objects.append(SysMLObject(**data))

        boundary = getattr(self, "get_ibd_boundary", lambda: None)()
        if boundary:
            ensure_boundary_contains_parts(boundary, self.objects)

        self.redraw()
        self._sync_to_repository()
        if self.app:
            self.app.update_views()


class ControlFlowDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None, history=None):
        tools = [
            "Existing Element",
            "Control Action",
            "Feedback",
            "STPA Analysis",
        ]
        super().__init__(master, "Control Flow Diagram", tools, diagram_id, app=app, history=history)

    def select_tool(self, tool):
        if tool == "STPA Analysis":
            repo = SysMLRepository.get_instance()
            self.app.open_stpa_window()
            diag_id = self.diagram_id
            doc = next((d for d in self.app.stpa_docs if d.diagram == diag_id), None)
            if not doc:
                diag = repo.diagrams.get(diag_id)
                name = diag.name or diag.diag_id if diag else f"STPA {len(self.app.stpa_docs)+1}"
                doc = StpaDoc(name, diag_id, [])
                self.app.stpa_docs.append(doc)
            self.app.active_stpa = doc
            self.app.stpa_entries = doc.entries
            if hasattr(self.app, "_stpa_window"):
                self.app._stpa_window.refresh_docs()
                self.app._stpa_window.doc_var.set(doc.name)
                self.app._stpa_window.select_doc()
            return
        super().select_tool(tool)


class NewDiagramDialog(simpledialog.Dialog):
    """Dialog to create a new diagram and assign a name and type."""

    def __init__(self, master):
        self.name = ""
        self.diag_type = "Use Case Diagram"
        super().__init__(master, title="New Diagram")

    def body(self, master):
        ttk.Label(master, text="Name:").grid(row=0, column=0, padx=4, pady=4, sticky="e")
        self.name_var = tk.StringVar()
        ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(master, text="Type:").grid(row=1, column=0, padx=4, pady=4, sticky="e")
        self.type_var = tk.StringVar(value=self.diag_type)
        ttk.Combobox(
            master,
            textvariable=self.type_var,
                values=[
                    "Use Case Diagram",
                    "Activity Diagram",
                    "BPMN Diagram",
                    "Block Diagram",
                    "Internal Block Diagram",
                    "Control Flow Diagram",
                ],
        ).grid(row=1, column=1, padx=4, pady=4)

    def apply(self):
        self.name = self.name_var.get()
        self.diag_type = self.type_var.get()


class DiagramPropertiesDialog(simpledialog.Dialog):
    """Dialog to edit a diagram's metadata."""

    def __init__(self, master, diagram: SysMLDiagram):
        self.diagram = diagram
        self.added_parts: list[dict] = []
        super().__init__(master, title="Diagram Properties")

    def body(self, master):
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self.name_var = tk.StringVar(value=self.diagram.name)
        ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, padx=4, pady=2)
        ttk.Label(master, text="Description:").grid(row=1, column=0, sticky="e", padx=4, pady=2)
        self.desc_var = tk.StringVar(value=getattr(self.diagram, "description", ""))
        ttk.Entry(master, textvariable=self.desc_var).grid(row=1, column=1, padx=4, pady=2)
        ttk.Label(master, text="Color:").grid(row=2, column=0, sticky="e", padx=4, pady=2)
        self.color_var = tk.StringVar(value=getattr(self.diagram, "color", "#FFFFFF"))
        ttk.Entry(master, textvariable=self.color_var).grid(row=2, column=1, padx=4, pady=2)
        if self.diagram.diag_type == "Internal Block Diagram":
            repo = SysMLRepository.get_instance()
            blocks = [e for e in repo.elements.values() if e.elem_type == "Block"]
            idmap = {b.name or b.elem_id: b.elem_id for b in blocks}
            ttk.Label(master, text="Father:").grid(row=3, column=0, sticky="e", padx=4, pady=2)
            self.father_map = idmap
            cur_id = getattr(self.diagram, "father", "")
            cur_name = next((n for n, i in idmap.items() if i == cur_id), "")
            self.father_var = tk.StringVar(value=cur_name)
            ttk.Combobox(master, textvariable=self.father_var, values=list(idmap.keys())).grid(
                row=3, column=1, padx=4, pady=2
            )
        else:
            self.father_map = {}
            self.father_var = tk.StringVar()

    def apply(self):
        self.diagram.name = self.name_var.get()
        self.diagram.description = self.desc_var.get()
        self.diagram.color = self.color_var.get()
        if self.diagram.diag_type == "Internal Block Diagram":
            father_id = self.father_map.get(self.father_var.get())
            repo = SysMLRepository.get_instance()
            self.added_parts = set_ibd_father(
                repo, self.diagram, father_id, app=getattr(self.master, "app", None)
            )
            self.added_parts.extend(inherit_father_parts(repo, self.diagram))


class PackagePropertiesDialog(simpledialog.Dialog):
    """Dialog to edit a package's name."""

    def __init__(self, master, package: SysMLElement):
        self.package = package
        super().__init__(master, title="Package Properties")

    def body(self, master):
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self.name_var = tk.StringVar(value=self.package.name)
        ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, padx=4, pady=2)

    def apply(self):
        self.package.name = self.name_var.get()


class ElementPropertiesDialog(simpledialog.Dialog):
    """Dialog to edit a generic element's name and properties."""

    def __init__(self, master, element: SysMLElement):
        self.element = element
        super().__init__(master, title=f"{element.elem_type} Properties")

    def body(self, master):
        ttk.Label(master, text="Name:").grid(row=0, column=0, sticky="e", padx=4, pady=2)
        self.name_var = tk.StringVar(value=self.element.name)
        ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, padx=4, pady=2)
        self.entries = {}
        key = f"{self.element.elem_type.replace(' ', '')}Usage"
        row = 1
        for prop in SYSML_PROPERTIES.get(key, []):
            if prop == "partProperties":
                # Part properties are configured through dedicated dialogs.
                # Skip them in the generic properties window.
                continue
            ttk.Label(master, text=f"{prop}:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
            var = tk.StringVar(value=self.element.properties.get(prop, ""))
            ttk.Entry(master, textvariable=var).grid(row=row, column=1, padx=4, pady=2)
            self.entries[prop] = var
            row += 1

    def apply(self):
        repo = SysMLRepository.get_instance()
        new_name = self.name_var.get()
        if self.element.elem_type == "Block":
            rename_block(repo, self.element.elem_id, new_name)
        else:
            self.element.name = new_name
        for prop, var in self.entries.items():
            self.element.properties[prop] = var.get()


class ArchitectureManagerDialog(tk.Frame):
    """Manage packages and diagrams in a hierarchical tree."""

    def __init__(self, master, app=None):
        if isinstance(master, tk.Toplevel):
            container = master
        else:
            container = master
        super().__init__(container)
        self.app = app
        if isinstance(master, tk.Toplevel):
            master.title("AutoML Explorer")
            master.geometry("350x400")
            self.pack(fill=tk.BOTH, expand=True)
        self.repo = SysMLRepository.get_instance()

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        self.tree = ttk.Treeview(tree_frame)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        # simple icons to visually distinguish packages, diagrams and objects
        self.pkg_icon = self._create_icon("folder", "#b8860b")
        self.diagram_icons = {
            "Use Case Diagram": self._create_icon("circle", "blue"),
            "Activity Diagram": self._create_icon("arrow", "green"),
            "BPMN Diagram": self._create_icon("arrow", "green"),
            "Block Diagram": self._create_icon("rect", "orange"),
            "Internal Block Diagram": self._create_icon("nested", "purple"),
        }
        self.elem_icons = {
            "Actor": self._create_icon("circle"),
            "Use Case": self._create_icon("circle"),
            "Block": self._create_icon("rect"),
            "Part": self._create_icon("rect"),
            "Port": self._create_icon("circle"),
        }
        self.default_diag_icon = self._create_icon("rect")
        self.default_elem_icon = self._create_icon("rect")
        btns = ttk.Frame(self)
        btns.pack(fill=tk.X, padx=4, pady=4)
        ttk.Button(btns, text="Open", command=self.open).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Properties", command=self.properties).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="New Package", command=self.new_package).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="New Diagram", command=self.new_diagram).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Cut", command=self.cut).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Paste", command=self.paste).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Delete", command=self.delete).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Close", command=self.destroy).pack(side=tk.RIGHT, padx=2)
        self.populate()
        self.tree.bind("<Button-3>", self.on_right_click)
        self.tree.bind("<Double-1>", self.on_double)
        self.tree.bind("<ButtonPress-1>", self.on_drag_start)
        self.tree.bind("<B1-Motion>", self.on_drag_motion)
        self.tree.bind("<ButtonRelease-1>", self.on_drag_release)
        self.bind("<FocusIn>", lambda _e: self.populate())
        self.drag_item = None
        self.cut_item = None

    def populate(self):
        """Populate the tree view with packages, diagrams and elements."""
        self.tree.delete(*self.tree.get_children())
        from collections import defaultdict

        rel_children = defaultdict(list)
        for rel in self.repo.relationships:
            rel_children[rel.source].append((rel.rel_id, rel.target, rel.rel_type))

        visited: set[str] = set()

        # collect all elements that already appear on a diagram so they don't
        # show up twice in the hierarchy
        diagram_elems = {
            elem_id
            for diag in self.repo.diagrams.values()
            for elem_id in (
                list(getattr(diag, "elements", []))
                + [
                    getattr(o, "element_id", o.get("element_id"))
                    for o in getattr(diag, "objects", [])
                    if getattr(o, "element_id", o.get("element_id"))
                ]
            )
        }

        def add_elem(elem_id: str, parent: str):
            if elem_id in visited:
                return
            visited.add(elem_id)
            elem = self.repo.elements[elem_id]
            icon = self.elem_icons.get(elem.elem_type, self.default_elem_icon)
            if self.tree.exists(elem_id):
                node = elem_id
            else:
                node = self.tree.insert(
                    parent,
                    "end",
                    iid=elem_id,
                    text=elem.name or elem_id,
                    values=(elem.elem_type,),
                    image=icon,
                )
            for rel_id, tgt_id, rtype in rel_children.get(elem_id, []):
                if tgt_id in self.repo.elements:
                    rel_iid = f"rel_{rel_id}"
                    if self.tree.exists(rel_iid):
                        rel_node = rel_iid
                    else:
                        rel_node = self.tree.insert(
                            node, "end", iid=rel_iid, text=rtype, values=("Relationship",)
                        )
                    add_elem(tgt_id, rel_node)
            visited.remove(elem_id)

        root_pkg = getattr(self.repo, "root_package", None)
        if not root_pkg or root_pkg.elem_id not in self.repo.elements:
            # ensure a valid root package exists
            self.repo.root_package = self.repo.create_element("Package", name="Root")
            root_pkg = self.repo.root_package

        def add_pkg(pkg_id, parent=""):
            pkg = self.repo.elements[pkg_id]
            if self.tree.exists(pkg_id):
                node = pkg_id
            else:
                node = self.tree.insert(
                    parent,
                    "end",
                    iid=pkg_id,
                    text=pkg.name or pkg_id,
                    open=True,
                    image=self.pkg_icon,
                )
            for p in self.repo.elements.values():
                if p.elem_type == "Package" and p.owner == pkg_id:
                    add_pkg(p.elem_id, node)
            for e in self.repo.elements.values():
                if (
                    e.owner == pkg_id
                    and e.elem_type not in ("Package", "Part")
                    and e.name
                    and e.elem_id not in diagram_elems
                ):
                    add_elem(e.elem_id, node)
            for d in self.repo.diagrams.values():
                if d.package == pkg_id and "safety-management" not in getattr(d, "tags", []):
                    label = d.name or d.diag_id
                    icon = self.diagram_icons.get(d.diag_type, self.default_diag_icon)
                    diag_iid = f"diag_{d.diag_id}"
                    if self.tree.exists(diag_iid):
                        diag_node = diag_iid
                    else:
                        diag_node = self.tree.insert(
                            node,
                            "end",
                            iid=diag_iid,
                            text=label,
                            values=(d.diag_type,),
                            image=icon,
                        )
                    objs = sorted(
                        d.objects,
                        key=lambda o: (
                            1 if getattr(o, "obj_type", o.get("obj_type")) == "Port" else 0
                        ),
                    )
                    for obj in objs:
                        props = getattr(obj, "properties", obj.get("properties", {}))
                        name = props.get("name", getattr(obj, "obj_type", obj.get("obj_type")))
                        oid = getattr(obj, "obj_id", obj.get("obj_id"))
                        otype = getattr(obj, "obj_type", obj.get("obj_type"))
                        icon = self.elem_icons.get(otype, self.default_elem_icon)
                        parent_node = diag_node
                        if (
                            otype == "Port"
                            and props.get("parent")
                            and self.tree.exists(f"obj_{d.diag_id}_{props.get('parent')}")
                        ):
                            parent_node = f"obj_{d.diag_id}_{props.get('parent')}"
                        obj_iid = f"obj_{d.diag_id}_{oid}"
                        if self.tree.exists(obj_iid):
                            continue
                        self.tree.insert(
                            parent_node,
                            "end",
                            iid=obj_iid,
                            text=name,
                            values=(obj.get("obj_type"),),
                            image=icon,
                        )

        add_pkg(root_pkg.elem_id)
        if self.app:
            self.app.update_views()

    def selected(self):
        sel = self.tree.selection()
        if sel:
            return sel[0]
        item = self.tree.focus()
        return item if item else None

    def open(self):
        item = self.selected()
        if not item:
            return
        if item.startswith("diag_"):
            self.open_diagram(item[5:])
        elif item.startswith("obj_"):
            diag_id, oid = item[4:].split("_", 1)
            win = self.open_diagram(diag_id)
            if win:
                for o in win.objects:
                    if o.obj_id == int(oid):
                        win.selected_obj = o
                        win.redraw()
                        break

    def on_double(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            if item.startswith("diag_"):
                self.open_diagram(item[5:])
            elif item.startswith("obj_"):
                self.open()

    def open_diagram(self, diag_id: str):
        diag = self.repo.diagrams.get(diag_id)
        if not diag:
            return None

        # If an application instance is available, open the diagram using
        # the main document notebook so duplicate tabs are avoided.
        if self.app and hasattr(self.app, "diagram_tabs"):
            idx = next(
                (i for i, d in enumerate(self.app.arch_diagrams) if d.diag_id == diag_id),
                -1,
            )
            if idx != -1:
                self.app.open_arch_window(idx)
                tab = self.app.diagram_tabs.get(diag_id)
                if tab and tab.winfo_exists():
                    for child in tab.winfo_children():
                        if isinstance(child, SysMLDiagramWindow):
                            return child
                return None

        master = self.master if self.master else self
        win = None
        if diag.diag_type == "Use Case Diagram":
            win = UseCaseDiagramWindow(master, self.app, diagram_id=diag_id)
        elif diag.diag_type == "Activity Diagram":
            win = ActivityDiagramWindow(master, self.app, diagram_id=diag_id)
        elif diag.diag_type == "BPMN Diagram":
            win = BPMNDiagramWindow(master, self.app, diagram_id=diag_id)
        elif diag.diag_type == "Block Diagram":
            win = BlockDiagramWindow(master, self.app, diagram_id=diag_id)
        elif diag.diag_type == "Internal Block Diagram":
            win = InternalBlockDiagramWindow(master, self.app, diagram_id=diag_id)
        return win

    def new_package(self):
        item = self.selected() or self.repo.root_package.elem_id
        if item.startswith("diag_"):
            item = self.repo.diagrams[item[5:]].package
        name = simpledialog.askstring("New Package", "Name:")
        if name:
            self.repo.create_package(name, parent=item)
            self.populate()

    def new_diagram(self):
        item = self.selected() or self.repo.root_package.elem_id
        if item.startswith("diag_"):
            item = self.repo.diagrams[item[5:]].package
        dlg = NewDiagramDialog(self)
        if dlg.name:
            self.repo.create_diagram(dlg.diag_type, name=dlg.name, package=item)
            self.populate()

    def delete(self):
        item = self.selected()
        if not item:
            return
        if item.startswith("diag_"):
            self.repo.delete_diagram(item[5:])
        elif item.startswith("obj_"):
            diag_id, oid = item[4:].split("_", 1)
            diag = self.repo.diagrams.get(diag_id)
            if diag:
                diag.objects = [o for o in diag.objects if str(o.get("obj_id")) != oid]
        else:
            if item == self.repo.root_package.elem_id:
                messagebox.showerror("Delete", "Cannot delete the root package.")
            else:
                self.repo.delete_package(item)
        self.populate()

    def properties(self):
        item = self.selected()
        if not item:
            return
        if item.startswith("diag_"):
            diag = self.repo.diagrams.get(item[5:])
            if diag:
                DiagramPropertiesDialog(self, diag)
                self.populate()
        elif item.startswith("obj_"):
            diag_id, oid = item[4:].split("_", 1)
            diag = self.repo.diagrams.get(diag_id)
            if diag:
                obj_data = next(
                    (o for o in diag.objects if str(o.get("obj_id")) == oid),
                    None,
                )
                if obj_data:
                    obj = SysMLObject(**obj_data)
                    SysMLObjectDialog(self, obj)
                    diag.objects = [
                        obj.__dict__ if str(o.get("obj_id")) == oid else o for o in diag.objects
                    ]
                self.populate()
        else:
            elem = self.repo.elements.get(item)
            if elem:
                if elem.elem_type == "Package":
                    PackagePropertiesDialog(self, elem)
                else:
                    ElementPropertiesDialog(self, elem)
                self.populate()

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self.tree.selection_set(item)
        menu = tk.Menu(self.tree, tearoff=0)
        menu.add_command(label="Rename", command=lambda: self.rename_item(item))
        menu.tk_popup(event.x_root, event.y_root)

    def rename_item(self, item=None):
        item = item or self.selected()
        if not item:
            return
        if item.startswith("diag_"):
            diag = self.repo.diagrams.get(item[5:])
            if diag and "safety-management" in getattr(diag, "tags", []):
                return
            if diag:
                name = simpledialog.askstring("Rename Diagram", "Name:", initialvalue=diag.name)
                if name:
                    diag.name = name
                    self.populate()
        elif item.startswith("obj_"):
            return
        else:
            elem = self.repo.elements.get(item)
            if elem:
                name = simpledialog.askstring("Rename", "Name:", initialvalue=elem.name)
                if name:
                    name = self.repo.ensure_unique_element_name(name, elem.elem_id)
                    if elem.elem_type == "Block":
                        rename_block(self.repo, elem.elem_id, name)
                    else:
                        elem.name = name
                    self.populate()

    # ------------------------------------------------------------------
    # Cut/Paste and Drag & Drop Handling
    # ------------------------------------------------------------------
    def cut(self):
        item = self.selected()
        if item:
            self.cut_item = item

    def paste(self):
        if not self.cut_item:
            return
        target = self.selected() or self.repo.root_package.elem_id
        if target.startswith("diag_"):
            target = self.repo.diagrams[target[5:]].package
        self._move_item(self.cut_item, target)
        self.cut_item = None
        self.populate()

    def on_drag_start(self, event):
        self.drag_item = self.tree.identify_row(event.y)
        if self.drag_item:
            self.tree.selection_set(self.drag_item)

    def on_drag_motion(self, _event):
        pass

    def on_drag_release(self, event):
        if not self.drag_item:
            return
        target = self.tree.identify_row(event.y)
        if not target:
            self.drag_item = None
            return
        if target == self.drag_item:
            self.drag_item = None
            return
        if self.drag_item.startswith("obj_"):
            messagebox.showerror("Drop Error", "Objects cannot be moved in the explorer.")
            self.drag_item = None
            return
        if target.startswith("obj_"):
            messagebox.showerror("Drop Error", "Cannot drop items on an object.")
            self.drag_item = None
            return
        region = self.tree.identify_region(event.x, event.y)
        if region in ("separator", "nothing"):
            parent = self.tree.parent(target)
            index = self.tree.index(target)
            self.tree.move(self.drag_item, parent, index)
            self._move_item(self.drag_item, parent)
        else:
            if target.startswith("diag_"):
                diag = self.repo.diagrams.get(target[5:])
                self._drop_on_diagram(self.drag_item, diag)
            else:
                self.tree.move(self.drag_item, target, "end")
                self._move_item(self.drag_item, target)
        self.drag_item = None
        self.populate()

    def _move_item(self, item, new_parent):
        if item.startswith("obj_") or new_parent.startswith("obj_"):
            messagebox.showerror("Drop Error", "Cannot drop items on an object.")
            return
        if new_parent == "":
            new_parent = self.repo.root_package.elem_id
        if item.startswith("diag_"):
            self.repo.diagrams[item[5:]].package = new_parent
        else:
            elem = self.repo.elements.get(item)
            if elem:
                elem.owner = new_parent

    def _drop_on_diagram(self, elem_id, diagram):
        repo = self.repo
        if elem_id.startswith("obj_"):
            messagebox.showerror("Drop Error", "Objects cannot be dropped on a diagram.")
            return
        # Dropping a diagram onto an Activity or BPMN Diagram creates a behavior reference
        if elem_id.startswith("diag_"):
            src_diag = repo.diagrams.get(elem_id[5:])
            if src_diag and diagram.diag_type == "Activity Diagram" and src_diag.diag_type in (
                "Activity Diagram",
                "Internal Block Diagram",
                "BPMN Diagram",
            ):
                elem_type = "Action" if diagram.diag_type == "BPMN Diagram" else "CallBehaviorAction"
                act = repo.create_element(
                    elem_type, name=src_diag.name, owner=diagram.package
                )
                repo.add_element_to_diagram(diagram.diag_id, act.elem_id)
                props = {"name": src_diag.name}
                if src_diag.diag_type == "Internal Block Diagram":
                    props["view"] = src_diag.diag_id
                    repo.link_diagram(act.elem_id, None)
                else:
                    repo.link_diagram(act.elem_id, src_diag.diag_id)
                obj = SysMLObject(
                    _get_next_id(),
                    elem_type,
                    50.0,
                    50.0,
                    element_id=act.elem_id,
                    properties=props,
                )
                diagram.objects.append(obj.__dict__)
                return
            if (
                src_diag
                and diagram.diag_type == "BPMN Diagram"
                and src_diag.diag_type == "BPMN Diagram"
            ):
                act = repo.create_element("Action", name=src_diag.name, owner=diagram.package)
                repo.add_element_to_diagram(diagram.diag_id, act.elem_id)
                props = {"name": src_diag.name}
                repo.link_diagram(act.elem_id, src_diag.diag_id)
                obj = SysMLObject(
                    _get_next_id(),
                    "Action",
                    50.0,
                    50.0,
                    element_id=act.elem_id,
                    properties=props,
                )
                diagram.objects.append(obj.__dict__)
                return
            messagebox.showerror("Drop Error", "This item cannot be dropped on that diagram.")
            return

        allowed = diagram.diag_type == "Block Diagram"
        if allowed and repo.elements[elem_id].elem_type == "Package":
            block = repo.create_element("Block", name=repo.elements[elem_id].name, owner=elem_id)
            repo.add_element_to_diagram(diagram.diag_id, block.elem_id)
            obj = SysMLObject(_get_next_id(), "Block", 50.0, 50.0, element_id=block.elem_id)
            diagram.objects.append(obj.__dict__)
        else:
            messagebox.showerror("Drop Error", "This item cannot be dropped on that diagram.")

    def _create_icon(self, shape: str, color: str = "black") -> tk.PhotoImage:
        """Return a simple 16x16 PhotoImage representing the given shape."""
        size = 16
        img = tk.PhotoImage(width=size, height=size)
        img.put("white", to=(0, 0, size - 1, size - 1))
        c = color
        if shape == "circle":
            r = size // 2 - 2
            cx = cy = size // 2
            for y in range(size):
                for x in range(size):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                        img.put(c, (x, y))
        elif shape == "arrow":
            mid = size // 2
            for x in range(2, mid + 1):
                img.put(c, to=(x, mid - 1, x + 1, mid + 1))
            for i in range(4):
                img.put(c, to=(mid + i, mid - 2 - i, mid + i + 1, mid - i))
                img.put(c, to=(mid + i, mid + i, mid + i + 1, mid + 2 + i))
        elif shape == "rect":
            for x in range(3, size - 3):
                img.put(c, (x, 3))
                img.put(c, (x, size - 4))
            for y in range(3, size - 3):
                img.put(c, (3, y))
                img.put(c, (size - 4, y))
        elif shape == "nested":
            for x in range(1, size - 1):
                img.put(c, (x, 1))
                img.put(c, (x, size - 2))
            for y in range(1, size - 1):
                img.put(c, (1, y))
                img.put(c, (size - 2, y))
            for x in range(5, size - 5):
                img.put(c, (x, 5))
                img.put(c, (x, size - 6))
            for y in range(5, size - 5):
                img.put(c, (5, y))
                img.put(c, (size - 6, y))
        elif shape == "folder":
            for x in range(1, size - 1):
                img.put(c, (x, 4))
                img.put(c, (x, size - 2))
            for y in range(4, size - 1):
                img.put(c, (1, y))
                img.put(c, (size - 2, y))
            for x in range(3, size - 3):
                img.put(c, (x, 2))
            img.put(c, to=(1, 3, size - 2, 4))
        else:
            img.put(c, to=(2, 2, size - 2, size - 2))
        return img