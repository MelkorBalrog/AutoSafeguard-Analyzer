import sys
from pathlib import Path
import tkinter as tk
import pytest
from tkinter import ttk

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.button_utils import set_uniform_button_width


def test_uniform_width_for_capsule_button():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    frame = tk.Frame(root)
    frame.pack()
    btn1 = ttk.Button(frame, text="Short")
    btn1.pack()
    btn2 = ttk.Button(frame, text="Longer label")
    btn2.pack()
    set_uniform_button_width(frame)
    root.update_idletasks()
    assert btn1.winfo_width() == btn2.winfo_width()
    root.destroy()
