import math
import tkinter as tk


def show_splash(root: tk.Tk, duration: int = 3000) -> None:
    """Display a simple animated splash screen.

    Parameters
    ----------
    root:
        Root ``tk.Tk`` instance that owns the splash screen.
    duration:
        How long the splash screen should stay visible in milliseconds.
    """
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)
    width, height = 400, 300
    # Center the window on the screen
    screen_w = splash.winfo_screenwidth()
    screen_h = splash.winfo_screenheight()
    x = (screen_w - width) // 2
    y = (screen_h - height) // 2
    splash.geometry(f"{width}x{height}+{x}+{y}")
    splash.attributes("-topmost", True)
    try:
        splash.attributes("-alpha", 0.95)
    except tk.TclError:
        pass

    canvas = tk.Canvas(splash, width=width, height=height, highlightthickness=0, bg="white")
    canvas.pack()

    center_x, center_y = width / 2, height / 2 - 20
    size = 100
    angle = 0
    square = canvas.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, outline="#333", width=2)
    canvas.create_text(center_x, center_y, text="\u2699", font=("Helvetica", 36), fill="#666")
    canvas.create_text(
        width / 2,
        height - 60,
        text="Automotive Modeling Language\nby\nKarel Capek Robotics",
        font=("Helvetica", 12),
        justify="center",
        fill="#333",
    )

    def animate() -> None:
        nonlocal angle
        angle += 5
        radians = math.radians(angle)
        half = size / 2
        points = []
        for dx, dy in [(-half, -half), (half, -half), (half, half), (-half, half)]:
            x = center_x + dx * math.cos(radians) - dy * math.sin(radians)
            y = center_y + dx * math.sin(radians) + dy * math.cos(radians)
            points.extend([x, y])
        canvas.coords(square, *points)
        splash.after(50, animate)

    animate()
    splash.after(duration, splash.destroy)
    root.wait_window(splash)
