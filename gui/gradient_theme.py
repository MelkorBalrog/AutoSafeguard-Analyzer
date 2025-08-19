import tkinter as tk
from tkinter import ttk

def apply_gradient_theme(style: ttk.Style) -> None:
    """Apply a light-blue to white gradient background to ttk frames.

    A thin dark line is added at the bottom to give a subtle 3D effect.
    The created gradient image is stored on ``style`` to prevent garbage
    collection.
    """
    root = style.master if hasattr(style, 'master') else None
    if root is None:
        root = tk._get_default_root()
        if root is None:
            return
    height = 64
    img = tk.PhotoImage(master=root, width=1, height=height)
    r1, g1, b1 = root.winfo_rgb("#add8e6")  # light blue
    r2, g2, b2 = root.winfo_rgb("#ffffff")  # white
    for i in range(height - 1):
        r = int(r1 + (r2 - r1) * i / (height - 1)) // 256
        g = int(g1 + (g2 - g1) * i / (height - 1)) // 256
        b = int(b1 + (b2 - b1) * i / (height - 1)) // 256
        img.put(f"#{r:02x}{g:02x}{b:02x}", to=(0, i))
    # dark bottom line for subtle depth
    img.put("#708090", to=(0, height - 1))
    style.element_create("GradientFrame", "image", img, border=0, sticky="nsew")
    style.layout("TFrame", [("GradientFrame", {"sticky": "nsew"})])
    # keep reference
    style._gradient_image = img
