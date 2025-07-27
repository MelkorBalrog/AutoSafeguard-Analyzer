# Author: Miguel Marina <karel.capek.robotics@gmail.com>
import tkinter as tk
import tkinter.font as tkFont
from tkinter import ttk, simpledialog, messagebox
import json
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Tuple

from sysml.sysml_repository import SysMLRepository, SysMLDiagram, SysMLElement

from sysml.sysml_spec import SYSML_PROPERTIES
from analysis.models import global_requirements, ASIL_ORDER

# ---------------------------------------------------------------------------
# Appearance customization
# ---------------------------------------------------------------------------
# Basic fill colors for different AutoML object types. This provides a simple
# color palette so diagrams appear less bland and more professional.
OBJECT_COLORS: dict[str, str] = {
    "Actor": "#E0F7FA",
    "Use Case": "#FFF3E0",
    "System Boundary": "#ECEFF1",
    "Action Usage": "#E8F5E9",
    "Action": "#E8F5E9",
    "CallBehaviorAction": "#E8F5E9",
    "Part": "#FFFDE7",
    "Port": "#F3E5F5",
    "Block": "#E0E0E0",
    "Decision": "#E1F5FE",
    "Merge": "#E1F5FE",
    # Fork and Join bars remain black so are not listed here
}


_next_obj_id = 1


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
    # also follow Association relationships
    for rel in repo.relationships:
        if rel.rel_type != "Association":
            continue
        if rel.source == block_id and rel.target in repo.elements:
            parents.add(rel.target)
        elif rel.target == block_id and rel.source in repo.elements:
            parents.add(rel.source)
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
                [p.strip() for p in elem.properties.get("partProperties", "").split(",") if p.strip()]
            )
        parts.extend(_collect_parent_parts(repo, parent, visited))
    seen = []
    for p in parts:
        if p not in seen:
            seen.append(p)
    return seen


def extend_block_parts_with_parents(repo: SysMLRepository, block_id: str) -> None:
    """Merge parent block parts into the given block's ``partProperties``."""
    block = repo.elements.get(block_id)
    if not block:
        return
    names = [p.strip() for p in block.properties.get("partProperties", "").split(",") if p.strip()]
    for p in _collect_parent_parts(repo, block_id):
        if p not in names:
            names.append(p)
    joined = ", ".join(names)
    block.properties["partProperties"] = joined
    for d in repo.diagrams.values():
        for o in getattr(d, "objects", []):
            if o.get("element_id") == block_id:
                o.setdefault("properties", {})["partProperties"] = joined


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
    part_ids = {o.obj_id for o in objs if o.obj_type == "Part"}
    filtered: List[SysMLObject] = []
    for o in objs:
        if o.obj_type == "Port":
            pid = o.properties.get("parent")
            if not pid or int(pid) not in part_ids:
                continue
        filtered.append(o)
    objs[:] = filtered


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
    plist = ", ".join(
        f"{p.name}: {p.type}" if p.type else p.name for p in op.parameters
    )
    ret = f" : {op.return_type}" if op.return_type else ""
    return f"{op.name}({plist}){ret}"


def operations_to_json(ops: List[OperationDefinition]) -> str:
    return json.dumps([asdict(o) for o in ops])


@dataclass
class DiagramConnection:
    src: int
    dst: int
    conn_type: str
    style: str = "Straight"  # Straight, Squared, Custom
    points: List[Tuple[float, float]] = field(default_factory=list)
    src_pos: Tuple[float, float] | None = None  # relative anchor (x,y)
    dst_pos: Tuple[float, float] | None = None


