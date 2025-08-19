import tkinter as tk
import math


class SplashScreen(tk.Toplevel):
    """Simple splash screen with rotating cube and gear."""

    def __init__(self, master, duration: int = 3000):
        super().__init__(master)
        self.duration = duration
        self.overrideredirect(True)

        # Shadow window to create simple 3D effect
        self.shadow = tk.Toplevel(master)
        self.shadow.overrideredirect(True)
        self.shadow.configure(bg="black")
        try:
            # Transparency might not be supported on all systems
            self.shadow.attributes("-alpha", 0.3)
        except tk.TclError:
            pass

        self.canvas_size = 300
        # Black background so colors pop
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            highlightthickness=0,
            bg="black",
        )
        self.canvas.pack()
        self._draw_gradient()
        self._center()
        # Initialize cube geometry
        self.angle = 0.0
        self.vertices = [
            (-1, -1, -1),
            (1, -1, -1),
            (1, 1, -1),
            (-1, 1, -1),
            (-1, -1, 1),
            (1, -1, 1),
            (1, 1, 1),
            (-1, 1, 1),
        ]
        self.edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]
        # Text at bottom
        self.canvas.create_text(
            self.canvas_size / 2,
            self.canvas_size - 40,
            text="Automotive Modeling Language\nby\nKarel Capek Robotics",
            justify="center",
            font=("Helvetica", 12),
            fill="white",
        )
        # Start animation
        self.after(10, self._animate)
        self.after(self.duration, self._close)

    def _center(self):
        self.update_idletasks()
        w = self.canvas_size
        h = self.canvas_size
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        # Position shadow slightly offset from the splash window
        self.shadow.geometry(f"{w}x{h}+{x + 5}+{y + 5}")
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.shadow.lower(self)

    def _draw_gradient(self):
        """Draw a multi-color gradient dominated by black."""
        # Color stops: violet -> magenta -> light green -> black
        stops = [
            (0.0, (138, 43, 226)),   # violet
            (0.3, (255, 0, 255)),    # magenta
            (0.5, (144, 238, 144)),  # light green
            (1.0, (0, 0, 0)),        # black
        ]
        steps = self.canvas_size
        for i in range(steps):
            ratio = i / steps
            # Find two surrounding color stops
            for idx in range(len(stops) - 1):
                if stops[idx][0] <= ratio <= stops[idx + 1][0]:
                    left_pos, left_col = stops[idx]
                    right_pos, right_col = stops[idx + 1]
                    break
            # Normalize ratio between the two stops
            local = (ratio - left_pos) / (right_pos - left_pos)
            r = int(left_col[0] + (right_col[0] - left_col[0]) * local)
            g = int(left_col[1] + (right_col[1] - left_col[1]) * local)
            b = int(left_col[2] + (right_col[2] - left_col[2]) * local)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(0, i, self.canvas_size, i, fill=color)

    def _project(self, x, y, z):
        """Project 3D point onto 2D canvas."""
        distance = 5
        factor = self.canvas_size / (2 * (z + distance))
        x = x * factor + self.canvas_size / 2
        y = y * factor + self.canvas_size / 2
        return x, y

    def _draw_cube(self):
        self.canvas.delete("cube")
        self.canvas.delete("shadow")
        # Simple oval shadow to give cube a floating appearance
        shadow_w = 80
        shadow_h = 20
        cx = self.canvas_size / 2
        cy = self.canvas_size / 2 + 60
        self.canvas.create_oval(
            cx - shadow_w / 2,
            cy - shadow_h / 2,
            cx + shadow_w / 2,
            cy + shadow_h / 2,
            fill="black",
            outline="",
            tags="shadow",
            stipple="gray50",
        )
        angle = math.radians(self.angle)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        points = []
        for x, y, z in self.vertices:
            # rotate around Y axis
            x1 = x * cos_a - z * sin_a
            z1 = x * sin_a + z * cos_a
            # rotate around X axis for slight 3D
            y1 = y * cos_a - z1 * sin_a
            z2 = y * sin_a + z1 * cos_a
            points.append(self._project(x1, y1, z2))
        for i, j in self.edges:
            x1, y1 = points[i]
            x2, y2 = points[j]
            # Bright cyan edges for visibility against black
            self.canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill="cyan",
                width=2,
                tags="cube",
            )

    def _draw_gear(self):
        self.canvas.delete("gear")
        teeth = 8
        inner = 20
        outer = 30
        pts = []
        angle = math.radians(self.angle * 2)
        for i in range(teeth * 2):
            r = outer if i % 2 == 0 else inner
            theta = angle + i * math.pi / teeth
            x = self.canvas_size / 2 + r * math.cos(theta)
            y = self.canvas_size / 2 + r * math.sin(theta)
            pts.append((x, y))
        # Light outline keeps gear visible on dark background
        self.canvas.create_polygon(
            pts, outline="lightgray", fill="", width=2, tags="gear"
        )

    def _animate(self):
        self.angle = (self.angle + 2) % 360
        self._draw_cube()
        self._draw_gear()
        self.after(50, self._animate)

    def _close(self):
        """Destroy splash screen and accompanying shadow window."""
        try:
            self.shadow.destroy()
        except Exception:
            pass
        self.destroy()
