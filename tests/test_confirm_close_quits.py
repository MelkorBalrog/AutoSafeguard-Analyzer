import tkinter as tk
from unittest.mock import MagicMock

import pytest

from AutoML import AutoMLApp


def test_confirm_close_quits_and_destroys():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tkinter GUI not available")
    root.withdraw()
    quit_spy = MagicMock(wraps=root.quit)
    destroy_spy = MagicMock(wraps=root.destroy)
    root.quit = quit_spy
    root.destroy = destroy_spy

    app = AutoMLApp.__new__(AutoMLApp)
    app.root = root
    app.has_unsaved_changes = lambda: False
    app._loaded_model_paths = []

    app.confirm_close()

    assert quit_spy.called
    assert destroy_spy.called
