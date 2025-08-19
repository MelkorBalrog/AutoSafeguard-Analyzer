import pytest
import tkinter as tk
import tkinter.font as tkfont

from gui.capsule_button import CapsuleButton


def test_capsule_button_renders_image_and_resizes():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    root.withdraw()
    img = tk.PhotoImage(width=10, height=10)
    text = "A very long label"
    btn = CapsuleButton(root, text=text, image=img, compound=tk.LEFT)
    root.update_idletasks()
    assert btn._image_item is not None
    font = tkfont.nametofont(btn.cget("font"))
    expected = font.measure(text) + img.width() + 4 + 20
    assert int(btn["width"]) >= expected
    root.destroy()
