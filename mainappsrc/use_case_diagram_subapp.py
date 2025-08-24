from __future__ import annotations

from tkinter import simpledialog
from sysml.sysml_repository import SysMLRepository
from gui.architecture import UseCaseDiagramWindow


class UseCaseDiagramSubApp:
    """Create new use case diagrams."""

    def __init__(self, app: "AutoMLApp") -> None:
        self.app = app

    def open(self) -> None:
        name = simpledialog.askstring("New Use Case Diagram", "Enter diagram name:")
        if not name:
            return
        repo = SysMLRepository.get_instance()
        diag = repo.create_diagram("Use Case Diagram", name=name, package=repo.root_package.elem_id)
        tab = self.app._new_tab(self.app._format_diag_title(diag))
        self.app.diagram_tabs[diag.diag_id] = tab
        UseCaseDiagramWindow(tab, self.app, diagram_id=diag.diag_id)
        self.app.refresh_all()
