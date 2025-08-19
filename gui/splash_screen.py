import tkinter as tk
import math


class SplashScreen(tk.Toplevel):
    """Simple splash screen with rotating cube and gear."""

    def __init__(self, master, duration: int = 3000):
        super().__init__(master)
        self.duration = duration
        self.overrideredirect(True)
        self.canvas_size = 300
        # Nearly black canvas with subtle bluish/greenish tint
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_size,
            height=self.canvas_size,
            highlightthickness=0,
            bg="#001010",
        )
        self.canvas.pack()
        self._center()
        self._draw_background()
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
        self.after(self.duration, self.destroy)

    def _center(self):
        self.update_idletasks()
        w = self.canvas_size
        h = self.canvas_size
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _draw_background(self):
        """Draw gradient background and subtle 3D frame."""
        # Gradient from white to dark teal across the canvas
        start_rgb = (255, 255, 255)
        end_rgb = (0, 16, 16)
        for i in range(self.canvas_size):
            ratio = i / self.canvas_size
            r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
            g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
            b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.canvas.create_line(i, 0, i, self.canvas_size, fill=color, tags="bg")

        # Shaded frame for subtle depth effect
        margin = 15
        light = "#003030"
        dark = "#000000"
        self.canvas.create_line(
            margin,
            margin,
            self.canvas_size - margin,
            margin,
            fill=light,
            width=3,
            tags="bg",
        )
        self.canvas.create_line(
            margin,
            margin,
            margin,
            self.canvas_size - margin,
            fill=light,
            width=3,
            tags="bg",
        )
        self.canvas.create_line(
            self.canvas_size - margin,
            margin,
            self.canvas_size - margin,
            self.canvas_size - margin,
            fill=dark,
            width=3,
            tags="bg",
        )
        self.canvas.create_line(
            margin,
            self.canvas_size - margin,
            self.canvas_size - margin,
            self.canvas_size - margin,
            fill=dark,
            width=3,
            tags="bg",
        )

    def _project(self, x, y, z):
        """Project 3D point onto 2D canvas."""
        distance = 5
        factor = self.canvas_size / (2 * (z + distance))
        x = x * factor + self.canvas_size / 2
        y = y * factor + self.canvas_size / 2
        return x, y

    def _draw_cube(self):
        self.canvas.delete("cube")
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
