import tkinter as tk

from AutoML import AutoMLApp


def test_mixins_configure_app():
    root = tk.Tk()
    app = AutoMLApp(root)
    # Style mixin
    assert hasattr(app, "style_app")
    # Service mixin
    assert hasattr(app, "nav_input")
    # Icon mixin
    assert hasattr(app, "pkg_icon")
    root.destroy()
