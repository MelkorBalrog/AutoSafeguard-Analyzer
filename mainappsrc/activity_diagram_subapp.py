from __future__ import annotations

from tkinter import simpledialog
from mainappsrc.models.sysml.sysml_repository import SysMLRepository
from gui.architecture import ActivityDiagramWindow


class ActivityDiagramSubApp:
    """Create new activity diagrams."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    def open(self) -> None:
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
