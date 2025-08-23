import sys
from pathlib import Path
import tkinter as tk
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from main.AutoML import AutoMLApp


def test_fta_menu_within_quantitative():
    try:
        root = tk.Tk()
        root.withdraw()
    except tk.TclError:
        pytest.skip("Tk not available")
    app = AutoMLApp(root)
    q_labels = [app.quantitative_menu.entrycget(i, "label") for i in range(app.quantitative_menu.index("end") + 1)]
    assert "FTA" in q_labels
    top_labels = [app.menubar.entrycget(i, "label") for i in range(app.menubar.index("end") + 1)]
    assert "FTA" not in top_labels
    fta_labels = [app.fta_menu.entrycget(i, "label") for i in range(app.fta_menu.index("end") + 1)]
    assert "Add Confidence" not in fta_labels
    assert "Add Robustness" not in fta_labels
    root.destroy()
