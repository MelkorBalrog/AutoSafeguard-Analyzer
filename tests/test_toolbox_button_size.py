import os
import tkinter as tk
from tkinter import ttk
from types import SimpleNamespace

import pytest

from gui.architecture import GovernanceDiagramWindow, BlockDiagramWindow
from gui.gsn_diagram_window import GSNDiagramWindow
from gui.causal_bayesian_network_window import CausalBayesianNetworkWindow
from mainappsrc.models.gsn import GSNDiagram
from mainappsrc.models.sysml.sysml_repository import SysMLRepository


def _button_data(widget):
    widths: list[int] = []
    fits = True
    for child in widget.winfo_children():
        if isinstance(child, ttk.Button):
            width = child.winfo_width()
            req = child.winfo_reqwidth()
            if hasattr(child, "_content_width"):
                try:
                    req = max(req, child._content_width(int(child["height"])))
                except Exception:  # pragma: no cover - defensive
                    pass
            widths.append(width)
            if width < req:
                fits = False
        else:
            w, f = _button_data(child)
            widths.extend(w)
            fits = fits and f
    return widths, fits


@pytest.mark.skipif("DISPLAY" not in os.environ, reason="Tk display not available")
def test_governance_toolbox_buttons_same_width():
    SysMLRepository.reset_instance()
    root = tk.Tk()
    root.withdraw()
    repo = SysMLRepository.get_instance()
    diag = repo.create_diagram("Governance", name="Gov")
    win = GovernanceDiagramWindow(root, app=SimpleNamespace(), diagram_id=diag.diag_id)
    root.update_idletasks()
    widths, fits = _button_data(win.toolbox)
    assert fits
    assert len(set(widths)) == 1
    root.destroy()


@pytest.mark.skipif("DISPLAY" not in os.environ, reason="Tk display not available")
def test_block_toolbox_buttons_same_width():
    SysMLRepository.reset_instance()
    root = tk.Tk()
    root.withdraw()
    win = BlockDiagramWindow(root, app=SimpleNamespace())
    root.update_idletasks()
    widths, fits = _button_data(win.toolbox)
    assert fits
    assert len(set(widths)) == 1
    root.destroy()


@pytest.mark.skipif("DISPLAY" not in os.environ, reason="Tk display not available")
def test_gsn_toolbox_buttons_same_width():
    root = tk.Tk()
    root.withdraw()
    win = GSNDiagramWindow(root, SimpleNamespace(), GSNDiagram("Test"))
    root.update_idletasks()
    widths, fits = _button_data(win.toolbox)
    assert fits
    assert len(set(widths)) == 1
    root.destroy()


@pytest.mark.skipif("DISPLAY" not in os.environ, reason="Tk display not available")
def test_cbn_toolbox_buttons_same_width():
    root = tk.Tk()
    root.withdraw()
    win = CausalBayesianNetworkWindow(root, SimpleNamespace(cbn_docs=[]))
    root.update_idletasks()
    widths, fits = _button_data(win.toolbox)
    assert fits
    assert len(set(widths)) == 1
    root.destroy()
