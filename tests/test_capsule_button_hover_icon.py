import sys
from pathlib import Path

import tkinter as tk
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gui.capsule_button import CapsuleButton, _lighten


def test_capsule_button_lightens_icon_on_hover():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    img = tk.PhotoImage(width=1, height=1)
    img.put("#808080", to=(0, 0, 1, 1))
    btn = CapsuleButton(root, image=img)
    btn.pack()
    root.update_idletasks()
    # hover image should be a lighter tone of original
    assert btn._hover_image.get(0, 0) == _lighten("#808080")
    btn._on_enter(type("E", (), {})())
    assert btn.itemcget(btn._image_item, "image") == str(btn._hover_image)
    # Motion inside maintains hover image, outside restores original
    inside_evt = type("E", (), {"x": 0, "y": 0})()
    outside_evt = type("E", (), {"x": btn.winfo_width() + 1, "y": btn.winfo_height() + 1})()
    btn._on_motion(inside_evt)
    assert btn.itemcget(btn._image_item, "image") == str(btn._hover_image)
    btn._on_motion(outside_evt)
    assert btn.itemcget(btn._image_item, "image") == str(btn._image)
    btn._on_leave(type("E", (), {})())
    assert btn.itemcget(btn._image_item, "image") == str(btn._image)
    root.destroy()


def test_capsule_button_preserves_transparency_on_hover():
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    img = tk.PhotoImage(width=2, height=1)
    img.put("#808080", to=(0, 0, 1, 1))
    btn = CapsuleButton(root, image=img)
    btn.pack()
    root.update_idletasks()
    assert btn._image.get(1, 0) == "{}"
    assert btn._hover_image.get(1, 0) == btn._image.get(1, 0)
    btn._on_enter(type("E", (), {})())
    assert btn.itemcget(btn._image_item, "image") == str(btn._hover_image)
    btn._on_leave(type("E", (), {})())
    assert btn.itemcget(btn._image_item, "image") == str(btn._image)
    root.destroy()


def test_lighten_image_preserves_alpha_with_png():
    try:
        from PIL import Image, ImageTk  # type: ignore
    except Exception:
        pytest.skip("Tk or Pillow not available")
    try:
        root = tk.Tk()
    except tk.TclError:
        pytest.skip("Tk not available")
    img = Image.new("RGBA", (2, 1))
    img.putpixel((0, 0), (128, 128, 128, 255))
    img.putpixel((1, 0), (0, 0, 0, 0))
    photo = ImageTk.PhotoImage(img)
    btn = CapsuleButton(root, image=photo)
    btn.pack()
    root.update_idletasks()
    hover = btn._hover_image
    pil_hover = ImageTk.getimage(hover)
    assert pil_hover.getpixel((1, 0))[3] == 0
    root.destroy()
