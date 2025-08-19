import sys
import types
from pathlib import Path

import tkinter as tk

sys.path.append(str(Path(__file__).resolve().parents[1]))

from AutoML import AutoMLApp


class DummyMenu:
    def __init__(self):
        self.states = {}

    def entryconfig(self, idx, state=tk.DISABLED):
        self.states[idx] = state


def test_matrix_menu_enabled_with_work_product():
    menu = DummyMenu()
    app = types.SimpleNamespace(
        WORK_PRODUCT_INFO={
            "Requirement Specification": (
                "Area",
                "Tool",
                "show_requirements_editor",
            )
        },
        enable_process_area=lambda area: None,
        tool_actions={},
        tool_listboxes={},
        work_product_menus={"Requirement Specification": [(menu, 0)]},
        enabled_work_products=set(),
        WORK_PRODUCT_PARENTS={},
        tool_to_work_product={},
        update_views=lambda: None,
    )

    AutoMLApp.enable_work_product(app, "Requirement Specification", refresh=False)

    assert menu.states[0] == tk.NORMAL
