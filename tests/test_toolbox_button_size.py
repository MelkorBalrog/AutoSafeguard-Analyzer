import os
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace

import pytest

from gui.architecture import GovernanceDiagramWindow, BlockDiagramWindow
from gui.gsn_diagram_window import GSNDiagramWindow
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from gsn import GSNDiagram
from sysml.sysml_repository import SysMLRepository


def _button_widths(widget):
    widths = []
    for child in widget.winfo_children():
        if isinstance(child, ttk.Button):
            widths.append(child.winfo_width())
        else:
            widths.extend(_button_widths(child))
    return widths


@pytest.mark.skipif("DISPLAY" not in os.environ, reason="Tk display not available")
def test_governance_toolbox_buttons_same_width():
    SysMLRepository.reset_instance()
    root = tk.Tk()
    root.withdraw()
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance", name="Gov")
    win = GovernanceDiagramWindow(root, app=SimpleNamespace(), diagram_id=diag.diag_id)
    root.update_idletasks()
    widths = _button_widths(win.toolbox)
    assert len(set(widths)) == 1
    root.destroy()


@pytest.mark.skipif("DISPLAY" not in os.environ, reason="Tk display not available")
def test_block_toolbox_buttons_same_width():
    SysMLRepository.reset_instance()
    root = tk.Tk()
    root.withdraw()
    win = BlockDiagramWindow(root, app=SimpleNamespace())
    root.update_idletasks()
    widths = _button_widths(win.toolbox)
    assert len(set(widths)) == 1
    root.destroy()


@pytest.mark.skipif("DISPLAY" not in os.environ, reason="Tk display not available")
def test_gsn_toolbox_buttons_same_width():
    root = tk.Tk()
    root.withdraw()
    win = GSNDiagramWindow(root, SimpleNamespace(), GSNDiagram("Test"))
    root.update_idletasks()
    widths = _button_widths(win.toolbox)
    assert len(set(widths)) == 1
    root.destroy()


@pytest.mark.skipif("DISPLAY" not in os.environ, reason="Tk display not available")
def test_cbn_toolbox_buttons_same_width():
    root = tk.Tk()
    root.withdraw()
    win = CausalBayesianNetworkWindow(root, SimpleNamespace(cbn_docs=[]))
    root.update_idletasks()
    widths = _button_widths(win.toolbox)
    assert len(set(widths)) == 1
    root.destroy()