class SysMLDiagramWindow(tk.Frame):
    """Base frame for AutoML diagrams with zoom and pan support."""

    def __init__(self, master, title, tools, diagram_id: str | None = None, app=None):
        super().__init__(master)
        self.app = app
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
        else:
            # When embedded in another window, provide a small X button so
            # the user can close the frame.
            close_btn = ttk.Button(self, text="x", width=2, command=self.on_close)
            close_btn.place(relx=1.0, x=-4, y=4, anchor="ne")

        # Load any saved objects and connections for this diagram
        self.objects: List[SysMLObject] = []
        for data in getattr(diagram, "objects", []):
            if "requirements" not in data:
                data["requirements"] = []
            self.objects.append(SysMLObject(**data))
        self.sort_objects()
        self.connections: List[DiagramConnection] = [
            DiagramConnection(**data) for data in getattr(diagram, "connections", [])
        ]
        if self.objects:
            global _next_obj_id
            _next_obj_id = max(o.obj_id for o in self.objects) + 1

        self.zoom = 1.0
        self.font = tkFont.Font(family="Arial", size=int(8 * self.zoom))
        self.current_tool = None
        self.start = None
        self.selected_obj: SysMLObject | None = None
        self.selected_conn: DiagramConnection | None = None
        self.drag_offset = (0, 0)
        self.dragging_point_index: int | None = None
        self.dragging_endpoint: str | None = None  # "src" or "dst"
        self.conn_drag_offset: tuple[float, float] | None = None
        self.clipboard: SysMLObject | None = None
        self.resizing_obj: SysMLObject | None = None
        self.resize_edge: str | None = None
        self.temp_line_end: tuple[float, float] | None = None
        self.rc_dragged = False

        self.toolbox = ttk.Frame(self)
        self.toolbox.pack(side=tk.LEFT, fill=tk.Y)

        # Always provide a select tool
        tools = ["Select"] + tools
        for tool in tools:
            ttk.Button(self.toolbox, text=tool,
                       command=lambda t=tool: self.select_tool(t)).pack(
                fill=tk.X, padx=2, pady=2)

        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        if not isinstance(self.master, tk.Toplevel):
            # When a diagram is embedded in another window, add a small
            # close button over the canvas so the frame can be closed.
            self.close_btn = ttk.Button(self.canvas, text="x", width=2,
                                       command=self.on_close)
            self.close_btn.place(relx=1.0, x=-4, y=4, anchor="ne")
            self.close_btn.lift()

        self.canvas.bind("<Button-1>", self.on_left_press)
        self.canvas.bind("<B1-Motion>", self.on_left_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_left_release)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<ButtonPress-3>", self.on_rc_press)
        self.canvas.bind("<B3-Motion>", self.on_rc_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_rc_release)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Control-MouseWheel>", self.on_ctrl_mousewheel)
        self.bind("<Control-c>", self.copy_selected)
        self.bind("<Control-x>", self.cut_selected)
        self.bind("<Control-v>", self.paste_selected)
        self.bind("<Delete>", self.delete_selected)

        self.redraw()
        if not isinstance(self.master, tk.Toplevel):
            self.pack(fill=tk.BOTH, expand=True)

    def select_tool(self, tool):
        self.current_tool = tool
        self.start = None
        self.temp_line_end = None
        self.selected_obj = None
        self.selected_conn = None
        self.dragging_point_index = None
        self.dragging_endpoint = None
        self.conn_drag_offset = None
        cursor = "arrow"
        if tool != "Select":
            cursor = "crosshair" if tool in (
                "Association",
                "Include",
                "Extend",
                "Flow",
                "Connector",
            ) else "tcross"
        self.canvas.configure(cursor=cursor)

    # ------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------
    def validate_connection(self, src: SysMLObject, dst: SysMLObject, conn_type: str) -> tuple[bool, str]:
        """Return (valid, message) for a potential connection."""
        diag = self.repo.diagrams.get(self.diagram_id)
        diag_type = diag.diag_type if diag else ""

        if conn_type in ("Association", "Include", "Extend", "Flow", "Connector"):
            if src == dst:
                return False, "Cannot connect an element to itself"

        if diag_type == "Use Case Diagram":
            if conn_type == "Association":
                actors = {"Actor"}
                if not ((src.obj_type in actors and dst.obj_type == "Use Case") or (
                    dst.obj_type in actors and src.obj_type == "Use Case")):
                    return False, "Associations must connect an Actor and a Use Case"
            elif conn_type in ("Include", "Extend"):
                if src.obj_type != "Use Case" or dst.obj_type != "Use Case":
                    return False, f"{conn_type} relationships must connect two Use Cases"

        elif diag_type == "Block Diagram":
            if conn_type == "Association":
                if src.obj_type != "Block" or dst.obj_type != "Block":
                    return False, "Associations in block diagrams must connect Blocks"

        elif diag_type == "Internal Block Diagram":
            if conn_type == "Connector":
                if src.obj_type not in ("Port", "Part") or dst.obj_type not in (
                    "Port",
                    "Part",
                ):
                    return False, "Connectors must link Parts or Ports"

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

        return True, ""

    def on_left_press(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        obj = self.find_object(x, y)
        t = self.current_tool

        if t in ("Association", "Include", "Extend", "Flow", "Connector"):
            if self.start is None:
                if obj:
                    self.start = obj
                    # Do not highlight objects while adding a connection
                    self.selected_obj = None
                    self.temp_line_end = (x, y)
                    self.redraw()
            else:
                if obj and obj != self.start:
                    valid, msg = self.validate_connection(self.start, obj, t)
                    if valid:
                        conn = DiagramConnection(self.start.obj_id, obj.obj_id, t)
                        self.connections.append(conn)
                        src_id = self.start.element_id
                        dst_id = obj.element_id
                        if src_id and dst_id:
                            rel = self.repo.create_relationship(t, src_id, dst_id)
                            self.repo.add_relationship_to_diagram(self.diagram_id, rel.rel_id)
                        self._sync_to_repository()
                        ConnectionDialog(self, conn)
                    else:
                        messagebox.showwarning("Invalid Connection", msg)
                self.start = None
                self.temp_line_end = None
                self.selected_obj = None
                self.redraw()
        elif t and t != "Select":
            if t == "Port":
                parent_obj = obj if obj and obj.obj_type == "Part" else None
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
                    # Persist the port by adding it to the parent part's list
                    pname = new_obj.properties.get("name") or ""
                    ports = [p.strip() for p in parent_obj.properties.get("ports", "").split(",") if p.strip()]
                    if not pname:
                        base = "Port"
                        idx = 1
                        existing = set(ports)
                        existing.update(
                            p.properties.get("name")
                            for p in self.objects
                            if p.obj_type == "Port" and p.properties.get("parent") == str(parent_obj.obj_id)
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
                            self.repo.elements[parent_obj.element_id].properties["ports"] = parent_obj.properties["ports"]
            element.properties.update(new_obj.properties)
            self.ensure_text_fits(new_obj)
            if t == "System Boundary":
                self.objects.insert(0, new_obj)
            else:
                self.objects.append(new_obj)
            self.sort_objects()
            self._sync_to_repository()
            self.selected_obj = new_obj
            self.redraw()
        else:
            if obj:
                self.selected_obj = obj
                self.drag_offset = (x / self.zoom - obj.x, y / self.zoom - obj.y)
                self.resizing_obj = None
                self.resize_edge = self.hit_resize_handle(obj, x, y)
                if self.resize_edge:
                    self.resizing_obj = obj
                self.redraw()
            else:
                conn = self.find_connection(x, y)
                if conn:
                    if (event.state & 0x0001) and conn.style == "Custom":
                        conn.points.append((x / self.zoom, y / self.zoom))
                        self._sync_to_repository()
                    self.selected_conn = conn
                    self.selected_obj = None
                    self.dragging_point_index = None
                    self.dragging_endpoint = None
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
                            mx = conn.points[0][0] * self.zoom if conn.points else (
                                (src_obj.x + dst_obj.x) / 2 * self.zoom
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
                        elif abs(dxp - x) <= 6 and abs(dyp - y) <= 6:
                            self.dragging_endpoint = "dst"
                            self.conn_drag_offset = (x - dxp, y - dyp)
                    self.redraw()
                else:
                    # allow clicking on the resize handle even if outside the object
                    if self.selected_obj:
                        self.resize_edge = self.hit_resize_handle(self.selected_obj, x, y)
                        if self.resize_edge:
                            self.resizing_obj = self.selected_obj
                            return
                    self.selected_obj = None
                    self.selected_conn = None
                    self.resizing_obj = None
                    self.resize_edge = None
                    self.redraw()

    def on_left_drag(self, event):
        if self.start and self.current_tool in (
            "Association",
            "Include",
            "Extend",
            "Flow",
            "Connector",
        ):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.temp_line_end = (x, y)
            self.redraw()
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
                if obj:
                    ex, ey = self.edge_point(obj, x, y)
                    rx = (ex / self.zoom - obj.x) / (obj.width / 2)
                    ry = (ey / self.zoom - obj.y) / (obj.height / 2)
                    self.selected_conn.src_pos = (rx, ry)
            else:
                obj = self.get_object(self.selected_conn.dst)
                if obj:
                    ex, ey = self.edge_point(obj, x, y)
                    rx = (ex / self.zoom - obj.x) / (obj.width / 2)
                    ry = (ey / self.zoom - obj.y) / (obj.height / 2)
                    self.selected_conn.dst_pos = (rx, ry)
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
            if obj.obj_type in ("Initial", "Final"):
                return
            cx = obj.x * self.zoom
            cy = obj.y * self.zoom
            new_w = obj.width
            new_h = obj.height
            min_w, min_h = (10.0, 10.0)
            if obj.obj_type == "Block":
                min_w, min_h = self._min_block_size(obj)
            if "e" in self.resize_edge or "w" in self.resize_edge:
                desired_w = 2 * abs(x - cx) / self.zoom
                new_w = max(min_w, desired_w)
            if "n" in self.resize_edge or "s" in self.resize_edge:
                if obj.obj_type not in ("Fork", "Join"):
                    desired_h = 2 * abs(y - cy) / self.zoom
                    new_h = max(min_h, desired_h)
            if obj.obj_type in ("Initial", "Final"):
                size = max(new_w, new_h)
                new_w = new_h = size
            obj.width = new_w
            obj.height = new_h
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
            self.selected_obj.x = x / self.zoom - self.drag_offset[0]
            self.selected_obj.y = y / self.zoom - self.drag_offset[1]
            dx = self.selected_obj.x - old_x
            dy = self.selected_obj.y - old_y
            if self.selected_obj.obj_type == "Part":
                for p in self.objects:
                    if p.obj_type == "Port" and p.properties.get("parent") == str(self.selected_obj.obj_id):
                        p.x += dx
                        p.y += dy
                        self.snap_port_to_parent(p, self.selected_obj)
            if self.selected_obj.obj_type == "System Boundary":
                for o in self.objects:
                    if o.properties.get("boundary") == str(self.selected_obj.obj_id):
                        o.x += dx
                        o.y += dy
            else:
                b_id = self.selected_obj.properties.get("boundary")
                if b_id:
                    b = self.get_object(int(b_id))
                    if b:
                        b.x += dx
                        b.y += dy
                        for o in self.objects:
                            if o is not self.selected_obj and o.properties.get("boundary") == b_id:
                                o.x += dx
                                o.y += dy
        self.redraw()
        self._sync_to_repository()

    def on_left_release(self, event):
        if self.start and self.current_tool in (
            "Association",
            "Include",
            "Extend",
            "Flow",
            "Connector",
        ):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            obj = self.find_object(x, y)
            if obj and obj != self.start:
                valid, msg = self.validate_connection(self.start, obj, self.current_tool)
                if valid:
                    conn = DiagramConnection(self.start.obj_id, obj.obj_id, self.current_tool)
                    self.connections.append(conn)
                    if self.start.element_id and obj.element_id:
                        rel = self.repo.create_relationship(
                            self.current_tool, self.start.element_id, obj.element_id
                        )
                        self.repo.add_relationship_to_diagram(self.diagram_id, rel.rel_id)
                    self._sync_to_repository()
                    ConnectionDialog(self, conn)
                else:
                    messagebox.showwarning("Invalid Connection", msg)
        self.start = None
        self.temp_line_end = None
        self.resizing_obj = None
        self.resize_edge = None
        if self.dragging_point_index is not None and self.selected_conn:
            self._sync_to_repository()
        self.dragging_point_index = None
        if self.dragging_endpoint is not None and self.selected_conn:
            self._sync_to_repository()
        self.dragging_endpoint = None
        self.conn_drag_offset = None
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
            "Connector",
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
            "Connector",
        ):
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)
            self.temp_line_end = (x, y)
            self.redraw()

    def on_double_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        obj = self.find_object(x, y)
        if obj:
            if self._open_linked_diagram(obj):
                return
            SysMLObjectDialog(self, obj)
            self.redraw()
        else:
            conn = self.find_connection(x, y)
            if conn:
                ConnectionDialog(self, conn)
                self.redraw()

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
        obj = self.find_object(x, y)
        conn = None
        if not obj:
            conn = self.find_connection(x, y)
            if not conn:
                return
        self.selected_obj = obj
        self.selected_conn = conn
        menu = tk.Menu(self, tearoff=0)
        if obj:
            menu.add_command(label="Properties", command=lambda: self._edit_object(obj))
            diag_id = self.repo.get_linked_diagram(obj.element_id)
            if diag_id and diag_id in self.repo.diagrams or obj.properties.get("view"):
                menu.add_command(label="Open Linked Diagram", command=lambda: self._open_linked_diagram(obj))
            menu.add_separator()
            menu.add_command(label="Copy", command=self.copy_selected)
            menu.add_command(label="Cut", command=self.cut_selected)
            menu.add_command(label="Paste", command=self.paste_selected)
        menu.add_command(label="Delete", command=self.delete_selected)
        menu.tk_popup(event.x_root, event.y_root)

    def _edit_object(self, obj):
        SysMLObjectDialog(self, obj)
        self._sync_to_repository()
        self.redraw()

    def _open_linked_diagram(self, obj) -> bool:
        diag_id = self.repo.get_linked_diagram(obj.element_id)
        view_id = obj.properties.get("view")
        if obj.obj_type == "CallBehaviorAction" and diag_id and view_id and view_id in self.repo.diagrams:
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
        if diag.diag_type == "Use Case Diagram":
            UseCaseDiagramWindow(self.master, self.app, diagram_id=chosen)
        elif diag.diag_type == "Activity Diagram":
            ActivityDiagramWindow(self.master, self.app, diagram_id=chosen)
        elif diag.diag_type == "Block Diagram":
            BlockDiagramWindow(self.master, self.app, diagram_id=chosen)
        elif diag.diag_type == "Internal Block Diagram":
            InternalBlockDiagramWindow(self.master, self.app, diagram_id=chosen)
        return True
    def on_ctrl_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    # ------------------------------------------------------------
    # Utility methods
    # ------------------------------------------------------------
    def find_object(self, x: float, y: float) -> SysMLObject | None:
        for obj in reversed(self.objects):
            ox = obj.x * self.zoom
            oy = obj.y * self.zoom
            w = obj.width * self.zoom / 2
            h = obj.height * self.zoom / 2
            if obj.obj_type in ("Initial", "Final"):
                r = min(w, h)
                if (x - ox) ** 2 + (y - oy) ** 2 <= r ** 2:
                    return obj
            elif ox - w <= x <= ox + w and oy - h <= y <= oy + h:
                return obj
        return None

    def hit_resize_handle(self, obj: SysMLObject, x: float, y: float) -> str | None:
        if obj.obj_type in ("Initial", "Final"):
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

    def find_connection(self, x: float, y: float) -> DiagramConnection | None:
        for conn in self.connections:
            src = self.get_object(conn.src)
            dst = self.get_object(conn.dst)
            if not src or not dst:
                continue
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
                if self._dist_to_segment((x, y), a, b) <= 8:
                    return conn
        return None

    def snap_port_to_parent(self, port: SysMLObject, parent: SysMLObject) -> None:
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

    def edge_point(
        self,
        obj: SysMLObject,
        tx: float,
        ty: float,
        rel: tuple[float, float] | None = None,
    ) -> Tuple[float, float]:
        x = obj.x * self.zoom
        y = obj.y * self.zoom
        if obj.obj_type == "Port":
            return x, y
        if rel is not None:
            rx, ry = rel
            return (
                (obj.x + rx * obj.width / 2) * self.zoom,
                (obj.y + ry * obj.height / 2) * self.zoom,
            )
        w = obj.width * self.zoom / 2
        h = obj.height * self.zoom / 2
        dx = tx - x
        dy = ty - y
        if obj.obj_type in ("Initial", "Final"):
            r = min(w, h)
            dist = (dx ** 2 + dy ** 2) ** 0.5 or 1
            return x + dx / dist * r, y + dy / dist * r
        if abs(dx) > abs(dy):
            if dx > 0:
                x += w
                y += dy * (w / abs(dx)) if dx != 0 else 0
            else:
                x -= w
                y += dy * (w / abs(dx)) if dx != 0 else 0
        else:
            if dy > 0:
                y += h
                x += dx * (h / abs(dy)) if dy != 0 else 0
            else:
                y -= h
                x += dx * (h / abs(dy)) if dy != 0 else 0
        return x, y

    def sync_ports(self, part: SysMLObject) -> None:
        names: List[str] = []
        block_id = part.properties.get("definition")
        if block_id and block_id in self.repo.elements:
            block_elem = self.repo.elements[block_id]
            names.extend([p.strip() for p in block_elem.properties.get("ports", "").split(",") if p.strip()])
        names.extend([p.strip() for p in part.properties.get("ports", "").split(",") if p.strip()])
        existing = {o.properties.get("name"): o for o in self.objects if o.obj_type == "Port" and o.properties.get("parent") == str(part.obj_id)}
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
        return [
            ("Attributes", obj.properties.get("valueProperties", "")),
            ("Parts", obj.properties.get("partProperties", "")),
            ("References", obj.properties.get("referenceProperties", "")),
            (
                "Operations",
                "; ".join(
                    format_operation(op)
                    for op in parse_operations(obj.properties.get("operations", ""))
                ),
            ),
            ("Constraints", obj.properties.get("constraintProperties", "")),
            ("Ports", obj.properties.get("ports", "")),
            (
                "Reliability",
                " ".join(
                    f"{label}={obj.properties.get(key, '')}"
                    for label, key in (
                        ("FIT", "fit"),
                        ("Qual", "qualification"),
                        ("FM", "failureModes"),
                    )
                    if obj.properties.get(key, "")
                ),
            ),
            ("Requirements", "; ".join(r.get("id") for r in obj.requirements)),
        ]

    def _min_block_size(self, obj: SysMLObject) -> tuple[float, float]:
        """Return minimum width and height to display all Block text."""
        header = f"<<block>> {obj.properties.get('name', '')}".strip()
        width_px = self.font.measure(header) + 8 * self.zoom
        compartments = self._block_compartments(obj)
        for label, text in compartments:
            display = f"{label}: {text}" if text else f"{label}:"
            width_px = max(width_px, self.font.measure(display) + 8 * self.zoom)
        height_px = (1 + len(compartments)) * 20 * self.zoom
        return width_px / self.zoom, height_px / self.zoom

    def ensure_text_fits(self, obj: SysMLObject) -> None:
        """Expand the object's size so its label is fully visible."""
        label_lines: list[str] = []
        if obj.obj_type == "System Boundary":
            name = obj.properties.get("name", "")
            if name:
                label_lines.append(name)
        else:
            name = obj.properties.get("name", obj.obj_type)
            if obj.obj_type == "Part":
                def_id = obj.properties.get("definition")
                if def_id and def_id in self.repo.elements:
                    def_name = self.repo.elements[def_id].name or def_id
                    name = f"{name} : {def_name}" if name else def_name
            diag_id = self.repo.get_linked_diagram(obj.element_id)
            if diag_id and diag_id in self.repo.diagrams:
                diag = self.repo.diagrams[diag_id]
                diag_name = diag.name or diag_id
                label_lines.append(diag_name)
            label_lines.append(name)

        if not label_lines:
            return

        text_width = max(self.font.measure(line) for line in label_lines)
        text_height = self.font.metrics("linespace") * len(label_lines)
        padding = 10 * self.zoom
        min_w = (text_width + padding) / self.zoom
        min_h = (text_height + padding) / self.zoom

        if obj.obj_type == "Block":
            b_w, b_h = self._min_block_size(obj)
            min_w = max(min_w, b_w)
            min_h = max(min_h, b_h)

        if min_w > obj.width:
            obj.width = min_w
        if obj.obj_type not in ("Fork", "Join", "Initial", "Final") and min_h > obj.height:
            obj.height = min_h

    def sort_objects(self) -> None:
        """Ensure System Boundaries are drawn and selected behind others."""
        self.objects.sort(key=lambda o: 0 if o.obj_type == "System Boundary" else 1)

    def redraw(self):
        self.canvas.delete("all")
        self.sort_objects()
        remove_orphan_ports(self.objects)
        for obj in list(self.objects):
            if obj.obj_type == "Part":
                self.sync_ports(obj)
            self.ensure_text_fits(obj)
            self.draw_object(obj)
        for conn in self.connections:
            src = self.get_object(conn.src)
            dst = self.get_object(conn.dst)
            if src and dst:
                self.draw_connection(src, dst, conn, conn is self.selected_conn)
        if (
            self.start
            and self.temp_line_end
            and self.current_tool in (
                "Association",
                "Include",
                "Extend",
                "Flow",
                "Connector",
            )
        ):
            sx, sy = self.edge_point(self.start, *self.temp_line_end)
            ex, ey = self.temp_line_end
            self.canvas.create_line(sx, sy, ex, ey, dash=(2, 2), arrow=tk.LAST)
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
        return self.canvas.create_polygon(
            points, smooth=True, splinesteps=36, **kwargs
        )

    def draw_object(self, obj: SysMLObject):
        x = obj.x * self.zoom
        y = obj.y * self.zoom
        w = obj.width * self.zoom / 2
        h = obj.height * self.zoom / 2
        color = OBJECT_COLORS.get(obj.obj_type, "white")
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
            self._create_round_rect(
                x - w,
                y - h,
                x + w,
                y + h,
                radius=12 * self.zoom,
                dash=(4, 2),
                outline=outline,
                fill=color,
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
        elif obj.obj_type in ("Action Usage", "Action", "CallBehaviorAction", "Part", "Port"):
            dash = ()
            fill = color
            if obj.obj_type == "Part":
                dash = (4, 2)
            if obj.obj_type == "Port":
                side = obj.properties.get("side", "E")
                sz = 6 * self.zoom
                self.canvas.create_rectangle(
                    x - sz,
                    y - sz,
                    x + sz,
                    y + sz,
                    fill=color,
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
                        self.canvas.create_line(x + outside, y, x + inside, y, arrow=tk.LAST)
                    elif direction == "out":
                        self.canvas.create_line(x + inside, y, x + outside, y, arrow=tk.LAST)
                    else:
                        self.canvas.create_line(x - half, y, x + half, y, arrow=tk.BOTH)
                else:  # N or S
                    if side == "S":
                        inside = -half
                        outside = half
                    else:
                        inside = half
                        outside = -half
                    if direction == "in":
                        self.canvas.create_line(x, y + outside, x, y + inside, arrow=tk.LAST)
                    elif direction == "out":
                        self.canvas.create_line(x, y + inside, x, y + outside, arrow=tk.LAST)
                    else:
                        self.canvas.create_line(x, y - half, x, y + half, arrow=tk.BOTH)

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
                    self._create_round_rect(
                        x - w,
                        y - h,
                        x + w,
                        y + h,
                        radius=8 * self.zoom,
                        dash=dash,
                        fill=fill,
                        outline=outline,
                    )
                else:
                    self.canvas.create_rectangle(
                        x - w,
                        y - h,
                        x + w,
                        y + h,
                        dash=dash,
                        fill=fill,
                        outline=outline,
                    )
        elif obj.obj_type == "Block":
            left, top = x - w, y - h
            right, bottom = x + w, y + h
            self._create_round_rect(
                left,
                top,
                right,
                bottom,
                radius=6 * self.zoom,
                fill=color,
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
            compartments = [
                ("Attributes", obj.properties.get("valueProperties", "")),
                ("Parts", obj.properties.get("partProperties", "")),
                ("References", obj.properties.get("referenceProperties", "")),
                (
                    "Operations",
                    "; ".join(
                        format_operation(op)
                        for op in parse_operations(
                            obj.properties.get("operations", "")
                        )
                    ),
                ),
                ("Constraints", obj.properties.get("constraintProperties", "")),
                ("Ports", obj.properties.get("ports", "")),
                (
                    "Reliability",
                    " ".join(
                        f"{label}={obj.properties.get(key,'')}"
                        for label, key in (
                            ("FIT", "fit"),
                            ("Qual", "qualification"),
                            ("FM", "failureModes"),
                        )
                        if obj.properties.get(key, "")
                    ),
                ),
                (
                    "Requirements",
                    "; ".join(r.get("id") for r in obj.requirements),
                ),
            ]
            cy = top + 20 * self.zoom
            for label, text in compartments:
                self.canvas.create_line(left, cy, right, cy)
                display = f"{label}: {text}" if text else f"{label}:"
                self.canvas.create_text(
                    left + 4 * self.zoom,
                    cy + 10 * self.zoom,
                    text=display,
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
                self.canvas.create_oval(x - inner, y - inner, x + inner, y + inner,
                                        fill="black")
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
            self.canvas.create_rectangle(x - half, y - 5 * self.zoom,
                                        x + half, y + 5 * self.zoom,
                                        fill="black")
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

        if obj.obj_type not in ("Block", "System Boundary", "Port"):
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
            key = obj.obj_type.replace(' ', '')
            if not key.endswith('Usage'):
                key += 'Usage'
            for prop in SYSML_PROPERTIES.get(key, []):
                if obj.obj_type == "Part" and prop in ("fit", "qualification", "failureModes", "asil"):
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
                self.canvas.create_text(label_x, label_y, text="\n".join(label_lines), anchor="n")
            elif obj.obj_type in ("Initial", "Final"):
                label_y = y + obj.height / 2 * self.zoom + 10 * self.zoom
                self.canvas.create_text(x, label_y, text="\n".join(label_lines), anchor="n")
            else:
                self.canvas.create_text(x, y, text="\n".join(label_lines), anchor="center")

        if obj == self.selected_obj:
            bx = x - w
            by = y - h
            ex = x + w
            ey = y + h
            self.canvas.create_rectangle(bx, by, ex, ey, outline="red", dash=(2, 2))
            s = 4
            for hx, hy in [(bx, by), (bx, ey), (ex, by), (ex, ey)]:
                self.canvas.create_rectangle(hx - s, hy - s, hx + s, hy + s,
                                             outline="red", fill="white")

    def draw_connection(
        self, a: SysMLObject, b: SysMLObject, conn: DiagramConnection, selected: bool = False
    ):
        axc, ayc = a.x * self.zoom, a.y * self.zoom
        bxc, byc = b.x * self.zoom, b.y * self.zoom
        ax, ay = self.edge_point(a, bxc, byc, conn.src_pos)
        bx, by = self.edge_point(b, axc, ayc, conn.dst_pos)
        dash = ()
        label = None
        if conn.conn_type in ("Include", "Extend"):
            dash = (4, 2)
            label = f"<<{conn.conn_type.lower()}>>"
        points = [(ax, ay)]
        if conn.style == "Squared":
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
        self.canvas.create_line(*flat, arrow=tk.LAST, dash=dash, fill=color, width=width)
        if selected:
            if conn.style == "Custom":
                for px, py in conn.points:
                    hx = px * self.zoom
                    hy = py * self.zoom
                    s = 3
                    self.canvas.create_rectangle(hx - s, hy - s, hx + s, hy + s, outline="red", fill="white")
            elif conn.style == "Squared":
                if conn.points:
                    mx = conn.points[0][0] * self.zoom
                else:
                    mx = (ax + bx) / 2
                hy = (ay + by) / 2
                s = 3
                self.canvas.create_rectangle(mx - s, hy - s, mx + s, hy + s, outline="red", fill="white")
            # draw endpoint handles
            for hx, hy in [(ax, ay), (bx, by)]:
                s = 3
                self.canvas.create_rectangle(hx - s, hy - s, hx + s, hy + s, outline="red", fill="white")
        if label:
            mx, my = (ax + bx) / 2, (ay + by) / 2
            self.canvas.create_text(
                mx,
                my - 10 * self.zoom,
                text=label,
                font=self.font,
            )

    def get_object(self, oid: int) -> SysMLObject | None:
        for o in self.objects:
            if o.obj_id == oid:
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

    def delete_selected(self, _event=None):
        if self.selected_obj:
            self.remove_object(self.selected_obj)
            self.selected_obj = None
            self._sync_to_repository()
            self.redraw()
            return
        if self.selected_conn:
            if self.selected_conn in self.connections:
                self.connections.remove(self.selected_conn)
                # remove matching repository relationship
                src_elem = self.get_object(self.selected_conn.src)
                dst_elem = self.get_object(self.selected_conn.dst)
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
                            break
                self.selected_conn = None
                self._sync_to_repository()
                self.redraw()

    def remove_object(self, obj: SysMLObject) -> None:
        if obj in self.objects:
            self.objects.remove(obj)
        self.connections = [c for c in self.connections if c.src != obj.obj_id and c.dst != obj.obj_id]
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag and obj.element_id in diag.elements:
            diag.elements.remove(obj.element_id)
        self._sync_to_repository()

    def _sync_to_repository(self) -> None:
        """Persist current objects and connections back to the repository."""
        diag = self.repo.diagrams.get(self.diagram_id)
        if diag:
            diag.objects = [obj.__dict__ for obj in self.objects]
            diag.connections = [conn.__dict__ for conn in self.connections]

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
                ttk.Checkbutton(self.check_frame, text=text, variable=var).pack(anchor="w", padx=2, pady=2)
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
                ttk.Checkbutton(self.check_frame, text=comp.name, variable=var).pack(anchor="w", padx=2, pady=2)
            return self.check_frame

        def apply(self):
            self.result = [c for c, var in self.selected.items() if var.get()]

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
        ttk.Entry(gen_frame, textvariable=self.name_var).grid(row=gen_row, column=1, padx=4, pady=4)
        gen_row += 1
        ttk.Label(gen_frame, text="Width:").grid(row=gen_row, column=0, sticky="e", padx=4, pady=2)
        self.width_var = tk.StringVar(value=str(self.obj.width))
        width_state = "readonly" if self.obj.obj_type in ("Initial", "Final") else "normal"
        ttk.Entry(gen_frame, textvariable=self.width_var, state=width_state).grid(row=gen_row, column=1, padx=4, pady=2)
        gen_row += 1
        if self.obj.obj_type not in ("Fork", "Join"):
            ttk.Label(gen_frame, text="Height:").grid(row=gen_row, column=0, sticky="e", padx=4, pady=2)
            self.height_var = tk.StringVar(value=str(self.obj.height))
            height_state = "readonly" if self.obj.obj_type in ("Initial", "Final") else "normal"
            ttk.Entry(gen_frame, textvariable=self.height_var, state=height_state).grid(row=gen_row, column=1, padx=4, pady=2)
            gen_row += 1
        else:
            self.height_var = tk.StringVar(value=str(self.obj.height))
        self.entries = {}
        self.listboxes = {}
        self._operations: List[OperationDefinition] = []
        prop_row = 0
        rel_row = 0
        if self.obj.obj_type == "Part":
            self.obj.properties.setdefault("asil", calculate_allocated_asil(self.obj.requirements))
        key = f"{self.obj.obj_type.replace(' ', '')}Usage"
        list_props = {
            "ports",
            "partProperties",
            "referenceProperties",
            "valueProperties",
            "constraintProperties",
            "operations",
            "failureModes",
        }
        reliability_props = {"analysis", "component", "fit", "qualification", "failureModes", "asil"}
        app = getattr(self.master, 'app', None)
        for prop in SYSML_PROPERTIES.get(key, []):
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
            elif prop in list_props:
                lb = tk.Listbox(frame, height=4)
                items = [p.strip() for p in self.obj.properties.get(prop, "").split(",") if p.strip()]
                for it in items:
                    lb.insert(tk.END, it)
                lb.grid(row=row, column=1, padx=4, pady=2, sticky="we")
                btnf = ttk.Frame(frame)
                btnf.grid(row=row, column=2, padx=2)
                ttk.Button(btnf, text="Add", command=lambda p=prop: self.add_list_item(p)).pack(side=tk.TOP)
                ttk.Button(btnf, text="Remove", command=lambda p=prop: self.remove_list_item(p)).pack(side=tk.TOP)
                self.listboxes[prop] = lb
            elif prop == "direction":
                var = tk.StringVar(value=self.obj.properties.get(prop, "in"))
                ttk.Combobox(frame, textvariable=var, values=["in", "out", "inout"]).grid(row=row, column=1, padx=4, pady=2)
                self.entries[prop] = var
            elif self.obj.obj_type == "Use Case" and prop == "useCaseDefinition":
                repo = SysMLRepository.get_instance()
                diags = [
                    d for d in repo.diagrams.values()
                    if d.diag_type == "Use Case Diagram" and d.diag_id != self.master.diagram_id
                ]
                idmap = {d.name or d.diag_id: d.diag_id for d in diags}
                self.ucdef_map = idmap
                cur_id = self.obj.properties.get(prop, "")
                cur_name = next((n for n, i in idmap.items() if i == cur_id), "")
                var = tk.StringVar(value=cur_name)
                ttk.Combobox(frame, textvariable=var, values=list(idmap.keys())).grid(row=row, column=1, padx=4, pady=2)
                self.entries[prop] = var
            elif self.obj.obj_type == "Use Case" and prop == "includedUseCase":
                repo = SysMLRepository.get_instance()
                targets = [
                    repo.elements[t].name or t
                    for rel in repo.relationships
                    if rel.rel_type == "Include" and rel.source == self.obj.element_id
                    if (t := rel.target) in repo.elements
                ]
                ttk.Label(frame, text=", ".join(targets)).grid(row=row, column=1, sticky="w", padx=4, pady=2)
            elif prop == "analysis" and app:
                analyses = getattr(app, 'reliability_analyses', [])
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
                    if 'fit' in self.entries:
                        self.entries['fit'].set(f"{ra.total_fit:.2f}")
                    else:
                        self.obj.properties['fit'] = f"{ra.total_fit:.2f}"
                    # update part list preview from analysis BOM
                    names = [c.name for c in ra.components]
                    joined = ", ".join(names)
                    if 'partProperties' in self.listboxes:
                        lb = self.listboxes['partProperties']
                        lb.delete(0, tk.END)
                        for n in names:
                            lb.insert(tk.END, n)
                    else:
                        self.obj.properties['partProperties'] = joined

                cb.bind("<<ComboboxSelected>>", sync_analysis)
            elif prop == "component" and app:
                comps = [
                    c
                    for ra in getattr(app, 'reliability_analyses', [])
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
                    if 'fit' in self.entries:
                        self.entries['fit'].set(f"{comp.fit:.2f}")
                    else:
                        self.obj.properties['fit'] = f"{comp.fit:.2f}"
                    if 'qualification' in self.entries:
                        self.entries['qualification'].set(comp.qualification)
                    else:
                        self.obj.properties['qualification'] = comp.qualification
                    modes = self._get_failure_modes(app, comp.name)
                    if 'failureModes' in self.entries:
                        self.entries['failureModes'].set(modes)
                    else:
                        self.obj.properties['failureModes'] = modes

                cb.bind("<<ComboboxSelected>>", sync_component)
            else:
                var = tk.StringVar(value=self.obj.properties.get(prop, ""))
                state = "normal"
                if self.obj.obj_type == "Block" and prop in ("fit", "qualification"):
                    state = "readonly"
                if self.obj.obj_type == "Part" and prop == "asil":
                    state = "readonly"
                ttk.Entry(frame, textvariable=var, state=state).grid(row=row, column=1, padx=4, pady=2)
                self.entries[prop] = var
            if prop in reliability_props:
                rel_row += 1
            else:
                prop_row += 1

        # Display inherited reliability values only for Blocks
        if self.obj.obj_type == "Block":
            for prop in ("fit", "qualification"):
                if prop not in self.entries and self.obj.properties.get(prop, ""):
                    ttk.Label(rel_frame, text=f"{prop}:").grid(row=rel_row, column=0, sticky="e", padx=4, pady=2)
                    var = tk.StringVar(value=self.obj.properties.get(prop, ""))
                    ttk.Entry(rel_frame, textvariable=var, state="readonly").grid(row=rel_row, column=1, padx=4, pady=2)
                    self.entries[prop] = var
                    rel_row += 1

        repo = SysMLRepository.get_instance()
        link_row = 0
        if self.obj.obj_type == "Block":
            diags = [d for d in repo.diagrams.values() if d.diag_type == "Internal Block Diagram"]
            ids = {d.name or d.diag_id: d.diag_id for d in diags}
            ttk.Label(link_frame, text="Internal Block Diagram:").grid(row=link_row, column=0, sticky="e", padx=4, pady=2)
            self.diag_map = ids
            cur_id = repo.get_linked_diagram(self.obj.element_id)
            cur_name = next((n for n, i in ids.items() if i == cur_id), "")
            self.diagram_var = tk.StringVar(value=cur_name)
            ttk.Combobox(link_frame, textvariable=self.diagram_var, values=list(ids.keys())).grid(row=link_row, column=1, padx=4, pady=2)
            link_row += 1
        elif self.obj.obj_type in ("Action Usage", "Action"):
            diagrams = [d for d in repo.diagrams.values() if d.diag_type == "Activity Diagram"]
            self.behavior_map = {d.name or d.diag_id: d.diag_id for d in diagrams}
            ttk.Label(link_frame, text="Behavior Diagram:").grid(row=link_row, column=0, sticky="e", padx=4, pady=2)
            cur_id = repo.get_linked_diagram(self.obj.element_id)
            cur_name = next((n for n, i in self.behavior_map.items() if i == cur_id), "")
            self.behavior_var = tk.StringVar(value=cur_name)
            ttk.Combobox(link_frame, textvariable=self.behavior_var, values=list(self.behavior_map.keys())).grid(row=link_row, column=1, padx=4, pady=2)
            link_row += 1
        elif self.obj.obj_type == "CallBehaviorAction":
            bdiags = [d for d in repo.diagrams.values() if d.diag_type == "Activity Diagram"]
            self.behavior_map = {d.name or d.diag_id: d.diag_id for d in bdiags}
            ttk.Label(link_frame, text="Behavior Diagram:").grid(row=link_row, column=0, sticky="e", padx=4, pady=2)
            cur_id = repo.get_linked_diagram(self.obj.element_id)
            cur_name = next((n for n, i in self.behavior_map.items() if i == cur_id), "")
            self.behavior_var = tk.StringVar(value=cur_name)
            ttk.Combobox(link_frame, textvariable=self.behavior_var, values=list(self.behavior_map.keys())).grid(row=link_row, column=1, padx=4, pady=2)
            link_row += 1
            vdiags = [d for d in repo.diagrams.values() if d.diag_type == "Internal Block Diagram"]
            self.view_map = {d.name or d.diag_id: d.diag_id for d in vdiags}
            ttk.Label(link_frame, text="View:").grid(row=link_row, column=0, sticky="e", padx=4, pady=2)
            view_id = self.obj.properties.get("view", "")
            vname = next((n for n, i in self.view_map.items() if i == view_id), "")
            self.view_var = tk.StringVar(value=vname)
            ttk.Combobox(link_frame, textvariable=self.view_var, values=list(self.view_map.keys())).grid(row=link_row, column=1, padx=4, pady=2)
            link_row += 1
        elif self.obj.obj_type == "Part":
            blocks = [e for e in repo.elements.values() if e.elem_type == "Block"]
            idmap = {b.name or b.elem_id: b.elem_id for b in blocks}
            ttk.Label(link_frame, text="Definition:").grid(row=link_row, column=0, sticky="e", padx=4, pady=2)
            self.def_map = idmap
            cur_id = self.obj.properties.get("definition", "")
            cur_name = next((n for n, i in idmap.items() if i == cur_id), "")
            self.def_var = tk.StringVar(value=cur_name)
            ttk.Combobox(link_frame, textvariable=self.def_var, values=list(idmap.keys())).grid(row=link_row, column=1, padx=4, pady=2)
            link_row += 1

        # Requirement allocation section
        req_row = 0
        ttk.Label(req_frame, text="Requirements:").grid(row=req_row, column=0, sticky="ne", padx=4, pady=2)
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

    def add_list_item(self, prop: str):
        val = simpledialog.askstring(prop, "Value:", parent=self)
        if val:
            self.listboxes[prop].insert(tk.END, val)

    def remove_list_item(self, prop: str):
        lb = self.listboxes[prop]
        sel = list(lb.curselection())
        for idx in reversed(sel):
            lb.delete(idx)

    class OperationDialog(simpledialog.Dialog):
        def __init__(self, parent, operation=None):
            self.operation = operation
            super().__init__(parent, title="Operation")

        def body(self, master):
            ttk.Label(master, text="Name:").grid(row=0, column=0, padx=4, pady=2, sticky="e")
            self.name_var = tk.StringVar(value=getattr(self.operation, "name", ""))
            ttk.Entry(master, textvariable=self.name_var).grid(row=0, column=1, padx=4, pady=2)
            ttk.Label(master, text="Parameters (name:type:dir)").grid(row=1, column=0, columnspan=2, padx=4, pady=2)
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
                    params.append(OperationParameter(name=parts[0], type=parts[1], direction=parts[2]))
            self.result = OperationDefinition(name, params, self.ret_var.get().strip())

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
        for e in getattr(app, 'fmea_entries', []):
            if getattr(e, 'fmea_component', '') == comp_name:
                label = getattr(e, 'description', '') or getattr(e, 'user_name', '')
                if label:
                    modes.add(label)
        for fmea in getattr(app, 'fmeas', []):
            for e in fmea.get('entries', []):
                if getattr(e, 'fmea_component', '') == comp_name:
                    label = getattr(e, 'description', '') or getattr(e, 'user_name', '')
                    if label:
                        modes.add(label)
        return ", ".join(sorted(modes))
        
    def apply(self):
        self.obj.properties["name"] = self.name_var.get()
        repo = SysMLRepository.get_instance()
        if self.obj.element_id and self.obj.element_id in repo.elements:
            repo.elements[self.obj.element_id].name = self.name_var.get()
        for prop, var in self.entries.items():
            self.obj.properties[prop] = var.get()
            if self.obj.element_id and self.obj.element_id in repo.elements:
                repo.elements[self.obj.element_id].properties[prop] = var.get()
        for prop, lb in self.listboxes.items():
            if prop == "operations":
                self.obj.properties[prop] = operations_to_json(self._operations)
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties[prop] = self.obj.properties[prop]
            else:
                items = [lb.get(i) for i in range(lb.size())]
                joined = ", ".join(items)
                self.obj.properties[prop] = joined
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties[prop] = joined
        try:
            if self.obj.obj_type not in ("Initial", "Final"):
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
                cur = [p.strip() for p in self.obj.properties.get("partProperties", "").split(",") if p.strip()]
                names = [c.name for c in ra.components]
                for n in names:
                    if n not in cur:
                        cur.append(n)
                joined = ", ".join(cur)
                self.obj.properties["partProperties"] = joined
                if self.obj.element_id and self.obj.element_id in repo.elements:
                    repo.elements[self.obj.element_id].properties["partProperties"] = joined
                if self.obj.element_id:
                    extend_block_parts_with_parents(repo, self.obj.element_id)
                    self.obj.properties["partProperties"] = repo.elements[self.obj.element_id].properties["partProperties"]

        # Update linked diagram if applicable
        link_id = None
        if hasattr(self, "behavior_var") and self.behavior_var.get():
            link_id = self.behavior_map.get(self.behavior_var.get())
        elif hasattr(self, "diagram_var"):
            link_id = self.diag_map.get(self.diagram_var.get())
        if hasattr(self, "behavior_var") or hasattr(self, "diagram_var"):
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
                                        "failureModes": self._get_failure_modes(getattr(self.master, "app", None), c.name),
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
                                    repo.elements[self.obj.element_id].properties["partProperties"] = joined
                                # update all diagram objects referencing this block element
                                for d in repo.diagrams.values():
                                    for o in getattr(d, "objects", []):
                                        if o.get("element_id") == self.obj.element_id:
                                            o.setdefault("properties", {})["partProperties"] = joined
                                # include parent block parts
                                if self.obj.element_id:
                                    extend_block_parts_with_parents(repo, self.obj.element_id)
                                    joined = repo.elements[self.obj.element_id].properties["partProperties"]
                                    self.obj.properties["partProperties"] = joined
                            repo.diagrams[diag_id] = diag
                            if hasattr(self.master, "_sync_to_repository"):
                                self.master._sync_to_repository()

        
class ConnectionDialog(simpledialog.Dialog):
    """Edit connection style and custom routing points."""

    def __init__(self, master, connection: DiagramConnection):
        self.connection = connection
        super().__init__(master, title="Connection Properties")

    def body(self, master):
        ttk.Label(master, text="Style:").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        self.style_var = tk.StringVar(value=self.connection.style)
        ttk.Combobox(master, textvariable=self.style_var,
                     values=["Straight", "Squared", "Custom"]).grid(row=0, column=1, padx=4, pady=4)
        ttk.Label(master, text="Points:").grid(row=1, column=0, sticky="ne", padx=4, pady=4)
        self.point_list = tk.Listbox(master, height=4)
        for px, py in self.connection.points:
            self.point_list.insert(tk.END, f"{px:.1f},{py:.1f}")
        self.point_list.grid(row=1, column=1, padx=4, pady=4, sticky="we")
        btnf = ttk.Frame(master)
        btnf.grid(row=1, column=2, padx=2)
        ttk.Button(btnf, text="Add", command=self.add_point).pack(side=tk.TOP)
        ttk.Button(btnf, text="Remove", command=self.remove_point).pack(side=tk.TOP)

    def add_point(self):
        x = simpledialog.askfloat("Point", "X:", parent=self)
        y = simpledialog.askfloat("Point", "Y:", parent=self)
        if x is not None and y is not None:
            self.point_list.insert(tk.END, f"{x},{y}")

    def remove_point(self):
        sel = list(self.point_list.curselection())
        for idx in reversed(sel):
            self.point_list.delete(idx)

    def apply(self):
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
        if hasattr(self.master, "_sync_to_repository"):
            self.master._sync_to_repository()

class UseCaseDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None):
        tools = [
            "Actor",
            "Use Case",
            "System Boundary",
            "Association",
        ]
        super().__init__(master, "Use Case Diagram", tools, diagram_id, app=app)


class ActivityDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None):
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
        ]
        super().__init__(master, "Activity Diagram", tools, diagram_id, app=app)


class BlockDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None):
        tools = [
            "Block",
            "Association",
        ]
        super().__init__(master, "Block Diagram", tools, diagram_id, app=app)


class InternalBlockDiagramWindow(SysMLDiagramWindow):
    def __init__(self, master, app, diagram_id: str | None = None):
        tools = [
            "Part",
            "Port",
            "Connector",
        ]
        super().__init__(master, "Internal Block Diagram", tools, diagram_id, app=app)
        ttk.Button(self.toolbox, text="Add Block Parts", command=self.add_block_parts).pack(
            fill=tk.X, padx=2, pady=2
        )

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

    def add_block_parts(self) -> None:
        repo = self.repo
        # determine which block this IBD represents
        block_id = next((eid for eid, did in repo.element_diagrams.items() if did == self.diagram_id), None)
        if not block_id or block_id not in repo.elements:
            messagebox.showinfo("Add Parts", "No block is linked to this diagram")
            return
        block = repo.elements[block_id]
        ra_name = block.properties.get("analysis", "")
        if not ra_name:
            messagebox.showinfo("Add Parts", "Block has no reliability analysis assigned")
            return
        analyses = getattr(self.app, "reliability_analyses", [])
        ra_map = {ra.name: ra for ra in analyses}
        ra = ra_map.get(ra_name)
        if not ra or not ra.components:
            messagebox.showinfo("Add Parts", "Analysis has no components")
            return
        comps = list(ra.components)
        dlg = SysMLObjectDialog.SelectComponentsDialog(self, comps)
        selected = dlg.result or []
        if not selected:
            return
        diag = repo.diagrams.get(self.diagram_id)
        if diag is None:
            return
        diag.objects = getattr(diag, "objects", [])
        existing = {
            o.get("properties", {}).get("component")
            for o in diag.objects
            if o.get("obj_type") == "Part"
        }
        base_x = 50.0
        base_y = 50.0
        offset = 60.0
        added = []
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
                    "failureModes": self._get_failure_modes(c.name),
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
            added.append(c.name)
        self.redraw()
        self._sync_to_repository()
        if added:
            names = [n.strip() for n in block.properties.get("partProperties", "").split(",") if n.strip()]
            for name in added:
                if name not in names:
                    names.append(name)
            joined = ", ".join(names)
            block.properties["partProperties"] = joined
            extend_block_parts_with_parents(repo, block_id)
            joined = repo.elements[block_id].properties["partProperties"]
            for d in repo.diagrams.values():
                for o in getattr(d, "objects", []):
                    if o.get("element_id") == block_id:
                        o.setdefault("properties", {})["partProperties"] = joined

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
        ttk.Combobox(master, textvariable=self.type_var,
                     values=["Use Case Diagram", "Activity Diagram", "Block Diagram", "Internal Block Diagram"]).grid(row=1, column=1, padx=4, pady=4)

    def apply(self):
        self.name = self.name_var.get()
        self.diag_type = self.type_var.get()

class DiagramPropertiesDialog(simpledialog.Dialog):
    """Dialog to edit a diagram's metadata."""

    def __init__(self, master, diagram: SysMLDiagram):
        self.diagram = diagram
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

    def apply(self):
        self.diagram.name = self.name_var.get()
        self.diagram.description = self.desc_var.get()
        self.diagram.color = self.color_var.get()

class PackagePropertiesDialog(simpledialog.Dialog):
    """Dialog to edit a package's name."""

    def __init__(self, master, package: SysMLElement):
        self.package = package
        super().__init__(master, title="Package Properties")

    def body(self, master):
        ttk.Label(master, text="Name:").grid(
            row=0, column=0, sticky="e", padx=4, pady=2
        )
        self.name_var = tk.StringVar(value=self.package.name)
        ttk.Entry(master, textvariable=self.name_var).grid(
            row=0, column=1, padx=4, pady=2
        )

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
            ttk.Label(master, text=f"{prop}:").grid(row=row, column=0, sticky="e", padx=4, pady=2)
            var = tk.StringVar(value=self.element.properties.get(prop, ""))
            ttk.Entry(master, textvariable=var).grid(row=row, column=1, padx=4, pady=2)
            self.entries[prop] = var
            row += 1

    def apply(self):
        self.element.name = self.name_var.get()
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
        self.tree = ttk.Treeview(self)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # simple icons to visually distinguish packages, diagrams and objects
        self.pkg_icon = self._create_icon("folder")
        self.diagram_icons = {
            "Use Case Diagram": self._create_icon("circle"),
            "Activity Diagram": self._create_icon("arrow"),
            "Block Diagram": self._create_icon("rect"),
            "Internal Block Diagram": self._create_icon("nested"),
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
                        rel_node = self.tree.insert(node, "end", iid=rel_iid,
                                                   text=rtype,
                                                   values=("Relationship",))
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
                if d.package == pkg_id:
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
                        key=lambda o: 1 if getattr(o, "obj_type", o.get("obj_type")) == "Port" else 0,
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
        master = self.master if self.master else self
        win = None
        if diag.diag_type == "Use Case Diagram":
            UseCaseDiagramWindow(master, self.app, diagram_id=diag_id)
        elif diag.diag_type == "Activity Diagram":
            ActivityDiagramWindow(master, self.app, diagram_id=diag_id)
        elif diag.diag_type == "Block Diagram":
            BlockDiagramWindow(master, self.app, diagram_id=diag_id)
        elif diag.diag_type == "Internal Block Diagram":
            InternalBlockDiagramWindow(master, self.app, diagram_id=diag_id)

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
                        obj.__dict__ if str(o.get("obj_id")) == oid else o
                        for o in diag.objects
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
        # Dropping a diagram onto an Activity Diagram creates a CallBehaviorAction
        if elem_id.startswith("diag_"):
            src_diag = repo.diagrams.get(elem_id[5:])
            if src_diag and diagram.diag_type == "Activity Diagram" and src_diag.diag_type in ("Activity Diagram", "Internal Block Diagram"):
                act = repo.create_element("CallBehaviorAction", name=src_diag.name, owner=diagram.package)
                repo.add_element_to_diagram(diagram.diag_id, act.elem_id)
                props = {"name": src_diag.name}
                if src_diag.diag_type == "Internal Block Diagram":
                    props["view"] = src_diag.diag_id
                    repo.link_diagram(act.elem_id, None)
                else:
                    repo.link_diagram(act.elem_id, src_diag.diag_id)
                obj = SysMLObject(_get_next_id(), "CallBehaviorAction", 50.0, 50.0, element_id=act.elem_id, properties=props)
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

    def _create_icon(self, shape: str) -> tk.PhotoImage:
        """Return a simple 16x16 PhotoImage representing the given shape."""
        size = 16
        img = tk.PhotoImage(width=size, height=size)
        img.put("white", to=(0, 0, size - 1, size - 1))
        if shape == "circle":
            r = size // 2 - 2
            cx = cy = size // 2
            for y in range(size):
                for x in range(size):
                    if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                        img.put("black", (x, y))
        elif shape == "arrow":
            mid = size // 2
            for x in range(2, mid + 1):
                img.put("black", to=(x, mid - 1, x + 1, mid + 1))
            for i in range(4):
                img.put("black", to=(mid + i, mid - 2 - i, mid + i + 1, mid - i))
                img.put("black", to=(mid + i, mid + i, mid + i + 1, mid + 2 + i))
        elif shape == "rect":
            for x in range(3, size - 3):
                img.put("black", (x, 3))
                img.put("black", (x, size - 4))
            for y in range(3, size - 3):
                img.put("black", (3, y))
                img.put("black", (size - 4, y))
        elif shape == "nested":
            for x in range(1, size - 1):
                img.put("black", (x, 1))
                img.put("black", (x, size - 2))
            for y in range(1, size - 1):
                img.put("black", (1, y))
                img.put("black", (size - 2, y))
            for x in range(5, size - 5):
                img.put("black", (x, 5))
                img.put("black", (x, size - 6))
            for y in range(5, size - 5):
                img.put("black", (5, y))
                img.put("black", (size - 6, y))
        elif shape == "folder":
            for x in range(1, size - 1):
                img.put("black", (x, 4))
                img.put("black", (x, size - 2))
            for y in range(4, size - 1):
                img.put("black", (1, y))
                img.put("black", (size - 2, y))
            for x in range(3, size - 3):
                img.put("black", (x, 2))
            img.put("black", to=(1, 3, size - 2, 4))
        else:
            img.put("black", to=(2, 2, size - 2, size - 2))
        return img

