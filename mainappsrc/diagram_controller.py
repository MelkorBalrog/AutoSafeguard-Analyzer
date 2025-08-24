"""Diagram operations for AutoMLApp."""
from __future__ import annotations

from tkinter import filedialog, simpledialog
from PIL import Image, ImageDraw, ImageFont
from sysml.sysml_repository import SysMLRepository
from gui.architecture import (
    UseCaseDiagramWindow,
    ActivityDiagramWindow,
    BlockDiagramWindow,
    InternalBlockDiagramWindow,
    ControlFlowDiagramWindow,
)


class DiagramController:
    """Manage diagram creation and export."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    # ------------------------------------------------------------------
    def save_diagram_png(self) -> None:
        app = self.app
        mb = app.messagebox
        margin = 50
        all_nodes = app.get_all_nodes(app.root_node)
        if not all_nodes:
            mb.showerror("Error", "No nodes to export.")
            return
        min_x = min(n.x for n in all_nodes) - margin
        min_y = min(n.y for n in all_nodes) - margin
        max_x = max(n.x for n in all_nodes) + margin
        max_y = max(n.y for n in all_nodes) + margin
        scale_factor = 4
        width = int((max_x - min_x) * scale_factor)
        height = int((max_y - min_y) * scale_factor)
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        grid_size = app.grid_size
        for x in range(0, int(max_x - min_x) + 1, grid_size):
            x_pos = int(x * scale_factor)
            draw.line([(x_pos, 0), (x_pos, height)], fill="#ddd")
        for y in range(0, int(max_y - min_y) + 1, grid_size):
            y_pos = int(y * scale_factor)
            draw.line([(0, y_pos), (width, y_pos)], fill="#ddd")
        try:
            font = ImageFont.truetype("arial.ttf", 10 * scale_factor)
        except IOError:
            font = ImageFont.load_default()
        for node in all_nodes:
            eff_x = int((node.x - min_x) * scale_factor)
            eff_y = int((node.y - min_y) * scale_factor)
            radius = int(45 * scale_factor)
            bbox = [eff_x - radius, eff_y - radius, eff_x + radius, eff_y + radius]
            node_color = app.get_node_fill_color(
                node, getattr(app.canvas, "diagram_mode", None)
            )
            draw.ellipse(bbox, outline="dimgray", fill=node_color)
            text = node.name
            text_size = draw.textsize(text, font=font)
            text_x = eff_x - text_size[0] // 2
            text_y = eff_y - text_size[1] // 2
            draw.text((text_x, text_y), text, fill="black", font=font)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG files", "*.png")]
        )
        if file_path:
            try:
                img.save(file_path, "PNG")
                mb.showinfo(
                    "Saved", "High-resolution diagram exported as PNG."
                )
            except Exception as exc:
                mb.showerror("Save Error", f"An error occurred: {exc}")

    # ------------------------------------------------------------------
    def open_use_case_diagram(self) -> None:
        name = simpledialog.askstring("New Use Case Diagram", "Enter diagram name:")
        if not name:
            return
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Use Case Diagram", name=name, package=repo.root_package.elem_id)
        tab = self.app._new_tab(self.app._format_diag_title(diag))
        self.app.diagram_tabs[diag.diag_id] = tab
        UseCaseDiagramWindow(tab, self.app, diagram_id=diag.diag_id)
        self.app.refresh_all()

    def open_activity_diagram(self) -> None:
        name = simpledialog.askstring("New Activity Diagram", "Enter diagram name:")
        if not name:
            return
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Activity Diagram", name=name, package=repo.root_package.elem_id)
        if hasattr(self.app, "safety_mgmt_toolbox"):
            self.app.safety_mgmt_toolbox.register_created_work_product(
                "Activity Diagram", diag.name
            )
        tab = self.app._new_tab(self.app._format_diag_title(diag))
        self.app.diagram_tabs[diag.diag_id] = tab
        ActivityDiagramWindow(tab, self.app, diagram_id=diag.diag_id)
        self.app.refresh_all()

    def open_block_diagram(self) -> None:
        name = simpledialog.askstring("New Block Diagram", "Enter diagram name:")
        if not name:
            return
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Block Diagram", name=name, package=repo.root_package.elem_id)
        tab = self.app._new_tab(self.app._format_diag_title(diag))
        self.app.diagram_tabs[diag.diag_id] = tab
        BlockDiagramWindow(tab, self.app, diagram_id=diag.diag_id)
        self.app.refresh_all()

    def open_internal_block_diagram(self) -> None:
        name = simpledialog.askstring(
            "New Internal Block Diagram", "Enter diagram name:"
        )
        if not name:
            return
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram(
            "Internal Block Diagram", name=name, package=repo.root_package.elem_id
        )
        tab = self.app._new_tab(self.app._format_diag_title(diag))
        self.app.diagram_tabs[diag.diag_id] = tab
        InternalBlockDiagramWindow(tab, self.app, diagram_id=diag.diag_id)
        self.app.refresh_all()

    def open_control_flow_diagram(self) -> None:
        name = simpledialog.askstring(
            "New Control Flow Diagram", "Enter diagram name:"
        )
        if not name:
            return
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram(
            "Control Flow Diagram", name=name, package=repo.root_package.elem_id
        )
        tab = self.app._new_tab(self.app._format_diag_title(diag))
        self.app.diagram_tabs[diag.diag_id] = tab
        ControlFlowDiagramWindow(tab, self.app, diagram_id=diag.diag_id)
        self.app.refresh_all()
